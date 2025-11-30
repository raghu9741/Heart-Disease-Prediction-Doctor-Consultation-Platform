#!/usr/bin/env python3
"""Smoke test for Razorpay order creation endpoint.

This script will register a test user (if needed), login via requests.Session, and call /create_order/<doctor_id> to verify order creation.
Requires the Flask app to be running and `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` set in the server env.
"""
import os
import requests
from datetime import datetime, timedelta

BASE = 'http://127.0.0.1:5000'

def main():
    key = os.environ.get('RAZORPAY_KEY_ID')
    secret = os.environ.get('RAZORPAY_KEY_SECRET')
    print('Razorpay keys present:' , bool(key and secret))

    s = requests.Session()

    # Check what the running server reports for its env
    try:
        # include test headers so a dev server without env vars can respond
        headers = {
            'X-Test-Razorpay-Key': os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_placeholder'),
            'X-Test-Razorpay-Secret': os.environ.get('RAZORPAY_KEY_SECRET', 'placeholder_secret')
        }
        r_env = s.get(f'{BASE}/env_check', timeout=3, headers=headers)
        try:
            print('Server env_check:', r_env.json())
        except Exception:
            print('Server env_check response text:', r_env.text[:200])
    except Exception as e:
        print('Could not reach server env_check:', e)

    # Register a user
    ts = int(datetime.now().timestamp())
    username = f'smoketest_{ts%1000000}'
    password = 'testpass123'
    email = f'smoketest_{ts%1000000}@example.com'

    print('Registering user:', username)
    r = s.post(f'{BASE}/register', data={'username': username, 'password': password, 'confirm_password': password, 'email': email})
    print('Register status:', r.status_code)

    # Now attempt to create order
    doctor_id = 1
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    payload = {'appointment_date': tomorrow, 'appointment_time': '10:00 AM', 'notes': 'Smoke test booking'}

    print('Calling create_order...')
    r = s.post(f'{BASE}/create_order/{doctor_id}', json=payload, headers=headers)
    print('Status:', r.status_code)
    try:
        print('Response JSON:', r.json())
    except Exception:
        print('Response text:', r.text[:400])

if __name__ == '__main__':
    main()
