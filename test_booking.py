"""Pytest in-process test: complete appointment booking workflow.

These tests use the Flask app's test client so they don't require a running
HTTP server on localhost:5000.
"""

from datetime import date, timedelta, datetime


def test_complete_booking_workflow(client):

    # Register a new user
    username = f'user_{int(datetime.now().timestamp())}'
    register_data = {
        'username': username,
        'password': 'password123',
        'confirm_password': 'password123'
    }
    resp = client.post('/register', data=register_data, follow_redirects=True)
    assert resp.status_code in (200, 302)

    # Book appointment for tomorrow
    tomorrow = date.today() + timedelta(days=1)
    booking_data = {
        'appointment_date': str(tomorrow),
        'appointment_time': '10:30 AM',
        'notes': 'I have chest pain and high blood pressure'
    }
    resp = client.post('/book_appointment/1', data=booking_data, follow_redirects=False)
    # The view redirects to /my_appointments on success
    assert resp.status_code in (302, 200)

    # Fetch appointments page and ensure the appointment is listed
    resp = client.get('/my_appointments')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'Dr. Rajesh Kumar' in body or '10:30 AM' in body
