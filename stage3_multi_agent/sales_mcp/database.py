"""Sales Database Setup - Stage 3 of Agent Oriented Architecture.

This module creates and populates the sales database with transaction history,
returns data, and revenue information for sales analytics.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

# Database path
DB_PATH = Path(__file__).parent / "sales.db"


def create_database():
    """Create the sales database with all necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sales transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_amount REAL NOT NULL,
        discount_amount REAL DEFAULT 0,
        customer_id TEXT,
        customer_type TEXT CHECK(customer_type IN ('NEW', 'RETURNING', 'VIP')),
        payment_method TEXT,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        warehouse_id INTEGER,
        shipping_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Returns table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS returns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        return_id TEXT UNIQUE NOT NULL,
        order_id TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        return_amount REAL NOT NULL,
        return_reason TEXT,
        return_category TEXT CHECK(return_category IN ('DEFECTIVE', 'NOT_AS_DESCRIBED', 'CHANGED_MIND', 'DAMAGED_IN_SHIPPING', 'OTHER')),
        return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_date TIMESTAMP,
        status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED', 'REFUNDED')),
        notes TEXT,
        FOREIGN KEY (order_id) REFERENCES sales_transactions(order_id)
    )
    """)

    # Daily sales summary table (for faster analytics)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_sales_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summary_date DATE NOT NULL,
        total_orders INTEGER NOT NULL,
        total_revenue REAL NOT NULL,
        total_units_sold INTEGER NOT NULL,
        unique_customers INTEGER NOT NULL,
        total_returns INTEGER DEFAULT 0,
        return_value REAL DEFAULT 0,
        net_revenue REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(summary_date)
    )
    """)

    # Product performance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        period_start DATE NOT NULL,
        period_end DATE NOT NULL,
        units_sold INTEGER NOT NULL,
        revenue REAL NOT NULL,
        returns_count INTEGER DEFAULT 0,
        return_rate REAL DEFAULT 0,
        avg_sale_price REAL NOT NULL,
        ranking INTEGER,
        UNIQUE(product_id, period_start, period_end)
    )
    """)

    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product ON sales_transactions(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_transactions(transaction_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales_transactions(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_product ON returns(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_date ON returns(return_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_summary_date ON daily_sales_summary(summary_date)")

    conn.commit()
    conn.close()


def populate_database():
    """Populate the database with sample sales data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM product_performance")
    cursor.execute("DELETE FROM daily_sales_summary")
    cursor.execute("DELETE FROM returns")
    cursor.execute("DELETE FROM sales_transactions")

    # Generate sales for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # Customer types distribution
    customer_types = ['NEW'] * 3 + ['RETURNING'] * 6 + ['VIP'] * 1
    payment_methods = ['CREDIT_CARD', 'DEBIT_CARD', 'PAYPAL', 'APPLE_PAY', 'GOOGLE_PAY']
    shipping_methods = ['STANDARD', 'EXPRESS', 'OVERNIGHT', 'PICKUP']
    
    # Warehouse IDs (matching inventory)
    warehouse_ids = [1, 2, 3, 4, 5]
    
    # Generate return reasons
    return_reasons = {
        'DEFECTIVE': ['Product not working', 'Dead on arrival', 'Malfunctioning'],
        'NOT_AS_DESCRIBED': ['Different from pictures', 'Wrong specifications', 'Misleading description'],
        'CHANGED_MIND': ["Didn't need it", 'Found better option', 'Too expensive'],
        'DAMAGED_IN_SHIPPING': ['Package damaged', 'Item broken in transit', 'Poor packaging'],
        'OTHER': ['No longer needed', 'Ordered by mistake', 'Gift return']
    }
    
    # Product price ranges (simplified, would normally join with product table)
    product_prices = {}
    for product_id in range(1, 126):
        # Random base prices between $10 and $500
        product_prices[product_id] = round(random.uniform(10, 500), 2)
    
    # Generate sales transactions
    current_date = start_date
    order_counter = 1000
    
    while current_date <= end_date:
        # Variable number of orders per day (more on weekends)
        is_weekend = current_date.weekday() >= 5
        num_orders = random.randint(20, 50) if is_weekend else random.randint(10, 30)
        
        for _ in range(num_orders):
            order_id = f"ORD-{order_counter:06d}"
            order_counter += 1
            
            # Random product and quantity
            product_id = random.randint(1, 125)
            quantity = random.randint(1, 5)
            unit_price = product_prices[product_id]
            
            # Apply occasional discounts
            discount_rate = random.choice([0, 0, 0, 0.1, 0.15, 0.2])  # Most have no discount
            discount_amount = round(unit_price * quantity * discount_rate, 2)
            total_amount = round(unit_price * quantity - discount_amount, 2)
            
            # Customer info
            customer_id = f"CUST-{random.randint(1000, 9999)}"
            customer_type = random.choice(customer_types)
            
            # Transaction details
            payment_method = random.choice(payment_methods)
            warehouse_id = random.choice(warehouse_ids)
            shipping_method = random.choice(shipping_methods)
            
            # Add some time variation within the day
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            transaction_date = current_date.replace(hour=hours, minute=minutes)
            
            cursor.execute("""
                INSERT INTO sales_transactions (
                    order_id, product_id, quantity, unit_price, total_amount,
                    discount_amount, customer_id, customer_type, payment_method,
                    transaction_date, warehouse_id, shipping_method
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, product_id, quantity, unit_price, total_amount,
                  discount_amount, customer_id, customer_type, payment_method,
                  transaction_date, warehouse_id, shipping_method))
            
            # Generate returns (about 5% of orders)
            if random.random() < 0.05:
                return_id = f"RET-{order_id[4:]}"
                return_quantity = random.randint(1, quantity)
                return_amount = round(unit_price * return_quantity, 2)
                return_category = random.choice(list(return_reasons.keys()))
                return_reason = random.choice(return_reasons[return_category])
                
                # Returns happen 1-14 days after purchase
                days_to_return = random.randint(1, 14)
                return_date = transaction_date + timedelta(days=days_to_return)
                
                # Most returns are processed within 3 days
                if random.random() < 0.8:
                    processed_date = return_date + timedelta(days=random.randint(1, 3))
                    status = random.choice(['APPROVED', 'APPROVED', 'APPROVED', 'REJECTED', 'REFUNDED'])
                else:
                    processed_date = None
                    status = 'PENDING'
                
                cursor.execute("""
                    INSERT INTO returns (
                        return_id, order_id, product_id, quantity, return_amount,
                        return_reason, return_category, return_date, processed_date, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (return_id, order_id, product_id, return_quantity, return_amount,
                      return_reason, return_category, return_date, processed_date, status))
        
        current_date += timedelta(days=1)
    
    # Generate daily summaries
    cursor.execute("""
        INSERT INTO daily_sales_summary (
            summary_date, total_orders, total_revenue, total_units_sold,
            unique_customers, total_returns, return_value, net_revenue
        )
        SELECT 
            DATE(transaction_date) as summary_date,
            COUNT(DISTINCT order_id) as total_orders,
            SUM(total_amount) as total_revenue,
            SUM(quantity) as total_units_sold,
            COUNT(DISTINCT customer_id) as unique_customers,
            0 as total_returns,
            0 as return_value,
            SUM(total_amount) as net_revenue
        FROM sales_transactions
        GROUP BY DATE(transaction_date)
    """)
    
    # Update return counts in daily summaries
    cursor.execute("""
        UPDATE daily_sales_summary
        SET total_returns = (
            SELECT COUNT(*) FROM returns 
            WHERE DATE(return_date) = daily_sales_summary.summary_date
        ),
        return_value = (
            SELECT COALESCE(SUM(return_amount), 0) FROM returns 
            WHERE DATE(return_date) = daily_sales_summary.summary_date
        ),
        net_revenue = total_revenue - (
            SELECT COALESCE(SUM(return_amount), 0) FROM returns 
            WHERE DATE(return_date) = daily_sales_summary.summary_date
        )
    """)
    
    # Generate monthly product performance
    cursor.execute("""
        INSERT INTO product_performance (
            product_id, period_start, period_end, units_sold,
            revenue, returns_count, return_rate, avg_sale_price
        )
        SELECT 
            st.product_id,
            DATE(st.transaction_date, 'start of month') as period_start,
            DATE(st.transaction_date, 'start of month', '+1 month', '-1 day') as period_end,
            SUM(st.quantity) as units_sold,
            SUM(st.total_amount) as revenue,
            COALESCE(ret.return_count, 0) as returns_count,
            CASE 
                WHEN SUM(st.quantity) > 0 
                THEN CAST(COALESCE(ret.return_count, 0) AS FLOAT) / SUM(st.quantity) * 100
                ELSE 0 
            END as return_rate,
            AVG(st.unit_price) as avg_sale_price
        FROM sales_transactions st
        LEFT JOIN (
            SELECT product_id, COUNT(*) as return_count
            FROM returns
            GROUP BY product_id
        ) ret ON st.product_id = ret.product_id
        GROUP BY st.product_id, period_start, period_end
    """)

    conn.commit()
    conn.close()


def main():
    """Create and populate the sales database."""
    print("Creating sales database...")
    create_database()
    
    print("Populating with sample data...")
    populate_database()
    
    # Verify the data
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM sales_transactions")
    transaction_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM returns")
    return_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total_revenue) FROM daily_sales_summary")
    total_revenue = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\nDatabase created successfully!")
    print(f"- {transaction_count} sales transactions")
    print(f"- {return_count} returns")
    print(f"- ${total_revenue:,.2f} total revenue")
    print(f"\nDatabase location: {DB_PATH}")


if __name__ == "__main__":
    main()