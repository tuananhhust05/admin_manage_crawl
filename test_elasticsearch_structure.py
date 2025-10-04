#!/usr/bin/env python3
"""
Test script để kiểm tra cấu trúc dữ liệu Elasticsearch
"""

import json
from elasticsearch_service import elasticsearch_service

def test_elasticsearch_structure():
    """Test cấu trúc dữ liệu Elasticsearch"""
    
    print("🔍 Testing Elasticsearch Structure...")
    
    # 1. Kiểm tra health
    health = elasticsearch_service.health_check()
    print(f"Health Check: {health}")
    
    if not health['overall']:
        print("❌ Elasticsearch hoặc model không sẵn sàng")
        return
    
    # 2. Kiểm tra index stats
    stats = elasticsearch_service.get_index_stats()
    print(f"Index Stats: {json.dumps(stats, indent=2)}")
    
    # 3. Test search với sample data
    print("\n🔍 Testing search functionality...")
    
    # Sample search query
    search_result = elasticsearch_service.search_chunks(
        query="test video content",
        size=5
    )
    
    if search_result['success']:
        print(f"✅ Search successful: {len(search_result['results'])} results")
        
        # Hiển thị cấu trúc của result đầu tiên
        if search_result['results']:
            first_result = search_result['results'][0]
            print("\n📋 Sample result structure:")
            print(json.dumps(first_result, indent=2, ensure_ascii=False))
            
            # Kiểm tra các field chính
            required_fields = ['url_channel', 'url', 'origin_content', 'time', 'vector']
            print(f"\n🔍 Checking required fields:")
            for field in required_fields:
                if field in first_result:
                    print(f"  ✅ {field}: {type(first_result[field])}")
                else:
                    print(f"  ❌ {field}: Missing")
    else:
        print(f"❌ Search failed: {search_result['message']}")
    
    # 4. Test index mapping
    print("\n📋 Testing index mapping...")
    try:
        mapping = elasticsearch_service.es.indices.get_mapping(index=elasticsearch_service.index_name)
        print("✅ Index mapping retrieved successfully")
        
        # Hiển thị mapping structure
        properties = mapping[elasticsearch_service.index_name]['mappings']['properties']
        print("\n📋 Index Properties:")
        for field, config in properties.items():
            print(f"  {field}: {config.get('type', 'unknown')}")
            
    except Exception as e:
        print(f"❌ Failed to get mapping: {str(e)}")

def test_sample_data():
    """Test với sample data"""
    print("\n🧪 Testing with sample data...")
    
    # Sample chunks data
    sample_chunks = [
        {
            'chunk_id': 'test_chunk_1',
            'text': 'This is a test video about machine learning and artificial intelligence.',
            'start_time': 10.5,
            'end_time': 15.2,
            'duration': 4.7,
            'chunk_index': 0
        },
        {
            'chunk_id': 'test_chunk_2', 
            'text': 'In this section, we will discuss neural networks and deep learning concepts.',
            'start_time': 15.2,
            'end_time': 20.8,
            'duration': 5.6,
            'chunk_index': 1
        }
    ]
    
    # Sample video info
    sample_video_info = {
        'video_id': 'test_video_123',
        'title': 'Machine Learning Tutorial',
        'channel_name': 'Tech Channel',
        'url': 'https://youtube.com/watch?v=test123',
        'channel_url': 'https://youtube.com/channel/testchannel'
    }
    
    print(f"🤖 Using model: all-distilroberta-v1 (768D vectors)")
    
    # Test indexing
    print("🔄 Testing indexing...")
    index_result = elasticsearch_service.index_chunks(sample_chunks, sample_video_info)
    
    if index_result['success']:
        print(f"✅ Indexing successful: {index_result['indexed_count']} chunks indexed")
        
        # Test search với data vừa index
        print("🔍 Testing search with indexed data...")
        search_result = elasticsearch_service.search_chunks(
            query="machine learning neural networks",
            size=5
        )
        
        if search_result['success']:
            print(f"✅ Search successful: {len(search_result['results'])} results")
            
            # Hiển thị kết quả
            for i, result in enumerate(search_result['results']):
                print(f"\n📄 Result {i+1}:")
                print(f"  URL Channel: {result.get('url_channel', 'N/A')}")
                print(f"  URL Video: {result.get('url', 'N/A')}")
                print(f"  Content: {result.get('origin_content', 'N/A')[:100]}...")
                print(f"  Time: {result.get('time', 'N/A')}")
                print(f"  Score: {result.get('score', 'N/A')}")
        else:
            print(f"❌ Search failed: {search_result['message']}")
            
        # Cleanup - xóa test data
        print("\n🧹 Cleaning up test data...")
        delete_result = elasticsearch_service.delete_video_chunks('test_video_123')
        if delete_result['success']:
            print(f"✅ Cleanup successful: {delete_result.get('deleted_count', 0)} chunks deleted")
        else:
            print(f"⚠️ Cleanup failed: {delete_result['message']}")
            
    else:
        print(f"❌ Indexing failed: {index_result['message']}")

if __name__ == "__main__":
    print("🚀 Elasticsearch Structure Test")
    print("=" * 50)
    
    try:
        test_elasticsearch_structure()
        test_sample_data()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
