import os
import json
import anthropic
import openai
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Union
import logging
import random
from datetime import datetime
import sys
import asyncio

# Configuración de logging con formato mejorado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_system.log')
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Verificar configuración
def verify_config():
    required_vars = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    }
    
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return required_vars

# Inicializar configuración
try:
    config = verify_config()
    logger.info("Configuración verificada correctamente")
except Exception as e:
    logger.error(f"Error en la configuración: {e}")
    raise

# Configuración de los clientes
openai.api_key = config["OPENAI_API_KEY"]

# Configuración de modelos
ANTHROPIC_MODEL = config["ANTHROPIC_MODEL"]
OPENAI_MODEL = config["OPENAI_MODEL"]
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "64826"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "1.0"))

# Configuración adicional para las herramientas
NETWORK_SCAN_TIMEOUT = int(os.getenv("NETWORK_SCAN_TIMEOUT", "30"))
ENTROPY_BUFFER_SIZE = int(os.getenv("ENTROPY_BUFFER_SIZE", "4096"))
FINANCIAL_ANALYSIS_THRESHOLD = float(os.getenv("FINANCIAL_ANALYSIS_THRESHOLD", "0.85"))
CODE_OBFUSCATION_SEED = int(os.getenv("CODE_OBFUSCATION_SEED", "42"))

# Definición de herramientas personalizadas
CUSTOM_TOOLS = [
    {
        "type": "function",
        "name": "NetworkVulnerabilityScanner",
        "description": "Escanea un objetivo de red en busca de vulnerabilidades conocidas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "La dirección IP o el nombre de dominio a escanear."
                },
                "scan_depth": {
                    "type": "string",
                    "enum": ["superficial", "standard", "deep_intrusive"],
                },
                "stealth_level": {
                    "type": "string",
                    "enum": ["normal", "stealthy", "ghost_protocol"],
                }
            },
            "required": ["target", "scan_depth"]
        }
    },
    {
        "type": "function",
        "name": "QuantumEntropyOracle",
        "description": "Genera secuencias de bits pseudoaleatorios usando simulación cuántica.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bits_requested": {
                    "type": "integer",
                    "minimum": 64,
                    "maximum": 4096,
                },
                "entropy_source_simulation": {
                    "type": "string",
                    "enum": ["vacuum_fluctuations", "thermal_noise", "photonic_emission"],
                }
            },
            "required": ["bits_requested"]
        }
    },
    {
        "type": "function",
        "name": "FinancialAnomalyDetector",
        "description": "Analiza transacciones financieras para detectar anomalías.",
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_batch_id": {
                    "type": "string"
                },
                "sensitivity": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 1.0
                },
                "analysis_profile": {
                    "type": "string",
                    "enum": ["insider_trading", "money_laundering", "fraudulent_activity"]
                }
            },
            "required": ["transaction_batch_id", "sensitivity", "analysis_profile"]
        }
    },
    {
        "type": "function",
        "name": "CodeObfuscator",
        "description": "Ofusca código fuente manteniendo su funcionalidad.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source_code": {
                    "type": "string"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript", "java", "cpp"]
                },
                "obfuscation_level": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5
                }
            },
            "required": ["source_code", "language", "obfuscation_level"]
        }
    }
]

