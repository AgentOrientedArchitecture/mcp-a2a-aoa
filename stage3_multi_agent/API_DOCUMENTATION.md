# **📚 API Documentation - Telemetry System**

## **📋 Overview**

This document provides comprehensive API documentation for the OpenTelemetry + SMOL Agents + Arize AI Phoenix telemetry system, including all telemetry managers, agent capabilities, and monitoring endpoints.

---

## **🏗️ Architecture Components**

### **Core Telemetry Managers**

#### **1. TelemetryManager**
Main orchestrator for all telemetry components.

```python
from telemetry import TelemetryManager

# Initialize telemetry manager
telemetry_manager = TelemetryManager()

# Get individual managers
smol_telemetry = telemetry_manager.get_smol_instrumentation()
a2a_telemetry = telemetry_manager.get_a2a_instrumentation()
mcp_telemetry = telemetry_manager.get_mcp_instrumentation()
business_metrics = telemetry_manager.get_business_metrics()
performance_monitor = telemetry_manager.get_performance_monitoring()
```

#### **2. SMOLTelemetryManager**
Handles SMOL agents instrumentation and tracing.

```python
from telemetry.smol_instrumentation import SMOLTelemetryManager

# Initialize
smol_telemetry = SMOLTelemetryManager(tracer_provider)

# Create agent spans
with smol_telemetry.create_agent_span(agent_name, operation) as span:
    # Agent operations
    pass

# Trace agent execution
with smol_telemetry.trace_agent_execution(agent_name, task_id, operation) as span:
    # Agent execution
    pass
```

#### **3. A2ATelemetryManager**
Handles A2A (Agent-to-Agent) communication tracing.

```python
from telemetry.a2a_instrumentation import A2ATelemetryManager

# Initialize
a2a_telemetry = A2ATelemetryManager(tracer_provider)

# Trace agent discovery
with a2a_telemetry.trace_agent_discovery(agent_name, endpoint) as span:
    # Discovery operations
    pass

# Trace inter-agent communication
with a2a_telemetry.trace_agent_communication(from_agent, to_agent, message_type) as span:
    # Communication operations
    pass
```

#### **4. MCPTelemetryManager**
Handles MCP (Model Context Protocol) interactions.

```python
from telemetry.mcp_instrumentation import MCPTelemetryManager

# Initialize
mcp_telemetry = MCPTelemetryManager(tracer_provider)

# Trace tool calls
with mcp_telemetry.trace_mcp_tool_call(tool_name, args, result) as span:
    # Tool execution
    pass

# Trace server connections
with mcp_telemetry.trace_mcp_server_connection(server_path, status) as span:
    # Connection operations
    pass
```

#### **5. BusinessMetricsManager**
Handles business-specific metrics and KPIs.

```python
from telemetry.business_metrics import BusinessMetricsManager

# Initialize
business_metrics = BusinessMetricsManager(tracer_provider)

# Trace product search
with business_metrics.trace_product_search(query, results_count, search_time) as span:
    # Search operations
    pass

# Trace inventory checks
with business_metrics.trace_inventory_check(product_id, stock_level, threshold) as span:
    # Inventory operations
    pass
```

---

## **🤖 Enhanced Agent APIs**

### **EnhancedBaseA2AAgent**

Base class for all enhanced A2A agents with telemetry integration.

```python
from a2a_protocol.base_agent import EnhancedBaseA2AAgent

class MyEnhancedAgent(EnhancedBaseA2AAgent):
    def __init__(self):
        super().__init__(
            agent_name="My Agent",
            agent_description="Enhanced agent with telemetry",
            agent_card_path="path/to/agent_card.json",
            smol_agent=None,
            enable_telemetry=True,
            phoenix_endpoint="http://phoenix:4317"
        )
    
    def setup_custom_capabilities(self):
        """Register custom capabilities with telemetry."""
        self.register_capability("my_capability", self._handle_my_capability)
    
    async def _handle_my_capability(self, args):
        """Handle capability with telemetry."""
        if self.telemetry:
            with self.telemetry.get_business_metrics().create_span_with_context(
                "business.my_capability",
                **args
            ) as span:
                # Capability implementation
                return {"result": "success"}
        else:
            # Fallback without telemetry
            return {"result": "success"}
```

