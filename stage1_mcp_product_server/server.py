"""MCP Server for Product Catalog - Stage 1 of Agent Oriented Architecture.

This server provides tools for interacting with a product catalog database
via the Model Context Protocol (MCP). It demonstrates the foundation of AOA
by enabling LLMs to access structured data through a standardized protocol.
"""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

try:
    from .database import (
        init_database,
        seed_database,
        get_schema_info,
        execute_query,
    )
except ImportError:
    # For direct execution
    from database import (  # type: ignore
        init_database,  # type: ignore
        seed_database,  # type: ignore
        get_schema_info,  # type: ignore
        execute_query,  # type: ignore
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("product-catalog")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for the product catalog."""
    return [
        types.Tool(
            name="get_schema",
            description="Get information about the product catalog database schema",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="query_products",
            description="Execute a SQL query on the product catalog (read-only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute",
                    }
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="search_products",
            description="Search for products by name, category, or brand",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Term to search for in product names, categories, or brands",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by product category (optional)",
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price filter (optional)",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter (optional)",
                    },
                    "in_stock_only": {
                        "type": "boolean",
                        "description": "Only show products in stock (optional)",
                        "default": False,
                    },
                },
                "required": ["search_term"],
            },
        ),
        types.Tool(
            name="get_product_by_id",
            description="Get detailed information about a specific product by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "The product ID"}
                },
                "required": ["product_id"],
            },
        ),
        types.Tool(
            name="get_categories",
            description="Get a list of all product categories with counts",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="get_price_range",
            description="Get the minimum and maximum prices in the catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category (optional)",
                    }
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for the product catalog."""

    try:
        if name == "get_schema":
            schema_info = get_schema_info()
            return [
                types.TextContent(type="text", text=json.dumps(schema_info, indent=2))
            ]

        elif name == "query_products":
            if not arguments or "query" not in arguments:
                raise ValueError("Query parameter is required")

            query = arguments["query"]
            results = execute_query(query)

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {"query": query, "row_count": len(results), "results": results},
                        indent=2,
                    ),
                )
            ]

        elif name == "search_products":
            if not arguments or "search_term" not in arguments:
                raise ValueError("search_term parameter is required")

            search_term = arguments["search_term"]
            category = arguments.get("category")
            min_price = arguments.get("min_price")
            max_price = arguments.get("max_price")
            in_stock_only = arguments.get("in_stock_only", False)

            # Build query
            query = """
                SELECT * FROM products 
                WHERE (name LIKE ? OR category LIKE ? OR brand LIKE ?)
            """
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]

            if category:
                query += " AND category = ?"
                params.append(category)

            if min_price is not None:
                query += " AND price >= ?"
                params.append(min_price)

            if max_price is not None:
                query += " AND price <= ?"
                params.append(max_price)

            if in_stock_only:
                query += " AND stock_status = 'in_stock'"

            query += " ORDER BY rating DESC, name LIMIT 50"

            results = execute_query(query, tuple(params))

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "search_term": search_term,
                            "filters_applied": {
                                "category": category,
                                "min_price": min_price,
                                "max_price": max_price,
                                "in_stock_only": in_stock_only,
                            },
                            "result_count": len(results),
                            "results": results,
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "get_product_by_id":
            if not arguments or "product_id" not in arguments:
                raise ValueError("product_id parameter is required")

            product_id = arguments["product_id"]
            results = execute_query(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            )

            if not results:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"No product found with ID {product_id}"},
                            indent=2,
                        ),
                    )
                ]

            return [
                types.TextContent(type="text", text=json.dumps(results[0], indent=2))
            ]

        elif name == "get_categories":
            results = execute_query(
                """
                SELECT category, COUNT(*) as product_count,
                       MIN(price) as min_price, MAX(price) as max_price,
                       AVG(rating) as avg_rating
                FROM products
                GROUP BY category
                ORDER BY category
            """
            )

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {"total_categories": len(results), "categories": results},
                        indent=2,
                    ),
                )
            ]

        elif name == "get_price_range":
            category = arguments.get("category") if arguments else None

            if category:
                query = "SELECT MIN(price) as min_price, MAX(price) as max_price FROM products WHERE category = ?"
                results = execute_query(query, (category,))
            else:
                query = "SELECT MIN(price) as min_price, MAX(price) as max_price FROM products"
                results = execute_query(query)

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "category": category or "all",
                            "price_range": (
                                results[0]
                                if results
                                else {"min_price": 0, "max_price": 0}
                            ),
                        },
                        indent=2,
                    ),
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [
            types.TextContent(
                type="text", text=json.dumps({"error": str(e), "tool": name}, indent=2)
            )
        ]


async def run():
    """Run the MCP server."""
    # Initialize database
    init_database()
    seed_database()

    logger.info("Starting Product Catalog MCP Server...")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="product-catalog",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Entry point for the server."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
