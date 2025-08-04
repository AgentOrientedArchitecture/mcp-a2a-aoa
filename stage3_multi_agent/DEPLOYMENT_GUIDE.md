# Enhanced A2A Multi-Agent System with Telemetry - Deployment Guide

## 🎯 Overview

This guide provides comprehensive instructions for deploying the Enhanced A2A Multi-Agent System with OpenTelemetry and Arize AI Phoenix integration. The system includes three enhanced agents with comprehensive telemetry, performance monitoring, and business metrics tracking.

## 📋 Prerequisites

### System Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Python**: Version 3.12 or higher (for local development)
- **Memory**: Minimum 4GB RAM
- **Storage**: Minimum 10GB free space

### API Keys Required
- **OpenAI API Key**: For LLM integration
- **Anthropic API Key**: For alternative LLM integration (optional)

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Phoenix UI    │    │  Product Agent  │    │ Inventory Agent │
│   (Port 6006)   │    │   (Port 8001)   │    │   (Port 8002)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Sales Agent   │              │
         │              │   (Port 8003)   │              │
         │              └─────────────────┘              │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ MCP Product     │
                    │ Server (8000)   │
                    └─────────────────┘
```

### Telemetry Flow

```
Agents → OpenTelemetry → Phoenix Collector → Phoenix UI
   ↓           ↓              ↓              ↓
Traces    Business      Performance    Visualization
Metrics    Metrics      Monitoring     & Analytics
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd stage3_multi_agent

# Copy environment configuration
cp env.telemetry.example .env

# Edit the environment file with your API keys
nano .env
```

### 2. Configure Environment

Edit the `.env` file with your configuration:

```bash
# Required: API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Customize settings
PHOENIX_PROJECT_NAME=a2a-multi-agent
ENABLE_TELEMETRY=true
LOG_LEVEL=INFO
```

### 3. Deploy with Telemetry

```bash
# Make deployment script executable
chmod +x deploy_with_telemetry.sh

# Deploy the complete system
./deploy_with_telemetry.sh deploy
```

### 4. Verify Deployment

```bash
# Check service status
./deploy_with_telemetry.sh status

# Check service health
./deploy_with_telemetry.sh health

# View logs
./deploy_with_telemetry.sh logs
```

## 📊 Monitoring and Observability

### Phoenix UI Access

Once deployed, access the Phoenix UI at:
- **URL**: http://localhost:6006
- **Features**: Trace visualization, metrics dashboard, performance analytics

### Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Phoenix UI | http://localhost:6006 | Telemetry visualization |
| Product Agent | http://localhost:8001 | Product catalog operations |
| Inventory Agent | http://localhost:8002 | Inventory management |
| Sales Agent | http://localhost:8003 | Sales analytics |
| MCP Server | http://localhost:8000 | Product data server |

### Agent Capabilities

#### Product Agent (6 capabilities)
- `search_products`: Product search with telemetry
- `analyze_prices`: Price analysis with metrics
- `find_similar`: Similar product search
- `recommendations`: Recommendation generation
- `get_product_info`: Product information retrieval
- `analyze_category`: Category analysis

#### Inventory Agent (6 capabilities)
- `check_stock`: Stock level checking with telemetry
- `update_inventory`: Inventory updates with metrics
- `low_stock_alert`: Low stock alerts
- `inventory_analysis`: Inventory analysis
- `supply_chain_status`: Supply chain monitoring
- `reorder_recommendations`: Reorder recommendations

#### Sales Agent (6 capabilities)
- `sales_analysis`: Sales analysis with telemetry
- `revenue_tracking`: Revenue tracking with metrics
- `performance_metrics`: Performance metrics calculation
- `customer_insights`: Customer insight generation
- `trend_analysis`: Trend analysis
- `forecasting`: Sales forecasting

## 🧪 Testing

### Run Comprehensive Tests

```bash
# Run all enhanced agent tests
./deploy_with_telemetry.sh test

# Or run tests directly
python test_all_agents.py
```

### Test Individual Components

```bash
# Test product agent
python test_product_agent.py

# Test telemetry integration
python test_telemetry.py
```

## 🔧 Management Commands

### Deployment Script Commands

```bash
# Full deployment
./deploy_with_telemetry.sh deploy

# Start services
./deploy_with_telemetry.sh start

# Stop services
./deploy_with_telemetry.sh stop

# Restart services
./deploy_with_telemetry.sh restart

# Check status
./deploy_with_telemetry.sh status

# View logs
./deploy_with_telemetry.sh logs [service_name]

# Check health
./deploy_with_telemetry.sh health

# Run tests
./deploy_with_telemetry.sh test

# Cleanup
./deploy_with_telemetry.sh cleanup
```

### Docker Compose Commands

```bash
# Start all services
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose -f docker-compose.yml logs -f

# Stop services
docker-compose -f docker-compose.yml down

