"""Tests for the MCP server."""

import pytest
import json
from unittest.mock import patch

import mcp.types as types
from stage1_mcp_product_server.server import handle_list_tools, handle_call_tool


@pytest.mark.asyncio
async def test_list_tools():
    """Test that all tools are listed correctly."""
    tools = await handle_list_tools()

    assert len(tools) == 6
    tool_names = [tool.name for tool in tools]
    assert "get_schema" in tool_names
    assert "query_products" in tool_names
    assert "search_products" in tool_names
    assert "get_product_by_id" in tool_names
    assert "get_categories" in tool_names
    assert "get_price_range" in tool_names

    # Check that all tools have proper schemas
    for tool in tools:
        assert isinstance(tool, types.Tool)
        assert tool.description is not None
        assert tool.inputSchema is not None


@pytest.mark.asyncio
async def test_get_schema_tool():
    """Test the get_schema tool."""
    with patch("stage1_mcp_product_server.server.get_schema_info") as mock_schema:
        mock_schema.return_value = {
            "table_name": "products",
            "row_count": 100,
            "categories": ["Electronics", "Books"],
        }

        result = await handle_call_tool("get_schema", {})

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        data = json.loads(result[0].text)
        assert data["table_name"] == "products"
        assert data["row_count"] == 100


@pytest.mark.asyncio
async def test_query_products_tool():
    """Test the query_products tool."""
    with patch("stage1_mcp_product_server.server.execute_query") as mock_query:
        mock_query.return_value = [{"id": 1, "name": "Test Product", "price": 99.99}]

        result = await handle_call_tool(
            "query_products", {"query": "SELECT * FROM products LIMIT 1"}
        )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        data = json.loads(result[0].text)
        assert data["row_count"] == 1
        assert len(data["results"]) == 1


@pytest.mark.asyncio
async def test_search_products_tool():
    """Test the search_products tool."""
    with patch("stage1_mcp_product_server.server.execute_query") as mock_query:
        mock_query.return_value = [
            {"id": 1, "name": "Laptop", "category": "Electronics", "price": 999.99}
        ]

        result = await handle_call_tool(
            "search_products",
            {
                "search_term": "laptop",
                "category": "Electronics",
                "min_price": 500,
                "max_price": 1500,
                "in_stock_only": True,
            },
        )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        data = json.loads(result[0].text)
        assert data["search_term"] == "laptop"
        assert data["result_count"] == 1
        assert data["filters_applied"]["category"] == "Electronics"


@pytest.mark.asyncio
async def test_get_product_by_id_tool():
    """Test the get_product_by_id tool."""
    with patch("stage1_mcp_product_server.server.execute_query") as mock_query:
        # Test successful retrieval
        mock_query.return_value = [{"id": 1, "name": "Test Product", "price": 99.99}]

        result = await handle_call_tool("get_product_by_id", {"product_id": 1})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["id"] == 1
        assert data["name"] == "Test Product"

        # Test product not found
        mock_query.return_value = []

        result = await handle_call_tool("get_product_by_id", {"product_id": 999})

        data = json.loads(result[0].text)
        assert "error" in data


@pytest.mark.asyncio
async def test_get_categories_tool():
    """Test the get_categories tool."""
    with patch("stage1_mcp_product_server.server.execute_query") as mock_query:
        mock_query.return_value = [
            {
                "category": "Electronics",
                "product_count": 25,
                "min_price": 29.99,
                "max_price": 1999.99,
                "avg_rating": 4.2,
            }
        ]

        result = await handle_call_tool("get_categories", {})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["total_categories"] == 1
        assert len(data["categories"]) == 1


@pytest.mark.asyncio
async def test_get_price_range_tool():
    """Test the get_price_range tool."""
    with patch("stage1_mcp_product_server.server.execute_query") as mock_query:
        mock_query.return_value = [{"min_price": 9.99, "max_price": 1999.99}]

        # Test without category filter
        result = await handle_call_tool("get_price_range", {})
        data = json.loads(result[0].text)
        assert data["category"] == "all"
        assert data["price_range"]["min_price"] == 9.99

        # Test with category filter
        result = await handle_call_tool("get_price_range", {"category": "Electronics"})
        data = json.loads(result[0].text)
        assert data["category"] == "Electronics"


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in tools."""
    # Test missing required parameter
    result = await handle_call_tool("query_products", {})
    data = json.loads(result[0].text)
    assert "error" in data

    # Test unknown tool
    result = await handle_call_tool("unknown_tool", {})
    data = json.loads(result[0].text)
    assert "error" in data
    assert "Unknown tool" in data["error"]
