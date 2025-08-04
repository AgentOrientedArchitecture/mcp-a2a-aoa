# **🔍 Telemetry Setup Guide - OpenTelemetry + SMOL Agents + Arize AI Phoenix**

## **📋 Overview**

This guide provides step-by-step instructions for setting up comprehensive observability for the A2A multi-agent system using OpenTelemetry, SMOL agents instrumentation, and Arize AI Phoenix for monitoring and evaluation.

## **🎯 What You'll Learn**

- How to set up OpenTelemetry instrumentation
- How to configure Arize AI Phoenix
- How to deploy the complete observability stack
- How to monitor and analyze telemetry data
- How to troubleshoot common issues

---

## **🚀 Quick Start**

### **Prerequisites**

```bash
# System Requirements
- Docker 20.10+
- Docker Compose 2.0+ (docker compose command)
- Python 3.12+
- 4GB RAM minimum
- 10GB free space

# API Keys Required
- OpenAI API Key
- Anthropic API Key (optional)
```

### **1. Clone and Setup**

```bash
# Navigate to the project
cd stage3_multi_agent

# Copy environment configuration
cp env.telemetry.example .env

# Edit with your API keys
nano .env
```

### **2. Configure Environment**

```bash
# Required: API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Customize settings
PHOENIX_PROJECT_NAME=a2a-multi-agent
ENABLE_TELEMETRY=true
LOG_LEVEL=INFO
```

### **3. Deploy with Telemetry**

```bash
# Make deployment script executable
chmod +x deploy_with_telemetry.sh

# Deploy the complete system
./deploy_with_telemetry.sh deploy
```

### **4. Access Phoenix UI**

```bash
# Open in your browser
http://localhost:6006
```

---

## **🏗️ Architecture Overview**

### **System Components**

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

### **Telemetry Flow**

```
Agents → OpenTelemetry → Phoenix Collector → Phoenix UI
   ↓           ↓              ↓              ↓
Traces    Business      Performance    Visualization
Metrics    Metrics      Monitoring     & Analytics
```

---

## **📦 Installation**

### **Step 1: Install Dependencies**

```bash
# Install OpenTelemetry packages
uv add opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http

# Install Phoenix integration
uv add arize-phoenix-otel

# Install SMOL agents instrumentation
uv add openinference-instrumentation-smolagents

# Install LLM provider instrumentations
uv add openinference-instrumentation-openai
uv add openinference-instrumentation-anthropic

# Install additional dependencies
uv add python-dotenv psutil
```

### **Step 2: Verify Installation**

```bash
# Test telemetry initialization
python test_telemetry.py

# Expected output:
# ✅ Telemetry initialized successfully
# ✅ All telemetry managers created
# ✅ Span creation working
```

---

## **⚙️ Configuration**

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

# Agent Ports
PRODUCT_AGENT_PORT=8001
INVENTORY_AGENT_PORT=8002
SALES_AGENT_PORT=8003

# Performance Monitoring
PERFORMANCE_MONITORING_INTERVAL=30
ENABLE_SYSTEM_METRICS=true

# Error Handling
ENABLE_ERROR_REPORTING=true
ERROR_REPORTING_LEVEL=WARNING
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=5
```

### **Docker Configuration**

```yaml
# docker-compose-with-phoenix.yml
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
```

---

## **🔧 Deployment**

### **Method 1: Docker Compose (Recommended)**

```bash
# Deploy with telemetry
./deploy_with_telemetry.sh deploy

# Check status
./deploy_with_telemetry.sh status

# View logs
./deploy_with_telemetry.sh logs
```

### **Method 2: Manual Deployment**

```bash
# Build images
docker build -f product.Dockerfile -t aoa-enhanced-product-agent .
docker build -f inventory.Dockerfile -t aoa-enhanced-inventory-agent .
docker build -f sales.Dockerfile -t aoa-enhanced-sales-agent .

# Start services
docker compose -f docker-compose.yml up -d

# Verify deployment
docker compose -f docker-compose.yml ps
```

### **Method 3: Local Development**

```bash
# Set up local environment
cp env.telemetry.example .env
# Edit .env with your configuration

