"""Product Catalog Agent - Stage 2 of Agent Oriented Architecture.

This agent provides intelligent interaction with the product catalog,
using SMOL agents to add business intelligence on top of the MCP server.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp import StdioServerParameters
from smolagents import CodeAgent, LiteLLMModel, MCPClient

# Add parent directory to path to import from stage1
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables only if not in Docker
# Docker Compose passes environment variables directly
if not os.getenv("DOCKER_CONTAINER", False):
    load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductCatalogAgent:
    """Intelligent agent for product catalog queries and recommendations."""

    def __init__(self):
        """Initialize the Product Catalog Agent."""
        # Load configuration
        self.agent_name = os.getenv("AGENT_NAME", "ProductCatalogAssistant")
        self.agent_description = os.getenv(
            "AGENT_DESCRIPTION",
            "An intelligent assistant for product catalog queries and recommendations"
        )
        
        # Initialize LLM
        model_id = os.getenv("LLM_MODEL", "claude-3-7-sonnet-20250219")
        
        # Determine which API key to use based on the model
        if model_id.startswith("gpt") or model_id.startswith("o1"):
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    f"OpenAI model '{model_id}' specified but OPENAI_API_KEY not found in .env"
                )
        else:
            # Default to Anthropic for claude models
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    f"Anthropic model '{model_id}' specified but ANTHROPIC_API_KEY not found in .env"
                )
        
        self.model = LiteLLMModel(model_id=model_id, api_key=api_key)
        logger.info(f"Initialized LLM: {model_id}")
        
        # Initialize MCP client using SMOL agents' native support
        mcp_server_path = os.getenv(
            "MCP_SERVER_PATH",
            "stage1_mcp_product_server/server_fastmcp.py"
        )
        
        # If path is relative, resolve from project root
        if not Path(mcp_server_path).is_absolute():
            project_root = Path(__file__).parent.parent
            mcp_server_path = project_root / mcp_server_path
        else:
            mcp_server_path = Path(mcp_server_path)
        
        if not mcp_server_path.exists():
            raise FileNotFoundError(f"MCP server not found at {mcp_server_path}")
        
        # Set up MCP server parameters for stdio communication
        self.server_params = StdioServerParameters(
            command=sys.executable,  # Use current Python interpreter
            args=[str(mcp_server_path)],
            env={**os.environ}  # Pass through environment
        )
        
        logger.info(f"Configured MCP server at {mcp_server_path}")
        
        # Initialize MCP client and keep it alive
        self.mcp_client = MCPClient(self.server_params)
        self.mcp_tools = self.mcp_client.get_tools()
        logger.info(f"Connected to MCP server with {len(self.mcp_tools)} tools")
        
        # Initialize the agent with all tools
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the SMOL agent with all tools."""
        # Import business intelligence tools
        from stage2_product_agent.tools.product_tools import (
            AnalyzePriceTrendsTool,
            FindSimilarProductsTool,
            GenerateProductRecommendationsTool,
            NaturalLanguageProductSearchTool,
        )
        
        # Create business intelligence tools with MCP access
        mcp_tools_dict = {tool.name: tool for tool in self.mcp_tools}
        
        business_tools = [
            FindSimilarProductsTool(mcp_tools_dict),
            AnalyzePriceTrendsTool(mcp_tools_dict),
            GenerateProductRecommendationsTool(mcp_tools_dict),
            NaturalLanguageProductSearchTool(mcp_tools_dict),
        ]
        
        # Combine all tools
        all_tools = list(self.mcp_tools) + business_tools
        
        # Create the agent
        self.agent = CodeAgent(
            tools=all_tools,
            model=self.model,
            add_base_tools=False,  # We don't need web search or other base tools
            name=self.agent_name,
            description=self.agent_description,
            max_steps=10,
            verbosity_level=1
        )
        
        logger.info(f"Initialized agent with {len(all_tools)} tools")

    def run(self, query: str, **kwargs) -> str:
        """Run the agent with a query.

        Args:
            query: The user's query
            **kwargs: Additional arguments for the agent

        Returns:
            The agent's response
        """
        try:
            logger.info(f"Processing query: {query}")
            result = self.agent.run(query, **kwargs)
            logger.info("Query processed successfully")
            return result
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"

    def get_customer_insights(self, customer_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze customer purchase history to derive preferences.

        Args:
            customer_history: List of previous purchases/interactions

        Returns:
            Dictionary of inferred customer preferences
        """
        preferences = {
            "categories": [],
            "budget_min": float('inf'),
            "budget_max": 0,
            "avg_rating_preference": 0,
            "brand_preferences": [],
            "keywords": []
        }
        
        if not customer_history:
            return preferences
        
        # Analyze history
        categories = {}
        brands = {}
        total_rating = 0
        rating_count = 0
        
        for item in customer_history:
            # Track categories
            cat = item.get("category")
            if cat:
                categories[cat] = categories.get(cat, 0) + 1
            
            # Track price range
            price = item.get("price", 0)
            if price:
                preferences["budget_min"] = min(preferences["budget_min"], price * 0.7)
                preferences["budget_max"] = max(preferences["budget_max"], price * 1.3)
            
            # Track brands
            brand = item.get("brand")
            if brand:
                brands[brand] = brands.get(brand, 0) + 1
            
            # Track ratings
            rating = item.get("rating", 0)
            if rating > 0:
                total_rating += rating
                rating_count += 1
        
        # Set preferences based on history
        if categories:
            preferences["categories"] = [k for k, _ in sorted(
                categories.items(), key=lambda x: x[1], reverse=True
            )][:3]
        
        if brands:
            preferences["brand_preferences"] = [k for k, _ in sorted(
                brands.items(), key=lambda x: x[1], reverse=True
            )][:3]
        
        if rating_count > 0:
            preferences["avg_rating_preference"] = total_rating / rating_count
            preferences["min_rating"] = max(3.0, preferences["avg_rating_preference"] - 0.5)
        
        # Reset infinite budget min
        if preferences["budget_min"] == float('inf'):
            preferences["budget_min"] = 0
        
        return preferences

    def __del__(self):
        """Clean up MCP client connection."""
        if hasattr(self, 'mcp_client'):
            try:
                self.mcp_client.disconnect()
                logger.info("Disconnected from MCP server")
            except Exception as e:
                logger.error(f"Error disconnecting from MCP server: {e}")


def main():
    """Main function to run the agent interactively."""
    print(f"\n{'='*60}")
    print("Product Catalog Agent - Stage 2")
    print("Intelligent Assistant for Product Queries")
    print(f"{'='*60}\n")
    
    agent = None
    try:
        # Initialize agent
        agent = ProductCatalogAgent()
        print(f"✅ Agent 'Product Catalog Assistant' initialized successfully!")
        print("\nAvailable capabilities:")
        print("- Natural language product search")
        print("- Price trend analysis")
        print("- Similar product recommendations")
        print("- Personalized recommendations")
        print("- Database queries")
        print("\nType 'quit' to exit.\n")
        
        # Interactive loop
        while True:
            try:
                query = input("You: ").strip()
                if query.lower() in ['quit', 'exit', 'bye']:
                    print("\nGoodbye! 👋")
                    break
                
                if not query:
                    continue
                
                print("\nAgent: ", end="", flush=True)
                response = agent.run(query)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("\nPlease check:")
        print("1. You have created a .env file with your API key")
        print("2. The MCP server from Stage 1 is accessible")
        print("3. All dependencies are installed (uv sync)")
        sys.exit(1)
    finally:
        # Clean up
        if agent:
            del agent


if __name__ == "__main__":
    main()