import unittest
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path
import logging
from AI1 import AISystem

class TestSuite:
    """Gestor principal de pruebas del sistema."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.test_results = []
    
    def _setup_logging(self):
        """Configura el sistema de logging."""
        log_file = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger = logging.getLogger("TestSuite")
        logger.setLevel(logging.INFO)
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        logger.addHandler(console_handler)
        
        return logger
    
    async def run_tests(self):
        """Ejecuta todas las pruebas del sistema."""
        self.logger.info("Iniciando suite de pruebas...")
        
        try:
            # Pruebas de inicialización
            await self.test_system_init()
            
            # Pruebas de seguridad
            await self.test_security_features()
            
            # Pruebas financieras
            await self.test_financial_features()
            
            # Pruebas de entropía
            await self.test_entropy_generation()
            
            # Pruebas de ofuscación
            await self.test_code_obfuscation()
            
            self.logger.info("Suite de pruebas completada exitosamente.")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en la suite de pruebas: {str(e)}")
            return False
    
    async def test_system_init(self):
        """Prueba la inicialización del sistema."""
        self.logger.info("Probando inicialización del sistema...")
        system = AISystem()
        assert system.config is not None, "Configuración no inicializada"
        assert system.clients is not None, "Clientes API no inicializados"
        assert system.tools is not None, "Herramientas no inicializadas"
        self.logger.info("✓ Inicialización del sistema correcta")
    
    async def test_security_features(self):
        """Prueba las características de seguridad."""
        self.logger.info("Probando características de seguridad...")
        system = AISystem()
        
        test_cases = [
            ("localhost", {"depth": "standard", "stealth": True}),
            ("example.com", {"depth": "deep", "stealth": False}),
        ]
        
        for target, options in test_cases:
            result = await system.process_security_scan(target, options)
            assert isinstance(result, dict), "El resultado debe ser un diccionario"
            assert "vulnerabilities" in result, "Falta información de vulnerabilidades"
        
        self.logger.info("✓ Pruebas de seguridad completadas")
    
    async def test_financial_features(self):
        """Prueba las características financieras."""
        self.logger.info("Probando análisis financiero...")
        system = AISystem()
        
        test_data = {
            "transactions": [
                {"amount": 1000, "timestamp": "2025-05-14T10:00:00Z", "type": "deposit"},
                {"amount": -500, "timestamp": "2025-05-14T11:00:00Z", "type": "withdrawal"},
            ]
        }
        
        result = await system.analyze_financial_data(test_data, "anomaly_detection")
        assert isinstance(result, dict), "El resultado debe ser un diccionario"
        assert "anomalies" in result, "Falta información de anomalías"
        
        self.logger.info("✓ Pruebas financieras completadas")
    
    async def test_entropy_generation(self):
        """Prueba la generación de entropía."""
        self.logger.info("Probando generación de entropía...")
        system = AISystem()
        
        test_cases = [
            (256, "quantum"),
            (512, "thermal"),
            (1024, "photonic")
        ]
        
        for bits, source in test_cases:
            entropy = system.generate_entropy(bits, source)
            assert isinstance(entropy, bytes), "La entropía debe ser bytes"
            assert len(entropy) == bits // 8, "Longitud incorrecta de entropía"
        
        self.logger.info("✓ Pruebas de entropía completadas")
    
    async def test_code_obfuscation(self):
        """Prueba la ofuscación de código."""
        self.logger.info("Probando ofuscación de código...")
        system = AISystem()
        
        test_code = """
def calculate_sum(a: int, b: int) -> int:
    return a + b
"""
        languages = ["python", "javascript", "java"]
        levels = [1, 3, 5]
        
        for lang in languages:
            for level in levels:
                result = system.obfuscate_code(test_code, lang, level)
                assert isinstance(result, str), "El resultado debe ser string"
                assert result != test_code, "El código no fue ofuscado"
        
        self.logger.info("✓ Pruebas de ofuscación completadas")

def run_tests():
    """Función principal para ejecutar todas las pruebas."""
    suite = TestSuite()
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(suite.run_tests())
    
    if success:
        print("\n✨ Todas las pruebas completadas exitosamente!")
        sys.exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los logs para más detalles.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
