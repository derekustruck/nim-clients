@echo off
setlocal enabledelayedexpansion

REM Studio Voice Audio Batch Processing Script
REM This script processes multiple audio files using the Studio Voice NIM
REM Supports nested directory structures and uses the nim virtual environment
REM Usage: process_audio_batch.bat [source_root] [options]

REM Configuration
set SOURCE_ROOT=%1
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%scripts\studio_voice.py
set VENV_ACTIVATE=%SCRIPT_DIR%nim\Scripts\activate.bat
set SERVER_TARGET=127.0.0.1:8001
set MODEL_TYPE=48k-hq
set STREAMING_MODE=false
set MAX_FILE_SIZE=36700160
set DRY_RUN=false

REM Parse additional arguments - shift past the first required argument
if not "%1"=="" shift
:parse_args
if "%1"=="--model-type" (
    set MODEL_TYPE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--streaming" (
    set STREAMING_MODE=true
    shift
    goto parse_args
)
if "%1"=="--dry-run" (
    set DRY_RUN=true
    shift
    goto parse_args
)
if not "%1"=="" (
    shift
    goto parse_args
)

REM Display usage if no arguments provided
if "%SOURCE_ROOT%"=="" (
    echo =========================================
    echo  Studio Voice Audio Batch Processor
    echo =========================================
    echo.
    echo Usage: %0 [source_root] [options]
    echo.
    echo Arguments:
    echo   source_root    Root directory containing audio files to process
    echo.
    echo Options:
    echo   --model-type   Model type: 48k-hq, 48k-ll, 16k-hq ^(default: 48k-hq^)
    echo   --streaming    Enable streaming mode
    echo   --dry-run      Show what would be processed without actually processing
    echo.
    echo Examples:
    echo   %0 "D:\CaptureManager\Media"
    echo   %0 "D:\CaptureManager\Media" --model-type 16k-hq
    echo   %0 "D:\CaptureManager\Media" --streaming --dry-run
    echo.
    echo Model Types:
    echo   48k-hq  - 48kHz High Quality ^(default^)
    echo   48k-ll  - 48kHz Low Latency
    echo   16k-hq  - 16kHz High Quality
    echo.
    echo File Management:
    echo   - Enhanced audio REPLACES the original file ^(same name and location^)
    echo   - Original files are moved to "../original audio/" folders
    echo   - Directory structure is preserved
    echo.
    echo Directory Structure Example:
    echo   Before: "D:\CaptureManager\Media\MySlate_7\Audio\Audio\audio.wav"
    echo   After:  "D:\CaptureManager\Media\MySlate_7\Audio\Audio\audio.wav" ^(enhanced^)
    echo           "D:\CaptureManager\Media\MySlate_7\Audio\original audio\audio.wav" ^(original^)
    exit /b 1
)

REM Validate source directory
if not exist "%SOURCE_ROOT%" (
    echo ERROR: Source directory does not exist: %SOURCE_ROOT%
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment not found at: %VENV_ACTIVATE%
    echo Please ensure the 'nim' virtual environment is properly set up.
    exit /b 1
)

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: studio_voice.py not found at: %PYTHON_SCRIPT%
    echo Please ensure you're running this script from the studio-voice directory
    exit /b 1
)

echo =========================================
echo  Studio Voice Audio Batch Processor
echo =========================================
echo Source Directory: %SOURCE_ROOT%
echo Model Type: %MODEL_TYPE%
echo Streaming Mode: %STREAMING_MODE%
echo Server Target: %SERVER_TARGET%
echo Using Virtual Environment: %VENV_ACTIVATE%
echo File Management: Replace originals, backup to "original audio" folders
echo.

REM Activate virtual environment and test server connectivity
echo Activating virtual environment and testing server connectivity...
call "%VENV_ACTIVATE%"
python -c "import grpc; channel = grpc.insecure_channel('%SERVER_TARGET%'); grpc.channel_ready_future(channel).result(timeout=5); print('Server is ready')" 2>nul
if errorlevel 1 (
    echo ERROR: Cannot connect to Studio Voice server at %SERVER_TARGET%
    echo Please ensure the NIM container is running with studio_voice_server.bat:
    echo.
    echo   podman run -it --rm --name=studio-voice \
    echo     --device nvidia.com/gpu=all \
    echo     --shm-size=8GB \
    echo     -e NGC_API_KEY=your_api_key \
    echo     -e FILE_SIZE_LIMIT=36700160 \
    echo     -e STREAMING=false \
    echo     -p 8000:8000 \
    echo     -p 8001:8001 \
    echo     nvcr.io/nim/nvidia/maxine-studio-voice:latest
    exit /b 1
)

echo Server is ready. Starting batch processing...
echo.

REM Initialize counters
set /a TOTAL_FILES=0
set /a PROCESSED_FILES=0
set /a FAILED_FILES=0
set /a SKIPPED_FILES=0

REM Process audio files recursively through all subdirectories
echo Scanning for audio files recursively...
echo.