### **Agent Capabilities**

#### **Product Agent Capabilities**

```python
# Search products with telemetry
async def search_products(self, args):
    """Search products with comprehensive telemetry."""
    query = args.get("query", "")
    category = args.get("category", "")
    
    if self.telemetry:
        with self.telemetry.get_business_metrics().trace_product_search(
            query, 0, 0.0
        ) as span:
            # Search implementation
            results = await self._perform_search(query, category)
            span.set_attribute("search.results_count", len(results))
            return {"results": results}
    else:
        return {"results": await self._perform_search(query, category)}

# Analyze prices with telemetry
async def analyze_prices(self, args):
    """Analyze product prices with telemetry."""
    category = args.get("category", "")
    price_range = args.get("price_range", (0, 1000))
    
    if self.telemetry:
        with self.telemetry.get_business_metrics().trace_price_analysis(
            category, price_range, "analysis"
        ) as span:
            # Analysis implementation
            analysis = await self._analyze_prices(category, price_range)
            return {"analysis": analysis}
    else:
        return {"analysis": await self._analyze_prices(category, price_range)}
```

#### **Inventory Agent Capabilities**

```python
# Check stock with telemetry
async def check_stock(self, args):
    """Check inventory stock with telemetry."""
    product_id = args.get("product_id", "")
    threshold = args.get("threshold", 10)
    
    if self.telemetry:
        with self.telemetry.get_business_metrics().trace_inventory_check(
            product_id, 0, threshold
        ) as span:
            # Stock check implementation
            stock_level = await self._check_stock_level(product_id)
            span.set_attribute("stock.level", stock_level)
            return {"stock_level": stock_level, "threshold": threshold}
    else:
        stock_level = await self._check_stock_level(product_id)
        return {"stock_level": stock_level, "threshold": threshold}

# Update inventory with telemetry
async def update_inventory(self, args):
    """Update inventory with telemetry."""
    product_id = args.get("product_id", "")
    quantity = args.get("quantity", 0)
    operation = args.get("operation", "add")
    
    if self.telemetry:
        with self.telemetry.get_business_metrics().create_span_with_context(
            "business.inventory.update",
            product_id=product_id,
            operation=operation,
            quantity=quantity
        ) as span:
            # Update implementation
            result = await self._update_inventory(product_id, quantity, operation)
            return {"result": result}
    else:
        result = await self._update_inventory(product_id, quantity, operation)
        return {"result": result}
```

#### **Sales Agent Capabilities**

```python
# Sales analysis with telemetry
async def sales_analysis(self, args):
    """Perform sales analysis with telemetry."""
    period = args.get("period", "monthly")
    revenue = args.get("revenue", 0.0)
    transaction_count = args.get("transaction_count", 0)
    
    if self.telemetry:
        with self.telemetry.get_business_metrics().trace_sales_analysis(
            period, revenue, transaction_count
        ) as span:
            # Analysis implementation
            analysis = await self._analyze_sales(period, revenue, transaction_count)
            return {"analysis": analysis}
    else:
        analysis = await self._analyze_sales(period, revenue, transaction_count)
        return {"analysis": analysis}

# Revenue tracking with telemetry
async def revenue_tracking(self, args):
    """Track revenue with telemetry."""
    time_period = args.get("time_period", "daily")
    
    if self.telemetry:
        with self.telemetry.get_business_metrics().create_span_with_context(
            "business.sales.revenue_tracking",
            time_period=time_period
        ) as span:
            # Tracking implementation
            revenue_data = await self._track_revenue(time_period)
            span.set_attribute("revenue.total", revenue_data.get("total", 0))
            return {"revenue_data": revenue_data}
    else:
        revenue_data = await self._track_revenue(time_period)
        return {"revenue_data": revenue_data}
```

---

## **📊 Monitoring Endpoints**

### **Health Check Endpoints**

#### **Agent Health Checks**

