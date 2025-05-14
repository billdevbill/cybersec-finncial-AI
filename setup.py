# Initial setup and configuration script
import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('setup.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the Python environment"""
    try:
        # Create virtual environment if it doesn't exist
        if not Path('venv').exists():
            logger.info("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Get the virtual environment Python path
        if sys.platform == "win32":
            venv_python = Path('venv/Scripts/python.exe')
        else:
            venv_python = Path('venv/bin/python')
        
        # Upgrade pip
        logger.info("Upgrading pip...")
        subprocess.run([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # Install requirements
        logger.info("Installing requirements...")
        subprocess.run([str(venv_python), '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        
        logger.info("Environment setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        return False

def verify_installation():
    """Verify the installation"""
    try:
        # Import test
        import anthropic
        import openai
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Check API keys
        api_keys = {
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
        }
        
        missing_keys = [k for k, v in api_keys.items() if not v]
        if missing_keys:
            logger.error(f"Missing API keys: {missing_keys}")
            return False
        
        logger.info("Installation verified successfully")
        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return False

if __name__ == "__main__":
    try:
        logger.info("Starting setup process...")
        if setup_environment() and verify_installation():
            logger.info("Setup completed successfully!")
            sys.exit(0)
        else:
            logger.error("Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
