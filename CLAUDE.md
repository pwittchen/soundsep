# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

demix is a Python CLI tool that separates audio from songs into individual stems (vocals, instruments) using AI-powered audio processing. It can download from YouTube or process local audio files, apply tempo/pitch adjustments, and cut audio segments.

## Development Commands

```bash
# Setup environment (requires Python 3.8, ffmpeg installed via homebrew or similar)
mkvirtualenv -p /path/to/python3.8 demix
workon demix
pip install -r requirements.txt

# Run tests
pip install pytest
pytest -v                    # all tests
pytest -v -k test_name       # specific test

# Lint (as used in CI)
flake8 . --max-complexity=10 --max-line-length=127

# Run the tool
python demix.py -u <youtube-url> [options]
python demix.py -f <audio-file> [options]
```

## Architecture

**Single-file design**: The entire application is in `demix.py` (~377 lines). It's a wrapper that orchestrates three external tools:

1. **pytubefix** - YouTube downloads
2. **FFmpeg** - Audio/video conversion and effects (subprocess calls)
3. **Spleeter** - AI audio separation (subprocess calls to CLI)

**Processing pipeline**: download → convert to MP3 → separate with Spleeter → apply effects (tempo/pitch) → output

**Output structure**:
```
output/
├── music/         # Extracted audio (music.mp3) and separated wav stems
│   └── mp3/       # Final separated stems as mp3
├── video/         # Downloaded video and accompaniment video container
pretrained_models/ # Cached Spleeter models (~300MB, downloads on first run)
```

**Key design patterns**:
- All heavy operations run as subprocesses with suppressed output
- `Spinner` class provides threaded terminal progress indication
- Effects (tempo/pitch) are chained FFmpeg filters (rubberband for pitch, atempo for tempo)
- Spleeter models lazy-load on first separation

## Separation Modes

- `2stems`: vocals, accompaniment
- `4stems`: vocals, drums, bass, other
- `5stems`: vocals, drums, bass, piano, other

## Dependencies

System: ffmpeg, ffprobe (checked at runtime)
Python: pytubefix, ffmpeg (bindings), spleeter
