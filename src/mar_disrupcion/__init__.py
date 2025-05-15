import os
import json
from typing import Dict, List, Any, Optional, Union
import random
from datetime import datetime
import sys
import asyncio
import sqlite3
import numpy as np
from pathlib import Path
import structlog
import anthropic
import openai

from tools.network_analyzer import AdvancedNetworkAnalyzer, ParallelProcessor
from integrations.api_client import SecurityFeedIntegration, FinancialDataIntegration
from core.memory_system import AdvancedMemorySystem
from core.config import config, logger

# Importar configuración centralizada y logging
from core.config import config, logger, setup_logging

# Asegurar que el logging está configurado correctamente
setup_logging(config)

# Configurar logging adicional específico para este módulo
logging.basicConfig(
    level=getattr(logging, config["monitoring"]["log_level"]),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_system.log')
    ]
)
logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, retention_period: int = 7200):
        self.db_path = Path("memory/system_memory.db")
        self.retention_period = retention_period
        self._init_database()

    def _init_database(self):
        """Inicializa la base de datos de memoria."""
        self.db_path.parent.mkdir(exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    category TEXT,
                    data JSON,
                    importance FLOAT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_data JSON,
                    confidence FLOAT,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    async def store_memory(self, category: str, data: Dict, importance: float = 0.5):
        """Almacena nueva información en la memoria."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT INTO memory (category, data, importance) VALUES (?, ?, ?)",
                (category, json.dumps(data), importance)
            )

    async def retrieve_memories(self, category: str, limit: int = 10) -> List[Dict]:
        """Recupera memorias por categoría."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT data FROM memory WHERE category = ? ORDER BY importance DESC LIMIT ?",
                (category, limit)
            )
            return [json.loads(row[0]) for row in cursor.fetchall()]

class DecisionEngine:
    def __init__(self, confidence_threshold: float = 0.85):
        self.confidence_threshold = confidence_threshold
        self.memory_manager = MemoryManager()
        self.decision_weights = {
            "security_risk": 0.4,
            "financial_impact": 0.3,
            "execution_confidence": 0.3
        }

    async def evaluate_action(self, context: Dict, options: List[Dict]) -> Dict:
        """Evalúa y selecciona la mejor acción basada en el contexto."""
        scores = []
        
        for option in options:
            security_score = await self._evaluate_security_risk(option)
            financial_score = await self._evaluate_financial_impact(option)
            confidence_score = await self._evaluate_confidence(option, context)
            
            total_score = (
                security_score * self.decision_weights["security_risk"] +
                financial_score * self.decision_weights["financial_impact"] +
                confidence_score * self.decision_weights["execution_confidence"]
            )
            
            scores.append({
                "option": option,
                "score": total_score,
                "confidence": confidence_score
            })
        
        best_decision = max(scores, key=lambda x: x["score"])
        if best_decision["confidence"] >= self.confidence_threshold:
            await self.memory_manager.store_memory(
                "decisions",
                {"decision": best_decision, "context": context},
                importance=best_decision["score"]
            )
            return best_decision
        
        return None

    async def _evaluate_security_risk(self, option: Dict) -> float:
        """Evalúa el riesgo de seguridad de una opción."""
        # Implementación del análisis de riesgo
        return 0.5  # Placeholder

    async def _evaluate_financial_impact(self, option: Dict) -> float:
        """Evalúa el impacto financiero de una opción."""
        # Implementación del análisis financiero
        return 0.5  # Placeholder

    async def _evaluate_confidence(self, option: Dict, context: Dict) -> float:
        """Evalúa la confianza en la ejecución de una opción."""
        # Implementación de la evaluación de confianza
        return 0.5  # Placeholder

