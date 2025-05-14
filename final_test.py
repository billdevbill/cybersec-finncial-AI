import os
import sys
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('final_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def check_environment() -> Dict[str, Any]:
    """Check Python environment and installed packages"""
    env_info = {
        "python_version": sys.version,
        "python_path": sys.executable,
        "working_dir": os.getcwd(),
        "pythonpath": os.getenv("PYTHONPATH", "Not set"),
        "packages": {}
    }
    
    try:
        from dotenv import load_dotenv
        env_info["packages"]["python-dotenv"] = "✓"
        load_dotenv(dotenv_path=Path(".env"))
    except Exception as e:
        env_info["packages"]["python-dotenv"] = f"✗ ({str(e)})"
        logger.error(f"Error loading dotenv: {e}")
    
    # Check API keys
    env_info["api_keys"] = {
        "ANTHROPIC_API_KEY": "✓" if os.getenv("ANTHROPIC_API_KEY") else "✗",
        "OPENAI_API_KEY": "✓" if os.getenv("OPENAI_API_KEY") else "✗"
    }
    
    return env_info

async def test_anthropic() -> Dict[str, Any]:
    """Test Anthropic API connection"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=100,
            messages=[{"role": "user", "content": "Respond with one word: Test?"}]
        )
        
        return {
            "status": "success",
            "response": response.content[0].text,
            "model": "claude-3-opus-20240229"
        }
    except Exception as e:
        logger.error(f"Anthropic test failed: {traceback.format_exc()}")
        return {
            "status": "error",
            "error": str(e)
        }

async def test_openai() -> Dict[str, Any]:
    """Test OpenAI API connection"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "Respond with one word: Test?"}]
        )
        
        return {
            "status": "success",
            "response": response.choices[0].message.content,
            "model": "gpt-4-turbo-preview"
        }
    except Exception as e:
        logger.error(f"OpenAI test failed: {traceback.format_exc()}")
        return {
            "status": "error",
            "error": str(e)
        }

async def main():
    """Main test function"""
    import asyncio
    logger.info("Starting final system test...")
    
    # Check environment
    env_info = check_environment()
    logger.info("\nEnvironment Information:")
    for key, value in env_info.items():
        logger.info(f"{key}: {value}")
    
    # Test APIs
    logger.info("\nTesting APIs...")
    
    # Run API tests concurrently
    anthropic_result, openai_result = await asyncio.gather(
        test_anthropic(),
        test_openai(),
        return_exceptions=True
    )
    
    # Log results
    logger.info("\nTest Results:")
    logger.info(f"Anthropic API: {anthropic_result}")
    logger.info(f"OpenAI API: {openai_result}")
    
    # Determine overall success
    success = (
        isinstance(anthropic_result, dict) and 
        isinstance(openai_result, dict) and
        anthropic_result.get("status") == "success" and
        openai_result.get("status") == "success"
    )
    
    logger.info(f"\nFinal Status: {'✓ Success' if success else '✗ Failed'}")
    return success

if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {traceback.format_exc()}")
        sys.exit(1)