```bash
# Product Agent Health Check
curl -f http://localhost:8001/.well-known/agent-card.json

# Inventory Agent Health Check
curl -f http://localhost:8002/.well-known/agent-card.json

# Sales Agent Health Check
curl -f http://localhost:8003/.well-known/agent-card.json

# MCP Server Health Check
curl -f http://localhost:8000/health
```

#### **Phoenix Health Check**

```bash
# Phoenix UI Health Check
curl -f http://localhost:6006/health

# Phoenix Collector Health Check
curl -f http://localhost:4317/health
```

### **Telemetry Endpoints**

#### **OTLP HTTP Endpoint**

```bash
# Send traces to Phoenix
POST http://localhost:4317/v1/traces
Content-Type: application/x-protobuf

# Example trace data
{
  "resourceSpans": [
    {
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "a2a-multi-agent"}}
        ]
      },
      "scopeSpans": [
        {
          "scope": {"name": "telemetry"},
          "spans": [
            {
              "traceId": "1234567890abcdef",
              "spanId": "abcdef1234567890",
              "name": "agent.operation",
              "startTimeUnixNano": "1640995200000000000",
              "endTimeUnixNano": "1640995201000000000"
            }
          ]
        }
      ]
    }
  ]
}
```

#### **Phoenix UI Endpoints**

```bash
# Access Phoenix UI
GET http://localhost:6006

# Query traces
GET http://localhost:6006/api/v1/traces

# Query metrics
GET http://localhost:6006/api/v1/metrics

# Query logs
GET http://localhost:6006/api/v1/logs
```

---

## **🔧 Configuration APIs**

### **Environment Variables**

```bash
# Phoenix Configuration
PHOENIX_PROJECT_NAME=a2a-multi-agent
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317
ENABLE_TELEMETRY=true

# Agent Configuration
A2A_HOST=0.0.0.0
DISCOVERY_METHOD=docker
LOG_LEVEL=INFO

# Performance Configuration
PERFORMANCE_MONITORING_INTERVAL=30
ENABLE_SYSTEM_METRICS=true

# Error Handling Configuration
ENABLE_ERROR_REPORTING=true
ERROR_REPORTING_LEVEL=WARNING
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=5
```

### **Docker Configuration**

```yaml
# docker-compose-with-phoenix.yml
version: '3.8'

services:
  phoenix:
    image: arizephoenix/phoenix:latest
    ports:
      - "6006:6006"  # Phoenix UI
      - "4317:4317"  # OTLP HTTP receiver
    environment:
      - PHOENIX_PROJECT_NAME=a2a-multi-agent
    volumes:
      - phoenix_data:/phoenix/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6006/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  enhanced-product-agent:
    build:
      context: ..
      dockerfile: stage3_multi_agent/product.Dockerfile
    ports:
      - "8001:8001"
    environment:
      - ENABLE_TELEMETRY=true
      - PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317
    depends_on:
      phoenix:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/.well-known/agent-card.json"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## **🧪 Testing APIs**

### **Test Endpoints**

```bash
# Run comprehensive tests
python run_telemetry_tests.py

# Run specific test categories
python telemetry/tests/test_smol_instrumentation.py
python telemetry/tests/test_a2a_instrumentation.py
python telemetry/tests/test_mcp_instrumentation.py
python telemetry/tests/test_business_metrics.py

# Test telemetry initialization
python test_telemetry.py

# Test enhanced agents
python test_all_agents.py
```

### **Test Configuration**

```python
# Test telemetry manager
from telemetry import TelemetryManager
from opentelemetry.sdk.trace import TracerProvider

# Initialize for testing
tracer_provider = TracerProvider()
telemetry_manager = TelemetryManager()

# Test span creation
with telemetry_manager.get_smol_instrumentation().create_agent_span(
    "test_agent", "test_operation"
) as span:
    span.set_attribute("test.attribute", "test_value")
    # Test operations
    pass
```

---

## **📈 Performance APIs**

### **Performance Monitoring**

```python
from telemetry.performance_monitoring import PerformanceMonitor

# Initialize performance monitor
performance_monitor = PerformanceMonitor(tracer_provider)

