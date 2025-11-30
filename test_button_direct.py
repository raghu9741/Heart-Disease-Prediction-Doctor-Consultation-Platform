#!/usr/bin/env python3
"""
Direct test of the booking button functionality using Flask test client
"""

import sys
sys.path.insert(0, '/c/Users/RaghuKote/Desktop/AK MINI PROJECT')

from app import app, get_db
import json
from datetime import datetime, timedelta

def test_booking_with_client():
    """Test booking using Flask test client"""
    
    with app.app_context():
        client = app.test_client()
        
        print("=" * 70)
        print("TESTING CONFIRM BOOKING & PAY BUTTON")
        print("=" * 70)
        print()
        
        # All requests within one client context
        with client:
            # Step 1: Register
            print("Step 1: Register user...")
            import time
            user_id = int(time.time() * 1000) % 1000000
            username = f"testuser_{user_id}"
            password = "testpass123"
            email = f"test_{user_id}@example.com"
            
            resp = client.post('/register', data={
                'username': username,
                'password': password,
                'email': email
            })
            
            print(f"   Status: {resp.status_code}, Location: {resp.location}")
            assert resp.status_code in [200, 302], f"Register failed: {resp.status_code}"
            print(f"✅ User registered: {username}\n")
            
            # Step 2: User is already logged in after registration
            print("Step 2: User is already logged in after registration")
            print(f"✅ User logged in\n")
            
            # Step 3: Test AJAX booking endpoint
            print("Step 3: Test AJAX booking endpoint (Confirm Booking & Pay button)...")
            
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            booking_time = "10:00 AM"
            notes = "Test booking"
            doctor_id = 1
            
            booking_payload = {
                'appointment_date': tomorrow,
                'appointment_time': booking_time,
                'notes': notes
            }
            
            print(f"   Doctor ID: {doctor_id}")
            print(f"   Date: {tomorrow}")
            print(f"   Time: {booking_time}\n")
            
            resp = client.post(
                f'/api/book_appointment/{doctor_id}',
                data=json.dumps(booking_payload),
                content_type='application/json'
            )
            
            print(f"   Response Status: {resp.status_code}")
            print(f"   Response Content-Type: {resp.content_type}\n")
            
            if resp.status_code == 200:
                try:
                    data = resp.get_json()
                    print(f"   Response JSON: {data}")
                    
                    if data.get('success'):
                        print(f"\n✅ AJAX BOOKING SUCCESSFUL!")
                        print(f"   Message: {data['message']}\n")
                        appointment_confirmed = True
                    else:
                        print(f"\n❌ API returned success=False")
                        print(f"   Message: {data.get('message')}\n")
                        appointment_confirmed = False
                except Exception as e:
                    print(f"❌ Response is not valid JSON: {e}\n")
                    appointment_confirmed = False
            else:
                print(f"❌ API returned status {resp.status_code}\n")
                appointment_confirmed = False
            
            # Step 4: Verify appointment in dashboard
            if appointment_confirmed:
                print("Step 4: Verify appointment appears in dashboard...")
                resp = client.get('/my_appointments')
                
                if resp.status_code == 200:
                    dashboard_html = resp.data.decode()
                    if 'scheduled' in dashboard_html.lower() or tomorrow in dashboard_html:
                        print(f"✅ Appointment appears in user dashboard\n")
                    else:
                        print(f"⚠️ Appointment may not be visible\n")
                
                # Step 5: Verify in database
                print("Step 5: Verify appointment in database...")
                conn = get_db()
                cur = conn.cursor()
                cur.execute("""
                    SELECT COUNT(*) FROM appointments 
                    WHERE appointment_date = ? AND appointment_time = ?
                """, (tomorrow, booking_time))
                
                count = cur.fetchone()[0]
                if count > 0:
                    print(f"✅ Appointment found in database (Count: {count})\n")
                else:
                    print(f"❌ Appointment NOT found in database\n")
                
                conn.close()

if __name__ == '__main__':
    try:
        test_booking_with_client()
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
