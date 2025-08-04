#!/bin/bash

# Enhanced A2A Multi-Agent System Deployment Script with Telemetry
# This script deploys the complete multi-agent system with Phoenix telemetry

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
ENV_FILE="$SCRIPT_DIR/env.telemetry.example"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "All prerequisites are satisfied"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Check if .env file exists, if not copy from example
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        if [ -f "$ENV_FILE" ]; then
            cp "$ENV_FILE" "$SCRIPT_DIR/.env"
            print_warning "Created .env file from example. Please edit it with your configuration."
        else
            print_error "Environment file not found. Please create .env file manually."
            exit 1
        fi
    fi
    
    # Load environment variables
    if [ -f "$SCRIPT_DIR/.env" ]; then
        export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
        print_success "Environment variables loaded"
    fi
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    
    # Build MCP Product Server
    print_status "Building MCP Product Server..."
    cd "$PROJECT_ROOT"
    docker build -f stage3_multi_agent/product.Dockerfile -t aoa-mcp-product-server .
    
    # Build Enhanced Agents
    print_status "Building Enhanced Agents..."
    cd "$PROJECT_ROOT"
    docker build -f stage3_multi_agent/product.Dockerfile -t aoa-enhanced-product-agent .
    docker build -f stage3_multi_agent/inventory.Dockerfile -t aoa-enhanced-inventory-agent .
    docker build -f stage3_multi_agent/sales.Dockerfile -t aoa-enhanced-sales-agent .
    
    print_success "All images built successfully"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    cd "$SCRIPT_DIR"
    
    # Start Phoenix first
    print_status "Starting Phoenix telemetry service..."
    docker compose -f "$COMPOSE_FILE" up -d phoenix
    
    # Wait for Phoenix to be healthy
    print_status "Waiting for Phoenix to be ready..."
    timeout=120
    counter=0
    while [ $counter -lt $timeout ]; do
        if docker compose -f "$COMPOSE_FILE" ps phoenix | grep -q "healthy"; then
            print_success "Phoenix is ready"
            break
        fi
        sleep 2
        counter=$((counter + 2))
        echo -n "."
    done
    
    if [ $counter -ge $timeout ]; then
        print_error "Phoenix failed to start within timeout"
        exit 1
    fi
    
    # Start all agents
    print_status "Starting enhanced agents..."
    docker compose -f "$COMPOSE_FILE" up -d product-agent inventory-agent sales-agent web-ui
    
    print_success "All services started"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    cd "$SCRIPT_DIR"
    
    # Check all services
    services=("phoenix" "product-agent" "inventory-agent" "sales-agent" "web-ui")
    
    for service in "${services[@]}"; do
        print_status "Checking $service..."
        if docker compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy"; then
            print_success "$service is healthy"
        else
            print_warning "$service is not healthy"
        fi
    done
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    cd "$SCRIPT_DIR"
    docker compose -f "$COMPOSE_FILE" ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Phoenix UI: http://localhost:6006"
    echo "  Web UI: http://localhost:3000"
    echo "  Product Agent: http://localhost:8001"
    echo "  Inventory Agent: http://localhost:8002"
    echo "  Sales Agent: http://localhost:8003"
    echo "  MCP Product Server: http://localhost:8000"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    cd "$SCRIPT_DIR"
    docker compose -f "$COMPOSE_FILE" down
    print_success "All services stopped"
}

# Function to show logs
show_logs() {
    local service=${1:-"all"}
    print_status "Showing logs for $service..."
    cd "$SCRIPT_DIR"
    docker compose -f "$COMPOSE_FILE" logs -f "$service"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    cd "$SCRIPT_DIR"
    docker compose -f "$COMPOSE_FILE" down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to run tests
run_tests() {
    print_status "Running telemetry tests..."
    cd "$SCRIPT_DIR"
    
    # Wait for services to be ready
    sleep 10
    
    # Run the comprehensive test
    if [ -f "test_all_enhanced_agents.py" ]; then
        python test_all_enhanced_agents.py
    else
        print_warning "Test file not found"
    fi
    
    # Run web UI integration test
    print_status "Running web UI integration tests..."
    if [ -f "test_web_ui_integration.py" ]; then
        python test_web_ui_integration.py
    else
        print_warning "Web UI test file not found"
    fi
}

# Function to show help
show_help() {
    echo "Enhanced A2A Multi-Agent System Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy      - Deploy the complete system with telemetry"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  status      - Show service status"
    echo "  logs        - Show logs (optional: specify service name)"
    echo "  health      - Check service health"
    echo "  test        - Run telemetry tests"
    echo "  cleanup     - Clean up all containers and volumes"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 logs phoenix"
    echo "  $0 test"
}

# Main script logic
case "${1:-help}" in
    "deploy")
        check_prerequisites
        setup_environment
        build_images
        start_services
        check_health
        show_status
        print_success "Deployment completed successfully!"
        echo ""
        print_status "Next steps:"
        echo "  1. Open Web UI at http://localhost:3000"
        echo "  2. Open Phoenix UI at http://localhost:6006"
        echo "  3. Run tests: $0 test"
        echo "  4. Check logs: $0 logs"
        ;;
    "start")
        check_prerequisites
        setup_environment
        start_services
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "health")
        check_health
        ;;
    "test")
        run_tests
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        show_help
        ;;
esac 