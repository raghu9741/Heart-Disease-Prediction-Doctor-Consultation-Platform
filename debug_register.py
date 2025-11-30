#!/usr/bin/env python3
"""
Test registration directly and check session
"""

import sys
sys.path.insert(0, '/c/Users/RaghuKote/Desktop/AK MINI PROJECT')

from app import app
from flask import session

def test_registration():
    """Test registration and see if user is logged in"""
    
    with app.app_context():
        client = app.test_client()
        
        print("Testing registration...\n")
        
        import time
        user_id = int(time.time() * 1000) % 1000000
        username = f"testuser_{user_id}"
        password = "testpass123"
        email = f"test_{user_id}@example.com"
        
        print(f"Registering user: {username}\n")
        
        with client:
            # Send registration form
            resp = client.post('/register', data={
                'username': username,
                'password': password,
                'confirm_password': password,
                'email': email
            })
            
            print(f"Registration response status: {resp.status_code}")
            print(f"Location: {resp.location}\n")
            
            # Check session after registration
            print(f"Session after registration:")
            print(f"  session.logged_in = {session.get('logged_in')}")
            print(f"  session.admin_user = {session.get('admin_user')}")
            print(f"  All session keys: {list(dict(session).keys())}\n")
            
            # Check if registration returned HTML or redirected
            if resp.status_code == 302:
                print(f"Registration redirected (expected)\n")
            else:
                print(f"Response HTML length: {len(resp.data)}\n")
                if b"already taken" in resp.data or b"error" in resp.data.lower():
                    print("❌ Registration failed!")
                    print(f"Response contains error\n")
                else:
                    print("Registration response received\n")

if __name__ == '__main__':
    test_registration()
