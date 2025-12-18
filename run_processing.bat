@echo off
REM ====================================================================
REM BKW Daily Processing Batch Script
REM 
REM This script runs the automated BKW data processing pipeline.
REM Designed to be executed by Windows Task Scheduler.
REM ====================================================================

REM Change to project directory
cd /d "%~dp0"

REM Ensure logs directory exists
if not exist "%~dp0logs" mkdir "%~dp0logs"

REM Log start time
echo [%date% %time%] BKW Processing Started >> "%~dp0logs\task_scheduler.log"

REM Pre-sync INCOMING (ensure new data is downloaded before processing)
echo [%date% %time%] Forcing OneDrive download (incoming)... >> "%~dp0logs\task_scheduler.log"
powershell.exe -ExecutionPolicy Bypass -File "%~dp0force_onedrive_sync.ps1" -FolderPath "C:\Users\sandovalsu\OneDrive - NOTUS energy GmbH\PowerAutomate\BKW test\Dynamic_folder\incoming" >> "%~dp0logs\task_scheduler.log" 2>&1
echo [%date% %time%] Incoming sync completed (exit code: %ERRORLEVEL%) >> "%~dp0logs\task_scheduler.log"

REM Run with absolute Python path (works even when user not logged on)
"C:\Users\sandovalsu\AppData\Local\Programs\Python\Python311\python.exe" "%~dp0run_daily_processing.py" >> "%~dp0logs\task_scheduler.log" 2>&1

REM Post-sync OUTGOING (upload processed files)
echo [%date% %time%] Forcing OneDrive upload (outgoing)... >> "%~dp0logs\task_scheduler.log"
powershell.exe -ExecutionPolicy Bypass -File "%~dp0force_onedrive_sync.ps1" -FolderPath "C:\Users\sandovalsu\OneDrive - NOTUS energy GmbH\PowerAutomate\BKW test\Dynamic_folder\outgoing" >> "%~dp0logs\task_scheduler.log" 2>&1
echo [%date% %time%] Outgoing sync completed (exit code: %ERRORLEVEL%) >> "%~dp0logs\task_scheduler.log"

REM Log completion
echo [%date% %time%] Processing completed - Exit code: %ERRORLEVEL% >> "%~dp0logs\task_scheduler.log"
echo.>> "%~dp0logs\task_scheduler.log"
