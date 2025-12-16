#!/usr/bin/env python3
"""
Setup validation script for Prospecting module

Tests:
1. Python dependencies installed
2. API keys configured
3. Module imports work
4. Cache directory exists
5. Basic client initialization

Usage:
    cd prospecting-public
    python3 scripts/utilities/test_setup.py
"""

import sys
import os
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def test_dependencies():
    """Test that required Python packages are installed."""
    print("\n1. Testing Python dependencies...")

    try:
        import requests
        print_success("requests library installed")
    except ImportError:
        print_error("requests not installed. Run: pip3 install requests")
        return False

    try:
        import dotenv
        print_success("python-dotenv library installed")
    except ImportError:
        print_error("python-dotenv not installed. Run: pip3 install python-dotenv")
        return False

    return True

def test_api_keys():
    """Test that API keys are configured in .env file."""
    print("\n2. Testing API keys configuration...")

    env_path = Path(__file__).parent.parent / '.env'

    if not env_path.exists():
        print_error(f".env file not found at {env_path}")
        print_warning("Create .env file by copying .env.example and adding your API keys")
        return False

    print_success(f".env file exists at {env_path}")

    from dotenv import load_dotenv
    load_dotenv(env_path)

    # Check ZoomInfo PKI authentication variables
    zoominfo_username = os.getenv('ZOOMINFO_USERNAME')
    zoominfo_client_id = os.getenv('ZOOMINFO_CLIENT_ID')
    zoominfo_key_file = os.getenv('ZOOMINFO_PRIVATE_KEY_FILE', '.zoominfo_private_key.pem')
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')

    # Test ZoomInfo configuration
    all_zi_configured = True
    if not zoominfo_username or zoominfo_username == 'your_username@example.com':
        print_error("ZOOMINFO_USERNAME not configured in .env")
        all_zi_configured = False
    else:
        print_success(f"ZOOMINFO_USERNAME configured: {zoominfo_username}")

    if not zoominfo_client_id or zoominfo_client_id == 'your-client-id-uuid':
        print_error("ZOOMINFO_CLIENT_ID not configured in .env")
        all_zi_configured = False
    else:
        print_success(f"ZOOMINFO_CLIENT_ID configured: {zoominfo_client_id[:8]}...")

    # Check if private key file exists
    key_file_path = Path(__file__).parent.parent / zoominfo_key_file
    if not key_file_path.exists():
        print_error(f"ZOOMINFO_PRIVATE_KEY_FILE not found: {key_file_path}")
        all_zi_configured = False
    else:
        print_success(f"ZOOMINFO_PRIVATE_KEY_FILE found: {zoominfo_key_file}")

    if not perplexity_key or perplexity_key == 'pplx-your_perplexity_api_key_here':
        print_error("PERPLEXITY_API_KEY not configured in .env")
        return False
    else:
        print_success(f"PERPLEXITY_API_KEY configured (length: {len(perplexity_key)})")

    return all_zi_configured

def test_module_imports():
    """Test that all Prospecting modules can be imported."""
    print("\n3. Testing module imports...")

    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from src.caching import ContactCache, APIResponseCache
        print_success("caching.py imports successfully")
    except Exception as e:
        print_error(f"Failed to import caching.py: {e}")
        return False

    try:
        from src.zoominfo_client import ZoomInfoClient
        print_success("zoominfo_client.py imports successfully")
    except Exception as e:
        print_error(f"Failed to import zoominfo_client.py: {e}")
        return False

    try:
        from src.perplexity_client import PerplexityClient
        print_success("perplexity_client.py imports successfully")
    except Exception as e:
        print_error(f"Failed to import perplexity_client.py: {e}")
        return False

    try:
        from src.research_orchestrator import ResearchOrchestrator
        print_success("research_orchestrator.py imports successfully")
    except Exception as e:
        print_error(f"Failed to import research_orchestrator.py: {e}")
        return False

    try:
        from src.context_synthesizer import ContextSynthesizer, format_research_brief
        print_success("context_synthesizer.py imports successfully")
    except Exception as e:
        print_error(f"Failed to import context_synthesizer.py: {e}")
        return False

    try:
        from src.quality_controls import ProspectEmailLinter
        print_success("quality_controls.py imports successfully")
    except Exception as e:
        print_error(f"Failed to import quality_controls.py: {e}")
        return False

    return True

def test_cache_directory():
    """Test that cache directory exists and is writable."""
    print("\n4. Testing cache directory...")

    cache_dir = Path(__file__).parent.parent / '.cache' / 'prospects'

    if not cache_dir.exists():
        print_warning(f"Cache directory doesn't exist, creating: {cache_dir}")
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            print_success("Cache directory created")
        except Exception as e:
            print_error(f"Failed to create cache directory: {e}")
            return False
    else:
        print_success(f"Cache directory exists: {cache_dir}")

    # Test write permission
    test_file = cache_dir / '.test_write'
    try:
        test_file.write_text('test')
        test_file.unlink()
        print_success("Cache directory is writable")
    except Exception as e:
        print_error(f"Cache directory not writable: {e}")
        return False

    return True

def test_client_initialization():
    """Test that API clients can be initialized."""
    print("\n5. Testing client initialization...")

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')

    zoominfo_username = os.getenv('ZOOMINFO_USERNAME')
    zoominfo_client_id = os.getenv('ZOOMINFO_CLIENT_ID')
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')

    # Test ZoomInfo client with JWT authentication
    if not zoominfo_username or not zoominfo_client_id:
        print_warning("Skipping ZoomInfo client test (credentials not configured)")
    else:
        try:
            from src.zoominfo_client import ZoomInfoClient
            from src.zoominfo_jwt_manager import ZoomInfoJWTManager

            jwt_manager = ZoomInfoJWTManager()
            client = ZoomInfoClient(jwt_manager)
            print_success("ZoomInfo client initialized successfully")
        except Exception as e:
            print_error(f"Failed to initialize ZoomInfo client: {e}")
            return False

    if not perplexity_key or perplexity_key == 'your_perplexity_api_key_here':
        print_warning("Skipping Perplexity client test (no API key)")
    else:
        try:
            from src.perplexity_client import PerplexityClient
            client = PerplexityClient(api_key=perplexity_key)
            print_success("Perplexity client initialized successfully")
        except Exception as e:
            print_error(f"Failed to initialize Perplexity client: {e}")
            return False

    try:
        from src.caching import ContactCache
        cache = ContactCache()
        print_success("ContactCache initialized successfully")
    except Exception as e:
        print_error(f"Failed to initialize ContactCache: {e}")
        return False

    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Prospecting Module Setup Validation")
    print("=" * 60)

    results = []

    results.append(("Dependencies", test_dependencies()))
    results.append(("API Keys", test_api_keys()))
    results.append(("Module Imports", test_module_imports()))
    results.append(("Cache Directory", test_cache_directory()))
    results.append(("Client Initialization", test_client_initialization()))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        if passed:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
            all_passed = False

    print("=" * 60)

    if all_passed:
        print(f"\n{GREEN}All tests passed!{RESET} Prospecting module is ready to use.")
        print(f"\nNext steps:")
        print(f"1. Test the module: python3 scripts/run_prospect_research.py \"John Smith\" \"Acme Corp\"")
        print(f"2. Or use the slash command: /prospect \"John Smith\" \"Acme Corp\"")
        return 0
    else:
        print(f"\n{RED}Some tests failed.{RESET} Please fix the issues above before using the module.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
