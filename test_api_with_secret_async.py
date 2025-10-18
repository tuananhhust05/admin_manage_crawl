#!/usr/bin/env python3
"""
Test script for async article generation with actual secret key
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
SECRET_KEY = "your_actual_secret_key"  # Replace with your actual secret key from env

def test_async_article_generation():
    """Test async article generation with real secret key"""
    
    print("🧪 Testing Async Article Generation API")
    print("=" * 50)
    
    # Test data for event_match_end
    test_data = {
        "type": "event_match_end",
        "fixture_id": f"fixture_{int(time.time())}",  # Unique fixture ID
        "match_data": {
            "home_team": "Chelsea",
            "away_team": "Liverpool", 
            "score": "2-1",
            "status": "finished",
            "events": [
                {"type": "goal", "team": "home", "minute": 15, "player": "Caicedo"},
                {"type": "goal", "team": "away", "minute": 65, "player": "Gakpo"},
                {"type": "goal", "team": "home", "minute": 95, "player": "Estêvão"}
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print(f"📡 API URL: {API_BASE_URL}/api/requests")
    print(f"🔑 Secret Key: {SECRET_KEY[:8]}...")
    print(f"📋 Fixture ID: {test_data['fixture_id']}")
    print()
    
    # Make API call
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/requests",
            params={"secret_key": SECRET_KEY},
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Request saved successfully!")
            print(f"📄 Request ID: {result.get('request_id')}")
            print(f"🔄 Generation Status: {result.get('article_generation_status')}")
            print(f"⏰ Started At: {result.get('article_generation_started_at')}")
            print()
            
            if result.get('article_generation_status') == 'processing':
                print("🚀 Async article generation started!")
                print("⏳ Waiting 25 seconds for article generation to complete...")
                time.sleep(25)
                
                # Check if article was generated
                check_generated_articles(test_data['fixture_id'])
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_generated_articles(fixture_id):
    """Check if article was generated for the fixture"""
    
    print(f"\n🔍 Checking generated articles for fixture: {fixture_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/generated-articles")
        
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            
            # Find article for our fixture
            matching_articles = [a for a in articles if a.get('fixture_id') == fixture_id]
            
            if matching_articles:
                article = matching_articles[0]
                print("✅ Article generated successfully!")
                print(f"📄 Article ID: {article.get('_id')}")
                print(f"📝 Title: {article.get('title')}")
                print(f"📊 Source Requests: {article.get('source_requests_count')}")
                print(f"⏰ Generated At: {article.get('generated_at')}")
                print()
                print("📖 Article Content Preview:")
                content = article.get('content', '')
                print(content[:500] + "..." if len(content) > 500 else content)
            else:
                print("⏳ No article found yet - may still be processing")
                
        else:
            print(f"❌ Failed to get generated articles: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking generated articles: {str(e)}")

def test_multiple_requests():
    """Test multiple event_match_end requests"""
    
    print("\n🧪 Testing Multiple Event Match End Requests")
    print("=" * 50)
    
    fixture_ids = []
    
    for i in range(3):
        fixture_id = f"fixture_batch_{int(time.time())}_{i}"
        fixture_ids.append(fixture_id)
        
        test_data = {
            "type": "event_match_end",
            "fixture_id": fixture_id,
            "match_data": {
                "home_team": f"Team A{i}",
                "away_team": f"Team B{i}",
                "score": f"{i+1}-{i}",
                "status": "finished"
            }
        }
        
        print(f"📡 Sending request {i+1}/3 for fixture: {fixture_id}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/requests",
                params={"secret_key": SECRET_KEY},
                json=test_data,
                timeout=5
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Request {i+1} saved - Status: {result.get('article_generation_status')}")
            else:
                print(f"❌ Request {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request {i+1} error: {str(e)}")
        
        time.sleep(1)  # Small delay between requests
    
    print(f"\n⏳ Waiting 30 seconds for all articles to be generated...")
    time.sleep(30)
    
    # Check all generated articles
    print("\n🔍 Checking all generated articles...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/generated-articles")
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            
            print(f"📊 Total generated articles: {len(articles)}")
            
            for fixture_id in fixture_ids:
                matching = [a for a in articles if a.get('fixture_id') == fixture_id]
                if matching:
                    print(f"✅ {fixture_id}: Article generated")
                else:
                    print(f"⏳ {fixture_id}: Still processing or failed")
                    
    except Exception as e:
        print(f"❌ Error checking articles: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Async Article Generation Tests")
    print("=" * 50)
    
    # Test 1: Single request
    test_async_article_generation()
    
    # Test 2: Multiple requests
    test_multiple_requests()
    
    print("\n🏁 All tests completed!")
    print("=" * 50)
    print("📋 Check server logs for detailed thread processing information")
    print("🔍 Look for thread logs with emojis: 🚀, ⏰, 📋, ✅, ❌")
