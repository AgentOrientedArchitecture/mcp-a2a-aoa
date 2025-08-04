"""A2A Protocol OpenTelemetry Instrumentation Manager.

This module provides comprehensive OpenTelemetry instrumentation for A2A communications,
enabling trace collection and monitoring of inter-agent interactions.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from openinference.semconv.trace import SpanAttributes

logger = logging.getLogger(__name__)


class A2ATelemetryManager:
    """Manages OpenTelemetry instrumentation for A2A communications."""
    
    def __init__(self, tracer_provider: TracerProvider):
        """Initialize the A2A telemetry manager.
        
        Args:
            tracer_provider: OpenTelemetry tracer provider instance
        """
        self.tracer = trace.get_tracer(__name__)
        self.tracer_provider = tracer_provider
        
        logger.info("Initialized A2ATelemetryManager")
    
    def trace_agent_discovery(self, agent_name: str, endpoint: str, **attributes):
        """Trace agent discovery operations.
        
        Args:
            agent_name: Name of the agent being discovered
            endpoint: Endpoint URL of the discovered agent
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "agent.endpoint": endpoint,
            "discovery.method": "http",
            "protocol": "a2a",
            **attributes
        }
        
        return self.tracer.start_span(
            "a2a.agent.discovery",
            attributes=span_attrs
        )
    
    def trace_agent_communication(self, from_agent: str, to_agent: str, message_type: str, **attributes):
        """Trace inter-agent communication.
        
        Args:
            from_agent: Name of the source agent
            to_agent: Name of the destination agent
            message_type: Type of message being sent
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "from.agent": from_agent,
            "to.agent": to_agent,
            "message.type": message_type,
            "protocol": "a2a",
            "communication.direction": "outbound",
            **attributes
        }
        
        return self.tracer.start_span(
            "a2a.agent.communication",
            attributes=span_attrs
        )
    
    def trace_capability_invocation(self, agent_name: str, capability: str, args: Dict[str, Any], **attributes):
        """Trace capability invocations.
        
        Args:
            agent_name: Name of the agent invoking the capability
            capability: Name of the capability being invoked
            args: Arguments passed to the capability
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "capability.name": capability,
            "capability.args": json.dumps(args, default=str),
            "invocation.timestamp": time.time(),
            "protocol": "a2a",
            **attributes
        }
        
        return self.tracer.start_span(
            "a2a.capability.invocation",
            attributes=span_attrs
        )
    
    def trace_task_execution(self, agent_name: str, task_id: str, task_type: str, **attributes):
        """Trace task execution.
        
        Args:
            agent_name: Name of the agent executing the task
            task_id: Unique identifier for the task
            task_type: Type of task being executed
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "task.id": task_id,
            "task.type": task_type,
            "execution.timestamp": time.time(),
            "protocol": "a2a",
            **attributes
        }
        
        return self.tracer.start_span(
            "a2a.task.execution",
            attributes=span_attrs
        )
    
    def trace_agent_registration(self, agent_name: str, endpoint: str, capabilities: list, **attributes):
        """Trace agent registration.
        
        Args:
            agent_name: Name of the agent being registered
            endpoint: Endpoint URL of the agent
            capabilities: List of agent capabilities
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "agent.endpoint": endpoint,
            "agent.capabilities": json.dumps(capabilities),
            "registration.timestamp": time.time(),
            "protocol": "a2a",
            **attributes
        }
        
        return self.tracer.start_span(
            "a2a.agent.registration",
            attributes=span_attrs
        )
    
    def trace_error(self, agent_name: str, error_type: str, error_message: str, **attributes):
        """Trace errors in A2A communications.
        
        Args:
            agent_name: Name of the agent where the error occurred
            error_type: Type of error
            error_message: Error message
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "error.type": error_type,
            "error.message": error_message,
            "error.timestamp": time.time(),
            "protocol": "a2a",
            **attributes
        }
        
        return self.tracer.start_span(
            "a2a.error",
            attributes=span_attrs
        )
    
    def trace_performance_metrics(self, agent_name: str, operation: str, duration: float, **attributes):
        """Trace performance metrics.
        
        Args:
            agent_name: Name of the agent
            operation: Type of operation
            duration: Duration of the operation in seconds
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "operation.type": operation,
            "performance.duration_ms": duration * 1000,
            "performance.timestamp": time.time(),
            "protocol": "a2a",
            **attributes
        }
        
        return self.tracer.start_span(
            "a2a.performance.metrics",
            attributes=span_attrs
        )
    
    def create_span_with_context(self, span_name: str, **attributes):
        """Create a custom span with context.
        
        Args:
            span_name: Name of the span
            **attributes: Span attributes
            
        Returns:
            Active span context manager
        """
        return self.tracer.start_span(span_name, attributes=attributes) 