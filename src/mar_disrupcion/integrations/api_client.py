import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime, timedelta
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from prometheus_client import Counter, Histogram
import ssl
from aiohttp import TCPConnector, ClientTimeout
from contextlib import asynccontextmanager
from core.config import config, logger

logger = structlog.get_logger(__name__)

class APIError(Exception):
    """Base exception for API errors"""
    pass

class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass

class ConnectionError(APIError):
    """Raised when connection fails"""
    pass

class ExternalAPIIntegration:
    def __init__(self):
        self.session = None
        self._api_keys = {}
        self._rate_limits = {}
        
        # Configuración de caché
        cache_size = int(config.get("API_CACHE_SIZE", 1000))
        cache_ttl = int(config.get("API_CACHE_TTL", 300))  # 5 minutos por defecto
        self._cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        
        # Métricas
        self._requests_counter = Counter('api_requests_total', 
                                      'Total API requests', 
                                      ['api_name', 'endpoint', 'status'])
        self._response_time = Histogram('api_response_time_seconds', 
                                      'API response time in seconds', 
                                      ['api_name', 'endpoint'])
        self._errors_counter = Counter('api_errors_total',
                                     'Total API errors',
                                     ['api_name', 'error_type'])
        self._cache_hits = Counter('api_cache_hits_total',
                                 'Total cache hits',
                                 ['api_name'])
        
        logger.info("API Integration inicializada",
                   cache_size=cache_size,
                   cache_ttl=cache_ttl)
          async def initialize(self):
        """Inicializa la sesión HTTP con configuración optimizada."""
        try:
            if self.session:
                await self.close()
            
            # Configuración SSL
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Configuración de timeouts
            timeout = ClientTimeout(
                total=float(config.get("API_TIMEOUT_TOTAL", 30)),
                connect=float(config.get("API_TIMEOUT_CONNECT", 10)),
                sock_read=float(config.get("API_TIMEOUT_READ", 30))
            )
            
            # Configuración del conector TCP
            connector = TCPConnector(
                ssl=ssl_context,
                limit=int(config.get("API_CONNECTION_LIMIT", 100)),
                ttl_dns_cache=300,
                keepalive_timeout=60
            )
            
            # Crear sesión
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                raise_for_status=True
            )
            
            logger.info("Sesión HTTP inicializada con configuración optimizada",
                       timeout_total=timeout.total,
                       connection_limit=connector._limit)
                       
        except Exception as e:
            logger.error("Error inicializando sesión HTTP",
                        error=str(e),
                        exc_info=True)
            raise RuntimeError(f"Error inicializando sesión HTTP: {str(e)}")
        ssl_context = ssl.create_default_context()
        connector = TCPConnector(
            ssl=ssl_context,
            limit=100,  # Límite de conexiones concurrentes
            ttl_dns_cache=300,  # Cache DNS por 5 minutos
            use_dns_cache=True,
            keepalive_timeout=60
        )
        timeout = ClientTimeout(total=30, connect=10, sock_read=20)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            raise_for_status=True
        )
    
    async def close(self):
        """Cierra la sesión HTTP de manera segura."""
        if self.session and not self.session.closed:
            await self.session.close()
            await asyncio.sleep(0.25)  # Esperar a que se cierren las conexiones
    
    def register_api(self, name: str, config: Dict):
        """Registra una nueva API."""
        self._api_keys[name] = config.get("api_key")
        self._rate_limits[name] = {
            "calls": 0,
            "reset_time": datetime.now(),
            "limit": config.get("rate_limit", 60)
        }    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=lambda e: isinstance(e, (ConnectionError, TimeoutError, RateLimitError)),
        before=lambda retry_state: logger.warning(
            "Reintentando llamada API",
            attempt=retry_state.attempt_number,
            api_name=retry_state.args[0] if retry_state.args else None
        ),
        after=lambda retry_state: logger.info(
            "Reintento exitoso" if retry_state.outcome.failed else "Llamada API exitosa",
            attempt=retry_state.attempt_number,
            api_name=retry_state.args[0] if retry_state.args else None
        )
    )
    async def call_api(self, api_name: str, endpoint: str, 
                      method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Realiza una llamada a una API externa con reintentos y caché."""
        if not self.session:
            await self.initialize()
        
        if api_name not in self._api_keys:
            raise ValueError(f"API {api_name} no registrada")
        
        # Verificar caché para GET requests
        cache_key = f"{api_name}:{endpoint}:{method}:{json.dumps(data) if data else ''}"
        if method == "GET" and cache_key in self._cache:
            logger.info(f"Retornando resultado cacheado para {api_name}")
            return self._cache[cache_key]
        
        headers = {
            "Authorization": f"Bearer {self._api_keys[api_name]}",
            "Content-Type": "application/json",
            "User-Agent": "MAR-DISRUPCION/0.1.0"
        }
        
        start_time = datetime.now()
        try:
            async with self.session.request(
                method, endpoint, json=data, headers=headers
            ) as response:
                self._requests_counter.labels(api_name=api_name, endpoint=endpoint).inc()
                
                if response.status == 429:  # Rate limit
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit alcanzado para {api_name}. "
                                 f"Esperando {retry_after} segundos.")
                    raise RateLimitError(f"Rate limit exceeded for {api_name}")
                
                response.raise_for_status()
                result = await response.json()
                
                # Almacenar en caché si es GET
                if method == "GET":
                    self._cache[cache_key] = result
                
                # Registrar tiempo de respuesta
                response_time = (datetime.now() - start_time).total_seconds()
                self._response_time.labels(api_name=api_name).observe(response_time)
                
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"Error de conexión con {api_name} API: {e}")
            raise ConnectionError(f"Connection error: {str(e)}")
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout llamando a {api_name} API: {e}")
            raise TimeoutError(f"Request timeout: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado llamando a {api_name} API: {e}", exc_info=True)
            raise

class SecurityFeedIntegration(ExternalAPIIntegration):
    """Integración con feeds de seguridad."""
    
    async def get_vulnerability_feed(self) -> List[Dict]:
        """Obtiene el feed de vulnerabilidades más reciente."""
        return await self.call_api(
            "vulnerability_db",
            "https://api.vulnerability-db.com/v1/recent",
            "GET"
        )
    
    async def report_incident(self, incident_data: Dict) -> Dict:
        """Reporta un incidente de seguridad."""
        return await self.call_api(
            "incident_tracker",
            "https://api.incident-tracker.com/v1/reports",
            "POST",
            data=incident_data
        )

class FinancialDataIntegration(ExternalAPIIntegration):
    """Integración con APIs financieras."""
    
    async def get_market_data(self, symbol: str) -> Dict:
        """Obtiene datos de mercado en tiempo real."""
        return await self.call_api(
            "market_data",
            f"https://api.financial-data.com/v1/quotes/{symbol}",
            "GET"
        )
    
    async def analyze_transaction(self, transaction: Dict) -> Dict:
        """Analiza una transacción financiera."""
        return await self.call_api(
            "transaction_analyzer",
            "https://api.transaction-analysis.com/v1/analyze",
            "POST",
            data=transaction
        )
