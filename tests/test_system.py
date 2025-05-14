import sys
from pathlib import Path
import logging
import json
import asyncio
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_run.log')
    ]
)
logger = logging.getLogger(__name__)

async def run_test_suite():
    """Ejecuta una serie de pruebas para verificar la funcionalidad del sistema."""
    try:
        # Importar la clase principal
        from AI1 import AIOrchestrator
        logger.info("Sistema inicializado correctamente")
        
        # Crear una instancia del orquestador
        ai = AIOrchestrator()
          # Serie de pruebas
        test_cases = [
            {
                "name": "Análisis de Seguridad Básico",
                "prompt": "Realiza un análisis de seguridad básico para la dirección IP 192.168.1.1",
                "provider": "auto"
            },
            {
                "name": "Análisis con Claude",
                "prompt": "Genera 128 bits de entropía usando fluctuaciones cuánticas",
                "provider": "claude"
            },
            {
                "name": "Análisis con OpenAI",
                "prompt": "Detecta anomalías en las transacciones del lote BATCH-001 con sensibilidad alta",
                "provider": "openai"
            },
            {
                "name": "Análisis Combinado Avanzado",
                "prompt": "Desarrolla una estrategia de trading algorítmico que combine análisis técnico y fundamental",
                "provider": "auto"
            }
        ]
          # Ejecutar las pruebas
        results = []
        for test in test_cases:
            logger.info(f"Ejecutando prueba: {test['name']} con proveedor: {test['provider']}")
            try:
                response = await ai.process_message(test["prompt"], test["provider"])
                results.append({
                    "test_name": test["name"],
                    "provider": test["provider"],
                    "status": "success" if "error" not in response else "error",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error en prueba {test['name']}: {e}")
                results.append({
                    "test_name": test["name"],
                    "provider": test["provider"],
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Guardar resultados
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Mostrar resultados
        print("\nResultados de las pruebas:")
        for result in results:
            print(f"\nPrueba: {result['test_name']}")
            print(f"Estado: {result['status']}")
            if result['status'] == "success":
                print("Respuesta:", json.dumps(result['response'], indent=2, ensure_ascii=False))
            else:
                print("Error:", result['error'])
        
        return results
        
    except Exception as e:
        logger.error(f"Error durante la ejecución de las pruebas: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Ejecutar el bucle de eventos de asyncio
        asyncio.run(run_test_suite())
    except KeyboardInterrupt:
        logger.info("Pruebas interrumpidas por el usuario")
    except Exception as e:
        logger.error(f"Error en la ejecución de pruebas: {e}")
        raise
