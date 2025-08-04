#!/usr/bin/env python3
"""Unit tests for business metrics."""

import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from telemetry.business_metrics import BusinessMetricsManager
from opentelemetry.sdk.trace import TracerProvider


class TestBusinessMetricsManager(unittest.TestCase):
    """Test cases for BusinessMetricsManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracer_provider = TracerProvider()
        self.business_metrics = BusinessMetricsManager(self.tracer_provider)

    def test_initialization(self):
        """Test business metrics manager initialization."""
        self.assertIsNotNone(self.business_metrics)
        self.assertIsNotNone(self.business_metrics.tracer)
        self.assertEqual(self.business_metrics.tracer_provider, self.tracer_provider)

    def test_trace_product_search(self):
        """Test product search metrics tracing."""
        query = "laptop"
        results_count = 5
        search_time = 0.5

        with self.business_metrics.trace_product_search(query, results_count, search_time) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("search.query"), query)
            self.assertEqual(span.get_attribute("search.results_count"), results_count)
            self.assertEqual(span.get_attribute("search.duration_ms"), search_time * 1000)
            self.assertEqual(span.get_attribute("business.domain"), "ecommerce")
            self.assertEqual(span.get_attribute("operation.type"), "product_search")
            self.assertIsNotNone(span.get_attribute("search.timestamp"))

    def test_trace_inventory_check(self):
        """Test inventory check metrics tracing."""
        product_id = "PROD001"
        stock_level = 15
        threshold = 10

        with self.business_metrics.trace_inventory_check(product_id, stock_level, threshold) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("product.id"), product_id)
            self.assertEqual(span.get_attribute("stock.level"), stock_level)
            self.assertEqual(span.get_attribute("stock.threshold"), threshold)
            self.assertEqual(span.get_attribute("stock.status"), "adequate")
            self.assertEqual(span.get_attribute("business.domain"), "inventory")
            self.assertEqual(span.get_attribute("operation.type"), "inventory_check")
            self.assertIsNotNone(span.get_attribute("check.timestamp"))

    def test_trace_inventory_check_low_stock(self):
        """Test inventory check with low stock."""
        product_id = "PROD002"
        stock_level = 5
        threshold = 10

        with self.business_metrics.trace_inventory_check(product_id, stock_level, threshold) as span:
            self.assertIsNotNone(span)
            self.assertEqual(span.get_attribute("stock.status"), "low")

    def test_trace_sales_analysis(self):
        """Test sales analysis metrics tracing."""
        period = "monthly"
        revenue = 50000.0
        transaction_count = 250

        with self.business_metrics.trace_sales_analysis(period, revenue, transaction_count) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("analysis.period"), period)
            self.assertEqual(span.get_attribute("revenue.total"), revenue)
            self.assertEqual(span.get_attribute("transactions.count"), transaction_count)
            self.assertEqual(span.get_attribute("revenue.average"), revenue / transaction_count)
            self.assertEqual(span.get_attribute("business.domain"), "sales")
            self.assertEqual(span.get_attribute("operation.type"), "sales_analysis")
            self.assertIsNotNone(span.get_attribute("analysis.timestamp"))

    def test_trace_sales_analysis_zero_transactions(self):
        """Test sales analysis with zero transactions."""
        period = "daily"
        revenue = 0.0
        transaction_count = 0

        with self.business_metrics.trace_sales_analysis(period, revenue, transaction_count) as span:
            self.assertIsNotNone(span)
            self.assertEqual(span.get_attribute("revenue.average"), 0)

    def test_trace_customer_insight(self):
        """Test customer insight metrics tracing."""
        customer_id = "CUST123"
        insight_type = "purchase_pattern"
        confidence = 0.85

        with self.business_metrics.trace_customer_insight(customer_id, insight_type, confidence) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("customer.id"), customer_id)
            self.assertEqual(span.get_attribute("insight.type"), insight_type)
            self.assertEqual(span.get_attribute("insight.confidence"), confidence)
            self.assertEqual(span.get_attribute("business.domain"), "customer_analytics")
            self.assertEqual(span.get_attribute("operation.type"), "customer_insight")
            self.assertIsNotNone(span.get_attribute("insight.timestamp"))

    def test_trace_recommendation_generation(self):
        """Test recommendation generation metrics tracing."""
        user_id = "USER456"
        recommendation_count = 10
        algorithm = "collaborative_filtering"

        with self.business_metrics.trace_recommendation_generation(user_id, recommendation_count, algorithm) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("user.id"), user_id)
            self.assertEqual(span.get_attribute("recommendations.count"), recommendation_count)
            self.assertEqual(span.get_attribute("algorithm.name"), algorithm)
            self.assertEqual(span.get_attribute("business.domain"), "recommendations")
            self.assertEqual(span.get_attribute("operation.type"), "recommendation_generation")
            self.assertIsNotNone(span.get_attribute("generation.timestamp"))

    def test_trace_price_analysis(self):
        """Test price analysis metrics tracing."""
        product_category = "electronics"
        price_range = (100, 1000)
        analysis_type = "trend"

        with self.business_metrics.trace_price_analysis(product_category, price_range, analysis_type) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("product.category"), product_category)
            self.assertEqual(span.get_attribute("price.min"), price_range[0])
            self.assertEqual(span.get_attribute("price.max"), price_range[1])
            self.assertEqual(span.get_attribute("analysis.type"), analysis_type)
            self.assertEqual(span.get_attribute("business.domain"), "pricing")
            self.assertEqual(span.get_attribute("operation.type"), "price_analysis")
            self.assertIsNotNone(span.get_attribute("analysis.timestamp"))

    def test_trace_supply_chain_event(self):
        """Test supply chain event metrics tracing."""
        event_type = "delivery_delay"
        location = "warehouse_west"
        impact_level = "high"

        with self.business_metrics.trace_supply_chain_event(event_type, location, impact_level) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("event.type"), event_type)
            self.assertEqual(span.get_attribute("event.location"), location)
            self.assertEqual(span.get_attribute("event.impact_level"), impact_level)
            self.assertEqual(span.get_attribute("business.domain"), "supply_chain")
            self.assertEqual(span.get_attribute("operation.type"), "supply_chain_event")
            self.assertIsNotNone(span.get_attribute("event.timestamp"))

    def test_trace_business_kpi(self):
        """Test business KPI metrics tracing."""
        kpi_name = "conversion_rate"
        kpi_value = 0.15
        target_value = 0.20

        with self.business_metrics.trace_business_kpi(kpi_name, kpi_value, target_value) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("kpi.name"), kpi_name)
            self.assertEqual(span.get_attribute("kpi.value"), kpi_value)
            self.assertEqual(span.get_attribute("kpi.target"), target_value)
            self.assertEqual(span.get_attribute("kpi.performance_ratio"), kpi_value / target_value)
            self.assertEqual(span.get_attribute("kpi.status"), "below_target")
            self.assertEqual(span.get_attribute("business.domain"), "kpi_tracking")
            self.assertEqual(span.get_attribute("operation.type"), "kpi_measurement")
            self.assertIsNotNone(span.get_attribute("measurement.timestamp"))

    def test_trace_business_kpi_above_target(self):
        """Test business KPI above target."""
        kpi_name = "revenue_growth"
        kpi_value = 0.25
        target_value = 0.20

        with self.business_metrics.trace_business_kpi(kpi_name, kpi_value, target_value) as span:
            self.assertIsNotNone(span)
            self.assertEqual(span.get_attribute("kpi.status"), "above_target")

    def test_trace_business_kpi_zero_target(self):
        """Test business KPI with zero target."""
        kpi_name = "new_metric"
        kpi_value = 0.10
        target_value = 0.0

        with self.business_metrics.trace_business_kpi(kpi_name, kpi_value, target_value) as span:
            self.assertIsNotNone(span)
            self.assertEqual(span.get_attribute("kpi.performance_ratio"), 0)

    def test_create_span_with_context(self):
        """Test custom span creation."""
        span_name = "business.custom.metric"
        attributes = {"custom.attr": "value", "test.attr": 123}

        with self.business_metrics.create_span_with_context(span_name, **attributes) as span:
            self.assertIsNotNone(span)
            # Verify span attributes
            self.assertEqual(span.get_attribute("custom.attr"), "value")
            self.assertEqual(span.get_attribute("test.attr"), 123)

    def test_complex_business_scenarios(self):
        """Test complex business scenarios."""
        # Simulate a complex e-commerce scenario
        with self.business_metrics.trace_product_search("gaming laptop", 3, 0.8) as search_span:
            # Simulate inventory check for found products
            with self.business_metrics.trace_inventory_check("LAPTOP001", 5, 10) as inventory_span:
                # Simulate price analysis
                with self.business_metrics.trace_price_analysis("gaming", (800, 2000), "competitive") as price_span:
                    # Simulate customer insight
                    with self.business_metrics.trace_customer_insight("CUST789", "preference", 0.92) as insight_span:
                        # Simulate recommendation
                        with self.business_metrics.trace_recommendation_generation("CUST789", 5, "ml_based") as rec_span:
                            # Verify all spans are created
                            self.assertIsNotNone(search_span)
                            self.assertIsNotNone(inventory_span)
                            self.assertIsNotNone(price_span)
                            self.assertIsNotNone(insight_span)
                            self.assertIsNotNone(rec_span)

    def test_performance_metrics_integration(self):
        """Test performance metrics integration."""
        # Simulate operation with timing
        start_time = time.time()
        with self.business_metrics.trace_product_search("performance_test", 10, 0.0) as span:
            # Simulate work
            time.sleep(0.1)
        
        # Update span with actual duration
        actual_duration = time.time() - start_time
        span.set_attribute("search.actual_duration_ms", actual_duration * 1000)
        
        self.assertIsNotNone(span.get_attribute("search.actual_duration_ms"))

    def test_error_scenarios(self):
        """Test error scenarios in business metrics."""
        # Test with invalid parameters
        with self.business_metrics.trace_product_search("", 0, -1) as span:
            self.assertIsNotNone(span)
            self.assertEqual(span.get_attribute("search.query"), "")
            self.assertEqual(span.get_attribute("search.results_count"), 0)

        # Test with extreme values
        with self.business_metrics.trace_sales_analysis("yearly", 999999999.99, 1000000) as span:
            self.assertIsNotNone(span)
            self.assertIsNotNone(span.get_attribute("revenue.average"))

    def test_multiple_concurrent_operations(self):
        """Test multiple concurrent business operations."""
        operations = [
            ("product_search", "laptop", 5, 0.5),
            ("inventory_check", "PROD001", 15, 10),
            ("sales_analysis", "daily", 1000.0, 10),
            ("customer_insight", "CUST123", "behavior", 0.8),
            ("recommendation_generation", "USER456", 5, "collaborative")
        ]
        
        spans = []
        for op_type, *args in operations:
            if op_type == "product_search":
                span = self.business_metrics.trace_product_search(*args)
            elif op_type == "inventory_check":
                span = self.business_metrics.trace_inventory_check(*args)
            elif op_type == "sales_analysis":
                span = self.business_metrics.trace_sales_analysis(*args)
            elif op_type == "customer_insight":
                span = self.business_metrics.trace_customer_insight(*args)
            elif op_type == "recommendation_generation":
                span = self.business_metrics.trace_recommendation_generation(*args)
            spans.append(span)

        # Verify all spans are created
        self.assertEqual(len(spans), 5)
        for span in spans:
            self.assertIsNotNone(span)

        # Clean up spans
        for span in spans:
            span.__exit__(None, None, None)


class TestBusinessMetricsIntegration(unittest.TestCase):
    """Integration tests for business metrics."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracer_provider = TracerProvider()
        self.business_metrics = BusinessMetricsManager(self.tracer_provider)

    def test_end_to_end_ecommerce_workflow(self):
        """Test end-to-end e-commerce workflow."""
        # Simulate complete e-commerce workflow
        with self.business_metrics.trace_product_search("smartphone", 8, 0.6) as search_span:
            # Simulate inventory checks for found products
            for i in range(3):
                with self.business_metrics.trace_inventory_check(f"PHONE{i+1:03d}", 10+i, 5) as inventory_span:
                    # Simulate price analysis
                    with self.business_metrics.trace_price_analysis("mobile", (200, 800), "market") as price_span:
                        # Simulate customer analysis
                        with self.business_metrics.trace_customer_insight(f"CUST{i+1:03d}", "preference", 0.85+i*0.05) as insight_span:
                            # Simulate recommendations
                            with self.business_metrics.trace_recommendation_generation(f"USER{i+1:03d}", 3, "ml_based") as rec_span:
                                pass

    def test_supply_chain_monitoring(self):
        """Test supply chain monitoring workflow."""
        # Simulate supply chain events
        events = [
            ("order_received", "warehouse_east", "low"),
            ("inventory_update", "warehouse_west", "medium"),
            ("delivery_delay", "distribution_center", "high"),
            ("quality_check", "warehouse_central", "low")
        ]
        
        for event_type, location, impact in events:
            with self.business_metrics.trace_supply_chain_event(event_type, location, impact) as span:
                self.assertIsNotNone(span)
                self.assertEqual(span.get_attribute("event.type"), event_type)
                self.assertEqual(span.get_attribute("event.location"), location)
                self.assertEqual(span.get_attribute("event.impact_level"), impact)

    def test_kpi_tracking_scenario(self):
        """Test KPI tracking scenario."""
        # Simulate various KPIs
        kpis = [
            ("conversion_rate", 0.15, 0.20),
            ("average_order_value", 85.50, 75.00),
            ("customer_satisfaction", 4.2, 4.0),
            ("inventory_turnover", 6.5, 5.0),
            ("return_rate", 0.08, 0.10)
        ]
        
        for kpi_name, kpi_value, target_value in kpis:
            with self.business_metrics.trace_business_kpi(kpi_name, kpi_value, target_value) as span:
                self.assertIsNotNone(span)
                self.assertEqual(span.get_attribute("kpi.name"), kpi_name)
                self.assertEqual(span.get_attribute("kpi.value"), kpi_value)
                self.assertEqual(span.get_attribute("kpi.target"), target_value)

    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        # Simulate performance-critical operations
        operations = [
            ("product_search", "complex_query", 0.8),
            ("inventory_check", "bulk_check", 1.2),
            ("sales_analysis", "comprehensive", 2.5),
            ("customer_insight", "deep_analysis", 1.8),
            ("recommendation_generation", "real_time", 0.3)
        ]
        
        for operation, description, duration in operations:
            with self.business_metrics.create_span_with_context(
                f"business.performance.{operation}",
                operation=operation,
                description=description,
                duration_ms=duration * 1000
            ) as span:
                self.assertIsNotNone(span)
                self.assertEqual(span.get_attribute("operation"), operation)
                self.assertEqual(span.get_attribute("description"), description)
                self.assertEqual(span.get_attribute("duration_ms"), duration * 1000)


def main():
    """Run all business metrics tests."""
    print("🧪 Testing Business Metrics Implementation")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessMetricsManager))
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessMetricsIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All business metrics tests passed!")
        return True
    else:
        print("❌ Some business metrics tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 