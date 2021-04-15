# KeyLogger
A keylogger that can run silently in the background and log keypresses,
take screenshots of the screen and capture images from the device's webcam. <br>
(Logs saved into a "dumps" dir, located in the root dir of the project)

### Disclaimer: 
This program was made for educational purposes only and should not be used with any malicious intent

## <u>How to run</u>
With python installed, download the project and run the following in the command line:
1) python -m venv C:\\*<path_to_project\>*\venv 
2) C:\\*<path_to_project\>*\venv\Scripts\activate.bat
3) pip install -r C:\\*<path_to_project\>*\requirements.txt
4) pythonw main.py \<*arguments*\>

"pythonw" is launching the app as a GUI app, although we don't have any 
GUI, this way the app can keep running in the background, even if you close the cmd.

### Arguments <br>
-s *interval* <br>
-w *interval*
<br> <br>
**-s**: enables screenshots at the interval specified in minutes (integer). If no interval is given,
the default value of 3 minutes is used <br>
**-w**: enables webcam captures at the interval specified in minutes (integer). If not interval is given,
the default value of 17 minutes is used. <br><br>
If 0 is passed as interval, it gets converted to 1. <br><br>
**Note**: when a webcam capture is taken, the program makes no attempt to hide
the flashing light that may light up for one second. <br>

### Examples
- pythonw main.py -s 5 -w 10 <br>
(screenshots every 5 mins, webcam captures every 10 mins)
- pythonw main.py -w <br>
  (webcam captures every 17 minutes(default), no screenshots)
- pythonw main.py <br>
  (no screenshots and not webcam captures, only keystrokes collected)
  <br>
  
## <u>Limitations</u> <br>
- The package used to read the keyboard input makes Windows' keyboard shortcuts unreliable, meaning it is not 
  guarantied that a shortcut like shift+alt will work and change the language 100% of the times it is pressed
  
- Right now, for every backspace press, always the most recent keystroke is deleted and not logged into the file,
  but if the cursor is moved from the last position using the mouse or the arrow keys(this will be fixed), the recorded keystrokes
  will not correspond with the actual letters the user typed after the deletes. Also, using keyboard 
  shortcuts like Ctrl+A and then backspace, Ctrl+D, Ctrl+Z will not affect the logged text.
