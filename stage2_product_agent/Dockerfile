# Stage 2: Product Agent Dockerfile
# Multi-stage build for efficient image size

# Builder stage
FROM python:3.12-slim as builder

# Install uv for fast dependency installation
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv pip install --system --no-cache .

# Runtime stage
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 agent

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application code
COPY stage2_product_agent/ ./stage2_product_agent/
COPY stage1_mcp_product_server/ ./stage1_mcp_product_server/

# Change ownership to non-root user
RUN chown -R agent:agent /app

# Switch to non-root user
USER agent

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/home/agent/.local/bin:${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import smolagents; print('healthy')" || exit 1

# Default command - run the agent with unbuffered output for interactive mode
CMD ["python", "-u", "-m", "stage2_product_agent.agent"]