"""
Core modules for MAR-DISRUPCION.
This package contains the core functionality including configuration,
memory management, and metrics collection.
"""

from .config import config, logger, setup_logging
from .memory_system import AdvancedMemorySystem
from .metrics import SCAN_DURATION, record_security_alert

__all__ = [
    'config',
    'logger',
    'setup_logging',
    'AdvancedMemorySystem',
    'SCAN_DURATION',
    'record_security_alert',
]
