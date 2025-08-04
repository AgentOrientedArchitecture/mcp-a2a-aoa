"""MCP (Model Context Protocol) OpenTelemetry Instrumentation Manager.

This module provides comprehensive OpenTelemetry instrumentation for MCP interactions,
enabling trace collection and monitoring of tool calls and server communications.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from openinference.semconv.trace import SpanAttributes

logger = logging.getLogger(__name__)


class MCPTelemetryManager:
    """Manages OpenTelemetry instrumentation for MCP interactions."""
    
    def __init__(self, tracer_provider: TracerProvider):
        """Initialize the MCP telemetry manager.
        
        Args:
            tracer_provider: OpenTelemetry tracer provider instance
        """
        self.tracer = trace.get_tracer(__name__)
        self.tracer_provider = tracer_provider
        
        logger.info("Initialized MCPTelemetryManager")
    
    def trace_mcp_tool_call(self, tool_name: str, args: Dict[str, Any], result: Any, **attributes):
        """Trace MCP tool calls.
        
        Args:
            tool_name: Name of the MCP tool being called
            args: Arguments passed to the tool
            result: Result returned by the tool
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "tool.name": tool_name,
            "tool.args": json.dumps(args, default=str),
            "tool.result_type": type(result).__name__,
            "tool.result_length": len(str(result)) if result else 0,
            "protocol": "mcp",
            "operation.type": "tool_call",
            **attributes
        }
        
        return self.tracer.start_span(
            "mcp.tool.call",
            attributes=span_attrs
        )
    
    def trace_mcp_server_connection(self, server_path: str, status: str, **attributes):
        """Trace MCP server connection events.
        
        Args:
            server_path: Path to the MCP server
            status: Connection status (connected, failed, disconnected)
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "server.path": server_path,
            "connection.status": status,
            "connection.timestamp": time.time(),
            "protocol": "mcp",
            "operation.type": "server_connection",
            **attributes
        }
        
        return self.tracer.start_span(
            "mcp.server.connection",
            attributes=span_attrs
        )
    
    def trace_mcp_schema_discovery(self, server_path: str, schema_info: Dict[str, Any], **attributes):
        """Trace MCP schema discovery.
        
        Args:
            server_path: Path to the MCP server
            schema_info: Schema information discovered
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "server.path": server_path,
            "schema.tools_count": len(schema_info.get("tools", [])),
            "schema.resources_count": len(schema_info.get("resources", [])),
            "discovery.timestamp": time.time(),
            "protocol": "mcp",
            "operation.type": "schema_discovery",
            **attributes
        }
        
        return self.tracer.start_span(
            "mcp.schema.discovery",
            attributes=span_attrs
        )
    
    def trace_mcp_resource_access(self, resource_name: str, operation: str, **attributes):
        """Trace MCP resource access operations.
        
        Args:
            resource_name: Name of the resource being accessed
            operation: Type of operation (read, write, list)
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "resource.name": resource_name,
            "resource.operation": operation,
            "access.timestamp": time.time(),
            "protocol": "mcp",
            "operation.type": "resource_access",
            **attributes
        }
        
        return self.tracer.start_span(
            "mcp.resource.access",
            attributes=span_attrs
        )
    
    def trace_mcp_error(self, server_path: str, error_type: str, error_message: str, **attributes):
        """Trace MCP errors.
        
        Args:
            server_path: Path to the MCP server where error occurred
            error_type: Type of error
            error_message: Error message
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "server.path": server_path,
            "error.type": error_type,
            "error.message": error_message,
            "error.timestamp": time.time(),
            "protocol": "mcp",
            "operation.type": "error",
            **attributes
        }
        
        return self.tracer.start_span(
            "mcp.error",
            attributes=span_attrs
        )
    
    def trace_mcp_performance(self, operation: str, duration: float, **attributes):
        """Trace MCP performance metrics.
        
        Args:
            operation: Type of MCP operation
            duration: Duration of the operation in seconds
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "operation.type": operation,
            "performance.duration_ms": duration * 1000,
            "performance.timestamp": time.time(),
            "protocol": "mcp",
            **attributes
        }
        
        return self.tracer.start_span(
            "mcp.performance.metrics",
            attributes=span_attrs
        )
    
    def trace_mcp_client_initialization(self, client_type: str, server_path: str, **attributes):
        """Trace MCP client initialization.
        
        Args:
            client_type: Type of MCP client (stdio, tcp, etc.)
            server_path: Path to the MCP server
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "client.type": client_type,
            "server.path": server_path,
            "initialization.timestamp": time.time(),
            "protocol": "mcp",
            "operation.type": "client_initialization",
            **attributes
        }
        
        return self.tracer.start_span(
            "mcp.client.initialization",
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