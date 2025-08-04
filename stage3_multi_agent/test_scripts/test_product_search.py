#!/usr/bin/env python3
"""Test script to verify product search functionality."""

import requests
import json

def test_product_search():
    """Test product search with various parameter combinations."""
    
    # Test endpoint
    url = "http://localhost:8001/execute"
    
    # Test queries
    test_cases = [
        {
            "name": "Search for all laptops",
            "query": "Show me all laptops"
        },
        {
            "name": "Search for laptops in stock",
            "query": "Show me laptops that are in stock"
        },
        {
            "name": "Count products",
            "query": "How many laptops are in the catalog?"
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {test['name']}")
        print(f"Query: {test['query']}")
        print("-"*60)
        
        payload = {
            "task": test['query']
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"Status: SUCCESS")
                print(f"Response: {result.get('result', 'No result')[:500]}...")
            else:
                print(f"Status: FAILED - Status code {response.status_code}")
                print(f"Response: {response.text[:500]}")
        except Exception as e:
            print(f"Status: ERROR - {str(e)}")
    
    print(f"\n{'='*60}")
    print("Tests completed!")

if __name__ == "__main__":
    test_product_search()