# Run agents locally
python agents/product_agent.py &
python agents/inventory_agent.py &
python agents/sales_agent.py &

# Start Phoenix (if available)
# docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
```

---

## **📊 Monitoring and Observability**

### **Phoenix UI Access**

Once deployed, access the Phoenix UI at:
- **URL**: http://localhost:6006
- **Features**: 
  - Trace visualization
  - Metrics dashboard
  - Performance analytics
  - Error analysis
  - Custom dashboards

### **Service Endpoints**

| Service | URL | Description |
|---------|-----|-------------|
| Phoenix UI | http://localhost:6006 | Telemetry visualization |
| Product Agent | http://localhost:8001 | Product catalog operations |
| Inventory Agent | http://localhost:8002 | Inventory management |
| Sales Agent | http://localhost:8003 | Sales analytics |
| MCP Server | http://localhost:8000 | Product data server |

### **Key Metrics to Monitor**

#### **Agent Performance**
- Response times
- Throughput
- Error rates
- Resource usage

#### **Business Metrics**
- Product search performance
- Inventory levels
- Sales analytics
- Customer insights

#### **System Health**
- Agent availability
- Network connectivity
- Memory usage
- CPU utilization

---

## **🧪 Testing**

### **Run Comprehensive Tests**

```bash
# Run all telemetry tests
python run_telemetry_tests.py

# Run specific test categories
python telemetry/tests/test_smol_instrumentation.py
python telemetry/tests/test_a2a_instrumentation.py
python telemetry/tests/test_mcp_instrumentation.py
python telemetry/tests/test_business_metrics.py
```

### **Test Individual Components**

```bash
# Test telemetry initialization
python test_telemetry.py

# Test enhanced agents
python test_all_agents.py

# Test deployment script
./deploy_with_telemetry.sh test
```

### **Expected Test Results**

```bash
✅ Integration Tests: PASSED
✅ Telemetry Initialization: PASSED
✅ All enhanced agents working
✅ Telemetry spans being created
✅ Business metrics tracking
✅ Performance monitoring active
```

---

## **🛠️ Troubleshooting**

### **Common Issues**

#### **1. Phoenix Connection Errors**

```bash
# Check if Phoenix is running
docker compose -f docker-compose.yml ps phoenix

# View Phoenix logs
docker compose -f docker-compose.yml logs phoenix

# Restart Phoenix
docker compose -f docker-compose.yml restart phoenix
```

**Symptoms**: Connection refused errors in telemetry logs
**Solution**: Ensure Phoenix container is running and healthy

#### **2. Agent Health Issues**

```bash
# Check agent health
./deploy_with_telemetry.sh health

# View agent logs
./deploy_with_telemetry.sh logs enhanced-product-agent

# Restart specific agent
docker compose -f docker-compose.yml restart enhanced-product-agent
```

**Symptoms**: Agents not responding or telemetry not being sent
**Solution**: Check agent logs and restart if necessary

#### **3. Telemetry Not Working**

```bash
# Check telemetry configuration
grep ENABLE_TELEMETRY .env

# Verify Phoenix endpoint
grep PHOENIX_COLLECTOR_ENDPOINT .env

# Test telemetry connection
curl http://localhost:4317/health
```

**Symptoms**: No telemetry data in Phoenix UI
**Solution**: Verify environment variables and Phoenix connectivity

#### **4. Performance Issues**

```bash
# Check container resource usage
docker stats

# View performance monitoring logs
./deploy_with_telemetry.sh logs enhanced-product-agent

# Restart services to free memory
./deploy_with_telemetry.sh restart
```

**Symptoms**: Slow response times or high memory usage
**Solution**: Monitor resource usage and restart if needed

### **Debug Commands**

```bash
# Check all service status
./deploy_with_telemetry.sh status

# View all logs
./deploy_with_telemetry.sh logs

# Check specific service logs
./deploy_with_telemetry.sh logs phoenix

# Run health checks
./deploy_with_telemetry.sh health

