# **🛠️ Telemetry Troubleshooting Guide**

## **📋 Overview**

This guide provides comprehensive troubleshooting steps for the OpenTelemetry + SMOL Agents + Arize AI Phoenix telemetry system. It covers common issues, error messages, and step-by-step solutions.

---

## **🚨 Emergency Quick Fixes**

### **System Won't Start**

```bash
# 1. Check Docker status
docker info

# 2. Restart Docker if needed
sudo systemctl restart docker

# 3. Clean up and redeploy
./deploy_with_telemetry.sh cleanup
./deploy_with_telemetry.sh deploy
```

### **Phoenix UI Not Accessible**

```bash
# 1. Check if Phoenix is running
docker-compose -f docker-compose-with-phoenix.yml ps phoenix

# 2. Restart Phoenix
docker compose -f docker-compose-with-phoenix.yml restart phoenix

# 3. Check Phoenix logs
docker compose -f docker-compose-with-phoenix.yml logs phoenix
```

### **Agents Not Responding**

```bash
# 1. Check agent health
./deploy_with_telemetry.sh health

# 2. Restart all agents
./deploy_with_telemetry.sh restart

# 3. Check agent logs
./deploy_with_telemetry.sh logs enhanced-product-agent
```

---

## **🔍 Common Issues and Solutions**

### **Issue 1: Phoenix Connection Refused**

#### **Symptoms**
```
ConnectionRefusedError: [Errno 111] Connection refused
HTTPConnectionPool(host='localhost', port=6006): Max retries exceeded
```

#### **Root Cause**
- Phoenix container not running
- Network connectivity issues
- Port conflicts

#### **Solutions**

**Step 1: Check Phoenix Status**
```bash
# Check if Phoenix is running
docker compose -f docker-compose-with-phoenix.yml ps phoenix

# Expected output:
# Name                    Command               State           Ports
# aoa-phoenix   /bin/sh -c /phoenix/start ...   Up      0.0.0.0:6006->6006/tcp
```

**Step 2: Restart Phoenix**
```bash
# Stop Phoenix
docker compose -f docker-compose-with-phoenix.yml stop phoenix

# Start Phoenix
docker compose -f docker-compose-with-phoenix.yml up -d phoenix

# Wait for Phoenix to be ready
sleep 30
```

**Step 3: Check Phoenix Logs**
```bash
# View Phoenix logs
docker compose -f docker-compose-with-phoenix.yml logs phoenix

# Look for errors like:
# - Port already in use
# - Permission denied
# - Resource limits exceeded
```

**Step 4: Verify Network**
```bash
# Check if port 6006 is available
netstat -tulpn | grep 6006

# Check if port 4317 is available
netstat -tulpn | grep 4317
```

**Step 5: Manual Phoenix Start**
```bash
# Start Phoenix manually
docker run -d \
  --name aoa-phoenix \
  -p 6006:6006 \
  -p 4317:4317 \
  -e PHOENIX_PROJECT_NAME=a2a-multi-agent \
  arizephoenix/phoenix:latest
```

### **Issue 2: Agent Health Check Failures**

#### **Symptoms**
```
Health check failed for enhanced-product-agent
curl: (7) Failed to connect to localhost port 8001
```

#### **Root Cause**
- Agent container not running
- Agent startup errors
- Configuration issues

#### **Solutions**

**Step 1: Check Agent Status**
```bash
# Check all agent status
./deploy_with_telemetry.sh status

# Check specific agent
docker compose -f docker-compose-with-phoenix.yml ps enhanced-product-agent
```

**Step 2: View Agent Logs**
```bash
# View all agent logs
./deploy_with_telemetry.sh logs

# View specific agent logs
./deploy_with_telemetry.sh logs enhanced-product-agent
```

**Step 3: Restart Failed Agent**
```bash
# Restart specific agent
docker compose -f docker-compose-with-phoenix.yml restart enhanced-product-agent

# Wait for agent to be ready
sleep 10

# Check health again
./deploy_with_telemetry.sh health
```

**Step 4: Check Agent Configuration**
```bash
# Check environment variables
docker compose -f docker-compose-with-phoenix.yml exec enhanced-product-agent env | grep -E "(ENABLE_TELEMETRY|PHOENIX|AGENT)"

# Check agent configuration
docker compose -f docker-compose-with-phoenix.yml exec enhanced-product-agent cat /app/.env
```

### **Issue 3: Telemetry Not Being Sent**

#### **Symptoms**
- No traces in Phoenix UI
- Empty telemetry data
- No span creation logs

