"""
Modelos de configuración usando Pydantic para validación.
"""
from typing import Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class APIConfig(BaseModel):
    """Configuración de APIs externas"""
    anthropic_api_key: str = Field(..., description="API key para Anthropic")
    openai_api_key: str = Field(..., description="API key para OpenAI")
    anthropic_model: str = Field("claude-3-opus-20240229", description="Modelo de Anthropic a usar")
    openai_model: str = Field("gpt-4-turbo-preview", description="Modelo de OpenAI a usar")
    max_tokens: int = Field(64826, ge=1, le=100000, description="Máximo número de tokens")
    temperature: float = Field(1.0, ge=0, le=2, description="Temperatura para generación")

class SecurityConfig(BaseModel):
    """Configuración de seguridad"""
    network_scan_timeout: int = Field(30, ge=1, description="Timeout para escaneo de red")
    entropy_buffer_size: int = Field(4096, ge=1024, description="Tamaño del buffer de entropía")
    deep_scan_timeout: int = Field(120, ge=1, description="Timeout para escaneo profundo")
    packet_capture_buffer: int = Field(8192, ge=1024, description="Tamaño del buffer de captura")
    network_analysis_depth: int = Field(3, ge=1, le=10, description="Profundidad de análisis de red")
    vulnerability_db_api_key: Optional[str] = Field(None, description="API key para base de datos de vulnerabilidades")

class MemoryConfig(BaseModel):
    """Configuración del sistema de memoria"""
    retention_period: int = Field(7200, ge=1800, description="Período de retención en segundos")
    context_depth: int = Field(8, ge=1, le=50, description="Profundidad del contexto")
    confidence_threshold: float = Field(0.75, ge=0, le=1, description="Umbral de confianza")
    cache_size: int = Field(2048, ge=256, description="Tamaño de caché")

class MLConfig(BaseModel):
    """Configuración de aprendizaje automático"""
    learning_rate: float = Field(0.0005, ge=0.0001, le=0.1, description="Tasa de aprendizaje")
    lstm_hidden_size: int = Field(1024, ge=64, description="Tamaño de capa oculta LSTM")
    lstm_num_layers: int = Field(3, ge=1, le=10, description="Número de capas LSTM")
    dropout_rate: float = Field(0.2, ge=0, le=0.5, description="Tasa de dropout")

class MonitoringConfig(BaseModel):
    """Configuración de monitoreo"""
    log_level: str = Field("INFO", description="Nivel de logging")
    metrics_port: int = Field(9090, ge=1024, le=65535, description="Puerto para métricas")
    prometheus_enabled: bool = Field(True, description="Habilitar métricas Prometheus")

class Settings(BaseSettings):
    """Configuración global del sistema"""
    api: APIConfig
    security: SecurityConfig
    memory: MemoryConfig
    ml: MLConfig
    monitoring: MonitoringConfig
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False
    )
    
    @validator("*", pre=True)
    def check_none_values(cls, v):
        """Validar que los valores requeridos no sean None"""
        if v is None:
            raise ValueError("Este campo es requerido")
        return v
