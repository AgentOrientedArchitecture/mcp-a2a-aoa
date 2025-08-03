# Multi-Agent System Web UI

A modern web interface for interacting with the Stage 3 Multi-Agent System, featuring real-time communication visualization and an intuitive chat interface.

## Features

- **Agent Selection**: Choose which agent to interact with (Product Catalog, Inventory Management, or Sales Analytics)
- **Interactive Chat**: Send queries to agents and receive responses in real-time
- **Example Prompts**: Pre-defined queries for each agent to demonstrate capabilities
- **Communication Flow**: Visual timeline showing agent interactions and response times
- **Live Status**: Real-time agent health monitoring
- **Responsive Design**: Works on desktop and mobile devices

## Architecture

- **Frontend**: React with TypeScript and Material-UI
- **Backend**: Node.js/Express server proxying requests to agents
- **Real-time Updates**: WebSocket for live communication events
- **Container-ready**: Dockerfile for easy deployment

## Running Locally

### Prerequisites
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
cd backend
npm install
npm run dev
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The UI will be available at http://localhost:3000

## Running with Docker

The UI is integrated into the main docker-compose setup:

```bash
# From the stage3_multi_agent directory
docker compose up web-ui
```

## Example Queries

### Product Catalog Agent
- "Find all gaming laptops"
- "Show me products under $500"
- "List all products by brand TechCorp"

### Inventory Management Agent
- "Check stock level for product ID 100"
- "Which products are running low on stock?"
- "Show inventory status for warehouse Dallas"

### Sales Analytics Agent
- "What are the top 5 selling products?"
- "Show revenue by category"
- "Which brands are performing best?"

## Environment Variables

- `PRODUCT_AGENT_HOST`: Hostname for Product Agent (default: product-agent)
- `INVENTORY_AGENT_HOST`: Hostname for Inventory Agent (default: inventory-agent)
- `SALES_AGENT_HOST`: Hostname for Sales Agent (default: sales-agent)
- `PORT`: Backend server port (default: 3001)

## Development

The UI uses:
- Vite for fast development builds
- TypeScript for type safety
- Material-UI for consistent design
- React Query for efficient data fetching
- Socket.io for real-time updates