# demix

separates audio from songs into stems (vocals, instruments)

## installation

I suggest to create virtualenv for this project to not break system-wide packages installations (replace python path below with your own python3.8 path):

```
brew install virtualenvwrapper
brew install ffmpeg
mkvirtualenv -p /Users/pw/.pyenv/versions/3.8.16/bin/python demix
workon demix
pip install demix
demix -v
```

Please note: I'm using homebrew for installing `virtualenvwrapper` and `ffmpeg`.
If you're using another package manager or different operating system than macOS (e.g. Linux), you need to install it differently.

## development

prepare environment (replace python path below with your own python3.8 path):

```
brew install virtualenvwrapper
brew install ffmpeg
mkvirtualenv -p /Users/pw/.pyenv/versions/3.8.16/bin/python demix
workon demix
pip install -r requirements.txt
python demix.py -v
```

Please note: I'm using homebrew for installing `virtualenvwrapper` and `ffmpeg`.
If you're using another package manager or different operating system than macOS (e.g. Linux), you need to install it differently.

exit virtualenv, when you're done:

```
deactivate
```

to activate env again:

```
workon demix
```

## testing

install pytest:

```
pip install pytest
```

run all tests (`-v` param for verbose):

```
pytest -v
```

## usage

```
python demix.py -u <youtube-url> [options]
python demix.py -f <audio-file> [options]
```

### options

| Option | Description |
|--------|-------------|
| `-u`, `--url` | YouTube video URL to process |
| `-f`, `--file` | Local audio file to process (mp3, wav, flac, etc.) |
| `-o`, `--output` | Output directory (default: `output`) |
| `-t`, `--tempo` | Tempo factor for output audio (default: `1.0`, use `< 1.0` to slow down) |
| `-p`, `--transpose` | Transpose pitch by semitones (default: `0`, range: `-12` to `+12`) |
| `-ss`, `--start` | Start time for cutting (format: `MM:SS` or `HH:MM:SS`) |
| `-to`, `--end` | End time for cutting (format: `MM:SS` or `HH:MM:SS`) |
| `-m`, `--mode` | Separation mode: `2stems`, `4stems`, or `5stems` (default: `2stems`) |
| `-c`, `--clean` | Clean up files: `output`, `models`, or `all` |
| `-v`, `--version` | Show version number |
| `-h`, `--help` | Show help message |

### separation modes

| Mode | Stems |
|------|-------|
| `2stems` | vocals, accompaniment |
| `4stems` | vocals, drums, bass, other |
| `5stems` | vocals, drums, bass, piano, other |

### examples

```bash
# separate a YouTube video into vocals and accompaniment
demix -u 'https://www.youtube.com/watch?v=VIDEO_ID'

# separate a local file with 4 stems
demix -f /path/to/song.mp3 -m 4stems

# cut audio from 1:30 to 3:45 before separation
demix -f song.mp3 -ss 1:30 -to 3:45

# start from 0:30 (skip intro)
demix -f song.mp3 -ss 0:30

# keep only the first 2 minutes
demix -f song.mp3 -to 2:00

# combine cutting with tempo and transpose
demix -f song.mp3 -ss 1:00 -to 4:00 -t 0.8 -p -2
```
