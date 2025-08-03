# Stage 3: A2A Protocol - Multi-Agent Communication

This stage implements Google's A2A (Agent-to-Agent) protocol, transforming our isolated SMOL agents into a collaborative network.

## 🎯 What's New in Stage 3

- **A2A Protocol Integration**: Agents can discover and communicate with each other
- **Dynamic Discovery**: Agents find each other without hardcoded connections
- **Capability Negotiation**: Agents advertise and query capabilities
- **Async Task Handling**: Long-running operations without HTTP timeouts
- **Inter-Agent Queries**: Agents can request data from other agents

## 🤖 The Agent Network

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Product Agent      │────▶│  Inventory Agent    │────▶│   Sales Agent       │
│  Port: 8001         │◀────│  Port: 8002         │◀────│   Port: 8003        │
│                     │     │                     │     │                     │
│ • Product search    │     │ • Stock levels      │     │ • Sales analytics   │
│ • Price analysis    │     │ • Restock planning  │     │ • Customer insights │
│ • Recommendations   │     │ • Stockout predict  │     │ • Revenue forecast  │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         │                           │                           │
         └───────────────────────────┴───────────────────────────┘
                            A2A Communication
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd stage3_multi_agent
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Start All Agents

```bash
# Using Docker (recommended)
docker-compose up

# Or run individually
python agents/product_agent_a2a.py
python agents/inventory_agent_a2a.py
python agents/sales_agent_a2a.py
```

### 3. Test the System

```bash
# Check agent health
./health_check.py

# Test agent discovery
./test_scripts/test_agent_discovery.py

# Run interactive demo
./demo_agent_communication.py
```

## 📁 Project Structure

```
stage3_multi_agent/
├── a2a_protocol/          # Core A2A implementation
│   ├── base_agent.py      # Base class for all A2A agents
│   ├── agent_server.py    # A2A server setup
│   └── discovery.py       # Agent discovery client
├── agents/                # Agent implementations
│   ├── product_agent_a2a.py
│   ├── inventory_agent_a2a.py
│   └── sales_agent_a2a.py
├── agent_cards/           # Agent metadata (capabilities)
├── inventory_mcp/         # Inventory MCP server
├── sales_mcp/            # Sales MCP server
├── test_scripts/         # Testing utilities
├── demonstrations/       # Demo scripts
└── docker-compose.yml    # Multi-agent orchestration
```

## 🔧 Key Components

### Base A2A Agent

All agents inherit from `BaseA2AAgent` which provides:

```python
class BaseA2AAgent(AgentExecutor):
    def __init__(self, agent_name: str, smol_agent: Any):
        self.discovery_client = DiscoveryClient()
        self.known_agents = {}
        
    async def execute(self, context, event_queue):
        # Handles A2A message parsing
        # Routes to SMOL agent or async tasks
        
    async def query_other_agent(self, agent_name, query):
        # Enables inter-agent communication
```

### Agent Discovery

Agents discover each other through well-known endpoints:

```python
# Each agent exposes
http://localhost:8001/.well-known/agent-card.json

# Discovery process
discovery = DiscoveryClient()
agents = await discovery.discover_agents_on_ports([8001, 8002, 8003])
```

### Inter-Agent Communication

Agents communicate using JSON-RPC:

```python
# Product Agent asking Inventory Agent
response = await product_agent.query_other_agent(
    agent_name="Inventory Management Agent",
    query="Check stock for laptop SKU-123"
)
```

## 🧪 Testing

### Health Check
```bash
./health_check.py
# Output:
# ✅ Agent 'Product Catalog Agent' is healthy on port 8001
# ✅ Agent 'Inventory Management Agent' is healthy on port 8002
# ✅ Agent 'Sales Analytics Agent' is healthy on port 8003
```

### Discovery Test
```bash
./test_scripts/test_agent_discovery.py
# Shows all discovered agents and their capabilities
```

### Communication Demo
```bash
./demo_agent_communication.py
# Interactive demonstration of agents working together
```

## 🔍 Example: Multi-Agent Collaboration

**User Query**: "What gaming laptops under $1500 are in stock?"

1. **Product Agent** receives the query
2. Searches product catalog for gaming laptops < $1500
3. **Discovers** Inventory Agent via A2A
4. **Queries** Inventory Agent for stock levels
5. Returns consolidated results with availability

## 🐛 Troubleshooting

### Common Issues

1. **"No processable content found"**
   - Fixed by proper A2A message parsing (Part.root structure)

2. **Timeout errors**
   - Fixed by async task handling for complex queries

3. **Agents not discovering each other**
   - Check ports 8001-8003 are free
   - Verify DISCOVERY_METHOD environment variable

4. **Docker networking issues**
   - Use `docker-compose logs` to check agent startup
   - Ensure all agents are on the same network

## 📚 Key Learnings

1. **Message Format**: A2A SDK uses specific Pydantic models
2. **Async Handling**: Essential for LLM operations
3. **Discovery Patterns**: Both static and dynamic discovery needed
4. **Error Recovery**: Graceful degradation when agents unavailable

## 🔗 Resources

- [A2A Protocol Docs](https://github.com/google/a2a)
- [Blog Post: Stage 3 Implementation](../blog_posts/stage3_a2a_protocol.md)
- [SMOL Agents Documentation](https://huggingface.co/docs/smolagents)

## 📈 What's Next?

Stage 4 will introduce:
- A2A Registry for centralized discovery
- Dynamic agent spawning
- Advanced routing and load balancing
- Persistent task management

---

Ready to see agents working together? Start with `docker-compose up` and watch the magic happen! 🚀