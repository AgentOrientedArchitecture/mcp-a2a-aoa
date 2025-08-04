#!/usr/bin/env python3
"""Unit tests for A2A instrumentation."""

import json
import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from telemetry.a2a_instrumentation import A2ATelemetryManager
from opentelemetry.sdk.trace import TracerProvider


class TestA2ATelemetryManager(unittest.TestCase):
    """Test cases for A2ATelemetryManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracer_provider = TracerProvider()
        self.a2a_telemetry = A2ATelemetryManager(self.tracer_provider)

    def test_initialization(self):
        """Test A2A telemetry manager initialization."""
        self.assertIsNotNone(self.a2a_telemetry)
        self.assertIsNotNone(self.a2a_telemetry.tracer)
        self.assertEqual(self.a2a_telemetry.tracer_provider, self.tracer_provider)

    def test_trace_agent_discovery(self):
        """Test agent discovery tracing."""
        agent_name = "test_agent"
        endpoint = "http://localhost:8001"

        with self.a2a_telemetry.trace_agent_discovery(agent_name, endpoint) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("agent.name"), agent_name)
            self.assertEqual(span.get_attribute("agent.endpoint"), endpoint)
            self.assertEqual(span.get_attribute("discovery.method"), "http")
            self.assertEqual(span.get_attribute("protocol"), "a2a")

    def test_trace_agent_communication(self):
        """Test inter-agent communication tracing."""
        from_agent = "product_agent"
        to_agent = "inventory_agent"
        message_type = "query"

        with self.a2a_telemetry.trace_agent_communication(from_agent, to_agent, message_type) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("from.agent"), from_agent)
            self.assertEqual(span.get_attribute("to.agent"), to_agent)
            self.assertEqual(span.get_attribute("message.type"), message_type)
            self.assertEqual(span.get_attribute("protocol"), "a2a")
            self.assertEqual(span.get_attribute("communication.direction"), "outbound")

    def test_trace_capability_invocation(self):
        """Test capability invocation tracing."""
        agent_name = "test_agent"
        capability = "search_products"
        args = {"query": "laptop", "category": "electronics"}

        with self.a2a_telemetry.trace_capability_invocation(agent_name, capability, args) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("agent.name"), agent_name)
            self.assertEqual(span.get_attribute("capability.name"), capability)
            self.assertIsNotNone(span.get_attribute("capability.args"))
            self.assertIsNotNone(span.get_attribute("invocation.timestamp"))

    def test_trace_task_execution(self):
        """Test task execution tracing."""
        agent_name = "test_agent"
        task_id = "task_123"
        task_type = "search"

        with self.a2a_telemetry.trace_task_execution(agent_name, task_id, task_type) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("agent.name"), agent_name)
            self.assertEqual(span.get_attribute("task.id"), task_id)
            self.assertEqual(span.get_attribute("task.type"), task_type)
            self.assertIsNotNone(span.get_attribute("execution.timestamp"))

    def test_trace_agent_registration(self):
        """Test agent registration tracing."""
        agent_name = "test_agent"
        endpoint = "http://localhost:8001"
        capabilities = ["search", "analyze"]

        with self.a2a_telemetry.trace_agent_registration(agent_name, endpoint, capabilities) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("agent.name"), agent_name)
            self.assertEqual(span.get_attribute("agent.endpoint"), endpoint)
            self.assertIsNotNone(span.get_attribute("agent.capabilities"))
            self.assertIsNotNone(span.get_attribute("registration.timestamp"))

    def test_trace_error(self):
        """Test error tracing."""
        agent_name = "test_agent"
        error_type = "connection_error"
        error_message = "Failed to connect to agent"

        with self.a2a_telemetry.trace_error(agent_name, error_type, error_message) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("agent.name"), agent_name)
            self.assertEqual(span.get_attribute("error.type"), error_type)
            self.assertEqual(span.get_attribute("error.message"), error_message)
            self.assertIsNotNone(span.get_attribute("error.timestamp"))

    def test_trace_performance_metrics(self):
        """Test performance metrics tracing."""
        agent_name = "test_agent"
        operation = "search"
        duration = 1.5

        with self.a2a_telemetry.trace_performance_metrics(agent_name, operation, duration) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("agent.name"), agent_name)
            self.assertEqual(span.get_attribute("operation.type"), operation)
            self.assertEqual(span.get_attribute("performance.duration_ms"), duration * 1000)
            self.assertIsNotNone(span.get_attribute("performance.timestamp"))

    def test_create_span_with_context(self):
        """Test custom span creation."""
        span_name = "custom.operation"
        attributes = {"custom.attr": "value", "test.attr": 123}

        with self.a2a_telemetry.create_span_with_context(span_name, **attributes) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("custom.attr"), "value")
            self.assertEqual(span.get_attribute("test.attr"), 123)

    def test_span_context_manager(self):
        """Test span context manager behavior."""
        agent_name = "test_agent"
        operation = "test_operation"

        # Test normal execution
        with self.a2a_telemetry.trace_task_execution(agent_name, "task_123", operation) as span:
            # Verify span is active
            self.assertIsNotNone(span)
            # Simulate some work
            time.sleep(0.01)

        # Test exception handling
        try:
            with self.a2a_telemetry.trace_task_execution(agent_name, "task_456", operation) as span:
                raise ValueError("Test exception")
        except ValueError:
            # Exception should be re-raised
            pass

    def test_complex_attributes(self):
        """Test complex attribute types."""
        agent_name = "test_agent"
        complex_args = {
            "list_data": [1, 2, 3],
            "dict_data": {"key": "value"},
            "nested": {"level1": {"level2": "value"}}
        }

        with self.a2a_telemetry.trace_capability_invocation(agent_name, "complex_capability", complex_args) as span:
            self.assertIsNotNone(span)
            # Verify complex attributes are serialized
            args_attr = span.get_attribute("capability.args")
            self.assertIsNotNone(args_attr)
            # Should be JSON string
            self.assertIsInstance(args_attr, str)

    def test_multiple_concurrent_spans(self):
        """Test multiple concurrent spans."""
        agent_name = "test_agent"
        
        # Create multiple spans concurrently
        spans = []
        for i in range(5):
            span = self.a2a_telemetry.trace_task_execution(
                agent_name, f"task_{i}", "concurrent_test"
            )
            spans.append(span)

        # Verify all spans are created
        self.assertEqual(len(spans), 5)
        for span in spans:
            self.assertIsNotNone(span)

        # Clean up spans
        for span in spans:
            span.__exit__(None, None, None)


class TestA2ATelemetryIntegration(unittest.TestCase):
    """Integration tests for A2A telemetry."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracer_provider = TracerProvider()
        self.a2a_telemetry = A2ATelemetryManager(self.tracer_provider)

    def test_end_to_end_agent_communication(self):
        """Test end-to-end agent communication tracing."""
        # Simulate agent discovery
        with self.a2a_telemetry.trace_agent_discovery("product_agent", "http://localhost:8001") as discovery_span:
            # Simulate agent registration
            with self.a2a_telemetry.trace_agent_registration(
                "product_agent", "http://localhost:8001", ["search", "analyze"]
            ) as registration_span:
                # Simulate capability invocation
                with self.a2a_telemetry.trace_capability_invocation(
                    "product_agent", "search_products", {"query": "laptop"}
                ) as capability_span:
                    # Simulate inter-agent communication
                    with self.a2a_telemetry.trace_agent_communication(
                        "product_agent", "inventory_agent", "query"
                    ) as communication_span:
                        # Simulate task execution
                        with self.a2a_telemetry.trace_task_execution(
                            "product_agent", "task_123", "search"
                        ) as task_span:
                            # Verify all spans are created
                            self.assertIsNotNone(discovery_span)
                            self.assertIsNotNone(registration_span)
                            self.assertIsNotNone(capability_span)
                            self.assertIsNotNone(communication_span)
                            self.assertIsNotNone(task_span)

    def test_error_scenario_tracing(self):
        """Test error scenario tracing."""
        agent_name = "test_agent"
        
        # Simulate successful operation
        with self.a2a_telemetry.trace_task_execution(agent_name, "task_success", "operation") as success_span:
            pass

        # Simulate failed operation
        try:
            with self.a2a_telemetry.trace_task_execution(agent_name, "task_failure", "operation") as failure_span:
                raise RuntimeError("Simulated error")
        except RuntimeError:
            # Error should be traced
            with self.a2a_telemetry.trace_error(agent_name, "runtime_error", "Simulated error") as error_span:
                self.assertIsNotNone(error_span)

    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        agent_name = "test_agent"
        operation = "complex_operation"
        
        # Simulate operation with timing
        start_time = time.time()
        with self.a2a_telemetry.trace_task_execution(agent_name, "task_perf", operation) as task_span:
            # Simulate work
            time.sleep(0.1)
        
        duration = time.time() - start_time
        
        # Trace performance metrics
        with self.a2a_telemetry.trace_performance_metrics(agent_name, operation, duration) as perf_span:
            self.assertIsNotNone(perf_span)
            self.assertIsNotNone(perf_span.get_attribute("performance.duration_ms"))


def main():
    """Run all A2A telemetry tests."""
    print("🧪 Testing A2A Telemetry Implementation")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestA2ATelemetryManager))
    suite.addTests(loader.loadTestsFromTestCase(TestA2ATelemetryIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All A2A telemetry tests passed!")
        return True
    else:
        print("❌ Some A2A telemetry tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 