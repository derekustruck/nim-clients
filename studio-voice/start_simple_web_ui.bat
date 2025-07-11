@echo off
setlocal enabledelayedexpansion

REM Studio Voice Simple Web UI Launcher
REM This script starts the simplified web-based user interface for Studio Voice
REM Uses basic Flask without WebSockets to avoid compatibility issues
REM Usage: start_simple_web_ui.bat

echo =========================================
echo  Studio Voice Simple Web UI Launcher
echo =========================================
echo.

set SCRIPT_DIR=%~dp0
set WEB_UI_DIR=%SCRIPT_DIR%web-ui
set VENV_ACTIVATE=%SCRIPT_DIR%nim\Scripts\activate.bat
set FLASK_APP=%WEB_UI_DIR%\simple_app.py

REM Check if virtual environment exists
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment not found at: %VENV_ACTIVATE%
    echo Please ensure the 'nim' virtual environment is properly set up.
    echo You can create it by running: python -m venv nim
    pause
    exit /b 1
)

REM Check if web UI directory exists
if not exist "%WEB_UI_DIR%" (
    echo ERROR: Web UI directory not found at: %WEB_UI_DIR%
    echo Please ensure the web-ui folder exists with simple_app.py
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_ACTIVATE%"

REM Install simple web UI requirements if needed
echo Checking simple web UI dependencies...
cd "%WEB_UI_DIR%"

REM Check if Flask is installed
python -c "import flask; print('Flask version:', flask.__version__)" 2>nul
if errorlevel 1 (
    echo Installing simple web UI dependencies...
    pip install -r simple_requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Flask is installed and working!
)

REM Create uploads and outputs directories
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs

echo.
echo =========================================
echo  Starting Studio Voice Simple Web UI
echo =========================================
echo.
echo Simple Web UI will be available at: http://127.0.0.1:5000
echo.
echo Features:
echo - Upload multiple audio files
echo - Configure processing settings
echo - Monitor job progress
echo - Download enhanced files
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python simple_app.py

pause
