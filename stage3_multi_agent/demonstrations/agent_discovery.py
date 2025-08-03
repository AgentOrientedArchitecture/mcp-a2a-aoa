"""Agent Discovery Demo.

This demonstration shows how agents can dynamically discover each other
using the A2A protocol and Agent Cards.
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


async def demo_agent_discovery():
    """Demonstrate dynamic agent discovery."""
    print("\n" + "="*60)
    print("A2A Agent Discovery Demo")
    print("Discovering agents and their capabilities")
    print("="*60 + "\n")
    
    # Create discovery client
    discovery = DiscoveryClient()
    
    # Step 1: Discover agents
    print("Step 1: Scanning for agents...")
    
    # Try environment-based discovery first (for Docker)
    agents = await discovery.discover_agents_from_env()
    
    # Fall back to local ports if no env config
    if not agents:
        print("  No agents found via environment, trying local ports (8001-8003)...")
        agents = await discovery.discover_agents_on_ports()
    
    if not agents:
        print("❌ No agents found. Make sure agents are running.")
        return
    
    print(f"\n✅ Discovered {len(agents)} agents!\n")
    
    # Step 2: Display detailed information about each agent
    print("Step 2: Analyzing discovered agents...\n")
    
    for i, agent in enumerate(agents, 1):
        print(f"Agent {i}: {agent['name']}")
        print(f"  📍 Location: {agent['_discovered_at']}")
        print(f"  📄 Description: {agent['description']}")
        print(f"  🔌 Version: {agent['version']}")
        
        # Show endpoints
        endpoints = agent.get('endpoints', {})
        print(f"  🌐 Endpoints:")
        print(f"     - HTTP: {endpoints.get('http', 'N/A')}")
        print(f"     - WebSocket: {endpoints.get('websocket', 'N/A')}")
        
        # Show capabilities
        capabilities = agent.get('capabilities', [])
        print(f"  🎯 Capabilities ({len(capabilities)}):")
        for cap in capabilities:
            print(f"     - {cap['name']}: {cap['description']}")
        
        # Show metadata
        metadata = agent.get('metadata', {})
        if metadata:
            print(f"  📊 Metadata:")
            print(f"     - Domain: {metadata.get('domain', 'N/A')}")
            print(f"     - SMOL Agent: {metadata.get('smol_agent', False)}")
            if 'mcp_tools' in metadata:
                print(f"     - MCP Tools: {len(metadata['mcp_tools'])} available")
            if 'cross_domain_access' in metadata:
                print(f"     - Cross-Domain Access: {', '.join(metadata['cross_domain_access'])}")
        
        print()
    
    # Step 3: Find agents with specific capabilities
    print("Step 3: Searching for specific capabilities...\n")
    
    # Search for agents that can check stock
    print("🔍 Looking for agents with 'check_stock' capability...")
    stock_agents = await discovery.find_agents_with_capability("check_stock")
    
    if stock_agents:
        print(f"✅ Found {len(stock_agents)} agent(s) with stock checking:")
        for agent in stock_agents:
            print(f"   - {agent['name']}")
    else:
        print("❌ No agents found with stock checking capability")
    
    # Search for agents that can analyze sales
    print("\n🔍 Looking for agents with 'sales_summary' capability...")
    sales_agents = await discovery.find_agents_with_capability("sales_summary")
    
    if sales_agents:
        print(f"✅ Found {len(sales_agents)} agent(s) with sales analysis:")
        for agent in sales_agents:
            print(f"   - {agent['name']}")
    else:
        print("❌ No agents found with sales analysis capability")
    
    # Step 4: Test agent discovery endpoint
    print("\nStep 4: Testing agent discovery endpoints...\n")
    
    if agents:
        test_agent = agents[0]
        print(f"Testing discovery endpoint on {test_agent['name']}...")
        
        # Query for agents with specific capabilities
        discovered = await discovery.query_agent_discovery_endpoint(
            test_agent['_discovered_at'],
            required_capabilities=["analyze_prices"]
        )
        
        if discovered:
            print(f"✅ Agent reported {len(discovered)} matching agents")
            for d in discovered:
                print(f"   - {d.get('name', 'Unknown')}")
        else:
            print("❌ No matching agents reported")
    
    # Step 5: Show discovery cache
    print("\nStep 5: Discovery cache summary...\n")
    
    cached = discovery.get_discovered_agents()
    print(f"📦 Cached agents: {len(cached)}")
    for name, card in cached.items():
        caps = [c['name'] for c in card.get('capabilities', [])]
        print(f"   - {name}: {len(caps)} capabilities")
    
    # Step 6: Demonstrate capability matrix
    print("\nStep 6: Agent Capability Matrix\n")
    
    # Build capability matrix
    all_capabilities = set()
    for agent in agents:
        for cap in agent.get('capabilities', []):
            all_capabilities.add(cap['name'])
    
    # Create matrix header
    print("Capability".ljust(30), end="")
    for agent in agents:
        short_name = agent['name'].split()[0][:10]
        print(short_name.center(12), end="")
    print()
    
    print("-" * (30 + 12 * len(agents)))
    
    # Fill matrix
    for capability in sorted(all_capabilities):
        print(capability.ljust(30), end="")
        for agent in agents:
            agent_caps = [c['name'] for c in agent.get('capabilities', [])]
            if capability in agent_caps:
                print("✓".center(12), end="")
            else:
                print("-".center(12), end="")
        print()
    
    print("\n✅ Discovery demo completed successfully!")
    
    print("\nKey Insights:")
    print("- Agents can be discovered dynamically via well-known URLs")
    print("- Agent Cards provide rich metadata about capabilities")
    print("- Discovery enables dynamic agent collaboration")
    print("- No central registry required for basic discovery")


async def main():
    """Run the demonstration."""
    try:
        await demo_agent_discovery()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    print("\n🚀 Starting A2A Agent Discovery Demo...")
    print("Make sure all three agents are running:")
    print("  - Product Agent on port 8001")
    print("  - Inventory Agent on port 8002")
    print("  - Sales Agent on port 8003")
    print("\nPress Ctrl+C to stop at any time.")
    
    asyncio.run(main())