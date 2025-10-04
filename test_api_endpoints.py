#!/usr/bin/env python3
"""
Test script để kiểm tra các API endpoints
"""

import requests
import json

def test_api_endpoints():
    """Test các API endpoints chính"""
    
    base_url = "http://localhost:5001"  # Thay đổi port nếu cần
    
    print("🔍 Testing API Endpoints...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing Elasticsearch Health...")
    try:
        response = requests.get(f"{base_url}/api/elasticsearch/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Elasticsearch Stats
    print("\n2. Testing Elasticsearch Stats...")
    try:
        response = requests.get(f"{base_url}/api/elasticsearch/stats")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Search API
    print("\n3. Testing Search API...")
    try:
        response = requests.get(f"{base_url}/api/search?q=test&size=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Cleanup API (với fake video_id)
    print("\n4. Testing Cleanup API...")
    try:
        response = requests.post(
            f"{base_url}/api/cleanup-video-data",
            json={"video_id": "507f1f77bcf86cd799439011"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 5: Crawl and Chunk API (với fake video_id)
    print("\n5. Testing Crawl and Chunk API...")
    try:
        response = requests.post(
            f"{base_url}/api/crawl-and-chunk-video",
            json={"video_id": "507f1f77bcf86cd799439011"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n✅ API Endpoints Test Complete!")

if __name__ == "__main__":
    test_api_endpoints()
