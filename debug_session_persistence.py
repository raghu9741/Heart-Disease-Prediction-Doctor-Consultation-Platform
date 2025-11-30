#!/usr/bin/env python3
"""
Debug why session is not persisting in test client
"""

import sys
sys.path.insert(0, '/c/Users/RaghuKote/Desktop/AK MINI PROJECT')

from app import app
from flask import session

def debug_session_persistence():
    """Debug session persistence across requests"""
    
    with app.app_context():
        client = app.test_client()
        
        print("Debugging session persistence...\n")
        
        # Register
        import time
        user_id = int(time.time() * 1000) % 1000000
        username = f"testuser_{user_id}"
        
        print(f"1. Register {username}")
        with client:
            resp = client.post('/register', data={
                'username': username,
                'password': 'testpass123',
                'email': f'test_{user_id}@example.com'
            }, follow_redirects=True)
            
            print(f"   Response status: {resp.status_code}")
            print(f"   Session after registration:")
            print(f"     logged_in={session.get('logged_in')}")
            print(f"     admin_user={session.get('admin_user')}")
            print()
        
        print(f"2. API call in separate with block")
        with client:
            resp = client.post('/api/book_appointment/1', json={
                'appointment_date': '2025-12-02',
                'appointment_time': '10:00 AM'
            })
            
            print(f"   Response status: {resp.status_code}")
            print(f"   Session during API call:")
            print(f"     logged_in={session.get('logged_in')}")
            print(f"     admin_user={session.get('admin_user')}")
            print()
        
        print(f"3. Combined with block")
        with client:
            # Register
            resp1 = client.post('/register', data={
                'username': f'user_{user_id}_v2',
                'password': 'testpass123',
                'email': f'test_{user_id}_v2@example.com'
            }, follow_redirects=True)
            
            print(f"   After registration:")
            print(f"     logged_in={session.get('logged_in')}")
            print(f"     admin_user={session.get('admin_user')}")
            
            # API call in same context
            resp2 = client.post('/api/book_appointment/1', json={
                'appointment_date': '2025-12-02',
                'appointment_time': '10:00 AM'
            })
            
            print(f"   API response status: {resp2.status_code}")
            print(f"   Session after API call:")
            print(f"     logged_in={session.get('logged_in')}")
            print(f"     admin_user={session.get('admin_user')}")

if __name__ == '__main__':
    debug_session_persistence()
