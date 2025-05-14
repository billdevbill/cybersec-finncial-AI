print("Starting minimal test...")

try:
    print("\nTesting dotenv...")
    from dotenv import load_dotenv
    load_dotenv()
    print("dotenv loaded successfully")
except Exception as e:
    print(f"dotenv error: {e}")

try:
    print("\nTesting anthropic...")
    import anthropic
    print("anthropic loaded successfully")
except Exception as e:
    print(f"anthropic error: {e}")

try:
    print("\nTesting openai...")
    import openai
    print("openai loaded successfully")
except Exception as e:
    print(f"openai error: {e}")

print("\nTest complete")
