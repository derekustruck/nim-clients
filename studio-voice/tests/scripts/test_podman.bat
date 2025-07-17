@echo off

REM Simple test for argument parsing
if "%1"=="--status" (
    echo Status check requested
    exit /b 0
)

echo Default action - would start container
