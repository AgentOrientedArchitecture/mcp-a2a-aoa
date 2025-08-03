"""Inventory MCP Server - Stage 3 of Agent Oriented Architecture.

This MCP server provides tools for inventory management, stock checking,
warehouse operations, and reorder predictions.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("inventory-management")

# Database path
DB_PATH = Path(__file__).parent / "inventory.db"


def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


@mcp.tool()
def check_stock(product_id: int, warehouse_id: Optional[int] = None) -> str:
    """Check stock levels for a product across warehouses.
    
    Args:
        product_id: The product ID to check
        warehouse_id: Optional specific warehouse ID
        
    Returns:
        JSON string with stock information
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if warehouse_id:
        query = """
        SELECT i.*, w.name as warehouse_name, w.location
        FROM inventory i
        JOIN warehouses w ON i.warehouse_id = w.id
        WHERE i.product_id = ? AND i.warehouse_id = ?
        """
        cursor.execute(query, (product_id, warehouse_id))
    else:
        query = """
        SELECT i.*, w.name as warehouse_name, w.location
        FROM inventory i
        JOIN warehouses w ON i.warehouse_id = w.id
        WHERE i.product_id = ?
        ORDER BY i.quantity DESC
        """
        cursor.execute(query, (product_id,))
    
    columns = [description[0] for description in cursor.description]
    results = []
    
    for row in cursor.fetchall():
        stock_info = dict(zip(columns, row))
        # Add stock status
        if stock_info['quantity'] == 0:
            stock_info['status'] = 'OUT_OF_STOCK'
        elif stock_info['quantity'] < stock_info['reorder_point']:
            stock_info['status'] = 'LOW_STOCK'
        else:
            stock_info['status'] = 'IN_STOCK'
        results.append(stock_info)
    
    # Get total stock across all warehouses
    cursor.execute("""
        SELECT SUM(quantity) as total_quantity
        FROM inventory
        WHERE product_id = ?
    """, (product_id,))
    
    total_quantity = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "product_id": product_id,
        "total_quantity": total_quantity,
        "warehouse_stock": results,
        "warehouses_count": len(results)
    }


