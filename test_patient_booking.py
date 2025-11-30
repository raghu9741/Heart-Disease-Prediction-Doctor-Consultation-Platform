from app import app, init_db
import re

# Use Flask test client
with app.test_client() as client:
    # Ensure DB initialized
    init_db()

    # Use a unique username per run to avoid duplicate registration issues
    import uuid
    username = f'testuser_{uuid.uuid4().hex[:8]}'
    password = 'testpass'

    # 1) Register user
    resp = client.post('/register', data={'username': username, 'password': password, 'confirm_password': password}, follow_redirects=True)
    print('Register status:', resp.status_code)

    # 2) Find a doctor id to book (use first doctor)
    resp2 = client.get('/doctors')
    html = resp2.get_data(as_text=True)
    m = re.search(r"/doctor/(\d+)", html)
    if m:
        doctor_id = int(m.group(1))
    else:
        # fallback to id 1
        doctor_id = 1
    print('Using doctor_id =', doctor_id)

    # 3) Book appointment (POST)
    # Choose a date: today's date
    from datetime import date, timedelta
    appt_date = (date.today() + timedelta(days=1)).isoformat()
    appt_time = '10:00 AM'

    resp3 = client.post(f'/book_appointment/{doctor_id}', data={'appointment_date': appt_date, 'appointment_time': appt_time, 'notes': 'Test booking'}, follow_redirects=True)
    print('Booking status:', resp3.status_code)
    if b'Appointment booked successfully' in resp3.data:
        print('Booking confirmed by flash message')
    else:
        print('Booking flash not found; response length', len(resp3.data))

    # 4) Access my_appointments
    resp4 = client.get('/my_appointments')
    print('My appointments status:', resp4.status_code)
    page = resp4.get_data(as_text=True)
    if appt_date in page and appt_time in page:
        print('Appointment appears on my_appointments page')
    else:
        print('Appointment NOT found on my_appointments page')

    # 5) Attempt to cancel the appointment by finding appointment id from page
    m2 = re.search(r"/cancel_appointment/(\d+)", page)
    if m2:
        appt_id = int(m2.group(1))
        resp5 = client.post(f'/cancel_appointment/{appt_id}', follow_redirects=True)
        print('Cancel status:', resp5.status_code)
        if b'Appointment cancelled successfully' in resp5.data:
            print('Cancellation confirmed')
        else:
            print('Cancellation flash not found')
    else:
        print('Could not find cancel link on page')
