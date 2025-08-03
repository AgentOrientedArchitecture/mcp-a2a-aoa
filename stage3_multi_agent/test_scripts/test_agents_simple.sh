#!/bin/bash
# Simple test script for A2A agents using curl

echo "=== Testing A2A Agents ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test agent card endpoints
echo "1. Testing Agent Card Endpoints:"
echo "--------------------------------"

echo -n "Product Agent: "
if curl -s http://localhost:8001/.well-known/agent-card.json | jq -e '.name' > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Agent card available"
    curl -s http://localhost:8001/.well-known/agent-card.json | jq '{name, description}'
else
    echo -e "${RED}✗${NC} Failed to fetch agent card"
fi
echo ""

echo -n "Inventory Agent: "
if curl -s http://localhost:8002/.well-known/agent-card.json | jq -e '.name' > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Agent card available"
    curl -s http://localhost:8002/.well-known/agent-card.json | jq '{name, description}'
else
    echo -e "${RED}✗${NC} Failed to fetch agent card"
fi
echo ""

echo -n "Sales Agent: "
if curl -s http://localhost:8003/.well-known/agent-card.json | jq -e '.name' > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Agent card available"
    curl -s http://localhost:8003/.well-known/agent-card.json | jq '{name, description}'
else
    echo -e "${RED}✗${NC} Failed to fetch agent card"
fi
echo ""

# Test JSON-RPC endpoints
echo ""
echo "2. Testing JSON-RPC Communication:"
echo "----------------------------------"

# Function to send JSON-RPC request and get task result
test_agent_rpc() {
    local name=$1
    local port=$2
    local query=$3
    
    echo "Testing $name with query: \"$query\""
    
    # Send message to create task - A2A SDK uses 'message/send' method
    response=$(curl -s -X POST "http://localhost:$port/" \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": "msg-'"$(date +%s)"'",
                    "role": "user",
                    "parts": [{
                        "text": "'"$query"'"
                    }]
                }
            },
            "id": 1
        }')
    
    # Extract task ID
    task_id=$(echo "$response" | jq -r '.result.taskId // empty')
    
    if [ -n "$task_id" ]; then
        echo -e "  ${GREEN}✓${NC} Task created: $task_id"
        
        # Wait for task to complete
        sleep 2
        
        # Get task result - A2A SDK uses 'tasks/get' method
        task_response=$(curl -s -X POST "http://localhost:$port/" \
            -H "Content-Type: application/json" \
            -d '{
                "jsonrpc": "2.0",
                "method": "tasks/get",
                "params": {"id": "'"$task_id"'"},
                "id": 2
            }')
        
        # Extract task state and message
        state=$(echo "$task_response" | jq -r '.result.task.state // empty')
        
        if [ "$state" = "completed" ]; then
            echo -e "  ${GREEN}✓${NC} Task completed"
            # Extract and display the response (first 200 chars)
            message=$(echo "$task_response" | jq -r '.result.task.messages[0].content[0].text // empty' | head -c 200)
            echo "  Response: $message..."
        else
            echo -e "  Task state: $state"
            echo "$task_response" | jq '.result.task'
        fi
    else
        echo -e "  ${RED}✗${NC} Failed to create task"
        echo "  Error: $response"
    fi
    echo ""
}

# Test each agent
test_agent_rpc "Product Agent" 8001 "Show me wireless headphones under 200 dollars"
test_agent_rpc "Inventory Agent" 8002 "What is the stock level for product P001?"
test_agent_rpc "Sales Agent" 8003 "What were the best selling products last month?"

# Test health endpoints
echo ""
echo "3. Testing Health Endpoints:"
echo "----------------------------"

for agent in "Product:8001" "Inventory:8002" "Sales:8003"; do
    name="${agent%:*}"
    port="${agent#*:}"
    
    echo -n "$name Agent: "
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health")
    if [ "$status" = "200" ]; then
        echo -e "${GREEN}✓${NC} Healthy"
    else
        echo -e "${RED}✗${NC} Unhealthy (HTTP $status)"
    fi
done

echo ""
echo "=== Tests Complete ==="