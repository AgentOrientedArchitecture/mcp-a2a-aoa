"""Performance Monitoring OpenTelemetry Instrumentation Manager.

This module provides performance monitoring and tracing for the A2A multi-agent system,
enabling tracking of system metrics, resource usage, and performance bottlenecks.
"""

import logging
import threading
import time
from typing import Any, Dict, Optional

import psutil
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors and traces performance metrics."""
    
    def __init__(self, tracer_provider: TracerProvider):
        """Initialize the performance monitor.
        
        Args:
            tracer_provider: OpenTelemetry tracer provider instance
        """
        self.tracer = trace.get_tracer(__name__)
        self.tracer_provider = tracer_provider
        self.monitoring_thread = None
        self.stop_monitoring = False
        self.monitoring_interval = 30  # seconds
        
        logger.info("Initialized PerformanceMonitor")
    
    def start_performance_monitoring(self, agent_name: str, interval: int = 30):
        """Start continuous performance monitoring.
        
        Args:
            agent_name: Name of the agent to monitor
            interval: Monitoring interval in seconds
        """
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.warning("Performance monitoring already running")
            return
        
        self.monitoring_interval = interval
        self.stop_monitoring = False
        
        self.monitoring_thread = threading.Thread(
            target=self._monitor_performance,
            args=(agent_name,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info(f"Started performance monitoring for agent: {agent_name}")
    
    def _monitor_performance(self, agent_name: str):
        """Monitor system performance metrics.
        
        Args:
            agent_name: Name of the agent being monitored
        """
        while not self.stop_monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Create performance span
                with self.tracer.start_span(
                    "system.performance.metrics",
                    attributes={
                        "agent.name": agent_name,
                        "cpu.usage_percent": cpu_percent,
                        "memory.usage_percent": memory.percent,
                        "memory.available_mb": memory.available / (1024 * 1024),
                        "memory.total_mb": memory.total / (1024 * 1024),
                        "memory.used_mb": memory.used / (1024 * 1024),
                        "disk.usage_percent": disk.percent,
                        "disk.free_gb": disk.free / (1024 * 1024 * 1024),
                        "disk.total_gb": disk.total / (1024 * 1024 * 1024),
                        "monitoring.timestamp": time.time(),
                        "monitoring.interval_seconds": self.monitoring_interval
                    }
                ):
                    pass
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def stop_performance_monitoring(self):
        """Stop performance monitoring."""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            logger.info("Stopped performance monitoring")
    
    def trace_operation_performance(self, operation_name: str, duration: float, **attributes):
        """Trace operation performance.
        
        Args:
            operation_name: Name of the operation
            duration: Duration of the operation in seconds
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "operation.name": operation_name,
            "performance.duration_ms": duration * 1000,
            "performance.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "performance.operation",
            attributes=span_attrs
        )
    
    def trace_memory_usage(self, agent_name: str, memory_usage_mb: float, **attributes):
        """Trace memory usage.
        
        Args:
            agent_name: Name of the agent
            memory_usage_mb: Memory usage in MB
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "memory.usage_mb": memory_usage_mb,
            "memory.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "performance.memory.usage",
            attributes=span_attrs
        )
    
    def trace_cpu_usage(self, agent_name: str, cpu_percent: float, **attributes):
        """Trace CPU usage.
        
        Args:
            agent_name: Name of the agent
            cpu_percent: CPU usage percentage
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "cpu.usage_percent": cpu_percent,
            "cpu.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "performance.cpu.usage",
            attributes=span_attrs
        )
    
    def trace_network_usage(self, agent_name: str, bytes_sent: int, bytes_recv: int, **attributes):
        """Trace network usage.
        
        Args:
            agent_name: Name of the agent
            bytes_sent: Bytes sent
            bytes_recv: Bytes received
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "network.bytes_sent": bytes_sent,
            "network.bytes_recv": bytes_recv,
            "network.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "performance.network.usage",
            attributes=span_attrs
        )
    
    def trace_disk_usage(self, agent_name: str, disk_usage_percent: float, **attributes):
        """Trace disk usage.
        
        Args:
            agent_name: Name of the agent
            disk_usage_percent: Disk usage percentage
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "disk.usage_percent": disk_usage_percent,
            "disk.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "performance.disk.usage",
            attributes=span_attrs
        )
    
    def trace_thread_count(self, agent_name: str, thread_count: int, **attributes):
        """Trace thread count.
        
        Args:
            agent_name: Name of the agent
            thread_count: Number of active threads
            **attributes: Additional span attributes
            
        Returns:
            Active span context manager
        """
        span_attrs = {
            "agent.name": agent_name,
            "threads.count": thread_count,
            "threads.timestamp": time.time(),
            **attributes
        }
        
        return self.tracer.start_span(
            "performance.threads.count",
            attributes=span_attrs
        )
    
    def get_current_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics.
        
        Returns:
            Dictionary containing current system metrics
        """
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "memory_total_mb": memory.total / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
                "disk_total_gb": disk.total / (1024 * 1024 * 1024),
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def create_span_with_context(self, span_name: str, **attributes):
        """Create a custom performance span with context.
        
        Args:
            span_name: Name of the span
            **attributes: Span attributes
            
        Returns:
            Active span context manager
        """
        return self.tracer.start_span(span_name, attributes=attributes) 