@echo off
setlocal enabledelayedexpansion

REM Studio Voice NIM Server Test Script
REM Tests if the Studio Voice server is running and accessible

echo =========================================
echo  Studio Voice NIM Server Test
echo =========================================
echo.

REM Check if virtual environment exists
set VENV_ACTIVATE=%~dp0nim\Scripts\activate.bat
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment not found at: %VENV_ACTIVATE%
    echo Please ensure the 'nim' virtual environment is properly set up.
    pause
    exit /b 1
)

echo [1/4] Testing port connectivity...
netstat -an | findstr :8001 >nul 2>&1
if errorlevel 1 (
    echo     ❌ Port 8001 is not listening
    echo     The Studio Voice container may not be running.
    echo.
    echo     To start the container, run: studio_voice_server.bat
    pause
    exit /b 1
) else (
    echo     ✅ Port 8001 is listening
)

netstat -an | findstr :8000 >nul 2>&1
if errorlevel 1 (
    echo     ❌ Port 8000 is not listening
) else (
    echo     ✅ Port 8000 is listening
)

echo.
echo [2/4] Testing gRPC connection...
call "%VENV_ACTIVATE%" >nul 2>&1
python -c "import grpc; channel = grpc.insecure_channel('127.0.0.1:8001'); grpc.channel_ready_future(channel).result(timeout=5); print('     ✅ gRPC server is responding')" 2>nul
if errorlevel 1 (
    echo     ❌ gRPC server is not responding
    echo     The server may be starting up or there's a configuration issue.
    pause
    exit /b 1
)

echo.
echo [3/4] Testing Studio Voice imports...
python -c "import sys; sys.path.append('interfaces/studio_voice'); import studiovoice_pb2, studiovoice_pb2_grpc; print('     ✅ Studio Voice modules imported successfully')" 2>nul
if errorlevel 1 (
    echo     ❌ Failed to import Studio Voice modules
    echo     Check that the interfaces are properly generated.
    pause
    exit /b 1
)

echo.
echo [4/4] Testing sample processing capability...
if exist "assets\studio_voice_48k_input.wav" (
    echo     ✅ Sample audio file found
    echo     Testing with sample file...
    
    python scripts\studio_voice.py --input "assets\studio_voice_48k_input.wav" --output "test_output.wav" --model-type 48k-hq >nul 2>&1
    if errorlevel 1 (
        echo     ❌ Sample processing failed
        echo     There may be an issue with the server or configuration.
    ) else (
        echo     ✅ Sample processing successful
        if exist "test_output.wav" del "test_output.wav"
    )
) else (
    echo     ⚠️  Sample audio file not found, skipping processing test
)

echo.
echo =========================================
echo         SERVER STATUS: READY
echo =========================================
echo.
echo The Studio Voice NIM server is running and ready to process audio files.
echo.
echo Server endpoints:
echo   - gRPC: 127.0.0.1:8001
echo   - HTTP: 127.0.0.1:8000
echo.
echo You can now run: process_audio_batch.bat [source_folder]
echo.
pause
