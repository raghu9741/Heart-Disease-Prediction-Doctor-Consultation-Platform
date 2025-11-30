"""Pytest in-process tests for appointments/bookings pages.

These are converted from network-style scripts so pytest can run them
without a separate Flask server process.
"""

def test_doctor_and_appointments_pages(client):

    # Doctor bookings page
    resp = client.get('/doctor-bookings/1')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'Bookings' in body or 'doctor_bookings' in body

    # All appointments dashboard
    resp = client.get('/all-doctor-appointments')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'All Doctor Appointments' in body or 'Bookings' in body

    # Doctor detail page
    resp = client.get('/doctor/1')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'View Bookings' in body or 'doctor-bookings/1' in body

    # Doctors listing
    resp = client.get('/doctors')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'View Bookings' in body and 'doctor-bookings/' in body


def test_navigation_and_responsive(client):

    # Register a user to reach predict_form
    username = f"navtest_{int(__import__('time').time())}"
    resp = client.post('/register', data={'username': username, 'password': 'test1234', 'confirm_password': 'test1234'}, follow_redirects=True)
    assert resp.status_code in (200, 302)

    resp = client.get('/predict_form')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert '/all-doctor-appointments' in body or 'All Bookings' in body

    # Responsive indicators on doctor-bookings page
    resp = client.get('/doctor-bookings/1')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'viewport' in body
