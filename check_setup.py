import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")
print("\nTrying to import required packages:")

def test_import(package_name):
    try:
        module = __import__(package_name)
        print(f"✓ {package_name} imported successfully (version: {getattr(module, '__version__', 'unknown')})")
        return True
    except ImportError as e:
        print(f"✗ Failed to import {package_name}: {str(e)}")
        return False

# Test imports
packages = ['anthropic', 'openai', 'dotenv']
all_success = all(test_import(pkg) for pkg in packages)

if all_success:
    print("\nAll packages imported successfully!")
else:
    print("\nSome packages failed to import. Please check the installation.")
