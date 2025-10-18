#!/usr/bin/env python3
"""
Monitor script to check thread activity and logs
"""

import requests
import json
import time
from datetime import datetime

def monitor_api_logs():
    """Monitor API logs and thread activity"""
    
    print("🔍 Monitoring API Thread Activity")
    print("=" * 50)
    
    # Test data
    test_data = {
        "type": "event_match_end",
        "fixture_id": f"monitor_test_{int(time.time())}",
        "match_data": {
            "home_team": "Arsenal",
            "away_team": "Manchester City",
            "score": "1-0",
            "status": "finished"
        }
    }
    
    print(f"📡 Sending test request...")
    print(f"📋 Fixture ID: {test_data['fixture_id']}")
    print()
    
    try:
        # Send request
        response = requests.post(
            "http://localhost:5000/api/requests",
            params={"secret_key": "your_secret_key"},  # Replace with actual key
            json=test_data,
            timeout=5
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Request sent successfully!")
            print(f"📄 Request ID: {result.get('request_id')}")
            print(f"🔄 Generation Status: {result.get('article_generation_status')}")
            print()
            
            if result.get('article_generation_status') == 'processing':
                print("🚀 Thread started - monitoring progress...")
                print("⏰ Timeline:")
                print("  0s:  Request received, thread started")
                print("  0s:  Thread waiting 20 seconds...")
                print("  20s: Thread begins article generation")
                print("  25s: Article generation should complete")
                print()
                
                # Monitor progress
                for i in range(30):
                    print(f"⏳ {i}s: Monitoring...", end="\r")
                    time.sleep(1)
                    
                    # Check request status every 5 seconds
                    if i % 5 == 0 and i > 0:
                        check_request_progress(result.get('request_id'))
                
                print("\n🏁 Monitoring completed!")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_request_progress(request_id):
    """Check the progress of a request"""
    
    try:
        response = requests.get(f"http://localhost:5000/api/requests/{request_id}")
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('article_generation_status', 'unknown')
            generated = result.get('article_generated', False)
            
            if generated:
                print(f"\n✅ Article generation completed!")
                if result.get('generated_article_id'):
                    print(f"📄 Generated article ID: {result.get('generated_article_id')}")
            elif status == 'processing':
                print(f"\n⏳ Still processing...")
            else:
                print(f"\n⚠️ Status: {status}")
                
    except Exception as e:
        print(f"\n❌ Error checking progress: {str(e)}")

def check_thread_info():
    """Check thread information (if available)"""
    
    print("\n🧵 Thread Information")
    print("=" * 30)
    
    try:
        # This would require a custom endpoint to expose thread info
        # For now, just show what we expect to see in logs
        print("📋 Expected Thread Logs:")
        print("  🚀 Starting async article generation for fixture_id: ...")
        print("  📋 Thread ID: ...")
        print("  ⏰ Waiting 20 seconds before processing...")
        print("  ⏰ 20s delay completed, starting article generation...")
        print("  📄 Collected X articles for generation")
        print("  🤖 Generating article for fixture_id: ... with X sources")
        print("  ✅ Generated article saved with ID: ...")
        print("  ✅ Updated request ... with generated article info")
        print()
        print("🔍 Check your server logs for these messages!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_concurrent_requests():
    """Test multiple concurrent requests"""
    
    print("\n🧪 Testing Concurrent Requests")
    print("=" * 40)
    
    import threading
    import queue
    
    results = queue.Queue()
    
    def send_request(fixture_id, results_queue):
        """Send a single request"""
        try:
            test_data = {
                "type": "event_match_end",
                "fixture_id": fixture_id,
                "match_data": {"test": "concurrent"}
            }
            
            response = requests.post(
                "http://localhost:5000/api/requests",
                params={"secret_key": "your_secret_key"},  # Replace with actual key
                json=test_data,
                timeout=5
            )
            
            results_queue.put({
                'fixture_id': fixture_id,
                'status': response.status_code,
                'success': response.status_code == 201
            })
            
        except Exception as e:
            results_queue.put({
                'fixture_id': fixture_id,
                'error': str(e),
                'success': False
            })
    
    # Send 5 concurrent requests
    threads = []
    for i in range(5):
        fixture_id = f"concurrent_test_{int(time.time())}_{i}"
        thread = threading.Thread(
            target=send_request,
            args=(fixture_id, results)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Collect results
    print("📊 Concurrent Request Results:")
    while not results.empty():
        result = results.get()
        fixture_id = result['fixture_id']
        if result['success']:
            print(f"✅ {fixture_id}: Success")
        else:
            print(f"❌ {fixture_id}: Failed - {result.get('error', 'Unknown error')}")
    
    print("\n⏳ Waiting 30 seconds for all articles to be generated...")
    time.sleep(30)
    
    # Check generated articles
    try:
        response = requests.get("http://localhost:5000/api/generated-articles")
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            print(f"📊 Total generated articles: {len(articles)}")
        else:
            print(f"❌ Failed to get generated articles: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Thread Monitoring and Testing")
    print("=" * 50)
    
    # Test 1: Monitor single request
    monitor_api_logs()
    
    # Test 2: Check thread info
    check_thread_info()
    
    # Test 3: Concurrent requests
    test_concurrent_requests()
    
    print("\n🏁 All monitoring completed!")
    print("=" * 50)
    print("📋 Check your server logs for detailed thread information")
    print("🔍 Look for thread logs with emojis and timing information")
