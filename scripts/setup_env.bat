@echo off
echo Setting up Python environment...

:: Check Python installation
where python
if %ERRORLEVEL% NEQ 0 (
    echo Python not found in PATH
    exit /b 1
)

:: Create virtual environment
python -m venv venv --clear
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment
    exit /b 1
)

:: Activate virtual environment and install requirements
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment
    exit /b 1
)

:: Install requirements
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements
    exit /b 1
)

:: Run minimal test
python minimal_test.py
if %ERRORLEVEL% NEQ 0 (
    echo Test failed
    exit /b 1
)

echo Setup completed successfully
