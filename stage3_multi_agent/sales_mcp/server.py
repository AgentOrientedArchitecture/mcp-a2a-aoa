"""Sales MCP Server - Stage 3 of Agent Oriented Architecture.

This MCP server provides tools for sales analytics, transaction history,
return analysis, and revenue insights.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("sales-analytics")

# Database path
DB_PATH = Path(__file__).parent / "sales.db"


def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


@mcp.tool()
def get_sales_history(
    product_id: Optional[int] = None,
    days: int = 30,
    customer_type: Optional[str] = None
) -> str:
    """Get sales transaction history with optional filters.
    
    Args:
        product_id: Optional product ID to filter by
        days: Number of days of history (default: 30)
        customer_type: Optional customer type filter ('NEW', 'RETURNING', 'VIP')
        
    Returns:
        JSON string with sales history
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    date_threshold = datetime.now() - timedelta(days=days)
    
    query = """
        SELECT 
            order_id, product_id, quantity, unit_price, total_amount,
            discount_amount, customer_id, customer_type, payment_method,
            transaction_date, warehouse_id, shipping_method
        FROM sales_transactions
        WHERE transaction_date >= ?
    """
    params = [date_threshold]
    
    if product_id:
        query += " AND product_id = ?"
        params.append(product_id)
    
    if customer_type:
        query += " AND customer_type = ?"
        params.append(customer_type)
    
    query += " ORDER BY transaction_date DESC LIMIT 1000"
    
    cursor.execute(query, params)
    
    columns = [description[0] for description in cursor.description]
    transactions = []
    
    for row in cursor.fetchall():
        transaction = dict(zip(columns, row))
        transactions.append(transaction)
    
    # Get summary statistics
    summary_query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(quantity) as total_units,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_order_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM sales_transactions
        WHERE transaction_date >= ?
    """
    
    if product_id:
        summary_query += " AND product_id = ?"
    if customer_type:
        summary_query += " AND customer_type = ?"
    
    cursor.execute(summary_query, params)
    summary = cursor.fetchone()
    
    conn.close()
    
    return {
        "period": f"Last {days} days",
        "filters": {
            "product_id": product_id,
            "customer_type": customer_type
        },
        "summary": {
            "total_transactions": summary[0],
            "total_units_sold": summary[1],
            "total_revenue": round(summary[2], 2) if summary[2] else 0,
            "average_order_value": round(summary[3], 2) if summary[3] else 0,
            "unique_customers": summary[4]
        },
        "transactions": transactions[:100]  # Limit to 100 for response size
    }


@mcp.tool()
def analyze_returns(
    product_id: Optional[int] = None,
    days: int = 30,
    return_category: Optional[str] = None
) -> str:
    """Analyze product returns and reasons.
    
    Args:
        product_id: Optional product ID to filter by
        days: Number of days to analyze (default: 30)
        return_category: Optional category filter
        
    Returns:
        JSON string with return analysis
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    date_threshold = datetime.now() - timedelta(days=days)
    
    # Get return details
    query = """
        SELECT 
            r.*,
            s.total_amount as original_order_amount,
            s.quantity as original_quantity
        FROM returns r
        JOIN sales_transactions s ON r.order_id = s.order_id
        WHERE r.return_date >= ?
    """
    params = [date_threshold]
    
    if product_id:
        query += " AND r.product_id = ?"
        params.append(product_id)
    
    if return_category:
        query += " AND r.return_category = ?"
        params.append(return_category)
    
    cursor.execute(query, params)
    
    columns = [description[0] for description in cursor.description]
    returns = []
    
    for row in cursor.fetchall():
        return_data = dict(zip(columns, row))
        returns.append(return_data)
    
    # Get return statistics by category
    cursor.execute("""
        SELECT 
            return_category,
            COUNT(*) as count,
            SUM(return_amount) as total_value
        FROM returns
        WHERE return_date >= ?
        GROUP BY return_category
        ORDER BY count DESC
    """, [date_threshold])
    
    category_stats = []
    for category, count, value in cursor.fetchall():
        category_stats.append({
            "category": category,
            "count": count,
            "total_value": round(value, 2)
        })
    
    # Get return rate
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT s.order_id) as total_orders,
            COUNT(DISTINCT r.order_id) as orders_with_returns
        FROM sales_transactions s
        LEFT JOIN returns r ON s.order_id = r.order_id
        WHERE s.transaction_date >= ?
    """, [date_threshold])
    
    total_orders, orders_with_returns = cursor.fetchone()
    return_rate = (orders_with_returns / total_orders * 100) if total_orders > 0 else 0
    
    conn.close()
    
    return {
        "period": f"Last {days} days",
        "filters": {
            "product_id": product_id,
            "return_category": return_category
        },
        "summary": {
            "total_returns": len(returns),
            "total_return_value": sum(r['return_amount'] for r in returns),
            "return_rate": round(return_rate, 2),
            "orders_with_returns": orders_with_returns,
            "total_orders": total_orders
        },
        "category_breakdown": category_stats,
        "recent_returns": returns[:50]  # Limit to 50 most recent
    }


@mcp.tool()
def calculate_revenue(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    group_by: str = "day"
) -> str:
    """Calculate revenue metrics for a period.
    
    Args:
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        group_by: Grouping period ('day', 'week', 'month')
        
    Returns:
        JSON string with revenue calculations
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Get revenue data from daily summaries
    cursor.execute("""
        SELECT * FROM daily_sales_summary
        WHERE summary_date >= ? AND summary_date <= ?
        ORDER BY summary_date
    """, (start_date, end_date))
    
    columns = [description[0] for description in cursor.description]
    daily_data = []
    
    for row in cursor.fetchall():
        daily_data.append(dict(zip(columns, row)))
    
    # Calculate aggregated metrics
    if daily_data:
        total_revenue = sum(d['total_revenue'] for d in daily_data)
        total_returns = sum(d['return_value'] for d in daily_data)
        net_revenue = sum(d['net_revenue'] for d in daily_data)
        total_orders = sum(d['total_orders'] for d in daily_data)
        total_units = sum(d['total_units_sold'] for d in daily_data)
        
        avg_daily_revenue = total_revenue / len(daily_data)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    else:
        total_revenue = total_returns = net_revenue = 0
        total_orders = total_units = 0
        avg_daily_revenue = avg_order_value = 0
    
    # Get top performing products
    cursor.execute("""
        SELECT 
            product_id,
            COUNT(*) as order_count,
            SUM(quantity) as units_sold,
            SUM(total_amount) as revenue
        FROM sales_transactions
        WHERE DATE(transaction_date) >= ? AND DATE(transaction_date) <= ?
        GROUP BY product_id
        ORDER BY revenue DESC
        LIMIT 10
    """, (start_date, end_date))
    
    top_products = []
    for product_id, order_count, units_sold, revenue in cursor.fetchall():
        top_products.append({
            "product_id": product_id,
            "order_count": order_count,
            "units_sold": units_sold,
            "revenue": round(revenue, 2)
        })
    
    conn.close()
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": len(daily_data)
        },
        "revenue_summary": {
            "gross_revenue": round(total_revenue, 2),
            "returns_value": round(total_returns, 2),
            "net_revenue": round(net_revenue, 2),
            "return_rate": round((total_returns / total_revenue * 100), 2) if total_revenue > 0 else 0
        },
        "order_metrics": {
            "total_orders": total_orders,
            "total_units_sold": total_units,
            "average_order_value": round(avg_order_value, 2),
            "average_daily_revenue": round(avg_daily_revenue, 2)
        },
        "top_products": top_products,
        "daily_breakdown": daily_data if group_by == "day" else []
    }


