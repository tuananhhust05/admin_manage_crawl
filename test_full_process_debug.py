#!/usr/bin/env python3
"""
Test script để debug Full Process không chạy vector hóa
"""

import os
import sys
import traceback

def test_elasticsearch_service():
    """Test Elasticsearch service"""
    
    print("🔍 Testing Elasticsearch Service...")
    print("=" * 50)
    
    try:
        # Test 1: Import service
        print("1. Testing import...")
        from elasticsearch_service import elasticsearch_service
        print("✅ Import successful")
        
        # Test 2: Check service status
        print("\n2. Checking service status...")
        print(f"ES client: {elasticsearch_service.es is not None}")
        print(f"Model: {elasticsearch_service.model is not None}")
        
        # Test 3: Health check
        print("\n3. Testing health check...")
        health = elasticsearch_service.health_check()
        print(f"Health: {health}")
        
        if not health['overall']:
            print("❌ Service not healthy!")
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
                'text': 'This is a test chunk for debugging the full process.',
                'start_time': 10.0,
                'end_time': 15.0,
                'duration': 5.0,
                'chunk_index': 0
            }
        ]
        
        sample_video_info = {
            'video_id': 'test_video_debug',
            'title': 'Debug Test Video',
            'channel_name': 'Debug Channel',
            'url': 'https://youtube.com/watch?v=debug123',
            'channel_url': 'https://youtube.com/channel/debugchannel'
        }
        
        result = elasticsearch_service.index_chunks(sample_chunks, sample_video_info)
        print(f"Indexing result: {result}")
        
        if result['success']:
            print(f"✅ Successfully indexed {result['indexed_count']} chunks")
            
            # Cleanup
            elasticsearch_service.delete_video_chunks('test_video_debug')
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

def test_api_endpoint():
    """Test API endpoint"""
    
    print("\n🔍 Testing API Endpoint...")
    print("=" * 50)
    
    try:
        # Test 1: Import routes
        print("1. Testing routes import...")
        from app.routes import main
        print("✅ Routes import successful")
        
        # Test 2: Import elasticsearch_service in routes
        print("\n2. Testing elasticsearch_service import in routes...")
        from app.routes import elasticsearch_service
        print("✅ Elasticsearch service import in routes successful")
        
        # Test 3: Check service availability
        print("\n3. Testing service availability...")
        if elasticsearch_service:
            print("✅ Service available in routes")
            
            # Test health check
            health = elasticsearch_service.health_check()
            print(f"Health in routes: {health}")
        else:
            print("❌ Service not available in routes")
            return False
        
        print("\n✅ API endpoint test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    
    print("\n🔍 Testing Environment...")
    print("=" * 50)
    
    # Check environment variables
    env_vars = [
        'ELASTICSEARCH_HOST',
        'ELASTICSEARCH_PORT', 
        'ELASTICSEARCH_INDEX',
        'SENTENCE_TRANSFORMER_MODEL'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'NOT_SET')
        print(f"{var}: {value}")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("\n✅ .env file exists")
    else:
        print("\n⚠️ .env file not found")
    
    return True

if __name__ == "__main__":
    print("🚀 Full Process Debug Test Suite")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment()
    
    # Test Elasticsearch service
    es_ok = test_elasticsearch_service()
    
    # Test API endpoint
    api_ok = test_api_endpoint()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 20)
    print(f"Environment: {'✅ OK' if env_ok else '❌ FAIL'}")
    print(f"Elasticsearch Service: {'✅ OK' if es_ok else '❌ FAIL'}")
    print(f"API Endpoint: {'✅ OK' if api_ok else '❌ FAIL'}")
    
    if env_ok and es_ok and api_ok:
        print("\n🎉 All components are working! The issue might be elsewhere.")
        print("\n💡 Suggestions:")
        print("1. Check browser console for JavaScript errors")
        print("2. Check server logs for backend errors")
        print("3. Verify video_id is valid")
        print("4. Check network requests in browser dev tools")
        print("5. Try running the debug script while the app is running")
    else:
        print("\n⚠️ Some components have issues. Please fix them first.")
        
        if not es_ok:
            print("\n💡 Elasticsearch service suggestions:")
            print("1. Check if Elasticsearch is running")
            print("2. Check if model can be loaded")
            print("3. Check environment variables")
            print("4. Check internet connection for model download")
