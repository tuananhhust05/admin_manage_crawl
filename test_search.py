#!/usr/bin/env python3
"""
Test the search functionality
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_search_api():
    print("🔍 Testing Search API...")
    
    # Test search request
    search_data = {
        "keyword": "Manchester City Match",
        "limit": 10,
        "min_score": 0.6,
        "include_content": True,
        "boost_recent": True
    }
    
    try:
        print(f"\n1. Testing search with keyword: '{search_data['keyword']}'")
        response = requests.post(
            f"{BASE_URL}/api/search-documents",
            json=search_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            
            if data.get('success') and 'data' in data:
                search_results = data['data']
                print(f"   Keyword: {search_results.get('keyword')}")
                print(f"   Results count: {len(search_results.get('results', []))}")
                print(f"   Min score used: {search_results.get('min_score_used')}")
                print(f"   Boost recent applied: {search_results.get('boost_recent_applied')}")
                
                # Show first result
                if search_results.get('results'):
                    first_result = search_results['results'][0]
                    print(f"\n   First result:")
                    print(f"     ID: {first_result.get('id')}")
                    print(f"     Score: {first_result.get('score')}")
                    print(f"     Time: {first_result.get('time')}")
                    print(f"     URL: {first_result.get('url')}")
                    print(f"     Content preview: {first_result.get('content_preview', '')[:100]}...")
            else:
                print(f"   Error: {data.get('error')}")
        else:
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   Error: Request timed out")
    except requests.exceptions.ConnectionError:
        print("   Error: Unable to connect to API")
    except Exception as e:
        print(f"   Error: {e}")

def test_search_page():
    print("\n2. Testing search page...")
    try:
        response = requests.get(f"{BASE_URL}/search")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Search page loaded successfully")
        else:
            print("   ❌ Search page failed to load")
    except Exception as e:
        print(f"   Error: {e}")

def test_invalid_search():
    print("\n3. Testing invalid search request...")
    try:
        # Test without keyword
        response = requests.post(
            f"{BASE_URL}/api/search-documents",
            json={"limit": 10},
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Error: {data.get('error')}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_search_api()
    test_search_page()
    test_invalid_search()
