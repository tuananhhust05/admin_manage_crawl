#!/usr/bin/env python3
"""
Test script để kiểm tra việc thay đổi model từ all-MiniLM-L6-v2 sang all-distilroberta-v1
"""

import os
import sys
from sentence_transformers import SentenceTransformer
import numpy as np

def test_model_change():
    """Test việc thay đổi model"""
    
    print("🤖 Testing Model Change: all-MiniLM-L6-v2 → all-distilroberta-v1")
    print("=" * 60)
    
    # Test 1: Load model mới
    print("\n1. 🔄 Loading all-distilroberta-v1 model...")
    try:
        model = SentenceTransformer('all-distilroberta-v1')
        print("✅ Model loaded successfully!")
        
        # Test 2: Kiểm tra vector dimensions
        print("\n2. 📏 Testing vector dimensions...")
        test_texts = [
            "This is a test sentence about machine learning.",
            "Artificial intelligence and neural networks are fascinating topics.",
            "Deep learning models can process natural language effectively."
        ]
        
        embeddings = model.encode(test_texts)
        print(f"✅ Generated embeddings shape: {embeddings.shape}")
        print(f"📊 Vector dimensions: {embeddings.shape[1]}")
        
        if embeddings.shape[1] == 768:
            print("✅ Correct dimensions: 768D (all-distilroberta-v1)")
        else:
            print(f"❌ Wrong dimensions: {embeddings.shape[1]}D (expected 768D)")
        
        # Test 3: Kiểm tra similarity
        print("\n3. 🔍 Testing similarity calculation...")
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        print(f"✅ Cosine similarity between first two texts: {similarity:.4f}")
        
        # Test 4: Performance test
        print("\n4. ⚡ Performance test...")
        import time
        
        start_time = time.time()
        large_texts = [f"This is test sentence number {i} for performance testing." for i in range(100)]
        large_embeddings = model.encode(large_texts)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"✅ Processed 100 texts in {duration:.2f} seconds")
        print(f"📊 Speed: {100/duration:.1f} texts/second")
        print(f"📊 Embeddings shape: {large_embeddings.shape}")
        
        # Test 5: Memory usage
        print("\n5. 💾 Memory usage...")
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"✅ Memory usage: {memory_mb:.1f} MB")
        
        print("\n✅ Model change test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing model: {str(e)}")
        return False

def test_elasticsearch_compatibility():
    """Test compatibility với Elasticsearch"""
    
    print("\n🔍 Testing Elasticsearch Compatibility...")
    print("=" * 40)
    
    try:
        from elasticsearch_service import elasticsearch_service
        
        # Test health check
        health = elasticsearch_service.health_check()
        print(f"✅ Elasticsearch health: {health}")
        
        if health['overall']:
            # Test index stats
            stats = elasticsearch_service.get_index_stats()
            print(f"✅ Index stats: {stats}")
            
            # Test search với model mới
            search_result = elasticsearch_service.search_chunks(
                query="machine learning artificial intelligence",
                size=3
            )
            print(f"✅ Search test: {search_result['success']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Elasticsearch compatibility error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Model Change Test Suite")
    print("=" * 50)
    
    # Test model change
    model_success = test_model_change()
    
    # Test Elasticsearch compatibility
    es_success = test_elasticsearch_compatibility()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 20)
    print(f"Model Change: {'✅ PASS' if model_success else '❌ FAIL'}")
    print(f"Elasticsearch: {'✅ PASS' if es_success else '❌ FAIL'}")
    
    if model_success and es_success:
        print("\n🎉 All tests passed! Model change successful!")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
