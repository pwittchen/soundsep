"""
demix - Separate audio into stems (vocals, instruments) using AI.

A CLI tool that separates audio from songs into individual stems using
Spleeter. Supports YouTube downloads or local audio files, with options
for tempo/pitch adjustments and audio cutting.
"""

__version__ = "1.0.2"
__author__ = "Piotr Wittchen"

from demix.cli import (
    main,
    STEM_MODES,
    DEFAULT_VIDEO_RESOLUTION,
    Spinner,
    parse_args,
    parse_time,
    format_time,
    remove_dir,
    clean,
    convert_wav_to_mp3,
    convert_to_mp3,
    separate_audio,
    download_video,
    create_empty_mkv_with_audio,
    check_ffmpeg,
)

__all__ = [
    "__version__",
    "main",
    "STEM_MODES",
    "DEFAULT_VIDEO_RESOLUTION",
    "Spinner",
    "parse_args",
    "parse_time",
    "format_time",
    "remove_dir",
    "clean",
    "convert_wav_to_mp3",
    "convert_to_mp3",
    "separate_audio",
    "download_video",
    "create_empty_mkv_with_audio",
    "check_ffmpeg",
]
