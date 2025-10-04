#!/usr/bin/env python3
"""
Test script để kiểm tra việc load model all-distilroberta-v1
"""

import os
import sys
import traceback

def test_model_loading():
    """Test loading the model"""
    
    print("🤖 Testing Model Loading: all-distilroberta-v1")
    print("=" * 50)
    
    try:
        # Test 1: Import sentence transformers
        print("1. Testing sentence-transformers import...")
        from sentence_transformers import SentenceTransformer
        print("✅ Import successful")
        
        # Test 2: Load model
        print("\n2. Loading all-distilroberta-v1 model...")
        model = SentenceTransformer('all-distilroberta-v1')
        print("✅ Model loaded successfully!")
        
        # Test 3: Test encoding
        print("\n3. Testing encoding...")
        test_texts = [
            "This is a test sentence for debugging.",
            "Machine learning and artificial intelligence are fascinating topics."
        ]
        
        embeddings = model.encode(test_texts)
        print(f"✅ Embeddings generated: shape {embeddings.shape}")
        print(f"✅ Vector dimensions: {embeddings.shape[1]}")
        
        # Test 4: Test similarity
        print("\n4. Testing similarity...")
        import numpy as np
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        print(f"✅ Cosine similarity: {similarity:.4f}")
        
        print("\n✅ Model loading test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {str(e)}")
        traceback.print_exc()
        return False

def test_elasticsearch_service_init():
    """Test Elasticsearch service initialization"""
    
    print("\n🔍 Testing Elasticsearch Service Initialization...")
    print("=" * 50)
    
    try:
        # Test 1: Import service
        print("1. Testing service import...")
        from elasticsearch_service import elasticsearch_service
        print("✅ Service import successful")
        
        # Test 2: Check if model is loaded
        print("\n2. Checking model status...")
        if elasticsearch_service.model:
            print("✅ Model is loaded")
            print(f"Model type: {type(elasticsearch_service.model)}")
        else:
            print("❌ Model is not loaded")
            return False
        
        # Test 3: Check Elasticsearch connection
        print("\n3. Checking Elasticsearch connection...")
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
        
        # Test 4: Health check
        print("\n4. Testing health check...")
        health = elasticsearch_service.health_check()
        print(f"Health status: {health}")
        
        if health['overall']:
            print("✅ Service is healthy")
        else:
            print("❌ Service is not healthy")
            if not health['elasticsearch']:
                print("❌ Elasticsearch not available")
            if not health['sentence_transformer']:
                print("❌ Sentence transformer not available")
            return False
        
        print("\n✅ Elasticsearch service initialization test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Model Loading Test Suite")
    print("=" * 50)
    
    # Test model loading
    model_ok = test_model_loading()
    
    # Test service initialization
    service_ok = test_elasticsearch_service_init()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 20)
    print(f"Model Loading: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"Service Init: {'✅ PASS' if service_ok else 'OK' if model_ok else '❌ FAIL'}")
    
    if model_ok and service_ok:
        print("\n🎉 All tests passed! Model and service are working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        
        if not model_ok:
            print("\n💡 Model loading suggestions:")
            print("1. Check internet connection (model needs to be downloaded)")
            print("2. Check disk space (model is ~400MB)")
            print("3. Try: pip install --upgrade sentence-transformers")
            print("4. Check if model name is correct: all-distilroberta-v1")
