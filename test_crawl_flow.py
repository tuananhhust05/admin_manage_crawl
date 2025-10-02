#!/usr/bin/env python3
"""
Test the complete crawl flow
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_complete_flow():
    print("🧪 Testing Complete Crawl Flow...")
    
    # Step 1: Create a test channel
    print("\n1. Creating test channel...")
    channel_data = {
        "url": "https://www.youtube.com/@testchannel",
        "channel_id": "UCorFnMmI4eXS1ftlY4PpTsw",  # Your test channel ID
        "title": "Test Channel",
        "description": "Test channel for crawling"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/youtube-channels",
            json=channel_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            channel_mongo_id = data.get('channel_id')
            print(f"   Created channel with MongoDB ID: {channel_mongo_id}")
        else:
            print(f"   Response: {response.json()}")
            return
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Step 2: Test crawl videos
    print("\n2. Testing crawl videos...")
    crawl_data = {
        "channel_id": "UCorFnMmI4eXS1ftlY4PpTsw"  # YouTube Channel ID
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/crawl-videos",
            json=crawl_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 3: Get videos for the channel
    print("\n3. Getting videos for channel...")
    try:
        response = requests.get(f"{BASE_URL}/api/videos?channel_id=UCorFnMmI4eXS1ftlY4PpTsw")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Videos count: {data.get('count', 0)}")
        if data.get('data'):
            print("   Sample video:")
            video = data['data'][0]
            print(f"     Title: {video.get('title', 'N/A')}")
            print(f"     URL: {video.get('url', 'N/A')}")
            print(f"     Status: {video.get('status', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 4: Test channel detail page URL
    print(f"\n4. Channel detail page URL:")
    print(f"   http://localhost:5001/channel-detail?id={channel_mongo_id}")

if __name__ == "__main__":
    test_complete_flow()
