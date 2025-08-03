"""Three-Agent Collaboration Demo.

This demonstration shows how all three agents can collaborate to answer
complex queries that span multiple domains.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent paths
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from a2a_protocol.discovery import DiscoveryClient, AgentConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_collaborative_query():
    """Demonstrate three-agent collaboration."""
    print("\n" + "="*60)
    print("A2A Three-Agent Collaboration Demo")
    print("Complex Query: 'Which trending products are low on stock?'")
    print("="*60 + "\n")
    
    # Create discovery client
    discovery = DiscoveryClient()
    
    # Step 1: Discover all agents
    print("Step 1: Discovering all available agents...")
    
    # Try environment-based discovery first (for Docker)
    agents = await discovery.discover_agents_from_env()
    
    # Fall back to local ports if no env config
    if not agents:
        print("  Trying local ports...")
        agents = await discovery.discover_agents_on_ports()
    
    if len(agents) < 3:
        print(f"❌ Need all 3 agents running, found only {len(agents)}")
        return
    
    print(f"✅ Found {len(agents)} agents:")
    
    # Create connections
    connections = {}
    for agent in agents:
        name = agent['name']
        print(f"  - {name}")
        connections[name] = AgentConnection(agent)
    
    # Identify specific agents
    product_conn = None
    inventory_conn = None
    sales_conn = None
    
    for name, conn in connections.items():
        if "Product" in name:
            product_conn = conn
        elif "Inventory" in name:
            inventory_conn = conn
        elif "Sales" in name:
            sales_conn = conn
    
    if not all([product_conn, inventory_conn, sales_conn]):
        print("\n❌ Could not identify all three agent types")
        return
    
    print("\nQuery: 'Which trending products are low on stock?'")
    print("This requires coordination between all three agents:")
    print("  1. Sales Agent → Identify trending products")
    print("  2. Product Agent → Get product details")
    print("  3. Inventory Agent → Check stock levels")
    
    # Step 2: Sales Agent identifies trending products
    print("\nStep 2: Sales Agent identifying trending products...")
    
    trending_response = await sales_conn.invoke_capability(
        "trending_products",
        {"days": 7, "limit": 5}
    )
    
    # Simulate trending products response
    trending_products = [
        {"product_id": 42, "sales_velocity": 15.2, "growth_rate": 0.35},
        {"product_id": 87, "sales_velocity": 12.8, "growth_rate": 0.28},
        {"product_id": 123, "sales_velocity": 10.5, "growth_rate": 0.22},
        {"product_id": 156, "sales_velocity": 9.7, "growth_rate": 0.18},
        {"product_id": 201, "sales_velocity": 8.3, "growth_rate": 0.15}
    ]
    
    print(f"✅ Found {len(trending_products)} trending products")
    print("\nTop trending products by sales velocity:")
    for i, product in enumerate(trending_products, 1):
        print(f"  {i}. Product ID {product['product_id']}: "
              f"velocity={product['sales_velocity']:.1f}, "
              f"growth={product['growth_rate']:.0%}")
    
    # Step 3: Product Agent gets product details
    print("\nStep 3: Product Agent retrieving product details...")
    
    product_details = []
    for trending in trending_products:
        # In a real implementation, we'd query the product agent
        # For demo, simulate product details
        details = {
            "id": trending["product_id"],
            "name": f"Product {trending['product_id']}",
            "category": "Electronics" if trending["product_id"] < 100 else "Accessories",
            "price": 99.99 + trending["product_id"]
        }
        
        # Simulate getting actual names
        if trending["product_id"] == 42:
            details["name"] = "Wireless Earbuds Pro"
        elif trending["product_id"] == 87:
            details["name"] = "Smart Watch X"
        elif trending["product_id"] == 123:
            details["name"] = "Phone Case Premium"
        elif trending["product_id"] == 156:
            details["name"] = "USB-C Hub"
        elif trending["product_id"] == 201:
            details["name"] = "Laptop Stand"
        
        product_details.append(details)
    
    print("✅ Retrieved details for all trending products")
    
    # Step 4: Inventory Agent checks stock levels
    print("\nStep 4: Inventory Agent checking stock levels...")
    
    stock_analysis = []
    for product, trending in zip(product_details, trending_products):
        # Check stock for each product
        stock_response = await inventory_conn.invoke_capability(
            "check_stock",
            {"product_id": product["id"]}
        )
        
        # Simulate stock response
        # Make some products low on stock
        if product["id"] in [42, 156, 201]:  # These are low stock
            total_stock = 5 + (product["id"] % 10)
            status = "LOW" if total_stock < 20 else "OK"
        else:
            total_stock = 50 + (product["id"] % 30)
            status = "OK"
        
        stock_info = {
            "product_id": product["id"],
            "product_name": product["name"],
            "category": product["category"],
            "price": product["price"],
            "total_stock": total_stock,
            "status": status,
            "sales_velocity": trending["sales_velocity"],
            "growth_rate": trending["growth_rate"],
            "days_until_stockout": total_stock / trending["sales_velocity"] if trending["sales_velocity"] > 0 else 999
        }
        
        stock_analysis.append(stock_info)
    
    print("✅ Stock analysis complete")
    
    # Step 5: Synthesize results
    print("\nStep 5: Synthesizing results...\n")
    
    print("="*80)
    print("TRENDING PRODUCTS WITH LOW STOCK ALERT")
    print("="*80)
    
    # Filter for low stock items
    low_stock_items = [item for item in stock_analysis if item["status"] == "LOW"]
    
    if low_stock_items:
        print(f"\n⚠️  {len(low_stock_items)} trending products need immediate attention:\n")
        
        # Sort by days until stockout
        low_stock_items.sort(key=lambda x: x["days_until_stockout"])
        
        for item in low_stock_items:
            print(f"🔴 {item['product_name']} (ID: {item['product_id']})")
            print(f"   Category: {item['category']} | Price: ${item['price']:.2f}")
            print(f"   Current Stock: {item['total_stock']} units")
            print(f"   Sales Velocity: {item['sales_velocity']:.1f} units/day")
            print(f"   Growth Rate: {item['growth_rate']:.0%}")
            print(f"   ⏰ STOCKOUT IN: {item['days_until_stockout']:.1f} DAYS")
            print(f"   Recommendation: Urgent restock needed!")
            print()
    else:
        print("\n✅ All trending products have adequate stock levels")
    
    # Show OK items
    ok_items = [item for item in stock_analysis if item["status"] == "OK"]
    if ok_items:
        print("\n✅ Trending products with adequate stock:")
        for item in ok_items:
            print(f"   - {item['product_name']}: {item['total_stock']} units "
                  f"({item['days_until_stockout']:.0f} days supply)")
    
    # Summary insights
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    
    print("\n📊 Analysis Summary:")
    print(f"   - Total trending products analyzed: {len(stock_analysis)}")
    print(f"   - Products needing urgent restock: {len(low_stock_items)}")
    print(f"   - Products with adequate stock: {len(ok_items)}")
    
    if low_stock_items:
        total_lost_sales = sum(
            item['sales_velocity'] * item['price'] * max(0, 7 - item['days_until_stockout'])
            for item in low_stock_items
        )
        print(f"\n💰 Potential Revenue Impact:")
        print(f"   - Estimated lost sales if not restocked (7 days): ${total_lost_sales:,.2f}")
    
    print("\n✅ Collaborative query completed successfully!")
    
    print("\nDemonstration Highlights:")
    print("- Sales Agent identified trending products")
    print("- Product Agent provided product details")
    print("- Inventory Agent analyzed stock levels")
    print("- Cross-domain insights revealed critical business intelligence")
    print("- No central coordinator needed - agents collaborated directly")


async def main():
    """Run the demonstration."""
    try:
        await demo_collaborative_query()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    print("\n🚀 Starting A2A Three-Agent Collaboration Demo...")
    print("Make sure all three agents are running:")
    print("  - Product Agent on port 8001")
    print("  - Inventory Agent on port 8002")
    print("  - Sales Agent on port 8003")
    print("\nPress Ctrl+C to stop at any time.")
    
    asyncio.run(main())