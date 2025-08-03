"""Inventory Database Setup - Stage 3 of Agent Oriented Architecture.

This module creates and populates the inventory database with stock levels,
warehouse information, and reorder points for product management.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

# Database path
DB_PATH = Path(__file__).parent / "inventory.db"


def create_database():
    """Create the inventory database with all necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Warehouses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warehouses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        current_usage INTEGER DEFAULT 0,
        manager TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        warehouse_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 0,
        reorder_point INTEGER NOT NULL DEFAULT 10,
        reorder_quantity INTEGER NOT NULL DEFAULT 50,
        last_restocked TIMESTAMP,
        last_counted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
        UNIQUE(product_id, warehouse_id)
    )
    """)

    # Stock movements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        warehouse_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL CHECK(movement_type IN ('IN', 'OUT', 'TRANSFER')),
        quantity INTEGER NOT NULL,
        reference_type TEXT,
        reference_id TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
    )
    """)

    # Reorder history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reorder_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        warehouse_id INTEGER NOT NULL,
        quantity_ordered INTEGER NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expected_delivery TIMESTAMP,
        actual_delivery TIMESTAMP,
        status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'DELIVERED', 'CANCELLED')),
        supplier TEXT,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
    )
    """)

    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_quantity ON inventory(quantity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movements_product ON stock_movements(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movements_date ON stock_movements(created_at)")

    conn.commit()
    conn.close()


def populate_database():
    """Populate the database with sample inventory data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM reorder_history")
    cursor.execute("DELETE FROM stock_movements")
    cursor.execute("DELETE FROM inventory")
    cursor.execute("DELETE FROM warehouses")

    # Insert warehouses
    warehouses = [
        ("Main Distribution Center", "Chicago, IL", 50000, 35000, "John Smith"),
        ("West Coast Warehouse", "Los Angeles, CA", 30000, 22000, "Maria Garcia"),
        ("East Coast Hub", "Newark, NJ", 40000, 28000, "David Chen"),
        ("Southern Facility", "Atlanta, GA", 25000, 18000, "Sarah Johnson"),
        ("Express Fulfillment", "Dallas, TX", 20000, 15000, "Michael Brown")
    ]

    for name, location, capacity, usage, manager in warehouses:
        cursor.execute("""
            INSERT INTO warehouses (name, location, capacity, current_usage, manager)
            VALUES (?, ?, ?, ?, ?)
        """, (name, location, capacity, usage, manager))

    # Get warehouse IDs
    cursor.execute("SELECT id FROM warehouses")
    warehouse_ids = [row[0] for row in cursor.fetchall()]

    # Simulate inventory for products 1-125 (matching Stage 1 products)
    now = datetime.now()
    
    for product_id in range(1, 126):
        # Each product is stored in 1-3 random warehouses
        num_warehouses = random.randint(1, 3)
        selected_warehouses = random.sample(warehouse_ids, num_warehouses)
        
        for warehouse_id in selected_warehouses:
            # Random inventory levels
            quantity = random.randint(0, 500)
            reorder_point = random.randint(10, 50)
            reorder_quantity = random.randint(50, 200)
            
            # Some items were recently restocked
            last_restocked = None
            if random.random() > 0.3:
                days_ago = random.randint(1, 30)
                last_restocked = now - timedelta(days=days_ago)
            
            cursor.execute("""
                INSERT INTO inventory (
                    product_id, warehouse_id, quantity, 
                    reorder_point, reorder_quantity, last_restocked
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (product_id, warehouse_id, quantity, reorder_point, 
                  reorder_quantity, last_restocked))
            
            # Add some stock movement history
            for _ in range(random.randint(0, 5)):
                movement_type = random.choice(['IN', 'OUT', 'TRANSFER'])
                movement_quantity = random.randint(10, 100)
                days_ago = random.randint(1, 60)
                movement_date = now - timedelta(days=days_ago)
                
                cursor.execute("""
                    INSERT INTO stock_movements (
                        product_id, warehouse_id, movement_type, 
                        quantity, reference_type, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (product_id, warehouse_id, movement_type, 
                      movement_quantity, 'ORDER', movement_date))

    # Add some reorder history
    cursor.execute("""
        SELECT product_id, warehouse_id, reorder_quantity 
        FROM inventory 
        WHERE quantity < reorder_point
    """)
    
    for product_id, warehouse_id, reorder_qty in cursor.fetchall():
        order_date = now - timedelta(days=random.randint(1, 5))
        expected_delivery = order_date + timedelta(days=random.randint(3, 7))
        
        cursor.execute("""
            INSERT INTO reorder_history (
                product_id, warehouse_id, quantity_ordered,
                order_date, expected_delivery, status, supplier
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_id, warehouse_id, reorder_qty, order_date, 
              expected_delivery, 'PENDING', 'Generic Supplier Co.'))

    conn.commit()
    conn.close()


def main():
    """Create and populate the inventory database."""
    print("Creating inventory database...")
    create_database()
    
    print("Populating with sample data...")
    populate_database()
    
    # Verify the data
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM warehouses")
    warehouse_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM inventory")
    inventory_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity < reorder_point")
    low_stock_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\nDatabase created successfully!")
    print(f"- {warehouse_count} warehouses")
    print(f"- {inventory_count} inventory records")
    print(f"- {low_stock_count} items below reorder point")
    print(f"\nDatabase location: {DB_PATH}")


if __name__ == "__main__":
    main()