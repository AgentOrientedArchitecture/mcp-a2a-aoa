FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./

# Copy necessary code
COPY stage3_multi_agent/inventory_mcp/ ./stage3_multi_agent/inventory_mcp/
COPY stage3_multi_agent/sales_mcp/ ./stage3_multi_agent/sales_mcp/
COPY stage3_multi_agent/agents/ ./stage3_multi_agent/agents/
COPY stage3_multi_agent/a2a_protocol/ ./stage3_multi_agent/a2a_protocol/
COPY stage3_multi_agent/agent_cards/ ./stage3_multi_agent/agent_cards/

# Install dependencies from pyproject.toml
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV INVENTORY_AGENT_PORT=8002
ENV A2A_HOST=0.0.0.0

# For Docker networking
ENV DISCOVERY_METHOD=docker

# Cross-domain access
ENV INVENTORY_CROSS_DOMAIN=true

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the A2A agent
CMD ["python", "stage3_multi_agent/agents/inventory_agent_a2a.py"]