# Clean up and restart
./deploy_with_telemetry.sh cleanup
./deploy_with_telemetry.sh deploy
```

---

## **📈 Performance Optimization**

### **Telemetry Configuration Tuning**

```bash
# Adjust batch processing
PHOENIX_BATCH_SIZE=100
PHOENIX_BATCH_TIMEOUT=5

# Optimize monitoring intervals
PERFORMANCE_MONITORING_INTERVAL=60

# Configure error reporting
ERROR_REPORTING_LEVEL=ERROR
MAX_RETRY_ATTEMPTS=5
```

### **Resource Management**

```bash
# Monitor resource usage
docker stats

# Set resource limits in docker-compose
services:
  enhanced-product-agent:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### **Scaling Considerations**

```bash
# Scale specific agents
docker compose -f docker-compose.yml up -d --scale enhanced-product-agent=3

# Load balancing
# Add nginx or traefik for load balancing
```

---

## **🔒 Security Considerations**

### **Environment Variables**
- Never commit API keys to version control
- Use `.env` file for sensitive configuration
- Rotate API keys regularly

### **Network Security**
- Services communicate over internal Docker network
- Phoenix UI exposed on localhost only
- Agent endpoints protected by health checks

### **Data Privacy**
- Telemetry data stored locally in Phoenix
- No external data transmission
- Configurable data retention

---

## **📚 Advanced Configuration**

### **Custom Telemetry Configuration**

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

### **Custom Dashboards**

Access Phoenix UI at http://localhost:6006 to create custom dashboards for:
- Agent performance metrics
- Business KPI tracking
- Error rate monitoring
- Resource utilization

### **Alerting Rules**

Configure alerting rules in Phoenix UI for:
- High error rates
- Performance degradation
- Agent communication failures
- Resource usage thresholds

---

## **🚀 Production Deployment**

### **Scaling Considerations**

```bash
# Scale specific agents
docker-compose -f docker-compose-with-phoenix.yml up -d --scale enhanced-product-agent=3

# Load balancing configuration
# Add nginx or traefik for load balancing
```

### **Monitoring and Alerting**

```bash
# Set up external monitoring
# Integrate with Prometheus, Grafana, or other monitoring tools

# Configure alerting rules in Phoenix UI
# Set up email/Slack notifications
```

### **Backup and Recovery**

```bash
# Backup Phoenix data
docker run --rm -v aoa-phoenix_data:/data -v $(pwd):/backup alpine tar czf /backup/phoenix_backup.tar.gz -C /data .

# Restore Phoenix data
docker run --rm -v aoa-phoenix_data:/data -v $(pwd):/backup alpine tar xzf /backup/phoenix_backup.tar.gz -C /data
```

---

## **📞 Support**

### **Getting Help**

1. **Check logs**: `./deploy_with_telemetry.sh logs`
2. **Verify health**: `./deploy_with_telemetry.sh health`
3. **Run tests**: `./deploy_with_telemetry.sh test`
4. **Check Phoenix UI**: http://localhost:6006

### **Documentation**

- **Telemetry Implementation Plan**: `TELEMETRY_IMPLEMENTATION_PLAN.md`
- **Test Results Summary**: `TEST_RESULTS_SUMMARY.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Agent Documentation**: See individual agent files

### **Community**

- **Issues**: Report bugs and feature requests
- **Discussions**: Share experiences and best practices
- **Contributions**: Submit improvements and enhancements

---

## **🎯 Next Steps**

1. **Deploy the complete system**
   ```bash
   ./deploy_with_telemetry.sh deploy
   ```

2. **Access Phoenix UI**
   - Open http://localhost:6006
   - Explore traces and metrics
   - Create custom dashboards

3. **Run comprehensive tests**
   ```bash
   python run_telemetry_tests.py
   ```

4. **Monitor and optimize**
   - Track performance metrics
   - Optimize resource usage
   - Configure alerting rules

---

**🎉 Congratulations!** You've successfully set up comprehensive observability for your A2A multi-agent system with OpenTelemetry and Arize AI Phoenix. 