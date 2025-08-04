"""Base Sales Analytics Agent using SMOL framework."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from smolagents import CodeAgent, LiteLLMModel, MCPClient
from mcp import StdioServerParameters


class SalesAnalyticsAgent:
    """Base Sales Analytics Agent with MCP integration."""
    
    def __init__(self):
        """Initialize the Sales Agent with MCP tools."""
        # Get model configuration
        model_name = os.getenv("LLM_MODEL", "claude-3-5-haiku-20241022")
        
        # Initialize the LLM model
        self.model = LiteLLMModel(model_id=model_name)
        
        # Add MCP clients for sales and inventory data
        sales_mcp_path = os.getenv("SALES_MCP_PATH", "/app/stage3_multi_agent/sales_mcp/server.py")
        inventory_mcp_path = os.getenv("INVENTORY_MCP_PATH", "/app/stage3_multi_agent/inventory_mcp/server.py")
        
        # Initialize MCP tools
        mcp_tools = []
        
        if os.path.exists(sales_mcp_path):
            sales_client = MCPClient(
                StdioServerParameters(
                    command="python",
                    args=[sales_mcp_path],
                    env={"PYTHONPATH": str(Path(__file__).parent.parent.parent)}
                )
            )
            mcp_tools.extend(sales_client.get_tools())
        
        if os.path.exists(inventory_mcp_path):
            inventory_client = MCPClient(
                StdioServerParameters(
                    command="python",
                    args=[inventory_mcp_path],
                    env={"PYTHONPATH": str(Path(__file__).parent.parent.parent)}
                )
            )
            mcp_tools.extend(inventory_client.get_tools())
        
        # Initialize the CodeAgent with tools and model
        self.agent = CodeAgent(
            tools=mcp_tools,
            model=self.model
        )
    
    async def run(self, task: str) -> str:
        """Run a task with the agent."""
        # Run the synchronous agent.run() in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.agent.run, task)