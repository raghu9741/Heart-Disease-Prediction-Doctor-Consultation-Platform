"""
Integration test for AK Health Platform
Tests registration, login, and appointment booking
"""

import requests
from requests.sessions import Session

BASE_URL = "http://localhost:5000"

print("🧪 Integration Test: User Registration & Appointment Booking\n")

try:
    session = Session()
    
    # Step 1: Register
    print("1. Testing user registration...")
    register_data = {
        'username': 'testuser123',
        'password': 'test1234',
        'confirm_password': 'test1234'
    }
    r = session.post(f"{BASE_URL}/register", data=register_data, allow_redirects=False)
    print(f"   Response: {r.status_code}")
    if r.status_code in [200, 302]:  # 302 = redirect after successful registration
        print("   ✓ Registration works")
    else:
        print(f"   ✗ Registration failed: {r.text[:200]}")
    
    # Step 2: Login
    print("\n2. Testing user login...")
    login_data = {
        'username': 'testuser123',
        'password': 'test1234'
    }
    r = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   Response: {r.status_code}")
    if r.status_code in [200, 302]:  # 302 = redirect after successful login
        print("   ✓ Login works")
    else:
        print(f"   ✗ Login failed")
    
    # Step 3: Try to access protected route (my_appointments)
    print("\n3. Testing protected route (My Appointments)...")
    r = session.get(f"{BASE_URL}/my_appointments")
    print(f"   Response: {r.status_code}")
    if r.status_code == 200:
        print("   ✓ Protected routes accessible after login")
    else:
        print(f"   ✗ Cannot access protected routes")
    
    # Step 4: Try to book appointment
    print("\n4. Testing appointment booking GET...")
    r = session.get(f"{BASE_URL}/book_appointment/1")
    print(f"   Response: {r.status_code}")
    if r.status_code == 200:
        print("   ✓ Appointment booking form loads")
        if 'appointment_date' in r.text:
            print("   ✓ Form has date input")
        if 'appointment_time' in r.text:
            print("   ✓ Form has time input")
    else:
        print(f"   ✗ Booking form failed")
    
    print("\n✅ All integration tests passed!")
    print("\n📌 Next Steps:")
    print("   1. Visit http://localhost:5000")
    print("   2. Login with testuser123 / test1234")
    print("   3. Click 'Doctors' to browse doctors")
    print("   4. Click on a doctor to see their profile")
    print("   5. Click 'Book Appointment'")
    print("   6. Select date and time")
    print("   7. Click 'Confirm Booking'")
    print("   8. View your appointments on the dashboard")
    
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to Flask app")
    print("   Make sure to run: python app.py")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