#### **Root Cause**
- Telemetry disabled
- Configuration errors
- Network connectivity issues

#### **Solutions**

**Step 1: Check Telemetry Configuration**
```bash
# Check if telemetry is enabled
grep ENABLE_TELEMETRY .env

# Should show: ENABLE_TELEMETRY=true

# Check Phoenix endpoint
grep PHOENIX_COLLECTOR_ENDPOINT .env

# Should show: PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317
```

**Step 2: Verify Telemetry Initialization**
```bash
# Test telemetry initialization
python test_telemetry.py

# Expected output:
# ✅ Telemetry initialized successfully
# ✅ All telemetry managers created
```

**Step 3: Check Network Connectivity**
```bash
# Test connection to Phoenix
curl -v http://localhost:4317/health

# Test from within agent container
docker compose -f docker-compose-with-phoenix.yml exec enhanced-product-agent curl -v http://phoenix:4317/health
```

**Step 4: Enable Debug Logging**
```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Restart agents with debug logging
./deploy_with_telemetry.sh restart

# Check debug logs
./deploy_with_telemetry.sh logs enhanced-product-agent | grep -i telemetry
```

### **Issue 4: Performance Problems**

#### **Symptoms**
- Slow response times
- High memory usage
- CPU spikes
- Timeout errors

#### **Root Cause**
- Resource constraints
- Telemetry overhead
- Configuration issues

#### **Solutions**

**Step 1: Monitor Resource Usage**
```bash
# Check container resource usage
docker stats

# Check system resources
top
htop
free -h
```

**Step 2: Optimize Telemetry Configuration**
```bash
# Reduce telemetry batch size
export PHOENIX_BATCH_SIZE=50

# Increase batch timeout
export PHOENIX_BATCH_TIMEOUT=10

# Reduce monitoring interval
export PERFORMANCE_MONITORING_INTERVAL=60
```

**Step 3: Set Resource Limits**
```yaml
# In docker-compose-with-phoenix.yml
services:
  enhanced-product-agent:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

**Step 4: Scale Services**
```bash
# Scale specific agents
docker-compose -f docker-compose-with-phoenix.yml up -d --scale enhanced-product-agent=2

# Monitor performance
docker stats
```

### **Issue 5: Test Failures**

#### **Symptoms**
```
❌ SMOL instrumentation tests failed
❌ A2A instrumentation tests failed
❌ Integration tests failed
```

#### **Root Cause**
- Missing dependencies
- Configuration issues
- Phoenix not running

#### **Solutions**

**Step 1: Install Dependencies**
```bash
# Install required packages
uv pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
uv pip install arize-phoenix-otel
uv pip install openinference-instrumentation-smolagents
uv pip install python-dotenv psutil
```

**Step 2: Check Test Environment**
```bash
# Verify test environment
python -c "import opentelemetry; print('OpenTelemetry installed')"
python -c "import arize_phoenix_otel; print('Phoenix OTLP installed')"

# Run basic telemetry test
python test_telemetry.py
```

**Step 3: Run Tests with Phoenix**
```bash
# Start Phoenix first
docker-compose -f docker-compose-with-phoenix.yml up -d phoenix

# Wait for Phoenix to be ready
sleep 30

# Run tests
python run_telemetry_tests.py
```

---

## **🔧 Advanced Troubleshooting**

### **Debug Mode**

**Enable Debug Logging**
```bash
# Set debug environment
export LOG_LEVEL=DEBUG
export DEBUG_TELEMETRY=true

# Restart with debug logging
./deploy_with_telemetry.sh restart

# View debug logs
./deploy_with_telemetry.sh logs | grep -i debug
```

**Enable Telemetry Debug**
```python
# In your agent code
import logging
logging.getLogger('opentelemetry').setLevel(logging.DEBUG)
logging.getLogger('telemetry').setLevel(logging.DEBUG)
```

### **Network Diagnostics**

**Check Network Connectivity**
```bash
# Test localhost connectivity
ping localhost

# Test Docker network
docker network ls
docker network inspect aoa-network

# Test inter-container communication
docker-compose -f docker-compose-with-phoenix.yml exec enhanced-product-agent ping phoenix
```

**Check Port Availability**
```bash
# Check if ports are in use
netstat -tulpn | grep -E "(6006|4317|8001|8002|8003)"

# Kill processes using ports if needed
sudo fuser -k 6006/tcp
sudo fuser -k 4317/tcp
```

### **Container Debugging**

**Inspect Container State**
```bash
# Check container details
docker inspect aoa-enhanced-product-agent

