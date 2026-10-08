#  Heart Disease Prediction & Doctor Consultation Platform

A comprehensive healthcare platform that combines AI-powered heart disease prediction with dynamic doctor consultation booking system, built with Flask and machine learning.

## 🎯 Features

### 1. **Heart Disease Prediction**
- AI-powered prediction using KNN machine learning model
- Trained on Cleveland Heart Disease dataset
- Analyzes 13 clinical parameters:
  - Age, Sex, Chest Pain Type
  - Blood Pressure, Cholesterol
  - Fasting Blood Sugar, Resting ECG
  - Maximum Heart Rate, Exercise-Induced Angina
  - ST Depression, Slope, Number of Major Vessels
  - Thalassemia Type

- **Output**: Disease risk prediction with confidence score
- **Features**:
  - Real-time PDF report generation
  - Prediction history logging
  - User-specific prediction tracking

### 2. **Doctor Consultation System** (Practo-Style)
Dynamic doctor booking platform with the following capabilities:

#### Doctor Browse & Search
- Browse available doctors with filtering options
- Filter by specialization (Cardiologist, General Physician, Nutritionist)
- Sort by ratings, experience, and consultation fees
- Detailed doctor profiles with qualifications and patient reviews

#### Appointment Booking
- Dynamic date/time selection
- Available time slots (10:00 AM - 5:00 PM)
- Real-time fee calculation with GST
- Consultation notes for doctors
- Instant booking confirmation

#### Appointment Management
- View upcoming appointments
- See completed consultations
- Manage cancelled bookings
- Appointment status tracking (Scheduled, Completed, Cancelled)
- One-click appointment cancellation
- Video call integration readiness

### 3. **User Authentication**
- Secure user registration and login
- Password hashing with werkzeug
- Session management
- User-specific data isolation

### 4. **Admin Features**
- Prediction logs dashboard
- Appointment history viewing
- Performance tracking

---

## 📁 Project Structure

```
AK MINI PROJECT/
├── app.py                          # Main Flask application
├── train_model.py                 # Model training script
├── heart_cleveland_upload.csv      # Dataset
├── heart-disease-prediction-knn-model.pkl  # Trained ML model
├── heart_predictions.db           # SQLite database
├── templates/
│   ├── index.html                 # Home page
│   ├── main.html                  # Prediction form
│   ├── result.html                # Prediction results
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── logs.html                  # Admin logs
│   ├── doctors.html               # Doctor listing (NEW)
│   ├── doctor_detail.html         # Doctor profile (NEW)
│   ├── book_appointment.html      # Appointment booking (NEW)
│   └── my_appointments.html       # Appointments dashboard (NEW)
├── static/
│   ├── style.css                  # Original styles
│   └── [additional assets]
└── README.md                      # This file
```

---

## 🗄️ Database Schema

### Tables Created Automatically:

#### `users`
```sql
- id (PRIMARY KEY)
- username (UNIQUE)
- password_hash
- created_at
```

#### `predictions`
```sql
- id (PRIMARY KEY)
- created_at
- age, sex, cp, trestbps, chol, fbs, restecg
- thalach, exang, oldpeak, slope, ca, thal
- prediction (0 or 1)
- proba (confidence score)
```

#### `doctors` (NEW)
```sql
- id (PRIMARY KEY)
- name, specialization, experience_years
- qualifications, rating, total_reviews
- consultation_fee, availability
- bio, image_url, created_at
```

#### `appointments` (NEW)
```sql
- id (PRIMARY KEY)
- user_id, doctor_id (FOREIGN KEYS)
- appointment_date, appointment_time
- status (scheduled/completed/cancelled)
- notes, created_at
```

#### `consultation_reviews` (NEW)
```sql
- id (PRIMARY KEY)
- appointment_id, user_id, doctor_id
- rating (1-5), review_text, created_at
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Flask
- sqlite3
- numpy
- scikit-learn (if retraining model)
- reportlab (PDF generation)

### Installation

1. **Clone/Extract the project**
   ```bash
   cd "AK MINI PROJECT"
   ```

2. **Install dependencies**
   ```bash
   pip install flask numpy scikit-learn reportlab
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open browser and go to: `http://localhost:5000`
   - Default Flask runs on port 5000

---

## 📖 Usage Guide

### For Patients

#### 1. Register & Login
- Click "Register" on home page
- Create account with username and password
- Login with credentials

#### 2. Heart Disease Prediction
- Navigate to "Predict" or "Try Predictor"
- Fill in clinical parameters
- Submit form
- View real-time prediction with confidence score
- Download PDF report

#### 3. Doctor Consultation
- Click "Doctors" or "Consult Doctors"
- Browse available doctors
- Use filters to find specialists
- Click doctor card for detailed profile
- Click "Book Appointment" to schedule consultation
- Select date and time
- Add optional notes about your symptoms
- Confirm booking

#### 4. Manage Appointments
- Go to "Appointments" page
- View upcoming, completed, and cancelled appointments
- Cancel appointments (24-hour policy)
- Join video calls 5 minutes before scheduled time
- Leave reviews after consultation

