# Telemetry Guide - OpenTelemetry + Arize AI Phoenix

## Overview

This guide covers the complete telemetry implementation for the A2A multi-agent system using OpenTelemetry and Arize AI Phoenix. The system provides comprehensive observability across SMOL agents, A2A communications, MCP interactions, and business metrics.

## Quick Start

### 1. Enable Telemetry

```bash
# Set environment variables
export ENABLE_TELEMETRY=true
export PHOENIX_PROJECT_NAME=a2a-multi-agent

# Deploy with telemetry
./deploy_with_telemetry.sh deploy
```

### 2. Access Phoenix UI

```bash
# Open Phoenix dashboard
open http://localhost:6006

# View traces, metrics, and performance data
```

## Architecture

### Telemetry Stack

```
┌─────────────────────────────────────────┐
│            Agent Operations             │
├─────────────────────────────────────────┤
│         Telemetry Managers              │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ SMOL │ │ A2A  │ │ MCP  │ │ Biz  │  │
│  └──────┘ └──────┘ └──────┘ └──────┘  │
├─────────────────────────────────────────┤
│          OpenTelemetry SDK              │
├─────────────────────────────────────────┤
│        OTLP Exporter (HTTP)             │
├─────────────────────────────────────────┤
│     Phoenix Collector (Port 4317)       │
├─────────────────────────────────────────┤
│      Phoenix UI (Port 6006)             │
└─────────────────────────────────────────┘
```

### Core Components

#### 1. TelemetryManager
Central orchestrator for all telemetry operations:

```python
from telemetry import TelemetryManager

# Initialize telemetry
telemetry = TelemetryManager(
    phoenix_endpoint="http://phoenix:4317",
    project_name="a2a-multi-agent"
)

# Access specific managers
smol_telemetry = telemetry.get_smol_instrumentation()
a2a_telemetry = telemetry.get_a2a_instrumentation()
business_metrics = telemetry.get_business_metrics()
```

#### 2. SMOL Agent Instrumentation
Automatic tracing for SMOL agent operations:

```python
with smol_telemetry.trace_agent_execution(
    agent_name="ProductAgent",
    task_id="task-123",
    operation="product_search"
) as span:
    # Agent execution with automatic instrumentation
    span.set_attribute("search.query", query)
    span.set_attribute("search.results", len(results))
```

#### 3. A2A Communication Tracing
Track inter-agent communications:

```python
with a2a_telemetry.trace_agent_communication(
    from_agent="ProductAgent",
    to_agent="InventoryAgent",
    message_type="stock_check"
) as span:
    # Communication tracking
    span.set_attribute("message.size", len(message))
    span.set_attribute("response.time", response_time)
```

#### 4. Business Metrics
Domain-specific metrics tracking:

```python
# Product search metrics
with business_metrics.trace_product_search(
    query="gaming laptops",
    results_count=15,
    search_time=1.2
) as span:
    # Business logic with metrics
    pass

# Inventory operations
with business_metrics.trace_inventory_check(
    product_id="SKU-123",
    stock_level=45,
    threshold=10
) as span:
    # Inventory logic
    pass

# Sales analytics
with business_metrics.trace_sales_analysis(
    period="monthly",
    revenue=125000.00,
    transaction_count=342
) as span:
    # Sales analysis
    pass
```

## Configuration

### Environment Variables

```bash
# Phoenix Configuration
PHOENIX_PROJECT_NAME=a2a-multi-agent
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317
ENABLE_TELEMETRY=true

# Performance Monitoring
PERFORMANCE_MONITORING_INTERVAL=30
ENABLE_SYSTEM_METRICS=true

# Error Handling
ENABLE_ERROR_REPORTING=true
ERROR_REPORTING_LEVEL=WARNING
```

### Docker Integration

The telemetry system is fully integrated with Docker deployment:

```yaml
services:
  phoenix:
    image: arizephoenix/phoenix:latest
    ports:
      - "6006:6006"  # UI
      - "4317:4317"  # OTLP collector
    environment:
      - PHOENIX_LOG_LEVEL=INFO
    volumes:
      - phoenix_data:/phoenix/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6006/health"]
```

## Key Features

### 1. Automatic Span Creation
All agent operations are automatically instrumented:
- Agent initialization
- Tool execution
- LLM calls
- Inter-agent communication
- Error handling

### 2. Performance Monitoring
Real-time system metrics:
- CPU and memory usage
- Response times
- Throughput metrics
- Resource utilization

