import sys
print(f"1. Python Version: {sys.version}")

try:
    print("\n2. Loading dotenv")
    from dotenv import load_dotenv
    import os
    load_dotenv()
    print("   .env loaded successfully")
    print(f"   ANTHROPIC_API_KEY present: {'Yes' if os.getenv('ANTHROPIC_API_KEY') else 'No'}")
    print(f"   OPENAI_API_KEY present: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
except Exception as e:
    print(f"   Error loading dotenv: {e}")

try:
    print("\n3. Testing Anthropic import")
    import anthropic
    print("   Anthropic imported successfully")
except Exception as e:
    print(f"   Error importing Anthropic: {e}")

try:
    print("\n4. Testing OpenAI import")
    import openai
    print("   OpenAI imported successfully")
except Exception as e:
    print(f"   Error importing OpenAI: {e}")

print("\nDiagnóstico completado")
