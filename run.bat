@echo off
REM Navigate to the script's directory
cd /d "%~dp0"

REM Activate the virtual environment
call .venv\Scripts\activate

REM Run the Python script. Change 'example.py' to the name of your script.
python example.py

REM Deactivate the virtual environment
deactivate

REM Pause the script to see the output
pause