#!/usr/bin/env python3
"""Test script to verify UI gets proper responses from agents."""

import requests
import json
import time

def test_agent_response():
    """Test that agents return actual results, not task IDs."""
    
    # Test via Web UI backend API
    url = "http://localhost:3001/api/agent/product-catalog/query"
    
    payload = {
        "query": "Show me all laptops"
    }
    
    print("Testing agent response through Web UI backend...")
    print(f"Query: {payload['query']}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if we got a real response or a task ID
            response_text = result.get('response', '')
            
            if 'task' in response_text.lower() and 'started' in response_text.lower():
                print("❌ FAILED: Got async task ID instead of actual results")
                print(f"Response: {response_text}")
            elif 'laptop' in response_text.lower():
                print("✅ SUCCESS: Got actual product results")
                print(f"Response preview: {response_text[:200]}...")
            else:
                print("⚠️  WARNING: Got response but no laptop data found")
                print(f"Response: {response_text[:500]}...")
            
            print(f"\nResponse time: {elapsed:.2f} seconds")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_agent_response()