### 3. Business Intelligence
Track business-specific KPIs:
- Product search performance
- Inventory turnover
- Sales conversion rates
- Customer engagement metrics

### 4. Error Tracking
Comprehensive error handling:
- Automatic error capture
- Stack trace preservation
- Error categorization
- Recovery metrics

## Using Phoenix UI

### Viewing Traces

1. Navigate to http://localhost:6006
2. Select your project: "a2a-multi-agent"
3. View traces in real-time or historical

### Key Views

- **Traces**: Complete request flows
- **Metrics**: Performance and business metrics
- **Spans**: Individual operation details
- **Service Map**: Agent communication patterns

### Creating Dashboards

1. Click "New Dashboard"
2. Add widgets for:
   - Agent response times
   - Error rates
   - Business metrics
   - Communication patterns

## Best Practices

### 1. Span Naming Convention

```python
# Format: <domain>.<operation>.<sub_operation>
"business.product.search"
"system.agent.initialization"
"network.a2a.communication"
```

### 2. Attribute Standards

```python
# Use consistent attribute naming
span.set_attribute("agent.name", agent_name)
span.set_attribute("operation.type", "search")
span.set_attribute("business.domain", "ecommerce")
```

### 3. Error Handling

```python
with telemetry.trace_operation("risky_operation") as span:
    try:
        result = risky_operation()
        span.set_attribute("operation.success", True)
    except Exception as e:
        span.set_attribute("operation.success", False)
        span.set_attribute("error.message", str(e))
        span.record_exception(e)
        raise
```

### 4. Performance Optimization

- Use batch span processing
- Configure appropriate sampling rates
- Set reasonable retention periods
- Monitor collector resource usage

## Troubleshooting

### Common Issues

#### Phoenix Not Collecting Data
```bash
# Check Phoenix health
curl http://localhost:4317/health

# Verify environment variables
docker exec product-agent env | grep PHOENIX

# Check network connectivity
docker exec product-agent ping phoenix
```

#### Missing Traces
```bash
# Verify telemetry is enabled
grep ENABLE_TELEMETRY .env

# Check agent logs for telemetry initialization
docker logs product-agent | grep -i telemetry
```

#### Performance Impact
```bash
# Monitor resource usage
docker stats

# Adjust batch settings if needed
export PHOENIX_BATCH_SIZE=50
export PHOENIX_BATCH_TIMEOUT=10
```

## Advanced Features

### Custom Spans

Create custom spans for specific operations:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("custom_operation") as span:
    span.set_attribute("custom.attribute", "value")
    # Custom logic
```

### Metric Collection

Add custom metrics:

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
counter = meter.create_counter("custom_counter")

counter.add(1, {"dimension": "value"})
```

### Distributed Tracing

Track operations across multiple services:

```python
# Propagate context across agents
from opentelemetry import propagate

headers = {}
propagate.inject(headers)
# Send headers with inter-agent requests
```

## Integration with Enhanced Agents

All enhanced agents automatically include telemetry:

```python
class EnhancedAgent(EnhancedBaseA2AAgent):
    def __init__(self):
        super().__init__(
            enable_telemetry=True,
            phoenix_endpoint="http://phoenix:4317"
        )
```

Agent operations are automatically traced:
- Capability registration
- Request handling
- Tool execution
- Response generation

## Monitoring Dashboard Examples

### Agent Performance Dashboard
- Average response time by agent
- Request volume over time
- Error rate by operation
- Resource utilization

### Business Metrics Dashboard
- Product search performance
- Inventory levels and trends
- Sales analytics
- Customer interaction patterns

### System Health Dashboard
- Service availability
- Network latency
- Resource consumption
- Error distribution

## Data Retention and Privacy

### Retention Policy
- Default: 7 days of trace data
- Configurable via Phoenix settings
- Automatic cleanup of old data

### Data Privacy
- No PII in telemetry data
- Sanitize sensitive attributes
- Local storage only (no cloud)
- Configurable data masking

## Performance Impact

Typical overhead:
- CPU: < 2% increase
- Memory: < 50MB per agent
- Latency: < 5ms per operation
- Network: < 1KB per trace

## Next Steps

1. **Deploy and explore**: See telemetry in action
2. **Create custom dashboards**: Tailor to your needs
3. **Set up alerts**: Proactive monitoring
4. **Analyze patterns**: Optimize agent behavior
5. **Export data**: Integration with other tools

---

*With comprehensive telemetry, you can transform your multi-agent system from a black box into a transparent, optimizable, and trustworthy platform.*