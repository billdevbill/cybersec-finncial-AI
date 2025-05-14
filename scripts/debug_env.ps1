Write-Host "PowerShell Debug Script" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green

# Check Python installation
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if ($pythonPath) {
    Write-Host "Python found at: $($pythonPath.Source)"
    & python --version
} else {
    Write-Host "Python not found in PATH" -ForegroundColor Red
}

# Check pip installation
Write-Host "`nChecking pip installation..." -ForegroundColor Yellow
$pipPath = Get-Command pip -ErrorAction SilentlyContinue
if ($pipPath) {
    Write-Host "pip found at: $($pipPath.Source)"
    & pip --version
} else {
    Write-Host "pip not found in PATH" -ForegroundColor Red
}

# List installed packages
Write-Host "`nListing installed packages..." -ForegroundColor Yellow
& python -m pip list

# Check environment variables
Write-Host "`nChecking environment variables..." -ForegroundColor Yellow
$envFile = ".env"
if (Test-Path $envFile) {
    Write-Host ".env file found"
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^[^#]') {
            Write-Host "Found config: $($_ -replace '=.*', '=<value>')"
        }
    }
} else {
    Write-Host ".env file not found" -ForegroundColor Red
}

# List Python files
Write-Host "`nListing Python files in current directory..." -ForegroundColor Yellow
Get-ChildItem -Filter "*.py" | ForEach-Object {
    Write-Host $_.Name
}
