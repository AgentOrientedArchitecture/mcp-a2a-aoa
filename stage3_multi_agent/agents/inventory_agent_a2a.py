"""A2A-enabled Inventory Management Agent - Stage 3 of Agent Oriented Architecture.

This module wraps the Inventory Agent with A2A protocol support,
enabling it to be discovered and communicate with other agents.
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
from mcp import StdioServerParameters
from smolagents import CodeAgent, LiteLLMModel, MCPClient

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


class InventoryAgent:
    """Simple SMOL agent for inventory management."""
    
    def __init__(self, sales_mcp_path: Optional[str] = None):
        """Initialize the Inventory Agent."""
        # Initialize LLM
        model_id = os.getenv("LLM_MODEL", "claude-3-5-haiku-20241022")
        
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
        
        # Initialize MCP client for inventory
        mcp_server_path = os.getenv(
            "INVENTORY_MCP_PATH",
            "stage3_multi_agent/inventory_mcp/server.py"
        )
        
        # If path is relative, resolve from project root
        if not Path(mcp_server_path).is_absolute():
            project_root = Path(__file__).parent.parent.parent.parent
            mcp_server_path = project_root / mcp_server_path
        else:
            mcp_server_path = Path(mcp_server_path)
        
        if not mcp_server_path.exists():
            raise FileNotFoundError(f"MCP server not found at {mcp_server_path}")
        
        # Set up MCP server parameters
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(mcp_server_path)],
            env={**os.environ}
        )
        
        # Initialize MCP client
        self.mcp_client = MCPClient(self.server_params)
        self.mcp_tools = self.mcp_client.get_tools()
        logger.info(f"Connected to MCP server with {len(self.mcp_tools)} tools")
        
        # Initialize agent
        self.agent = CodeAgent(
            tools=self.mcp_tools,
            model=self.model
        )
    
    async def run(self, task: str) -> str:
        """Run a task with the agent."""
        # Run the synchronous agent.run() in a thread pool
        return await asyncio.to_thread(self.agent.run, task)


class InventoryAgentA2A(BaseA2AAgent):
    """A2A-enabled Inventory Management Agent."""
    
    def __init__(self):
        """Initialize the A2A Inventory Agent."""
        # Initialize the underlying SMOL agent with cross-domain access
        self.inventory_agent = InventoryAgent(
            sales_mcp_path="stage3_multi_agent/sales_mcp/server.py"
        )
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "inventory_agent.json"
        
        # Initialize base A2A agent
        super().__init__(
            agent_name="Inventory Management Agent",
            agent_description="Intelligent inventory management with predictive analytics",
            agent_card_path=str(agent_card_path),
            smol_agent=self.inventory_agent
        )
        
        # Setup custom capabilities
        self.setup_custom_capabilities()
        
        logger.info("Initialized A2A Inventory Agent")
    
    @override
    def setup_custom_capabilities(self):
        """Setup inventory-specific capabilities."""
        # Register specific handlers for structured capabilities
        self.register_capability("check_stock", self._handle_check_stock)
        self.register_capability("optimize_restocking", self._handle_optimize_restocking)
        self.register_capability("predict_stockouts", self._handle_predict_stockouts)
        self.register_capability("warehouse_optimization", self._handle_warehouse_optimization)
        self.register_capability("inventory_health_check", self._handle_health_check)
    
    async def _handle_check_stock(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle structured stock check requests."""
        product_id = args.get("product_id")
        warehouse_id = args.get("warehouse_id")
        
        if not product_id:
            return {"error": "product_id is required"}
        
        # Build query
        query = f"Check stock for product ID {product_id}"
        if warehouse_id:
            query += f" in warehouse {warehouse_id}"
        
        # Execute via SMOL agent
        result = await self._execute_with_smol_agent(query)
        
        # Try to parse structured response
        try:
            if "{" in result and "}" in result:
                start = result.find("{")
                end = result.rfind("}") + 1
                json_str = result[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "stock_levels": [],
            "total_stock": 0,
            "raw_response": result
        }
    
    async def _handle_optimize_restocking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle restocking optimization requests."""
        warehouse_id = args.get("warehouse_id")
        urgency_threshold = args.get("urgency_threshold", 7)
        
        query = f"Optimize restocking with {urgency_threshold} day urgency threshold"
        if warehouse_id:
            query += f" for warehouse {warehouse_id}"
        
        result = await self._execute_with_smol_agent(query)
        
        # Try to parse structured response
        try:
            if "{" in result and "}" in result:
                start = result.find("{")
                end = result.rfind("}") + 1
                return json.loads(result[start:end])
        except:
            return {"optimization": result}
    
    async def _handle_predict_stockouts(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stockout prediction requests."""
        days_ahead = args.get("days_ahead", 14)
        
        query = f"Predict stockouts for the next {days_ahead} days"
        result = await self._execute_with_smol_agent(query)
        
        return {"predictions": result}
    
    async def _handle_warehouse_optimization(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle warehouse optimization requests."""
        target_utilization = args.get("target_utilization", 85)
        
        query = f"Optimize warehouse space with target utilization of {target_utilization}%"
        result = await self._execute_with_smol_agent(query)
        
        return {"optimization": result}
    
    async def _handle_health_check(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inventory health check requests."""
        query = "Perform comprehensive inventory health check"
        result = await self._execute_with_smol_agent(query)
        
        # Try to parse structured response
        try:
            if "{" in result and "}" in result:
                start = result.find("{")
                end = result.rfind("}") + 1
                return json.loads(result[start:end])
        except:
            return {"health_report": result}
    
    @override
    async def _handle_text_query(self, query: str) -> str:
        """Handle text queries using the SMOL agent."""
        return await self._execute_with_smol_agent(query)


def main():
    """Run the A2A Inventory Agent server."""
    print(f"\n{'='*60}")
    print("A2A Inventory Management Agent - Stage 3")
    print(f"{'='*60}\n")
    
    try:
        # Create the A2A agent
        agent = InventoryAgentA2A()
        
        # Get configuration
        port = int(os.getenv("INVENTORY_AGENT_PORT", "8002"))
        host = os.getenv("A2A_HOST", "0.0.0.0")
        
        print(f"✅ Agent initialized successfully!")
        print(f"📍 Starting A2A server on {host}:{port}")
        print(f"📋 Agent card available at: http://{host}:{port}/.well-known/agent-card.json")
        print(f"🔧 Health check at: http://{host}:{port}/health")
        print("\nCapabilities:")
        print("- Real-time stock monitoring")
        print("- Predictive stockout analysis")
        print("- Warehouse space optimization")
        print("- Intelligent reorder recommendations")
        print("- Cross-domain sales integration")
        print("\nPress Ctrl+C to stop the server.\n")
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "inventory_agent.json"
        
        # Run the A2A server
        create_and_run_agent_server(
            agent_executor=agent,
            agent_card_path=str(agent_card_path),
            host=host,
            port=port,
            server_name="inventory-agent-a2a"
        )
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully... 👋")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()