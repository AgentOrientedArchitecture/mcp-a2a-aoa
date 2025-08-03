# Stage 3: A2A Protocol Implementation Plan

## Overview
Transform the existing multi-agent system to use A2A protocol for agent discovery and communication, demonstrating how three specialized agents can collaborate through Agent Cards.

## Agents to Implement

### 1. Product Catalog Agent (from Stage 2)
- Already exists and works with MCP
- Add A2A protocol support
- Create Agent Card describing capabilities

### 2. Inventory Management Agent  
- Adapt existing agent from current Stage 3
- Remove ACP decorators, keep SMOL functionality
- Add A2A protocol support
- Create Agent Card

### 3. Sales Analytics Agent
- Adapt existing agent from current Stage 3
- Remove ACP decorators, keep SMOL functionality  
- Add A2A protocol support
- Create Agent Card

## A2A Implementation Details

### Agent Cards Structure
Each agent needs an Agent Card following the A2A specification:
```json
{
  "name": "Product Catalog Agent",
  "description": "Intelligent product search and analysis",
  "version": "1.0.0",
  "capabilities": [
    {
      "name": "product_search",
      "description": "Natural language product search",
      "input_schema": {...},
      "output_schema": {...}
    }
  ],
  "endpoints": {
    "http": "http://localhost:8001/agent",
    "websocket": "ws://localhost:8001/ws"
  },
  "supported_protocols": ["a2a/1.0"],
  "authentication": "bearer_token"
}
```

### A2A Protocol Endpoints
Each agent needs to implement:
1. `GET /.well-known/agent-card.json` - Serve the Agent Card
2. `POST /agent/discover` - Discover other agents
3. `POST /agent/communicate` - Handle inter-agent messages
4. `WebSocket /agent/stream` - Real-time communication

### Communication Patterns
1. **Direct Communication**: Agent A directly calls Agent B
2. **Broadcast Discovery**: Agent broadcasts capability needs
3. **Negotiated Collaboration**: Agents negotiate task delegation

## Directory Structure
```
stage3_multi_agent/
├── README.md
├── agents/
│   ├── product_agent.py      # From Stage 2, with A2A
│   ├── inventory_agent.py    # Adapted, with A2A
│   └── sales_agent.py        # Adapted, with A2A
├── agent_cards/
│   ├── product_agent.json
│   ├── inventory_agent.json
│   └── sales_agent.json
├── a2a_protocol/
│   ├── __init__.py
│   ├── server.py             # A2A server implementation
│   ├── client.py             # A2A client for agent communication
│   └── discovery.py          # Discovery mechanisms
├── inventory_mcp/            # Keep as-is
├── sales_mcp/                # Keep as-is
├── docker-compose.yml        # Updated for A2A
└── demonstrations/
    ├── direct_communication.py
    ├── agent_discovery.py
    └── collaborative_query.py
```

## Implementation Steps

### Phase 1: Clean Up Existing Code
1. Remove all ACP imports and decorators from agents
2. Remove `acp_integration/` directory
3. Keep MCP servers unchanged (they work perfectly)
4. Update imports to remove ACP references

### Phase 2: Add A2A Protocol
1. Install A2A SDK: `uv add a2a-sdk`
2. Create base A2A server implementation
3. Add A2A endpoints to each agent
4. Implement Agent Card serving

### Phase 3: Create Agent Cards
1. Define capabilities for each agent
2. Create JSON Agent Cards
3. Implement card validation
4. Add discovery endpoints

### Phase 4: Implement Communication
1. Add inter-agent communication handlers
2. Implement message routing
3. Create streaming endpoints for real-time updates
4. Add authentication/authorization

### Phase 5: Create Demonstrations
1. **Direct Communication Demo**: Product agent queries inventory agent
2. **Discovery Demo**: Sales agent discovers available agents
3. **Collaborative Demo**: Multi-agent query processing

## Example Scenarios

### Scenario 1: Stock Check Before Recommendation
```
User -> Product Agent: "Show me laptops we have in stock"
Product Agent -> Inventory Agent: "Check stock for category:laptops"
Inventory Agent -> Product Agent: [Stock levels]
Product Agent -> User: "Here are available laptops..."
```

### Scenario 2: Sales-Informed Inventory
```
User -> Inventory Agent: "What should we reorder?"
Inventory Agent -> Sales Agent: "Get sales velocity for all products"
Sales Agent -> Inventory Agent: [Sales data]
Inventory Agent -> User: "Based on sales trends, reorder..."
```

### Scenario 3: Three-Agent Collaboration
```
User -> Any Agent: "Which products have high returns but low stock?"
Agent -> Discovers other agents via A2A
Agent -> Coordinates: Product data + Return analysis + Stock levels
Agents -> User: Comprehensive analysis
```

## Blog Post Outline

### Title: "Agent Discovery - Making AI Agents Social with A2A Protocol"

1. **Introduction**: The need for agent collaboration
2. **A2A Protocol Overview**: Agent Cards and discovery
3. **Implementation Walkthrough**: Step-by-step A2A integration
4. **Live Demonstrations**: Real agent interactions
5. **Comparison to UDDI**: Learning from the past
6. **What's Next**: Dynamic registries in Stage 4

## Success Criteria
- [ ] All three agents have A2A endpoints
- [ ] Agent Cards are properly formatted and served
- [ ] Agents can discover each other
- [ ] Direct agent-to-agent communication works
- [ ] Demonstrations show real collaboration
- [ ] Blog post with working code examples