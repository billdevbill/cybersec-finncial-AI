import os
from dotenv import load_dotenv
import anthropic
import openai

# Cargar variables de entorno
load_dotenv()

def test_connections():
    print("Probando conexiones a APIs...")
    
    # Probar Anthropic
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        print("✓ Conexión a Anthropic exitosa")
    except Exception as e:
        print(f"✗ Error con Anthropic: {e}")
    
    # Probar OpenAI
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("✓ Conexión a OpenAI exitosa")
    except Exception as e:
        print(f"✗ Error con OpenAI: {e}")

if __name__ == "__main__":
    test_connections()
