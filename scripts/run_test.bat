@echo off
echo Running system test...
echo =====================
echo.

REM Set environment variables
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

REM Add current directory to PYTHONPATH
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Run the test
python final_test.py

REM Check the exit code
if errorlevel 1 (
    echo.
    echo Test failed with errors
    exit /b 1
) else (
    echo.
    echo Test completed successfully
    exit /b 0
)
