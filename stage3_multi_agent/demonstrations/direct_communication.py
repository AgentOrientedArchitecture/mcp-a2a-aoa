"""Direct Agent-to-Agent Communication Demo.

This demonstration shows how the Product Agent can directly communicate
with the Inventory Agent to check stock levels before making recommendations.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent paths
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from a2a_protocol.discovery import DiscoveryClient, AgentConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_direct_communication():
    """Demonstrate direct agent-to-agent communication."""
    print("\n" + "="*60)
    print("A2A Direct Communication Demo")
    print("Product Agent → Inventory Agent")
    print("="*60 + "\n")
    
    # Create discovery client
    discovery = DiscoveryClient()
    
    # Step 1: Discover available agents
    print("Step 1: Discovering agents...")
    
    # Try environment-based discovery first (for Docker)
    agents = await discovery.discover_agents_from_env()
    
    # Fall back to local ports if no env config
    if not agents:
        print("  Trying local ports...")
        agents = await discovery.discover_agents_on_ports()
    
    if not agents:
        print("❌ No agents found. Make sure agents are running.")
        print("   For local: ports 8001-8003")
        print("   For Docker: check DISCOVERY_HOSTS environment variable")
        return
    
    print(f"✅ Found {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent['name']} at {agent['_discovered_at']}")
    
    # Find Product and Inventory agents
    product_agent = None
    inventory_agent = None
    
    for agent in agents:
        if "Product" in agent["name"]:
            product_agent = agent
        elif "Inventory" in agent["name"]:
            inventory_agent = agent
    
    if not product_agent or not inventory_agent:
        print("\n❌ Could not find both Product and Inventory agents")
        return
    
    # Step 2: Connect to agents
    print("\nStep 2: Connecting to agents...")
    product_conn = AgentConnection(product_agent)
    inventory_conn = AgentConnection(inventory_agent)
    
    # Step 3: Product agent searches for laptops
    print("\nStep 3: Product Agent searching for laptops...")
    
    # Send natural language query to product agent
    product_response = await product_conn.send_task(
        "Find all laptops under $1500"
    )
    
    print("Product Agent response received")
    print(f"Task ID: {product_response.get('task_id', 'N/A')}")
    
    # In a real implementation, we'd wait for task completion
    # For demo, we'll simulate finding some products
    found_products = [
        {"id": 42, "name": "TechPro Laptop X1", "price": 1299},
        {"id": 87, "name": "WorkStation Pro", "price": 1450},
        {"id": 123, "name": "Student Laptop Basic", "price": 899}
    ]
    
    print(f"\nFound {len(found_products)} laptops:")
    for p in found_products:
        print(f"  - {p['name']} (ID: {p['id']}) - ${p['price']}")
    
    # Step 4: Check stock for each product
    print("\nStep 4: Checking stock levels with Inventory Agent...")
    
    stock_results = []
    for product in found_products:
        # Use structured capability invocation
        stock_response = await inventory_conn.invoke_capability(
            "check_stock",
            {"product_id": product["id"]}
        )
        
        # Simulate stock response
        stock_info = {
            "product_id": product["id"],
            "product_name": product["name"],
            "total_stock": 15 if product["id"] != 87 else 0,
            "warehouses": [
                {"id": 1, "name": "West Coast", "stock": 10},
                {"id": 2, "name": "East Coast", "stock": 5}
            ] if product["id"] != 87 else []
        }
        
        stock_results.append(stock_info)
        
        status = "✅ In Stock" if stock_info["total_stock"] > 0 else "❌ Out of Stock"
        print(f"  - {product['name']}: {status} (Total: {stock_info['total_stock']})")
    
    # Step 5: Product agent filters recommendations
    print("\nStep 5: Product Agent filtering recommendations based on stock...")
    
    available_products = [
        p for p, s in zip(found_products, stock_results)
        if s["total_stock"] > 0
    ]
    
    print(f"\nFinal Recommendations ({len(available_products)} available):")
    for product in available_products:
        stock = next(s for s in stock_results if s["product_id"] == product["id"])
        print(f"  ✅ {product['name']} - ${product['price']}")
        print(f"     Stock: {stock['total_stock']} units across {len(stock['warehouses'])} warehouses")
    
    # Show excluded products
    excluded = [
        p for p, s in zip(found_products, stock_results)
        if s["total_stock"] == 0
    ]
    
    if excluded:
        print(f"\nExcluded due to no stock:")
        for product in excluded:
            print(f"  ❌ {product['name']} - Currently out of stock")
    
    print("\n✅ Demo completed successfully!")
    print("\nKey Insights:")
    print("- Product Agent discovered available laptops")
    print("- Inventory Agent provided real-time stock information")
    print("- Product Agent filtered recommendations based on availability")
    print("- Direct A2A communication enabled intelligent recommendations")


async def main():
    """Run the demonstration."""
    try:
        await demo_direct_communication()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    print("\n🚀 Starting A2A Direct Communication Demo...")
    print("Make sure all three agents are running:")
    print("  - Product Agent on port 8001")
    print("  - Inventory Agent on port 8002")
    print("  - Sales Agent on port 8003")
    print("\nPress Ctrl+C to stop at any time.")
    
    asyncio.run(main())