# Start monitoring
performance_monitor.start_monitoring(agent_name="test_agent")

# Monitor specific operation
with performance_monitor.trace_operation("test_operation") as span:
    # Operation implementation
    pass

# Stop monitoring
performance_monitor.stop_monitoring()
```

### **Resource Monitoring**

```python
import psutil

# Monitor system resources
cpu_percent = psutil.cpu_percent()
memory_percent = psutil.virtual_memory().percent
disk_percent = psutil.disk_usage('/').percent

# Create resource span
with business_metrics.create_span_with_context(
    "system.resources",
    cpu_percent=cpu_percent,
    memory_percent=memory_percent,
    disk_percent=disk_percent
) as span:
    # Resource monitoring
    pass
```

---

## **🔍 Debugging APIs**

### **Debug Logging**

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('opentelemetry').setLevel(logging.DEBUG)
logging.getLogger('telemetry').setLevel(logging.DEBUG)

# Debug telemetry initialization
telemetry_manager = TelemetryManager()
print(f"Telemetry initialized: {telemetry_manager is not None}")
```

### **Span Inspection**

```python
# Inspect span attributes
with smol_telemetry.create_agent_span("test_agent", "test_operation") as span:
    # Add custom attributes
    span.set_attribute("custom.attr", "custom_value")
    span.set_attribute("debug.enabled", True)
    
    # Inspect span
    print(f"Span name: {span.name}")
    print(f"Span attributes: {span.attributes}")
```

---

## **🚀 Deployment APIs**

### **Deployment Script**

```bash
# Deploy with telemetry
./deploy_with_telemetry.sh deploy

# Check status
./deploy_with_telemetry.sh status

# View logs
./deploy_with_telemetry.sh logs

# Health check
./deploy_with_telemetry.sh health

# Run tests
./deploy_with_telemetry.sh test

# Cleanup
./deploy_with_telemetry.sh cleanup
```

### **Docker Commands**

```bash
# Build images
docker build -f product.Dockerfile -t aoa-enhanced-product-agent .
docker build -f inventory.Dockerfile -t aoa-enhanced-inventory-agent .
docker build -f sales.Dockerfile -t aoa-enhanced-sales-agent .

# Start services
docker-compose -f docker-compose-with-phoenix.yml up -d

# Check status
docker-compose -f docker-compose-with-phoenix.yml ps

# View logs
docker-compose -f docker-compose-with-phoenix.yml logs -f

# Scale services
docker-compose -f docker-compose-with-phoenix.yml up -d --scale enhanced-product-agent=3
```

---

## **📊 Metrics and KPIs**

### **Business Metrics**

```python
# Product search metrics
with business_metrics.trace_product_search(query, results_count, search_time) as span:
    span.set_attribute("search.query", query)
    span.set_attribute("search.results_count", results_count)
    span.set_attribute("search.duration_ms", search_time * 1000)

# Inventory metrics
with business_metrics.trace_inventory_check(product_id, stock_level, threshold) as span:
    span.set_attribute("product.id", product_id)
    span.set_attribute("stock.level", stock_level)
    span.set_attribute("stock.threshold", threshold)
    span.set_attribute("stock.status", "adequate" if stock_level >= threshold else "low")

# Sales metrics
with business_metrics.trace_sales_analysis(period, revenue, transaction_count) as span:
    span.set_attribute("analysis.period", period)
    span.set_attribute("revenue.total", revenue)
    span.set_attribute("transactions.count", transaction_count)
    span.set_attribute("revenue.average", revenue / transaction_count if transaction_count > 0 else 0)
```

### **Performance Metrics**

```python
# Response time metrics
with performance_monitor.trace_operation("api_call") as span:
    start_time = time.time()
    # API call implementation
    response_time = time.time() - start_time
    span.set_attribute("response_time_ms", response_time * 1000)

# Throughput metrics
with performance_monitor.trace_operation("batch_processing") as span:
    items_processed = len(items)
    processing_time = time.time() - start_time
    throughput = items_processed / processing_time
    span.set_attribute("items_processed", items_processed)
    span.set_attribute("processing_time_ms", processing_time * 1000)
    span.set_attribute("throughput_per_second", throughput)
```

