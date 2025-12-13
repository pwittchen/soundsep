# soundsep 🎤
removes vocals from the song in the youtube video

## functionality

in the input you provide:
- youtube url

in the output you get:
- downloaded video
- song from the video
- separated vocals
- separated music
- empty video with black screen and extracted music without vocals

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
