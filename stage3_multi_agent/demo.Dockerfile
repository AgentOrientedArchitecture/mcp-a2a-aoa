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
COPY README.md ./

# Copy necessary code for demonstrations
COPY stage3_multi_agent/a2a_protocol/ ./stage3_multi_agent/a2a_protocol/
COPY stage3_multi_agent/demonstrations/ ./stage3_multi_agent/demonstrations/

# Install dependencies from pyproject.toml
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# For Docker networking
ENV DISCOVERY_METHOD=docker
ENV DISCOVERY_HOSTS=product-agent:8001,inventory-agent:8002,sales-agent:8003

# Run the Docker demo by default
CMD ["python", "stage3_multi_agent/demonstrations/docker_demo.py"]