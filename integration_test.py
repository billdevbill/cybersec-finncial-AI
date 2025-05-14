import os
import sys
import logging
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('integration_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

async def test_anthropic():
    """Prueba la conexión y funcionalidad básica de Anthropic"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Prueba simple de mensaje
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=100,
            messages=[{"role": "user", "content": "Di 'Hola mundo' y confirma que estás funcionando"}]
        )
        
        logger.info(f"✓ Anthropic test exitoso: {response.content[0].text}")
        return True
    except Exception as e:
        logger.error(f"✗ Error en prueba Anthropic: {str(e)}")
        return False

async def test_openai():
    """Prueba la conexión y funcionalidad básica de OpenAI"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Prueba simple de mensaje
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "Di 'Hola mundo' y confirma que estás funcionando"}]
        )
        
        logger.info(f"✓ OpenAI test exitoso: {response.choices[0].message.content}")
        return True
    except Exception as e:
        logger.error(f"✗ Error en prueba OpenAI: {str(e)}")
        return False

async def test_tools():
    """Prueba las herramientas especializadas"""
    try:
        from AI1 import NetworkScanner, QuantumSimulator, FinancialAnalyzer, CodeSecurityTools
        
        # Prueba NetworkScanner
        net_result = NetworkScanner.scan("192.168.1.1", "standard", "normal")
        logger.info(f"✓ NetworkScanner test exitoso: {net_result}")
        
        # Prueba QuantumSimulator
        quantum_result = QuantumSimulator.generate_entropy(128)
        logger.info(f"✓ QuantumSimulator test exitoso: {len(quantum_result)} bits generados")
        
        # Prueba FinancialAnalyzer
        finance_result = FinancialAnalyzer.detect_anomalies("TEST-001", 0.85, "insider_trading")
        logger.info(f"✓ FinancialAnalyzer test exitoso: {finance_result}")
        
        # Prueba CodeSecurityTools
        code_result = CodeSecurityTools.obfuscate("print('test')", "python", 1)
        logger.info(f"✓ CodeSecurityTools test exitoso: {code_result}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error en prueba de herramientas: {str(e)}")
        return False

async def main():
    """Ejecuta todas las pruebas de integración"""
    logger.info("Iniciando pruebas de integración...")
    start_time = datetime.now()
    
    # Ejecutar pruebas
    results = await asyncio.gather(
        test_anthropic(),
        test_openai(),
        test_tools()
    )
    
    # Analizar resultados
    success_count = sum(1 for r in results if r)
    total_tests = len(results)
    
    # Reportar resultados
    logger.info(f"\nResumen de pruebas:")
    logger.info(f"Total pruebas: {total_tests}")
    logger.info(f"Exitosas: {success_count}")
    logger.info(f"Fallidas: {total_tests - success_count}")
    logger.info(f"Tiempo total: {datetime.now() - start_time}")
    
    return success_count == total_tests

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        sys.exit(1)
