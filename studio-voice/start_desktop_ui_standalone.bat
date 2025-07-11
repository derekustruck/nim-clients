@echo off
setlocal enabledelayedexpansion

REM Studio Voice Desktop UI Launcher - Standalone Version
REM This script starts the standalone desktop GUI for Studio Voice
REM Includes dependency checking and automatic installation
REM Usage: start_desktop_ui_standalone.bat

echo =========================================
echo  Studio Voice Desktop UI - Standalone
echo =========================================
echo.

set SCRIPT_DIR=%~dp0
set DESKTOP_UI_DIR=%SCRIPT_DIR%desktop-ui
set VENV_ACTIVATE=%SCRIPT_DIR%nim\Scripts\activate.bat
set PYTHON_SCRIPT=%DESKTOP_UI_DIR%\studio_voice_gui_standalone.py

REM Check if virtual environment exists
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment not found at: %VENV_ACTIVATE%
    echo Please ensure the 'nim' virtual environment is properly set up.
    echo You can create it by running: python -m venv nim
    pause
    exit /b 1
)

REM Check if standalone desktop UI script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Standalone Desktop UI script not found at: %PYTHON_SCRIPT%
    echo Please ensure the desktop-ui folder exists with studio_voice_gui_standalone.py
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_ACTIVATE%"

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
echo Features:
echo - Automatic dependency checking
echo - In-place file processing
echo - Backup management
echo - Progress tracking
echo.
echo Note: Use 'Check Dependencies' button in the app if you encounter any import errors
echo.

REM Start the desktop application
cd "%DESKTOP_UI_DIR%"
python studio_voice_gui_standalone.py

pause
