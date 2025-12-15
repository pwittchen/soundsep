"""Command-line interface for demix."""

import argparse
import subprocess
import os
import shutil
import sys
import threading
import itertools
import time
from pytubefix import YouTube


def get_version():
    """Get version from package metadata or fallback."""
    try:
        from demix import __version__
        return __version__
    except ImportError:
        return "1.0.0"


DEFAULT_VIDEO_RESOLUTION = "1280x720"


def parse_time(time_str):
    """Parse time string in MM:SS or HH:MM:SS format to seconds."""
    if time_str is None:
        return None
    parts = time_str.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        raise ValueError(f"Invalid time format: {time_str}. Use MM:SS or HH:MM:SS")


def format_time(seconds):
    """Format seconds to MM:SS or HH:MM:SS string."""
    if seconds is None:
        return None
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    return f"{minutes}:{secs:05.2f}"


class Spinner:
    def __init__(self, message="Loading..."):
        self.message = message
        self.spinning = False
        self.thread = None
        self.spinner_chars = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])

    def _spin(self):
        while self.spinning:
            char = next(self.spinner_chars)
            sys.stdout.write(f"\r{char} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)

    def start(self):
        self.spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def stop(self, success=True):
        self.spinning = False
        if self.thread:
            self.thread.join()
        symbol = "\033[32m✓\033[0m" if success else "\033[31m✗\033[0m"
        sys.stdout.write(f"\r{symbol} {self.message}\n")
        sys.stdout.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(success=exc_type is None)


def check_ffmpeg():
    """Check if ffmpeg and ffprobe are installed and accessible."""
    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg is not installed or not found in PATH.")
        print("Please install ffmpeg:")
        print("  macOS:   brew install ffmpeg")
        print("  Ubuntu:  sudo apt install ffmpeg")
        print("  Windows: https://ffmpeg.org/download.html")
        return False
    if shutil.which("ffprobe") is None:
        print("Error: ffprobe is not installed or not found in PATH.")
        print("ffprobe is usually included with ffmpeg. Please reinstall ffmpeg.")
        return False
    return True


def download_video(url, output_path):
    os.makedirs(output_path, exist_ok=True)
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    ext = stream.mime_type.split("/")[-1]
    filename = f"video.{ext}"
    stream.download(output_path=output_path, filename=filename)
    return os.path.join(output_path, filename)


def convert_to_mp3(input_file, output_file, start_time=None, end_time=None):
    cmd = ["ffmpeg"]
    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    if end_time is not None:
        cmd.extend(["-to", str(end_time)])
    cmd.extend(["-i", input_file, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", output_file])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def convert_wav_to_mp3(input_file, output_file, tempo=1.0, transpose=0):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    cmd = ["ffmpeg", "-i", input_file]
    filters = []
    # Apply transpose (pitch shift) using rubberband filter
    # Formula: pitch_ratio = 2^(semitones/12)
    if transpose != 0:
        pitch_ratio = 2 ** (transpose / 12)
        filters.append(f"rubberband=pitch={pitch_ratio}")
    # Apply tempo adjustment using atempo filter
    if tempo != 1.0:
        # atempo filter only accepts values between 0.5 and 2.0
        # chain multiple filters for values outside this range
        tempo_value = tempo
        while tempo_value < 0.5:
            filters.append("atempo=0.5")
            tempo_value /= 0.5
        while tempo_value > 2.0:
            filters.append("atempo=2.0")
            tempo_value /= 2.0
        filters.append(f"atempo={tempo_value}")
    if filters:
        cmd.extend(["-af", ",".join(filters)])
    cmd.extend(["-b:a", "192k", output_file])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


STEM_MODES = {
    "2stems": ["vocals", "accompaniment"],
    "4stems": ["vocals", "drums", "bass", "other"],
    "5stems": ["vocals", "drums", "bass", "piano", "other"],
}


def separate_audio(mp3_file, output_folder, mode="2stems"):
    subprocess.run([
        "spleeter", "separate", "-p", f"spleeter:{mode}", "-o", output_folder, mp3_file
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_empty_mkv_with_audio(mp3_file, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    duration_cmd = [
        "ffprobe", "-i", mp3_file, "-show_entries", "format=duration",
        "-v", "quiet", "-of", "csv=p=0"
    ]
    duration = subprocess.check_output(duration_cmd).decode().strip()
    ffmpeg_cmd = [
        "ffmpeg", "-f", "lavfi", "-i", f"color=c=black:s={DEFAULT_VIDEO_RESOLUTION}:d={duration}",
        "-i", mp3_file, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental",
        "-shortest", output_file
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def remove_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Removed: {path}")
    else:
        print(f"Directory does not exist: {path}")


def clean(target, output_dir="output"):
    if target == "output":
        remove_dir(output_dir)
    elif target == "models":
        remove_dir("pretrained_models")
    elif target == "all":
        remove_dir(output_dir)
        remove_dir("pretrained_models")


def parse_args():
    # Custom formatter with wider help position for better readability
    class WideHelpFormatter(argparse.RawDescriptionHelpFormatter):
        def __init__(self, prog):
            super().__init__(prog, max_help_position=40)

    parser = argparse.ArgumentParser(
        prog="demix",
        description="Separate audio into stems (vocals, instruments) from a YouTube video or local audio file.",
        epilog="Examples:\n"
               "  demix -u 'https://www.youtube.com/watch?v=VIDEO_ID' -m 4stems\n"
               "  demix -f /path/to/song.mp3 -m 2stems\n"
               "  demix -f song.mp3 -ss 1:30 -to 3:45      # cut from 1:30 to 3:45\n"
               "  demix -f song.mp3 -ss 0:30               # start from 0:30\n"
               "  demix -f song.mp3 -to 2:00               # cut first 2 minutes",
        formatter_class=WideHelpFormatter
    )
    parser.add_argument(
        "-u", "--url",
        metavar="URL",
        help="YouTube video URL to process"
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="local audio file to process (mp3, wav, flac, etc.)"
    )
    parser.add_argument(
        "-o", "--output",
        default="output",
        metavar="DIR",
        help="output directory (default: output)"
    )
    parser.add_argument(
        "-c", "--clean",
        choices=["output", "models", "all"],
        metavar="TARGET",
        help="clean up files: output, models, or all"
    )
    parser.add_argument(
        "-t", "--tempo",
        type=float,
        default=1.0,
        metavar="FACTOR",
        help="tempo factor for output audio (default: 1.0, use < 1.0 to slow down, e.g., 0.8 for 80%% tempo)"
    )
    parser.add_argument(
        "-p", "--transpose",
        type=int,
        default=0,
        metavar="SEMITONES",
        help="transpose pitch by semitones (default: 0, range: -12 to +12, e.g., -5 for 5 semitones down)"
    )
    parser.add_argument(
        "-ss", "--start",
        metavar="TIME",
        help="start time for cutting (format: MM:SS or HH:MM:SS, e.g., 1:30 for 1 min 30 sec)"
    )
    parser.add_argument(
        "-to", "--end",
        metavar="TIME",
        help="end time for cutting (format: MM:SS or HH:MM:SS, e.g., 3:45 for 3 min 45 sec)"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["2stems", "4stems", "5stems"],
        default="2stems",
        metavar="MODE",
        help="separation mode: 2stems (vocals/accompaniment), "
             "4stems (vocals/drums/bass/other), "
             "5stems (vocals/drums/bass/piano/other). "
             "Default: 2stems"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {get_version()}"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.clean:
        clean(args.clean, args.output)
        return

    if not check_ffmpeg():
        return

    if not args.url and not args.file:
        print("Error: --url or --file is required when not using --clean")
        print("Run with --help for usage information")
        return

    if args.url and args.file:
        print("Error: --url and --file cannot be used together")
        print("Run with --help for usage information")
        return

    if args.file and not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}")
        return

    # Parse time cutting parameters
    try:
        start_time = parse_time(args.start)
        end_time = parse_time(args.end)
    except ValueError as e:
        print(f"Error: {e}")
        return

    output_dir = args.output
    tmp_dir = os.path.join(output_dir, "tmp")
    music_dir = os.path.join(output_dir, "music")
    mp3_dir = os.path.join(music_dir, "mp3")
    video_dir = os.path.join(output_dir, "video")

    mode = args.mode
    stems = STEM_MODES[mode]

    source = args.url if args.url else args.file
    print(f"Processing: {source}")
    print(f"Output directory: {output_dir}")
    print(f"Separation mode: {mode} ({', '.join(stems)})")
    if start_time is not None or end_time is not None:
        cut_info = "Cutting: "
        if start_time is not None:
            cut_info += f"from {args.start}"
        if end_time is not None:
            cut_info += f" to {args.end}" if start_time else f"to {args.end}"
        print(cut_info)
    print()

    remove_dir(output_dir)

    mp3_file = os.path.join(tmp_dir, "music.mp3")

    cut_msg = " and cutting" if start_time is not None or end_time is not None else ""
    if args.url:
        with Spinner("Downloading video..."):
            video_file = download_video(args.url, tmp_dir)

        with Spinner(f"Converting to MP3{cut_msg}..."):
            convert_to_mp3(video_file, mp3_file, start_time, end_time)
    else:
        with Spinner(f"Converting audio file to MP3{cut_msg}..."):
            os.makedirs(tmp_dir, exist_ok=True)
            convert_to_mp3(args.file, mp3_file, start_time, end_time)

    first_run = not os.path.exists("pretrained_models")
    if first_run:
        print("\033[33mℹ\033[0m First run detected - Spleeter models will be downloaded (~300MB).")
        print("  This is a one-time operation (unless you delete models with --clean models).")
        print("  Subsequent operations will be faster.\n")

    with Spinner(f"Separating audio ({mode})..."):
        separate_audio(mp3_file, output_dir, mode)

    convert_msg = "Converting separated tracks to MP3..."
    effects = []
    if args.tempo != 1.0:
        effects.append(f"tempo: {args.tempo}x")
    if args.transpose != 0:
        sign = "+" if args.transpose > 0 else ""
        effects.append(f"transpose: {sign}{args.transpose} semitones")
    if effects:
        convert_msg = f"Converting separated tracks to MP3 ({', '.join(effects)})..."
    with Spinner(convert_msg):
        for stem in stems:
            convert_wav_to_mp3(
                os.path.join(music_dir, f"{stem}.wav"),
                os.path.join(mp3_dir, f"{stem}.mp3"),
                args.tempo,
                args.transpose
            )

    # Create video only for 2stems mode (accompaniment = complete music without vocals)
    if mode == "2stems":
        with Spinner("Creating video for accompaniment track..."):
            create_empty_mkv_with_audio(
                os.path.join(mp3_dir, "accompaniment.mp3"),
                os.path.join(video_dir, "accompaniment.mkv"),
            )

    print(f"\n\033[32m✓\033[0m Done! Check the '{output_dir}/' directory for results.")
    print(f"  Separated stems: {', '.join(stems)}")


if __name__ == "__main__":
    main()
