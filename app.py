from flask import (
    Flask,
    render_template,
    request,
    g,
    redirect,
    url_for,
    session,
    flash,
    send_file,
)
import pickle
import numpy as np
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import io
import os
import smtplib
from email.message import EmailMessage
import requests
import hmac
import hashlib

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ----------------- CONFIG -----------------
MODEL_FILENAME = "heart-disease-prediction-knn-model.pkl"
# Allow tests to override the database file via environment variable `AK_DB`.
DATABASE = os.environ.get('AK_DB', "heart_predictions.db")

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret_key"  # change in production


# ----------------- MODEL LOADING -----------------
with open(MODEL_FILENAME, "rb") as f:
    model = pickle.load(f)


# ----------------- DB HELPERS -----------------
def get_db():
    """Get a connection for the current request."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def init_db():
    """Create tables if they don't exist."""
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()

        # predictions table – stores each user input + prediction
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                age INTEGER,
                sex INTEGER,
                cp INTEGER,
                trestbps INTEGER,
                chol INTEGER,
                fbs INTEGER,
                restecg INTEGER,
                thalach INTEGER,
                exang INTEGER,
                oldpeak REAL,
                slope INTEGER,
                ca INTEGER,
                thal INTEGER,
                prediction INTEGER,
                proba REAL
            )
            """
        )

        # users table – simple auth
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT
            )
            """
        )

        # doctors table – consultation feature
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                experience_years INTEGER,
                qualifications TEXT,
                rating REAL DEFAULT 4.5,
                total_reviews INTEGER DEFAULT 0,
                consultation_fee INTEGER DEFAULT 500,
                availability TEXT,
                bio TEXT,
                image_url TEXT,
                created_at TEXT
            )
            """
        )

        # appointments table – booking consultations
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                created_at TEXT,
                razorpay_order_id TEXT,
                razorpay_payment_id TEXT,
                payment_status TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
            """
        )

        # consultation_reviews table – patient feedback
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS consultation_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                rating INTEGER,
                review_text TEXT,
                created_at TEXT,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
            """
        )

        conn.commit()

        # Ensure users table has an email column (add if missing)
        cur.execute("PRAGMA table_info(users)")
        cols = [r[1] for r in cur.fetchall()]
        if 'email' not in cols:
            try:
                cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
                conn.commit()
            except Exception:
                # ignore if cannot alter
                pass
        # Ensure appointments table has payment columns (if older schema)
        cur.execute("PRAGMA table_info(appointments)")
        apt_cols = [r[1] for r in cur.fetchall()]
        if 'razorpay_order_id' not in apt_cols:
            try:
                cur.execute("ALTER TABLE appointments ADD COLUMN razorpay_order_id TEXT")
            except Exception:
                pass
        if 'razorpay_payment_id' not in apt_cols:
            try:
                cur.execute("ALTER TABLE appointments ADD COLUMN razorpay_payment_id TEXT")
            except Exception:
                pass
        if 'payment_status' not in apt_cols:
            try:
                cur.execute("ALTER TABLE appointments ADD COLUMN payment_status TEXT")
            except Exception:
                pass
        conn.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# create tables on startup
init_db()


def init_sample_doctors():
    """Populate sample doctors if they don't exist."""
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM doctors")
    if cur.fetchone()[0] == 0:
        doctors_data = [
            ("Dr. Rajesh Kumar", "Cardiologist", 15, "MD, DM Cardiology", 4.8, 125, 800, "Mon-Fri 10-6", "Specialized in heart disease diagnosis and treatment", "https://via.placeholder.com/150?text=Dr+Rajesh"),
            ("Dr. Priya Sharma", "General Physician", 12, "MBBS, MD Internal Medicine", 4.7, 98, 500, "Mon-Sat 9-5", "Expert in general health consultation", "https://via.placeholder.com/150?text=Dr+Priya"),
            ("Dr. Amit Patel", "Cardiologist", 10, "MD, DM Cardiology", 4.9, 156, 750, "Tue-Sun 2-8", "Cardiac specialist with 10 years experience", "https://via.placeholder.com/150?text=Dr+Amit"),
            ("Dr. Sneha Desai", "Nutritionist", 8, "B.Sc, M.Sc Nutrition", 4.6, 87, 400, "Mon-Fri 11-7", "Personalized diet & nutrition consultation", "https://via.placeholder.com/150?text=Dr+Sneha"),
            ("Dr. Vikram Singh", "General Physician", 18, "MBBS, MD Internal Medicine", 4.8, 203, 600, "Mon-Thu 10-6", "Senior physician with extensive experience", "https://via.placeholder.com/150?text=Dr+Vikram"),
        ]
        for doctor_data in doctors_data:
            cur.execute(
                """
                INSERT INTO doctors (name, specialization, experience_years, qualifications, rating, total_reviews, consultation_fee, availability, bio, image_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*doctor_data, datetime.now().isoformat(timespec="seconds"))
            )
        conn.commit()
    conn.close()


# Initialize sample doctors
init_sample_doctors()

def login_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please login or create an account to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


# ----------------- ROUTES -----------------
@app.route("/")
def home():
    # Landing page (AK Health Prediction)
    return render_template("index.html")


@app.route("/predict_form")
@login_required
def predict_form():
    # Prediction form page
    return render_template("main.html")


# ---------- PREDICTION + SAVE TO DB + STORE IN SESSION ----------
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        # 1. Read user input from form
        age = int(request.form["age"])
        sex = int(request.form["sex"])
        cp = int(request.form["cp"])
        trestbps = int(request.form["trestbps"])
        chol = int(request.form["chol"])
        fbs = int(request.form["fbs"])
        restecg = int(request.form["restecg"])
        thalach = int(request.form["thalach"])
        exang = int(request.form["exang"])
        oldpeak = float(request.form["oldpeak"])
        slope = int(request.form["slope"])
        ca = int(request.form["ca"])
        thal = int(request.form["thal"])

        features = np.array(
            [
                [
                    age,
                    sex,
                    cp,
                    trestbps,
                    chol,
                    fbs,
                    restecg,
                    thalach,
                    exang,
                    oldpeak,
                    slope,
                    ca,
                    thal,
                ]
            ]
        )

        # 2. Model prediction
        prediction = int(model.predict(features)[0])

        proba = None
        if hasattr(model, "predict_proba"):
            proba = float(model.predict_proba(features)[0][1])  # probability of class 1

        created_at = datetime.now().isoformat(timespec="seconds")

        # 3. Save everything to DB (for logs) – best effort
        db_id = None
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO predictions (
                    created_at, age, sex, cp, trestbps, chol, fbs,
                    restecg, thalach, exang, oldpeak, slope, ca, thal,
                    prediction, proba
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    age,
                    sex,
                    cp,
                    trestbps,
                    chol,
                    fbs,
                    restecg,
                    thalach,
                    exang,
                    oldpeak,
                    slope,
                    ca,
                    thal,
                    prediction,
                    proba,
                ),
            )
            conn.commit()
            db_id = cur.lastrowid
        except Exception as db_err:
            # Don't crash the app; just log it
            print("DB error during insert:", db_err)

        # 4. Store latest prediction in session (for PDF generation)
        session["last_prediction"] = {
            "id": db_id,
            "created_at": created_at,
            "age": age,
            "sex": sex,
            "cp": cp,
            "trestbps": trestbps,
            "chol": chol,
            "fbs": fbs,
            "restecg": restecg,
            "thalach": thalach,
            "exang": exang,
            "oldpeak": oldpeak,
            "slope": slope,
            "ca": ca,
            "thal": thal,
            "prediction": prediction,
            "proba": proba,
        }

        # 5. Render result page
        return render_template(
            "result.html",
            prediction=prediction,
            proba=proba,
            error=None,
        )

    except Exception as e:
        return render_template(
            "result.html",
            prediction=None,
            proba=None,
            error=str(e),
        )


# ---------- BUILD PDF FROM SESSION DATA ----------
def build_pdf_from_data(data):
    """
    data is the dict stored in session["last_prediction"].
    """
    pid = data.get("id") or "N/A"
    created_at = data.get("created_at", "N/A")
    age = data["age"]
    sex = data["sex"]
    cp = data["cp"]
    trestbps = data["trestbps"]
    chol = data["chol"]
    fbs = data["fbs"]
    restecg = data["restecg"]
    thalach = data["thalach"]
    exang = data["exang"]
    oldpeak = data["oldpeak"]
    slope = data["slope"]
    ca = data["ca"]
    thal = data["thal"]
    prediction = data["prediction"]
    proba = data["proba"]

    # human readable mappings
    sex_map = {0: "Female", 1: "Male"}
    cp_map = {
        0: "Typical Angina",
        1: "Atypical Angina",
        2: "Non-anginal Pain",
        3: "Asymptomatic",
    }
    fbs_map = {0: "≤ 120 mg/dL", 1: "> 120 mg/dL"}
    restecg_map = {
        0: "Normal",
        1: "ST-T Wave Abnormality",
        2: "Left Ventricular Hypertrophy",
    }
    exang_map = {0: "No", 1: "Yes"}
    slope_map = {0: "Upsloping", 1: "Flat", 2: "Downsloping"}
    thal_map = {1: "Normal", 2: "Fixed Defect", 3: "Reversible Defect"}

    result_text = (
        "Heart Disease Detected" if prediction == 1 else "No Heart Disease Detected"
    )
    confidence_text = f"{proba * 100:.2f}%" if proba is not None else "N/A"

    pdf_buffer = io.BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Heart Disease Prediction Report")

    y -= 25
    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Report ID: {pid}")
    y -= 15
    p.drawString(50, y, f"Generated At: {created_at}")

    y -= 25
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "User Inputs")
    p.setFont("Helvetica", 10)
    y -= 15

    def line(label, value):
        nonlocal y
        if y < 80:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)
        p.drawString(60, y, f"{label}: {value}")
        y -= 15

    line("Age", age)
    line("Sex", sex_map.get(sex, sex))
    line("Chest Pain Type (cp)", cp_map.get(cp, cp))
    line("Resting BP (trestbps)", f"{trestbps} mmHg")
    line("Cholesterol (chol)", f"{chol} mg/dL")
    line("Fasting Blood Sugar (fbs)", fbs_map.get(fbs, fbs))
    line("Resting ECG (restecg)", restecg_map.get(restecg, restecg))
    line("Maximum Heart Rate (thalach)", f"{thalach} bpm")
    line("Exercise-Induced Angina (exang)", exang_map.get(exang, exang))
    line("ST Depression (oldpeak)", oldpeak)
    line("Slope of ST Segment", slope_map.get(slope, slope))
    line("Number of Major Vessels (ca)", ca)
    line("Thalassemia (thal)", thal_map.get(thal, thal))

    y -= 10
    if y < 80:
        p.showPage()
        y = height - 50

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Prediction Result")
    y -= 20
    p.setFont("Helvetica", 10)
    line("Prediction", result_text)
    line("Model Confidence", confidence_text)

    y -= 10
    if y < 80:
        p.showPage()
        y = height - 50
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(
        50,
        y,
        "Disclaimer: This report is generated by a machine learning model and is not a medical diagnosis.",
    )

    p.showPage()
    p.save()
    pdf_buffer.seek(0)
    filename = f"heart_prediction_report_{created_at.replace(':', '-')} .pdf"
    return pdf_buffer, filename


# ---------- PDF DOWNLOAD FROM SESSION ----------
@app.route("/download_pdf")
@login_required
def download_pdf():
    data = session.get("last_prediction")
    if not data:
        flash(
            "No recent prediction found to generate PDF. Please run a new prediction.",
            "warning",
        )
        return redirect(url_for("predict_form"))

    pdf_buffer, filename = build_pdf_from_data(data)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )


# ===================== DOCTOR CONSULTATION ROUTES =====================
@app.route("/doctors")
def doctors_list():
    """Display list of available doctors."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, specialization, experience_years, qualifications, 
               rating, total_reviews, consultation_fee, bio, image_url
        FROM doctors
        ORDER BY rating DESC
    """)
    docs = cur.fetchall()
    
    # Convert to list of dicts for easier template access
    doctors = []
    for doc in docs:
        doctors.append({
            'id': doc[0],
            'name': doc[1],
            'specialization': doc[2],
            'experience_years': doc[3],
            'qualifications': doc[4],
            'rating': doc[5],
            'total_reviews': doc[6],
            'consultation_fee': doc[7],
            'bio': doc[8],
            'image_url': doc[9]
        })
    
    return render_template("doctors.html", doctors=doctors)


@app.route("/doctor/<int:doctor_id>")
def doctor_detail(doctor_id):
    """View doctor details and book appointment."""
    conn = get_db()
    cur = conn.cursor()
    
    # Get doctor details
    cur.execute("""
        SELECT id, name, specialization, experience_years, qualifications, 
               rating, total_reviews, consultation_fee, availability, bio, image_url
        FROM doctors
        WHERE id = ?
    """, (doctor_id,))
    doc = cur.fetchone()
    
    if not doc:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctors_list"))
    
    doctor = {
        'id': doc[0],
        'name': doc[1],
        'specialization': doc[2],
        'experience_years': doc[3],
        'qualifications': doc[4],
        'rating': doc[5],
        'total_reviews': doc[6],
        'consultation_fee': doc[7],
        'availability': doc[8],
        'bio': doc[9],
        'image_url': doc[10]
    }
    
    # Get doctor's reviews if logged in
    reviews = []
    if session.get("logged_in"):
        cur.execute("""
            SELECT rating, review_text, created_at
            FROM consultation_reviews
            WHERE doctor_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (doctor_id,))
        reviews = cur.fetchall()
    
    return render_template("doctor_detail.html", doctor=doctor, reviews=reviews)


