"""A2A-enabled Sales Analytics Agent - Stage 3 of Agent Oriented Architecture.

This module wraps the Sales Agent with A2A protocol support,
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


class SalesAnalyticsAgent:
    """Simple SMOL agent for sales analytics."""
    
    def __init__(self, inventory_mcp_path: Optional[str] = None):
        """Initialize the Sales Analytics Agent."""
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
        
        # Initialize MCP client for sales
        mcp_server_path = os.getenv(
            "SALES_MCP_PATH",
            "stage3_multi_agent/sales_mcp/server.py"
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


class SalesAgentA2A(BaseA2AAgent):
    """A2A-enabled Sales Analytics Agent."""
    
    def __init__(self):
        """Initialize the A2A Sales Agent."""
        # Initialize the underlying SMOL agent with cross-domain access
        self.sales_agent = SalesAnalyticsAgent(
            inventory_mcp_path="stage3_multi_agent/inventory_mcp/server.py"
        )
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "sales_agent.json"
        
        # Initialize base A2A agent
        super().__init__(
            agent_name="Sales Analytics Agent",
            agent_description="Intelligent sales analytics with predictive insights",
            agent_card_path=str(agent_card_path),
            smol_agent=self.sales_agent
        )
        
        # Setup custom capabilities
        self.setup_custom_capabilities()
        
        logger.info("Initialized A2A Sales Agent")
    
    @override
    def setup_custom_capabilities(self):
        """Setup sales-specific capabilities."""
        # Register specific handlers for structured capabilities
        self.register_capability("sales_summary", self._handle_sales_summary)
        self.register_capability("analyze_returns", self._handle_analyze_returns)
        self.register_capability("customer_insights", self._handle_customer_insights)
        self.register_capability("sales_forecast", self._handle_sales_forecast)
        self.register_capability("trending_products", self._handle_trending_products)
        self.register_capability("revenue_analysis", self._handle_revenue_analysis)
    
    async def _handle_sales_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sales summary requests."""
        period = args.get("period", "month")
        
        query = f"Get sales summary for the {period}"
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
            "total_revenue": 0,
            "transaction_count": 0,
            "raw_response": result
        }
    
    async def _handle_analyze_returns(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle return analysis requests."""
        product_id = args.get("product_id")
        days = args.get("days", 30)
        
        query = f"Analyze returns for the last {days} days"
        if product_id:
            query += f" for product ID {product_id}"
        
        result = await self._execute_with_smol_agent(query)
        
        # Try to parse structured response
        try:
            if "{" in result and "}" in result:
                start = result.find("{")
                end = result.rfind("}") + 1
                return json.loads(result[start:end])
        except:
            return {"analysis": result}
    
    async def _handle_customer_insights(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer insights requests."""
        segment = args.get("segment")
        
        query = "Get customer behavior insights"
        if segment:
            query += f" for {segment} segment"
        
        result = await self._execute_with_smol_agent(query)
        return {"insights": result}
    
    async def _handle_sales_forecast(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sales forecast requests."""
        days_ahead = args.get("days_ahead", 30)
        product_id = args.get("product_id")
        
        query = f"Forecast sales for the next {days_ahead} days"
        if product_id:
            query += f" for product ID {product_id}"
        
        result = await self._execute_with_smol_agent(query)
        return {"forecast": result}
    
    async def _handle_trending_products(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trending products requests."""
        days = args.get("days", 7)
        limit = args.get("limit", 10)
        
        query = f"Show top {limit} trending products from the last {days} days"
        result = await self._execute_with_smol_agent(query)
        
        # Try to parse structured response
        try:
            if "{" in result and "}" in result:
                start = result.find("{")
                end = result.rfind("}") + 1
                return json.loads(result[start:end])
        except:
            return {"trending_products": result}
    
    async def _handle_revenue_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle revenue analysis requests."""
        group_by = args.get("group_by", "category")
        
        query = f"Analyze revenue grouped by {group_by}"
        result = await self._execute_with_smol_agent(query)
        
        return {"revenue_analysis": result}
    
    @override
    async def _handle_text_query(self, query: str) -> str:
        """Handle text queries using the SMOL agent."""
        return await self._execute_with_smol_agent(query)


def main():
    """Run the A2A Sales Agent server."""
    print(f"\n{'='*60}")
    print("A2A Sales Analytics Agent - Stage 3")
    print(f"{'='*60}\n")
    
    try:
        # Create the A2A agent
        agent = SalesAgentA2A()
        
        # Get configuration
        port = int(os.getenv("SALES_AGENT_PORT", "8003"))
        host = os.getenv("A2A_HOST", "0.0.0.0")
        
        print(f"✅ Agent initialized successfully!")
        print(f"📍 Starting A2A server on {host}:{port}")
        print(f"📋 Agent card available at: http://{host}:{port}/.well-known/agent-card.json")
        print(f"🔧 Health check at: http://{host}:{port}/health")
        print("\nCapabilities:")
        print("- Sales performance analytics")
        print("- Return pattern analysis")
        print("- Customer behavior insights")
        print("- Sales forecasting")
        print("- Trending product identification")
        print("- Cross-domain inventory integration")
        print("\nPress Ctrl+C to stop the server.\n")
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "sales_agent.json"
        
        # Run the A2A server
        create_and_run_agent_server(
            agent_executor=agent,
            agent_card_path=str(agent_card_path),
            host=host,
            port=port,
            server_name="sales-agent-a2a"
        )
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully... 👋")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()