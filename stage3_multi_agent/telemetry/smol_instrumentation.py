"""SMOL Agents OpenTelemetry Instrumentation Manager.

This module provides comprehensive OpenTelemetry instrumentation for SMOL agents,
enabling trace collection and monitoring of agent activities.
"""

import logging
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

logger = logging.getLogger(__name__)


class SMOLTelemetryManager:
    """Manages OpenTelemetry instrumentation for SMOL agents."""
    
    def __init__(self, phoenix_endpoint: Optional[str] = None):
        """Initialize the SMOL telemetry manager.
        
        Args:
            phoenix_endpoint: Phoenix collector endpoint URL. 
                             Defaults to environment variable PHOENIX_COLLECTOR_ENDPOINT
                             or http://localhost:6006/v1/traces
        """
        self.phoenix_endpoint = phoenix_endpoint or os.getenv(
            "PHOENIX_COLLECTOR_ENDPOINT", 
            "http://localhost:6006/v1/traces"
        )
        self.tracer_provider = None
        self.smol_instrumentor = None
        self.tracer = None
        self._is_initialized = False
        
        logger.info(f"Initialized SMOLTelemetryManager with endpoint: {self.phoenix_endpoint}")
    
    def setup(self, project_name: str = "a2a-multi-agent") -> TracerProvider:
        """Initialize OpenTelemetry with Phoenix integration.
        
        Args:
            project_name: Name of the project for trace organization
            
        Returns:
            Configured TracerProvider instance
        """
        try:
            # Register Phoenix-aware tracer provider
            self.tracer_provider = register(
                project_name=project_name,
                endpoint=self.phoenix_endpoint,
                batch=True,
                auto_instrument=True
            )
            
            # Instrument SMOL agents
            self.smol_instrumentor = SmolagentsInstrumentor()
            self.smol_instrumentor.instrument(tracer_provider=self.tracer_provider)
            
            # Get tracer for custom spans
            self.tracer = trace.get_tracer(__name__)
            
            self._is_initialized = True
            logger.info(f"Successfully initialized SMOL telemetry for project: {project_name}")
            
            return self.tracer_provider
            
        except Exception as e:
            logger.error(f"Failed to initialize SMOL telemetry: {e}")
            raise
    
    def create_agent_span(self, agent_name: str, operation: str, **attributes):
        """Create custom span for agent operations.
        
        Args:
            agent_name: Name of the agent
            operation: Type of operation being performed
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        if not self._is_initialized:
            logger.warning("SMOL telemetry not initialized. Creating dummy span.")
            return DummySpanContext()
        
        span_attrs = {
            "agent.name": agent_name,
            "operation.type": operation,
            "framework": "smolagents",
            **attributes
        }
        
        return self.tracer.start_span(
            f"{agent_name}.{operation}",
            attributes=span_attrs
        )
    
    def create_tool_call_span(self, tool_name: str, agent_name: str, **attributes):
        """Create span for tool calls.
        
        Args:
            tool_name: Name of the tool being called
            agent_name: Name of the agent making the call
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        if not self._is_initialized:
            logger.warning("SMOL telemetry not initialized. Creating dummy span.")
            return DummySpanContext()
        
        span_attrs = {
            "tool.name": tool_name,
            "agent.name": agent_name,
            "operation.type": "tool_call",
            "framework": "smolagents",
            **attributes
        }
        
        return self.tracer.start_span(
            f"{agent_name}.tool_call.{tool_name}",
            attributes=span_attrs
        )
    
    def create_llm_call_span(self, model_name: str, agent_name: str, **attributes):
        """Create span for LLM calls.
        
        Args:
            model_name: Name of the LLM model
            agent_name: Name of the agent making the call
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        if not self._is_initialized:
            logger.warning("SMOL telemetry not initialized. Creating dummy span.")
            return DummySpanContext()
        
        span_attrs = {
            "llm.model": model_name,
            "agent.name": agent_name,
            "operation.type": "llm_call",
            "framework": "smolagents",
            **attributes
        }
        
        return self.tracer.start_span(
            f"{agent_name}.llm_call.{model_name}",
            attributes=span_attrs
        )
    
    def is_initialized(self) -> bool:
        """Check if telemetry is properly initialized.
        
        Returns:
            True if telemetry is initialized, False otherwise
        """
        return self._is_initialized
    
    def get_tracer(self) -> Optional[trace.Tracer]:
        """Get the configured tracer.
        
        Returns:
            Tracer instance if initialized, None otherwise
        """
        return self.tracer if self._is_initialized else None


class DummySpanContext:
    """Dummy span context for when telemetry is not initialized."""
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def set_attribute(self, key: str, value):
        """Dummy method for setting span attributes."""
        pass
    
    def set_attributes(self, attributes: dict):
        """Dummy method for setting multiple span attributes."""
        pass 