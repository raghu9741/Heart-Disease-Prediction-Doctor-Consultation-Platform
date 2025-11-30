#!/usr/bin/env python3
"""Run a verify_payment flow in-process using Flask test client.
"""
import os
import sqlite3
from datetime import datetime, timedelta

# Enable mock mode
os.environ['RAZORPAY_MOCK'] = '1'
os.environ['RAZORPAY_KEY_ID'] = 'rzp_test_placeholder'
os.environ['RAZORPAY_KEY_SECRET'] = 'placeholder_secret'

from app import app

DB = 'heart_predictions.db'

def query_appointment_by_order(order_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT id, status, razorpay_payment_id, payment_status FROM appointments WHERE razorpay_order_id = ?', (order_id,))
    row = cur.fetchone()
    conn.close()
    return row


def main():
    with app.test_client() as c:
        ts = int(datetime.now().timestamp())
        username = f'verify_{ts%1000000}'
        password = 'testpass123'
        email = f'verify_{ts%1000000}@example.com'

        print('Registering user:', username)
        r = c.post('/register', data={'username': username, 'password': password, 'confirm_password': password, 'email': email}, follow_redirects=True)
        print('Register status:', r.status_code)

        doctor_id = 1
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        payload = {'appointment_date': tomorrow, 'appointment_time': '10:00 AM', 'notes': 'Verify inproc booking'}

        print('Calling create_order...')
        r = c.post(f'/create_order/{doctor_id}', json=payload)
        print('create_order status:', r.status_code)
        order_resp = r.get_json() or {}
        print('create_order response:', order_resp)

        order_id = order_resp.get('order_id')
        if not order_id:
            print('No order_id returned, aborting')
            return

        # Now simulate payment verification
        payment_payload = {
            'razorpay_payment_id': f'pay_mock_{int(datetime.now().timestamp())}',
            'razorpay_order_id': order_id,
            'razorpay_signature': 'mock_signature',
            'appointment_date': tomorrow,
            'appointment_time': '10:00 AM',
            'notes': 'Verify inproc booking'
        }

        print('Calling verify_payment...')
        r2 = c.post(f'/verify_payment/{doctor_id}', json=payment_payload)
        print('verify_payment status:', r2.status_code)
        print('verify_payment response:', r2.get_json())

        # Query DB to confirm update
        apt = query_appointment_by_order(order_id)
        print('DB appointment row:', apt)

if __name__ == '__main__':
    main()