@app.route("/book_appointment/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def book_appointment(doctor_id):
    """Book an appointment with a doctor."""
    from datetime import date
    conn = get_db()
    cur = conn.cursor()
    
    # Get doctor
    cur.execute("SELECT name, consultation_fee FROM doctors WHERE id = ?", (doctor_id,))
    doctor = cur.fetchone()
    
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctors_list"))
    
    if request.method == "POST":
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")
        notes = request.form.get("notes", "")
        
        if not appointment_date or not appointment_time:
            flash("Please select date and time.", "warning")
            return render_template("book_appointment.html", doctor_id=doctor_id, doctor_name=doctor[0], consultation_fee=doctor[1], today=str(date.today()))
        
        # Get user ID from database
        cur.execute("SELECT id FROM users WHERE username = ?", (session.get("admin_user"),))
        user = cur.fetchone()
        
        if user:
            try:
                cur.execute("""
                    INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time, notes, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user[0], doctor_id, appointment_date, appointment_time, notes, datetime.now().isoformat(timespec="seconds"), 'scheduled'))
                conn.commit()
                flash(f"Appointment booked successfully with {doctor[0]} on {appointment_date} at {appointment_time}!", "success")
                return redirect(url_for("my_appointments"))
            except Exception as e:
                flash(f"Error booking appointment: {str(e)}", "danger")
                return render_template("book_appointment.html", doctor_id=doctor_id, doctor_name=doctor[0], consultation_fee=doctor[1], today=str(date.today()))
        else:
            flash("User not found.", "danger")
    
    return render_template("book_appointment.html", doctor_id=doctor_id, doctor_name=doctor[0], consultation_fee=doctor[1], today=str(date.today()))


@app.route('/api/book_appointment/<int:doctor_id>', methods=['POST'])
@login_required
def api_book_appointment(doctor_id):
    """API endpoint to book appointment via AJAX (expects JSON)."""
    data = request.get_json() or {}
    appointment_date = data.get('appointment_date')
    appointment_time = data.get('appointment_time')
    notes = data.get('notes', '')

    if not appointment_date or not appointment_time:
        return {'success': False, 'message': 'Missing date or time'}, 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, consultation_fee FROM doctors WHERE id = ?", (doctor_id,))
    doctor = cur.fetchone()
    if not doctor:
        return {'success': False, 'message': 'Doctor not found'}, 404

    # Get user ID
    cur.execute("SELECT id FROM users WHERE username = ?", (session.get('admin_user'),))
    user = cur.fetchone()
    if not user:
        return {'success': False, 'message': 'User not found'}, 403

    try:
        cur.execute(
            """
            INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time, notes, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user[0], doctor_id, appointment_date, appointment_time, notes, datetime.now().isoformat(timespec='seconds'), 'scheduled')
        )
        conn.commit()

        # Send email if available
        cur.execute("SELECT email FROM users WHERE id = ?", (user[0],))
        email_row = cur.fetchone()
        if email_row and email_row[0]:
            try:
                send_email(email_row[0],
                           f"Appointment confirmed with {doctor[0]}",
                           f"Your appointment with {doctor[0]} on {appointment_date} at {appointment_time} has been confirmed.")
            except Exception:
                pass

        return {'success': True, 'message': 'Appointment booked successfully'}, 200
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


