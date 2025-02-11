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
workon soundsep
python soundsep.py <url>
```

e.g.

```
python soundsep.py "https://www.youtube.com/watch?v=cw1B4NRvosE"
```

## cleanup

cleaning output:

```
./clean.sh
```

cleaning pretrained models

```
./clean_models.sh
```