# demix

separates audio from songs into stems (vocals, instruments)

## development

prepare environment (replace python path below with your own python3.8 path):

```
brew install virtualenvwrapper
brew install ffmpeg
mkvirtualenv -p /Users/pw/.pyenv/versions/3.8.16/bin/python demix
workon demix
pip install -r requirements.txt
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
```

### options

| Option | Description |
|--------|-------------|
| `-u`, `--url` | YouTube video URL to process |
| `-o`, `--output` | Output directory (default: `output`) |
| `-t`, `--tempo` | Tempo factor for output audio (default: `1.0`, use `< 1.0` to slow down) |
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
