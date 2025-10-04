#!/usr/bin/env python3
"""
Test script để kiểm tra toàn bộ luồng Full Process
"""

import requests
import json
import time

def test_full_process():
    """Test toàn bộ luồng Full Process"""
    
    base_url = "http://localhost:5001"
    
    print("🔄 Testing Full Process Flow...")
    print("=" * 50)
    
    # Test video ID (thay đổi thành video ID thật)
    test_video_id = "507f1f77bcf86cd799439011"  # Thay đổi thành video ID thật
    
    print(f"🎬 Testing with video ID: {test_video_id}")
    
    # BƯỚC 1: Test Cleanup API
    print("\n🗑️ Step 1: Testing Cleanup API...")
    try:
        response = requests.post(
            f"{base_url}/api/cleanup-video-data",
            json={"video_id": test_video_id},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cleanup successful: {data.get('message', '')}")
            print(f"📊 Results: {json.dumps(data.get('results', {}), indent=2)}")
        else:
            print(f"❌ Cleanup failed: {response.text}")
    except Exception as e:
        print(f"❌ Cleanup error: {str(e)}")
    
    # BƯỚC 2: Test Crawl and Chunk API
    print("\n🎬 Step 2: Testing Crawl and Chunk API...")
    try:
        print("⏳ Starting crawl and chunk process (this may take a while)...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/api/crawl-and-chunk-video",
            json={"video_id": test_video_id},
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutes timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Status: {response.status_code}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Crawl and chunk successful!")
            print(f"📄 Message: {data.get('message', '')}")
            print(f"📊 Chunks count: {data.get('chunks_count', 0)}")
            print(f"📊 Video status: {data.get('video_status', 0)}")
            
            # Kiểm tra Elasticsearch result
            es_result = data.get('elasticsearch', {})
            if es_result:
                print(f"🤖 Elasticsearch result:")
                print(f"  - Success: {es_result.get('success', False)}")
                print(f"  - Indexed count: {es_result.get('indexed_count', 0)}")
                print(f"  - Message: {es_result.get('message', '')}")
            
        else:
            print(f"❌ Crawl and chunk failed: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timeout - process may still be running")
    except Exception as e:
        print(f"❌ Crawl and chunk error: {str(e)}")
    
    # BƯỚC 3: Test Search API
    print("\n🔍 Step 3: Testing Search API...")
    try:
        response = requests.get(f"{base_url}/api/search?q=test&size=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"📊 Results count: {len(data.get('results', []))}")
            print(f"📊 Total: {data.get('total', 0)}")
            print(f"⏱️ Took: {data.get('took', 0)}ms")
        else:
            print(f"❌ Search failed: {response.text}")
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
    
    # BƯỚC 4: Test Elasticsearch Stats
    print("\n📊 Step 4: Testing Elasticsearch Stats...")
    try:
        response = requests.get(f"{base_url}/api/elasticsearch/stats")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print(f"✅ Stats retrieved!")
            print(f"📊 Index name: {stats.get('index_name', 'N/A')}")
            print(f"📊 Document count: {stats.get('document_count', 0)}")
            print(f"📊 Index size: {stats.get('index_size', 0)} bytes")
            print(f"📊 Health: {stats.get('health', 'N/A')}")
        else:
            print(f"❌ Stats failed: {response.text}")
    except Exception as e:
        print(f"❌ Stats error: {str(e)}")
    
    print("\n✅ Full Process Test Complete!")

if __name__ == "__main__":
    test_full_process()
