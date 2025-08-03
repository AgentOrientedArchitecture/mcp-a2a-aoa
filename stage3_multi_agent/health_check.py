#!/usr/bin/env python3
"""Simple health check for A2A agents."""

import sys
import httpx
import asyncio
import json


async def check_agent_health(port: int, host: str = "localhost"):
    """Check if an A2A agent is healthy by fetching its agent card."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to fetch the agent card
            response = await client.get(f"http://{host}:{port}/.well-known/agent-card.json")
            
            if response.status_code == 200:
                card = response.json()
                print(f"✅ Agent '{card.get('name', 'Unknown')}' is healthy on port {port}")
                return True
            else:
                print(f"❌ Agent on port {port} returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to connect to agent on port {port}: {e}")
        return False


async def main():
    """Check health of all standard agents."""
    ports = [8001, 8002, 8003]
    names = ["Product", "Inventory", "Sales"]
    
    print("=== A2A Agent Health Check ===\n")
    
    results = []
    for port, name in zip(ports, names):
        print(f"Checking {name} Agent on port {port}...")
        healthy = await check_agent_health(port)
        results.append((name, healthy))
        print()
    
    # Summary
    print("=== Summary ===")
    all_healthy = all(r[1] for r in results)
    if all_healthy:
        print("✅ All agents are healthy!")
    else:
        print("❌ Some agents are not healthy:")
        for name, healthy in results:
            if not healthy:
                print(f"   - {name} Agent")
    
    return 0 if all_healthy else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))