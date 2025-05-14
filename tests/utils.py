import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_run.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def check_environment() -> Dict[str, Any]:
    """Check Python environment and installed packages"""
    env_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "working_directory": os.getcwd(),
        "platform": sys.platform
    }
    
    # Load and check environment variables
    load_dotenv()
    required_env_vars = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
    env_info["env_vars_status"] = {
        var: "Present" if os.getenv(var) else "Missing" 
        for var in required_env_vars
    }
    
    # Check required packages
    required_packages = ["anthropic", "openai", "torch", "numpy", "streamlit"]
    env_info["packages_status"] = {}
    
    for package in required_packages:
        try:
            __import__(package)
            env_info["packages_status"][package] = "Installed"
        except ImportError as e:
            env_info["packages_status"][package] = f"Missing: {str(e)}"
    
    return env_info

async def test_api_connection(api: str) -> Dict[str, Any]:
    """Test connection to an API service"""
    try:
        if api.lower() == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            return {"status": "success", "message": "Anthropic API connection successful"}
        
        elif api.lower() == "openai":
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            return {"status": "success", "message": "OpenAI API connection successful"}
        
        else:
            return {"status": "error", "message": f"Unknown API: {api}"}
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to {api} API",
            "error": str(e)
        }

def run_async_test(test_func: callable) -> None:
    """Run an async test function with proper Windows event loop handling"""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_func())