class AISystem:
    def __init__(self):
        """Inicializa el sistema MAR-DISRUPCION."""
        self.config = config  # Usar configuración centralizada
        self.clients = self._initialize_clients()
        self.memory_system = AdvancedMemorySystem(
            config=self.config,
            db_path=str(Path("memory/system_memory.db"))
        )
        self.decision_engine = DecisionEngine(
            confidence_threshold=float(self.config.get("DECISION_CONFIDENCE_THRESHOLD", 0.85))
        )
        self.network_analyzer = AdvancedNetworkAnalyzer(
            timeout=int(self.config.get("DEEP_SCAN_TIMEOUT", 120)),
            buffer_size=int(self.config.get("PACKET_CAPTURE_BUFFER", 8192)),
            analysis_depth=int(self.config.get("NETWORK_ANALYSIS_DEPTH", 3))
        )
        self.parallel_processor = ParallelProcessor(
            batch_size=int(self.config.get("BATCH_PROCESSING_SIZE", 64))
        )
        self.security_feed = SecurityFeedIntegration()
        self.financial_data = FinancialDataIntegration()
        self._setup_integrations()
        logger.info("Sistema AI inicializado con memoria avanzada y motor de decisiones")
      def _validate_config_value(self, value: Any, key: str, 
                              min_value: Optional[float] = None, 
                              max_value: Optional[float] = None,
                              required: bool = True) -> bool:
        """Valida un valor de configuración."""
        if required and value is None:
            raise ValueError(f"La variable de configuración {key} es requerida")
        
        if value is not None:
            if min_value is not None and value < min_value:
                raise ValueError(f"{key} debe ser mayor o igual a {min_value}")
            if max_value is not None and value > max_value:
                raise ValueError(f"{key} debe ser menor o igual a {max_value}")
        return True    def _load_config(self) -> dict:
        """Carga y valida la configuración del sistema."""
        try:
            # Cargar variables de entorno desde .env
            dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
            if os.path.exists(dotenv_path):
                load_dotenv(dotenv_path=dotenv_path)
                logger.info("Variables de entorno cargadas desde .env")
            else:
                logger.warning("Archivo .env no encontrado, usando variables de entorno del sistema")
            
            # Definir configuración y valores por defecto
            config = {
                # Claves de API (requeridas)
                "ANTHROPIC_API_KEY": self._validate_config_value(os.getenv("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY"),
                "OPENAI_API_KEY": self._validate_config_value(os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY"),
                
                # Configuración de modelos
                "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
                "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                
                # Parámetros de generación
                "MAX_TOKENS": self._validate_config_value(os.getenv("MAX_TOKENS", "64826"), 
                                                        "MAX_TOKENS", 
                                                        min_value=1, 
                                                        max_value=100000),
                "TEMPERATURE": self._validate_config_value(os.getenv("TEMPERATURE", "1"), 
                                                         "TEMPERATURE", 
                                                         min_value=0, 
                                                         max_value=2),
                
                # Timeouts y límites
                "NETWORK_SCAN_TIMEOUT": self._validate_config_value(os.getenv("NETWORK_SCAN_TIMEOUT", "30"), 
                                                                  "NETWORK_SCAN_TIMEOUT", 
                                                                  min_value=1),
                "ENTROPY_BUFFER_SIZE": self._validate_config_value(os.getenv("ENTROPY_BUFFER_SIZE", "4096"), 
                                                                 "ENTROPY_BUFFER_SIZE", 
                                                                 min_value=1024),
            "FINANCIAL_ANALYSIS_THRESHOLD": float(os.getenv("FINANCIAL_ANALYSIS_THRESHOLD", "0.85")),
            "CODE_OBFUSCATION_SEED": int(os.getenv("CODE_OBFUSCATION_SEED", "42")),
            "MEMORY_RETENTION_PERIOD": int(os.getenv("MEMORY_RETENTION_PERIOD", "7200")),
            "DECISION_CONFIDENCE_THRESHOLD": float(os.getenv("DECISION_CONFIDENCE_THRESHOLD", "0.85")),
            "DEEP_SCAN_TIMEOUT": int(os.getenv("DEEP_SCAN_TIMEOUT", "120")),
            "PACKET_CAPTURE_BUFFER": int(os.getenv("PACKET_CAPTURE_BUFFER", "8192")),
            "NETWORK_ANALYSIS_DEPTH": int(os.getenv("NETWORK_ANALYSIS_DEPTH", "3")),
            "BATCH_PROCESSING_SIZE": int(os.getenv("BATCH_PROCESSING_SIZE", "64")),
            "VULNERABILITY_DB_API_KEY": os.getenv("VULNERABILITY_DB_API_KEY"),
            "MARKET_DATA_API_KEY": os.getenv("MARKET_DATA_API_KEY"),
            "CONTEXT_DEPTH": int(os.getenv("CONTEXT_DEPTH", "8")),
            "MEMORY_CONFIDENCE_THRESHOLD": float(os.getenv("MEMORY_CONFIDENCE_THRESHOLD", "0.75")),
            "CACHE_SIZE": int(os.getenv("CACHE_SIZE", "2048")),
            "LEARNING_RATE": float(os.getenv("LEARNING_RATE", "0.0005")),
            "LSTM_HIDDEN_SIZE": int(os.getenv("LSTM_HIDDEN_SIZE", "1024")),
            "LSTM_NUM_LAYERS": int(os.getenv("LSTM_NUM_LAYERS", "3")),
            "DROPOUT_RATE": float(os.getenv("DROPOUT_RATE", "0.2"))
        }
        
        missing = [k for k, v in config.items() if v is None]
        if missing:
            raise ValueError(f"Faltan variables de entorno requeridas: {', '.join(missing)}")
        
        return config    def _initialize_clients(self) -> dict:
        """Inicializa los clientes de API usando las claves de la configuración."""
        try:
            if not self.config.get("ANTHROPIC_API_KEY") or not self.config.get("OPENAI_API_KEY"):
                raise ValueError("Las claves de API ANTHROPIC_API_KEY y OPENAI_API_KEY son requeridas")
                
            clients = {}
            
            # Inicializar cliente Anthropic
            try:
                clients["anthropic"] = anthropic.Anthropic(
                    api_key=self.config["ANTHROPIC_API_KEY"]
                )
                logger.info("Cliente Anthropic inicializado correctamente")
            except Exception as e:
                logger.error("Error inicializando cliente Anthropic", error=str(e))
                raise ValueError(f"Error inicializando Anthropic: {str(e)}")
            
            # Inicializar cliente OpenAI
            try:
                clients["openai"] = openai.OpenAI(
                    api_key=self.config["OPENAI_API_KEY"]
                )
                logger.info("Cliente OpenAI inicializado correctamente")
            except Exception as e:
                logger.error("Error inicializando cliente OpenAI", error=str(e))
                raise ValueError(f"Error inicializando OpenAI: {str(e)}")
                
            return clients
            
        except Exception as e:
            logger.error("Error crítico inicializando clientes API", 
                        error=str(e), exc_info=True)
            raise RuntimeError("Error crítico inicializando clientes API") from e

    def _setup_integrations(self):
        """Configura las integraciones con APIs externas."""
        # Configuración de APIs de seguridad
        self.security_feed.register_api("vulnerability_db", {
            "api_key": self.config.get("VULNERABILITY_DB_API_KEY"),
            "rate_limit": 60
        })
        
        # Configuración de APIs financieras
        self.financial_data.register_api("market_data", {
            "api_key": self.config.get("MARKET_DATA_API_KEY"),
            "rate_limit": 120
        })    async def process_security_scan(self, target: str, options: dict) -> dict:
        """Realiza un análisis de seguridad."""
        try:
            return await self.network_analyzer.deep_scan(target)
        except ConnectionError as e:
            logger.error(f"Error de conexión durante análisis de seguridad: {e}")
            raise ConnectionError(f"No se pudo conectar al objetivo: {target}")
        except TimeoutError as e:
            logger.error(f"Timeout durante análisis de seguridad: {e}")
            raise TimeoutError(f"El análisis excedió el tiempo límite de {self.config.get('DEEP_SCAN_TIMEOUT')} segundos")
        except asyncio.CancelledError:
            logger.warning("Análisis de seguridad cancelado")
            raise
        except Exception as e:
            logger.error(f"Error inesperado durante análisis de seguridad: {str(e)}", exc_info=True)
            raise RuntimeError(f"Error en análisis de seguridad: {str(e)}")    async def analyze_financial_data(self, data: Union[str, dict], analysis_type: str) -> dict:
        """Realiza análisis financiero."""
        try:
            if not data:
                raise ValueError("Los datos de análisis no pueden estar vacíos")
            
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    raise ValueError("Los datos en formato string deben ser JSON válido")
            
            return await self.financial_data.get_market_data(data)
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar datos JSON: {e}")
            raise ValueError(f"Datos JSON inválidos: {str(e)}")
        except ConnectionError as e:
            logger.error(f"Error de conexión durante análisis financiero: {e}")
            raise ConnectionError("No se pudo conectar al servicio de datos financieros")
        except TimeoutError as e:
            logger.error(f"Timeout durante análisis financiero: {e}")
            raise TimeoutError("El análisis financiero excedió el tiempo límite")
        except Exception as e:
            logger.error(f"Error inesperado durante análisis financiero: {str(e)}", exc_info=True)
            raise RuntimeError(f"Error en análisis financiero: {str(e)}")

    async def process_with_memory(self, data: Dict, category: str) -> Dict:
        """Procesa datos utilizando el sistema de memoria avanzado."""
        try:
            # Recuperar contexto relevante
            context = await self.memory_system.retrieve_memories(
                category=category,
                limit=self.memory_system.context_depth,
                min_importance=0.5
            )
            
            # Procesar datos con contexto
            result = await self._process_data_with_context(data, context)
            
            # Almacenar resultado en memoria
            await self.memory_system.store_memory(
                content=result,
                category=category,
                importance=result.get("confidence", 0.5)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error en procesamiento con memoria: {e}")
            raise
    
    async def _process_data_with_context(self, data: Dict, context: List[Dict]) -> Dict:
        """Procesa datos utilizando el contexto recuperado."""
        try:
            # Integrar contexto con datos actuales
            enriched_data = {
                "current_data": data,
                "historical_context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            # Realizar procesamiento
            result = await self.process_security_scan(enriched_data) \
                    if "security" in data \
                    else await self.analyze_financial_data(enriched_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error en procesamiento con contexto: {e}")
            raise

# Inicializar sistema
system = AISystem()
