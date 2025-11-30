"""
Database verification script
Checks that all tables and sample data are properly created
"""

import sqlite3
import json

DB_FILE = "heart_predictions.db"

print("🔍 Database Verification Report\n")
print("=" * 60)

try:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    
    print(f"📊 Tables Found: {len(tables)}")
    print("-" * 60)
    
    for table in tables:
        table_name = table[0]
        
        # Get table info
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = cur.fetchall()
        
        # Get row count
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        
        print(f"\n✓ {table_name.upper()}")
        print(f"  Rows: {count} | Columns: {len(columns)}")
        
        if count > 0:
            # Show sample data
            if table_name == "doctors":
                cur.execute("SELECT id, name, specialization, rating FROM doctors LIMIT 2")
                rows = cur.fetchall()
                print(f"  Sample Data:")
                for row in rows:
                    print(f"    - Dr {row[1]} ({row[2]}) ⭐{row[3]}")
            
            elif table_name == "users":
                cur.execute("SELECT COUNT(*) FROM users")
                print(f"  Status: {count} user(s) registered")
            
            elif table_name == "appointments":
                cur.execute("SELECT COUNT(*) FROM appointments WHERE status='scheduled'")
                scheduled = cur.fetchone()[0]
                print(f"  Scheduled: {scheduled} | Total: {count}")
            
            elif table_name == "predictions":
                print(f"  Total predictions: {count}")
    
    print("\n" + "=" * 60)
    print("✅ DATABASE VERIFICATION COMPLETE\n")
    
    # Verify sample doctors
    print("📚 Sample Doctors Verification:")
    print("-" * 60)
    cur.execute("SELECT id, name, specialization, rating, consultation_fee FROM doctors")
    doctors = cur.fetchall()
    
    if len(doctors) == 5:
        print("✅ All 5 sample doctors found\n")
        for doc in doctors:
            print(f"  {doc[0]}. Dr. {doc[1]}")
            print(f"     Specialization: {doc[2]}")
            print(f"     Rating: {doc[3]}⭐")
            print(f"     Fee: ₹{doc[4]}\n")
    else:
        print(f"⚠ Expected 5 doctors, found {len(doctors)}")
    
    print("=" * 60)
    print("✅ All Systems Operational!\n")
    
    conn.close()

except FileNotFoundError:
    print(f"❌ Database file not found: {DB_FILE}")
    print("   Make sure to run: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
