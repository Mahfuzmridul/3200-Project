@echo off
REM Windows Batch Script to run the Log & PCAP Analyzer
REM This script checks for admin privileges and runs the application

echo ========================================
echo   Unified Log ^& PCAP Analyzer v2.0
echo ========================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
    echo.
) else (
    echo [WARNING] Not running as Administrator
    echo Some features may not work properly.
    echo.
    echo To run as Administrator:
    echo   1. Right-click this file
    echo   2. Select "Run as administrator"
    echo.
    pause
)

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo [OK] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found
    echo Using system Python...
)

echo.
echo Starting application...
echo.

REM Run the main application
python main.py

REM Pause if there was an error
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Application exited with errors
    pause
)