@mcp.tool()
def get_warehouse_info(warehouse_id: Optional[int] = None) -> str:
    """Get warehouse information and capacity utilization.
    
    Args:
        warehouse_id: Optional specific warehouse ID
        
    Returns:
        JSON string with warehouse information
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if warehouse_id:
        cursor.execute("""
            SELECT * FROM warehouses WHERE id = ?
        """, (warehouse_id,))
    else:
        cursor.execute("""
            SELECT * FROM warehouses ORDER BY capacity DESC
        """)
    
    columns = [description[0] for description in cursor.description]
    warehouses = []
    
    for row in cursor.fetchall():
        warehouse = dict(zip(columns, row))
        
        # Calculate utilization
        if warehouse['capacity'] > 0:
            warehouse['utilization_percent'] = round(
                (warehouse['current_usage'] / warehouse['capacity']) * 100, 2
            )
        else:
            warehouse['utilization_percent'] = 0
        
        # Get product count in warehouse
        cursor.execute("""
            SELECT COUNT(DISTINCT product_id) as product_count,
                   SUM(quantity) as total_items
            FROM inventory
            WHERE warehouse_id = ?
        """, (warehouse['id'],))
        
        stats = cursor.fetchone()
        warehouse['product_count'] = stats[0]
        warehouse['total_items'] = stats[1] or 0
        
        warehouses.append(warehouse)
    
    conn.close()
    
    if warehouse_id and warehouses:
        return warehouses[0]
    return warehouses


@mcp.tool()
def predict_stockouts(days_ahead: int = 7, min_quantity: int = 0) -> str:
    """Predict which products will need restocking soon.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        min_quantity: Minimum quantity threshold (default: 0)
        
    Returns:
        JSON string with predicted stockouts
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get average daily movement for each product
    days_history = 30
    date_threshold = datetime.now() - timedelta(days=days_history)
    
    cursor.execute("""
        SELECT 
            i.product_id,
            i.warehouse_id,
            w.name as warehouse_name,
            i.quantity as current_stock,
            i.reorder_point,
            COALESCE(AVG(CASE WHEN sm.movement_type = 'OUT' THEN sm.quantity ELSE 0 END), 0) as avg_daily_usage
        FROM inventory i
        JOIN warehouses w ON i.warehouse_id = w.id
        LEFT JOIN stock_movements sm ON 
            i.product_id = sm.product_id AND 
            i.warehouse_id = sm.warehouse_id AND
            sm.created_at > ?
        GROUP BY i.product_id, i.warehouse_id
        HAVING i.quantity > ?
    """, (date_threshold, min_quantity))
    
    predictions = []
    
    for row in cursor.fetchall():
        product_id, warehouse_id, warehouse_name, current_stock, reorder_point, avg_daily_usage = row
        
        if avg_daily_usage > 0:
            days_until_out = current_stock / avg_daily_usage
            days_until_reorder = (current_stock - reorder_point) / avg_daily_usage
            
            if days_until_out <= days_ahead:
                predictions.append({
                    "product_id": product_id,
                    "warehouse_id": warehouse_id,
                    "warehouse_name": warehouse_name,
                    "current_stock": current_stock,
                    "avg_daily_usage": round(avg_daily_usage, 2),
                    "days_until_stockout": round(days_until_out, 1),
                    "days_until_reorder_point": round(days_until_reorder, 1) if days_until_reorder > 0 else 0,
                    "urgency": "CRITICAL" if days_until_out <= 3 else "HIGH"
                })
    
    # Sort by urgency
    predictions.sort(key=lambda x: x['days_until_stockout'])
    
    conn.close()
    
    return {
        "analysis_date": datetime.now().isoformat(),
        "days_ahead": days_ahead,
        "predicted_stockouts": len(predictions),
        "predictions": predictions[:50]  # Limit to top 50
    }


