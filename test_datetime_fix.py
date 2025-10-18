#!/usr/bin/env python3
"""
Test script to verify datetime serialization fix
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
SECRET_KEY = "your_secret_key_here"  # Replace with your actual secret key

def test_datetime_serialization_fix():
    """Test that datetime objects are properly serialized"""
    
    print("🧪 Testing Datetime Serialization Fix")
    print("=" * 50)
    
    # Test data with datetime fields
    test_data = {
        "type": "event_match_end",
        "fixture_id": f"datetime_test_{int(time.time())}",
        "match_data": {
            "home_team": "Chelsea",
            "away_team": "Liverpool",
            "score": "2-1",
            "status": "finished",
            "match_date": datetime.utcnow().isoformat(),
            "events": [
                {
                    "type": "goal",
                    "team": "home",
                    "minute": 15,
                    "player": "Caicedo",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        },
        "timestamp": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    print(f"📡 Making API call to: {API_BASE_URL}/api/requests")
    print(f"🔑 Using secret key: {SECRET_KEY[:8]}...")
    print(f"📋 Fixture ID: {test_data['fixture_id']}")
    print(f"🏆 Teams: {test_data['match_data']['home_team']} vs {test_data['match_data']['away_team']}")
    print()
    
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
            print()
            
            if result.get('article_generation_status') == 'processing':
                print("🚀 Async processing started!")
                print("⏳ Waiting 15 seconds for processing...")
                time.sleep(15)
                
                # Check if processing completed without errors
                check_processing_status(result.get('request_id'))
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_processing_status(request_id):
    """Check if processing completed successfully"""
    
    print(f"\n🔍 Checking processing status for request: {request_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/requests/{request_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("📊 Request Status:")
            print(f"   📄 Request ID: {result.get('_id')}")
            print(f"   🏆 Fixture ID: {result.get('fixture_id')}")
            print(f"   ✅ Article Generated: {result.get('article_generated', False)}")
            print(f"   📝 Generated Article ID: {result.get('generated_article_id', 'N/A')}")
            print(f"   ❌ Generation Error: {result.get('generation_error', 'None')}")
            
            if result.get('article_generated'):
                print("✅ Article generation completed successfully!")
                
                # Check generated article
                check_generated_article(result.get('generated_article_id'))
            else:
                if result.get('generation_error'):
                    print(f"❌ Generation failed: {result.get('generation_error')}")
                else:
                    print("⏳ Generation still in progress...")
                    
        else:
            print(f"❌ Failed to get request status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking request status: {str(e)}")

def check_generated_article(article_id):
    """Check generated article details"""
    
    if not article_id:
        return
        
    print(f"\n📄 Checking generated article: {article_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/generated-articles/{article_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Generated article found!")
            print(f"   📝 Title: {result.get('title')}")
            print(f"   🏆 Team Names: {result.get('team_names', [])}")
            print(f"   📊 Source Requests: {result.get('source_requests_count')}")
            print(f"   ⏰ Generated At: {result.get('generated_at')}")
            
            # Check if team names were extracted
            team_names = result.get('team_names', [])
            if team_names:
                print(f"✅ Team names extracted successfully: {len(team_names)} variations")
            else:
                print("⚠️ No team names found")
                
        else:
            print(f"❌ Failed to get generated article: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking generated article: {str(e)}")

def test_multiple_datetime_scenarios():
    """Test multiple scenarios with datetime fields"""
    
    print("\n🧪 Testing Multiple Datetime Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Basic datetime fields",
            "data": {
                "type": "event_match_end",
                "fixture_id": f"datetime_basic_{int(time.time())}",
                "match_data": {
                    "home_team": "Arsenal",
                    "away_team": "Manchester City",
                    "match_date": datetime.utcnow().isoformat()
                },
                "created_at": datetime.utcnow().isoformat()
            }
        },
        {
            "name": "Nested datetime fields",
            "data": {
                "type": "event_match_end",
                "fixture_id": f"datetime_nested_{int(time.time())}",
                "match_data": {
                    "home_team": "Real Madrid",
                    "away_team": "Barcelona",
                    "events": [
                        {
                            "type": "goal",
                            "timestamp": datetime.utcnow().isoformat(),
                            "player": "Benzema"
                        }
                    ]
                }
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n📋 Test {i+1}: {scenario['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/requests",
                params={"secret_key": SECRET_KEY},
                json=scenario['data'],
                timeout=5
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Request sent - Status: {result.get('article_generation_status')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        time.sleep(1)
    
    print(f"\n⏳ Waiting 20 seconds for all processing...")
    time.sleep(20)
    
    # Check results
    print("\n🔍 Checking all results...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/generated-articles")
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            print(f"📊 Total generated articles: {len(articles)}")
            
            for scenario in scenarios:
                fixture_id = scenario['data']['fixture_id']
                matching = [a for a in articles if a.get('fixture_id') == fixture_id]
                
                if matching:
                    article = matching[0]
                    print(f"✅ {scenario['name']}: Article generated successfully")
                else:
                    print(f"⏳ {scenario['name']}: Still processing or failed")
                    
    except Exception as e:
        print(f"❌ Error checking results: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Datetime Serialization Fix Tests")
    print("=" * 50)
    
    # Test 1: Single request with datetime fields
    test_datetime_serialization_fix()
    
    # Test 2: Multiple scenarios
    test_multiple_datetime_scenarios()
    
    print("\n🏁 All tests completed!")
    print("=" * 50)
    print("📋 Check server logs for any remaining datetime serialization errors")
    print("🔍 Look for successful processing without 'Object of type datetime is not JSON serializable' errors")
