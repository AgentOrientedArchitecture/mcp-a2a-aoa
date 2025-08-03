# Multi-Agent System Web UI Demo

The web UI is now running and accessible at: **http://localhost:3000**

## Quick Start

1. Open your browser and navigate to http://localhost:3000
2. You'll see the Multi-Agent System Interface with three columns:
   - **Left**: Agent selector and example prompts
   - **Middle**: Chat interface
   - **Right**: Communication flow visualization

## Demo Walkthrough

### 1. Check Agent Status
- Look at the agent selector dropdown
- Each agent shows its status (green = online, red = offline)
- All three agents should be online

### 2. Try Example Prompts
- Select "Product Catalog Agent" from the dropdown
- Click on any example prompt like "Find all gaming laptops"
- Watch the response appear in the chat interface
- Notice the response time indicator

### 3. Test Different Agents
- Switch to "Inventory Management Agent"
- Try "Check stock level for product ID 100"
- See how the response differs from the product agent

### 4. Custom Queries
- Type your own query in the chat input
- Examples:
  - Product Agent: "Show me all products from TechCorp under $1000"
  - Inventory Agent: "Which products need restocking?"
  - Sales Agent: "What are the top selling categories?"

### 5. Communication Flow
- Watch the right panel as you send queries
- You'll see:
  - Query start events (blue)
  - Successful completions (green)
  - Any errors (red)
  - Response times for each interaction

## API Endpoints

The backend API is available at http://localhost:3001 with these endpoints:

- `GET /health` - Health check
- `GET /api/agents/status` - Get all agents' status
- `POST /api/agent/:agentName/query` - Send query to specific agent
- WebSocket at `ws://localhost:3001/ws` - Real-time updates

## Troubleshooting

If the UI doesn't load:
1. Check all containers are running: `docker ps`
2. Check agent health: `docker logs agent-web-ui`
3. Verify agents are accessible: `curl http://localhost:8001/.well-known/agent-card.json`

## Features Demonstrated

1. **Multi-Agent Interaction**: Query different specialized agents
2. **Real-time Communication**: WebSocket updates for live status
3. **Example Prompts**: Pre-defined queries to showcase capabilities
4. **Response Visualization**: JSON syntax highlighting for structured data
5. **Performance Metrics**: Response time tracking
6. **Agent Health Monitoring**: Live status indicators

Enjoy exploring the multi-agent system!