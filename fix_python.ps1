# Force PowerShell to use UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Python Environment Diagnostic Tool" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

# Function to test Python execution
function Test-PythonExecution {
    param (
        [string]$Command
    )
    try {
        $result = & python -c $Command 2>&1
        return $result
    }
    catch {
        return $_.Exception.Message
    }
}

# Check Python installation
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if ($pythonPath) {
    Write-Host "Python found at: $($pythonPath.Source)" -ForegroundColor Green
    $version = Test-PythonExecution "import sys; print(sys.version)"
    Write-Host "Python version: $version" -ForegroundColor Green
}
else {
    Write-Host "Python not found in PATH!" -ForegroundColor Red
    exit 1
}

# Check pip and installed packages
Write-Host "`nChecking pip and packages..." -ForegroundColor Yellow
$packages = python -m pip list
Write-Host "Installed packages:" -ForegroundColor Green
$packages | Where-Object { $_ -match 'anthropic|openai|python-dotenv' }

# Check environment variables
Write-Host "`nChecking environment variables..." -ForegroundColor Yellow
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
Write-Host "PYTHONPATH: $env:PYTHONPATH"
Write-Host "PYTHONHOME: $env:PYTHONHOME"
Write-Host "PYTHONIOENCODING: $env:PYTHONIOENCODING"

# Try to run our test script
Write-Host "`nAttempting to run test script..." -ForegroundColor Yellow
try {
    python final_test.py
    Write-Host "Test script executed successfully" -ForegroundColor Green
}
catch {
    Write-Host "Error running test script: $_" -ForegroundColor Red
}
