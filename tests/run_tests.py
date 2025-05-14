import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
log_file = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)

def run_all_tests():
    """Run all system tests."""
    logger.info("Starting test suite execution...")
    
    try:
        # Change to project root directory
        os.chdir(project_root)
        
        # Import and run our consolidated test suite
        from tests.test_ai_system import run_tests
        success = run_tests()
        
        if success:
            logger.info("✨ All tests completed successfully!")
        else:
            logger.error("❌ Some tests failed!")
        
        return success
        
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