### For Admin
- View prediction logs with full history
- Monitor all user predictions and trends
- Verify appointment bookings and cancellations

---

## 🎨 Design Features

### Modern UI/UX
- Gradient backgrounds and smooth animations
- Responsive design (mobile, tablet, desktop)
- Practo-inspired doctor cards with ratings
- Bootstrap 5 for responsive layouts
- Google Fonts (Poppins) for typography

### Dynamic Elements
- Real-time search and filtering
- Interactive time slot selection
- Status badges for appointment states
- Animated navbar with typing effect
- Smooth transitions and hover effects

### Color Scheme
- Primary Blue: #2563eb
- Primary Red: #d63031
- Light Gray: #f5f7fa
- Success: #10b981
- Warning: #f59e0b

---

## 🔐 Security Features

1. **Password Hashing**: Werkzeug security
2. **Session Management**: Secure Flask sessions
3. **Login Required**: Decorator for protected routes
4. **CSRF Protection**: Flask built-in protection
5. **Database Transactions**: Atomic operations

---

## 📊 API Routes

### Authentication Routes
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Prediction Routes
- `GET /predict_form` - Show prediction form
- `POST /predict` - Process prediction
- `GET /download_pdf` - Download PDF report
- `GET /logs` - View prediction logs

### Doctor Routes (NEW)
- `GET /doctors` - List all doctors with search/filter
- `GET /doctor/<id>` - View doctor details and reviews
- `GET/POST /book_appointment/<id>` - Book appointment
- `GET /my_appointments` - View user's appointments
- `POST /cancel_appointment/<id>` - Cancel appointment
- `GET /api/doctor_availability/<id>` - Get time slots (AJAX)

### Home & Navigation
- `GET /` - Landing page

---

## 🎓 Sample Doctor Data

The system auto-populates with 5 sample doctors:

1. **Dr. Rajesh Kumar** - Cardiologist (4.8★, 125 reviews)
2. **Dr. Priya Sharma** - General Physician (4.7★, 98 reviews)
3. **Dr. Amit Patel** - Cardiologist (4.9★, 156 reviews)
4. **Dr. Sneha Desai** - Nutritionist (4.6★, 87 reviews)
5. **Dr. Vikram Singh** - General Physician (4.8★, 203 reviews)

---

## ⚙️ Configuration

### Flask Settings
```python
app.secret_key = "change_this_to_a_random_secret_key"  # ⚠️ Change in production
app.run(debug=True)  # Set to False in production
```

### Model File
- Location: `heart-disease-prediction-knn-model.pkl`
- Type: Pickled scikit-learn KNN classifier
- Generated by: `train_model.py`

### Database
- Location: `heart_predictions.db`
- Type: SQLite3
- Auto-created on first run

---

## 🔧 Troubleshooting

### Issue: "Model file not found"
**Solution**: Ensure `heart-disease-prediction-knn-model.pkl` exists in project root

### Issue: "Database locked"
**Solution**: Close all connections and delete `heart_predictions.db`, it will regenerate

### Issue: Port 5000 already in use
**Solution**: Change port in app.py:
```python
app.run(debug=True, port=5001)
```

### Issue: Appointments not saving
**Solution**: Check database permissions in project folder

---

## 📝 Notes & Disclaimers

⚠️ **IMPORTANT DISCLAIMERS**

1. **Medical**: This application is for **EDUCATIONAL PURPOSES ONLY**
   - Predictions are not medical diagnoses
   - Do NOT use as a substitute for professional medical advice
   - Always consult qualified healthcare professionals

2. **Data**: Cleveland Heart Disease Dataset
   - Historical data from 1980s-1990s
   - May not reflect current populations
   - Trained on ~300 samples

3. **Model Accuracy**: KNN Model
   - Accuracy varies with test data
   - Use calibration carefully
   - Cross-validation recommended

4. **Video Calls**: Feature is placeholder
   - Integration requires video platform (Jitsi, Zoom API, etc.)
   - Currently shows mock confirmation

---

## 🚀 Future Enhancements

- [ ] Real video conferencing integration (Jitsi/Zoom)
- [ ] Email notifications for appointments
- [ ] Payment gateway integration
- [ ] Prescription management
- [ ] Medical records storage
- [ ] Doctor availability calendar
- [ ] Appointment reminders (SMS/Email)
- [ ] Review rating system
- [ ] Multi-language support
- [ ] Admin panel for doctor management
- [ ] Advanced analytics dashboard
- [ ] Telemedicine features

---

## 👨‍💼 Credits

- **Framework**: Flask
- **ML Library**: scikit-learn
- **Frontend**: Bootstrap 5
- **Icons & Fonts**: Google Fonts, Unicode
- **Database**: SQLite3
- **Dataset**: Cleveland Heart Disease

---

## 📄 License

Educational Project - Free to modify and use

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Verify all dependencies are installed
3. Ensure database file has proper permissions
4. Check terminal for error messages

---

## 🎉 Happy Consulting!

The platform is ready to use. Register, explore doctor profiles, book consultations, and get heart disease predictions!

**Start by visiting**: `http://localhost:5000`

---

*Last Updated: November 2025*
*Version: 2.0 (With Doctor Consultation)*
