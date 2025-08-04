"""Inventory MCP Server - Stage 3 of Agent Oriented Architecture.

This MCP server provides tools for inventory management, stock checking,
warehouse operations, and reorder predictions.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

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
    
    result = {
        "product_id": product_id,
        "total_quantity": total_quantity,
        "warehouse_stock": results,
        "warehouses_count": len(results)
    }
    
    return json.dumps(result, indent=2)


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
        
        warehouses.append(warehouse)
    
    conn.close()
    
    result = {
        "warehouses": warehouses,
        "total_warehouses": len(warehouses)
    }
    
    return json.dumps(result, indent=2)


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
    
    # Calculate future stock levels based on current trends
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
        WHERE i.quantity > 0 AND i.quantity <= i.reorder_point + ?
        ORDER BY (i.reorder_point - i.quantity) DESC
    """, (days_ahead,))
    
    predictions = []
    
    for row in cursor.fetchall():
        product_id, warehouse_id, warehouse_name, current_stock, reorder_point, reorder_quantity, last_restocked = row
        
        # Simple prediction: if current stock is close to reorder point, likely to stockout
        days_to_stockout = max(1, (current_stock - min_quantity) // max(1, (reorder_point - current_stock) // days_ahead))
        
        prediction = {
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse_name,
            "current_stock": current_stock,
            "reorder_point": reorder_point,
            "predicted_stockout_days": days_to_stockout,
            "risk_level": "HIGH" if days_to_stockout <= 3 else "MEDIUM" if days_to_stockout <= 7 else "LOW",
            "last_restocked": last_restocked
        }
        
        predictions.append(prediction)
    
    conn.close()
    
    result = {
        "predictions": predictions,
        "total_predictions": len(predictions),
        "high_risk": len([p for p in predictions if p['risk_level'] == 'HIGH']),
        "medium_risk": len([p for p in predictions if p['risk_level'] == 'MEDIUM']),
        "low_risk": len([p for p in predictions if p['risk_level'] == 'LOW'])
    }
    
    return json.dumps(result, indent=2)


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
    
    result = {
        "total_suggestions": len(suggestions),
        "urgent_reorders": len([s for s in suggestions if s['action'] == 'ORDER_NOW']),
        "suggestions": suggestions
    }
    
    return json.dumps(result, indent=2)


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
        SELECT COUNT(*) as recent_movements
        FROM stock_movements
        WHERE created_at > datetime('now', '-7 days')
    """)
    
    recent_activity = cursor.fetchone()
    
    conn.close()
    
    result = {
        "summary": {
            "total_products": stats[0],
            "total_inventory_records": stats[1],
            "total_items": stats[2],
            "out_of_stock": stats[3],
            "low_stock": stats[4],
            "in_stock": stats[5]
        },
        "warehouse_utilization": {
            "average": round(utilization[0], 2) if utilization[0] else 0,
            "minimum": round(utilization[1], 2) if utilization[1] else 0,
            "maximum": round(utilization[2], 2) if utilization[2] else 0
        },
        "recent_activity": {
            "movements_last_7_days": recent_activity[0]
        }
    }
    
    return json.dumps(result, indent=2)


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
            return json.dumps({
                "error": f"No inventory record found for product {product_id} in warehouse {warehouse_id}"
            }, indent=2)
        
        current_quantity = result[0]
        new_quantity = current_quantity + quantity_change
        
        if new_quantity < 0:
            return json.dumps({
                "error": f"Insufficient stock. Current: {current_quantity}, Requested change: {quantity_change}"
            }, indent=2)
        
        # Update inventory
        cursor.execute("""
            UPDATE inventory 
            SET quantity = ?, last_updated = datetime('now')
            WHERE product_id = ? AND warehouse_id = ?
        """, (new_quantity, product_id, warehouse_id))
        
        # Record movement
        cursor.execute("""
            INSERT INTO stock_movements 
            (product_id, warehouse_id, quantity, movement_type, reference, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (product_id, warehouse_id, quantity_change, movement_type, reference or ""))
        
        conn.commit()
        
        result = {
            "success": True,
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "previous_quantity": current_quantity,
            "new_quantity": new_quantity,
            "quantity_change": quantity_change,
            "movement_type": movement_type,
            "reference": reference
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        conn.rollback()
        return json.dumps({
            "error": f"Failed to update stock: {str(e)}"
        }, indent=2)
    finally:
        conn.close()


if __name__ == "__main__":
    # Run the server
    mcp.run()