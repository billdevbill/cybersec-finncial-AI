# PowerShell script for installing and setting up the AI system
param (
    [switch]$dev,
    [switch]$update,
    [switch]$force
)

Set-ExecutionPolicy Bypass -Scope Process -Force
$ErrorActionPreference = "Stop"

function Write-Status {
    param($Message)
    Write-Host "🔄 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Check Python version
try {
    $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([version]$pythonVersion -lt [version]"3.9") {
        Write-Error "Python 3.9 or higher is required. Current version: $pythonVersion"
        exit 1
    }
    Write-Success "Python $pythonVersion detected"
} catch {
    Write-Error "Python 3.9 or higher is required but not found"
    exit 1
}

# Create and activate virtual environment
Write-Status "Creating virtual environment..."
if (Test-Path "venv") {
    if ($force) {
        Remove-Item -Recurse -Force "venv"
    } elseif (-not $update) {
        Write-Error "Virtual environment already exists. Use -update to upgrade or -force to recreate."
        exit 1
    }
}

if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Activate virtual environment
. .\venv\Scripts\Activate.ps1
Write-Success "Virtual environment activated"

# Upgrade pip
Write-Status "Upgrading pip..."
python -m pip install --upgrade pip

# Create required directories
Write-Status "Creating required directories..."
$directories = @("memory", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Success "Created directory: $dir"
    }
}

# Install dependencies
Write-Status "Installing dependencies..."
if ($dev) {
    python -m pip install -e ".[dev]"
    Write-Success "Development dependencies installed"
} else {
    python -m pip install -e "."
    Write-Success "Base dependencies installed"
}

# Verify installation
Write-Status "Verifying installation..."
try {
    python -c "import anthropic, openai, torch, streamlit, numpy, pandas"
    Write-Success "Core packages verified"
} catch {
    Write-Error "Package verification failed: $_"
    exit 1
}

# Configure environment
if (-not (Test-Path ".env")) {
    Write-Status "Creating .env file..."
    @"
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_MODEL=claude-3-opus-20240229
OPENAI_MODEL=gpt-4-turbo-preview
MAX_TOKENS=64826
TEMPERATURE=1
MEMORY_RETENTION_PERIOD=14400
CONTEXT_DEPTH=8
MEMORY_CONFIDENCE_THRESHOLD=0.75
CACHE_SIZE=2048
LEARNING_RATE=0.0005
LSTM_HIDDEN_SIZE=1024
LSTM_NUM_LAYERS=3
DROPOUT_RATE=0.2
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Status "Created .env file - please edit with your API keys"
}

Write-Success "Installation completed successfully!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Edit the .env file with your API keys"
Write-Host "2. Run 'pytest' to verify everything works"
Write-Host "3. Start the web interface with 'streamlit run app.py'"
