# Stage 2: Product Catalog Agent with SMOL Agents

An intelligent agent that adds business intelligence and natural language understanding on top of the MCP server from Stage 1. Built with HuggingFace's SMOL Agents framework.

## Key Innovation: SMOL Agents MCP Integration

This stage demonstrates the power of SMOL agents' native MCP support:
- **Direct MCP Tool Access**: SMOL agents automatically discovers and uses MCP tools
- **Seamless Integration**: MCPClient handles all stdio communication with the MCP server
- **Tool Composition**: Business intelligence tools can access MCP tools directly
- **No Custom Wrappers**: Clean, maintainable code using framework features

## Features

### Core Capabilities
- **Natural Language Understanding**: Convert complex queries into structured searches
- **Price Analysis**: Analyze price trends, identify outliers, and provide insights
- **Smart Recommendations**: Generate personalized product recommendations
- **Similar Products**: Find products similar to a reference item
- **Customer Insights**: Learn from purchase history to improve recommendations

### Technical Features
- **Native MCP Integration**: Uses SMOL agents' built-in MCPClient
- **SMOL Agents**: Leverages HuggingFace's agent framework
- **LLM Flexibility**: Supports Claude, GPT-4, and other models via LiteLLM
- **Docker Ready**: Containerized for easy deployment
- **Clean Architecture**: No custom wrappers needed

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

### Running the Agent

#### Interactive Mode (Development)
Run from the AOA root directory:
```bash
uv run python stage2_product_agent/agent.py
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

You'll see the startup message and can interact directly:
```
============================================================
Product Catalog Agent - Stage 2
Intelligent Assistant for Product Queries
============================================================

✅ Agent 'Product Catalog Assistant' initialized successfully!

Available capabilities:
- Natural language product search
- Price trend analysis
- Similar product recommendations
- Personalized recommendations
- Database queries

Type 'quit' to exit.

You: Show me all laptops under $1000
Agent: [Agent responds with search results]

You: What are the price trends for electronics?
Agent: [Agent provides price analysis]

You: quit
Goodbye! 👋
```

3. **Why not `docker compose up`?**

`docker compose up` is designed for services that run in the background. For interactive applications, use:
- `docker compose run --rm product-agent` - Best for interactive sessions
- `docker compose exec` - To connect to an already running container

4. **Alternative methods**:

```bash
# Run with custom environment variables
docker compose run --rm -e LOG_LEVEL=DEBUG product-agent

# Run without removing container after exit
docker compose run product-agent

# If you need to run as a service and attach later
docker compose up -d
docker attach product-catalog-agent
```

5. **View logs** (if running as service):
```bash
docker compose logs -f product-agent
```

6. **Clean up**:
```bash
# Remove stopped containers
docker compose down

# Remove with volumes
docker compose down -v
```

## Usage Examples

### Natural Language Queries
```
You: Show me laptops under $1000 that are in stock
Agent: [Searches for laptops with price < 1000 and in_stock_only=true]

You: What are the price trends for electronics?
Agent: [Analyzes price statistics, identifies outliers, provides insights]

You: Find products similar to product ID 42
Agent: [Finds products with similar characteristics and ranks by similarity]
```

### Business Intelligence
```
You: Generate recommendations for a customer who likes premium electronics
Agent: [Creates personalized recommendations based on preferences]

You: Analyze the pricing strategy for our sports category
Agent: [Provides detailed price analysis with quartiles, outliers, and insights]
```

## Architecture

```
┌─────────────────┐     Natural Language      ┌─────────────────┐
│      User       │ ◄───────────────────────► │  Product Agent  │
└─────────────────┘                           └─────────────────┘
                                                       │
                                              ┌────────┴────────┐
                                              │                 │
                                    Business Intelligence     MCP Tools
                                         Tools               (Auto-discovered)
                                              │                 │
                                              └────────┬────────┘
                                                       │
                                              ┌─────────────────┐
                                              │   MCPClient     │
                                              │  (SMOL Native)  │
                                              └─────────────────┘
                                                       │
                                                    stdio
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   MCP Server    │
                                              │   (Stage 1)     │
                                              └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │     SQLite      │
                                              │    Database     │
                                              └─────────────────┘
```

### How SMOL Agents MCP Integration Works

1. **Automatic Tool Discovery**: MCPClient connects to the MCP server and discovers all available tools
2. **Tool Registration**: Both MCP tools and custom business tools are registered with the SMOL agent
3. **Unified Interface**: The agent can seamlessly use both types of tools in response to queries
4. **Tool Composition**: Business intelligence tools receive MCP tools as dependencies and can call them directly

### Code Simplification with SMOL Agents

The SMOL agents framework dramatically simplifies MCP integration:

```python
# Initialize MCP client - that's it!
self.mcp_client = MCPClient(self.server_params)
self.mcp_tools = self.mcp_client.get_tools()

# Create business tools that use MCP tools
mcp_tools_dict = {tool.name: tool for tool in self.mcp_tools}
business_tools = [
    FindSimilarProductsTool(mcp_tools_dict),
    AnalyzePriceTrendsTool(mcp_tools_dict),
    # ...
]

