# Agent Oriented Architecture (AOA) Project

## Project Overview
This project demonstrates the evolution from simple data access through MCP to a complete Agent Oriented Architecture, showcasing practical implementations of MCP, A2A protocols, and emergent agent systems.

## Environment & Tools
- **Python**: 3.12
- **Package Manager**: uv (NOT pip, poetry, or conda)
- **MCP Server**: Context7 enabled for real-time documentation
- **Container**: Docker for agent deployment (from Stage 2 onwards)
- **Working Directory**: `/home/lewis/work/AOA`
- **Default LLM Model**: claude-3-7-sonnet-20250219
- **Default LLM Model**: claude-3-7-sonnet-20250219

## Development Philosophy
- **Use existing frameworks and SDKs** - Never reinvent the wheel
- **Leverage Context7 MCP** - Always consult current documentation for libraries
- **Follow SDK patterns** - Use official SDK examples and best practices
- **Incremental complexity** - Each stage builds on the previous

## Package Management with UV
```bash
# Project initialization
uv init                     # Create new project
uv python pin 3.12          # Pin Python version
uv add <package>            # Add dependencies
uv add --dev <package>      # Add dev dependencies
uv sync                     # Sync environment from lock file
uv run <command>            # Run commands in project environment
```

## Core Dependencies
```bash
# Stage 1: MCP Foundation
uv add mcp sqlite3

# Stage 2: SMOL Agents
uv add "smolagents[all]"

# Stage 3: A2A Protocol
uv add a2a-sdk

# Stage 4: AOA Foundation
# A2A SDK already added in Stage 3

# Development tools
uv add --dev pytest pytest-asyncio ruff black mypy
```

## Project Structure
```
/home/lewis/work/AOA/
├── README.md
├── pyproject.toml
├── uv.lock
├── claude.md (this file)
├── stage1_mcp_product_server/
│   ├── __init__.py
│   ├── server.py           # MCP server implementation
│   ├── database.py         # SQLite initialization
│   ├── product_catalog.db  # SQLite database
│   └── tests/
├── stage2_product_agent/
│   ├── __init__.py
│   ├── agent.py            # SMOL agent implementation
│   ├── Dockerfile
│   └── tests/
├── stage3_multi_agent/
│   ├── inventory_mcp/
│   ├── sales_mcp/
│   ├── agents/
│   ├── agent_cards/
│   ├── docker-compose.yml
│   └── tests/
├── stage4_a2a_discovery/
│   ├── crm_mcp/
│   ├── agent_registry/
│   ├── orchestrator/
│   └── tests/
├── stage5_aoa_complete/
│   ├── orchestrator/
│   ├── specialized_agents/
│   ├── docker-compose.yml
│   └── demonstrations/
└── blog_posts/
    ├── stage1_mcp_foundation.md
    ├── stage2_smol_agents.md
    ├── stage3_a2a_discovery.md
    ├── stage4_aoa_foundation.md
    └── stage5_aoa_complete.md
```

## MCP Server Development Guidelines

### Stage 1: SQLite MCP Server
- Use official MCP Python SDK patterns
- Implement using `@server.tool` decorators
- Follow stdio transport protocol
- Include comprehensive error handling
- Test with Claude Desktop integration

### MCP Server Template
```python
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

server = Server("product-catalog")

@server.tool()
async def tool_name(arguments: dict) -> list[types.TextContent]:
    """Tool description for Claude"""
    # Implementation
    pass

async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="product-catalog",
                server_version="0.1.0"
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
```

## Agent Development Guidelines

### SMOL Agents (HuggingFace)
- Follow official smolagents documentation
- Use Tool and Agent base classes
- Implement proper async patterns
- Include comprehensive logging

### Docker Containerization (from Stage 2)
```dockerfile
# Use multi-stage builds
FROM python:3.12-slim as builder
RUN pip install uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv pip install --system .

FROM python:3.12-slim
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY . /app
WORKDIR /app
CMD ["python", "agent.py"]
```

## Code Quality Standards
- **Type hints**: All functions must have type annotations
- **Docstrings**: All public functions/classes need docstrings
- **Error handling**: Comprehensive try/except with logging
- **Testing**: Minimum 80% coverage with pytest
- **Formatting**: Use black and ruff for consistency

## Context7 MCP Integration
When implementing any library integration:
1. Use Context7 to fetch current documentation
2. Follow the exact patterns from official docs
3. Avoid assumptions about API behavior
4. Test against latest library versions

## Blog Post Standards
- Start with business value proposition
- Include working code snippets
- Use mermaid diagrams for architecture
- Provide "try it yourself" sections
- Each post builds on previous concepts

## Testing Strategy
```bash
# Run tests for specific stage
uv run pytest stage1_mcp_product_server/tests/

# Run all tests with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest -v stage1_mcp_product_server/tests/test_server.py
```

## Common Commands
```bash
# Start MCP server (Stage 1)
uv run python stage1_mcp_product_server/server.py

# Run agent (Stage 2+)
docker-compose up agent-name

# Format code
uv run black .
uv run ruff check --fix .

# Type checking
uv run mypy .
```

## Important Reminders
1. **Always use uv** for package management, not pip
2. **Consult Context7** for library usage patterns
3. **Follow SDK examples** rather than creating custom implementations
4. **Test with Claude Desktop** for MCP servers
5. **Use Docker** for all agents after Stage 1
6. **Document everything** in blog posts with working examples

## Security Considerations
- Never commit `.env` files or secrets
- Use environment variables for configuration
- Implement proper authentication for agent communication
- Follow principle of least privilege for agent permissions

## Performance Guidelines
- Implement connection pooling for databases
- Use async/await for I/O operations
- Cache frequently accessed data
- Monitor resource usage in Docker containers

## Debugging Tips
- Use MCP Inspector for protocol debugging
- Enable verbose logging during development
- Test agents in isolation before integration
- Use Docker logs for containerized services

---

This project demonstrates cutting-edge agent architectures. Each stage has working code that can be run and tested. Focus on practical implementation over theoretical perfection.