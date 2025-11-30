"""
Test script to verify AK Health Platform routes are working correctly
"""

import requests
import time

BASE_URL = "http://localhost:5000"

print("🧪 Testing AK Health Platform Routes...\n")

try:
    # Test 1: Home page
    print("1. Testing home page...")
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"Home page failed: {r.status_code}"
    print("   ✓ Home page works")
    
    # Test 2: Doctors page (should work for everyone)
    print("2. Testing doctors listing...")
    r = requests.get(f"{BASE_URL}/doctors")
    assert r.status_code == 200, f"Doctors page failed: {r.status_code}"
    print("   ✓ Doctors listing works")
    
    # Test 3: Doctor detail page
    print("3. Testing doctor detail page...")
    r = requests.get(f"{BASE_URL}/doctor/1")
    assert r.status_code == 200, f"Doctor detail failed: {r.status_code}"
    print("   ✓ Doctor detail page works")
    
    # Test 4: Register page
    print("4. Testing registration page...")
    r = requests.get(f"{BASE_URL}/register")
    assert r.status_code == 200, f"Register page failed: {r.status_code}"
    print("   ✓ Registration page works")
    
    # Test 5: Login page
    print("5. Testing login page...")
    r = requests.get(f"{BASE_URL}/login")
    assert r.status_code == 200, f"Login page failed: {r.status_code}"
    print("   ✓ Login page works")
    
    print("\n✅ All basic routes are working!")
    print("\n📝 NOTE: To test protected routes, you need to:")
    print("   1. Register a new account")
    print("   2. Login with your credentials")
    print("   3. Try booking appointments and viewing your appointments")
    
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to Flask app at http://localhost:5000")
    print("   Make sure to run: python app.py")
except AssertionError as e:
    print(f"❌ ERROR: {e}")
except Exception as e:
    print(f"❌ ERROR: {e}")
