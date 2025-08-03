"""Docker Demo - Run demonstrations in Docker environment.

This script is designed to run inside a Docker container and
discover other agents using Docker's internal DNS.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent paths
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

# Import demonstrations
from direct_communication import demo_direct_communication
from agent_discovery import demo_agent_discovery
from collaborative_query import demo_collaborative_query


async def run_all_demos():
    """Run all demonstrations in sequence."""
    print("\n" + "="*60)
    print("A2A Docker Demonstration Suite")
    print("="*60 + "\n")
    
    # Set discovery hosts for Docker environment
    if not os.getenv("DISCOVERY_HOSTS"):
        # Set default Docker service names
        os.environ["DISCOVERY_HOSTS"] = "product-agent:8001,inventory-agent:8002,sales-agent:8003"
        print("Using Docker service discovery:")
        print(f"  DISCOVERY_HOSTS={os.environ['DISCOVERY_HOSTS']}")
    
    print("\nThis will run three demonstrations:")
    print("1. Direct Communication - Product Agent talks to Inventory Agent")
    print("2. Agent Discovery - Dynamic discovery of all agents")
    print("3. Collaborative Query - All three agents working together")
    
    print("\n" + "-"*60)
    input("Press Enter to start Demo 1: Direct Communication...")
    
    try:
        await demo_direct_communication()
    except Exception as e:
        print(f"\n❌ Demo 1 failed: {e}")
    
    print("\n" + "-"*60)
    input("Press Enter to start Demo 2: Agent Discovery...")
    
    try:
        await demo_agent_discovery()
    except Exception as e:
        print(f"\n❌ Demo 2 failed: {e}")
    
    print("\n" + "-"*60)
    input("Press Enter to start Demo 3: Collaborative Query...")
    
    try:
        await demo_collaborative_query()
    except Exception as e:
        print(f"\n❌ Demo 3 failed: {e}")
    
    print("\n" + "="*60)
    print("All demonstrations completed!")
    print("="*60)


async def test_connectivity():
    """Test connectivity to all agents."""
    from a2a_protocol.discovery import DiscoveryClient
    
    print("\n🔍 Testing agent connectivity...")
    discovery = DiscoveryClient()
    
    # Discover agents
    agents = await discovery.discover_agents_from_env()
    
    if not agents:
        print("❌ No agents discovered. Check that all services are running.")
        print("   Expected services: product-agent, inventory-agent, sales-agent")
        return False
    
    print(f"✅ Successfully connected to {len(agents)} agents:")
    for agent in agents:
        print(f"   - {agent['name']} at {agent['_discovered_at']}")
    
    # Check we have all three
    agent_names = {agent['name'] for agent in agents}
    expected = {"Product Catalog Agent", "Inventory Management Agent", "Sales Analytics Agent"}
    missing = expected - agent_names
    
    if missing:
        print(f"\n⚠️  Missing agents: {', '.join(missing)}")
        return False
    
    print("\n✅ All agents are running and accessible!")
    return True


async def main():
    """Main entry point."""
    print("\n🚀 A2A Docker Demonstration")
    print("This demo runs inside Docker and uses Docker's internal DNS")
    print("to discover and communicate with other agent containers.\n")
    
    # Test connectivity first
    if not await test_connectivity():
        print("\n❌ Please ensure all agent services are running:")
        print("   docker compose up")
        return
    
    # Run demonstrations
    await run_all_demos()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")