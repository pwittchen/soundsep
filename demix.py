import argparse
import subprocess
import os
import shutil
import sys
import threading
import itertools
import time
from pytubefix import YouTube

__version__ = "1.0.0"
DEFAULT_VIDEO_RESOLUTION = "1280x720"


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
        symbol = "✓" if success else "✗"
        sys.stdout.write(f"\r{symbol} {self.message}\n")
        sys.stdout.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(success=exc_type is None)


def download_video(url, output_path):
    os.makedirs(output_path, exist_ok=True)
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    ext = stream.mime_type.split("/")[-1]
    filename = f"video.{ext}"
    stream.download(output_path=output_path, filename=filename)
    return os.path.join(output_path, filename)


def convert_to_mp3(input_file, output_file):
    subprocess.run([
        "ffmpeg", "-i", input_file, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", output_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def convert_wav_to_mp3(input_file, output_file, tempo=1.0):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    cmd = ["ffmpeg", "-i", input_file]
    if tempo != 1.0:
        # atempo filter only accepts values between 0.5 and 2.0
        # chain multiple filters for values outside this range
        atempo_filters = []
        tempo_value = tempo
        while tempo_value < 0.5:
            atempo_filters.append("atempo=0.5")
            tempo_value /= 0.5
        while tempo_value > 2.0:
            atempo_filters.append("atempo=2.0")
            tempo_value /= 2.0
        atempo_filters.append(f"atempo={tempo_value}")
        cmd.extend(["-af", ",".join(atempo_filters)])
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
    parser = argparse.ArgumentParser(
        prog="demix",
        description="Download a YouTube video and separate audio into stems (vocals, instruments).",
        epilog="Example: python demix.py -u 'https://www.youtube.com/watch?v=VIDEO_ID' -m 4stems",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-u", "--url",
        metavar="URL",
        help="YouTube video URL to process"
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
        "-m", "--mode",
        choices=["2stems", "4stems", "5stems"],
        default="2stems",
        metavar="MODE",
        help="separation mode: 2stems (vocals/accompaniment),"
             "4stems (vocals/drums/bass/other),"
             "5stems (vocals/drums/bass/piano/other)."
             "Default: 2stems"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.clean:
        clean(args.clean, args.output)
        return

    if not args.url:
        print("Error: --url is required when not using --clean")
        print("Run with --help for usage information")
        return

    output_dir = args.output
    tmp_dir = os.path.join(output_dir, "tmp")
    music_dir = os.path.join(output_dir, "music")
    mp3_dir = os.path.join(music_dir, "mp3")
    video_dir = os.path.join(output_dir, "video")

    mode = args.mode
    stems = STEM_MODES[mode]

    print(f"Processing: {args.url}")
    print(f"Output directory: {output_dir}")
    print(f"Separation mode: {mode} ({', '.join(stems)})\n")

    remove_dir(output_dir)

    with Spinner("Downloading video..."):
        video_file = download_video(args.url, tmp_dir)

    with Spinner("Converting to MP3..."):
        mp3_file = os.path.join(tmp_dir, "music.mp3")
        convert_to_mp3(video_file, mp3_file)

    with Spinner(f"Separating audio ({mode})..."):
        separate_audio(mp3_file, output_dir, mode)

    tempo_msg = "Converting separated tracks to MP3..."
    if args.tempo != 1.0:
        tempo_msg = f"Converting separated tracks to MP3 (tempo: {args.tempo}x)..."
    with Spinner(tempo_msg):
        for stem in stems:
            convert_wav_to_mp3(
                os.path.join(music_dir, f"{stem}.wav"),
                os.path.join(mp3_dir, f"{stem}.mp3"),
                args.tempo
            )

    # Create video only for 2stems mode (accompaniment = complete music without vocals)
    if mode == "2stems":
        with Spinner("Creating video for accompaniment track..."):
            create_empty_mkv_with_audio(
                os.path.join(mp3_dir, "accompaniment.mp3"),
                os.path.join(video_dir, "accompaniment.mkv"),
            )

    print(f"\n✓ Done! Check the '{output_dir}/' directory for results.")
    print(f"  Separated stems: {', '.join(stems)}")


if __name__ == "__main__":
    main()