for /r "%SOURCE_ROOT%" %%F in (*.wav *.mp3 *.flac *.m4a *.aac) do (
    call :process_file "%%F"
)

goto :display_summary

:process_file
set "CURRENT_FILE=%~1"
set /a TOTAL_FILES+=1

REM Get file info
for %%i in ("%CURRENT_FILE%") do (
    set "FILENAME=%%~ni"
    set "EXTENSION=%%~xi"
    set "FILE_DIR=%%~dpi"
)

REM Create original backup directory (one level up from current file)
for %%i in ("%FILE_DIR%.") do set "PARENT_DIR=%%~dpi"
set "ORIGINAL_DIR=%PARENT_DIR%original audio"

echo [%TOTAL_FILES%] Processing: %CURRENT_FILE%
echo     Will replace original and backup to: %ORIGINAL_DIR%\%FILENAME%%EXTENSION%

REM Check file size
for %%s in ("%CURRENT_FILE%") do set FILE_SIZE=%%~zs
if %FILE_SIZE% GTR %MAX_FILE_SIZE% (
    echo     WARNING: File exceeds size limit ^(%FILE_SIZE% bytes^), skipping
    set /a SKIPPED_FILES+=1
    echo.
    goto :eof
)

REM Handle non-WAV files
if /i not "%EXTENSION%"==".wav" (
    echo     NOTE: Studio Voice requires WAV format. Skipping %EXTENSION% file.
    echo     Convert with: ffmpeg -i "%CURRENT_FILE%" "%CURRENT_FILE:~0,-4%.wav"
    set /a SKIPPED_FILES+=1
    echo.
    goto :eof
)

if "%DRY_RUN%"=="true" (
    echo     DRY RUN: Would process this file
    echo.
    goto :eof
)

REM Create original backup directory
if not exist "%ORIGINAL_DIR%" mkdir "%ORIGINAL_DIR%"

REM Create temporary output file
set "TEMP_OUTPUT=%CURRENT_FILE%.tmp"

REM Build Python command
set "PYTHON_CMD=python "%PYTHON_SCRIPT%" --input "%CURRENT_FILE%" --output "%TEMP_OUTPUT%" --model-type %MODEL_TYPE% --target %SERVER_TARGET%"
if "%STREAMING_MODE%"=="true" (
    set "PYTHON_CMD=%PYTHON_CMD% --streaming"
)

REM Execute processing
echo     Processing with Studio Voice...
%PYTHON_CMD% >nul 2>&1

if errorlevel 1 (
    echo     ERROR: Processing failed
    set /a FAILED_FILES+=1
    REM Clean up temp file
    if exist "%TEMP_OUTPUT%" del "%TEMP_OUTPUT%"
    REM Show detailed error
    echo     Detailed error:
    %PYTHON_CMD%
) else (
    echo     SUCCESS: Processing completed
    REM Move original to backup location
    move "%CURRENT_FILE%" "%ORIGINAL_DIR%\%FILENAME%%EXTENSION%" >nul
    if errorlevel 1 (
        echo     ERROR: Could not move original file to backup location
        set /a FAILED_FILES+=1
        if exist "%TEMP_OUTPUT%" del "%TEMP_OUTPUT%"
    ) else (
        REM Move processed file to original location
        move "%TEMP_OUTPUT%" "%CURRENT_FILE%" >nul
        if errorlevel 1 (
            echo     ERROR: Could not move processed file to original location
            REM Try to restore original
            move "%ORIGINAL_DIR%\%FILENAME%%EXTENSION%" "%CURRENT_FILE%" >nul
            set /a FAILED_FILES+=1
        ) else (
            echo     SUCCESS: Enhanced audio replaced original, backup saved
            set /a PROCESSED_FILES+=1
        )
    )
)

echo.
goto :eof

:display_summary
REM Display final summary
echo =========================================
echo         PROCESSING SUMMARY
echo =========================================
echo Total Files Found: %TOTAL_FILES%
echo Successfully Processed: %PROCESSED_FILES%
echo Failed: %FAILED_FILES%
echo Skipped: %SKIPPED_FILES%
echo.

if %PROCESSED_FILES% GTR 0 (
    echo Enhanced audio files have replaced the originals in-place.
    echo Original files have been moved to "original audio" folders.
    echo Processed files maintain the same names and locations.
)

if %FAILED_FILES% GTR 0 (
    echo Some files failed to process. Check the error messages above.
    echo.
    echo Common issues:
    echo   - Server not running ^(run studio_voice_server.bat^)
    echo   - File format not supported ^(convert to WAV^)
    echo   - File size exceeds limit ^(36MB max^)
    echo   - Sample rate mismatch ^(check model requirements^)
    echo   - File permissions ^(ensure write access^)
)

echo.
echo File Management Summary:
echo   - Enhanced files replace originals ^(same filename and location^)
echo   - Original files moved to "../original audio/" folders
echo   - Directory structure preserved
echo.
echo Batch processing completed!
if not "%DRY_RUN%"=="true" pause
