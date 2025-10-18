#!/usr/bin/env python3
"""
Test script to verify team names extraction fix
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
SECRET_KEY = "your_secret_key_here"  # Replace with your actual secret key

def test_team_names_extraction_fix():
    """Test team names extraction with fixed model"""
    
    print("🧪 Testing Team Names Extraction Fix")
    print("=" * 50)
    
    # Test data với thông tin đội bóng rõ ràng
    test_data = {
        "type": "event_match_end",
        "fixture_id": f"team_fix_test_{int(time.time())}",
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
                print("⏳ Waiting 15 seconds for team names extraction and article generation...")
                time.sleep(15)
                
                # Check generated articles
                check_generated_article_with_teams(test_data['fixture_id'])
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_generated_article_with_teams(fixture_id):
    """Check if article was generated with team names"""
    
    print(f"\n🔍 Checking generated article for fixture: {fixture_id}")
    
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
                
                # Check team names
                team_names = article.get('team_names', [])
                team_names_raw = article.get('team_names_raw', '')
                
                if team_names:
                    print("🏆 Team Names Extracted Successfully:")
                    print(f"   📋 Parsed: {team_names}")
                    print(f"   📄 Raw: {team_names_raw}")
                    print()
                    
                    # Validate team names
                    expected_teams = ['Brentford', 'Manchester United']
                    found_teams = []
                    
                    for team in expected_teams:
                        if any(team.lower() in name.lower() for name in team_names):
                            found_teams.append(team)
                    
                    print(f"✅ Validation: Found {len(found_teams)}/2 expected teams: {found_teams}")
                    
                    if len(found_teams) == 2:
                        print("🎉 Perfect! Both teams identified correctly!")
                    elif len(found_teams) == 1:
                        print("⚠️ Partial success - only one team identified")
                    else:
                        print("❌ No expected teams found in extracted names")
                    
                else:
                    print("⚠️ No team names found in generated article")
                    print("🔍 This might indicate the team names extraction failed")
                
                print("\n📖 Article Content Preview:")
                content = article.get('content', '')
                print(content[:300] + "..." if len(content) > 300 else content)
                
            else:
                print("⏳ No article found yet - may still be processing")
                
        else:
            print(f"❌ Failed to get generated articles: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking generated articles: {str(e)}")

def test_different_team_scenarios():
    """Test different team name scenarios"""
    
    print("\n🧪 Testing Different Team Name Scenarios")
    print("=" * 50)
    
    test_scenarios = [
        {
            "name": "Premier League Teams",
            "data": {
                "type": "event_match_end",
                "fixture_id": f"prem_teams_{int(time.time())}",
                "match_data": {
                    "home_team": "Chelsea",
                    "away_team": "Liverpool",
                    "score": "2-1",
                    "competition": "Premier League"
                }
            }
        },
        {
            "name": "La Liga Teams",
            "data": {
                "type": "event_match_end",
                "fixture_id": f"laliga_teams_{int(time.time())}",
                "match_data": {
                    "home_team": "Real Madrid",
                    "away_team": "Barcelona",
                    "score": "1-0",
                    "competition": "La Liga"
                }
            }
        },
        {
            "name": "Teams with Abbreviations",
            "data": {
                "type": "event_match_end",
                "fixture_id": f"abbrev_teams_{int(time.time())}",
                "match_data": {
                    "home_team": "PSG",
                    "away_team": "Bayern Munich",
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
        
        time.sleep(1)  # Small delay between requests
    
    print(f"\n⏳ Waiting 20 seconds for all articles to be generated...")
    time.sleep(20)
    
    # Check all generated articles
    print("\n🔍 Checking all generated articles...")
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
                    team_names = article.get('team_names', [])
                    if team_names:
                        print(f"✅ {scenario['name']}: {len(team_names)} team names - {team_names}")
                    else:
                        print(f"⚠️ {scenario['name']}: Article generated but no team names")
                else:
                    print(f"⏳ {scenario['name']}: Still processing or failed")
                    
    except Exception as e:
        print(f"❌ Error checking articles: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Team Names Extraction Fix Tests")
    print("=" * 50)
    
    # Test 1: Single request with team names
    test_team_names_extraction_fix()
    
    # Test 2: Multiple scenarios
    test_different_team_scenarios()
    
    print("\n🏁 All tests completed!")
    print("=" * 50)
    print("📋 Check server logs for team names extraction information")
    print("🔍 Look for logs with emojis: 🏆, 🔍, ✅, ❌")
    print("📄 Expected team names format: Brentford, BRE, Bees, Manchester United, MAN, Red Devils")
    print("🔧 Model changed from 'llama-3.1-70b-versatile' to 'llama-3.1-8b-instant'")
