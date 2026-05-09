@echo off
cd /d %~dp0

echo Checking Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing / updating dependencies...
py -m pip install -r toolkit\requirements.txt --quiet

echo Starting app...
py -m streamlit run toolkit/app.py
pause