@mcp.tool()
def get_trending_products(days: int = 7, min_orders: int = 5) -> str:
    """Get trending products based on recent sales velocity.
    
    Args:
        days: Number of days to analyze (default: 7)
        min_orders: Minimum orders to be considered (default: 5)
        
    Returns:
        JSON string with trending products
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_period_start = datetime.now() - timedelta(days=days)
    previous_period_start = current_period_start - timedelta(days=days)
    
    # Get current period sales
    cursor.execute("""
        SELECT 
            product_id,
            COUNT(*) as order_count,
            SUM(quantity) as units_sold,
            SUM(total_amount) as revenue,
            AVG(unit_price) as avg_price
        FROM sales_transactions
        WHERE transaction_date >= ?
        GROUP BY product_id
        HAVING COUNT(*) >= ?
    """, (current_period_start, min_orders))
    
    current_sales = {}
    for row in cursor.fetchall():
        product_id = row[0]
        current_sales[product_id] = {
            "order_count": row[1],
            "units_sold": row[2],
            "revenue": row[3],
            "avg_price": row[4]
        }
    
    # Get previous period sales for comparison
    cursor.execute("""
        SELECT 
            product_id,
            COUNT(*) as order_count,
            SUM(quantity) as units_sold
        FROM sales_transactions
        WHERE transaction_date >= ? AND transaction_date < ?
        GROUP BY product_id
    """, (previous_period_start, current_period_start))
    
    previous_sales = {}
    for product_id, order_count, units_sold in cursor.fetchall():
        previous_sales[product_id] = {
            "order_count": order_count,
            "units_sold": units_sold
        }
    
    # Calculate trends
    trending = []
    for product_id, current in current_sales.items():
        previous = previous_sales.get(product_id, {"order_count": 0, "units_sold": 0})
        
        # Calculate growth rates
        order_growth = ((current["order_count"] - previous["order_count"]) / previous["order_count"] * 100) if previous["order_count"] > 0 else 100
        unit_growth = ((current["units_sold"] - previous["units_sold"]) / previous["units_sold"] * 100) if previous["units_sold"] > 0 else 100
        
        # Calculate trend score (combination of growth and volume)
        trend_score = (order_growth * 0.4 + unit_growth * 0.4 + current["order_count"] * 0.2)
        
        trending.append({
            "product_id": product_id,
            "current_period": {
                "orders": current["order_count"],
                "units": current["units_sold"],
                "revenue": round(current["revenue"], 2),
                "avg_price": round(current["avg_price"], 2)
            },
            "previous_period": {
                "orders": previous["order_count"],
                "units": previous["units_sold"]
            },
            "growth": {
                "order_growth": round(order_growth, 1),
                "unit_growth": round(unit_growth, 1)
            },
            "trend_score": round(trend_score, 2)
        })
    
    # Sort by trend score
    trending.sort(key=lambda x: x["trend_score"], reverse=True)
    
    conn.close()
    
    return {
        "analysis_period": f"Last {days} days",
        "comparison_period": f"Previous {days} days",
        "min_orders_threshold": min_orders,
        "trending_count": len(trending),
        "trending_products": trending[:20]  # Top 20 trending
    }


@mcp.tool()
def get_customer_insights(customer_id: Optional[str] = None) -> str:
    """Get insights about customer behavior and preferences.
    
    Args:
        customer_id: Optional specific customer ID
        
    Returns:
        JSON string with customer insights
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if customer_id:
        # Get specific customer data
        cursor.execute("""
            SELECT 
                customer_id,
                customer_type,
                COUNT(*) as total_orders,
                SUM(total_amount) as lifetime_value,
                AVG(total_amount) as avg_order_value,
                MIN(transaction_date) as first_purchase,
                MAX(transaction_date) as last_purchase,
                COUNT(DISTINCT product_id) as unique_products
            FROM sales_transactions
            WHERE customer_id = ?
            GROUP BY customer_id, customer_type
        """, (customer_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return {"error": f"Customer {customer_id} not found"}
        
        customer_data = {
            "customer_id": result[0],
            "customer_type": result[1],
            "total_orders": result[2],
            "lifetime_value": round(result[3], 2),
            "avg_order_value": round(result[4], 2),
            "first_purchase": result[5],
            "last_purchase": result[6],
            "unique_products": result[7]
        }
        
        # Get favorite products
        cursor.execute("""
            SELECT 
                product_id,
                COUNT(*) as order_count,
                SUM(quantity) as total_quantity
            FROM sales_transactions
            WHERE customer_id = ?
            GROUP BY product_id
            ORDER BY order_count DESC
            LIMIT 5
        """, (customer_id,))
        
        favorite_products = []
        for product_id, order_count, total_quantity in cursor.fetchall():
            favorite_products.append({
                "product_id": product_id,
                "order_count": order_count,
                "total_quantity": total_quantity
            })
        
        customer_data["favorite_products"] = favorite_products
        
        conn.close()
        return customer_data
    
    else:
        # Get overall customer insights
        cursor.execute("""
            SELECT 
                customer_type,
                COUNT(DISTINCT customer_id) as customer_count,
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value
            FROM sales_transactions
            GROUP BY customer_type
        """)
        
        customer_segments = []
        for row in cursor.fetchall():
            customer_segments.append({
                "customer_type": row[0],
                "customer_count": row[1],
                "total_orders": row[2],
                "total_revenue": round(row[3], 2),
                "avg_order_value": round(row[4], 2)
            })
        
        # Get retention metrics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT customer_id) as total_customers,
                COUNT(DISTINCT CASE 
                    WHEN customer_id IN (
                        SELECT customer_id 
                        FROM sales_transactions 
                        WHERE transaction_date >= datetime('now', '-30 days')
                    ) THEN customer_id 
                END) as active_last_30_days,
                COUNT(DISTINCT CASE 
                    WHEN customer_id IN (
                        SELECT customer_id 
                        FROM sales_transactions 
                        GROUP BY customer_id 
                        HAVING COUNT(*) > 1
                    ) THEN customer_id 
                END) as repeat_customers
            FROM sales_transactions
        """)
        
        total, active_30, repeat = cursor.fetchone()
        
        conn.close()
        
        return {
            "customer_overview": {
                "total_customers": total,
                "active_last_30_days": active_30,
                "repeat_customers": repeat,
                "repeat_rate": round((repeat / total * 100), 2) if total > 0 else 0
            },
            "customer_segments": customer_segments
        }


@mcp.tool()
def get_sales_forecast(days_ahead: int = 7) -> str:
    """Generate sales forecast based on historical trends.
    
    Args:
        days_ahead: Number of days to forecast (default: 7)
        
    Returns:
        JSON string with sales forecast
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get historical daily averages by day of week
    cursor.execute("""
        SELECT 
            CAST(strftime('%w', summary_date) AS INTEGER) as day_of_week,
            AVG(total_orders) as avg_orders,
            AVG(total_revenue) as avg_revenue,
            AVG(total_units_sold) as avg_units,
            COUNT(*) as sample_size
        FROM daily_sales_summary
        WHERE summary_date >= date('now', '-60 days')
        GROUP BY day_of_week
    """)
    
    day_patterns = {}
    for day_of_week, avg_orders, avg_revenue, avg_units, sample_size in cursor.fetchall():
        day_patterns[day_of_week] = {
            "avg_orders": round(avg_orders, 1),
            "avg_revenue": round(avg_revenue, 2),
            "avg_units": round(avg_units, 1),
            "sample_size": sample_size
        }
    
    # Get trend (compare last 30 days to previous 30)
    cursor.execute("""
        SELECT 
            AVG(CASE WHEN summary_date >= date('now', '-30 days') THEN total_revenue END) as recent_avg,
            AVG(CASE WHEN summary_date < date('now', '-30 days') THEN total_revenue END) as previous_avg
        FROM daily_sales_summary
        WHERE summary_date >= date('now', '-60 days')
    """)
    
    recent_avg, previous_avg = cursor.fetchone()
    trend_factor = (recent_avg / previous_avg) if previous_avg and previous_avg > 0 else 1.0
    
    # Generate forecast
    forecast = []
    current_date = datetime.now()
    
    for i in range(days_ahead):
        forecast_date = current_date + timedelta(days=i+1)
        day_of_week = forecast_date.weekday()
        
        if day_of_week in day_patterns:
            base_forecast = day_patterns[day_of_week]
            
            # Apply trend
            forecast_orders = round(base_forecast["avg_orders"] * trend_factor, 0)
            forecast_revenue = round(base_forecast["avg_revenue"] * trend_factor, 2)
            forecast_units = round(base_forecast["avg_units"] * trend_factor, 0)
            
            # Add some uncertainty range (±15%)
            forecast.append({
                "date": forecast_date.strftime('%Y-%m-%d'),
                "day_of_week": forecast_date.strftime('%A'),
                "forecast": {
                    "orders": int(forecast_orders),
                    "revenue": forecast_revenue,
                    "units": int(forecast_units)
                },
                "confidence_range": {
                    "orders": [int(forecast_orders * 0.85), int(forecast_orders * 1.15)],
                    "revenue": [round(forecast_revenue * 0.85, 2), round(forecast_revenue * 1.15, 2)]
                }
            })
    
    # Calculate totals
    total_forecast_orders = sum(f["forecast"]["orders"] for f in forecast)
    total_forecast_revenue = sum(f["forecast"]["revenue"] for f in forecast)
    
    conn.close()
    
    return {
        "forecast_period": f"Next {days_ahead} days",
        "generated_at": datetime.now().isoformat(),
        "trend_factor": round(trend_factor, 3),
        "forecast_summary": {
            "total_orders": total_forecast_orders,
            "total_revenue": round(total_forecast_revenue, 2),
            "daily_average_orders": round(total_forecast_orders / days_ahead, 1),
            "daily_average_revenue": round(total_forecast_revenue / days_ahead, 2)
        },
        "daily_forecast": forecast
    }


if __name__ == "__main__":
    # Run the server
    mcp.run()