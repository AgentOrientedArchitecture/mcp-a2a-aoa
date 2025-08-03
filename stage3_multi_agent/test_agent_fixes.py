#!/usr/bin/env python3
"""Quick test script to verify agent fixes."""

import asyncio
import httpx
import json

async def test_agent(name: str, port: int):
    """Test a single agent."""
    print(f"\n=== Testing {name} on port {port} ===")
    
    # Test simple query
    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": f"test-{name}",
                "role": "user",
                "parts": [{"text": "What can you do?"}]
            }
        },
        "id": f"req-{name}"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"http://localhost:{port}/", json=payload)
            result = response.json()
            
            if "result" in result:
                message = result["result"]
                if "parts" in message and message["parts"]:
                    text = message["parts"][0].get("text", "No text in response")
                    print(f"✅ Response: {text[:100]}...")
                else:
                    print(f"❌ No parts in message: {message}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Failed: {e}")

async def main():
    """Test all agents."""
    agents = [
        ("Product Catalog Agent", 8001),
        ("Inventory Management Agent", 8002),
        ("Sales Analytics Agent", 8003)
    ]
    
    # Test each agent
    for name, port in agents:
        await test_agent(name, port)
    
    print("\n=== Test specific functionality ===")
    
    # Test inventory check
    print("\nTesting inventory check...")
    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "test-inventory",
                "role": "user",
                "parts": [{"text": "Check stock for product ID 100"}]
            }
        },
        "id": "req-inventory"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://localhost:8002/", json=payload)
            result = response.json()
            
            if "result" in result:
                message = result["result"]
                if "parts" in message and message["parts"]:
                    text = message["parts"][0].get("text", "No text")
                    print(f"✅ Inventory response: {text[:200]}...")
                    
    except Exception as e:
        print(f"❌ Inventory check failed: {e}")
    
    # Test sales analysis
    print("\nTesting sales analysis...")
    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "test-sales",
                "role": "user",
                "parts": [{"text": "Show me top selling categories"}]
            }
        },
        "id": "req-sales"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://localhost:8003/", json=payload)
            result = response.json()
            
            if "result" in result:
                message = result["result"]
                if "parts" in message and message["parts"]:
                    text = message["parts"][0].get("text", "No text")
                    print(f"✅ Sales response: {text[:200]}...")
                    
    except Exception as e:
        print(f"❌ Sales analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())