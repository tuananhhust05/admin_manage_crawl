#!/usr/bin/env python3
"""
Debug script để kiểm tra tại sao Full Process không chạy vector hóa
"""

import os
import sys
import traceback

def debug_elasticsearch_service():
    """Debug Elasticsearch service"""
    
    print("🔍 Debugging Elasticsearch Service...")
    print("=" * 50)
    
    try:
        # Test 1: Import service
        print("1. Testing import...")
        from elasticsearch_service import elasticsearch_service
        print("✅ Import successful")
        
        # Test 2: Health check
        print("\n2. Testing health check...")
        health = elasticsearch_service.health_check()
        print(f"Health: {health}")
        
        if not health['overall']:
            print("❌ Service not healthy!")
            if not health['elasticsearch']:
                print("❌ Elasticsearch not available")
            if not health['sentence_transformer']:
                print("❌ Sentence transformer not available")
            return False
        
        # Test 3: Test model loading
        print("\n3. Testing model...")
        if elasticsearch_service.model:
            print("✅ Model loaded")
            print(f"Model type: {type(elasticsearch_service.model)}")
            
            # Test embedding generation
            test_text = "This is a test sentence for debugging."
            try:
                embedding = elasticsearch_service.model.encode([test_text])
                print(f"✅ Embedding generated: shape {embedding.shape}")
                print(f"✅ Vector dimensions: {embedding.shape[1]}")
            except Exception as e:
                print(f"❌ Embedding generation failed: {str(e)}")
                return False
        else:
            print("❌ Model not loaded")
            return False
        
        # Test 4: Test Elasticsearch connection
        print("\n4. Testing Elasticsearch connection...")
        if elasticsearch_service.es:
            try:
                info = elasticsearch_service.es.info()
                print(f"✅ Elasticsearch connected: {info.get('version', {}).get('number', 'unknown')}")
            except Exception as e:
                print(f"❌ Elasticsearch connection failed: {str(e)}")
                return False
        else:
            print("❌ Elasticsearch client not available")
            return False
        
        # Test 5: Test index creation
        print("\n5. Testing index creation...")
        try:
            elasticsearch_service._create_index()
            print("✅ Index creation test passed")
        except Exception as e:
            print(f"❌ Index creation failed: {str(e)}")
            return False
        
        # Test 6: Test sample indexing
        print("\n6. Testing sample indexing...")
        try:
            sample_chunks = [
                {
                    'chunk_id': 'debug_chunk_1',
                    'text': 'This is a debug test chunk for vector indexing.',
                    'start_time': 10.0,
                    'end_time': 15.0,
                    'duration': 5.0,
                    'chunk_index': 0
                }
            ]
            
            sample_video_info = {
                'video_id': 'debug_video_123',
                'title': 'Debug Test Video',
                'channel_name': 'Debug Channel',
                'url': 'https://youtube.com/watch?v=debug123',
                'channel_url': 'https://youtube.com/channel/debugchannel'
            }
            
            result = elasticsearch_service.index_chunks(sample_chunks, sample_video_info)
            print(f"✅ Sample indexing result: {result}")
            
            if result['success']:
                print(f"✅ Indexed {result['indexed_count']} chunks successfully")
                
                # Cleanup
                elasticsearch_service.delete_video_chunks('debug_video_123')
                print("✅ Cleanup completed")
            else:
                print(f"❌ Sample indexing failed: {result['message']}")
                return False
                
        except Exception as e:
            print(f"❌ Sample indexing error: {str(e)}")
            traceback.print_exc()
            return False
        
        print("\n✅ All tests passed! Elasticsearch service is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        traceback.print_exc()
        return False

def debug_api_endpoint():
    """Debug API endpoint"""
    
    print("\n🔍 Debugging API Endpoint...")
    print("=" * 50)
    
    try:
        # Test import routes
        print("1. Testing routes import...")
        from app.routes import main
        print("✅ Routes import successful")
        
        # Test import elasticsearch_service in routes
        print("\n2. Testing elasticsearch_service import in routes...")
        from app.routes import elasticsearch_service
        print("✅ Elasticsearch service import in routes successful")
        
        # Test service availability
        print("\n3. Testing service availability...")
        if elasticsearch_service:
            print("✅ Service available in routes")
        else:
            print("❌ Service not available in routes")
            return False
        
        print("\n✅ API endpoint debug completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ API endpoint debug failed: {str(e)}")
        traceback.print_exc()
        return False

def debug_environment():
    """Debug environment variables"""
    
    print("\n🔍 Debugging Environment...")
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
    print("🚀 Full Process Debug Suite")
    print("=" * 50)
    
    # Debug environment
    env_ok = debug_environment()
    
    # Debug Elasticsearch service
    es_ok = debug_elasticsearch_service()
    
    # Debug API endpoint
    api_ok = debug_api_endpoint()
    
    # Summary
    print("\n📋 Debug Summary:")
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
    else:
        print("\n⚠️ Some components have issues. Please fix them first.")
