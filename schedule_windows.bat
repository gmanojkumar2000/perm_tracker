@echo off
REM USCIS Tracker - Windows Task Scheduler Script
REM This script runs the USCIS tracker daily

echo Starting USCIS Tracker...
cd /d "D:\Mano_Codebase\uscis_application_status_tracker"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the daily test
python tests\daily_test.py

REM Run the main application
python main.py

echo USCIS Tracker completed at %date% %time%
