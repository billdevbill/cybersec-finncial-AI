"""
Sistema de logging centralizado con manejo de errores.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import structlog
from prometheus_client import Counter

# Métricas de errores
ERROR_COUNTER = Counter(
    'error_total',
    'Total number of errors by type',
    ['error_type', 'severity']
)

def get_logger(name: str) -> structlog.BoundLogger:
    """Obtiene un logger configurado para el módulo especificado."""
    return structlog.get_logger(name)

def log_error(
    logger: structlog.BoundLogger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    severity: str = "error"
) -> None:
    """
    Registra un error de forma centralizada.
    
    Args:
        logger: Logger estructurado
        error: Excepción a registrar
        context: Contexto adicional del error
        severity: Nivel de severidad del error
    """
    error_type = type(error).__name__
    
    # Incrementar contador de errores
    ERROR_COUNTER.labels(error_type=error_type, severity=severity).inc()
    
    # Preparar contexto del error
    error_context = {
        "error_type": error_type,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat(),
        "severity": severity
    }
    
    # Agregar contexto adicional si se proporciona
    if context:
        error_context.update(context)
    
    # Registrar error con el nivel apropiado
    if severity == "critical":
        logger.error("Error crítico", **error_context, exc_info=True)
    elif severity == "error":
        logger.error("Error", **error_context)
    else:
        logger.warning("Advertencia", **error_context)

def setup_error_handling(config: Dict[str, Any]) -> None:
    """
    Configura el manejo de errores global.
    
    Args:
        config: Configuración del sistema
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Manejador global de excepciones no capturadas."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger = get_logger("error_handler")
        log_error(
            logger,
            exc_value,
            context={"traceback": True},
            severity="critical"
        )
    
    # Establecer manejador de excepciones global
    sys.excepthook = handle_exception
