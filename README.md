# Simple Waveform Visualiser

Uses `pyaudio` to get sound data from your microphone. Visualises with some basic options.

## Installing pyaudio

### Python 3.6-

`pip3 install pyaudio`

### Python 3.7+

There is an unofficial version which fixes a setup script for python 3.7 from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Download the relevant `PyAudio‑0.2.11‑cp37‑cp37m‑win*.whl` file to this directory, then run:

`pip3 install PyAudio-0.2.11-cp37-cp37m-win*.whl`

## Building for windows

You can build it as an executable for people who don't have Python installed.

```bash
pip3 install PyInstaller
pyinstaller.exe ./viewer.py
```

Creates a bunch of files and folders, the executable is `./dist/viewer/viewer.exe`, and you need to transport the whole `./dist/viewer/` folder whereever you want to run it.
