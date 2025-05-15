param(
    [Parameter(Mandatory=$false)]
    [int]$BackupInterval = 24,
    
    [Parameter(Mandatory=$false)]
    [int]$RetentionDays = 7,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupDir = ".\backups"
)

# Importar módulos requeridos
Import-Module PSScheduledJob

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Crear directorio de backups si no existe
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir
}

# Función para ejecutar el backup
function Invoke-MemoryBackup {
    param(
        [string]$BackupDir,
        [int]$RetentionDays
    )
    
    $pythonScript = @"
import asyncio
from pathlib import Path
from src.mar_disrupcion.core.memory_backup import MemoryBackup
from src.mar_disrupcion.core.memory_system import AdvancedMemorySystem

async def run_backup():
    config = {
        'memory': {
            'retention_period': 7200,
            'context_depth': 8,
            'confidence_threshold': 0.75,
            'cache_size': 2048
        },
        'neural': {
            'learning_rate': 0.001,
            'lstm_hidden_size': 256,
            'lstm_num_layers': 2,
            'dropout_rate': 0.2
        }
    }
    
    system = AdvancedMemorySystem(config)
    backup = MemoryBackup(system.db_path, Path('$BackupDir'))
    
    await backup.create_backup()
    await backup._cleanup_old_backups(keep=$RetentionDays)

asyncio.run(run_backup())
"@
    
    $pythonScript | python
}

# Registrar tarea programada
$jobName = "MemorySystemBackup"
$trigger = New-JobTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours $BackupInterval) -RepeatIndefinitely
$options = New-ScheduledJobOption -RunElevated -RequireNetwork

Register-ScheduledJob -Name $jobName -ScriptBlock {
    param($BackupDir, $RetentionDays)
    Invoke-MemoryBackup -BackupDir $BackupDir -RetentionDays $RetentionDays
} -Trigger $trigger -ScheduledJobOption $options -ArgumentList $BackupDir, $RetentionDays

Write-Host "Tarea de backup programada cada $BackupInterval horas"
Write-Host "Los backups se guardarán en: $BackupDir"
Write-Host "Se mantendrán los últimos $RetentionDays backups"

# Ejecutar backup inicial
Write-Host "Ejecutando backup inicial..."
Invoke-MemoryBackup -BackupDir $BackupDir -RetentionDays $RetentionDays
