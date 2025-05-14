import os
from dotenv import load_dotenv
import anthropic
import openai
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno
load_dotenv()

def main():
    print("Iniciando pruebas básicas...")
    
    # Probar Anthropic
    try:
        print("\nProbando Anthropic:")
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        print("Cliente Anthropic creado exitosamente")
    except Exception as e:
        print(f"Error con Anthropic: {e}")
    
    # Probar OpenAI
    try:
        print("\nProbando OpenAI:")
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("Cliente OpenAI creado exitosamente")
    except Exception as e:
        print(f"Error con OpenAI: {e}")

if __name__ == "__main__":
    main()
