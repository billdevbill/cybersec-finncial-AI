"""
Configuración centralizada para el proyecto MAR-DISRUPCION
"""
import os
import sys
import structlog
from pathlib import Path
import toml
from typing import Dict, Any

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.toml"
LOG_PATH = PROJECT_ROOT / "logs"
MEMORY_PATH = PROJECT_ROOT / "memory"

# Asegurar que existen los directorios necesarios
LOG_PATH.mkdir(exist_ok=True)
MEMORY_PATH.mkdir(exist_ok=True)

def load_config() -> Dict[str, Any]:
    """Carga la configuración desde el archivo TOML y variables de entorno"""
    try:
        config = toml.load(CONFIG_PATH)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de configuración en {CONFIG_PATH}")
        sys.exit(1)
    
    # Agregar variables de entorno a la configuración
    env_vars = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "VULNERABILITY_DB_API_KEY": os.getenv("VULNERABILITY_DB_API_KEY"),
        "MARKET_DATA_API_KEY": os.getenv("MARKET_DATA_API_KEY")
    }
    
    config["api_keys"] = {k: v for k, v in env_vars.items() if v is not None}
    
    return config

def setup_logging(config: Dict[str, Any]) -> None:
    """Configura el logging estructurado"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, config["monitoring"]["log_level"].upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True
    )

# Cargar configuración
config = load_config()

# Configurar logging
setup_logging(config)

# Crear logger para este módulo
logger = structlog.get_logger(__name__)
