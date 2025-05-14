import sys
import os

def main():
    print("System Information:")
    print("-" * 50)
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    print("\nPython Path:")
    for path in sys.path:
        print(f"  - {path}")
        
    print("\nTrying to import required packages:")
    try:
        import dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        
    try:
        import anthropic
        print("✓ anthropic")
    except ImportError as e:
        print(f"✗ anthropic: {e}")
        
    try:
        import openai
        print("✓ openai")
    except ImportError as e:
        print(f"✗ openai: {e}")

if __name__ == "__main__":
    main()
