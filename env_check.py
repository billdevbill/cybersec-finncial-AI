import os
import sys
from dotenv import load_dotenv

def main():
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)
    print("\nChecking .env and environment variables...")
    
    # Load .env file
    load_dotenv()
    
    # Check environment variables
    env_vars = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL")
    }
    
    for var, value in env_vars.items():
        print(f"{var}: {'Present' if value else 'Missing'}")
    
    print("\nTesting imports...")
    
    try:
        import anthropic
        print("✓ anthropic import successful")
    except ImportError as e:
        print(f"✗ anthropic import failed: {e}")
    
    try:
        import openai
        print("✓ openai import successful")
    except ImportError as e:
        print(f"✗ openai import failed: {e}")

if __name__ == "__main__":
    main()
