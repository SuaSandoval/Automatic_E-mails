@echo off
REM ====================================================================
REM BKW Daily Processing Batch Script
REM 
REM This script runs the automated BKW data processing pipeline.
REM Designed to be executed by Windows Task Scheduler.
REM ====================================================================

REM Change to project directory
cd /d "%~dp0"

REM Activate Python environment and run script
REM Option 1: If using conda environment
REM call conda activate your_env_name
REM python run_daily_processing.py

REM Option 2: If using system Python (default)
python run_daily_processing.py

REM Option 3: If using specific Python installation
REM "C:\Path\To\Python\python.exe" run_daily_processing.py

REM Log completion
echo Processing completed at %date% %time%

REM Keep window open if running manually (comment out for scheduled tasks)
REM pause
