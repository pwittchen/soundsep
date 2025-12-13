import argparse
import subprocess
import os
from pytubefix import YouTube

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

def convert_wav_to_mp3(input_file, output_file):
    subprocess.run(["mkdir", "-p", "output/music/mp3"])
    subprocess.run([
        "ffmpeg", "-i", input_file, "-b:a", "192k", output_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def remove_vocals(mp3_file, output_folder):
    subprocess.run([
        "spleeter", "separate", "-p", "spleeter:2stems", "-o", output_folder, mp3_file
    ], check=True)

def create_empty_mkv_with_audio(mp3_file, output_mkv, resolution="1280x720"):
    duration_cmd = [
        "ffprobe", "-i", mp3_file, "-show_entries", "format=duration",
        "-v", "quiet", "-of", "csv=p=0"
    ]
    duration = subprocess.check_output(duration_cmd).decode().strip()
    ffmpeg_cmd = [
        "ffmpeg", "-f", "lavfi", "-i", f"color=c=black:s={resolution}:d={duration}",
        "-i", mp3_file, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental",
        "-shortest", output_mkv
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def remove_output_dir():
    if os.path.exists("output"):
        subprocess.run(["rm", "-rf", "output"])
    else:
        print("Directory output/ does not exist.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a YouTube video, convert it into mp3 and remove vocals from it")
    parser.add_argument("url", help="the YouTube video URL to download.")
    args = parser.parse_args()
    remove_output_dir()
    video_file = download_video(args.url, "output/tmp")
    convert_to_mp3(video_file, "output/tmp/music.mp3")
    remove_vocals("output/tmp/music.mp3", "output")
    convert_wav_to_mp3("output/music/accompaniment.wav", "output/music/mp3/accompaniment.mp3")
    convert_wav_to_mp3("output/music/vocals.wav", "output/music/mp3/vocals.mp3")
    create_empty_mkv_with_audio("output/music/mp3/accompaniment.mp3", "output/tmp/empty_video_with_music_without_vocals.mkv")
    print("process completed, please check output/ directory")
