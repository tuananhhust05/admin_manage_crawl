#!/usr/bin/env python3
"""
Test script để test trực tiếp model loading
"""

import os
import sys
import traceback

def test_model_direct():
    """Test model loading trực tiếp"""
    
    print("🤖 Testing Model Loading Directly...")
    print("=" * 50)
    
    try:
        # Test 1: Import sentence transformers
        print("1. Testing sentence-transformers import...")
        from sentence_transformers import SentenceTransformer
        print("✅ Import successful")
        
        # Test 2: Load model
        print("\n2. Loading all-distilroberta-v1 model...")
        print("⏳ This may take a few minutes on first run...")
        
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
        
        # Test 5: Test with Vietnamese text
        print("\n5. Testing with Vietnamese text...")
        vietnamese_texts = [
            "Học máy và trí tuệ nhân tạo là những chủ đề thú vị.",
            "Xử lý ngôn ngữ tự nhiên và tìm kiếm ngữ nghĩa rất quan trọng."
        ]
        
        vietnamese_embeddings = model.encode(vietnamese_texts)
        print(f"✅ Vietnamese embeddings generated: shape {vietnamese_embeddings.shape}")
        
        vietnamese_similarity = np.dot(vietnamese_embeddings[0], vietnamese_embeddings[1]) / (
            np.linalg.norm(vietnamese_embeddings[0]) * np.linalg.norm(vietnamese_embeddings[1])
        )
        print(f"✅ Vietnamese similarity: {vietnamese_similarity:.4f}")
        
        print("\n✅ Model loading test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Model Direct Test Suite")
    print("=" * 50)
    
    # Test model loading
    model_ok = test_model_direct()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 20)
    print(f"Model Loading: {'✅ PASS' if model_ok else '❌ FAIL'}")
    
    if model_ok:
        print("\n🎉 Model is working correctly!")
    else:
        print("\n⚠️ Model has issues. Please check the errors above.")
        
        print("\n💡 Model loading suggestions:")
        print("1. Check internet connection (model needs to be downloaded)")
        print("2. Check disk space (model is ~400MB)")
        print("3. Try: pip install --upgrade sentence-transformers")
        print("4. Check if model name is correct: all-distilroberta-v1")
        print("5. Try: pip install torch torchvision torchaudio")
