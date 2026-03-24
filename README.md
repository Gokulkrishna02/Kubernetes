# 🛫 Airline Reservation System

A full-stack airline reservation and booking platform built with **Python Flask** backend and responsive **HTML5/CSS3/JavaScript** frontend. Features user authentication, flight search, real-time booking, and reservation management with SQLite database persistence.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Features](#features)
- [Docker Deployment](#docker-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Security Enhancements](#security-enhancements)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

The **Airline Reservation System** is a web application that allows users to:
- Register and create accounts securely
- Search and browse available flights
- Book airline tickets with passenger details
- Manage their bookings and cancel reservations
- View booking history and confirmations

Built for simplicity and scalability, the system uses session-based authentication and SQLite for data persistence.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.9+ with Flask |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Database** | SQLite (`airline.db`) |
| **Server** | Flask Built-in / Gunicorn (Production) |
| **CORS** | Flask-CORS |
| **Containerization** | Docker |
| **CI/CD** | Jenkins |

---

## 📁 Project Structure

```
Airline-Reservation-System/
├── app.py                      # Main Flask application & API routes
├── backend.py                  # Backend utilities & helpers
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration (Python)
├── Jenkinsfile                 # CI/CD Pipeline configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── templates/                  # HTML Templates
│   ├── index.html              # Landing page
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── reservation.html        # Flight search & booking
│   ├── mybookings.html         # User bookings
│   └── confirm.html            # Booking confirmation
│
├── static/                     # Static assets
│   ├── css/
│   │   ├── reset.css           # CSS reset
│   │   ├── layout.css          # Layout styles
│   │   └── style.css           # Main styling
│   ├── js/
│   │   └── script.js           # Frontend logic
│   └── images/                 # Image assets
```

---

## ⚙️ Prerequisites

- **Python 3.9+** installed
- **pip** (Python package manager)
- **Docker** (optional, for containerization)
- **Git** (for version control)

### Verify Installation
```bash
python --version      # Should be 3.9+
pip --version
docker --version      # Optional
```

---

## 💻 Installation & Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/GVanithasri/Airline-Reservation-System.git
cd Airline-Reservation-System
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
pip list
```

Expected packages:
- Flask
- Flask-CORS

---

## 🚀 Running the Application

### Development Mode
```bash
python app.py
```

Server runs at: **http://127.0.0.1:5000/**

### Production Mode (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Container
```bash
# Build image
docker build -t airline-res:latest .

# Run container
docker run -p 5000:5000 airline-res:latest

# Access at http://localhost:5000/
```

---

## 🔗 API Documentation

### Base URL
```
http://localhost:5000/api/
```

### Authentication Endpoints

#### 1. Register User
```http
POST /api/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "message": "Registration successful"
}
```

---

#### 2. Login User
```http
POST /api/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": "john@example.com"
}
```

---

#### 3. Logout User
```http
POST /api/logout
```

---

### Flight Endpoints

#### 4. Get Available Flights
```http
GET /api/flights
```

**Response:**
```json
[
  {
    "flight_number": "AI 101",
    "airline": "Air India",
    "from": "Delhi",
    "to": "Mumbai",
    "date": "2024-12-01",
    "departure": "06:00",
    "arrival": "08:00",
    "duration": "2h 0m",
    "price": 2500,
    "class": "Economy"
  }
]
```

---

### Booking Endpoints

#### 5. Create Booking
```http
POST /api/book
Content-Type: application/json

{
  "passenger_name": "John Doe",
  "phone": "+91-9876543210",
  "aadhar_number": "123456789012",
  "address": "123 Main Street, Delhi",
  "from": "Delhi",
  "to": "Mumbai",
  "date": "2024-12-01",
  "seats": 1,
  "class": "Economy",
  "base": 2500,
  "tax": 500,
  "total": 3000
}
```

---

#### 6. Get User Bookings
```http
GET /api/bookings
```

---

#### 7. Cancel Booking
```http
DELETE /api/booking/ARS456789
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    ticket_id TEXT UNIQUE NOT NULL,
    user_email TEXT NOT NULL,
    passenger_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    aadhar_number TEXT NOT NULL,
    address TEXT NOT NULL,
    from_city TEXT NOT NULL,
    to_city TEXT NOT NULL,
    travel_date TEXT NOT NULL,
    seats INTEGER NOT NULL,
    travel_class TEXT NOT NULL,
    base_fare INTEGER NOT NULL,
    tax INTEGER NOT NULL,
    total_fare INTEGER NOT NULL,
    booked_at TEXT NOT NULL
);
```

---

## ✨ Features

✅ User registration & login  
✅ Flight search & booking  
✅ View bookings  
✅ Cancel bookings  
✅ Session management  
✅ Input validation  
✅ Aadhar validation (12 digits)  
✅ CORS enabled  
✅ Unique ticket generation  

---

## 🐳 Docker

### Quick Commands
```bash
# Build
docker build -t airline-res:latest .

# Run
docker run -p 5000:5000 airline-res:latest

# Stop
docker stop <container_id>
```

---

## 🔄 CI/CD Pipeline (Jenkins)

### Jenkinsfile Stages
1. **Checkout** - Clone repository
2. **Setup Python** - Create virtual environment
3. **Code Quality** - Flake8 linting
4. **Unit Tests** - Pytest suite
5. **Security Scan** - Bandit analysis
6. **Build Docker** - Create container image
7. **Deploy Dev** - Deploy on develop branch
8. **Deploy Prod** - Deploy on main branch
9. **Cleanup** - Remove temporary files

### Setup Jenkins Job
1. Create New Pipeline Job
2. Configure Git repository
3. Select "Pipeline script from SCM"
4. Point to `Jenkinsfile`

---

## 🔒 Security Enhancements

### ⚠️ Current Approaches
- Passwords in plain text (consider bcrypt)
- Session-based auth (stateful)
- No HTTPS by default

### ✅ Recommended Improvements
1. Hash passwords with `werkzeug.security.generate_password_hash`
2. Add JWT for stateless auth
3. Implement HTTPS with reverse proxy
4. Add rate limiting
5. Input sanitization
6. SQL injection protection (use parameterized queries)

---

## 🚀 Future Enhancements

### Phase 2
- [ ] Payment gateway (Razorpay/Stripe)
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Seat selection UI

### Phase 3
- [ ] Admin dashboard
- [ ] Revenue analytics
- [ ] User management

### Phase 4
- [ ] Mobile app
- [ ] Caching (Redis)
- [ ] Multi-language support

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/YourFeature`
3. Commit: `git commit -m 'Add YourFeature'`
4. Push: `git push origin feature/YourFeature`
5. Open Pull Request

---

## 📝 License

MIT License - See LICENSE file

---

## 👨‍💼 Author

**GVanithasri**  
GitHub: [@GVanithasri](https://github.com/GVanithasri)

---

**Last Updated:** March 24, 2026  
**Version:** 1.0.0  
**Status:** Production Ready