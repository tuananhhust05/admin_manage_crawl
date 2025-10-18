#!/usr/bin/env python3
"""
Test script for async article generation API
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
SECRET_KEY = "your_secret_key_here"  # Replace with your actual secret key

def test_event_match_end_api():
    """Test the event_match_end API with async article generation"""
    
    print("🧪 Testing Event Match End API with Async Article Generation")
    print("=" * 60)
    
    # Test data
    test_data = {
        "type": "event_match_end",
        "fixture_id": "test_fixture_123",
        "match_data": {
            "home_team": "Chelsea",
            "away_team": "Liverpool",
            "score": "2-1",
            "status": "finished"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Make API call
    url = f"{API_BASE_URL}/api/requests"
    params = {"secret_key": SECRET_KEY}
    
    print(f"📡 Making API call to: {url}")
    print(f"🔑 Using secret key: {SECRET_KEY[:8]}...")
    print(f"📋 Test data: {json.dumps(test_data, indent=2)}")
    print()
    
    try:
        response = requests.post(
            url,
            params=params,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10  # Short timeout since we expect immediate response
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 201:
            result = response.json()
            print("✅ API Response:")
            print(json.dumps(result, indent=2))
            print()
            
            # Check if async processing was started
            if result.get('article_generation_status') == 'processing':
                print("🚀 Async article generation started successfully!")
                print(f"⏰ Processing started at: {result.get('article_generation_started_at')}")
                print("⏳ Article generation will begin in 20 seconds...")
                print()
                
                # Wait a bit and check the request status
                print("⏳ Waiting 25 seconds to check if article was generated...")
                time.sleep(25)
                
                # Check request status
                request_id = result.get('request_id')
                if request_id:
                    check_request_status(request_id)
                    
            else:
                print("⚠️ Async processing not started or failed")
                if result.get('generation_error'):
                    print(f"❌ Error: {result.get('generation_error')}")
                    
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (expected for immediate response)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_request_status(request_id):
    """Check the status of a request"""
    
    print(f"🔍 Checking status of request: {request_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/requests/{request_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("📊 Request Status:")
            print(json.dumps(result, indent=2))
            
            if result.get('article_generated'):
                print("✅ Article generation completed!")
                if result.get('generated_article_id'):
                    print(f"📄 Generated article ID: {result.get('generated_article_id')}")
            else:
                print("⏳ Article generation still in progress or failed")
                if result.get('generation_error'):
                    print(f"❌ Error: {result.get('generation_error')}")
        else:
            print(f"❌ Failed to get request status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking request status: {str(e)}")

def test_without_secret_key():
    """Test API without secret key (should fail)"""
    
    print("\n🧪 Testing API without secret key (should fail)")
    print("=" * 60)
    
    test_data = {
        "type": "event_match_end",
        "fixture_id": "test_fixture_456",
        "match_data": {"test": "data"}
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/requests",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected request without secret key")
        else:
            print("⚠️ Unexpected response - should have been rejected")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Async Article Generation Tests")
    print("=" * 60)
    
    # Test 1: With secret key
    test_event_match_end_api()
    
    # Test 2: Without secret key
    test_without_secret_key()
    
    print("\n🏁 Tests completed!")
    print("=" * 60)
    print("📋 Check the server logs for detailed thread processing information")
    print("🔍 Look for logs with emojis: 🚀, ⏰, 📋, ✅, ❌")
