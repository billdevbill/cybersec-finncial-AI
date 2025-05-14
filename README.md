# CyberSec Financial AI - Sistema Avanzado de Análisis

Sistema avanzado que integra Claude de Anthropic y GPT-4 para análisis de seguridad, detección de anomalías financieras, generación de entropía cuántica y protección de código. Diseñado para proporcionar análisis profundo y protección robusta en entornos financieros y de seguridad.

## Configuración del Entorno

### Configuración Inicial

1. Crear y activar el entorno virtual:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Instalar dependencias:
```powershell
pip install -r requirements.txt
```

### Configuración de Variables de Entorno

1. Copiar el archivo de plantilla de variables de entorno:
```powershell
Copy-Item .env.template .env
```

2. Editar el archivo `.env` con tus propias claves API y configuraciones:
   - Reemplazar `your_anthropic_api_key_here` con tu clave API de Anthropic
   - Reemplazar `your_openai_api_key_here` con tu clave API de OpenAI
   - Ajustar otras configuraciones según sea necesario

⚠️ IMPORTANTE: Seguridad
- Nunca compartir o exponer las claves API
- No incluir el archivo `.env` en el control de versiones
- No hardcodear valores sensibles en el código
- Usar variables de entorno para toda la información sensible

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
