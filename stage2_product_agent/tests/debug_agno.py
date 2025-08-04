"""Debug script for Agno agent MCP integration."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def debug_agno_agent():
    """Debug the Agno agent MCP integration."""
    try:
        from agno_agent import ProductCatalogAgnoAgent
        
        print("Debugging Agno Agent MCP Integration")
        print("=" * 50)
        
        # Check if API key is available
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("⚠️  No API key found")
            return False
        
        # Initialize agent
        print("Initializing Agno agent...")
        agent = ProductCatalogAgnoAgent()
        print("✅ Agno agent initialized")
        
        # Test a simple query
        test_query = "Show me all products in the electronics category"
        print(f"\nTesting query: {test_query}")
        print("-" * 40)
        
        # Process query
        print("Processing query...")
        response = agent.query(test_query)
        
        # Handle RunResponse object
        if hasattr(response, 'content'):
            response_text = response.content
        elif hasattr(response, 'message'):
            response_text = response.message
        else:
            response_text = str(response)
        
        print(f"\nResponse length: {len(response_text)}")
        print(f"Response preview: {response_text[:200]}...")
        
        # Check if response contains actual data indicators
        if "electronics" in response_text.lower() or "product" in response_text.lower():
            print("✅ Response appears to contain real data")
            return True
        else:
            print("❌ Response may not be using real MCP data")
            print(f"Full response: {response_text}")
            return False
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_agno_agent()
    sys.exit(0 if success else 1) 