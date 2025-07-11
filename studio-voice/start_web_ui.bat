@echo off
setlocal enabledelayedexpansion

REM Studio Voice Web UI Launcher
REM This script starts the web-based user interface for Studio Voice
REM Usage: start_web_ui.bat

echo =========================================
echo  Studio Voice Web UI Launcher
echo =========================================
echo.

set SCRIPT_DIR=%~dp0
set WEB_UI_DIR=%SCRIPT_DIR%web-ui
set VENV_ACTIVATE=%SCRIPT_DIR%nim\Scripts\activate.bat
set FLASK_APP=%WEB_UI_DIR%\app.py

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
    echo Please ensure the web-ui folder exists with app.py
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_ACTIVATE%"

REM Install web UI requirements if needed
echo Checking web UI dependencies...
cd "%WEB_UI_DIR%"

REM Check if Flask is installed and compatible
python -c "import flask; print('Flask version:', flask.__version__)" 2>nul
if errorlevel 1 (
    echo Installing web UI dependencies...
    pip install --upgrade -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Trying to force reinstall...
        pip install --force-reinstall -r requirements.txt
        if errorlevel 1 (
            echo ERROR: Failed to install dependencies after force reinstall
            pause
            exit /b 1
        )
    )
) else (
    echo Flask is installed, checking for compatibility issues...
    python -c "import flask_socketio" 2>nul
    if errorlevel 1 (
        echo Installing missing or incompatible dependencies...
        pip install --upgrade -r requirements.txt
    )
)

REM Create uploads and outputs directories
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs

echo.
echo =========================================
echo  Starting Studio Voice Web UI
echo =========================================
echo.
echo Web UI will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app.py

pause
