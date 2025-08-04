"""Telemetry Module for A2A Multi-Agent System.

This module provides comprehensive OpenTelemetry instrumentation for the A2A multi-agent system,
combining SMOL agents, A2A communications, MCP interactions, business metrics, and performance monitoring.
"""

from .smol_instrumentation import SMOLTelemetryManager
from .a2a_instrumentation import A2ATelemetryManager
from .mcp_instrumentation import MCPTelemetryManager
from .business_metrics import BusinessMetricsManager
from .performance_monitoring import PerformanceMonitor

__all__ = [
    "SMOLTelemetryManager",
    "A2ATelemetryManager", 
    "MCPTelemetryManager",
    "BusinessMetricsManager",
    "PerformanceMonitor",
    "TelemetryManager"
]


class TelemetryManager:
    """Unified telemetry manager for the A2A multi-agent system."""
    
    def __init__(self, phoenix_endpoint: str = None, project_name: str = "a2a-multi-agent"):
        """Initialize the unified telemetry manager.
        
        Args:
            phoenix_endpoint: Phoenix collector endpoint URL
            project_name: Name of the project for trace organization
        """
        # Initialize SMOL telemetry first (sets up the tracer provider)
        self.smol_telemetry = SMOLTelemetryManager(phoenix_endpoint)
        self.tracer_provider = self.smol_telemetry.setup(project_name)
        
        # Initialize other telemetry managers with the tracer provider
        self.a2a_telemetry = A2ATelemetryManager(self.tracer_provider)
        self.mcp_telemetry = MCPTelemetryManager(self.tracer_provider)
        self.business_metrics = BusinessMetricsManager(self.tracer_provider)
        self.performance_monitor = PerformanceMonitor(self.tracer_provider)
        
        self.project_name = project_name
        self.is_initialized = self.smol_telemetry.is_initialized()
        
        if self.is_initialized:
            print(f"✅ Telemetry initialized for project: {project_name}")
        else:
            print("⚠️ Telemetry initialization failed")
    
    def get_smol_telemetry(self) -> SMOLTelemetryManager:
        """Get SMOL telemetry manager."""
        return self.smol_telemetry
    
    def get_a2a_telemetry(self) -> A2ATelemetryManager:
        """Get A2A telemetry manager."""
        return self.a2a_telemetry
    
    def get_mcp_telemetry(self) -> MCPTelemetryManager:
        """Get MCP telemetry manager."""
        return self.mcp_telemetry
    
    def get_business_metrics(self) -> BusinessMetricsManager:
        """Get business metrics manager."""
        return self.business_metrics
    
    def get_performance_monitor(self) -> PerformanceMonitor:
        """Get performance monitor."""
        return self.performance_monitor
    
    def start_performance_monitoring(self, agent_name: str, interval: int = 30):
        """Start performance monitoring for an agent."""
        if self.is_initialized:
            self.performance_monitor.start_performance_monitoring(agent_name, interval)
        else:
            print("⚠️ Cannot start performance monitoring - telemetry not initialized")
    
    def stop_performance_monitoring(self):
        """Stop performance monitoring."""
        self.performance_monitor.stop_performance_monitoring()
    
    def is_telemetry_initialized(self) -> bool:
        """Check if telemetry is properly initialized."""
        return self.is_initialized
