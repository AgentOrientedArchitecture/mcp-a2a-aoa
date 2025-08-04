# Operations Guide - Deployment, Monitoring & Troubleshooting

## Overview

This guide covers day-to-day operations for the A2A multi-agent system with Phoenix telemetry, including deployment, monitoring, troubleshooting, and maintenance procedures.

## Table of Contents

1. [Deployment](#deployment)
2. [Service Management](#service-management)
3. [Monitoring](#monitoring)
4. [Troubleshooting](#troubleshooting)
5. [API Reference](#api-reference)
6. [Maintenance](#maintenance)

## Deployment

### Prerequisites

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **System Resources**: 4GB RAM, 10GB storage
- **API Keys**: OpenAI or Anthropic

### Quick Deployment

```bash
# Complete deployment in one command
cd stage3_multi_agent
./deploy_with_telemetry.sh deploy

# This will:
# 1. Check prerequisites
# 2. Setup environment
# 3. Build Docker images
# 4. Start all services
# 5. Verify health
# 6. Display access URLs
```

### Manual Deployment Steps

```bash
# 1. Environment setup
cp env.telemetry.example .env
# Edit .env with your API keys

# 2. Build images
docker build -f product.Dockerfile -t aoa-enhanced-product-agent ..
docker build -f inventory.Dockerfile -t aoa-enhanced-inventory-agent ..
docker build -f sales.Dockerfile -t aoa-enhanced-sales-agent ..

# 3. Start services
docker compose -f docker-compose.yml up -d

# 4. Verify deployment
docker compose -f docker-compose.yml ps
```

### Environment Configuration

```bash
# Required
OPENAI_API_KEY=sk-...              # Or use Anthropic
ANTHROPIC_API_KEY=sk-ant-...       # Or use OpenAI

# Phoenix Telemetry
PHOENIX_PROJECT_NAME=a2a-multi-agent
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317
ENABLE_TELEMETRY=true

# Agent Configuration
A2A_HOST=0.0.0.0
LOG_LEVEL=INFO
DISCOVERY_METHOD=docker

# Performance Tuning
PERFORMANCE_MONITORING_INTERVAL=30
PHOENIX_BATCH_SIZE=100
PHOENIX_BATCH_TIMEOUT=5
```

## Service Management

### Service Control Commands

```bash
# Start all services
./deploy_with_telemetry.sh start

# Stop all services
./deploy_with_telemetry.sh stop

# Restart services
./deploy_with_telemetry.sh restart

# Check status
./deploy_with_telemetry.sh status

# View logs
./deploy_with_telemetry.sh logs [service_name]

# Health check
./deploy_with_telemetry.sh health
```

### Service Architecture

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| Phoenix UI | 6006 | Telemetry visualization | `/health` |
| Phoenix Collector | 4317 | OTLP collection | `/health` |
| Web UI | 3000 | User interface | `/health` |
| Product Agent | 8001 | Product operations | `/.well-known/agent-card.json` |
| Inventory Agent | 8002 | Inventory management | `/.well-known/agent-card.json` |
| Sales Agent | 8003 | Sales analytics | `/.well-known/agent-card.json` |

### Docker Compose Management

```bash
# Scale services
docker compose -f docker-compose.yml up -d --scale product-agent=3

# View resource usage
docker stats

# Inspect service
docker compose -f docker-compose.yml logs product-agent

# Execute commands in container
docker compose -f docker-compose.yml exec product-agent bash
```

## Monitoring

### Health Monitoring

```bash
# Automated health check
./deploy_with_telemetry.sh health

# Manual health checks
curl -f http://localhost:8001/.well-known/agent-card.json  # Product Agent
curl -f http://localhost:8002/.well-known/agent-card.json  # Inventory Agent
curl -f http://localhost:8003/.well-known/agent-card.json  # Sales Agent
curl -f http://localhost:6006/health                        # Phoenix UI
curl -f http://localhost:3001/health                        # Web UI Backend
```

### Phoenix Telemetry Monitoring

Access Phoenix UI: http://localhost:6006

Key metrics to monitor:
- **Response Times**: Agent latency trends
- **Error Rates**: Failure patterns
- **Throughput**: Request volume
- **Resource Usage**: CPU/Memory consumption

### Log Monitoring

```bash
# View all logs
./deploy_with_telemetry.sh logs

# Follow logs in real-time
docker compose -f docker-compose.yml logs -f

# Filter by service
docker compose -f docker-compose.yml logs product-agent

# Search for errors
./deploy_with_telemetry.sh logs | grep -i error

# Check specific time range
docker compose -f docker-compose.yml logs --since 1h
```

### Performance Monitoring

```bash
# Real-time resource monitoring
docker stats

# Check system resources
free -h
df -h
top

# Network monitoring
netstat -tulpn | grep -E "(6006|8001|8002|8003)"
```

## Troubleshooting

### Common Issues & Solutions

#### 1. Services Won't Start

**Symptoms**: Containers fail to start or immediately exit

**Solutions**:
```bash
# Check Docker daemon
docker info

# Verify port availability
netstat -tulpn | grep -E "(6006|8001|8002|8003)"

# Clean and restart
./deploy_with_telemetry.sh cleanup
./deploy_with_telemetry.sh deploy

# Check logs for specific errors
docker compose -f docker-compose.yml logs
```

#### 2. Phoenix Not Collecting Data

**Symptoms**: No traces visible in Phoenix UI

**Solutions**:
```bash
# Verify Phoenix is running
docker compose -f docker-compose.yml ps phoenix

# Check telemetry configuration
grep ENABLE_TELEMETRY .env

# Test Phoenix connectivity
curl http://localhost:4317/health

# Restart Phoenix
docker compose -f docker-compose.yml restart phoenix
```

#### 3. Agent Communication Failures

**Symptoms**: Agents can't discover or communicate with each other

**Solutions**:
```bash
# Check agent health
./deploy_with_telemetry.sh health

# Verify network
docker network ls
docker network inspect stage3_multi_agent_agent-network

# Test agent discovery
curl http://localhost:8001/.well-known/agent-card.json

# Check discovery configuration
docker compose -f docker-compose.yml exec product-agent env | grep DISCOVERY
```

#### 4. High Memory Usage

**Symptoms**: Containers consuming excessive memory

**Solutions**:
```bash
# Check current usage
docker stats

# Set resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'

# Restart services
./deploy_with_telemetry.sh restart

# Clear Docker cache
docker system prune -a
```

#### 5. Web UI Not Loading

**Symptoms**: Cannot access Web UI at localhost:3000

**Solutions**:
```bash
# Check Web UI container
docker logs agent-web-ui

# Verify backend API
curl http://localhost:3001/health

# Restart Web UI
docker compose -f docker-compose.yml restart web-ui

# Check agent connectivity
docker compose -f docker-compose.yml exec web-ui ping product-agent
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Set debug environment
export LOG_LEVEL=DEBUG
export DEBUG_TELEMETRY=true

# Restart with debug
./deploy_with_telemetry.sh restart

# View debug logs
./deploy_with_telemetry.sh logs | grep -i debug
```

### Emergency Procedures

```bash
# Complete system reset
./deploy_with_telemetry.sh cleanup
docker system prune -a --volumes
./deploy_with_telemetry.sh deploy

# Backup Phoenix data
docker run --rm -v stage3_multi_agent_phoenix_data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/phoenix_backup_$(date +%Y%m%d).tar.gz -C /data .

# Restore Phoenix data
docker run --rm -v stage3_multi_agent_phoenix_data:/data \
  -v $(pwd):/backup alpine \
  tar xzf /backup/phoenix_backup_20240101.tar.gz -C /data
```

## API Reference

### Agent Endpoints

#### Product Agent (Port 8001)

```bash
# Agent Card
GET http://localhost:8001/.well-known/agent-card.json

# Execute Task
POST http://localhost:8001/execute
Content-Type: application/json
{
  "task": "Find gaming laptops under $1500"
}

# Capabilities
- search_products
- analyze_prices
- find_similar
- recommendations
- get_product_info
- analyze_category
```

#### Inventory Agent (Port 8002)

```bash
# Agent Card
GET http://localhost:8002/.well-known/agent-card.json

# Execute Task
POST http://localhost:8002/execute
Content-Type: application/json
{
  "task": "Check stock for product ID 100"
}

# Capabilities
- check_stock
- update_inventory
- low_stock_alert
- inventory_analysis
- supply_chain_status
- reorder_recommendations
```

#### Sales Agent (Port 8003)

```bash
# Agent Card
GET http://localhost:8003/.well-known/agent-card.json

# Execute Task
POST http://localhost:8003/execute
Content-Type: application/json
{
  "task": "Analyze Q4 sales performance"
}

# Capabilities
- sales_analysis
- revenue_tracking
- performance_metrics
- customer_insights
- trend_analysis
- forecasting
```

### Phoenix Telemetry API

```bash
# Phoenix UI
GET http://localhost:6006

# OTLP Trace Submission
POST http://localhost:4317/v1/traces
Content-Type: application/x-protobuf

# Query Traces
GET http://localhost:6006/api/v1/traces

# Query Metrics
GET http://localhost:6006/api/v1/metrics
```

### Web UI API

```bash
# Health Check
GET http://localhost:3001/health

# Send Message to Agent
POST http://localhost:3001/api/agent/message
Content-Type: application/json
{
  "agent": "product",
  "message": "Find all laptops"
}
```

## Maintenance

### Regular Maintenance Tasks

#### Daily
```bash
# Check service health
./deploy_with_telemetry.sh health

# Review error logs
./deploy_with_telemetry.sh logs | grep -i error

# Monitor resource usage
docker stats --no-stream
```

#### Weekly
```bash
# Clean up unused resources
docker system prune -f

# Backup Phoenix data
./backup_phoenix.sh

# Review performance metrics in Phoenix UI
open http://localhost:6006
```

#### Monthly
```bash
# Full system restart
./deploy_with_telemetry.sh stop
./deploy_with_telemetry.sh cleanup
./deploy_with_telemetry.sh deploy

# Update base images
docker pull arizephoenix/phoenix:latest
docker pull python:3.12-slim

# Review and rotate logs
docker compose -f docker-compose.yml logs > logs_$(date +%Y%m).txt
```

### Performance Optimization

#### Resource Tuning
```yaml
# docker-compose-with-phoenix.yml
services:
  product-agent:
    deploy:
      resources:
        limits:
          memory: 2G  # Increase for better performance
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

#### Telemetry Optimization
```bash
# Reduce telemetry overhead
PHOENIX_BATCH_SIZE=200        # Larger batches
PHOENIX_BATCH_TIMEOUT=10      # Longer timeout
PERFORMANCE_MONITORING_INTERVAL=60  # Less frequent monitoring
```

#### Network Optimization
```yaml
# Use host network for better performance (Linux only)
network_mode: host
```

### Security Best Practices

1. **API Key Management**
   - Never commit .env files
   - Rotate keys regularly
   - Use secrets management in production

2. **Network Security**
   - Keep services on internal network
   - Use reverse proxy for external access
   - Enable TLS for production

3. **Access Control**
   - Implement authentication for agents
   - Use API rate limiting
   - Monitor for suspicious activity

### Backup and Recovery

#### Automated Backup Script
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup Phoenix data
docker run --rm -v stage3_multi_agent_phoenix_data:/data \
  -v $BACKUP_DIR:/backup alpine \
  tar czf /backup/phoenix_$DATE.tar.gz -C /data .

# Backup databases
cp inventory_mcp/inventory.db $BACKUP_DIR/inventory_$DATE.db
cp sales_mcp/sales.db $BACKUP_DIR/sales_$DATE.db

echo "Backup completed: $DATE"
```

#### Recovery Procedure
```bash
# Stop services
./deploy_with_telemetry.sh stop

# Restore Phoenix data
docker run --rm -v stage3_multi_agent_phoenix_data:/data \
  -v ./backups:/backup alpine \
  tar xzf /backup/phoenix_20240101_120000.tar.gz -C /data

# Restore databases
cp ./backups/inventory_20240101_120000.db inventory_mcp/inventory.db
cp ./backups/sales_20240101_120000.db sales_mcp/sales.db

# Restart services
./deploy_with_telemetry.sh start
```

## Production Deployment

### Scaling Considerations

```bash
# Horizontal scaling
docker compose -f docker-compose.yml up -d \
  --scale product-agent=3 \
  --scale inventory-agent=2

# Load balancer configuration (add nginx/traefik)
# See production-deployment/ for examples
```

### Monitoring Integration

```yaml
# Prometheus integration
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

### High Availability

- Use Docker Swarm or Kubernetes for orchestration
- Implement health checks and auto-restart
- Configure persistent volumes for data
- Set up monitoring and alerting

---

*This operations guide provides everything needed to deploy, monitor, and maintain the A2A multi-agent system in production.*