# Register all tools with the agent
self.agent = CodeAgent(
    tools=list(self.mcp_tools) + business_tools,
    model=self.model,
    # ...
)
```

No need for:
- Custom MCP wrappers
- Manual tool conversion
- Complex communication handling
- Tool adapter patterns

## Tools Reference

### MCP Tools (from Stage 1)
- `get_schema`: Database schema information
- `query_products`: SQL query execution
- `search_products`: Product search with filters
- `get_product_by_id`: Get product details
- `get_categories`: Category statistics
- `get_price_range`: Price range information

### Business Intelligence Tools (Stage 2)
- `find_similar_products`: Find products similar to a reference
- `analyze_price_trends`: Comprehensive price analysis
- `generate_product_recommendations`: Personalized recommendations
- `natural_language_product_search`: NL query parsing

## Configuration

### Environment Variables
```bash
# LLM Configuration
LLM_MODEL=claude-3-7-sonnet-20250219  # or gpt-4, etc.
ANTHROPIC_API_KEY=your-key-here        # or OPENAI_API_KEY

# Agent Configuration
AGENT_NAME="Product Catalog Assistant"
LOG_LEVEL=INFO

# MCP Server Path (relative to AOA directory)
MCP_SERVER_PATH="stage1_mcp_product_server/server_fastmcp.py"
```

### Docker Configuration

#### Docker Compose Setup
The `docker-compose.yml` file provides production-ready configuration:

```yaml
services:
  product-agent:
    build:
      context: ..  # Builds from parent directory to include stage1
      dockerfile: stage2_product_agent/Dockerfile
    environment:
      - MCP_SERVER_PATH=/app/stage1_mcp_product_server/server_fastmcp.py
    env_file:
      - .env  # Load API keys and config
    stdin_open: true  # Interactive mode
    tty: true
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

#### Key Features:
- **Multi-stage build**: Optimized image size
- **Resource limits**: Prevents runaway resource usage
- **Volume persistence**: Data survives container restarts
- **Network isolation**: Secure by default
- **Interactive mode**: Full agent interaction support

#### Docker Commands Reference:
```bash
# Build without cache
docker compose build --no-cache

# Run with live logs
docker compose up

# Run specific number of instances
docker compose up --scale product-agent=3

# Execute commands in running container
docker compose exec product-agent python -c "print('test')"

# View resource usage
docker compose stats
```

## Development

### Running Tests (from AOA directory)
```bash
# All tests
uv run pytest stage2_product_agent/tests/

# Specific test file
uv run pytest stage2_product_agent/tests/test_agent.py -v

# With coverage
uv run pytest stage2_product_agent/tests/ --cov=stage2_product_agent
```

### Code Quality (from AOA directory)
```bash
# Format code
uv run black stage2_product_agent/

# Lint
uv run ruff check stage2_product_agent/

# Type checking
uv run mypy stage2_product_agent/
```

## Project Structure
```
stage2_product_agent/
├── __init__.py
├── agent.py                  # Main agent implementation
├── tools/
│   ├── __init__.py
│   └── product_tools.py     # Business intelligence tools
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_product_tools.py
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Orchestration
├── .env.example            # Environment template
└── README.md
```

## Troubleshooting

### Common Issues

1. **"No API key found" error**
   - Ensure you've created `.env` from `.env.example`
   - Add your ANTHROPIC_API_KEY or OPENAI_API_KEY

2. **"MCP server not found" error**
   - Make sure you're running from the AOA directory: `cd /path/to/AOA`
   - Check that Stage 1 is properly set up
   - Verify the MCP_SERVER_PATH in your .env
   - Default path assumes: `AOA/stage1_mcp_product_server/server_fastmcp.py`

3. **Docker build fails**
   - Ensure you're building from the stage2_product_agent directory
   - Check that both stage1 and stage2 directories exist
   - Verify Docker has access to the parent directory

4. **Can't interact with Docker container**
   - Use `docker compose run --rm product-agent` for interactive mode
   - Do NOT use `docker compose up` for interactive sessions
   - Check that `stdin_open: true` and `tty: true` are in docker-compose.yml
   - On Windows, you may need to use `winpty docker compose run --rm product-agent`
   - Ensure PYTHONUNBUFFERED=1 is set in the environment

5. **Container exits immediately**
   - Check logs: `docker compose logs product-agent`
   - Verify .env file is in the stage2_product_agent directory
   - Ensure API keys are valid

6. **Running from wrong directory**
   - Docker commands should be run from stage2_product_agent directory
   - Python commands should be run from the AOA root directory
   - Use absolute paths in .env if running from elsewhere

### Debug Mode
Enable detailed logging:
```bash
LOG_LEVEL=DEBUG uv run python stage2_product_agent/agent.py
```

## Next Steps

This agent demonstrates how SMOL Agents add intelligence to basic data access. In Stage 3, we'll:
- Add multiple data sources (inventory, sales)
- Implement multi-agent coordination with ACP
- Enable cross-domain queries

## License

MIT License - See parent project for details.