# Rebuild and start
docker-compose -f docker-compose.yml up --build -d
```

## 📈 Telemetry Features

### OpenTelemetry Integration

- **SMOL Agents Instrumentation**: Automatic tracing of agent operations
- **A2A Communications**: Inter-agent communication tracing
- **Business Metrics**: Domain-specific metrics tracking
- **Performance Monitoring**: System resource monitoring
- **Error Tracking**: Comprehensive error reporting

### Phoenix Features

- **Trace Visualization**: View request flows and dependencies
- **Performance Analytics**: Monitor response times and throughput
- **Error Analysis**: Identify and debug issues
- **Custom Dashboards**: Create business-specific visualizations
- **Alerting**: Set up performance and error alerts

### Business Metrics Tracked

#### Product Operations
- Search query performance
- Result count and relevance
- Category analysis metrics
- Price analysis trends

#### Inventory Operations
- Stock level monitoring
- Inventory update frequency
- Low stock alerts
- Supply chain status

#### Sales Operations
- Revenue tracking
- Transaction analysis
- Customer insights
- Forecasting accuracy

## 🛠️ Troubleshooting

### Common Issues

#### Phoenix Connection Errors
```bash
# Check if Phoenix is running
docker-compose -f docker-compose.yml ps phoenix

# View Phoenix logs
docker-compose -f docker-compose.yml logs phoenix

# Restart Phoenix
docker-compose -f docker-compose.yml restart phoenix
```

#### Agent Health Issues
```bash
# Check agent health
./deploy_with_telemetry.sh health

# View agent logs
./deploy_with_telemetry.sh logs product-agent

# Restart specific agent
docker-compose -f docker-compose.yml restart enhanced-product-agent
```

#### Telemetry Not Working
```bash
# Check telemetry configuration
grep ENABLE_TELEMETRY .env

# Verify Phoenix endpoint
grep PHOENIX_COLLECTOR_ENDPOINT .env

# Test telemetry connection
curl http://localhost:4317/health
```

### Performance Issues

#### High Memory Usage
```bash
# Check container resource usage
docker stats

# Restart services to free memory
./deploy_with_telemetry.sh restart
```

#### Slow Response Times
```bash
# Check Phoenix UI for performance metrics
# Open http://localhost:6006

# View performance monitoring logs
./deploy_with_telemetry.sh logs product-agent
```

## 🔒 Security Considerations

### Environment Variables
- Never commit API keys to version control
- Use `.env` file for sensitive configuration
- Rotate API keys regularly

### Network Security
- Services communicate over internal Docker network
- Phoenix UI exposed on localhost only
- Agent endpoints protected by health checks

### Data Privacy
- Telemetry data stored locally in Phoenix
- No external data transmission
- Configurable data retention

## 📚 Advanced Configuration

### Custom Telemetry Configuration

Edit the telemetry managers in `telemetry/` directory:

```python
# Custom business metrics
from telemetry import BusinessMetricsManager

# Add custom spans
with business_metrics.trace_custom_operation(
    operation_name="custom_metric",
    **custom_attributes
) as span:
    # Your custom operation
    pass
```

### Performance Tuning

```bash
# Adjust monitoring intervals
PERFORMANCE_MONITORING_INTERVAL=60

# Configure batch processing
PHOENIX_BATCH_SIZE=100
PHOENIX_BATCH_TIMEOUT=5
```

### Custom Dashboards

Access Phoenix UI at http://localhost:6006 to create custom dashboards for:
- Agent performance metrics
- Business KPI tracking
- Error rate monitoring
- Resource utilization

## 🚀 Production Deployment

### Scaling Considerations

```bash
# Scale specific agents
docker-compose -f docker-compose.yml up -d --scale enhanced-product-agent=3

# Load balancing configuration
# Add nginx or traefik for load balancing
```

### Monitoring and Alerting

```bash
# Set up external monitoring
# Integrate with Prometheus, Grafana, or other monitoring tools

# Configure alerting rules in Phoenix UI
# Set up email/Slack notifications
```

### Backup and Recovery

```bash
# Backup Phoenix data
docker run --rm -v aoa-phoenix_data:/data -v $(pwd):/backup alpine tar czf /backup/phoenix_backup.tar.gz -C /data .

# Restore Phoenix data
docker run --rm -v aoa-phoenix_data:/data -v $(pwd):/backup alpine tar xzf /backup/phoenix_backup.tar.gz -C /data
```

## 📞 Support

### Getting Help

1. **Check logs**: `./deploy_with_telemetry.sh logs`
2. **Verify health**: `./deploy_with_telemetry.sh health`
3. **Run tests**: `./deploy_with_telemetry.sh test`
4. **Check Phoenix UI**: http://localhost:6006

### Documentation

- **Telemetry Implementation Plan**: `TELEMETRY_IMPLEMENTATION_PLAN.md`
- **Agent Documentation**: See individual agent files
- **API Documentation**: Check agent endpoints for capabilities

### Community

- **Issues**: Report bugs and feature requests
- **Discussions**: Share experiences and best practices
- **Contributions**: Submit improvements and enhancements

---

**🎉 Congratulations!** You've successfully deployed the Enhanced A2A Multi-Agent System with comprehensive telemetry and observability features. 