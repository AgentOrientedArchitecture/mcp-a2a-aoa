# Stage 2: Product Catalog Agent - Dual Framework Implementation

An intelligent agent that adds business intelligence and natural language understanding on top of the MCP server from Stage 1. Now supports both **SMOL Agents** and **Agno** frameworks for comparison and evaluation.

## Key Innovation: Dual Framework Architecture

This stage demonstrates the power of both agent frameworks:
- **SMOL Agents**: HuggingFace's lightweight agent framework with native MCP support
- **Agno Framework**: Advanced reasoning capabilities with native MCP integration via MCPTools
- **Side-by-Side Comparison**: Run both agents to evaluate capabilities
- **Benchmark Testing**: Systematic comparison of performance and reasoning quality

## Framework Comparison

| Feature | SMOL Agents | Agno Framework |
|---------|-------------|----------------|
| **MCP Integration** | ✅ Native support | ✅ Native MCPTools |
| **Reasoning** | Basic tool calling | ✅ Advanced chain-of-thought |
| **Explainability** | Standard output | ✅ Full reasoning display |
| **Performance** | Fast, lightweight | More detailed processing |
| **Memory** | Basic context | ✅ Advanced memory management |
| **Tool Analysis** | Direct execution | ✅ Result analysis and iteration |

## Features

### Core Capabilities (Both Frameworks)
- **Natural Language Understanding**: Convert complex queries into structured searches
- **Price Analysis**: Analyze price trends, identify outliers, and provide insights
- **Smart Recommendations**: Generate personalized product recommendations
- **Similar Products**: Find products similar to a reference item
- **Customer Insights**: Learn from purchase history to improve recommendations

### SMOL Agents Features
- **Native MCP Integration**: Direct tool discovery and usage
- **Lightweight**: Fast response times
- **Simple Architecture**: Easy to understand and extend

### Agno Framework Features
- **Native MCP Integration**: Built-in MCPTools for seamless MCP server connection
- **Advanced Reasoning**: Chain-of-thought reasoning with `reasoning=True`
- **Enhanced Explainability**: `show_full_reasoning=True` for detailed output
- **Tool Analysis**: Can analyze tool results and iterate on solutions
- **Memory Management**: Built-in memory capabilities for context retention
- **Multi-Model Support**: Different models for reasoning vs. response
- **Async Context Management**: Proper connection lifecycle with MCP servers

## Quick Start

### Prerequisites
- Python 3.12+
- uv package manager
- Stage 1 MCP server (must be accessible)
- API key for Claude or OpenAI

### Installation

1. Navigate to the project root:
```bash
cd /path/to/AOA
```

2. Copy and configure environment variables:
```bash
cp stage2_product_agent/.env.example stage2_product_agent/.env
# Edit stage2_product_agent/.env with your API key
```

3. Install dependencies:
```bash
uv sync
```

### Running the Agents

#### Interactive Mode (Development)

**Run SMOL Agent:**
```bash
uv run python stage2_product_agent/agent.py
```

**Run Agno Agent:**
```bash
uv run python stage2_product_agent/agno_agent.py
```

**Run Dual Agent Comparison:**
```bash
uv run python stage2_product_agent/dual_agent_runner.py
```

#### Docker Mode (Production)

1. **Build the container**:
```bash
# From the stage2_product_agent directory
cd stage2_product_agent
docker compose build
```

2. **Run the agent interactively**:

For interactive mode, you must use `docker compose run`:
```bash
# This will start the agent in interactive mode
docker compose run --rm product-agent
```

### Configuration

The `.env` file controls which framework to use:

```bash
# Agent Framework Selection
# Options: smol, agno, both (for comparison)
AGENT_FRAMEWORK=both

# Agno-specific Configuration
AGNO_REASONING=true
AGNO_SHOW_FULL_REASONING=true
AGNO_MARKDOWN=true
AGNO_DEBUG_MODE=false
```

## Testing Examples

### Basic Product Search
```bash
# Test SMOL agent
uv run python stage2_product_agent/agent.py
> Show me all electronics products

# Test Agno agent  
uv run python stage2_product_agent/agno_agent.py
> Show me all electronics products
```

### Price Analysis
```bash
# Test price range queries
> Find products under $1000
> Show me the most expensive electronics
> What's the average price of laptops?
```

### Category Analysis
```bash
# Test category-specific queries
> Show me all gaming consoles
> What clothing items are in stock?
> List all home & garden products
```

### Complex Queries
```bash
# Test multi-criteria searches
> Find electronics with 4+ star rating under $1500
> Show me in-stock laptops from DigitalPro brand
> What are the best-rated products in each category?
```

