# REMI Frontend
## Important Note
You must use your system's native terminal to run the frontend. This means terminal for Mac OS or Linux and cmd for Windows. Please use Python 3.6 to run this project.

## Setup
### Install requirements:
```python
pip install -r requirements.txt
```

### Installing pyaudio:
You might run into an issue with pyaudio due to its portaudio dependency.

**For Windows**:<br/>
 If this happens, you will need to install pyaudio using a manually downloaded .whl file. Make sure you use the pip registered with Windows to do this. The safest method to do this is to run all the commands below via the Windows command prompt. 

If you insist on doing it via wsl/cygwin, make sure to reference the pip registered with Windows.

1) Identify the python version you are using via cmd:
```shell
python --version
```

2) Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and select the .whl file that matches your system.

The .whl files are formatted in this way: PyAudio‑0.2.11‑cp{PYTHON_VERSION}‑cp{PYTHON_VERSION}‑win_<32/amd64>.whl

3) Via the command prompt, navigate to the folder that contains the pyaudio .whl file and run:
```python
pip install <name-of-whl-file>
```

**For Unix/MacOS**:
```shell
sudo apt-get install python-pyaudio python3-pyaudio
```

## Run
Run app.py using your native terminal.
* If you are using Windows, you will need to run app.py using the Windows Command Prompt:

```python
python app.py
```

## Screenshots
### Recipe Search Page
![Recipe Search Page](https://drive.google.com/uc?id=16Oeaq60KQaSX_0a2DTOWM3AFOy2kFbwg&export=download)

### Chat Page
![Chat Page](https://drive.google.com/uc?id=1-RB73t4uNtbkL72AUtUu4fgYVbYehzjZ&export=download)

### Chat Page (Recipe Display)
![Chat Page Recipe Display](https://drive.google.com/uc?id=107LvjxwfGyb1cteRBrppMr-YPI9FuROf&export=download)

### Chat Page (Timers Display)
![Chat Page Timers Display](https://drive.google.com/uc?id=1JM-TCJZszuNC0yuhXW0Yu7uFoi74EsXg&export=download)