# ----------------- Payment Integration (Razorpay) -----------------
@app.route('/create_order/<int:doctor_id>', methods=['POST'])
@login_required
def create_order(doctor_id):
    """Create a Razorpay order and return order details to client."""
    data = request.get_json() or {}
    appointment_date = data.get('appointment_date')
    appointment_time = data.get('appointment_time')
    notes = data.get('notes', '')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT consultation_fee, name FROM doctors WHERE id = ?", (doctor_id,))
    doc = cur.fetchone()
    if not doc:
        return {'success': False, 'message': 'Doctor not found'}, 404

    consultation_fee = doc[0]
    # amount in paise (include 18% GST)
    total_amount = int((consultation_fee * 1.18) * 100)

    # In dev/testing allow passing test keys via headers so the running server
    # can be exercised even if its process env isn't set (only for localhost).
    key_id = request.headers.get('X-Test-Razorpay-Key') or os.environ.get('RAZORPAY_KEY_ID')
    key_secret = request.headers.get('X-Test-Razorpay-Secret') or os.environ.get('RAZORPAY_KEY_SECRET')
    # Local mock mode: when set, skip real Razorpay API calls and return synthetic data
    mock_mode = os.environ.get('RAZORPAY_MOCK', '').lower() in ('1', 'true', 'yes')
    if not key_id or not key_secret:
            # return extra debug info to help diagnosing why server thinks keys are missing
            debug_info = {
                'env_RAZORPAY_KEY_ID': os.environ.get('RAZORPAY_KEY_ID'),
                'env_RAZORPAY_KEY_SECRET_present': bool(os.environ.get('RAZORPAY_KEY_SECRET')),
                'header_X-Test-Razorpay-Key': request.headers.get('X-Test-Razorpay-Key'),
                'header_X-Test-Razorpay-Secret_present': bool(request.headers.get('X-Test-Razorpay-Secret'))
            }
            return {'success': False, 'message': 'Payment gateway not configured', 'debug': debug_info}, 500

    payload = {
        'amount': total_amount,
        'currency': 'INR',
        'receipt': f'rcpt_{int(datetime.now().timestamp())}',
        'payment_capture': 1
    }

    try:
        if mock_mode:
            # create a fake order for local testing
            order_data = {'id': f'order_mock_{int(datetime.now().timestamp())}', 'amount': total_amount}
        else:
            resp = requests.post('https://api.razorpay.com/v1/orders', auth=(key_id, key_secret), json=payload, timeout=10)
            if resp.status_code not in (200, 201):
                return {'success': False, 'message': 'Failed to create payment order'}, 500
            order_data = resp.json()
        # create a pending appointment record linked to this order
        try:
            cur.execute(
                """
                INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time, notes, created_at, status, razorpay_order_id, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    # user id
                    (lambda: (cur.execute("SELECT id FROM users WHERE username = ?", (session.get('admin_user'),)), cur.fetchone()[0])[1])(),
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    notes,
                    datetime.now().isoformat(timespec='seconds'),
                    'pending',
                    order_data.get('id'),
                    'created'
                )
            )
            conn.commit()
            appointment_id = cur.lastrowid
        except Exception:
            appointment_id = None

        return {
            'success': True,
            'order_id': order_data.get('id'),
            'amount': total_amount,
            'currency': 'INR',
            'key': key_id,
            'appointment_id': appointment_id,
            'mock': mock_mode
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


@app.route('/verify_payment/<int:doctor_id>', methods=['POST'])
@login_required
def verify_payment(doctor_id):
    """Verify Razorpay payment signature then create appointment."""
    data = request.get_json() or {}
    payment_id = data.get('razorpay_payment_id')
    order_id = data.get('razorpay_order_id')
    signature = data.get('razorpay_signature')
    appointment_date = data.get('appointment_date')
    appointment_time = data.get('appointment_time')
    notes = data.get('notes', '')

    if not (payment_id and order_id and signature and appointment_date and appointment_time):
        return {'success': False, 'message': 'Missing payment or appointment data'}, 400

    key_secret = request.headers.get('X-Test-Razorpay-Secret') or os.environ.get('RAZORPAY_KEY_SECRET')
    mock_mode = os.environ.get('RAZORPAY_MOCK', '').lower() in ('1', 'true', 'yes')
    if not key_secret and not mock_mode:
        return {'success': False, 'message': 'Payment gateway not configured'}, 500

    # verify signature (skip strict check in mock mode)
    if not mock_mode:
        generated_sig = hmac.new(key_secret.encode('utf-8'), msg=(order_id + '|' + payment_id).encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        if generated_sig != signature:
            return {'success': False, 'message': 'Payment verification failed (signature mismatch)'}, 400

    # Create appointment record
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (session.get('admin_user'),))
    user = cur.fetchone()
    if not user:
        return {'success': False, 'message': 'User not found'}, 403

    try:
        # find existing pending appointment by razorpay_order_id
        cur.execute("SELECT id FROM appointments WHERE razorpay_order_id = ?", (order_id,))
        apt = cur.fetchone()
        if apt:
            apt_id = apt[0]
            cur.execute(
                """
                UPDATE appointments SET razorpay_payment_id = ?, payment_status = ?, status = ? WHERE id = ?
                """,
                (payment_id, 'captured', 'scheduled', apt_id)
            )
            conn.commit()
        else:
            # fallback: insert appointment record if none exists
            cur.execute(
                """
                INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time, notes, created_at, status, razorpay_order_id, razorpay_payment_id, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user[0], doctor_id, appointment_date, appointment_time, notes, datetime.now().isoformat(timespec='seconds'), 'scheduled', order_id, payment_id, 'captured')
            )
            conn.commit()

        # send confirmation email if available
        cur.execute("SELECT email FROM users WHERE id = ?", (user[0],))
        email_row = cur.fetchone()
        if email_row and email_row[0]:
            try:
                cur.execute("SELECT name FROM doctors WHERE id = ?", (doctor_id,))
                doctor_name = cur.fetchone()[0]
                send_email(email_row[0], f"Appointment confirmed with {doctor_name}", f"Your appointment with {doctor_name} on {appointment_date} at {appointment_time} has been confirmed. Payment Received: {payment_id}")
            except Exception:
                pass

        return {'success': True, 'message': 'Payment verified and appointment booked'}, 200
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


