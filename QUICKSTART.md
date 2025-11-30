# QUICK START GUIDE - AK Health Platform

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Python Packages
```bash
cd "c:\Users\RaghuKote\Desktop\AK MINI PROJECT"
pip install flask numpy scikit-learn reportlab werkzeug
```

### Step 2: Run the Application
```bash
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 3: Open in Browser
Go to: **http://localhost:5000**

---

## 📝 First-Time User Steps

### 1. Register Account
- Click "Register" button
- Enter username (e.g., `john_doe`)
- Enter password (min 4 characters)
- Confirm password
- Click "Register"

### 2. Login
- Click "Login"
- Enter your credentials
- Click "Login"

### 3. Try Heart Disease Predictor
- Click "Try Predictor" button
- Fill in sample data:
  ```
  Age: 45
  Sex: Male
  Chest Pain Type: Typical Angina
  Resting BP: 130
  Cholesterol: 250
  Fasting Blood Sugar: > 120
  Resting ECG: Normal
  Max Heart Rate: 150
  Exercise Induced Angina: No
  ST Depression: 1.0
  Slope: Upsloping
  Major Vessels: 0
  Thalassemia: Normal
  ```
- Click "Predict"
- Download PDF report if desired

### 4. Explore Doctor Consultation
- Click "Doctors" or "Consult Doctors"
- Browse the list of 5 sample doctors
- Use filters to sort by:
  - Specialization (Cardiologist, General Physician, Nutritionist)
  - Rating (4.5+, 4.0+)
  - Consultation Fee
- Click on a doctor card to see full profile
- Click "Book Appointment"

### 5. Book an Appointment
- Select appointment date (within 30 days)
- Choose time slot (10:00 AM - 5:00 PM)
- Add optional notes about your health
- Click "Confirm Booking"
- View appointment confirmation

### 6. Manage Appointments
- Click "Appointments" from navbar
- View all your appointments organized by status:
  - **Upcoming**: Scheduled consultations (with join button)
  - **Completed**: Finished consultations (with review option)
  - **Cancelled**: Cancelled bookings (with rebook option)
- Cancel any upcoming appointment (24-hour policy)

### 7. View Prediction History
- Click "Logs" to see all your predictions
- View detailed history of all past predictions

---

## 🎨 Features Overview

| Feature | Access | Details |
|---------|--------|---------|
| **Heart Disease Prediction** | Menu → Predict | AI-powered prediction with 13 parameters |
| **Doctor Search** | Menu → Doctors | Browse & filter 5 sample doctors |
| **Book Appointment** | Doctor Page → Book | Dynamic date/time selection |
| **My Appointments** | Menu → Appointments | Manage all consultations |
| **Prediction History** | Menu → Logs | View all past predictions |
| **PDF Reports** | Results Page → Download | Generate detailed reports |

---

## 🔑 Sample Login Credentials

After registration, you can log back in anytime with your credentials.

**Example**:
- Username: `testuser`
- Password: `test1234`

---

## 📊 Sample Data for Testing

### Doctor Data (Pre-populated)
- Dr. Rajesh Kumar (Cardiologist, ₹800/consultation)
- Dr. Priya Sharma (General Physician, ₹500/consultation)
- Dr. Amit Patel (Cardiologist, ₹750/consultation)
- Dr. Sneha Desai (Nutritionist, ₹400/consultation)
- Dr. Vikram Singh (General Physician, ₹600/consultation)

### Prediction Test Cases

**Case 1 - Low Risk**:
- Age: 35, Sex: Female, Chest Pain: Asymptomatic
- BP: 110, Cholesterol: 180, FBS: ≤120
- Max Heart Rate: 160, ST Depression: 0.1

**Case 2 - High Risk**:
- Age: 60, Sex: Male, Chest Pain: Typical Angina
- BP: 150, Cholesterol: 300, FBS: >120
- Max Heart Rate: 100, ST Depression: 2.5

---

## 🛠️ Troubleshooting

### Problem: "Port 5000 already in use"
**Solution**:
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Problem: "Module not found" error
**Solution**:
```bash
# Reinstall all dependencies
pip install --upgrade flask numpy scikit-learn reportlab werkzeug
```

### Problem: Database is locked
**Solution**:
1. Close the Flask application (Ctrl+C)
2. Delete `heart_predictions.db` file
3. Restart the application (it will recreate the database)

### Problem: Can't access doctors.html
**Make sure you are logged in first!** Doctor features require authentication.

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Run Flask app
3. ✅ Register and login
4. ✅ Test heart disease prediction
5. ✅ Browse and book with doctors
6. ✅ View appointments and logs
7. 🎓 Explore the code and modify as needed

---

## 📱 Mobile Responsiveness

The platform is fully responsive:
- **Desktop**: Full feature access
- **Tablet**: Optimized layout
- **Mobile**: Touch-friendly interface

---

## ⚠️ Important Reminders

1. **Medical Disclaimer**: This is educational only, NOT a medical diagnosis tool
2. **Password Security**: Change the `app.secret_key` in production
3. **Database**: Automatic SQLite3 database in project folder
4. **Model**: Pre-trained KNN model included (`heart-disease-prediction-knn-model.pkl`)
5. **Video Calls**: Currently placeholder - integrate with actual platform as needed

---

## 📚 File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application with all routes |
| `train_model.py` | Script to retrain the ML model |
| `heart_cleveland_upload.csv` | Original dataset |
| `heart-disease-prediction-knn-model.pkl` | Trained ML model (binary) |
| `heart_predictions.db` | SQLite database (auto-created) |
| `templates/*.html` | HTML templates for all pages |
| `static/style.css` | CSS styling |

---

## 🎉 Enjoy!

Your AK Health Platform is ready to use. Have fun exploring heart disease predictions and booking doctor consultations!

**Questions?** Check the main `README.md` for detailed documentation.

---

*Generated: November 2025*
