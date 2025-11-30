#!/usr/bin/env python3
"""
Debug script to check if session is being set correctly
"""

import sys
sys.path.insert(0, '/c/Users/RaghuKote/Desktop/AK MINI PROJECT')

from app import app
from flask import session

def test_session_handling():
    """Check if session is being set and retrieved correctly"""
    
    with app.app_context():
        client = app.test_client()
        
        print("Testing session handling...\n")
        
        # Step 1: Register
        print("1. Register user")
        import time
        user_id = int(time.time() * 1000) % 1000000
        username = f"testuser_{user_id}"
        
        resp = client.post('/register', data={
            'username': username,
            'password': 'testpass123',
            'email': f'test_{user_id}@example.com'
        })
        print(f"   Status: {resp.status_code}\n")
        
        # Step 2: Try to login and check session
        print("2. Login user")
        resp = client.post('/login', data={
            'username': username,
            'password': 'testpass123'
        })
        print(f"   Status: {resp.status_code}")
        print(f"   Response location: {resp.location}\n")
        
        # Step 3: Check if we can access protected route
        print("3. Access protected route (/doctors)")
        resp = client.get('/doctors')
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            print("   ✅ Can access protected route\n")
        else:
            print("   ❌ Cannot access protected route\n")
        
        # Step 4: Try /my_appointments
        print("4. Access /my_appointments (requires login)")
        resp = client.get('/my_appointments')
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            print("   ✅ Can access /my_appointments\n")
        else:
            print("   ❌ Redirected (likely to login)\n")
        
        # Step 5: Try API endpoint
        print("5. Access /api/book_appointment/1 (requires login)")
        resp = client.post('/api/book_appointment/1', json={
            'appointment_date': '2025-12-02',
            'appointment_time': '10:00 AM',
            'notes': 'test'
        })
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200 or resp.status_code == 400:
            print("   ✅ Reached API endpoint (not redirected)\n")
        else:
            print(f"   ❌ Redirected or error: {resp.status_code}\n")
            if resp.status_code == 302:
                print(f"   Location: {resp.location}\n")

if __name__ == '__main__':
    test_session_handling()
