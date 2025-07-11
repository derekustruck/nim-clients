@echo off

REM Check for test argument
if "%1"=="--test" (
    echo Redirecting to server test script
    call test_server.bat
    exit /b 0
)

REM Check for status argument
if "%1"=="--status" (
    echo =========================================
    echo  Studio Voice NIM Container Status
    echo =========================================
    echo.
    echo Checking container status in WSL NVIDIA-workbench
    echo.
    echo All containers:
    wsl -d NVIDIA-workbench -e bash -c "podman ps -a"
    echo.
    echo Studio Voice specific:
    wsl -d NVIDIA-workbench -e bash -c "podman ps -a --filter name=studio-voice"
    echo.
    pause
    exit /b 0
)

REM Check for stop argument
if "%1"=="--stop" (
    echo =========================================
    echo  Stopping Studio Voice NIM Container
    echo =========================================
    echo.
    echo Stopping container in WSL NVIDIA-workbench
    echo Command: podman stop studio-voice
    wsl -d NVIDIA-workbench -e bash -c "podman stop studio-voice"
    if errorlevel 1 (
        echo.
        echo Error stopping container. Possible reasons:
        echo   - Container is not running
        echo   - Container name studio-voice not found
        echo   - WSL distribution NVIDIA-workbench not available
        echo.
        echo Checking container status
        wsl -d NVIDIA-workbench -e bash -c "podman ps -a --filter name=studio-voice"
    ) else (
        echo.
        echo Container stopped successfully.
        echo.
        echo Container status:
        wsl -d NVIDIA-workbench -e bash -c "podman ps -a --filter name=studio-voice"
    )
    echo.
    pause
    exit /b 0
)

echo Opening WSL NVIDIA-workbench terminal and starting container
echo.
echo =========================================
echo  Starting Studio Voice NIM Container
echo =========================================
echo.
echo Container Details:
echo   - Name: studio-voice
echo   - GPU: All available NVIDIA GPUs
echo   - Memory: 8GB shared memory
echo   - Ports: 8000 HTTP, 8001 gRPC
echo   - File size limit: 36MB
echo   - Streaming: Disabled
echo.
echo Note: Make sure NGC_API_KEY environment variable is set in WSL
echo.
echo Usage:
echo   podman.bat          - Start the container
echo   podman.bat --test   - Test if server is running
echo   podman.bat --stop   - Stop the container
echo   podman.bat --status - Check container status
echo.

REM Start the container in WSL
echo Starting container
echo Command: podman start studio-voice
wsl -d NVIDIA-workbench -e bash -c "podman start studio-voice"
if errorlevel 1 (
    echo.
    echo Error starting container. Possible reasons:
    echo   - Container studio-voice does not exist
    echo   - Container is already running
    echo   - WSL distribution NVIDIA-workbench not available
    echo   - Podman is not installed in WSL
    echo.
    echo Checking container status
    wsl -d NVIDIA-workbench -e bash -c "podman ps -a --filter name=studio-voice"
    echo.
    echo If container doesn't exist, you may need to create it first with:
    echo   wsl -d NVIDIA-workbench -e bash -c "podman run -d --name studio-voice [options]"
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo Container started successfully!
    echo.
    echo Current container status:
    wsl -d NVIDIA-workbench -e bash -c "podman ps --filter name=studio-voice"
    echo.
    echo Server should be available at:
    echo   - HTTP: http://localhost:8000
    echo   - gRPC: localhost:8001
    echo.
    echo To test the server, run: podman.bat --test
    echo.
    pause
)
