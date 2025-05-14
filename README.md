# Sistema Avanzado de Análisis y Seguridad

Este sistema implementa una interfaz avanzada con Claude de Anthropic, incorporando herramientas especializadas para análisis de seguridad, generación de entropía cuántica, detección de anomalías financieras y ofuscación de código.

## Configuración del Entorno

1. Crear y activar el entorno virtual:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Instalar dependencias:
```powershell
pip install -r requirements.txt
```

3. Configurar el archivo .env:
```env
ANTHROPIC_API_KEY=tu_api_key_aquí
ANTHROPIC_MODEL=claude-3-opus-20240229
MAX_TOKENS=64826
TEMPERATURE=1.0

# Configuración de herramientas
NETWORK_SCAN_TIMEOUT=30
ENTROPY_BUFFER_SIZE=4096
FINANCIAL_ANALYSIS_THRESHOLD=0.85
CODE_OBFUSCATION_SEED=42
```

## Uso del Sistema

Para ejecutar una prueba básica del sistema:
```powershell
python test_system.py
```

## Herramientas Disponibles

1. NetworkVulnerabilityScanner
   - Escaneo de vulnerabilidades en red
   - Múltiples niveles de profundidad
   - Modo sigiloso disponible

2. QuantumEntropyOracle
   - Generación de entropía pseudocuántica
   - Múltiples fuentes de entropía simuladas
   - Configurable en tamaño y calidad

3. FinancialAnomalyDetector
   - Detección de anomalías en transacciones
   - Perfiles especializados de análisis
   - Sensibilidad ajustable

4. CodeObfuscator
   - Ofuscación de código fuente
   - Soporte para múltiples lenguajes
   - Niveles variables de ofuscación

## Seguridad

- Todas las claves API deben mantenerse seguras
- El archivo .env nunca debe compartirse
- Se recomienda usar un entorno virtual aislado

## Logging

El sistema mantiene logs detallados en `ai_system.log` para debugging y auditoría.
