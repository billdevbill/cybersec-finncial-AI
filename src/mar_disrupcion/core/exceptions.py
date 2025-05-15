"""
Excepciones personalizadas para el sistema MAR-DISRUPCION.
"""

class MarDisrupcionError(Exception):
    """Excepción base para el sistema."""
    pass

class ConfigurationError(MarDisrupcionError):
    """Error en la configuración del sistema."""
    pass

class APIError(MarDisrupcionError):
    """Error en llamadas a APIs externas."""
    pass

class SecurityError(MarDisrupcionError):
    """Error en operaciones de seguridad."""
    pass

class MemoryError(MarDisrupcionError):
    """Error en el sistema de memoria."""
    pass

class ProcessingError(MarDisrupcionError):
    """Error en el procesamiento de datos."""
    pass

class ValidationError(MarDisrupcionError):
    """Error en la validación de datos."""
    pass

class ConnectionError(MarDisrupcionError):
    """Error en conexiones externas."""
    pass

class ResourceError(MarDisrupcionError):
    """Error en el manejo de recursos."""
    pass
