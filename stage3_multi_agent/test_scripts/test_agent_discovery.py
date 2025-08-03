#!/usr/bin/env python3
"""Test agent discovery functionality."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from a2a_protocol.discovery import DiscoveryClient, AgentConnection


async def test_discovery():
    """Test discovering agents on local ports."""
    
    print("=== Testing Agent Discovery ===\n")
    
    # Create discovery client
    discovery = DiscoveryClient(timeout=5)
    
    # Test 1: Discover agents on known ports
    print("1. Discovering agents on default ports...")
    agents = await discovery.discover_agents_on_ports(
        host="localhost",
        ports=[8001, 8002, 8003]
    )
    
    print(f"Found {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent.get('name')} at {agent.get('_discovered_at')}")
        cap_names = []
        
        # Check skills (A2A SDK format)
        for skill in agent.get('skills', []):
            if isinstance(skill, dict):
                cap_names.append(skill.get('name') or skill.get('id'))
        
        # Check capabilities
        capabilities = agent.get('capabilities', [])
        if isinstance(capabilities, dict):
            # A2A SDK format - capabilities is a dict
            pass
        elif isinstance(capabilities, list):
            for cap in capabilities:
                if isinstance(cap, dict):
                    cap_names.append(cap.get('name', 'unknown'))
                elif isinstance(cap, str):
                    cap_names.append(cap)
        
        if cap_names:
            print(f"    Capabilities: {cap_names}")
    
    # Test 2: Find agents with specific capability
    print("\n2. Finding agents with 'search_products' capability...")
    product_agents = await discovery.find_agents_with_capability("search_products")
    print(f"Found {len(product_agents)} agents with product search capability")
    
    # Test 3: Connect to an agent and send a simple query
    if agents:
        print("\n3. Testing agent connection...")
        first_agent = agents[0]
        connection = AgentConnection(first_agent)
        
        print(f"Connecting to {connection.name}...")
        print(f"Capabilities: {connection.get_capabilities()}")
        
        # Send a simple task
        print("\nSending test query...")
        response = await connection.send_task("Hello, what can you do?")
        print(f"Response: {response}")
    
    # Test 4: Test capability invocation
    if product_agents:
        print("\n4. Testing capability invocation...")
        product_agent = product_agents[0]
        connection = AgentConnection(product_agent)
        
        response = await connection.invoke_capability(
            "search_products",
            {"query": "laptop", "filters": {"max_price": 1000}}
        )
        print(f"Capability response: {response}")
    
    print("\n=== Discovery Test Complete ===")


async def test_inter_agent_communication():
    """Test agent-to-agent communication."""
    
    print("\n=== Testing Inter-Agent Communication ===\n")
    
    discovery = DiscoveryClient()
    
    # Discover all available agents
    agents = await discovery.discover_agents_on_ports()
    
    if len(agents) < 2:
        print("Need at least 2 agents running for inter-agent communication test")
        return
    
    # Get connections to different agents
    agent_connections = {
        agent.get('name'): AgentConnection(agent)
        for agent in agents
    }
    
    print(f"Available agents: {list(agent_connections.keys())}")
    
    # Example: Product agent asks inventory agent about stock
    if "Product Catalog Agent" in agent_connections and "Inventory Management Agent" in agent_connections:
        print("\nTesting Product->Inventory communication...")
        
        product_conn = agent_connections["Product Catalog Agent"]
        
        # Send a query that requires inventory info
        response = await product_conn.send_task(
            "Check if we have laptops under $1000 in stock"
        )
        print(f"Response: {response}")


if __name__ == "__main__":
    # First run basic discovery
    asyncio.run(test_discovery())
    
    # Then test inter-agent communication
    asyncio.run(test_inter_agent_communication())