### Business Intelligence
```bash
# Test analytical queries
> Which brands have the most products?
> What's the price distribution in electronics?
> Show me products with limited stock
```

## Agent Comparison Examples

### SMOL Agent Response
```
You: Show me laptops under $1000

Agent: I'll search for laptops under $1000 for you.

[Tool: search_products]
Query: laptops under $1000
Results: Found 2 laptops under $1000

Here are the laptops under $1000:
1. SmartLife Laptop Plus - $1165.72 (above budget)
2. FutureTech Laptop - $1347.95 (above budget)

Note: No laptops found under $1000 in the current catalog.
```

### Agno Agent Response
```
You: Show me laptops under $1000

Agent: Let me think about this step by step.

**Reasoning Process:**
1. The user wants laptops under $1000
2. I need to search the product catalog for laptops
3. I should filter by price range and category
4. I'll use the search_products MCP tool to find relevant items

[Tool: search_products]
Query: laptops under $1000
Results: Found 2 laptops, but both are above $1000

**Analysis:**
I found 2 laptops in the catalog, but unfortunately both exceed the $1000 budget:
- SmartLife Laptop Plus: $1165.72
- FutureTech Laptop: $1347.95

**Recommendations:**
Based on the search results, there are no laptops under $1000 in the current catalog. However, I can suggest:

1. **Consider alternatives**: Look at other electronics categories that might fit your budget
2. **Check for sales**: Monitor for price drops on existing laptops
3. **Expand search**: Consider refurbished or older model options

The price distribution shows that laptops in this catalog start at $1165.72.
```

## MCP Integration Details

### SMOL Agents MCP Integration
```python
# SMOL agents have native MCP support
from smolagents import MCPClient

# Automatic tool discovery and registration
self.mcp_client = MCPClient(self.server_params)
self.mcp_tools = self.mcp_client.get_tools()
```

### Agno Framework MCP Integration
```python
# Agno uses MCPTools for native MCP integration
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

# Set up server parameters
server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(mcp_server_path)],
    env={**os.environ}
)

# Agno handles all MCP integration automatically
self.mcp_tools = MCPTools(server_params=server_params)

# Tools are automatically available to the agent
agent = Agent(
    tools=[self.mcp_tools],
    reasoning=True,
    show_full_reasoning=True
)
```

### Available MCP Tools (Both Frameworks)
Both agents have access to the same MCP tools from Stage 1:
- `get_schema`: Database schema information
- `query_products`: SQL query execution
- `search_products`: Product search with filters
- `get_product_by_id`: Get product details
- `get_categories`: Category statistics
- `get_price_range`: Price range information

## Testing and Validation

### Quick Tests
```bash
# Test basic setup
uv run python stage2_product_agent/tests/test_agno_agent.py
uv run python stage2_product_agent/tests/test_dual_runner.py

# Test MCP integration
uv run python stage2_product_agent/tests/test_mcp_integration.py

# Debug specific issues
uv run python stage2_product_agent/tests/debug_agno.py
```

### Expected Test Results
Both agents should return **real data** from the database:
- ✅ Electronics products with actual prices ($270-$2000 range)
- ✅ Real brands (DigitalPro, TechCorp, SmartLife, etc.)
- ✅ Actual ratings and stock status
- ✅ No fictional or made-up data

### Verification Commands
```bash
# Verify both agents work
uv run python stage2_product_agent/tests/test_mcp_integration.py

# Test specific queries
echo "Show me all electronics" | uv run python stage2_product_agent/agent.py
echo "Show me all electronics" | uv run python stage2_product_agent/agno_agent.py
```

## Benchmark Testing

Run systematic comparison tests:

```bash
# Run benchmark comparison
uv run python stage2_product_agent/tests/benchmark.py
```

The benchmark tests:
- **Basic Search**: Simple product queries
- **Complex Search**: Multi-criteria filtering
- **Price Analysis**: Statistical analysis
- **Recommendations**: Personalized suggestions
- **Data Analysis**: Category comparisons
- **Similar Products**: Feature-based matching
- **Business Intelligence**: Strategic insights
- **Natural Language**: Intent understanding
- **Reasoning**: Complex problem solving
- **Explainability**: Detailed reasoning display

## Architecture

### SMOL Agent Architecture
```
User Query → SMOL Agent → MCP Tools → Database
                ↓
            LLM Processing
                ↓
            Direct Response
```

### Agno Agent Architecture
```
User Query → Agno Agent → Reasoning Process → MCPTools → MCP Server → Database
                ↓                    ↓
            LLM Processing    Tool Result Analysis
                ↓                    ↓
            Iterative Refinement → Final Response
```

