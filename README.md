# soundsep
app, which removes vocals from the song in the youtube video

## development

prepare environment (replace python path below with your own python3.8 path):

```
brew install virtualenvwrapper
brew install ffmpeg
mkvirtualenv -p /Users/pw/.pyenv/versions/3.8.16/bin/python soundsep
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
python soundsep.py <url>
```

e.g.

```
python soundsep.py "https://www.youtube.com/watch?v=cw1B4NRvosE"
```

and then check `output/` directory

if you want to create "empty" video with generated accompaniment, please use the following script:

```
python emptyvideo.mp3
```

Please note: you need to run `soundsep.py` script first in order to have input file for the `emptyvideo.py` script.

## cleanup

cleaning output:

```
./clean_output.sh
```

cleaning pretrained models:

```
./clean_models.sh
```

cleaning everything:

```
./clean.sh
```