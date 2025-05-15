"""
Sistema de caché distribuido usando Redis.
"""
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import redis
from redis.cluster import RedisCluster
import structlog
from prometheus_client import Counter, Histogram

from ..core.metrics import record_memory_operation
from ..core.exceptions import MemoryError

logger = structlog.get_logger(__name__)

# Métricas de caché
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["cache_type"]
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    ["cache_type"]
)

CACHE_LATENCY = Histogram(
    "cache_operation_latency_seconds",
    "Cache operation latency in seconds",
    ["operation"]
)

class DistributedCache:
    """Implementación de caché distribuido usando Redis."""
    
    def __init__(
        self,
        hosts: List[str],
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        cluster_mode: bool = False,
        default_ttl: int = 3600
    ):
        """
        Inicializa el caché distribuido.
        
        Args:
            hosts: Lista de hosts de Redis
            port: Puerto de Redis
            db: Número de base de datos
            password: Contraseña de Redis
            cluster_mode: Si usar modo cluster
            default_ttl: Tiempo de vida por defecto en segundos
        """
        self.default_ttl = default_ttl
        
        try:
            if cluster_mode:
                nodes = [{"host": host, "port": port} for host in hosts]
                self.client = RedisCluster(
                    startup_nodes=nodes,
                    password=password,
                    decode_responses=True
                )
            else:
                self.client = redis.Redis(
                    host=hosts[0],
                    port=port,
                    db=db,
                    password=password,
                    decode_responses=True
                )
                
            logger.info(
                "Caché distribuido inicializado",
                cluster_mode=cluster_mode,
                hosts=hosts
            )
            
        except Exception as e:
            logger.error(
                "Error inicializando caché distribuido",
                error=str(e),
                exc_info=True
            )
            raise MemoryError(f"Error inicializando caché: {str(e)}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        try:
            start_time = datetime.now()
            value = self.client.get(key)
            
            if value is not None:
                CACHE_HITS.labels(cache_type="redis").inc()
                value = json.loads(value)
            else:
                CACHE_MISSES.labels(cache_type="redis").inc()
            
            duration = (datetime.now() - start_time).total_seconds()
            CACHE_LATENCY.labels(operation="get").observe(duration)
            
            record_memory_operation("cache_get", "success" if value else "miss")
            return value
            
        except Exception as e:
            logger.error(
                "Error obteniendo valor del caché",
                key=key,
                error=str(e)
            )
            record_memory_operation("cache_get", "error")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Guarda un valor en el caché."""
        try:
            start_time = datetime.now()
            serialized = json.dumps(value)
            
            if ttl is None:
                ttl = self.default_ttl
                
            success = self.client.setex(
                key,
                ttl,
                serialized
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            CACHE_LATENCY.labels(operation="set").observe(duration)
            
            record_memory_operation("cache_set", "success" if success else "error")
            return success
            
        except Exception as e:
            logger.error(
                "Error guardando valor en caché",
                key=key,
                error=str(e)
            )
            record_memory_operation("cache_set", "error")
            return False
    
    async def delete(self, key: str) -> bool:
        """Elimina un valor del caché."""
        try:
            start_time = datetime.now()
            success = bool(self.client.delete(key))
            
            duration = (datetime.now() - start_time).total_seconds()
            CACHE_LATENCY.labels(operation="delete").observe(duration)
            
            record_memory_operation("cache_delete", "success" if success else "miss")
            return success
            
        except Exception as e:
            logger.error(
                "Error eliminando valor del caché",
                key=key,
                error=str(e)
            )
            record_memory_operation("cache_delete", "error")
            return False
    
    async def flush(self) -> bool:
        """Limpia todo el caché."""
        try:
            start_time = datetime.now()
            success = self.client.flushdb()
            
            duration = (datetime.now() - start_time).total_seconds()
            CACHE_LATENCY.labels(operation="flush").observe(duration)
            
            record_memory_operation("cache_flush", "success" if success else "error")
            return success
            
        except Exception as e:
            logger.error("Error limpiando caché", error=str(e))
            record_memory_operation("cache_flush", "error")
            return False
