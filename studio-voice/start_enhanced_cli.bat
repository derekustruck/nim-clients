@echo off
setlocal enabledelayedexpansion

REM Studio Voice Enhanced CLI Launcher
REM This script starts the enhanced command-line interface for Studio Voice
REM Usage: start_enhanced_cli.bat [arguments]

set SCRIPT_DIR=%~dp0
set CLI_DIR=%SCRIPT_DIR%enhanced-cli
set VENV_ACTIVATE=%SCRIPT_DIR%nim\Scripts\activate.bat
set PYTHON_SCRIPT=%CLI_DIR%\studio_voice_cli.py

REM Check if virtual environment exists
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment not found at: %VENV_ACTIVATE%
    echo Please ensure the 'nim' virtual environment is properly set up.
    pause
    exit /b 1
)

REM Check if CLI script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Enhanced CLI script not found at: %PYTHON_SCRIPT%
    echo Please ensure the enhanced-cli folder exists with studio_voice_cli.py
    pause
    exit /b 1
)

REM Activate virtual environment
call "%VENV_ACTIVATE%"

REM Install enhanced CLI requirements if needed
echo Checking enhanced CLI dependencies...
cd "%CLI_DIR%"

REM Check if rich is installed
python -c "import rich" 2>nul
if errorlevel 1 (
    echo Installing enhanced CLI dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo =========================================
echo  Studio Voice Enhanced CLI
echo =========================================
echo.

REM Pass all arguments to the Python script
python studio_voice_cli.py %*

REM Only pause if no arguments were provided (interactive mode)
if "%~1"=="" pause
