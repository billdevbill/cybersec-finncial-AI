import aiohttp
import asyncio
from typing import Dict, List, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ExternalAPIIntegration:
    def __init__(self):
        self.session = None
        self._api_keys = {}
        self._rate_limits = {}
        
    async def initialize(self):
        """Inicializa la sesión HTTP."""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Cierra la sesión HTTP."""
        if self.session:
            await self.session.close()
    
    def register_api(self, name: str, config: Dict):
        """Registra una nueva API."""
        self._api_keys[name] = config.get("api_key")
        self._rate_limits[name] = {
            "calls": 0,
            "reset_time": datetime.now(),
            "limit": config.get("rate_limit", 60)
        }
    
    async def call_api(self, api_name: str, endpoint: str, 
                      method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Realiza una llamada a una API externa."""
        if not self.session:
            await self.initialize()
        
        if api_name not in self._api_keys:
            raise ValueError(f"API {api_name} no registrada")
        
        headers = {
            "Authorization": f"Bearer {self._api_keys[api_name]}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(
                method, endpoint, json=data, headers=headers
            ) as response:
                if response.status == 429:  # Rate limit
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit alcanzado para {api_name}. "
                                 f"Esperando {retry_after} segundos.")
                    await asyncio.sleep(retry_after)
                    return await self.call_api(api_name, endpoint, method, data)
                
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error llamando a {api_name} API: {e}")
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
