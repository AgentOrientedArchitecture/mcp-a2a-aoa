"""Tests for the database module."""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from stage1_mcp_product_server.database import (
    init_database,
    seed_database,
    get_connection,
    execute_query,
    get_schema_info,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    # Patch the get_database_path function
    with patch(
        "stage1_mcp_product_server.database.get_database_path", return_value=db_path
    ):
        init_database()
        yield db_path

    # Cleanup
    db_path.unlink()


def test_init_database(temp_db):
    """Test database initialization."""
    # Check that tables were created
    with sqlite3.connect(str(temp_db)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert ("products",) in tables


def test_seed_database(temp_db):
    """Test database seeding."""
    with patch(
        "stage1_mcp_product_server.database.get_database_path", return_value=temp_db
    ):
        seed_database()

        # Check that products were inserted
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            assert count == 125  # 5 categories * 25 products each


def test_execute_query_select(temp_db):
    """Test executing SELECT queries."""
    with patch(
        "stage1_mcp_product_server.database.get_database_path", return_value=temp_db
    ):
        seed_database()

        # Test simple SELECT
        results = execute_query("SELECT * FROM products LIMIT 5")
        assert len(results) == 5
        assert all(isinstance(r, dict) for r in results)

        # Test with parameters
        results = execute_query(
            "SELECT * FROM products WHERE category = ?", ("Electronics",)
        )
        assert all(r["category"] == "Electronics" for r in results)


def test_execute_query_security(temp_db):
    """Test SQL injection prevention."""
    with patch(
        "stage1_mcp_product_server.database.get_database_path", return_value=temp_db
    ):
        # Test non-SELECT queries
        with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
            execute_query("DROP TABLE products")

        with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
            execute_query("INSERT INTO products VALUES (1, 'test')")

        # Test dangerous keywords
        with pytest.raises(ValueError, match="forbidden keyword"):
            execute_query("SELECT * FROM products; DROP TABLE products")


def test_get_schema_info(temp_db):
    """Test schema information retrieval."""
    with patch(
        "stage1_mcp_product_server.database.get_database_path", return_value=temp_db
    ):
        seed_database()

        schema = get_schema_info()

        assert schema["table_name"] == "products"
        assert schema["row_count"] == 125
        assert len(schema["categories"]) == 5
        assert "Electronics" in schema["categories"]
        assert len(schema["columns"]) > 0
        assert len(schema["indexes"]) > 0


def test_product_data_integrity(temp_db):
    """Test that seeded product data has proper values."""
    with patch(
        "stage1_mcp_product_server.database.get_database_path", return_value=temp_db
    ):
        seed_database()

        products = execute_query("SELECT * FROM products")

        for product in products:
            # Check required fields
            assert product["id"] is not None
            assert product["name"] is not None
            assert product["category"] in [
                "Electronics",
                "Clothing",
                "Home & Garden",
                "Sports",
                "Books",
            ]
            assert product["price"] > 0
            assert product["description"] is not None
            assert product["sku"] is not None
            assert product["brand"] is not None
            assert 1 <= product["rating"] <= 5
            assert product["stock_status"] in [
                "in_stock",
                "out_of_stock",
                "limited_stock",
            ]

        # Check SKU uniqueness
        skus = [p["sku"] for p in products]
        assert len(skus) == len(set(skus))
