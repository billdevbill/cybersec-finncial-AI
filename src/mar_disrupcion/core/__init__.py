"""
Core modules for MAR-DISRUPCION.
This package contains the core functionality including configuration,
memory management, metrics collection, and error handling.
"""

from .config import config, logger, setup_logging
from .memory_system import AdvancedMemorySystem
from .metrics import (
    SCAN_DURATION, API_REQUESTS, API_LATENCY,
    record_security_alert, record_api_request,
    record_memory_operation, record_processing_metrics
)
from .error_handling import get_logger, log_error, setup_error_handling
from .exceptions import (
    MarDisrupcionError, ConfigurationError, APIError,
    SecurityError, MemoryError, ProcessingError
)
from .config_models import Settings

__all__ = [
    # Configuration
    'config',
    'logger',
    'setup_logging',
    'Settings',
    
    # Memory System
    'AdvancedMemorySystem',
    
    # Metrics
    'SCAN_DURATION',
    'API_REQUESTS',
    'API_LATENCY',
    'record_security_alert',
    'record_api_request',
    'record_memory_operation',
    'record_processing_metrics',
    
    # Error Handling
    'get_logger',
    'log_error',
    'setup_error_handling',
    
    # Exceptions
    'MarDisrupcionError',
    'ConfigurationError',
    'APIError',
    'SecurityError',
    'MemoryError',
    'ProcessingError',
]
