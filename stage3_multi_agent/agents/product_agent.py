"""Enhanced Product Catalog Agent with A2A Protocol and Telemetry.

This module implements an enhanced product catalog agent with comprehensive
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

# Import the original product agent
from stage2_product_agent.agent import ProductCatalogAgent

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


class EnhancedProductAgentA2A(EnhancedBaseA2AAgent):
    """Enhanced A2A-enabled Product Catalog Agent with telemetry."""
    
    def __init__(self):
        """Initialize the Enhanced A2A Product Agent."""
        # Initialize the underlying SMOL agent
        self.product_agent = ProductCatalogAgent()
        
        # Get agent card path
        agent_card_path = Path(__file__).parent.parent / "agent_cards" / "product_agent.json"
        
        # Get telemetry configuration
        enable_telemetry = os.getenv("ENABLE_TELEMETRY", "true").lower() == "true"
        phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
        
        # Initialize enhanced base A2A agent
        super().__init__(
            agent_name="Product Catalog Agent",
            agent_description="Intelligent product search, analysis, and recommendations with telemetry",
            agent_card_path=str(agent_card_path),
            smol_agent=self.product_agent,
            enable_telemetry=enable_telemetry,
            phoenix_endpoint=phoenix_endpoint
        )
        
        # Setup custom capabilities
        self.setup_custom_capabilities()
        
        # Start performance monitoring if telemetry is enabled
        if self.enable_telemetry:
            self.start_performance_monitoring()
        
        logger.info("Initialized Enhanced A2A Product Agent")
    
    @override
    def setup_custom_capabilities(self):
        """Setup custom product catalog capabilities."""
        self.register_capability("search_products", self._handle_search_products)
        self.register_capability("analyze_prices", self._handle_analyze_prices)
        self.register_capability("find_similar", self._handle_find_similar)
        self.register_capability("recommendations", self._handle_recommendations)
        self.register_capability("get_product_info", self._handle_get_product_info)
        self.register_capability("analyze_category", self._handle_analyze_category)
        
        logger.info("Registered custom product catalog capabilities")
    
    async def _handle_search_products(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product search with telemetry."""
        query = args.get("query", "")
        category = args.get("category", "")
        price_range = args.get("price_range", "")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_product_search(
                query, 0, 0.0  # We'll update these after execution
            ) as span:
                try:
                    # Build search query
                    search_query = f"Search for products"
                    if query:
                        search_query += f" matching '{query}'"
                    if category:
                        search_query += f" in category '{category}'"
                    if price_range:
                        search_query += f" with price range '{price_range}'"
                    
                    # Execute search
                    start_time = time.time()
                    result = await asyncio.to_thread(self.product_agent.run, search_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("search.duration_ms", duration * 1000)
                    span.set_attribute("search.category", category)
                    span.set_attribute("search.price_range", price_range)
                    
                    return {
                        "query": search_query,
                        "result": result,
                        "duration_ms": duration * 1000
                    }
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            search_query = f"Search for products"
            if query:
                search_query += f" matching '{query}'"
            if category:
                search_query += f" in category '{category}'"
            if price_range:
                search_query += f" with price range '{price_range}'"
            
            result = await asyncio.to_thread(self.product_agent.run, search_query)
            return {
                "query": search_query,
                "result": result
            }
    
    async def _handle_analyze_prices(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price analysis with telemetry."""
        category = args.get("category", "")
        analysis_type = args.get("analysis_type", "trend")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_price_analysis(
                category, (0, 1000), analysis_type
            ) as span:
                try:
                    # Build analysis query
                    analysis_query = f"Analyze price {analysis_type} for products"
                    if category:
                        analysis_query += f" in category '{category}'"
                    
                    # Execute analysis
                    start_time = time.time()
                    result = await asyncio.to_thread(self.product_agent.run, analysis_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("analysis.duration_ms", duration * 1000)
                    span.set_attribute("analysis.type", analysis_type)
                    
                    return {
                        "query": analysis_query,
                        "result": result,
                        "duration_ms": duration * 1000
                    }
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            analysis_query = f"Analyze price {analysis_type} for products"
            if category:
                analysis_query += f" in category '{category}'"
            
            result = await asyncio.to_thread(self.product_agent.run, analysis_query)
            return {
                "query": analysis_query,
                "result": result
            }
    
    async def _handle_find_similar(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle similar product search with telemetry."""
        product_name = args.get("product_name", "")
        similarity_criteria = args.get("similarity_criteria", "category")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().create_span_with_context(
                "business.product.similar_search",
                product_name=product_name,
                similarity_criteria=similarity_criteria
            ) as span:
                try:
                    # Build similarity query
                    similarity_query = f"Find products similar to '{product_name}' based on {similarity_criteria}"
                    
                    # Execute search
                    start_time = time.time()
                    result = await asyncio.to_thread(self.product_agent.run, similarity_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("search.duration_ms", duration * 1000)
                    span.set_attribute("search.criteria", similarity_criteria)
                    
                    return {
                        "query": similarity_query,
                        "result": result,
                        "duration_ms": duration * 1000
                    }
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            similarity_query = f"Find products similar to '{product_name}' based on {similarity_criteria}"
            result = await asyncio.to_thread(self.product_agent.run, similarity_query)
            return {
                "query": similarity_query,
                "result": result
            }
    
    async def _handle_recommendations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product recommendations with telemetry."""
        user_id = args.get("user_id", "anonymous")
        recommendation_count = args.get("count", 5)
        algorithm = args.get("algorithm", "collaborative")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_recommendation_generation(
                user_id, recommendation_count, algorithm
            ) as span:
                try:
                    # Build recommendation query
                    recommendation_query = f"Generate {recommendation_count} product recommendations for user {user_id} using {algorithm} algorithm"
                    
                    # Execute recommendation
                    start_time = time.time()
                    result = await asyncio.to_thread(self.product_agent.run, recommendation_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("recommendation.duration_ms", duration * 1000)
                    span.set_attribute("recommendation.algorithm", algorithm)
                    
                    return {
                        "query": recommendation_query,
                        "result": result,
                        "duration_ms": duration * 1000
                    }
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            recommendation_query = f"Generate {recommendation_count} product recommendations for user {user_id} using {algorithm} algorithm"
            result = await asyncio.to_thread(self.product_agent.run, recommendation_query)
            return {
                "query": recommendation_query,
                "result": result
            }
    
    async def _handle_get_product_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product information retrieval with telemetry."""
        product_id = args.get("product_id", "")
        product_name = args.get("product_name", "")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().create_span_with_context(
                "business.product.info",
                product_id=product_id,
                product_name=product_name
            ) as span:
                try:
                    # Build info query
                    if product_id:
                        info_query = f"Get detailed information for product with ID {product_id}"
                    elif product_name:
                        info_query = f"Get detailed information for product '{product_name}'"
                    else:
                        return {"error": "Either product_id or product_name must be provided"}
                    
                    # Execute query
                    start_time = time.time()
                    result = await asyncio.to_thread(self.product_agent.run, info_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("info.duration_ms", duration * 1000)
                    
                    return {
                        "query": info_query,
                        "result": result,
                        "duration_ms": duration * 1000
                    }
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            if product_id:
                info_query = f"Get detailed information for product with ID {product_id}"
            elif product_name:
                info_query = f"Get detailed information for product '{product_name}'"
            else:
                return {"error": "Either product_id or product_name must be provided"}
            
            result = await asyncio.to_thread(self.product_agent.run, info_query)
            return {
                "query": info_query,
                "result": result
            }
    
    async def _handle_analyze_category(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle category analysis with telemetry."""
        category = args.get("category", "")
        analysis_type = args.get("analysis_type", "overview")
        
        if self.telemetry:
            with self.telemetry.get_business_metrics().create_span_with_context(
                "business.category.analysis",
                category=category,
                analysis_type=analysis_type
            ) as span:
                try:
                    # Build analysis query
                    analysis_query = f"Provide {analysis_type} analysis for category '{category}'"
                    
                    # Execute analysis
                    start_time = time.time()
                    result = await asyncio.to_thread(self.product_agent.run, analysis_query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("analysis.duration_ms", duration * 1000)
                    span.set_attribute("analysis.type", analysis_type)
                    
                    return {
                        "query": analysis_query,
                        "result": result,
                        "duration_ms": duration * 1000
                    }
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            analysis_query = f"Provide {analysis_type} analysis for category '{category}'"
            result = await asyncio.to_thread(self.product_agent.run, analysis_query)
            return {
                "query": analysis_query,
                "result": result
            }
    
    @override
    async def _handle_text_query(self, query: str) -> str:
        """Handle text queries with telemetry."""
        if self.telemetry:
            with self.telemetry.get_business_metrics().trace_product_search(
                query, 0, 0.0  # We'll update these after execution
            ) as span:
                try:
                    # Execute query
                    start_time = time.time()
                    result = await asyncio.to_thread(self.product_agent.run, query)
                    duration = time.time() - start_time
                    
                    # Update span with actual metrics
                    span.set_attribute("search.duration_ms", duration * 1000)
                    span.set_attribute("search.results_count", len(str(result).split()))
                    
                    return result
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Fallback without telemetry
            return await asyncio.to_thread(self.product_agent.run, query)


def main():
    """Main entry point for the enhanced product agent."""
    try:
        # Create enhanced agent
        agent = EnhancedProductAgentA2A()
        
        # Get configuration
        host = os.getenv("A2A_HOST", "0.0.0.0")
        port = int(os.getenv("PRODUCT_AGENT_PORT", "8001"))
        
        logger.info(f"Starting Enhanced Product Agent on {host}:{port}")
        
        # Create and run agent server
        create_and_run_agent_server(
            agent_executor=agent,
            agent_card_path=str(agent.agent_card_path),
            host=host,
            port=port,
            server_name="Enhanced Product Agent"
        )
        
    except KeyboardInterrupt:
        logger.info("Enhanced Product Agent stopped by user")
    except Exception as e:
        logger.error(f"Enhanced Product Agent error: {e}")
        raise


if __name__ == "__main__":
    main() 