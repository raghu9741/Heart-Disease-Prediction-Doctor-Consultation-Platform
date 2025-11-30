#!/usr/bin/env python3
"""
Direct check of login route to see if session is set
"""

import sys
sys.path.insert(0, '/c/Users/RaghuKote/Desktop/AK MINI PROJECT')

from app import app
from flask import session

def test_login_session_setting():
    """Verify that login actually sets the session"""
    
    with app.app_context():
        client = app.test_client()
        
        print("Testing login session setting...\n")
        
        # Register
        import time
        user_id = int(time.time() * 1000) % 1000000
        username = f"testuser_{user_id}"
        
        client.post('/register', data={
            'username': username,
            'password': 'testpass123',
            'email': f'test_{user_id}@example.com'
        })
        
        print(f"Registered: {username}\n")
        
        # Login and inspect what happens
        print("Logging in...")
        with client:
            resp = client.post('/login', data={
                'username': username,
                'password': 'testpass123'
            })
            
            print(f"Status: {resp.status_code}")
            print(f"Headers: {dict(resp.headers)}\n")
            
            # Within the 'with client:' block, we can access the session
            # after the request is processed
            print(f"Session data after login request:")
            print(f"  session.logged_in = {session.get('logged_in')}")
            print(f"  session.admin_user = {session.get('admin_user')}")
            print(f"  All session keys: {dict(session)}\n")
            
            # Now try to access a protected route
            print("Accessing /my_appointments...")
            resp2 = client.get('/my_appointments')
            print(f"Status: {resp2.status_code}\n")
            
            print(f"Session data after /my_appointments request:")
            print(f"  session.logged_in = {session.get('logged_in')}")
            print(f"  session.admin_user = {session.get('admin_user')}")

if __name__ == '__main__':
    test_login_session_setting()
