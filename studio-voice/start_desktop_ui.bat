@echo off
setlocal enabledelayedexpansion

REM Studio Voice Desktop UI Launcher
REM This script starts the desktop GUI for Studio Voice
REM Usage: start_desktop_ui.bat

echo =========================================
echo  Studio Voice Desktop UI Launcher
echo =========================================
echo.

set SCRIPT_DIR=%~dp0
set DESKTOP_UI_DIR=%SCRIPT_DIR%desktop-ui
set VENV_ACTIVATE=%SCRIPT_DIR%nim\Scripts\activate.bat
set PYTHON_SCRIPT=%DESKTOP_UI_DIR%\studio_voice_gui.py

REM Check if virtual environment exists
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment not found at: %VENV_ACTIVATE%
    echo Please ensure the 'nim' virtual environment is properly set up.
    echo You can create it by running: python -m venv nim
    pause
    exit /b 1
)

REM Check if desktop UI script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Desktop UI script not found at: %PYTHON_SCRIPT%
    echo Please ensure the desktop-ui folder exists with studio_voice_gui.py
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_ACTIVATE%"

REM Check if required dependencies are installed
echo Checking dependencies...
python -c "import grpc" 2>nul
if errorlevel 1 (
    echo Installing required dependencies for Studio Voice...
    cd "%SCRIPT_DIR%"
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
) else (
    echo gRPC is installed, checking other dependencies...
    python -c "import soundfile, numpy" 2>nul
    if errorlevel 1 (
        echo Installing missing dependencies...
        cd "%SCRIPT_DIR%"
        pip install -r requirements.txt
    )
)

REM Check if tkinter is available (should be included with Python)
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo ERROR: tkinter not available. Please ensure you have a full Python installation.
    pause
    exit /b 1
)

echo.
echo =========================================
echo  Starting Studio Voice Desktop UI
echo =========================================
echo.

REM Start the desktop application
cd "%DESKTOP_UI_DIR%"
python studio_voice_gui.py

pause
