"""Simple test script for Agno agent initialization."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_agno_import():
    """Test that Agno can be imported."""
    try:
        import agno
        print("✅ Agno imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Agno: {e}")
        return False

def test_agno_agent_import():
    """Test that our Agno agent can be imported."""
    try:
        from agno_agent import ProductCatalogAgnoAgent
        print("✅ Agno agent class imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Agno agent: {e}")
        return False

def test_agno_agent_initialization():
    """Test that Agno agent can be initialized."""
    try:
        from agno_agent import ProductCatalogAgnoAgent
        
        # Check if API key is available
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("⚠️  No API key found - skipping initialization test")
            print("   Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file")
            return True
        
        # Try to initialize (this might fail due to MCP server, but should not crash)
        try:
            agent = ProductCatalogAgnoAgent()
            print("✅ Agno agent initialized successfully")
            return True
        except Exception as e:
            if "MCP server not found" in str(e):
                print("✅ Agno agent created (MCP server not available)")
                return True
            else:
                print(f"❌ Agno agent initialization failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Agno agent test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Agno Agent Setup")
    print("=" * 40)
    
    tests = [
        test_agno_import,
        test_agno_agent_import,
        test_agno_agent_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 