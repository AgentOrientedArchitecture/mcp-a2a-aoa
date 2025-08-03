"""A2A-enabled Product Catalog Agent - Stage 3 of Agent Oriented Architecture.

This module wraps the Product Catalog Agent from Stage 2 with A2A protocol
support, enabling it to be discovered and communicate with other agents.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from typing_extensions import override

# Import the original product agent
from stage2_product_agent.agent import ProductCatalogAgent

# Import A2A components
from a2a_protocol import BaseA2AAgent, create_and_run_agent_server

# Don't load .env in Docker - environment variables are passed by docker-compose
# load_dotenv()  # Commented out for Docker deployment

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductAgentA2A(BaseA2AAgent):
    """A2A-enabled Product Catalog Agent."""
    
    def __init__(self):
        """Initialize the A2A Product Agent."""
        # Initialize the underlying SMOL agent
        self.product_agent = ProductCatalogAgent()
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "product_agent.json"
        
        # Initialize base A2A agent
        super().__init__(
            agent_name="Product Catalog Agent",
            agent_description="Intelligent product search, analysis, and recommendations",
            agent_card_path=str(agent_card_path),
            smol_agent=self.product_agent
        )
        
        # Setup custom capabilities
        self.setup_custom_capabilities()
        
        logger.info("Initialized A2A Product Agent")
    
    @override
    def setup_custom_capabilities(self):
        """Setup product-specific capabilities."""
        # Register specific handlers for structured capabilities
        self.register_capability("search_products", self._handle_search_products)
        self.register_capability("analyze_prices", self._handle_analyze_prices)
        self.register_capability("find_similar_products", self._handle_find_similar)
        self.register_capability("generate_recommendations", self._handle_recommendations)
    
    async def _handle_search_products(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle structured product search requests."""
        query = args.get("query", "")
        filters = args.get("filters", {})
        
        # Build natural language query for SMOL agent
        nl_query = f"Search for {query}"
        
        if filters:
            if "category" in filters:
                nl_query += f" in category {filters['category']}"
            if "min_price" in filters and "max_price" in filters:
                nl_query += f" priced between ${filters['min_price']} and ${filters['max_price']}"
            elif "max_price" in filters:
                nl_query += f" under ${filters['max_price']}"
            if filters.get("in_stock"):
                nl_query += " that are in stock"
        
        # Execute via SMOL agent
        result = await self._execute_with_smol_agent(nl_query)
        
        # Try to parse structured response
        try:
            # If result contains JSON, extract it
            if "{" in result and "}" in result:
                start = result.find("{")
                end = result.rfind("}") + 1
                json_str = result[start:end]
                return json.loads(json_str)
            else:
                return {
                    "products": [],
                    "count": 0,
                    "raw_response": result
                }
        except:
            return {
                "products": [],
                "count": 0,
                "raw_response": result
            }
    
    async def _handle_analyze_prices(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price analysis requests."""
        category = args.get("category", "all products")
        
        query = f"Analyze price trends for {category}"
        result = await self._execute_with_smol_agent(query)
        
        # Return structured or raw response
        try:
            if "{" in result and "}" in result:
                start = result.find("{")
                end = result.rfind("}") + 1
                return json.loads(result[start:end])
        except:
            pass
        
        return {"analysis": result}
    
    async def _handle_find_similar(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle similar product requests."""
        product_id = args.get("product_id")
        limit = args.get("limit", 5)
        
        if not product_id:
            return {"error": "product_id is required"}
        
        query = f"Find {limit} products similar to product ID {product_id}"
        result = await self._execute_with_smol_agent(query)
        
        return {"similar_products": result}
    
    async def _handle_recommendations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle recommendation requests."""
        preferences = args.get("preferences", {})
        budget = args.get("budget")
        
        query = "Generate product recommendations"
        if preferences:
            query += f" based on preferences: {json.dumps(preferences)}"
        if budget:
            query += f" with budget of ${budget}"
        
        result = await self._execute_with_smol_agent(query)
        return {"recommendations": result}
    
    @override
    async def _handle_text_query(self, query: str) -> str:
        """Handle text queries using the SMOL agent."""
        # This is handled by parent class via _execute_with_smol_agent
        return await self._execute_with_smol_agent(query)


def main():
    """Run the A2A Product Agent server."""
    print(f"\n{'='*60}")
    print("A2A Product Catalog Agent - Stage 3")
    print(f"{'='*60}\n")
    
    try:
        # Create the A2A agent
        agent = ProductAgentA2A()
        
        # Get configuration
        port = int(os.getenv("PRODUCT_AGENT_PORT", "8001"))
        host = os.getenv("A2A_HOST", "0.0.0.0")
        
        print(f"✅ Agent initialized successfully!")
        print(f"📍 Starting A2A server on {host}:{port}")
        print(f"📋 Agent card available at: http://{host}:{port}/.well-known/agent-card.json")
        print(f"🔧 Health check at: http://{host}:{port}/health")
        print("\nPress Ctrl+C to stop the server.\n")
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "product_agent.json"
        
        # Run the A2A server
        create_and_run_agent_server(
            agent_executor=agent,
            agent_card_path=str(agent_card_path),
            host=host,
            port=port,
            server_name="product-agent-a2a"
        )
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully... 👋")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()