# Check container logs
docker logs aoa-enhanced-product-agent

# Execute commands in container
docker-compose -f docker-compose-with-phoenix.yml exec enhanced-product-agent bash
```

**Debug Container Startup**
```bash
# Run container interactively
docker run -it --rm aoa-enhanced-product-agent bash

# Check startup script
cat /app/start.sh

# Test telemetry initialization
python -c "from telemetry import TelemetryManager; print('Telemetry works')"
```

---

## **📊 Monitoring and Diagnostics**

### **Health Check Commands**

```bash
# Comprehensive health check
./deploy_with_telemetry.sh health

# Check specific services
docker-compose -f docker-compose-with-phoenix.yml ps

# Check resource usage
docker stats --no-stream

# Check logs for errors
./deploy_with_telemetry.sh logs | grep -i error
```

### **Performance Monitoring**

```bash
# Monitor CPU and memory
docker stats --no-stream

# Check disk usage
df -h

# Monitor network
netstat -i

# Check process limits
ulimit -a
```

### **Log Analysis**

```bash
# View all logs
./deploy_with_telemetry.sh logs

# Filter by service
./deploy_with_telemetry.sh logs phoenix
./deploy_with_telemetry.sh logs enhanced-product-agent

# Filter by log level
./deploy_with_telemetry.sh logs | grep -i error
./deploy_with_telemetry.sh logs | grep -i warning

# Follow logs in real-time
./deploy_with_telemetry.sh logs -f
```

---

## **🚨 Emergency Procedures**

### **Complete System Reset**

```bash
# Stop all services
./deploy_with_telemetry.sh stop

# Clean up containers and volumes
./deploy_with_telemetry.sh cleanup

# Remove all images
docker system prune -a --volumes

# Rebuild and redeploy
./deploy_with_telemetry.sh deploy
```

### **Data Recovery**

```bash
# Backup Phoenix data
docker run --rm -v aoa-phoenix_data:/data -v $(pwd):/backup alpine tar czf /backup/phoenix_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore Phoenix data
docker run --rm -v aoa-phoenix_data:/data -v $(pwd):/backup alpine tar xzf /backup/phoenix_backup_YYYYMMDD_HHMMSS.tar.gz -C /data
```

### **Emergency Contact**

If all else fails:

1. **Check System Resources**
   ```bash
   free -h
   df -h
   top
   ```

2. **Restart Docker**
   ```bash
   sudo systemctl restart docker
   ```

3. **Check Docker Logs**
   ```bash
   sudo journalctl -u docker.service
   ```

4. **Reboot System** (Last Resort)
   ```bash
   sudo reboot
   ```

---

## **📞 Getting Help**

### **Self-Service Resources**

1. **Check Documentation**
   - `TELEMETRY_SETUP_GUIDE.md`
   - `DEPLOYMENT_GUIDE.md`
   - `TEST_RESULTS_SUMMARY.md`

2. **Run Diagnostic Commands**
   ```bash
   # System diagnostics
   ./deploy_with_telemetry.sh health
   ./deploy_with_telemetry.sh status
   ./deploy_with_telemetry.sh logs
   ```

3. **Check Test Results**
   ```bash
   # Run comprehensive tests
   python run_telemetry_tests.py
   ```

### **When to Seek Help**

- All services down and won't restart
- Data loss or corruption
- Security incidents
- Performance issues affecting production
- Configuration changes not working

### **Information to Provide**

When seeking help, provide:

1. **System Information**
   ```bash
   uname -a
   docker --version
   docker-compose --version
   ```

2. **Error Messages**
   ```bash
   ./deploy_with_telemetry.sh logs | tail -50
   ```

3. **Configuration**
   ```bash
   cat .env | grep -v "^#" | grep -v "^$"
   ```

4. **Test Results**
   ```bash
   python run_telemetry_tests.py
   ```

---

## **🎯 Prevention Tips**

### **Regular Maintenance**

```bash
# Weekly health checks
./deploy_with_telemetry.sh health

# Monthly cleanup
./deploy_with_telemetry.sh cleanup
docker system prune -f

# Quarterly updates
docker pull arizephoenix/phoenix:latest
```

### **Monitoring Setup**

```bash
# Set up monitoring alerts
# Configure Phoenix UI alerts
# Monitor resource usage
# Track error rates
```

### **Backup Strategy**

```bash
# Daily backups
# Weekly full backups
# Monthly archive backups
# Test restore procedures
```

---

**🔧 This troubleshooting guide should help you resolve most issues with the telemetry system. If you continue to experience problems, refer to the documentation or seek additional support.** 