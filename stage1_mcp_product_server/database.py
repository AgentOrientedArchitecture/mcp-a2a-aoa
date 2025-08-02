"""Database module for product catalog MCP server.

This module handles SQLite database initialization, schema creation,
and data seeding for the product catalog.
"""

import sqlite3
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    brand TEXT NOT NULL,
    rating REAL CHECK(rating >= 1 AND rating <= 5),
    stock_status TEXT CHECK(stock_status IN ('in_stock', 'out_of_stock', 'limited_stock')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_rating ON products(rating);
CREATE INDEX IF NOT EXISTS idx_stock ON products(stock_status);
"""

# Product data for seeding
PRODUCT_DATA: Dict[str, Dict[str, Any]] = {
    "Electronics": {
        "brands": ["TechCorp", "ElectroMax", "SmartLife", "DigitalPro", "FutureTech"],
        "products": [
            "Wireless Headphones",
            "Smart Watch",
            "Tablet",
            "Laptop",
            "Smartphone",
            "Bluetooth Speaker",
            "Wireless Mouse",
            "USB-C Hub",
            "Power Bank",
            "Smart TV",
            "Gaming Console",
            "Fitness Tracker",
            "E-Reader",
            "Webcam",
            "Keyboard",
        ],
        "price_range": (29.99, 1999.99),
    },
    "Clothing": {
        "brands": [
            "FashionForward",
            "UrbanStyle",
            "ComfortWear",
            "TrendSetters",
            "ClassicThreads",
        ],
        "products": [
            "T-Shirt",
            "Jeans",
            "Sneakers",
            "Jacket",
            "Dress",
            "Sweater",
            "Shorts",
            "Hat",
            "Scarf",
            "Boots",
            "Shirt",
            "Pants",
            "Socks",
            "Belt",
            "Hoodie",
        ],
        "price_range": (14.99, 299.99),
    },
    "Home & Garden": {
        "brands": [
            "HomeEssentials",
            "GardenPro",
            "CozyLiving",
            "NatureFirst",
            "ModernHome",
        ],
        "products": [
            "Coffee Maker",
            "Blender",
            "Vacuum Cleaner",
            "Air Purifier",
            "Lamp",
            "Pillow",
            "Blanket",
            "Plant Pot",
            "Garden Tools",
            "Storage Box",
            "Kitchen Scale",
            "Cutting Board",
            "Towel Set",
            "Curtains",
            "Mirror",
        ],
        "price_range": (19.99, 499.99),
    },
    "Sports": {
        "brands": ["ActiveLife", "ProSport", "FitGear", "Athletix", "OutdoorPro"],
        "products": [
            "Yoga Mat",
            "Dumbbells",
            "Running Shoes",
            "Water Bottle",
            "Gym Bag",
            "Resistance Bands",
            "Jump Rope",
            "Tennis Racket",
            "Basketball",
            "Bike Helmet",
            "Swimming Goggles",
            "Camping Tent",
            "Hiking Backpack",
            "Fitness Ball",
            "Foam Roller",
        ],
        "price_range": (9.99, 399.99),
    },
    "Books": {
        "brands": [
            "ReadMore",
            "BookWorld",
            "LiteraryClassics",
            "KnowledgeHub",
            "PageTurners",
        ],
        "products": [
            "Science Fiction Novel",
            "Mystery Thriller",
            "Self-Help Book",
            "Cookbook",
            "Biography",
            "Fantasy Series",
            "History Book",
            "Programming Guide",
            "Art Book",
            "Travel Guide",
            "Poetry Collection",
            "Business Book",
            "Children's Book",
            "Graphic Novel",
            "Dictionary",
        ],
        "price_range": (7.99, 49.99),
    },
}


def get_database_path() -> Path:
    """Get the path to the SQLite database file."""
    db_dir = Path(__file__).parent
    return db_dir / "product_catalog.db"


def init_database() -> None:
    """Initialize the database with schema."""
    db_path = get_database_path()

    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(SCHEMA)
        conn.commit()

    logger.info(f"Database initialized at {db_path}")


def seed_database() -> None:
    """Seed the database with sample product data."""
    db_path = get_database_path()

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()

        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] > 0:
            logger.info("Database already contains data, skipping seed")
            return

        products_to_insert = []
        sku_counter = 1000

        for category, data in PRODUCT_DATA.items():
            # Generate 20+ products per category
            for i in range(25):
                brand = random.choice(data["brands"])
                product_base = random.choice(data["products"])

                # Create variations
                variations = [
                    "Pro",
                    "Plus",
                    "Max",
                    "Mini",
                    "Ultra",
                    "Essential",
                    "Premium",
                    "Basic",
                ]
                variation = random.choice(variations) if random.random() > 0.5 else ""

                name = f"{brand} {product_base} {variation}".strip()

                # Generate realistic description
                features = [
                    "High quality",
                    "Durable",
                    "Eco-friendly",
                    "Award-winning",
                    "Best-selling",
                    "Premium materials",
                    "Modern design",
                    "Lightweight",
                    "Versatile",
                    "Professional grade",
                    "Energy efficient",
                    "Innovative",
                ]
                selected_features = random.sample(features, 3)
                description = f"{name} - {', '.join(selected_features)}. Perfect for everyday use."

                min_price, max_price = data["price_range"]
                price = round(random.uniform(min_price, max_price), 2)
                rating = round(random.uniform(3.0, 5.0), 1)
                stock_status = random.choice(
                    [
                        "in_stock",
                        "in_stock",
                        "in_stock",
                        "limited_stock",
                        "out_of_stock",
                    ]
                )
                sku = f"SKU-{category[:3].upper()}-{sku_counter}"
                sku_counter += 1

                products_to_insert.append(
                    (
                        name,
                        category,
                        price,
                        description,
                        sku,
                        brand,
                        rating,
                        stock_status,
                    )
                )

        # Insert all products
        cursor.executemany(
            """INSERT INTO products 
               (name, category, price, description, sku, brand, rating, stock_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            products_to_insert,
        )

        conn.commit()
        logger.info(f"Seeded database with {len(products_to_insert)} products")


def get_connection() -> sqlite3.Connection:
    """Get a connection to the database with row factory."""
    conn = sqlite3.connect(str(get_database_path()))
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """Execute a read-only query and return results as list of dicts."""
    # Basic SQL injection prevention - only allow SELECT queries
    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")

    # Additional safety checks
    dangerous_keywords = [
        "DROP",
        "DELETE",
        "INSERT",
        "UPDATE",
        "ALTER",
        "CREATE",
        "EXEC",
        "EXECUTE",
    ]
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            raise ValueError(f"Query contains forbidden keyword: {keyword}")

    with get_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Convert Row objects to dicts
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_schema_info() -> Dict[str, Any]:
    """Get information about the database schema."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Get table info
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()

        # Get index info
        cursor.execute("PRAGMA index_list(products)")
        indexes = cursor.fetchall()

        # Get row count
        cursor.execute("SELECT COUNT(*) as count FROM products")
        row_count = cursor.fetchone()["count"]

        # Get categories
        cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        categories = [row["category"] for row in cursor.fetchall()]

        return {
            "table_name": "products",
            "columns": [dict(col) for col in columns],
            "indexes": [dict(idx) for idx in indexes],
            "row_count": row_count,
            "categories": categories,
        }


if __name__ == "__main__":
    # Initialize and seed database when run directly
    logging.basicConfig(level=logging.INFO)
    init_database()
    seed_database()

    # Print schema info
    schema = get_schema_info()
    print(f"Database initialized with {schema['row_count']} products")
    print(f"Categories: {', '.join(schema['categories'])}")
