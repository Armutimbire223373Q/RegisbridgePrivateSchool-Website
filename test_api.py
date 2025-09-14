"""
Test script for FastAPI endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint failed: {e}")
        return False

def test_docs():
    """Test API documentation"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"API docs: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"API docs failed: {e}")
        return False

def test_login():
    """Test login endpoint"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful: {data.get('user', {}).get('username')}")
            return data.get('access_token')
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login test failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test a protected endpoint"""
    if not token:
        print("No token available for protected endpoint test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/me", headers=headers)
        print(f"Protected endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"User info: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Protected endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing FastAPI Backend...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("API Documentation", test_docs),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print(f"✅ {test_name}: {'PASS' if result else 'FAIL'}")
    
    # Test login and protected endpoints
    print(f"\n🔍 Login Test...")
    token = test_login()
    results.append(("Login", token is not None))
    
    if token:
        print(f"\n🔍 Protected Endpoint Test...")
        protected_result = test_protected_endpoint(token)
        results.append(("Protected Endpoint", protected_result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! FastAPI backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()
