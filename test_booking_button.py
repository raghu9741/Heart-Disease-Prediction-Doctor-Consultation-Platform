"""In-process pytest test for AJAX booking workflow (/api/book_appointment)."""

from datetime import datetime, timedelta


def test_ajax_booking_and_dashboard(client):

    # Register a new user
    user_id = int(datetime.now().timestamp())
    username = f"testuser_{user_id}"
    register_data = {'username': username, 'password': 'testpass123', 'confirm_password': 'testpass123'}
    resp = client.post('/register', data=register_data, follow_redirects=True)
    assert resp.status_code in (200, 302)

    # Ensure doctors page exists and pick doctor_id=1
    resp = client.get('/doctors')
    assert resp.status_code == 200
    doctor_id = 1

    # Call AJAX booking endpoint
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    booking_time = '10:00 AM'
    booking_payload = {'appointment_date': tomorrow, 'appointment_time': booking_time, 'notes': 'Automated test booking'}

    resp = client.post(f'/api/book_appointment/{doctor_id}', json=booking_payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data and data.get('success') is True

    # Verify appointment appears in my_appointments
    resp = client.get('/my_appointments')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert tomorrow in body or booking_time in body
