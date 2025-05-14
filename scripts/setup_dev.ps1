# PowerShell script for setting up development environment
param (
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

# Install development tools
Write-Status "Installing development dependencies..."
.\install.ps1 -dev

# Configure git hooks
Write-Status "Setting up git hooks..."
if (-not (Test-Path ".git")) {
    git init
}

$preCommitHook = @"
#!/bin/sh
# Run tests before commit
python -m pytest || exit 1

# Run code formatting
python -m black . || exit 1
python -m isort . || exit 1

# Run type checking
python -m mypy . || exit 1

# Run linting
python -m pylint AI1.py core tools integrations || exit 1
"@

$preCommitHookPath = ".git/hooks/pre-commit"
$preCommitHook | Out-File -FilePath $preCommitHookPath -Encoding UTF8
Write-Success "Git hooks configured"

# Configure VS Code settings
Write-Status "Configuring VS Code settings..."
$vsCodeSettings = @"
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
"@

if (-not (Test-Path ".vscode")) {
    New-Item -ItemType Directory -Path ".vscode" | Out-Null
}
$vsCodeSettings | Out-File -FilePath ".vscode/settings.json" -Encoding UTF8
Write-Success "VS Code settings configured"

# Create tasks.json
$tasks = @"
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "python -m pytest",
            "group": {
                "kind": "test",
                "isDefault": true
            }
        },
        {
            "label": "Start Web App",
            "type": "shell",
            "command": "streamlit run app.py",
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "Format Code",
            "type": "shell",
            "command": "python -m black . && python -m isort .",
            "group": "none"
        },
        {
            "label": "Type Check",
            "type": "shell",
            "command": "python -m mypy .",
            "group": "none"
        }
    ]
}
"@
$tasks | Out-File -FilePath ".vscode/tasks.json" -Encoding UTF8
Write-Success "VS Code tasks configured"

Write-Success "Development environment setup completed!"
Write-Host ""
Write-Host "Recommended VS Code extensions:"
Write-Host "1. ms-python.python"
Write-Host "2. ms-python.vscode-pylance"
Write-Host "3. ms-python.black-formatter"
Write-Host "4. ms-python.pylint"
Write-Host "5. ms-python.isort"
Write-Host "6. ms-toolsai.jupyter"
