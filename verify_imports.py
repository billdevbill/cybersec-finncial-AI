print("Iniciando prueba...")

try:
    import anthropic
    print("Anthropic importado correctamente")
except Exception as e:
    print(f"Error importando Anthropic: {e}")

try:
    import openai
    print("OpenAI importado correctamente")
except Exception as e:
    print(f"Error importando OpenAI: {e}")

try:
    from dotenv import load_dotenv
    print("python-dotenv importado correctamente")
except Exception as e:
    print(f"Error importando python-dotenv: {e}")

print("Prueba completada")
