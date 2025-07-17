@echo off
REM Quick Studio Voice NIM Server Starter
REM This script starts the NVIDIA Studio Voice NIM server if it's not running

echo =========================================
echo  Studio Voice NIM Server Quick Start
echo =========================================
echo.

REM Check if server is already running
netstat -an | findstr :8001 >nul 2>&1
if not errorlevel 1 (
    echo ✓ Studio Voice NIM server is already running on port 8001
    echo.
    pause
    exit /b 0
)

echo Starting NVIDIA Studio Voice NIM server...
echo.

REM Start the server using the main server script
call studio_voice_server.bat

echo.
echo Server startup complete. The Web UI should now be able to connect.
pause
