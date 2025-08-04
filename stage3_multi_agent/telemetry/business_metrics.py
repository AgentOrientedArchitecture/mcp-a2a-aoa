"""Business Metrics OpenTelemetry Instrumentation Manager.

This module provides business-specific metrics and spans for the A2A multi-agent system,
enabling tracking of domain-specific KPIs and business intelligence.
"""

import logging
import time
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from openinference.semconv.trace import SpanAttributes

logger = logging.getLogger(__name__)


class BusinessMetricsManager:
    """Manages business-specific metrics and spans."""
    
    def __init__(self, tracer_provider: TracerProvider):
        """Initialize the business metrics manager.
        
        Args:
            tracer_provider: OpenTelemetry tracer provider instance
        """
        self.tracer = trace.get_tracer(__name__)
        self.tracer_provider = tracer_provider
        
        logger.info("Initialized BusinessMetricsManager")
    
    def trace_product_search(self, query: str, results_count: int, search_time: float, **attributes):
        """Trace product search operations.
        
        Args:
            query: Search query string
            results_count: Number of results returned
            search_time: Time taken for search in seconds
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "search.query": query,
            "search.results_count": results_count,
            "search.duration_ms": search_time * 1000,
            "business.domain": "ecommerce",
            "operation.type": "product_search",
            "search.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "business.product.search",
            attributes=span_attrs
        )
    
    def trace_inventory_check(self, product_id: str, stock_level: int, threshold: int, **attributes):
        """Trace inventory check operations.
        
        Args:
            product_id: ID of the product being checked
            stock_level: Current stock level
            threshold: Stock threshold for alerts
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "product.id": product_id,
            "stock.level": stock_level,
            "stock.threshold": threshold,
            "stock.status": "low" if stock_level < threshold else "adequate",
            "business.domain": "inventory",
            "operation.type": "inventory_check",
            "check.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "business.inventory.check",
            attributes=span_attrs
        )
    
    def trace_sales_analysis(self, period: str, revenue: float, transaction_count: int, **attributes):
        """Trace sales analysis operations.
        
        Args:
            period: Analysis period (daily, weekly, monthly)
            revenue: Total revenue for the period
            transaction_count: Number of transactions
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        avg_revenue = revenue / transaction_count if transaction_count > 0 else 0
        
        span_attrs = {
            "analysis.period": period,
            "revenue.total": revenue,
            "transactions.count": transaction_count,
            "revenue.average": avg_revenue,
            "business.domain": "sales",
            "operation.type": "sales_analysis",
            "analysis.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "business.sales.analysis",
            attributes=span_attrs
        )
    
    def trace_customer_insight(self, customer_id: str, insight_type: str, confidence: float, **attributes):
        """Trace customer insight generation.
        
        Args:
            customer_id: ID of the customer
            insight_type: Type of insight generated
            confidence: Confidence score of the insight
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "customer.id": customer_id,
            "insight.type": insight_type,
            "insight.confidence": confidence,
            "business.domain": "customer_analytics",
            "operation.type": "customer_insight",
            "insight.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "business.customer.insight",
            attributes=span_attrs
        )
    
    def trace_recommendation_generation(self, user_id: str, recommendation_count: int, algorithm: str, **attributes):
        """Trace recommendation generation.
        
        Args:
            user_id: ID of the user
            recommendation_count: Number of recommendations generated
            algorithm: Algorithm used for recommendations
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "user.id": user_id,
            "recommendations.count": recommendation_count,
            "algorithm.name": algorithm,
            "business.domain": "recommendations",
            "operation.type": "recommendation_generation",
            "generation.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "business.recommendation.generation",
            attributes=span_attrs
        )
    
    def trace_price_analysis(self, product_category: str, price_range: tuple, analysis_type: str, **attributes):
        """Trace price analysis operations.
        
        Args:
            product_category: Category of products analyzed
            price_range: Tuple of (min_price, max_price)
            analysis_type: Type of price analysis
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "product.category": product_category,
            "price.min": price_range[0],
            "price.max": price_range[1],
            "analysis.type": analysis_type,
            "business.domain": "pricing",
            "operation.type": "price_analysis",
            "analysis.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "business.price.analysis",
            attributes=span_attrs
        )
    
    def trace_supply_chain_event(self, event_type: str, location: str, impact_level: str, **attributes):
        """Trace supply chain events.
        
        Args:
            event_type: Type of supply chain event
            location: Location of the event
            impact_level: Impact level (low, medium, high, critical)
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "event.type": event_type,
            "event.location": location,
            "event.impact_level": impact_level,
            "business.domain": "supply_chain",
            "operation.type": "supply_chain_event",
            "event.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "business.supply_chain.event",
            attributes=span_attrs
        )
    
    def trace_business_kpi(self, kpi_name: str, kpi_value: float, target_value: float, **attributes):
        """Trace business KPI measurements.
        
        Args:
            kpi_name: Name of the KPI
            kpi_value: Current KPI value
            target_value: Target KPI value
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        performance_ratio = kpi_value / target_value if target_value > 0 else 0
        
        span_attrs = {
            "kpi.name": kpi_name,
            "kpi.value": kpi_value,
            "kpi.target": target_value,
            "kpi.performance_ratio": performance_ratio,
            "kpi.status": "above_target" if kpi_value >= target_value else "below_target",
            "business.domain": "kpi_tracking",
            "operation.type": "kpi_measurement",
            "measurement.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "business.kpi.measurement",
            attributes=span_attrs
        )
    
    def create_span_with_context(self, span_name: str, **attributes):
        """Create a custom business span with context.
        
        Args:
            span_name: Name of the span
            **attributes: Span attributes
            
        Returns:
            Active span context manager
        """
        return self.tracer.start_span(span_name, attributes=attributes) 