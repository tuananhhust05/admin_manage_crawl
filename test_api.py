#!/usr/bin/env python3
"""
Test script for YouTube Channels Manager API
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_api():
    print("🧪 Testing YouTube Channels Manager API...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Test endpoint
    print("\n2. Testing test endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Get channels
    print("\n3. Testing get channels...")
    try:
        response = requests.get(f"{BASE_URL}/api/youtube-channels")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Channels count: {data.get('count', 0)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Crawl videos (if channels exist)
    print("\n4. Testing crawl videos...")
    try:
        # First get a channel ID
        response = requests.get(f"{BASE_URL}/api/youtube-channels")
        if response.status_code == 200:
            data = response.json()
            if data.get('count', 0) > 0:
                channel_id = data['data'][0]['channel_id']
                print(f"   Using channel ID: {channel_id}")
                
                # Test crawl
                crawl_data = {"channel_id": channel_id}
                response = requests.post(
                    f"{BASE_URL}/api/crawl-videos",
                    json=crawl_data,
                    headers={'Content-Type': 'application/json'}
                )
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.json()}")
            else:
                print("   No channels found to test crawl")
        else:
            print("   Could not get channels")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Get videos
    print("\n5. Testing get videos...")
    try:
        response = requests.get(f"{BASE_URL}/api/videos")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Videos count: {data.get('count', 0)}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_api()