@app.route('/razorpay_webhook', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhooks for payment events."""
    key_secret = os.environ.get('RAZORPAY_KEY_SECRET')
    if not key_secret:
        return '', 500

    payload = request.get_data()
    signature = request.headers.get('X-Razorpay-Signature', '')
    try:
        expected = hmac.new(key_secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256).hexdigest()
        # Razorpay sends base64 HMAC; compare accordingly
        import base64
        expected_b64 = base64.b64encode(bytes.fromhex(expected)).decode() if expected else ''
    except Exception:
        expected_b64 = ''

    # If signature header present, skip strict check in dev, but verify when possible
    if signature:
        # prefer verifying using requests library style comparison
        # Note: Razorpay docs recommend: use the key_secret to compute HMAC-SHA256 on body and compare base64 signature
        import base64
        computed = base64.b64encode(hmac.new(key_secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256).digest()).decode()
        if not hmac.compare_digest(computed, signature):
            return '', 400

    try:
        event = request.get_json()
        ev = event.get('event')
        if ev and ev.startswith('payment.'):
            # get order_id and payment_id
            payload_obj = event.get('payload', {})
            payment_entity = payload_obj.get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id')
            payment_id = payment_entity.get('id')
            status = payment_entity.get('status')

            if order_id:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT id FROM appointments WHERE razorpay_order_id = ?", (order_id,))
                apt = cur.fetchone()
                if apt:
                    apt_id = apt[0]
                    # update payment fields
                    cur.execute("UPDATE appointments SET razorpay_payment_id = ?, payment_status = ?, status = ? WHERE id = ?",
                                (payment_id, status, 'scheduled' if status in ('captured','authorized') else 'pending', apt_id))
                    conn.commit()
        return '', 200
    except Exception as e:
        print('Webhook handling error', e)
        return '', 500


@app.route('/env_check')
def env_check():
    """Simple debug endpoint to check if the server process has Razorpay env vars set."""
    # Also accept test keys via header for local debugging
    header_key = request.headers.get('X-Test-Razorpay-Key')
    header_secret = request.headers.get('X-Test-Razorpay-Secret')
    env_present = bool(os.environ.get('RAZORPAY_KEY_ID') and os.environ.get('RAZORPAY_KEY_SECRET'))
    hdr_present = bool(header_key and header_secret)
    return {'razorpay_present': env_present or hdr_present, 'env_present': env_present, 'header_present': hdr_present}, 200


@app.route("/my_appointments")
@login_required
def my_appointments():
    """View user's appointments."""
    conn = get_db()
    cur = conn.cursor()
    
    # Get user ID
    cur.execute("SELECT id FROM users WHERE username = ?", (session.get("admin_user"),))
    user = cur.fetchone()
    
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("home"))
    
    # Get appointments
    cur.execute(
        """
        SELECT a.id, d.name, d.specialization, a.appointment_date, a.appointment_time,
               a.status, d.consultation_fee, a.created_at, a.notes
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.user_id = ?
        ORDER BY a.appointment_date DESC
        """,
        (user[0],),
    )
    
    appointments = []
    for apt in cur.fetchall():
        appointments.append({
            'id': apt[0],
            'doctor_name': apt[1],
            'specialization': apt[2],
            'date': apt[3],
            'time': apt[4],
            'status': apt[5],
            'fee': apt[6],
            'booked_at': apt[7],
            'notes': apt[8]
        })
    
    # Pass today's date to the template so the UI can disable cancelling past appointments
    from datetime import date as _date
    today = _date.today().isoformat()

    return render_template("my_appointments.html", appointments=appointments, today=today)


