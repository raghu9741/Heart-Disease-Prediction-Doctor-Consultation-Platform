#!/usr/bin/env python3
"""
Check if registration actually succeeds
"""

import sys
sys.path.insert(0, '/c/Users/RaghuKote/Desktop/AK MINI PROJECT')

from app import app
from flask import session

def check_registration():
    """Check if registration succeeds"""
    
    with app.app_context():
        client = app.test_client()
        
        print("Checking registration...\n")
        
        import time
        user_id = int(time.time() * 1000) % 1000000
        username = f"testuser_{user_id}"
        
        with client:
            resp = client.post('/register', data={
                'username': username,
                'password': 'testpass123',
                'confirm_password': 'testpass123',
                'email': f'test_{user_id}@example.com'
            })
            
            print(f"Registration response status: {resp.status_code}")
            print(f"Registration response location: {resp.location}")
            print(f"Response HTML length: {len(resp.data)}")
            
            # Check if response contains errors
            resp_text = resp.data.decode()
            if 'error' in resp_text.lower() or 'warning' in resp_text.lower():
                print("\n⚠️ Response contains error or warning!")
                # Find the error message
                if 'Username and password' in resp_text:
                    print("   Error: Username and password required")
                elif 'Passwords do not match' in resp_text:
                    print("   Error: Passwords do not match")
                elif 'least 4 characters' in resp_text:
                    print("   Error: Password too short")
                elif 'already taken' in resp_text:
                    print("   Error: Username already taken")
                else:
                    print(f"   Response text (first 300 chars):\n   {resp_text[:300]}")
            else:
                print("\n✅ No obvious errors in response")
            
            print(f"\nSession after registration:")
            print(f"  logged_in={session.get('logged_in')}")
            print(f"  admin_user={session.get('admin_user')}")

if __name__ == '__main__':
    check_registration()
