"""Tests for the FastMCP server."""

import json
from unittest.mock import patch

from stage1_mcp_product_server.server_fastmcp import (
    get_schema,
    query_products,
    search_products,
    get_product_by_id,
    get_categories,
    get_price_range,
)


def test_get_schema():
    """Test the get_schema tool."""
    with patch(
        "stage1_mcp_product_server.server_fastmcp.get_schema_info"
    ) as mock_schema:
        mock_schema.return_value = {
            "table_name": "products",
            "row_count": 100,
            "categories": ["Electronics", "Books"],
        }

        result = get_schema()
        data = json.loads(result)

        assert data["table_name"] == "products"
        assert data["row_count"] == 100


def test_query_products():
    """Test the query_products tool."""
    with patch("stage1_mcp_product_server.server_fastmcp.execute_query") as mock_query:
        mock_query.return_value = [{"id": 1, "name": "Test Product", "price": 99.99}]

        result = query_products("SELECT * FROM products LIMIT 1")
        data = json.loads(result)

        assert data["row_count"] == 1
        assert len(data["results"]) == 1


def test_search_products():
    """Test the search_products tool."""
    with patch("stage1_mcp_product_server.server_fastmcp.execute_query") as mock_query:
        mock_query.return_value = [
            {"id": 1, "name": "Laptop", "category": "Electronics", "price": 999.99}
        ]

        result = search_products(
            search_term="laptop",
            category="Electronics",
            min_price=500,
            max_price=1500,
            in_stock_only=True,
        )

        data = json.loads(result)
        assert data["search_term"] == "laptop"
        assert data["result_count"] == 1
        assert data["filters_applied"]["category"] == "Electronics"


def test_get_product_by_id():
    """Test the get_product_by_id tool."""
    with patch("stage1_mcp_product_server.server_fastmcp.execute_query") as mock_query:
        # Test successful retrieval
        mock_query.return_value = [{"id": 1, "name": "Test Product", "price": 99.99}]

        result = get_product_by_id(1)
        data = json.loads(result)

        assert data["id"] == 1
        assert data["name"] == "Test Product"

        # Test product not found
        mock_query.return_value = []

        result = get_product_by_id(999)
        data = json.loads(result)

        assert "error" in data


def test_get_categories():
    """Test the get_categories tool."""
    with patch("stage1_mcp_product_server.server_fastmcp.execute_query") as mock_query:
        mock_query.return_value = [
            {
                "category": "Electronics",
                "product_count": 25,
                "min_price": 29.99,
                "max_price": 1999.99,
                "avg_rating": 4.2,
            }
        ]

        result = get_categories()
        data = json.loads(result)

        assert data["total_categories"] == 1
        assert len(data["categories"]) == 1


def test_get_price_range():
    """Test the get_price_range tool."""
    with patch("stage1_mcp_product_server.server_fastmcp.execute_query") as mock_query:
        mock_query.return_value = [{"min_price": 9.99, "max_price": 1999.99}]

        # Test without category filter
        result = get_price_range()
        data = json.loads(result)
        assert data["category"] == "all"
        assert data["price_range"]["min_price"] == 9.99

        # Test with category filter
        result = get_price_range("Electronics")
        data = json.loads(result)
        assert data["category"] == "Electronics"


def test_error_handling():
    """Test error handling in tools."""
    with patch("stage1_mcp_product_server.server_fastmcp.execute_query") as mock_query:
        mock_query.side_effect = Exception("Database error")

        # Test query_products error
        result = query_products("SELECT * FROM products")
        data = json.loads(result)
        assert "error" in data
        assert "Database error" in data["error"]
