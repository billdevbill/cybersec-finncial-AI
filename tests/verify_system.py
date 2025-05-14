import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Asegurar que estamos en el directorio correcto
os.chdir(Path(__file__).parent)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment():
    """Verifica el entorno de ejecución"""
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Verificar .env
    if not os.path.exists('.env'):
        logger.error("Archivo .env no encontrado")
        return False
    
    load_dotenv()
    
    # Verificar variables de entorno
    env_vars = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL")
    }
    
    missing = [k for k, v in env_vars.items() if not v]
    if missing:
        logger.error(f"Faltan variables de entorno: {missing}")
        return False
    
    logger.info("Variables de entorno verificadas correctamente")
    return True

def test_imports():
    """Verifica las importaciones necesarias"""
    packages = [
        ('anthropic', 'Cliente de Anthropic'),
        ('openai', 'Cliente de OpenAI'),
        ('dotenv', 'Manejo de variables de entorno')
    ]
    
    for package, description in packages:
        try:
            __import__(package)
            logger.info(f"✓ {description} importado correctamente")
        except ImportError as e:
            logger.error(f"✗ Error importando {description}: {e}")
            return False
    
    return True

def test_api_clients():
    """Verifica la creación de clientes de API"""
    try:
        import anthropic
        import openai
        
        # Probar cliente Anthropic
        anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        logger.info("✓ Cliente Anthropic creado correctamente")
        
        # Probar cliente OpenAI
        openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("✓ Cliente OpenAI creado correctamente")
        
        return True
    except Exception as e:
        logger.error(f"Error creando clientes de API: {e}")
        return False

def main():
    """Ejecuta todas las verificaciones"""
    logger.info("Iniciando verificación del sistema...")
    
    checks = [
        ("Entorno", test_environment),
        ("Importaciones", test_imports),
        ("Clientes API", test_api_clients)
    ]
    
    results = []
    for name, check in checks:
        logger.info(f"\nEjecutando verificación: {name}")
        try:
            result = check()
            results.append(result)
            logger.info(f"Verificación {name}: {'✓ Exitosa' if result else '✗ Fallida'}")
        except Exception as e:
            logger.error(f"Error en verificación {name}: {e}")
            results.append(False)
    
    success = all(results)
    logger.info(f"\nResultado final: {'✓ Todo correcto' if success else '✗ Hay errores'}")
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nVerificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nError inesperado: {e}")
        sys.exit(1)