### Dual Agent Comparison
```
User Query → Dual Agent Runner
                ↓
        ┌─────────────┬─────────────┐
        ↓             ↓             ↓
    SMOL Agent   Agno Agent   Comparison
        ↓             ↓             ↓
    Direct      Reasoning      Side-by-Side
   Response     Process        Analysis
```

## Development

### Running Tests
```bash
# Test Agno agent setup
uv run python stage2_product_agent/tests/test_agno_agent.py

# Test dual agent runner
uv run python stage2_product_agent/tests/test_dual_runner.py

# Test MCP integration
uv run python stage2_product_agent/tests/test_mcp_integration.py

# Run all tests
uv run pytest stage2_product_agent/tests/
```

### Code Quality
```bash
# Format
uv run black stage2_product_agent/

# Lint
uv run ruff check stage2_product_agent/

# Type check
uv run mypy stage2_product_agent/
```

## Framework Selection Guide

### Choose SMOL Agents when:
- You need fast, lightweight responses
- Simple tool calling is sufficient
- You want minimal resource usage
- Native MCP integration is priority

### Choose Agno Framework when:
- You need advanced reasoning capabilities
- Detailed explainability is important
- Complex problem-solving is required
- Tool result analysis is needed
- Memory and context retention is important
- You want to leverage MCPTools for seamless MCP integration

### Use Both for:
- Framework comparison and evaluation
- Understanding strengths of each approach
- Making informed decisions for Stage 3
- Learning different agent patterns

## Performance Considerations

### SMOL Agents
- **Pros**: Fast response times, low resource usage, native MCP support
- **Cons**: Limited reasoning depth, basic explainability

### Agno Framework
- **Pros**: Advanced reasoning, detailed explanations, native MCPTools integration
- **Cons**: Slower response times, higher resource usage

## MCP Integration Comparison

### SMOL Agents MCP Integration
- **Native Support**: Built-in MCPClient
- **Tool Discovery**: Automatic tool registration
- **Communication**: Stdio transport
- **Complexity**: Simple, direct integration

### Agno Framework MCP Integration
- **Native Support**: MCPTools class
- **Tool Discovery**: Automatic via MCPTools
- **Communication**: Multiple transport support (stdio, HTTP, SSE)
- **Complexity**: Advanced with async context management
- **Features**: Connection lifecycle management, multi-server support

## Next Steps

This dual-agent implementation provides the foundation for:
1. **Framework Evaluation**: Systematic comparison of capabilities
2. **Stage 3 Decision**: Informed choice for A2A protocol implementation
3. **Hybrid Approaches**: Combining strengths of both frameworks
4. **Performance Optimization**: Understanding trade-offs and optimization opportunities

## Troubleshooting

### Common Issues

**Agno agent fails to initialize:**
- Check API key configuration in `.env`
- Verify MCP server path is correct
- Ensure all dependencies are installed
- Check that MCPTools can connect to the server

**SMOL agent not responding:**
- Verify MCP server is running
- Check tool discovery and registration
- Review agent configuration

**Dual agent comparison fails:**
- Ensure both agents can be initialized
- Check environment configuration
- Verify API keys are set correctly

**MCP connection issues:**
- Verify MCP server is accessible
- Check server parameters in agent configuration
- Ensure proper async context management for Agno

**Agents returning fictional data:**
- Ensure MCP tools are properly connected
- Check that agents are using real database queries
- Verify tool discovery is working

### Debug Mode

Enable debug mode for Agno agent:
```bash
AGNO_DEBUG_MODE=true
```

This will show detailed tool calls and reasoning processes.

### MCP Connection Debugging

For Agno MCP issues:
```python
# Test MCP connection directly
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

server_params = StdioServerParameters(
    command="python",
    args=["stage1_mcp_product_server/server_fastmcp.py"],
    env={**os.environ}
)

async with MCPTools(server_params=server_params) as mcp_tools:
    # Test connection
    print("MCP tools available:", len(mcp_tools.tools))
```

### Verification Tests
```bash
# Test that agents return real data
uv run python stage2_product_agent/tests/test_mcp_integration.py

# Test specific queries
echo "Show me electronics under $1000" | uv run python stage2_product_agent/agent.py
echo "Show me electronics under $1000" | uv run python stage2_product_agent/agno_agent.py
```

## Contributing

When adding new features:
1. Implement for both frameworks when possible
2. Add corresponding tests
3. Update benchmark queries
4. Document differences in behavior
5. Test MCP integration for both frameworks

---

This dual-agent implementation demonstrates the evolution from simple tool calling to advanced reasoning capabilities, with both frameworks providing native MCP integration for seamless data access and analysis. **Both agents now successfully use real MCP data from the product catalog database.**