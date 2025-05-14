import unittest
import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from AI1 import AISystem
from tests.utils import check_environment, test_api_connection

logger = logging.getLogger(__name__)

class TestAISystem(unittest.TestCase):
    """Test cases for the AI System"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.ai_system = AISystem()
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    def test_environment_setup(self):
        """Test Python environment and package installation"""
        env_info = check_environment()
        
        # Verify Python version
        self.assertGreaterEqual(tuple(map(int, sys.version.split()[0].split("."))), (3, 9))
        
        # Verify required packages
        for package, status in env_info["packages_status"].items():
            self.assertEqual(status, "Installed", f"Package {package} not properly installed")
        
        # Verify environment variables
        for var, status in env_info["env_vars_status"].items():
            self.assertEqual(status, "Present", f"Environment variable {var} is missing")
    
    def test_system_initialization(self):
        """Test system initialization"""
        self.assertIsNotNone(self.ai_system.config)
        self.assertIsNotNone(self.ai_system.clients)
        self.assertIsInstance(self.ai_system.memory_system.retention_period, int)
        self.assertGreater(self.ai_system.memory_system.cache_size, 0)
    
    async def test_api_connections(self):
        """Test API connections"""
        anthropic_result = await test_api_connection("anthropic")
        self.assertEqual(anthropic_result["status"], "success")
        
        openai_result = await test_api_connection("openai")
        self.assertEqual(openai_result["status"], "success")
    
    async def test_security_scan(self):
        """Test security scanning functionality"""
        test_target = "localhost"
        options = {"depth": "standard", "stealth": True}
        
        result = await self.ai_system.process_security_scan(test_target, options)
        self.assertIsInstance(result, dict)
        self.assertIn("vulnerabilities", result)
    
    async def test_financial_analysis(self):
        """Test financial analysis functionality"""
        test_data = {
            "transactions": [
                {"amount": 1000, "timestamp": datetime.now().isoformat(), "type": "deposit"},
                {"amount": -500, "timestamp": datetime.now().isoformat(), "type": "withdrawal"}
            ]
        }
        
        result = await self.ai_system.analyze_financial_data(test_data, "anomaly_detection")
        self.assertIsInstance(result, dict)
        self.assertIn("anomalies", result)
    
    async def test_memory_system(self):
        """Test memory system functionality"""
        test_data = {"test_key": "test_value"}
        category = "test"
        
        # Test storing and retrieving memory
        await self.ai_system.memory_system.store_memory(
            content=test_data,
            category=category,
            importance=0.8
        )
        
        memories = await self.ai_system.memory_system.retrieve_memories(
            category=category,
            limit=1,
            min_importance=0.5
        )
        
        self.assertIsInstance(memories, list)
        self.assertGreater(len(memories), 0)
        self.assertEqual(memories[0]["content"]["test_key"], "test_value")
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = self.ai_system.config
        required_keys = [
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY",
            "MAX_TOKENS",
            "TEMPERATURE"
        ]
        
        for key in required_keys:
            self.assertIn(key, config)
            self.assertIsNotNone(config[key])

def run_tests():
    """Run all tests with proper async support"""
    # Set up async event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAISystem)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
