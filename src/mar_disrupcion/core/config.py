"""
Configuración centralizada para el proyecto MAR-DISRUPCION
"""
import os
import sys
import structlog
from pathlib import Path
import toml
from typing import Dict, Any
from prometheus_client import start_http_server

from .config_models import (
    Settings, APIConfig, SecurityConfig,
    MemoryConfig, MLConfig, MonitoringConfig
)
from .exceptions import ConfigurationError

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.toml"
LOG_PATH = PROJECT_ROOT / "logs"
MEMORY_PATH = PROJECT_ROOT / "memory"

# Asegurar que existen los directorios necesarios
LOG_PATH.mkdir(exist_ok=True)
MEMORY_PATH.mkdir(exist_ok=True)

def load_config() -> Dict[str, Any]:
    """Carga y valida la configuración usando Pydantic."""
    try:
        # Cargar configuración base desde TOML
        raw_config = toml.load(CONFIG_PATH)
        
        # Crear instancias de los modelos de configuración
        api_config = APIConfig(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            **raw_config.get("api", {})
        )
        
        security_config = SecurityConfig(
            vulnerability_db_api_key=os.getenv("VULNERABILITY_DB_API_KEY"),
            **raw_config.get("security", {})
        )
        
        memory_config = MemoryConfig(**raw_config.get("memory", {}))
        ml_config = MLConfig(**raw_config.get("ml", {}))
        monitoring_config = MonitoringConfig(**raw_config.get("monitoring", {}))
        
        # Crear configuración global
        settings = Settings(
            api=api_config,
            security=security_config,
            memory=memory_config,
            ml=ml_config,
            monitoring=monitoring_config
        )
        
        # Convertir a diccionario para mantener compatibilidad
        config = settings.model_dump()
        
        # Iniciar servidor de métricas si está habilitado
        if config["monitoring"]["prometheus_enabled"]:
            start_http_server(config["monitoring"]["metrics_port"])
            logger.info(
                "Servidor de métricas iniciado",
                port=config["monitoring"]["metrics_port"]
            )
            
        return config
        
    except Exception as e:
        logger.error("Error cargando configuración", error=str(e))
        raise ConfigurationError(f"Error cargando configuración: {str(e)}")
    
    config["api_keys"] = {k: v for k, v in env_vars.items() if v is not None}
    
    return config

def setup_logging(config: Dict[str, Any]) -> None:
    """Configura el sistema de logging estructurado."""
    log_file = LOG_PATH / "mar_disrupcion.log"
    
    # Configurar procesadores de logging
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Agregar procesador JSON para archivos, pero mantener formato legible en consola
    if config["monitoring"].get("json_logging", False):
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
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
