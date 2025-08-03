#!/usr/bin/env python3
"""Demonstrate agent-to-agent communication in the A2A protocol."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from a2a_protocol.discovery import DiscoveryClient, AgentConnection


async def demo_agent_discovery():
    """Demonstrate basic agent discovery."""
    print("=== Agent Discovery Demo ===\n")
    
    discovery = DiscoveryClient()
    
    print("Discovering agents on local network...")
    agents = await discovery.discover_agents_on_ports()
    
    print(f"\nFound {len(agents)} agents:")
    for agent in agents:
        print(f"\n📍 {agent.get('name')}")
        print(f"   Description: {agent.get('description')}")
        print(f"   Endpoint: {agent.get('_discovered_at')}")
        capabilities = []
        for cap in agent.get('capabilities', []):
            if isinstance(cap, dict):
                capabilities.append(cap.get('name', 'unnamed'))
            elif isinstance(cap, str):
                capabilities.append(cap)
        print(f"   Capabilities: {', '.join(capabilities)}")


async def demo_direct_communication():
    """Demonstrate direct agent-to-agent communication."""
    print("\n\n=== Direct Agent Communication Demo ===\n")
    
    discovery = DiscoveryClient()
    agents = await discovery.discover_agents_on_ports()
    
    if not agents:
        print("❌ No agents found. Make sure agents are running.")
        return
    
    # Connect to the first agent
    agent = agents[0]
    connection = AgentConnection(agent)
    
    print(f"Connecting to {connection.name}...")
    
    # Test 1: Simple query
    print("\n1. Sending simple query...")
    response = await connection.send_task("Hello! What can you do?")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 2: Complex query
    if "Product Catalog Agent" in connection.name:
        print("\n2. Sending product search query...")
        response = await connection.send_task("Find me laptops under $1000")
        print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 3: Capability invocation
    if connection.get_capabilities():
        cap = connection.get_capabilities()[0]
        print(f"\n3. Invoking capability '{cap}'...")
        response = await connection.invoke_capability(cap, {})
        print(f"Response: {json.dumps(response, indent=2)}")


async def demo_multi_agent_scenario():
    """Demonstrate a multi-agent interaction scenario."""
    print("\n\n=== Multi-Agent Scenario Demo ===\n")
    
    discovery = DiscoveryClient()
    agents = await discovery.discover_agents_on_ports()
    
    # Create connections to all agents
    connections = {
        agent.get('name'): AgentConnection(agent)
        for agent in agents
    }
    
    print(f"Connected to {len(connections)} agents: {list(connections.keys())}")
    
    # Scenario 1: Product search with inventory check
    if "Product Catalog Agent" in connections and "Inventory Management Agent" in connections:
        print("\n📦 Scenario: Product Search with Inventory Check")
        
        product_agent = connections["Product Catalog Agent"]
        inventory_agent = connections["Inventory Management Agent"]
        
        # Step 1: Search for products
        print("\nStep 1: Searching for gaming laptops...")
        search_response = await product_agent.send_task("Find gaming laptops under $3500")
        print(f"Found products: {search_response}")
        
        # Step 2: Check inventory for a specific product
        print("\nStep 2: Checking inventory for a product...")
        inventory_response = await inventory_agent.send_task("Check stock level for product ID LAPTOP-001")
        print(f"Inventory status: {inventory_response}")
    
    # Scenario 2: Sales analysis with product recommendations
    if "Sales Analytics Agent" in connections and "Product Catalog Agent" in connections:
        print("\n\n📊 Scenario: Sales Analysis with Recommendations")
        
        sales_agent = connections["Sales Analytics Agent"]
        product_agent = connections["Product Catalog Agent"]
        
        # Step 1: Get top selling categories
        print("\nStep 1: Getting top selling categories...")
        sales_response = await sales_agent.send_task("What are the top selling product categories?")
        print(f"Top categories: {sales_response}")
        
        # Step 2: Get recommendations based on sales data
        print("\nStep 2: Getting product recommendations...")
        rec_response = await product_agent.send_task(
            "Recommend products from the electronics category for customers with a $500 budget"
        )
        print(f"Recommendations: {rec_response}")


async def demo_agent_querying_agent():
    """Demonstrate an agent querying another agent."""
    print("\n\n=== Agent-to-Agent Query Demo ===\n")
    
    discovery = DiscoveryClient()
    agents = await discovery.discover_agents_on_ports()
    
    if len(agents) < 2:
        print("❌ Need at least 2 agents for this demo")
        return
    
    # Connect to the first agent
    agent1 = agents[0]
    connection = AgentConnection(agent1)
    
    print(f"Using {agent1.get('name')} to query other agents...\n")
    
    # Have agent1 discover other agents
    print("1. Agent discovering other agents...")
    response = await connection.invoke_capability("discover_agents", {})
    print(f"Discovery response: {json.dumps(response, indent=2)}")
    
    # Have agent1 query another agent
    if len(agents) > 1:
        target_agent = agents[1].get('name')
        print(f"\n2. Having {agent1.get('name')} query {target_agent}...")
        
        response = await connection.invoke_capability(
            "query_agent",
            {
                "agent_name": target_agent,
                "query": "What are your main capabilities?"
            }
        )
        print(f"Query response: {json.dumps(response, indent=2)}")


async def main():
    """Run all demonstrations."""
    print("🚀 A2A Agent Communication Demonstration\n")
    
    # Run each demo
    await demo_agent_discovery()
    await demo_direct_communication()
    await demo_multi_agent_scenario()
    await demo_agent_querying_agent()
    
    print("\n\n✅ Demonstration complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")