# Enhanced Sales Agent Dockerfile with Telemetry
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv pip install --system .

# Install telemetry-specific dependencies
RUN uv pip install --system \
    arize-phoenix-otel \
    openinference-instrumentation-smolagents \
    openinference-instrumentation-openai \
    openinference-instrumentation-anthropic \
    psutil

# Copy application code
COPY . .

# Set environment variables for telemetry
ENV ENABLE_TELEMETRY=true
ENV PHOENIX_PROJECT_NAME=a2a-multi-agent

# Create telemetry initialization script
RUN echo '#!/bin/bash\n\
if [ "$ENABLE_TELEMETRY" = "true" ]; then\n\
    echo "Initializing OpenTelemetry with Phoenix..."\n\
    export PHOENIX_COLLECTOR_ENDPOINT=${PHOENIX_COLLECTOR_ENDPOINT:-http://phoenix:4317}\n\
fi\n\
exec python stage3_multi_agent/agents/sales_agent.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/.well-known/agent-card.json || exit 1

# Start the agent
CMD ["/app/start.sh"] 