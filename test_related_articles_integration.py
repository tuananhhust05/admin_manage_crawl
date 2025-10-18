#!/usr/bin/env python3
"""
Test script for related articles integration feature
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
SECRET_KEY = "your_secret_key_here"  # Replace with your actual secret key

def test_related_articles_integration():
    """Test related articles integration with match analysis"""
    
    print("🧪 Testing Related Articles Integration")
    print("=" * 50)
    
    # Test data với thông tin đội bóng rõ ràng
    test_data = {
        "type": "event_match_end",
        "fixture_id": f"related_articles_test_{int(time.time())}",
        "match_data": {
            "home_team": "Brentford",
            "away_team": "Manchester United",
            "score": "2-1",
            "status": "finished",
            "competition": "Premier League",
            "venue": "Brentford Community Stadium",
            "events": [
                {"type": "goal", "team": "home", "minute": 8, "player": "Igor Thiago", "description": "Brentford goal by Igor Thiago"},
                {"type": "substitution", "team": "away", "minute": 66, "player_in": "Kobbie Mainoo", "player_out": "Harry Maguire"},
                {"type": "card", "team": "away", "minute": 55, "player": "Bruno Fernandes", "card_type": "yellow"}
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
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
                print("⏳ Waiting 20 seconds for related articles query and analysis generation...")
                time.sleep(20)
                
                # Check generated articles
                check_generated_analysis_article(test_data['fixture_id'])
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_generated_analysis_article(fixture_id):
    """Check if analysis article was generated with related articles"""
    
    print(f"\n🔍 Checking generated analysis article for fixture: {fixture_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/generated-articles")
        
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            
            # Find article for our fixture
            matching_articles = [a for a in articles if a.get('fixture_id') == fixture_id]
            
            if matching_articles:
                article = matching_articles[0]
                print("✅ Analysis article generated successfully!")
                print(f"📄 Article ID: {article.get('_id')}")
                print(f"📝 Title: {article.get('title')}")
                print(f"📊 Source Requests: {article.get('source_requests_count')}")
                print(f"📰 Related Articles: {article.get('related_articles_count', 0)}")
                print(f"⏰ Generated At: {article.get('generated_at')}")
                print()
                
                # Check team names
                team_names = article.get('team_names', [])
                if team_names:
                    print("🏆 Team Names Extracted:")
                    print(f"   📋 Teams: {team_names}")
                
                # Check related articles
                related_articles_count = article.get('related_articles_count', 0)
                related_articles_ids = article.get('related_articles_ids', [])
                
                if related_articles_count > 0:
                    print(f"📰 Related Articles Found: {related_articles_count}")
                    print(f"📄 Related Article IDs: {related_articles_ids[:5]}...")  # Show first 5 IDs
                    print("✅ Related articles integration working!")
                else:
                    print("⚠️ No related articles found")
                    print("🔍 This might indicate:")
                    print("   - No articles in the last 48h containing team names")
                    print("   - Team names not matching any article content")
                    print("   - Database query issue")
                
                print("\n📖 Analysis Article Content Preview:")
                content = article.get('content', '')
                print(content[:500] + "..." if len(content) > 500 else content)
                
            else:
                print("⏳ No article found yet - may still be processing")
                
        else:
            print(f"❌ Failed to get generated articles: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking generated articles: {str(e)}")

def test_with_different_teams():
    """Test with different team combinations"""
    
    print("\n🧪 Testing with Different Team Combinations")
    print("=" * 50)
    
    test_scenarios = [
        {
            "name": "Popular Premier League Teams",
            "data": {
                "type": "event_match_end",
                "fixture_id": f"popular_teams_{int(time.time())}",
                "match_data": {
                    "home_team": "Chelsea",
                    "away_team": "Liverpool",
                    "score": "1-0",
                    "competition": "Premier League"
                }
            }
        },
        {
            "name": "La Liga Giants",
            "data": {
                "type": "event_match_end",
                "fixture_id": f"laliga_giants_{int(time.time())}",
                "match_data": {
                    "home_team": "Real Madrid",
                    "away_team": "Barcelona",
                    "score": "2-1",
                    "competition": "La Liga"
                }
            }
        },
        {
            "name": "Champions League Teams",
            "data": {
                "type": "event_match_end",
                "fixture_id": f"champions_league_{int(time.time())}",
                "match_data": {
                    "home_team": "Bayern Munich",
                    "away_team": "PSG",
                    "score": "3-2",
                    "competition": "Champions League"
                }
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📋 Test {i+1}: {scenario['name']}")
        print(f"🏆 Teams: {scenario['data']['match_data']['home_team']} vs {scenario['data']['match_data']['away_team']}")
        
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
    
    print(f"\n⏳ Waiting 25 seconds for all analysis articles to be generated...")
    time.sleep(25)
    
    # Check all generated articles
    print("\n🔍 Checking all generated analysis articles...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/generated-articles")
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            
            print(f"📊 Total generated articles: {len(articles)}")
            
            for scenario in test_scenarios:
                fixture_id = scenario['data']['fixture_id']
                matching = [a for a in articles if a.get('fixture_id') == fixture_id]
                
                if matching:
                    article = matching[0]
                    related_count = article.get('related_articles_count', 0)
                    team_names = article.get('team_names', [])
                    
                    print(f"✅ {scenario['name']}:")
                    print(f"   📰 Related articles: {related_count}")
                    print(f"   🏆 Team names: {len(team_names)} variations")
                    if related_count > 0:
                        print(f"   🎉 Related articles integration successful!")
                    else:
                        print(f"   ⚠️ No related articles found")
                else:
                    print(f"⏳ {scenario['name']}: Still processing or failed")
                    
    except Exception as e:
        print(f"❌ Error checking articles: {str(e)}")

def check_articles_database():
    """Check what articles are available in the database"""
    
    print("\n🔍 Checking Articles Database")
    print("=" * 30)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/articles")
        
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            
            print(f"📊 Total articles in database: {len(articles)}")
            
            if articles:
                print("📰 Recent articles:")
                for i, article in enumerate(articles[:5]):
                    content_preview = article.get('content', '')[:100] + "..." if len(article.get('content', '')) > 100 else article.get('content', '')
                    source = article.get('source', 'unknown')
                    created_at = article.get('created_at', 'unknown')
                    print(f"   {i+1}. Source: {source}, Date: {created_at}")
                    print(f"      Content: {content_preview}")
                    print()
            else:
                print("⚠️ No articles found in database")
                print("💡 You may need to add some articles first for the related articles feature to work")
                
        else:
            print(f"❌ Failed to get articles: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking articles database: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Related Articles Integration Tests")
    print("=" * 50)
    
    # Check articles database first
    check_articles_database()
    
    # Test 1: Single request with related articles
    test_related_articles_integration()
    
    # Test 2: Multiple scenarios
    test_with_different_teams()
    
    print("\n🏁 All tests completed!")
    print("=" * 50)
    print("📋 Check server logs for related articles query information")
    print("🔍 Look for logs with emojis: 📰, 🔍, 📅, 🔄, ✅, ❌")
    print("📄 Expected flow:")
    print("   1. Extract team names from match data")
    print("   2. Query articles containing team names (last 48h)")
    print("   3. Combine match data + related articles")
    print("   4. Generate analysis article with all sources")
