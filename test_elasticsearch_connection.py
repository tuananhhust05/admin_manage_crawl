#!/usr/bin/env python3
"""
Test script để kiểm tra kết nối đến Elasticsearch của bạn
"""

import os
import sys
import traceback
import requests
from elasticsearch import Elasticsearch

def test_elasticsearch_connection():
    """Test kết nối đến Elasticsearch"""
    
    print("🔍 Testing Elasticsearch Connection...")
    print("=" * 50)
    
    try:
        # Test 1: Test HTTP connection
        print("1. Testing HTTP connection...")
        url = "http://37.27.181.54:9200/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ HTTP connection successful!")
            print(f"Cluster: {data.get('cluster_name', 'unknown')}")
            print(f"Version: {data.get('version', {}).get('number', 'unknown')}")
        else:
            print(f"❌ HTTP connection failed: {response.status_code}")
            return False
        
        # Test 2: Test Elasticsearch client
        print("\n2. Testing Elasticsearch client...")
        es = Elasticsearch([{'host': '37.27.181.54', 'port': 9200}])
        
        if es.ping():
            print("✅ Elasticsearch client connection successful!")
        else:
            print("❌ Elasticsearch client connection failed!")
            return False
        
        # Test 3: Test index operations
        print("\n3. Testing index operations...")
        test_index = "test_connection"
        
        # Create test index
        if es.indices.exists(index=test_index):
            es.indices.delete(index=test_index)
            print("✅ Deleted existing test index")
        
        # Create new test index
        es.indices.create(index=test_index)
        print("✅ Created test index")
        
        # Test document indexing
        test_doc = {
            "test_field": "test_value",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        es.index(index=test_index, body=test_doc)
        print("✅ Indexed test document")
        
        # Test document search
        search_result = es.search(index=test_index, body={"query": {"match_all": {}}})
        print(f"✅ Search test: {search_result['hits']['total']['value']} documents found")
        
        # Cleanup
        es.indices.delete(index=test_index)
        print("✅ Cleaned up test index")
        
        # Test 4: Test articles index
        print("\n4. Testing articles index...")
        if es.indices.exists(index="articles"):
            print("✅ Articles index exists")
            
            # Get index stats
            stats = es.indices.stats(index="articles")
            doc_count = stats['indices']['articles']['total']['docs']['count']
            print(f"✅ Articles index has {doc_count} documents")
        else:
            print("⚠️ Articles index does not exist")
        
        print("\n✅ All Elasticsearch tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Elasticsearch test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_elasticsearch_service():
    """Test Elasticsearch service với cấu hình mới"""
    
    print("\n🔍 Testing Elasticsearch Service...")
    print("=" * 50)
    
    try:
        # Test 1: Import service
        print("1. Testing service import...")
        from elasticsearch_service import elasticsearch_service
        print("✅ Service import successful")
        
        # Test 2: Check configuration
        print("\n2. Checking configuration...")
        print(f"Host: {elasticsearch_service.es_host}")
        print(f"Port: {elasticsearch_service.es_port}")
        print(f"Index: {elasticsearch_service.index_name}")
        
        # Test 3: Health check
        print("\n3. Testing health check...")
        health = elasticsearch_service.health_check()
        print(f"Health: {health}")
        
        if health['overall']:
            print("✅ Service is healthy!")
        else:
            print("❌ Service is not healthy!")
            if not health['elasticsearch']:
                print("❌ Elasticsearch not available")
            if not health['sentence_transformer']:
                print("❌ Sentence transformer not available")
            return False
        
        # Test 4: Test sample indexing
        print("\n4. Testing sample indexing...")
        sample_chunks = [
            {
                'chunk_id': 'test_chunk_1',
                'text': 'This is a test chunk for debugging the connection.',
                'start_time': 10.0,
                'end_time': 15.0,
                'duration': 5.0,
                'chunk_index': 0
            }
        ]
        
        sample_video_info = {
            'video_id': 'test_video_connection',
            'title': 'Test Connection Video',
            'channel_name': 'Test Channel',
            'url': 'https://youtube.com/watch?v=test123',
            'channel_url': 'https://youtube.com/channel/testchannel'
        }
        
        result = elasticsearch_service.index_chunks(sample_chunks, sample_video_info)
        print(f"Indexing result: {result}")
        
        if result['success']:
            print(f"✅ Successfully indexed {result['indexed_count']} chunks")
            
            # Cleanup
            elasticsearch_service.delete_video_chunks('test_video_connection')
            print("✅ Cleanup completed")
        else:
            print(f"❌ Indexing failed: {result['message']}")
            return False
        
        print("\n✅ Elasticsearch service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Elasticsearch service test failed: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Elasticsearch Connection Test Suite")
    print("=" * 50)
    
    # Test direct connection
    connection_ok = test_elasticsearch_connection()
    
    # Test service
    service_ok = test_elasticsearch_service()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 20)
    print(f"Direct Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    
    if connection_ok and service_ok:
        print("\n🎉 All tests passed! Elasticsearch is working correctly!")
        print("\n💡 Now you can:")
        print("1. Restart your app: python app.py")
        print("2. Try the Full Process button again")
        print("3. Check the logs for successful vector indexing")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
