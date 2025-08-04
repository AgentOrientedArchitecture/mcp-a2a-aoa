"""MCP Server for Product Catalog using FastMCP - Stage 1 of Agent Oriented Architecture.

This server provides tools for interacting with a product catalog database
via the Model Context Protocol (MCP). It uses the FastMCP API for simpler
implementation and better Claude Desktop compatibility.
"""

import json
import logging
from typing import Optional, Union

from mcp.server.fastmcp import FastMCP

try:
    from .database import (
        init_database,
        seed_database,
        get_schema_info,
        execute_query,
    )
except ImportError:
    # For direct execution
    from database import (
        init_database,
        seed_database,
        get_schema_info,
        execute_query,
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database on import
init_database()
seed_database()

# Create FastMCP server instance
mcp = FastMCP("product-catalog")


@mcp.tool()
def get_schema() -> str:
    """Get information about the product catalog database schema."""
    try:
        schema_info = get_schema_info()
        return json.dumps(schema_info, indent=2)
    except Exception as e:
        logger.error(f"Error in get_schema: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def query_products(query: str) -> str:
    """Execute a SQL query on the product catalog (read-only).

    Args:
        query: SQL SELECT query to execute

    Returns:
        JSON string with query results
    """
    try:
        results = execute_query(query)
        return json.dumps(
            {"query": query, "row_count": len(results), "results": results}, indent=2
        )
    except Exception as e:
        logger.error(f"Error in query_products: {str(e)}")
        return json.dumps({"error": str(e), "query": query}, indent=2)


@mcp.tool()
def search_products(
    search_term: str,
    category: Optional[str] = None,
    min_price: Optional[Union[float, str]] = None,
    max_price: Optional[Union[float, str]] = None,
    in_stock_only: bool = False,
) -> str:
    """Search for products by name, category, or brand.

    Args:
        search_term: Term to search for in product names, categories, or brands
        category: Filter by product category (optional)
        min_price: Minimum price filter (optional)
        max_price: Maximum price filter (optional)
        in_stock_only: Only show products in stock (optional)

    Returns:
        JSON string with search results
    """
    try:
        # Handle string parameters by converting to appropriate types
        if isinstance(min_price, str):
            if min_price == "":
                min_price = None
            else:
                min_price = float(min_price)
                
        if isinstance(max_price, str):
            if max_price == "":
                max_price = None
            else:
                max_price = float(max_price)
                
        if category == "":
            category = None
            
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

        return json.dumps(
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
        )
    except Exception as e:
        logger.error(f"Error in search_products: {str(e)}")
        return json.dumps({"error": str(e), "search_term": search_term}, indent=2)


@mcp.tool()
def get_product_by_id(product_id: int) -> str:
    """Get detailed information about a specific product by ID.

    Args:
        product_id: The product ID

    Returns:
        JSON string with product details
    """
    try:
        results = execute_query("SELECT * FROM products WHERE id = ?", (product_id,))

        if not results:
            return json.dumps(
                {"error": f"No product found with ID {product_id}"}, indent=2
            )

        return json.dumps(results[0], indent=2)
    except Exception as e:
        logger.error(f"Error in get_product_by_id: {str(e)}")
        return json.dumps({"error": str(e), "product_id": product_id}, indent=2)


@mcp.tool()
def get_categories() -> str:
    """Get a list of all product categories with counts."""
    try:
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

        return json.dumps(
            {"total_categories": len(results), "categories": results}, indent=2
        )
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_price_range(category: Optional[str] = None) -> str:
    """Get the minimum and maximum prices in the catalog.

    Args:
        category: Filter by category (optional)

    Returns:
        JSON string with price range
    """
    try:
        if category:
            query = "SELECT MIN(price) as min_price, MAX(price) as max_price FROM products WHERE category = ?"
            results = execute_query(query, (category,))
        else:
            query = (
                "SELECT MIN(price) as min_price, MAX(price) as max_price FROM products"
            )
            results = execute_query(query)

        return json.dumps(
            {
                "category": category or "all",
                "price_range": (
                    results[0] if results else {"min_price": 0, "max_price": 0}
                ),
            },
            indent=2,
        )
    except Exception as e:
        logger.error(f"Error in get_price_range: {str(e)}")
        return json.dumps({"error": str(e), "category": category}, indent=2)


if __name__ == "__main__":
    # Run the server
    mcp.run()
