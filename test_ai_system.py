import unittest
import asyncio
from AI1 import AISystem
import os
import logging

logging.basicConfig(level=logging.INFO)

class TestAISystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para las pruebas."""
        cls.ai_system = AISystem()
    
    def test_system_initialization(self):
        """Prueba la inicialización del sistema."""
        self.assertIsNotNone(self.ai_system.config)
        self.assertIsNotNone(self.ai_system.clients)
        self.assertIsNotNone(self.ai_system.tools)
    
    def test_config_loading(self):
        """Prueba la carga de configuración."""
        config = self.ai_system.config
        self.assertIsNotNone(config["ANTHROPIC_API_KEY"])
        self.assertIsNotNone(config["OPENAI_API_KEY"])
    
    def test_tools_initialization(self):
        """Prueba la inicialización de herramientas."""
        tools = self.ai_system.tools
        self.assertIn("security", tools)
        self.assertIn("financial", tools)
        self.assertIn("entropy", tools)
        self.assertIn("code", tools)
    
    async def test_security_scan(self):
        """Prueba el análisis de seguridad."""
        result = await self.ai_system.process_security_scan(
            "example.com",
            {"depth": "standard", "stealth": True}
        )
        self.assertIsInstance(result, dict)
    
    def test_entropy_generation(self):
        """Prueba la generación de entropía."""
        entropy = self.ai_system.generate_entropy(
            bits=256,
            source="quantum"
        )
        self.assertIsInstance(entropy, bytes)
        self.assertEqual(len(entropy), 32)  # 256 bits = 32 bytes
    
    async def test_financial_analysis(self):
        """Prueba el análisis financiero."""
        test_data = {
            "transactions": [
                {"amount": 1000, "type": "deposit"},
                {"amount": -500, "type": "withdrawal"}
            ]
        }
        result = await self.ai_system.analyze_financial_data(
            test_data,
            "anomaly_detection"
        )
        self.assertIsInstance(result, dict)
    
    def test_code_obfuscation(self):
        """Prueba la ofuscación de código."""
        test_code = """
def hello_world():
    print("Hello, World!")
"""
        obfuscated = self.ai_system.obfuscate_code(
            test_code,
            "python",
            level=3
        )
        self.assertIsInstance(obfuscated, str)
        self.assertNotEqual(test_code, obfuscated)

def run_async_tests():
    """Ejecuta pruebas asíncronas."""
    loop = asyncio.get_event_loop()
    test_instance = TestAISystem()
    
    async def run_tests():
        await test_instance.test_security_scan()
        await test_instance.test_financial_analysis()
    
    loop.run_until_complete(run_tests())

if __name__ == '__main__':
    # Ejecutar pruebas síncronas
    unittest.main(verbosity=2, exit=False)
    
    # Ejecutar pruebas asíncronas
    run_async_tests()
