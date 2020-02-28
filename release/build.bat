pyinstaller --noconsole --exclude-module tkinter --hidden-import dataclasses --add-data dll;. --onefile ../src/main.py
pause