#!/usr/bin/env python3
"""
Test script để demo cách sử dụng API /api/requests với secret key
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
SECRET_KEY = "your-secret-key-here"  # Thay bằng secret key thực tế

def test_api_with_secret_key():
    """Test API với secret key qua URL parameter"""
    
    url = f"{API_BASE_URL}/api/requests"
    
    # Test data
    test_data = {
        "type": "test_event",
        "fixture_id": "12345",
        "message": "Test message with secret key",
        "timestamp": datetime.now().isoformat()
    }
    
    # Method 1: Secret key qua URL parameter
    print("🔐 Testing API with secret key via URL parameter...")
    params = {"secret_key": SECRET_KEY}
    
    try:
        response = requests.post(url, json=test_data, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Success: API call with secret key worked!")
        else:
            print("❌ Failed: API call failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")

def test_api_with_header():
    """Test API với secret key qua header"""
    
    url = f"{API_BASE_URL}/api/requests"
    
    # Test data
    test_data = {
        "type": "test_event_header",
        "fixture_id": "67890",
        "message": "Test message with secret key in header",
        "timestamp": datetime.now().isoformat()
    }
    
    # Method 2: Secret key qua header
    print("🔐 Testing API with secret key via header...")
    headers = {
        "X-Secret-Key": SECRET_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Success: API call with secret key in header worked!")
        else:
            print("❌ Failed: API call failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")

def test_api_without_secret():
    """Test API không có secret key (should fail)"""
    
    url = f"{API_BASE_URL}/api/requests"
    
    # Test data
    test_data = {
        "type": "test_event_no_secret",
        "fixture_id": "99999",
        "message": "Test message without secret key",
        "timestamp": datetime.now().isoformat()
    }
    
    print("🚫 Testing API without secret key (should fail)...")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Success: API correctly rejected request without secret key!")
        else:
            print("❌ Failed: API should have rejected this request")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")

def test_api_wrong_secret():
    """Test API với secret key sai (should fail)"""
    
    url = f"{API_BASE_URL}/api/requests"
    
    # Test data
    test_data = {
        "type": "test_event_wrong_secret",
        "fixture_id": "11111",
        "message": "Test message with wrong secret key",
        "timestamp": datetime.now().isoformat()
    }
    
    print("🔑 Testing API with wrong secret key (should fail)...")
    params = {"secret_key": "wrong-secret-key"}
    
    try:
        response = requests.post(url, json=test_data, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Success: API correctly rejected request with wrong secret key!")
        else:
            print("❌ Failed: API should have rejected this request")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")

def test_event_match_end():
    """Test API với type: event_match_end để trigger article generation"""
    
    url = f"{API_BASE_URL}/api/requests"
    
    # Test data for event_match_end
    test_data = {
        "type": "event_match_end",
        "fixture_id": "test_fixture_123",
        "message": "Match ended - trigger article generation",
        "timestamp": datetime.now().isoformat()
    }
    
    print("⚽ Testing API with event_match_end type...")
    params = {"secret_key": SECRET_KEY}
    
    try:
        response = requests.post(url, json=test_data, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Success: event_match_end processed successfully!")
        else:
            print("❌ Failed: event_match_end processing failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")

def main():
    """Main function to run all tests"""
    
    print("🚀 Starting API Secret Key Tests")
    print("="*50)
    
    # Check if SECRET_KEY is set
    if SECRET_KEY == "your-secret-key-here":
        print("⚠️  Warning: Please update SECRET_KEY in this script with your actual secret key")
        print("   You can also set it as environment variable: export SECRET_KEY=your_actual_key")
        print()
    
    # Run all tests
    test_api_without_secret()
    test_api_wrong_secret()
    test_api_with_secret_key()
    test_api_with_header()
    test_event_match_end()
    
    print("🏁 All tests completed!")
    print("\n📝 Usage Examples:")
    print("1. Via URL parameter:")
    print(f"   curl -X POST '{API_BASE_URL}/api/requests?secret_key={SECRET_KEY}' \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"type\": \"test\", \"message\": \"Hello World\"}'")
    print()
    print("2. Via Header:")
    print(f"   curl -X POST '{API_BASE_URL}/api/requests' \\")
    print(f"        -H 'X-Secret-Key: {SECRET_KEY}' \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"type\": \"test\", \"message\": \"Hello World\"}'")

if __name__ == "__main__":
    main()
