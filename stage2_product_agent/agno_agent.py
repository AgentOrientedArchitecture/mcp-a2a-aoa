"""Product Catalog Agent - Stage 2 with Agno Framework.

This agent provides intelligent interaction with the product catalog,
using Agno agents to add business intelligence and reasoning capabilities
on top of the MCP server.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Add parent directory to path to import from stage1
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables only if not in Docker
if not os.getenv("DOCKER_CONTAINER", False):
    load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductCatalogAgnoAgent:
    """Intelligent agent for product catalog queries and recommendations using Agno framework."""

    def __init__(self):
        """Initialize the Product Catalog Agent with Agno framework."""
        # Load configuration
        self.agent_name = os.getenv("AGENT_NAME", "ProductCatalogAssistant")
        self.agent_description = os.getenv(
            "AGENT_DESCRIPTION",
            "An intelligent assistant for product catalog queries and recommendations"
        )
        
        # Agno-specific configuration
        self.reasoning = os.getenv("AGNO_REASONING", "true").lower() == "true"
        self.show_full_reasoning = os.getenv("AGNO_SHOW_FULL_REASONING", "true").lower() == "true"
        self.markdown = os.getenv("AGNO_MARKDOWN", "true").lower() == "true"
        self.debug_mode = os.getenv("AGNO_DEBUG_MODE", "false").lower() == "true"
        
        # Initialize LLM
        model_id = os.getenv("LLM_MODEL", "claude-3-7-sonnet-20250219")
        
        # Determine which API key to use based on the model
        if model_id.startswith("gpt") or model_id.startswith("o1"):
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    f"OpenAI model '{model_id}' specified but OPENAI_API_KEY not found in .env"
                )
            # Import OpenAI model for Agno
            from agno.models.openai import OpenAIChat
            self.model = OpenAIChat(id=model_id)
        else:
            # Default to Anthropic for claude models
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    f"Anthropic model '{model_id}' specified but ANTHROPIC_API_KEY not found in .env"
                )
            # Import Claude model for Agno
            from agno.models.anthropic import Claude
            self.model = Claude(id=model_id)
        
        logger.info(f"Initialized Agno LLM: {model_id}")
        
        # Initialize MCP client
        self._initialize_mcp_client()
        
        # Initialize the Agno agent
        self._initialize_agent()

    def _initialize_mcp_client(self):
        """Initialize MCP client for tool access."""
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
        
        # Store MCP server path for tool creation
        self.mcp_server_path = mcp_server_path
        logger.info(f"Configured MCP server at {mcp_server_path}")

    def _initialize_agent(self):
        """Initialize the Agno agent with tools and configuration."""
        from agno.agent import Agent
        from agno.tools.reasoning import ReasoningTools
        from agno.tools.mcp import MCPTools
        from mcp import StdioServerParameters
        import asyncio
        
        # Set up MCP server parameters for Agno's MCPTools
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(self.mcp_server_path)],
            env={**os.environ}
        )
        
        # Create MCP tools using Agno's built-in MCPTools
        self.mcp_tools = MCPTools(server_params=server_params)
        
        # Connect to MCP tools before initializing agent
        try:
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Connect to MCP tools
            loop.run_until_complete(self.mcp_tools.connect())
            logger.info("Connected to MCP server")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            # Continue without MCP tools if connection fails
            self.mcp_tools = None
        
        # Initialize Agno agent with MCP tools and reasoning
        tools = [ReasoningTools(add_instructions=True)]
        if self.mcp_tools:
            tools.append(self.mcp_tools)
        
        self.agent = Agent(
            name=self.agent_name,
            model=self.model,
            reasoning=self.reasoning,
            tools=tools,
            show_tool_calls=True,
            markdown=self.markdown,
            debug_mode=self.debug_mode,
            instructions=[
                "You are an intelligent product catalog assistant.",
                "You have access to MCP tools that connect to a product database.",
                "ALWAYS use the MCP tools to search and analyze product data.",
                "NEVER make up product information - only use real data from the database.",
                "Available MCP tools: search_products, query_products, get_schema, get_categories, get_price_range, get_product_by_id",
                "Use search_products for natural language queries about products.",
                "Use query_products for SQL queries when needed.",
                "Provide detailed reasoning for your recommendations.",
                "Use tables to display data when appropriate.",
                "Always explain your thought process when making recommendations."
            ]
        )
        
        logger.info(f"Initialized Agno agent '{self.agent_name}' with {len(tools)} tools")

    async def _ensure_mcp_connected(self):
        """Ensure MCP tools are connected."""
        if self.mcp_tools and (not hasattr(self.mcp_tools, '_connected') or not self.mcp_tools._connected):
            await self.mcp_tools.connect()
            logger.info("Connected to MCP server")

    def query(self, user_input: str) -> str:
        """Process a user query using the Agno agent."""
        try:
            logger.info(f"Processing query: {user_input}")
            
            # Use Agno agent's async method for MCP tools
            import asyncio
            
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Use async method
            response = loop.run_until_complete(
                self.agent.arun(user_input)
            )
            
            # Extract content from RunResponse
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'message'):
                return response.message
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing your request: {str(e)}"

    async def aquery(self, user_input: str) -> str:
        """Async version of query for better MCP integration."""
        try:
            logger.info(f"Processing async query: {user_input}")
            
            # Ensure MCP tools are connected
            await self._ensure_mcp_connected()
            
            # Use Agno agent to process the query
            response = await self.agent.arun(user_input)
            
            # Extract content from RunResponse
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'message'):
                return response.message
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Error processing async query: {e}")
            return f"Error processing your request: {str(e)}"

    def get_customer_insights(self, customer_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate customer insights using Agno's reasoning capabilities."""
        try:
            # Format customer history for analysis
            history_text = self._format_customer_history(customer_history)
            
            query = f"""
            Analyze this customer purchase history and provide insights:
            
            {history_text}
            
            Please provide:
            1. Purchase patterns and preferences
            2. Price sensitivity analysis
            3. Product category preferences
            4. Recommendations for future purchases
            5. Customer lifetime value estimate
            """
            
            response = self.agent.print_response(
                query,
                stream=True,
                show_full_reasoning=self.show_full_reasoning
            )
            
            return {
                "insights": response,
                "customer_history": customer_history
            }
            
        except Exception as e:
            logger.error(f"Error generating customer insights: {e}")
            return {"error": str(e)}

    def _format_customer_history(self, history: List[Dict[str, Any]]) -> str:
        """Format customer history for analysis."""
        formatted = []
        for purchase in history:
            formatted.append(
                f"- {purchase.get('product_name', 'Unknown')} "
                f"(${purchase.get('price', 0):.2f}) "
                f"on {purchase.get('date', 'Unknown')}"
            )
        return "\n".join(formatted)

    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("=" * 60)
        print("Product Catalog Agent - Stage 2 (Agno Framework)")
        print("Intelligent Assistant with Reasoning Capabilities")
        print("=" * 60)
        print()
        print(f"✅ Agent '{self.agent_name}' initialized successfully!")
        print()
        print("Available capabilities:")
        print("- Natural language product search with reasoning")
        print("- Price trend analysis with detailed explanations")
        print("- Similar product recommendations")
        print("- Personalized recommendations with reasoning")
        print("- Customer insights and analysis")
        print("- Database queries with explanation")
        print()
        print("Type 'quit' to exit.")
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("\nAgent: ", end="", flush=True)
                response = self.query(user_input)
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_mcp_connected()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self.mcp_tools, 'close'):
            await self.mcp_tools.close()


def main():
    """Main entry point for the Agno agent."""
    try:
        agent = ProductCatalogAgnoAgent()
        agent.run_interactive()
    except Exception as e:
        logger.error(f"Failed to start Agno agent: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 