# Clase principal para manejar la comunicación con Claude
class ClaudeInterface:
    def __init__(self):
        try:
            self.client = anthropic.Anthropic(api_key=config["ANTHROPIC_API_KEY"])
            self.tools = CUSTOM_TOOLS
            self.message_history = []
            logger.info("ClaudeInterface inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar ClaudeInterface: {e}")
            raise

    def process_message(self, prompt: str) -> Dict[str, Any]:
        try:
            # Preparar el mensaje con el contexto anterior
            messages = self._prepare_messages(prompt)
            
            # Crear el mensaje
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system="tu roll es ser innovador, detallado y dominar el codigo hacker de las finanzas, debes mantener un nodo CEO",
                messages=messages
            )
            
            # Procesar la respuesta
            processed_response = self._handle_response(response)
            
            # Guardar en el historial
            self.message_history.append({
                "prompt": prompt,
                "response": processed_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return processed_response
        except anthropic.APIError as e:
            logger.error(f"Error de API de Anthropic: {e}")
            return {"error": f"Error de API: {str(e)}"}
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return {"error": str(e)}

    def _prepare_messages(self, prompt: str) -> List[Dict[str, Any]]:
        """Prepara los mensajes incluyendo contexto relevante del historial."""
        messages = []
        
        # Agregar contexto relevante del historial
        if self.message_history:
            # Tomar los últimos 3 intercambios relevantes
            relevant_history = self.message_history[-3:]
            for entry in relevant_history:
                messages.append({"role": "user", "content": entry["prompt"]})
                if "response" in entry and "error" not in entry["response"]:
                    messages.append({"role": "assistant", "content": entry["response"]})
        
        # Agregar el prompt actual
        messages.append({"role": "user", "content": prompt})
        return messages

    def _handle_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la respuesta y maneja el uso de herramientas."""
        try:
            if hasattr(response, 'content'):
                content = response.content[0].text
                # Verificar si hay llamadas a herramientas en el contenido
                tool_calls = self._extract_tool_calls(content)
                if tool_calls:
                    # Procesar las llamadas a herramientas
                    tool_results = self._process_tool_calls(tool_calls)
                    return {
                        "content": content,
                        "tool_results": tool_results
                    }
                return {"content": content}
            return {"error": "Respuesta sin contenido"}
        except Exception as e:
            logger.error(f"Error al procesar la respuesta: {e}")
            return {"error": f"Error al procesar la respuesta: {str(e)}"}

    def _extract_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extrae las llamadas a herramientas del contenido."""
        tool_calls = []
        # Implementar lógica para extraer llamadas a herramientas del contenido
        return tool_calls

    def _process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa las llamadas a herramientas y devuelve los resultados."""
        results = []
        for tool_call in tool_calls:
            try:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})
                
                if tool_name == "NetworkVulnerabilityScanner":
                    result = NetworkScanner.scan(**tool_args)
                elif tool_name == "QuantumEntropyOracle":
                    result = QuantumSimulator.generate_entropy(**tool_args)
                elif tool_name == "FinancialAnomalyDetector":
                    result = FinancialAnalyzer.detect_anomalies(**tool_args)
                elif tool_name == "CodeObfuscator":
                    result = CodeSecurityTools.obfuscate(**tool_args)
                else:
                    result = {"error": f"Herramienta no encontrada: {tool_name}"}
                
                results.append({
                    "tool": tool_name,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error al procesar herramienta {tool_name}: {e}")
                results.append({
                    "tool": tool_name,
                    "error": str(e)
                })
        
        return results

    def get_message_history(self) -> List[Dict[str, Any]]:
        """Devuelve el historial de mensajes."""
        return self.message_history

    def clear_history(self) -> None:
        """Limpia el historial de mensajes."""
        self.message_history = []
        logger.info("Historial de mensajes limpiado")

# Implementaciones de las herramientas
class NetworkScanner:
    @staticmethod
    def scan(target: str, scan_depth: str = "standard", stealth_level: str = "normal") -> Dict[str, Any]:
        # Simulación de escaneo de red
        vulnerabilities = ["SQL Injection Risk", "Open Ports: 80, 443", "Outdated SSL Certificates"]
        return {
            "target": target,
            "findings": vulnerabilities,
            "risk_level": "Medium",
            "scan_timestamp": datetime.now().isoformat()
        }

class QuantumSimulator:
    @staticmethod
    def generate_entropy(bits: int, source: str = "vacuum_fluctuations") -> str:
        # Simulación de generación de entropía cuántica
        return "".join([str(random.randint(0, 1)) for _ in range(bits)])

class FinancialAnalyzer:
    @staticmethod
    def detect_anomalies(batch_id: str, sensitivity: float, profile: str) -> Dict[str, Any]:
        # Simulación de detección de anomalías financieras
        return {
            "batch_id": batch_id,
            "anomalies_detected": 3,
            "confidence_score": sensitivity * 100,
            "risk_profile": profile,
            "timestamp": datetime.now().isoformat()
        }

class CodeSecurityTools:
    @staticmethod
    def obfuscate(code: str, language: str, level: int) -> str:
        # Simulación de ofuscación de código
        return f"[Código ofuscado nivel {level}] {code[:20]}..."

class OpenAIInterface:
    def __init__(self):
        self.client = openai.OpenAI()
        self.model = OPENAI_MODEL
        self.message_history = []
        logger.info("OpenAIInterface inicializado correctamente")

    async def process_message(self, prompt: str) -> Dict[str, Any]:
        try:
            messages = self._prepare_messages(prompt)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            processed_response = self._handle_response(response)
            self._update_history(prompt, processed_response)
            return processed_response
        except Exception as e:
            logger.error(f"Error en OpenAI: {e}")
            return {"error": str(e)}

    def _prepare_messages(self, prompt: str) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": "Eres un asistente experto en seguridad informática y finanzas."}]
        if self.message_history:
            for entry in self.message_history[-3:]:
                messages.append({"role": "user", "content": entry["prompt"]})
                if "response" in entry and "error" not in entry["response"]:
                    messages.append({"role": "assistant", "content": str(entry["response"])})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _handle_response(self, response: Any) -> Dict[str, Any]:
        try:
            return {
                "content": response.choices[0].message.content,
                "model": self.model,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            logger.error(f"Error al procesar respuesta de OpenAI: {e}")
            return {"error": str(e)}

    def _update_history(self, prompt: str, response: Dict[str, Any]):
        self.message_history.append({
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

class AIOrchestrator:
    def __init__(self):
        self.claude = ClaudeInterface()
        self.openai = OpenAIInterface()
        logger.info("AIOrchestrator inicializado correctamente")

    async def process_message(self, prompt: str, provider: str = "auto") -> Dict[str, Any]:
        """
        Procesa un mensaje usando el proveedor especificado o ambos en modo automático.
        
        Args:
            prompt: El mensaje a procesar
            provider: 'claude', 'openai', o 'auto' para usar ambos
        """
        try:
            if provider == "claude":
                return self.claude.process_message(prompt)
            elif provider == "openai":
                return await self.openai.process_message(prompt)
            else:  # modo auto
                # Usar ambos modelos y combinar resultados
                claude_response = self.claude.process_message(prompt)
                openai_response = await self.openai.process_message(prompt)
                
                return {
                    "claude": claude_response,
                    "openai": openai_response,
                    "combined": self._combine_responses(claude_response, openai_response)
                }
        except Exception as e:
            logger.error(f"Error en AIOrchestrator: {e}")
            return {"error": str(e)}

    def _combine_responses(self, claude_response: Dict[str, Any], openai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Combina las respuestas de ambos modelos de manera inteligente."""
        try:
            if "error" in claude_response and "error" in openai_response:
                return {"error": "Ambos modelos fallaron"}
            
            if "error" in claude_response:
                return openai_response
            
            if "error" in openai_response:
                return claude_response
            
            # Si ambos funcionaron, combinar los resultados
            combined_content = f"""
Respuesta combinada de ambos modelos:

Claude dice:
{claude_response.get('content', '')}

OpenAI dice:
{openai_response.get('content', '')}
"""
            return {
                "content": combined_content,
                "sources": {
                    "claude": claude_response,
                    "openai": openai_response
                }
            }
        except Exception as e:
            logger.error(f"Error al combinar respuestas: {e}")
            return {"error": f"Error al combinar respuestas: {str(e)}"}

# Inicialización del cliente
def main():
    orchestrator = AIOrchestrator()
    # Ejemplo de uso
    response = orchestrator.process_message("Analiza la seguridad de la red 192.168.1.1", provider="auto")
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()
