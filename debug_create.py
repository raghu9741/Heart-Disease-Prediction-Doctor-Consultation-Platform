import os
from datetime import datetime, timedelta

# ensure mock mode and use a temp DB to avoid altering real DB
os.environ['RAZORPAY_MOCK'] = '1'
os.environ['RAZORPAY_KEY_ID'] = 'rzp_test_placeholder'
os.environ['RAZORPAY_KEY_SECRET'] = 'placeholder_secret'

from app import app, init_db

# initialize DB
try:
    init_db()
except Exception:
    pass

with app.test_client() as c:
    ts = int(datetime.now().timestamp())
    username = f'test_{ts%1000000}'
    password = 'testpass123'
    email = f'test_{ts%1000000}@example.com'

    # Register
    r = c.post('/register', data={'username': username, 'password': password, 'confirm_password': password, 'email': email}, follow_redirects=True)
    print('register status', r.status_code)
    print('register body snippet', r.get_data(as_text=True)[:400])

    # Create order
    doctor_id = 1
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    payload = {'appointment_date': tomorrow, 'appointment_time': '10:00 AM', 'notes': 'debug booking'}
    r = c.post(f'/create_order/{doctor_id}', json=payload)
    print('create_order status', r.status_code)
    print('create_order body')
    print(r.get_data(as_text=True))

    # If JSON, print it
    try:
        print('json:', r.get_json())
    except Exception:
        pass
