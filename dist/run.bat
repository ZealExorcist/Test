@echo off

REM Run Python script in the background (hidden)
start "" pythonw pwd.py

REM Run Python script in the foreground
python abcd.py
pause
