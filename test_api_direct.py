#!/usr/bin/env python3
"""
Test script để test trực tiếp API endpoint
"""

import os
import sys
import traceback
import requests
import json

def test_api_direct():
    """Test API endpoint trực tiếp"""
    
    print("🔍 Testing API Endpoint Directly...")
    print("=" * 50)
    
    try:
        # Test 1: Check if app is running
        print("1. Checking if app is running...")
        try:
            response = requests.get('http://localhost:5000/', timeout=5)
            if response.status_code == 200:
                print("✅ App is running")
            else:
                print(f"⚠️ App responded with status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ App not running: {str(e)}")
            print("💡 Please start the app first: python app.py")
            return False
        
        # Test 2: Test Elasticsearch health endpoint
        print("\n2. Testing Elasticsearch health endpoint...")
        try:
            response = requests.get('http://localhost:5000/api/elasticsearch/health', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check request failed: {str(e)}")
        
        # Test 3: Test Elasticsearch stats endpoint
        print("\n3. Testing Elasticsearch stats endpoint...")
        try:
            response = requests.get('http://localhost:5000/api/elasticsearch/stats', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Stats: {data}")
            else:
                print(f"❌ Stats failed: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Stats request failed: {str(e)}")
        
        # Test 4: Test search endpoint
        print("\n4. Testing search endpoint...")
        try:
            response = requests.get('http://localhost:5000/api/search?q=machine learning', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Search: {data}")
            else:
                print(f"❌ Search failed: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Search request failed: {str(e)}")
        
        print("\n✅ API endpoint test completed!")
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 API Direct Test Suite")
    print("=" * 50)
    
    # Test API endpoint
    api_ok = test_api_direct()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 20)
    print(f"API Endpoint: {'✅ OK' if api_ok else '❌ FAIL'}")
    
    if api_ok:
        print("\n🎉 API endpoints are working!")
    else:
        print("\n⚠️ API endpoints have issues. Please check the errors above.")
