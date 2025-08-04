#!/usr/bin/env python3
"""Unit tests for MCP instrumentation."""

import json
import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from telemetry.mcp_instrumentation import MCPTelemetryManager
from opentelemetry.sdk.trace import TracerProvider


class TestMCPTelemetryManager(unittest.TestCase):
    """Test cases for MCPTelemetryManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracer_provider = TracerProvider()
        self.mcp_telemetry = MCPTelemetryManager(self.tracer_provider)

    def test_initialization(self):
        """Test MCP telemetry manager initialization."""
        self.assertIsNotNone(self.mcp_telemetry)
        self.assertIsNotNone(self.mcp_telemetry.tracer)
        self.assertEqual(self.mcp_telemetry.tracer_provider, self.tracer_provider)

    def test_trace_mcp_tool_call(self):
        """Test MCP tool call tracing."""
        tool_name = "search_products"
        args = {"query": "laptop", "category": "electronics"}
        result = {"products": [{"id": 1, "name": "Laptop"}]}

        with self.mcp_telemetry.trace_mcp_tool_call(tool_name, args, result) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("tool.name"), tool_name)
            self.assertIsNotNone(span.get_attribute("tool.args"))
            self.assertEqual(span.get_attribute("tool.result_type"), "dict")
            self.assertIsNotNone(span.get_attribute("tool.result_length"))
            self.assertEqual(span.get_attribute("protocol"), "mcp")
            self.assertEqual(span.get_attribute("operation.type"), "tool_call")

    def test_trace_mcp_server_connection(self):
        """Test MCP server connection tracing."""
        server_path = "/path/to/mcp/server"
        status = "connected"

        with self.mcp_telemetry.trace_mcp_server_connection(server_path, status) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("server.path"), server_path)
            self.assertEqual(span.get_attribute("connection.status"), status)
            self.assertIsNotNone(span.get_attribute("connection.timestamp"))
            self.assertEqual(span.get_attribute("protocol"), "mcp")
            self.assertEqual(span.get_attribute("operation.type"), "server_connection")

    def test_trace_mcp_schema_discovery(self):
        """Test MCP schema discovery tracing."""
        server_path = "/path/to/mcp/server"
        schema_info = {
            "tools": [
                {"name": "search_products", "description": "Search products"},
                {"name": "get_product", "description": "Get product details"}
            ],
            "resources": [
                {"name": "product_catalog", "description": "Product catalog"}
            ]
        }

        with self.mcp_telemetry.trace_mcp_schema_discovery(server_path, schema_info) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("server.path"), server_path)
            self.assertEqual(span.get_attribute("schema.tools_count"), 2)
            self.assertEqual(span.get_attribute("schema.resources_count"), 1)
            self.assertIsNotNone(span.get_attribute("discovery.timestamp"))
            self.assertEqual(span.get_attribute("protocol"), "mcp")
            self.assertEqual(span.get_attribute("operation.type"), "schema_discovery")

    def test_trace_mcp_resource_access(self):
        """Test MCP resource access tracing."""
        resource_name = "product_catalog"
        operation = "read"

        with self.mcp_telemetry.trace_mcp_resource_access(resource_name, operation) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("resource.name"), resource_name)
            self.assertEqual(span.get_attribute("resource.operation"), operation)
            self.assertIsNotNone(span.get_attribute("access.timestamp"))
            self.assertEqual(span.get_attribute("protocol"), "mcp")
            self.assertEqual(span.get_attribute("operation.type"), "resource_access")

    def test_trace_mcp_error(self):
        """Test MCP error tracing."""
        server_path = "/path/to/mcp/server"
        error_type = "connection_error"
        error_message = "Failed to connect to MCP server"

        with self.mcp_telemetry.trace_mcp_error(server_path, error_type, error_message) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("server.path"), server_path)
            self.assertEqual(span.get_attribute("error.type"), error_type)
            self.assertEqual(span.get_attribute("error.message"), error_message)
            self.assertIsNotNone(span.get_attribute("error.timestamp"))
            self.assertEqual(span.get_attribute("protocol"), "mcp")
            self.assertEqual(span.get_attribute("operation.type"), "error")

    def test_trace_mcp_performance(self):
        """Test MCP performance metrics tracing."""
        operation = "tool_call"
        duration = 0.5

        with self.mcp_telemetry.trace_mcp_performance(operation, duration) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("operation.type"), operation)
            self.assertEqual(span.get_attribute("performance.duration_ms"), duration * 1000)
            self.assertIsNotNone(span.get_attribute("performance.timestamp"))
            self.assertEqual(span.get_attribute("protocol"), "mcp")

    def test_trace_mcp_client_initialization(self):
        """Test MCP client initialization tracing."""
        client_type = "stdio"
        server_path = "/path/to/mcp/server"

        with self.mcp_telemetry.trace_mcp_client_initialization(client_type, server_path) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("client.type"), client_type)
            self.assertEqual(span.get_attribute("server.path"), server_path)
            self.assertIsNotNone(span.get_attribute("initialization.timestamp"))
            self.assertEqual(span.get_attribute("protocol"), "mcp")
            self.assertEqual(span.get_attribute("operation.type"), "client_initialization")

    def test_create_span_with_context(self):
        """Test custom span creation."""
        span_name = "mcp.custom.operation"
        attributes = {"custom.attr": "value", "test.attr": 123}

        with self.mcp_telemetry.create_span_with_context(span_name, **attributes) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("custom.attr"), "value")
            self.assertEqual(span.get_attribute("test.attr"), 123)

    def test_complex_tool_call_attributes(self):
        """Test complex tool call attributes."""
        tool_name = "complex_tool"
        complex_args = {
            "nested_data": {
                "level1": {
                    "level2": {
                        "items": [1, 2, 3, 4, 5],
                        "metadata": {"source": "database", "version": "1.0"}
                    }
                }
            },
            "filters": {
                "category": "electronics",
                "price_range": {"min": 100, "max": 1000},
                "in_stock": True
            }
        }
        complex_result = {
            "results": [
                {"id": 1, "name": "Product 1", "price": 150.0},
                {"id": 2, "name": "Product 2", "price": 250.0}
            ],
            "total_count": 2,
            "query_time_ms": 45
        }

        with self.mcp_telemetry.trace_mcp_tool_call(tool_name, complex_args, complex_result) as span:
            self.assertIsNotNone(span)
            # Verify complex attributes are serialized
            args_attr = span.get_attribute("tool.args")
            result_attr = span.get_attribute("tool.result_type")
            self.assertIsNotNone(args_attr)
            self.assertEqual(result_attr, "dict")
            # Should be JSON string
            self.assertIsInstance(args_attr, str)

    def test_multiple_concurrent_tool_calls(self):
        """Test multiple concurrent tool calls."""
        tool_calls = [
            ("search_products", {"query": "laptop"}, {"results": []}),
            ("get_product", {"id": 1}, {"product": {"id": 1, "name": "Laptop"}}),
            ("analyze_prices", {"category": "electronics"}, {"analysis": {}})
        ]
        
        spans = []
        for tool_name, args, result in tool_calls:
            span = self.mcp_telemetry.trace_mcp_tool_call(tool_name, args, result)
            spans.append(span)

        # Verify all spans are created
        self.assertEqual(len(spans), 3)
        for span in spans:
            self.assertIsNotNone(span)

        # Clean up spans
        for span in spans:
            span.__exit__(None, None, None)

    def test_error_scenarios(self):
        """Test error scenarios in MCP operations."""
        server_path = "/path/to/mcp/server"
        
        # Test connection failure
        with self.mcp_telemetry.trace_mcp_server_connection(server_path, "failed") as span:
            self.assertIsNotNone(span)
            self.assertEqual(span.get_attribute("connection.status"), "failed")

        # Test tool call error
        with self.mcp_telemetry.trace_mcp_tool_call("failing_tool", {}, None) as span:
            # Simulate error during tool call
            span.set_attribute("error.occurred", True)
            span.set_attribute("error.message", "Tool execution failed")

        # Test schema discovery error
        with self.mcp_telemetry.trace_mcp_schema_discovery(server_path, {}) as span:
            self.assertIsNotNone(span)
            self.assertEqual(span.get_attribute("schema.tools_count"), 0)


class TestMCPTelemetryIntegration(unittest.TestCase):
    """Integration tests for MCP telemetry."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracer_provider = TracerProvider()
        self.mcp_telemetry = MCPTelemetryManager(self.tracer_provider)

    def test_end_to_end_mcp_workflow(self):
        """Test end-to-end MCP workflow tracing."""
        server_path = "/path/to/mcp/server"
        
        # Simulate client initialization
        with self.mcp_telemetry.trace_mcp_client_initialization("stdio", server_path) as init_span:
            # Simulate server connection
            with self.mcp_telemetry.trace_mcp_server_connection(server_path, "connected") as conn_span:
                # Simulate schema discovery
                with self.mcp_telemetry.trace_mcp_schema_discovery(server_path, {"tools": []}) as schema_span:
                    # Simulate tool call
                    with self.mcp_telemetry.trace_mcp_tool_call("test_tool", {}, {}) as tool_span:
                        # Simulate resource access
                        with self.mcp_telemetry.trace_mcp_resource_access("test_resource", "read") as resource_span:
                            # Verify all spans are created
                            self.assertIsNotNone(init_span)
                            self.assertIsNotNone(conn_span)
                            self.assertIsNotNone(schema_span)
                            self.assertIsNotNone(tool_span)
                            self.assertIsNotNone(resource_span)

    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        operation = "complex_tool_call"
        
        # Simulate operation with timing
        start_time = time.time()
        with self.mcp_telemetry.trace_mcp_tool_call("performance_test", {}, {}) as tool_span:
            # Simulate work
            time.sleep(0.1)
        
        duration = time.time() - start_time
        
        # Trace performance metrics
        with self.mcp_telemetry.trace_mcp_performance(operation, duration) as perf_span:
            self.assertIsNotNone(perf_span)
            self.assertIsNotNone(perf_span.get_attribute("performance.duration_ms"))

    def test_error_recovery_scenario(self):
        """Test error recovery scenario."""
        server_path = "/path/to/mcp/server"
        
        # Simulate initial connection failure
        with self.mcp_telemetry.trace_mcp_server_connection(server_path, "failed") as fail_span:
            # Simulate error
            with self.mcp_telemetry.trace_mcp_error(server_path, "connection_error", "Connection failed") as error_span:
                pass
        
        # Simulate successful retry
        with self.mcp_telemetry.trace_mcp_server_connection(server_path, "connected") as success_span:
            # Simulate successful tool call
            with self.mcp_telemetry.trace_mcp_tool_call("recovery_tool", {}, {"success": True}) as tool_span:
                pass

    def test_schema_evolution_tracking(self):
        """Test schema evolution tracking."""
        server_path = "/path/to/mcp/server"
        
        # Initial schema
        initial_schema = {
            "tools": [{"name": "tool1"}],
            "resources": [{"name": "resource1"}]
        }
        
        # Updated schema
        updated_schema = {
            "tools": [{"name": "tool1"}, {"name": "tool2"}],
            "resources": [{"name": "resource1"}, {"name": "resource2"}]
        }
        
        # Track schema changes
        with self.mcp_telemetry.trace_mcp_schema_discovery(server_path, initial_schema) as initial_span:
            self.assertEqual(initial_span.get_attribute("schema.tools_count"), 1)
            self.assertEqual(initial_span.get_attribute("schema.resources_count"), 1)
        
        with self.mcp_telemetry.trace_mcp_schema_discovery(server_path, updated_schema) as updated_span:
            self.assertEqual(updated_span.get_attribute("schema.tools_count"), 2)
            self.assertEqual(updated_span.get_attribute("schema.resources_count"), 2)


def main():
    """Run all MCP telemetry tests."""
    print("🧪 Testing MCP Telemetry Implementation")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMCPTelemetryManager))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPTelemetryIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All MCP telemetry tests passed!")
        return True
    else:
        print("❌ Some MCP telemetry tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 