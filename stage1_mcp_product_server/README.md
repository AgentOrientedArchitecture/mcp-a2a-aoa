# Stage 1: MCP Product Server

A Model Context Protocol (MCP) server that provides AI assistants with direct access to a product catalog database. This is the foundation of our Agent Oriented Architecture demonstration.

## Features

- **6 MCP Tools** for comprehensive data access:
  - `get_schema`: Database schema information
  - `query_products`: Execute SQL queries (read-only)
  - `search_products`: Natural language product search
  - `get_product_by_id`: Get specific product details
  - `get_categories`: List categories with statistics
  - `get_price_range`: Price range information

- **Security First**:
  - Read-only database access
  - SQL injection prevention
  - Query validation and sanitization

- **Rich Product Data**:
  - 125+ products across 5 categories
  - Realistic pricing, ratings, and stock status
  - Comprehensive product attributes

## Quick Start

### Prerequisites

- Python 3.12+
- uv package manager
- Claude Desktop (for MCP integration)

### Installation

1. Clone and navigate to the project:
```bash
cd stage1_mcp_product_server
```

2. Install dependencies (from project root):
```bash
uv sync
```

3. Initialize the database:
```bash
uv run python stage1_mcp_product_server/database.py
```

### Running the Server

#### Standalone Mode
```bash
# Using the original low-level API server
uv run python stage1_mcp_product_server/server.py

# Using the FastMCP server (recommended for Claude Desktop)
uv run python stage1_mcp_product_server/server_fastmcp.py
```

#### Claude Desktop Integration

The easiest way to install the server for Claude Desktop is using the MCP install command:

```bash
# From the project root directory
cd /path/to/AOA
uv run mcp install stage1_mcp_product_server/server_fastmcp.py --name "Product Catalog"
```

This command will automatically:
- Configure the server for Claude Desktop
- Handle virtual environment activation
- Create the proper configuration entry

**Manual Configuration** (if needed):

After running the install command, the configuration will be added to:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

The configuration will look like:
```json
{
  "mcpServers": {
    "Product Catalog": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/absolute/path/to/stage1_mcp_product_server/server_fastmcp.py"
      ]
    }
  }
}
```

Restart Claude Desktop to load the server.

## Usage Examples

Once integrated with Claude Desktop, you can ask questions like:

- "Show me all electronics under $500"
- "What products do you have from TechCorp?"
- "Find the top-rated products in stock"
- "What's the price range for sports equipment?"
- "How many products are in each category?"

## Development

### Running Tests

```bash
# Run all tests
uv run pytest stage1_mcp_product_server/tests/

# Run with coverage
uv run pytest stage1_mcp_product_server/tests/ --cov=stage1_mcp_product_server
```

### Code Quality

```bash
# Format code
uv run black stage1_mcp_product_server/

# Lint
uv run ruff check stage1_mcp_product_server/

# Type checking
uv run mypy stage1_mcp_product_server/
```

## Architecture

```
┌─────────────┐     MCP Protocol      ┌─────────────┐
│   Claude/   │ ◄──────────────────► │ MCP Server  │
│     LLM     │                       │   (stdio)   │
└─────────────┘                       └─────────────┘
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │   SQLite    │
                                      │  Database   │
                                      └─────────────┘
```

## Project Structure

```
stage1_mcp_product_server/
├── __init__.py
├── server.py          # Original MCP server (low-level API)
├── server_fastmcp.py  # FastMCP server (recommended for Claude Desktop)
├── database.py        # Database setup and queries
├── product_catalog.db # SQLite database (auto-generated)
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_server.py
│   └── test_server_fastmcp.py
└── README.md
```

## API Reference

### Tools

#### get_schema
Returns database schema information including table structure, indexes, and statistics.

**Input**: None  
**Output**: JSON with schema details

#### query_products
Execute a read-only SQL query on the products table.

**Input**:
- `query` (string, required): SQL SELECT query

**Output**: Query results as JSON

#### search_products
Search products with multiple filter options.

**Input**:
- `search_term` (string, required): Search term
- `category` (string, optional): Filter by category
- `min_price` (number, optional): Minimum price
- `max_price` (number, optional): Maximum price
- `in_stock_only` (boolean, optional): Only show in-stock items

**Output**: Matching products as JSON

#### get_product_by_id
Get detailed information about a specific product.

**Input**:
- `product_id` (integer, required): Product ID

**Output**: Product details as JSON

#### get_categories
List all categories with product counts and statistics.

**Input**: None  
**Output**: Category statistics as JSON

#### get_price_range
Get price range information.

**Input**:
- `category` (string, optional): Filter by category

**Output**: Min/max prices as JSON

## Next Steps

This MCP server is the foundation for our Agent Oriented Architecture. In Stage 2, we'll add intelligence with SMOL agents that can understand business context and make recommendations.

## License

MIT License - See parent project for details.