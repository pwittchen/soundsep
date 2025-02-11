import argparse
import yt_dlp
import subprocess
import os
import sys

def download_video(url, output_path):
    ydl_opts = {
        "format": "bestvideo+bestaudio",
        "outtmpl": f"{output_path}/video.%(ext)s"
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def convert_mkv_to_mp3(input_file, output_file):
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
    print(f"Processing complete. Separated files are in: {output_folder}")

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
    download_video(args.url, "output/tmp")
    convert_mkv_to_mp3("output/tmp/video.mkv", "output/tmp/music.mp3")
    remove_vocals("output/tmp/music.mp3", "output")
    convert_wav_to_mp3("output/music/accompaniment.wav", "output/music/mp3/accompaniment.mp3")
    convert_wav_to_mp3("output/music/vocals.wav", "output/music/mp3/vocals.mp3")
    print("process completed, please check output/ directory")

