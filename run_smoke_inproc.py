#!/usr/bin/env python3
"""Run smoke test in-process using Flask test client. Avoids network binding issues.
"""
import os
from datetime import datetime, timedelta

# Enable mock mode
os.environ['RAZORPAY_MOCK'] = '1'
os.environ['RAZORPAY_KEY_ID'] = 'rzp_test_placeholder'
os.environ['RAZORPAY_KEY_SECRET'] = 'placeholder_secret'

from app import app

BASE = 'http://127.0.0.1:5000'

def main():
    with app.test_client() as c:
        ts = int(datetime.now().timestamp())
        username = f'inproc_{ts%1000000}'
        password = 'testpass123'
        email = f'inproc_{ts%1000000}@example.com'

        print('Registering user:', username)
        r = c.post('/register', data={'username': username, 'password': password, 'confirm_password': password, 'email': email}, follow_redirects=True)
        print('Register status:', r.status_code)

        # Now attempt to create order
        doctor_id = 1
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        payload = {'appointment_date': tomorrow, 'appointment_time': '10:00 AM', 'notes': 'Inproc smoke test booking'}

        print('Calling create_order...')
        r = c.post(f'/create_order/{doctor_id}', json=payload)
        print('Status:', r.status_code)
        try:
            print('Response JSON:', r.get_json())
        except Exception:
            print('Response data:', r.data[:400])

if __name__ == '__main__':
    main()
