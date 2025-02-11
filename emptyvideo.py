import subprocess
import os

def create_mkv_with_audio(mp3_file, output_mkv="output.mkv", resolution="1280x720"):
    # Get audio duration
    duration_cmd = [
        "ffprobe", "-i", mp3_file, "-show_entries", "format=duration",
        "-v", "quiet", "-of", "csv=p=0"
    ]
    duration = subprocess.check_output(duration_cmd).decode().strip()

    # Run FFmpeg to create an MKV file with black video and audio
    ffmpeg_cmd = [
        "ffmpeg", "-f", "lavfi", "-i", f"color=c=black:s={resolution}:d={duration}",
        "-i", mp3_file, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental",
        "-shortest", output_mkv
    ]

    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    create_mkv_with_audio("output/music/mp3/accompaniment.mp3", "output/tmp/empty_video_with_music.mkv")
    print("process completed, please check output/tmp directory")