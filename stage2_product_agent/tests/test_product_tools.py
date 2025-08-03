"""Tests for product tools functionality."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from stage2_product_agent.tools.product_tools import (
    analyze_price_trends,
    find_similar_products,
    generate_product_recommendations,
    natural_language_product_search,
)


class TestFindSimilarProducts:
    """Test the find_similar_products tool."""

    def test_find_similar_products_success(self):
        """Test finding similar products successfully."""
        # Mock MCP tools
        mock_tools = {
            "get_product_by_id": MagicMock(return_value=json.dumps({
                "id": 1,
                "name": "Test Product",
                "category": "Electronics",
                "price": 100.0,
                "rating": 4.5
            })),
            "search_products": MagicMock(return_value=json.dumps({
                "results": [
                    {"id": 2, "name": "Similar Product 1", "category": "Electronics", "price": 95.0, "rating": 4.3},
                    {"id": 3, "name": "Similar Product 2", "category": "Electronics", "price": 110.0, "rating": 4.7},
                    {"id": 1, "name": "Test Product", "category": "Electronics", "price": 100.0, "rating": 4.5},
                ]
            }))
        }
        
        result = find_similar_products(product_id=1, mcp_tools=mock_tools, max_results=2)
        result_data = json.loads(result)
        
        assert "reference_product" in result_data
        assert "similar_products" in result_data
        assert len(result_data["similar_products"]) <= 2
        assert result_data["reference_product"]["id"] == 1
        
        # Check that reference product is not in similar products
        similar_ids = [p["product"]["id"] for p in result_data["similar_products"]]
        assert 1 not in similar_ids

    def test_find_similar_products_not_found(self):
        """Test when reference product is not found."""
        mock_tools = {
            "get_product_by_id": MagicMock(return_value=json.dumps({
                "error": "Product not found"
            }))
        }
        
        result = find_similar_products(product_id=999, mcp_tools=mock_tools)
        result_data = json.loads(result)
        
        assert "error" in result_data


class TestAnalyzePriceTrends:
    """Test the analyze_price_trends tool."""

    def test_analyze_price_trends_all_products(self):
        """Test analyzing price trends for all products."""
        mock_tools = {
            "get_price_range": MagicMock(return_value=json.dumps({
                "price_range": {"min_price": 10.0, "max_price": 200.0}
            })),
            "query_products": MagicMock(return_value=json.dumps({
                "results": [
                    {"price": 10.0, "rating": 4.0, "stock_status": "in_stock"},
                    {"price": 50.0, "rating": 4.5, "stock_status": "in_stock"},
                    {"price": 100.0, "rating": 4.2, "stock_status": "out_of_stock"},
                    {"price": 200.0, "rating": 4.8, "stock_status": "in_stock"},
                ]
            }))
        }
        
        result = analyze_price_trends(category=None, mcp_tools=mock_tools)
        result_data = json.loads(result)
        
        assert "price_statistics" in result_data
        assert "outliers" in result_data
        assert "stock_distribution" in result_data
        assert "insights" in result_data
        
        stats = result_data["price_statistics"]
        assert stats["min"] == 10.0
        assert stats["max"] == 200.0
        assert stats["average"] > 0
        assert stats["median"] > 0

    def test_analyze_price_trends_by_category(self):
        """Test analyzing price trends for specific category."""
        mock_tools = {
            "get_price_range": MagicMock(return_value=json.dumps({
                "price_range": {"min_price": 20.0, "max_price": 150.0}
            })),
            "query_products": MagicMock(return_value=json.dumps({
                "results": [
                    {"price": 20.0, "rating": 4.0, "stock_status": "in_stock"},
                    {"price": 80.0, "rating": 4.5, "stock_status": "in_stock"},
                    {"price": 150.0, "rating": 4.8, "stock_status": "in_stock"},
                ]
            }))
        }
        
        result = analyze_price_trends(category="Electronics", mcp_tools=mock_tools)
        result_data = json.loads(result)
        
        assert result_data["category"] == "Electronics"
        assert "price_statistics" in result_data


class TestGenerateProductRecommendations:
    """Test the generate_product_recommendations tool."""

    def test_recommendations_with_preferences(self):
        """Test generating recommendations based on preferences."""
        mock_tools = {
            "search_products": MagicMock(return_value=json.dumps({
                "results": [
                    {"id": 1, "name": "Budget Phone", "category": "Electronics", "price": 200.0, "rating": 4.2},
                    {"id": 2, "name": "Premium Phone", "category": "Electronics", "price": 800.0, "rating": 4.8},
                ]
            }))
        }
        
        preferences = {
            "budget_max": 500,
            "categories": ["Electronics"],
            "min_rating": 4.0,
            "in_stock_only": True
        }
        
        result = generate_product_recommendations(
            customer_preferences=preferences,
            mcp_tools=mock_tools,
            max_recommendations=5
        )
        result_data = json.loads(result)
        
        assert "recommendations" in result_data
        assert "preferences_used" in result_data
        
        # Should only recommend the budget phone due to price constraint
        recommendations = result_data["recommendations"]
        for rec in recommendations:
            assert rec["product"]["price"] <= 500

    def test_recommendations_empty_preferences(self):
        """Test handling empty preferences."""
        mock_tools = {
            "search_products": MagicMock(return_value=json.dumps({
                "results": []
            }))
        }
        
        result = generate_product_recommendations(
            customer_preferences={},
            mcp_tools=mock_tools
        )
        result_data = json.loads(result)
        
        assert "recommendations" in result_data
        assert result_data["recommendations"] == []


class TestNaturalLanguageProductSearch:
    """Test the natural_language_product_search tool."""

    def test_parse_price_constraints(self):
        """Test parsing price constraints from natural language."""
        mock_tools = {
            "search_products": MagicMock(return_value=json.dumps({
                "results": [{"id": 1, "name": "Test", "price": 50.0}]
            }))
        }
        
        # Test "under" constraint
        result = natural_language_product_search(
            query="laptops under $1000",
            mcp_tools=mock_tools
        )
        result_data = json.loads(result)
        
        assert result_data["interpreted_as"]["price_range"]["max"] == 1000.0
        
        # Test "between" constraint
        result = natural_language_product_search(
            query="phones between $200 and $500",
            mcp_tools=mock_tools
        )
        result_data = json.loads(result)
        
        assert result_data["interpreted_as"]["price_range"]["min"] == 200.0
        assert result_data["interpreted_as"]["price_range"]["max"] == 500.0

    def test_parse_category_and_stock(self):
        """Test parsing category and stock requirements."""
        mock_tools = {
            "search_products": MagicMock(return_value=json.dumps({
                "results": []
            }))
        }
        
        result = natural_language_product_search(
            query="Electronics in stock under $500",
            mcp_tools=mock_tools
        )
        result_data = json.loads(result)
        
        interpreted = result_data["interpreted_as"]
        assert interpreted["category"] == "Electronics"
        assert interpreted["in_stock_only"] is True
        assert interpreted["price_range"]["max"] == 500.0

    def test_complex_natural_language_query(self):
        """Test complex natural language query parsing."""
        mock_tools = {
            "search_products": MagicMock(return_value=json.dumps({
                "results": []
            }))
        }
        
        result = natural_language_product_search(
            query="I need a good book for my vacation, preferably under $20 and available now",
            mcp_tools=mock_tools
        )
        result_data = json.loads(result)
        
        interpreted = result_data["interpreted_as"]
        assert interpreted["category"] == "Books"
        assert interpreted["in_stock_only"] is True
        assert interpreted["price_range"]["max"] == 20.0