@mcp.tool()
def get_reorder_suggestions() -> str:
    """Get suggestions for products that need reordering.
    
    Returns:
        JSON string with reorder suggestions
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find products below reorder point
    cursor.execute("""
        SELECT 
            i.product_id,
            i.warehouse_id,
            w.name as warehouse_name,
            i.quantity as current_stock,
            i.reorder_point,
            i.reorder_quantity,
            i.last_restocked
        FROM inventory i
        JOIN warehouses w ON i.warehouse_id = w.id
        WHERE i.quantity <= i.reorder_point
        ORDER BY (i.reorder_point - i.quantity) DESC
    """)
    
    suggestions = []
    
    for row in cursor.fetchall():
        product_id, warehouse_id, warehouse_name, current_stock, reorder_point, reorder_quantity, last_restocked = row
        
        # Check if already on order
        cursor.execute("""
            SELECT COUNT(*) FROM reorder_history
            WHERE product_id = ? AND warehouse_id = ? AND status = 'PENDING'
        """, (product_id, warehouse_id))
        
        pending_orders = cursor.fetchone()[0]
        
        suggestion = {
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse_name,
            "current_stock": current_stock,
            "reorder_point": reorder_point,
            "suggested_order_quantity": reorder_quantity,
            "stock_deficit": reorder_point - current_stock,
            "last_restocked": last_restocked,
            "pending_orders": pending_orders,
            "action": "ORDER_NOW" if pending_orders == 0 else "ALREADY_ORDERED"
        }
        
        suggestions.append(suggestion)
    
    conn.close()
    
    return {
        "total_suggestions": len(suggestions),
        "urgent_reorders": len([s for s in suggestions if s['action'] == 'ORDER_NOW']),
        "suggestions": suggestions
    }


@mcp.tool()
def get_inventory_summary() -> str:
    """Get a summary of inventory across all warehouses.
    
    Returns:
        JSON string with inventory summary statistics
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Overall statistics
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT product_id) as total_products,
            COUNT(*) as total_inventory_records,
            SUM(quantity) as total_items,
            COUNT(CASE WHEN quantity = 0 THEN 1 END) as out_of_stock,
            COUNT(CASE WHEN quantity > 0 AND quantity <= reorder_point THEN 1 END) as low_stock,
            COUNT(CASE WHEN quantity > reorder_point THEN 1 END) as in_stock
        FROM inventory
    """)
    
    stats = cursor.fetchone()
    
    # Warehouse utilization
    cursor.execute("""
        SELECT 
            AVG(CAST(current_usage AS FLOAT) / capacity * 100) as avg_utilization,
            MIN(CAST(current_usage AS FLOAT) / capacity * 100) as min_utilization,
            MAX(CAST(current_usage AS FLOAT) / capacity * 100) as max_utilization
        FROM warehouses
        WHERE capacity > 0
    """)
    
    utilization = cursor.fetchone()
    
    # Recent activity
    cursor.execute("""
        SELECT 
            movement_type,
            COUNT(*) as count,
            SUM(quantity) as total_quantity
        FROM stock_movements
        WHERE created_at > datetime('now', '-7 days')
        GROUP BY movement_type
    """)
    
    recent_movements = {}
    for movement_type, count, total_quantity in cursor.fetchall():
        recent_movements[movement_type.lower()] = {
            "count": count,
            "total_quantity": total_quantity
        }
    
    conn.close()
    
    return {
        "overview": {
            "total_products_tracked": stats[0],
            "total_inventory_records": stats[1],
            "total_items_in_stock": stats[2],
            "out_of_stock_locations": stats[3],
            "low_stock_locations": stats[4],
            "healthy_stock_locations": stats[5]
        },
        "warehouse_utilization": {
            "average": round(utilization[0], 2) if utilization[0] else 0,
            "minimum": round(utilization[1], 2) if utilization[1] else 0,
            "maximum": round(utilization[2], 2) if utilization[2] else 0
        },
        "recent_activity_7_days": recent_movements,
        "generated_at": datetime.now().isoformat()
    }


@mcp.tool()
def update_stock(product_id: int, warehouse_id: int, quantity_change: int, 
                movement_type: str, reference: Optional[str] = None) -> str:
    """Update stock levels for a product in a warehouse.
    
    Args:
        product_id: The product ID
        warehouse_id: The warehouse ID  
        quantity_change: The quantity to add (positive) or remove (negative)
        movement_type: Type of movement ('IN', 'OUT', or 'TRANSFER')
        reference: Optional reference information
        
    Returns:
        JSON string with update result
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get current stock
        cursor.execute("""
            SELECT quantity FROM inventory
            WHERE product_id = ? AND warehouse_id = ?
        """, (product_id, warehouse_id))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return {
                "success": False,
                "error": f"Product {product_id} not found in warehouse {warehouse_id}"
            }
        
        current_quantity = result[0]
        new_quantity = current_quantity + quantity_change
        
        if new_quantity < 0:
            conn.close()
            return {
                "success": False,
                "error": f"Insufficient stock. Current: {current_quantity}, Requested change: {quantity_change}"
            }
        
        # Update inventory
        cursor.execute("""
            UPDATE inventory 
            SET quantity = ?, last_counted = CURRENT_TIMESTAMP
            WHERE product_id = ? AND warehouse_id = ?
        """, (new_quantity, product_id, warehouse_id))
        
        # Record movement
        cursor.execute("""
            INSERT INTO stock_movements (
                product_id, warehouse_id, movement_type, 
                quantity, reference_type, reference_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, warehouse_id, movement_type, 
              abs(quantity_change), 'MANUAL', reference))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "previous_quantity": current_quantity,
            "quantity_change": quantity_change,
            "new_quantity": new_quantity,
            "movement_type": movement_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Run the server
    mcp.run()