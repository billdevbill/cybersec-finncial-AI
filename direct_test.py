import os
import sys
import logging
from dotenv import load_dotenv
import asyncio

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('direct_test.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_claude():
    """Test Anthropic's Claude API"""
    try:
        import anthropic
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        # Simple test message
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Responde con una palabra: ¿Estás funcionando?"
            }]
        )
        
        result = response.content[0].text
        logger.info(f"Claude response: {result}")
        return True
    except Exception as e:
        logger.error(f"Claude test failed: {str(e)}")
        return False

async def test_gpt():
    """Test OpenAI's GPT API"""
    try:
        import openai
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Simple test message
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{
                "role": "user", 
                "content": "Responde con una palabra: ¿Estás funcionando?"
            }]
        )
        
        result = response.choices[0].message.content
        logger.info(f"GPT response: {result}")
        return True
    except Exception as e:
        logger.error(f"GPT test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    logger.info("Starting direct tests...")
    
    # Load environment variables
    load_dotenv()
    
    # Verify environment variables
    required_vars = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing environment variables: {missing}")
        return False

    # Run tests
    results = await asyncio.gather(
        test_claude(),
        test_gpt()
    )
    
    success = all(results)
    logger.info(f"Tests completed. Success: {success}")
    return success

if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)