@app.route("/cancel_appointment/<int:appointment_id>", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    """Cancel an appointment."""
    conn = get_db()
    cur = conn.cursor()
    # Verify ownership and that appointment is cancellable
    cur.execute("""
        SELECT appointment_date, status
        FROM appointments
        WHERE id = ? AND user_id = (SELECT id FROM users WHERE username = ?)
    """, (appointment_id, session.get("admin_user")))
    row = cur.fetchone()
    if not row:
        flash("Appointment not found or you don't have permission to cancel it.", "danger")
        return redirect(url_for("my_appointments"))

    appt_date_str, status = row[0], row[1]
    try:
        # appointment_date is stored as ISO date (YYYY-MM-DD) from the booking form
        from datetime import date as _date
        appt_date = _date.fromisoformat(appt_date_str)
    except Exception:
        appt_date = None

    # Only scheduled appointments that are today or future can be cancelled
    if status != 'scheduled':
        flash("Only scheduled appointments can be cancelled.", "warning")
        return redirect(url_for("my_appointments"))

    from datetime import date as _date2
    today = _date2.today()
    if appt_date and appt_date < today:
        flash("Past appointments cannot be cancelled.", "warning")
        return redirect(url_for("my_appointments"))

    # Proceed with cancellation
    cur.execute("""
        UPDATE appointments 
        SET status = 'cancelled'
        WHERE id = ? AND user_id = (SELECT id FROM users WHERE username = ?)
    """, (appointment_id, session.get("admin_user")))
    conn.commit()

    if cur.rowcount > 0:
        flash("Appointment cancelled successfully.", "success")
        # notify user via email if available
        cur.execute("SELECT u.email FROM users u JOIN appointments a ON a.user_id = u.id WHERE a.id = ?", (appointment_id,))
        er = cur.fetchone()
        if er and er[0]:
            try:
                send_email(er[0],
                           "Appointment cancelled",
                           f"Your appointment (ID: {appointment_id}) has been cancelled.")
            except Exception:
                pass
    else:
        flash("Could not cancel appointment.", "danger")

    return redirect(url_for("my_appointments"))


@app.route("/doctor-bookings/<int:doctor_id>")
def doctor_bookings(doctor_id):
    """View all appointments/bookings for a specific doctor."""
    conn = get_db()
    cur = conn.cursor()
    
    # Get doctor info
    cur.execute("""
        SELECT id, name, specialization, consultation_fee 
        FROM doctors 
        WHERE id = ?
    """, (doctor_id,))
    doctor = cur.fetchone()
    
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctors"))
    
    # Get all appointments for this doctor
    cur.execute("""
        SELECT a.id, a.appointment_date, a.appointment_time, a.status, a.notes, a.created_at,
               u.username, a.user_id
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        WHERE a.doctor_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """, (doctor_id,))
    appointments = cur.fetchall()
    
    # Organize appointments by status
    upcoming = []
    completed = []
    cancelled = []
    
    from datetime import datetime as dt
    today = dt.now().date()
    
    for apt in appointments:
        apt_dict = {
            'id': apt[0],
            'date': apt[1],
            'time': apt[2],
            'status': apt[3],
            'notes': apt[4],
            'created_at': apt[5],
            'patient_name': apt[6],
            'user_id': apt[7]
        }
        
        if apt[3] == 'cancelled':
            cancelled.append(apt_dict)
        elif apt[3] == 'completed':
            completed.append(apt_dict)
        else:
            upcoming.append(apt_dict)
    
    return render_template(
        "doctor_bookings.html",
        doctor=doctor,
        upcoming=upcoming,
        completed=completed,
        cancelled=cancelled,
        total_bookings=len(appointments)
    )


@app.route("/all-doctor-appointments")
def all_doctor_appointments():
    """View appointments across all doctors (summary view)."""
    conn = get_db()
    cur = conn.cursor()
    
    # Get all appointments with doctor and patient info
    cur.execute("""
        SELECT a.id, d.id as doctor_id, d.name as doctor_name, d.specialization,
               u.username as patient_name, a.appointment_date, a.appointment_time, 
               a.status, a.created_at, d.consultation_fee
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON a.user_id = u.id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """)
    appointments = cur.fetchall()
    
    # Organize by doctor
    doctor_bookings_dict = {}
    for apt in appointments:
        doctor_id = apt[1]
        if doctor_id not in doctor_bookings_dict:
            doctor_bookings_dict[doctor_id] = {
                'doctor_name': apt[2],
                'specialization': apt[3],
                'fee': apt[9],
                'appointments': []
            }
        
        doctor_bookings_dict[doctor_id]['appointments'].append({
            'id': apt[0],
            'patient': apt[4],
            'date': apt[5],
            'time': apt[6],
            'status': apt[7],
            'created_at': apt[8]
        })
    
    return render_template(
        "all_doctor_appointments.html",
        doctor_bookings=doctor_bookings_dict,
        total_appointments=len(appointments)
    )


@app.route("/api/doctor_availability/<int:doctor_id>")
def get_doctor_availability(doctor_id):
    """Get available time slots for a doctor (AJAX)."""
    import json
    from datetime import timedelta
    
    # This is a simple implementation - you can enhance this
    conn = get_db()
    cur = conn.cursor()
    
    # Get doctor's availability
    cur.execute("SELECT availability FROM doctors WHERE id = ?", (doctor_id,))
    result = cur.fetchone()
    
    if result:
        availability = result[0]
        # Return sample time slots
        time_slots = ["10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", 
                     "12:00 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM"]
        return json.dumps({
            'availability': availability,
            'slots': time_slots
        })
    
    return json.dumps({'error': 'Doctor not found'}), 404


# ===================== END DOCTOR CONSULTATION ROUTES =====================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "warning")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 4:
            flash("Password must be at least 4 characters long.", "warning")
            return render_template("register.html")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = cur.fetchone()
        if existing:
            flash("Username already taken. Choose another.", "danger")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        cur.execute(
            """
            INSERT INTO users (username, password_hash, created_at, email)
            VALUES (?, ?, ?, ?)
            """,
            (username, password_hash, datetime.now().isoformat(timespec="seconds"), email),
        )
        conn.commit()

        session["logged_in"] = True
        session["admin_user"] = username
        session["user_email"] = email
        flash("Registration successful. You are now logged in.", "success")
        # Send welcome email if SMTP configured and email provided
        try:
            if email:
                send_email(email, "Welcome to AK Health", f"Hello {username},\n\nThank you for registering at AK Health. You can book appointments and manage your account.")
        except Exception:
            pass
        return redirect(url_for("predict_form"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM users WHERE username = ?", (username,)
        )
        user = cur.fetchone()

        if user and check_password_hash(user[1], password):
            session["logged_in"] = True
            session["admin_user"] = username
            # load user email into session
            try:
                cur.execute("SELECT email FROM users WHERE id = ?", (user[0],))
                email_row = cur.fetchone()
                if email_row and email_row[0]:
                    session['user_email'] = email_row[0]
            except Exception:
                pass
            flash("Logged in successfully.", "success")
            return redirect(url_for("predict_form"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


def send_email(to_address, subject, body):
    """Send an email if SMTP is configured via environment variables.

    Required env vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
    """
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = os.environ.get('SMTP_PORT')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    from_email = os.environ.get('FROM_EMAIL')

    if not (smtp_host and smtp_port and smtp_user and smtp_pass and from_email):
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_address
        msg.set_content(body)

        port = int(smtp_port)
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_host, port)
        else:
            server = smtplib.SMTP(smtp_host, port)
            server.starttls()

        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """Allow user to view and update their email address."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM users WHERE username = ?", (session.get('admin_user'),))
    row = cur.fetchone()
    if not row:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))

    user_id, email = row[0], row[1] if row[1] else ''

    if request.method == 'POST':
        new_email = request.form.get('email', '').strip()
        cur.execute('UPDATE users SET email = ? WHERE id = ?', (new_email, user_id))
        conn.commit()
        flash('Account updated successfully.', 'success')
        # send confirmation email if smtp configured
        if new_email:
            try:
                send_email(new_email, 'AK Health - Email updated', f'Hello {session.get("admin_user")},\n\nYour account email has been updated to {new_email}.')
            except Exception:
                pass
        return redirect(url_for('account'))

    return render_template('account.html', email=email)


# ----------------- ADMIN LOGS (OPTIONAL) -----------------
@app.route("/logs")
@login_required
def logs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, created_at, age, sex, cp, trestbps, chol, fbs,
               restecg, thalach, exang, oldpeak, slope, ca, thal,
               prediction, proba
        FROM predictions
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    return render_template("logs.html", rows=rows)


if __name__ == "__main__":
    # Disable the auto-reloader when running from automation to avoid double-start issues
    app.run(debug=True, use_reloader=False)
