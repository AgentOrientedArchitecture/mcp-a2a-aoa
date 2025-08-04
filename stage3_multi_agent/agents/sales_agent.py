"""Enhanced Sales Analytics Agent with A2A Protocol and Telemetry.

This module implements an enhanced sales analytics agent with comprehensive
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

# Import the base sales agent
from agents.sales_agent_base import SalesAnalyticsAgent

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


class EnhancedSalesAgentA2A(EnhancedBaseA2AAgent):
    """Enhanced A2A-enabled Sales Analytics Agent with telemetry."""
    
    def __init__(self):
        """Initialize the Enhanced A2A Sales Agent."""
        # Initialize the underlying SMOL agent with MCP integration
        self.sales_agent = SalesAnalyticsAgent()
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "sales_agent.json"
        
        # Get telemetry configuration
        enable_telemetry = os.getenv("ENABLE_TELEMETRY", "true").lower() == "true"
        phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
        
        # Initialize enhanced base A2A agent
        super().__init__(
            agent_name="Sales Analytics Agent",
            agent_description="Intelligent sales analysis, revenue tracking, and performance monitoring with telemetry",
            agent_card_path=str(agent_card_path),
            smol_agent=self.sales_agent,
            enable_telemetry=enable_telemetry,
            phoenix_endpoint=phoenix_endpoint
        )
        
        # Setup custom capabilities
        self.setup_custom_capabilities()
        
        # Start performance monitoring if telemetry is enabled
        if self.enable_telemetry:
            self.start_performance_monitoring()
        
        logger.info("Initialized Enhanced A2A Sales Agent")
    
    @override
    def setup_custom_capabilities(self):
        """Setup custom sales analytics capabilities."""
        self.register_capability("sales_analysis", self._handle_sales_analysis)
        self.register_capability("revenue_tracking", self._handle_revenue_tracking)
        self.register_capability("performance_metrics", self._handle_performance_metrics)
        self.register_capability("customer_insights", self._handle_customer_insights)
        self.register_capability("trend_analysis", self._handle_trend_analysis)
        self.register_capability("forecasting", self._handle_forecasting)
        
        logger.info("Registered custom sales analytics capabilities")
    
    async def _handle_sales_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sales analysis with telemetry."""
        period = args.get("period", "monthly")
        category = args.get("category", "")
        analysis_type = args.get("analysis_type", "overview")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_sales_analysis(
                period, 0.0, 0
            ) as span:
                try:
                    # Build analysis query
                    analysis_query = f"Perform {analysis_type} sales analysis for {period}"
                    if category:
                        analysis_query += f" in category '{category}'"
                    
                    # Execute analysis using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(analysis_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("analysis.duration_ms", duration * 1000)
                    span.set_attribute("analysis.type", analysis_type)
                    span.set_attribute("analysis.period", period)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"analysis": result, "period": period, "category": category}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            analysis_query = f"Perform {analysis_type} sales analysis for {period}"
            if category:
                analysis_query += f" in category '{category}'"
            
            result = await self._execute_with_smol_agent(analysis_query)
            return {"analysis": result, "period": period, "category": category}
    
    async def _handle_revenue_tracking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle revenue tracking with telemetry."""
        period = args.get("period", "monthly")
        granularity = args.get("granularity", "daily")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_revenue_tracking(
                period, 0.0
            ) as span:
                try:
                    # Build tracking query
                    tracking_query = f"Track revenue for {period} with {granularity} granularity"
                    
                    # Execute tracking using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(tracking_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("tracking.duration_ms", duration * 1000)
                    span.set_attribute("tracking.period", period)
                    span.set_attribute("tracking.granularity", granularity)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"revenue_tracking": result, "period": period, "granularity": granularity}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            tracking_query = f"Track revenue for {period} with {granularity} granularity"
            result = await self._execute_with_smol_agent(tracking_query)
            return {"revenue_tracking": result, "period": period, "granularity": granularity}
    
    async def _handle_performance_metrics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle performance metrics with telemetry."""
        metric_type = args.get("metric_type", "kpi")
        period = args.get("period", "monthly")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_performance_metrics(
                metric_type, period
            ) as span:
                try:
                    # Build metrics query
                    metrics_query = f"Get {metric_type} performance metrics for {period}"
                    
                    # Execute metrics using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(metrics_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("metrics.duration_ms", duration * 1000)
                    span.set_attribute("metrics.type", metric_type)
                    span.set_attribute("metrics.period", period)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"performance_metrics": result, "metric_type": metric_type, "period": period}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            metrics_query = f"Get {metric_type} performance metrics for {period}"
            result = await self._execute_with_smol_agent(metrics_query)
            return {"performance_metrics": result, "metric_type": metric_type, "period": period}
    
    async def _handle_customer_insights(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer insights with telemetry."""
        customer_id = args.get("customer_id", "")
        insight_type = args.get("insight_type", "behavior")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_customer_insights(
                customer_id, insight_type
            ) as span:
                try:
                    # Build insights query
                    insights_query = f"Get {insight_type} insights"
                    if customer_id:
                        insights_query += f" for customer {customer_id}"
                    
                    # Execute insights using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(insights_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("insights.duration_ms", duration * 1000)
                    span.set_attribute("insights.type", insight_type)
                    span.set_attribute("insights.customer_id", customer_id)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"customer_insights": result, "customer_id": customer_id, "insight_type": insight_type}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            insights_query = f"Get {insight_type} insights"
            if customer_id:
                insights_query += f" for customer {customer_id}"
            
            result = await self._execute_with_smol_agent(insights_query)
            return {"customer_insights": result, "customer_id": customer_id, "insight_type": insight_type}
    
    async def _handle_trend_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trend analysis with telemetry."""
        trend_type = args.get("trend_type", "sales")
        time_period = args.get("time_period", "monthly")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_trend_analysis(
                trend_type, time_period
            ) as span:
                try:
                    # Build trend query
                    trend_query = f"Analyze {trend_type} trends for {time_period}"
                    
                    # Execute trend analysis using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(trend_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("trend.duration_ms", duration * 1000)
                    span.set_attribute("trend.type", trend_type)
                    span.set_attribute("trend.time_period", time_period)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"trend_analysis": result, "trend_type": trend_type, "time_period": time_period}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            trend_query = f"Analyze {trend_type} trends for {time_period}"
            result = await self._execute_with_smol_agent(trend_query)
            return {"trend_analysis": result, "trend_type": trend_type, "time_period": time_period}
    
    async def _handle_forecasting(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle forecasting with telemetry."""
        forecast_period = args.get("forecast_period", "30 days")
        algorithm = args.get("algorithm", "default")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_forecasting(
                forecast_period, algorithm
            ) as span:
                try:
                    # Build forecast query
                    forecast_query = f"Forecast sales for {forecast_period} using {algorithm} algorithm"
                    
                    # Execute forecasting using the actual SMOL agent
                    start_time = time.time()
                    result = await self._execute_with_smol_agent(forecast_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("forecast.duration_ms", duration * 1000)
                    span.set_attribute("forecast.period", forecast_period)
                    span.set_attribute("forecast.algorithm", algorithm)
                    span.set_attribute("result.length", len(str(result)))
                    
                    return {"forecasting": result, "forecast_period": forecast_period, "algorithm": algorithm}
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            forecast_query = f"Forecast sales for {forecast_period} using {algorithm} algorithm"
            result = await self._execute_with_smol_agent(forecast_query)
            return {"forecasting": result, "forecast_period": forecast_period, "algorithm": algorithm}
    
    @override
    async def _handle_text_query(self, query: str) -> str:
        """Handle text queries with telemetry."""
        if self.telemetry:
            with self.telemetry.get_business_metrics().create_span_with_context(
                "business.sales.text_query",
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
    """Main entry point for the enhanced sales agent."""
    try:
        # Create enhanced agent
        agent = EnhancedSalesAgentA2A()
        
        # Get configuration
        host = os.getenv("A2A_HOST", "0.0.0.0")
        port = int(os.getenv("SALES_AGENT_PORT", "8003"))
        
        logger.info(f"Starting Enhanced Sales Agent on {host}:{port}")
        
        # Create and run agent server
        create_and_run_agent_server(
            agent_executor=agent,
            agent_card_path=str(agent.agent_card_path),
            host=host,
            port=port,
            server_name="Enhanced Sales Agent"
        )
        
    except KeyboardInterrupt:
        logger.info("Enhanced Sales Agent stopped by user")
    except Exception as e:
        logger.error(f"Enhanced Sales Agent error: {e}")
        raise


if __name__ == "__main__":
    main() 