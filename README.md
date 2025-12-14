# soundsep 🎤

removes vocals from the song in the youtube video

## development

prepare environment (replace python path below with your own python3.8 path):

```
brew install virtualenvwrapper
brew install ffmpeg
mkvirtualenv -p /Users/pw/.pyenv/versions/3.8.16/bin/python soundsep
workon soundsep
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
workon soundsep
```

## usage

```
python soundsep.py -u <youtube-url> [options]
```

### options

| Option | Description |
|--------|-------------|
| `-u`, `--url` | YouTube video URL to process |
| `-o`, `--output` | Output directory (default: `output`) |
| `-r`, `--resolution` | Resolution for generated video (default: `1280x720`) |
| `-s`, `--speed` | Speed factor for output audio (default: `1.0`, use `< 1.0` to slow down) |
| `-c`, `--clean` | Clean up files: `output`, `models`, or `all` |
| `-v`, `--version` | Show version number |
| `-h`, `--help` | Show help message |

### examples

basic usage:

```
python soundsep.py -u "https://www.youtube.com/watch?v=cw1B4NRvosE"
```

with custom output directory:

```
python soundsep.py -u "https://www.youtube.com/watch?v=cw1B4NRvosE" -o my_output
```

with custom resolution:

```
python soundsep.py -u "https://www.youtube.com/watch?v=cw1B4NRvosE" -r 1920x1080
```

slow down output to 80% speed (useful for practicing):

```
python soundsep.py -u "https://www.youtube.com/watch?v=cw1B4NRvosE" -s 0.8
```

slow down to 50% speed:

```
python soundsep.py -u "https://www.youtube.com/watch?v=cw1B4NRvosE" -s 0.5
```

speed up output to 120%:

```
python soundsep.py -u "https://www.youtube.com/watch?v=cw1B4NRvosE" -s 1.2
```

show help:

```
python soundsep.py --help
```

after processing, check the output directory for results

## cleanup

clean output directory:

```
python soundsep.py --clean output
```

clean pretrained models:

```
python soundsep.py --clean models
```

clean everything:

```
python soundsep.py --clean all
```
