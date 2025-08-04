"""Enhanced Inventory Management Agent with A2A Protocol and Telemetry.

This module implements an enhanced inventory management agent with comprehensive
telemetry integration for observability and monitoring.
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from typing_extensions import override
from mcp import StdioServerParameters
from smolagents import CodeAgent, LiteLLMModel, MCPClient

# Import the base inventory agent
from agents.inventory_agent_base import InventoryAgent

# Import enhanced base agent
from a2a_protocol.base_agent import EnhancedBaseA2AAgent
from a2a_protocol import create_and_run_agent_server

# Don't load .env in Docker - environment variables are passed by docker-compose
# load_dotenv()  # Commented out for Docker deployment

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedInventoryAgentA2A(EnhancedBaseA2AAgent):
    """Enhanced A2A-enabled Inventory Management Agent with telemetry."""
    
    def __init__(self):
        """Initialize the Enhanced A2A Inventory Agent."""
        # Initialize the underlying SMOL agent with MCP integration
        self.inventory_agent = InventoryAgent()
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "inventory_agent.json"
        
        # Get telemetry configuration
        enable_telemetry = os.getenv("ENABLE_TELEMETRY", "true").lower() == "true"
        phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
        
        # Initialize enhanced base A2A agent
        super().__init__(
            agent_name="Inventory Management Agent",
            agent_description="Intelligent inventory tracking, stock management, and supply chain monitoring with telemetry",
            agent_card_path=str(agent_card_path),
            smol_agent=self.inventory_agent,
            enable_telemetry=enable_telemetry,
            phoenix_endpoint=phoenix_endpoint
        )
        
        # Setup custom capabilities
        self.setup_custom_capabilities()
        
        # Start performance monitoring if telemetry is enabled
        if self.enable_telemetry:
            self.start_performance_monitoring()
        
        logger.info("Initialized Enhanced A2A Inventory Agent")
    
    @override
    def setup_custom_capabilities(self):
        """Setup custom inventory management capabilities."""
        self.register_capability("check_stock", self._handle_check_stock)
        self.register_capability("update_inventory", self._handle_update_inventory)
        self.register_capability("low_stock_alert", self._handle_low_stock_alert)
        self.register_capability("inventory_analysis", self._handle_inventory_analysis)
        self.register_capability("supply_chain_status", self._handle_supply_chain_status)
        self.register_capability("reorder_recommendations", self._handle_reorder_recommendations)
        
        logger.info("Registered custom inventory management capabilities")
    
    async def _handle_check_stock(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stock checking with telemetry."""
        product_id = args.get("product_id", "")
        product_name = args.get("product_name", "")
        threshold = args.get("threshold", 10)
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_inventory_check(
                product_id, threshold
            ) as span:
                try:
                    # Build check query
                    check_query = f"Check stock level for product {product_id}"
                    if product_name:
                        check_query += f" ({product_name})"
                    check_query += f" with threshold {threshold}"
                    
                    # Execute check using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(check_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("check.duration_ms", duration * 1000)
                    span.set_attribute("check.product_id", product_id)
                    span.set_attribute("check.threshold", threshold)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"stock_check": result, "product_id": product_id, "threshold": threshold}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            check_query = f"Check stock level for product {product_id}"
            if product_name:
                check_query += f" ({product_name})"
            check_query += f" with threshold {threshold}"
            
            result = await self._execute_with_smol_agent(check_query)
            return {"stock_check": result, "product_id": product_id, "threshold": threshold}
    
    async def _handle_update_inventory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inventory updates with telemetry."""
        product_id = args.get("product_id", "")
        quantity = args.get("quantity", 0)
        operation = args.get("operation", "add")  # add, remove, set
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_inventory_update(
                product_id, quantity, operation
            ) as span:
                try:
                    # Build update query
                    update_query = f"{operation.capitalize()} {quantity} units for product {product_id}"
                    
                    # Execute update using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(update_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("update.duration_ms", duration * 1000)
                    span.set_attribute("update.product_id", product_id)
                    span.set_attribute("update.quantity", quantity)
                    span.set_attribute("update.operation", operation)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"inventory_update": result, "product_id": product_id, "quantity": quantity, "operation": operation}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            update_query = f"{operation.capitalize()} {quantity} units for product {product_id}"
            result = await self._execute_with_smol_agent(update_query)
            return {"inventory_update": result, "product_id": product_id, "quantity": quantity, "operation": operation}
    
    async def _handle_low_stock_alert(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle low stock alerts with telemetry."""
        threshold = args.get("threshold", 10)
        category = args.get("category", "")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_low_stock_alert(
                threshold, category
            ) as span:
                try:
                    # Build alert query
                    alert_query = f"Check for low stock items with threshold {threshold}"
                    if category:
                        alert_query += f" in category '{category}'"
                    
                    # Execute alert check using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(alert_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("alert.duration_ms", duration * 1000)
                    span.set_attribute("alert.threshold", threshold)
                    span.set_attribute("alert.category", category)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"low_stock_alert": result, "threshold": threshold, "category": category}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            alert_query = f"Check for low stock items with threshold {threshold}"
            if category:
                alert_query += f" in category '{category}'"
            
            result = await self._execute_with_smol_agent(alert_query)
            return {"low_stock_alert": result, "threshold": threshold, "category": category}
    
    async def _handle_inventory_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inventory analysis with telemetry."""
        analysis_type = args.get("analysis_type", "overview")
        category = args.get("category", "")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_inventory_analysis(
                analysis_type, category
            ) as span:
                try:
                    # Build analysis query
                    analysis_query = f"Perform {analysis_type} inventory analysis"
                    if category:
                        analysis_query += f" for category '{category}'"
                    
                    # Execute analysis using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(analysis_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("analysis.duration_ms", duration * 1000)
                    span.set_attribute("analysis.type", analysis_type)
                    span.set_attribute("analysis.category", category)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"inventory_analysis": result, "analysis_type": analysis_type, "category": category}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            analysis_query = f"Perform {analysis_type} inventory analysis"
            if category:
                analysis_query += f" for category '{category}'"
            
            result = await self._execute_with_smol_agent(analysis_query)
            return {"inventory_analysis": result, "analysis_type": analysis_type, "category": category}
    
    async def _handle_supply_chain_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle supply chain status with telemetry."""
        location = args.get("location", "all")
        status_type = args.get("status_type", "overview")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_supply_chain_status(
                location, status_type
            ) as span:
                try:
                    # Build status query
                    status_query = f"Check {status_type} supply chain status"
                    if location != "all":
                        status_query += f" for location '{location}'"
                    
                    # Execute status check using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(status_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("status.duration_ms", duration * 1000)
                    span.set_attribute("status.location", location)
                    span.set_attribute("status.type", status_type)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"supply_chain_status": result, "location": location, "status_type": status_type}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            status_query = f"Check {status_type} supply chain status"
            if location != "all":
                status_query += f" for location '{location}'"
            
            result = await self._execute_with_smol_agent(status_query)
            return {"supply_chain_status": result, "location": location, "status_type": status_type}
    
    async def _handle_reorder_recommendations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reorder recommendations with telemetry."""
        algorithm = args.get("algorithm", "default")
        time_horizon = args.get("time_horizon", "30 days")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_reorder_recommendations(
                algorithm, time_horizon
            ) as span:
                try:
                    # Build recommendations query
                    recommendations_query = f"Generate reorder recommendations using {algorithm} algorithm for {time_horizon}"
                    
                    # Execute recommendations using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(recommendations_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("recommendations.duration_ms", duration * 1000)
                    span.set_attribute("recommendations.algorithm", algorithm)
                    span.set_attribute("recommendations.time_horizon", time_horizon)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"reorder_recommendations": result, "algorithm": algorithm, "time_horizon": time_horizon}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            recommendations_query = f"Generate reorder recommendations using {algorithm} algorithm for {time_horizon}"
            result = await self._execute_with_smol_agent(recommendations_query)
            return {"reorder_recommendations": result, "algorithm": algorithm, "time_horizon": time_horizon}
    
    @override
    async def _handle_text_query(self, query: str) -> str:
        """Handle text queries with telemetry."""
        if self.telemetry:
            with self.telemetry.get_business_metrics().create_span_with_context(
                "business.inventory.text_query",
                query_text=query
            ) as span:
                try:
                    # Execute query using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("query.duration_ms", duration * 1000)
                    span.set_attribute("query.length", len(query))
                    span.set_attribute("result.length", len(str(result)))
                    
                    return result
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            return await self._execute_with_smol_agent(query)


def main():
    """Main entry point for the enhanced inventory agent."""
    try:
        # Create enhanced agent
        agent = EnhancedInventoryAgentA2A()
        
        # Get configuration
        host = os.getenv("A2A_HOST", "0.0.0.0")
        port = int(os.getenv("INVENTORY_AGENT_PORT", "8002"))
        
        logger.info(f"Starting Enhanced Inventory Agent on {host}:{port}")
        
        # Create and run agent server
        create_and_run_agent_server(
            agent_executor=agent,
            agent_card_path=str(agent.agent_card_path),
            host=host,
            port=port,
            server_name="Enhanced Inventory Agent"
        )
        
    except KeyboardInterrupt:
        logger.info("Enhanced Inventory Agent stopped by user")
    except Exception as e:
        logger.error(f"Enhanced Inventory Agent error: {e}")
        raise


if __name__ == "__main__":
    main() 