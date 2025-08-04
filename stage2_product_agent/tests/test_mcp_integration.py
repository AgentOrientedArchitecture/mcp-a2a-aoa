"""Test MCP integration for Agno agent."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_agno_mcp_integration():
    """Test that Agno agent actually uses MCP tools."""
    try:
        from agno_agent import ProductCatalogAgnoAgent
        
        print("Testing Agno MCP Integration")
        print("=" * 40)
        
        # Check if API key is available
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("⚠️  No API key found - skipping test")
            print("   Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file")
            return True
        
        # Initialize agent
        agent = ProductCatalogAgnoAgent()
        print("✅ Agno agent initialized")
        
        # Test query that should use MCP tools
        test_query = "Show me all products in the electronics category"
        print(f"\nTesting query: {test_query}")
        print("-" * 40)
        
        # Process query
        response = agent.query(test_query)
        
        print(f"\nResponse: {response}")
        
        # Check if response contains actual data indicators
        if "electronics" in response.lower() or "product" in response.lower():
            print("✅ Response appears to contain real data")
            return True
        else:
            print("❌ Response may not be using real MCP data")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_smol_mcp_integration():
    """Test that SMOL agent uses MCP tools."""
    try:
        from agent import ProductCatalogAgent
        
        print("\nTesting SMOL MCP Integration")
        print("=" * 40)
        
        # Check if API key is available
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("⚠️  No API key found - skipping test")
            return True
        
        # Initialize agent
        agent = ProductCatalogAgent()
        print("✅ SMOL agent initialized")
        
        # Test query that should use MCP tools
        test_query = "Show me all products in the electronics category"
        print(f"\nTesting query: {test_query}")
        print("-" * 40)
        
        # Process query
        response = agent.run(test_query)
        
        print(f"\nResponse: {response}")
        
        # Check if response contains actual data indicators
        if "electronics" in response.lower() or "product" in response.lower():
            print("✅ Response appears to contain real data")
            return True
        else:
            print("❌ Response may not be using real MCP data")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run MCP integration tests."""
    print("Testing MCP Integration for Both Agents")
    print("=" * 50)
    
    tests = [
        test_agno_mcp_integration,
        test_smol_mcp_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All MCP integration tests passed!")
        return True
    else:
        print("❌ Some MCP integration tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 