---

## **🔒 Security APIs**

### **Authentication**

```python
# API key validation
def validate_api_key(api_key):
    """Validate API key for telemetry access."""
    if not api_key:
        raise ValueError("API key required")
    # Validation logic
    return True

# Secure telemetry initialization
def initialize_secure_telemetry(api_key):
    """Initialize telemetry with security."""
    validate_api_key(api_key)
    return TelemetryManager()
```

### **Data Privacy**

```python
# Sanitize sensitive data
def sanitize_span_attributes(attributes):
    """Remove sensitive data from span attributes."""
    sensitive_keys = ['password', 'api_key', 'token', 'secret']
    sanitized = {}
    for key, value in attributes.items():
        if key.lower() not in sensitive_keys:
            sanitized[key] = value
        else:
            sanitized[key] = '[REDACTED]'
    return sanitized

# Create secure span
with smol_telemetry.create_agent_span("secure_operation", "api_call") as span:
    # Sanitize attributes before setting
    safe_attributes = sanitize_span_attributes(attributes)
    for key, value in safe_attributes.items():
        span.set_attribute(key, value)
```

---

## **📚 Error Handling APIs**

### **Error Tracing**

```python
# Trace errors with context
def trace_error(error_type, error_message, context=None):
    """Trace errors with comprehensive context."""
    if telemetry_manager:
        with telemetry_manager.get_a2a_instrumentation().trace_error(
            agent_name, error_type, error_message
        ) as span:
            if context:
                for key, value in context.items():
                    span.set_attribute(f"error.context.{key}", value)
            span.set_attribute("error.timestamp", time.time())
            return span
    return None

# Usage
try:
    # Risky operation
    result = await risky_operation()
except Exception as e:
    trace_error("operation_failed", str(e), {"operation": "risky_operation"})
    raise
```

### **Retry Logic**

```python
import asyncio
from functools import wraps

def retry_with_telemetry(max_retries=3, delay=1):
    """Retry decorator with telemetry."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        # Final attempt failed
                        trace_error("max_retries_exceeded", str(e), {
                            "function": func.__name__,
                            "attempts": max_retries
                        })
                        raise
                    else:
                        # Log retry attempt
                        trace_error("retry_attempt", str(e), {
                            "function": func.__name__,
                            "attempt": attempt + 1
                        })
                        await asyncio.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

# Usage
@retry_with_telemetry(max_retries=3, delay=1)
async def unreliable_operation():
    # Operation that might fail
    pass
```

---

## **🎯 Best Practices**

### **Span Naming**

```python
# Use consistent naming conventions
# Format: <domain>.<operation>.<sub_operation>

# Good examples
"business.product.search"
"business.inventory.check_stock"
"business.sales.analyze_revenue"
"system.performance.monitor"
"network.a2a.communication"

# Avoid
"operation"  # Too generic
"do_something"  # Not descriptive
"op123"  # Not meaningful
```

### **Attribute Naming**

```python
# Use consistent attribute naming
# Format: <category>.<attribute_name>

# Good examples
span.set_attribute("search.query", query)
span.set_attribute("search.results_count", count)
span.set_attribute("business.domain", "ecommerce")
span.set_attribute("agent.name", agent_name)
span.set_attribute("performance.duration_ms", duration_ms)

# Avoid
span.set_attribute("query", query)  # Too generic
span.set_attribute("count", count)  # Too generic
span.set_attribute("domain", "ecommerce")  # Too generic
```

### **Error Handling**

```python
# Always handle exceptions in spans
with smol_telemetry.create_agent_span("risky_operation") as span:
    try:
        # Risky operation
        result = await risky_operation()
        span.set_attribute("operation.success", True)
        return result
    except Exception as e:
        span.set_attribute("operation.success", False)
        span.set_attribute("error.message", str(e))
        span.set_attribute("error.type", type(e).__name__)
        raise
```

---

**📚 This API documentation provides comprehensive coverage of all telemetry system components, enabling developers to effectively integrate and utilize the observability features.** 