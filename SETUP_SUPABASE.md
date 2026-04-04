# Airline Reservation System - Supabase Setup Guide

## Step 1: Create Supabase Account
1. Go to https://supabase.com
2. Click "Start your project for free"
3. Sign up with email or GitHub
4. Create a new project

## Step 2: Get Your Database Connection String
1. In Supabase Dashboard, go to **Project Settings** → **Database**
2. Copy the **Connection String** (URI format)
3. It will look like: `postgresql://postgres:password@host:5432/postgres`

## Step 3: Create .env File
Create a `.env` file in the `Airline-Reservation-System` folder with:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_HOST.supabase.co:5432/postgres
```

## Step 4: Install Dependencies
```bash
cd Airline-Reservation-System
pip install -r requirements.txt
```

## Step 5: Initialize Database (Run SQL in Supabase)
1. Go to Supabase Dashboard → **SQL Editor**
2. Click **New Query**
3. Paste this SQL and run it:

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) UNIQUE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    from_city VARCHAR(100) NOT NULL,
    to_city VARCHAR(100) NOT NULL,
    travel_date DATE NOT NULL,
    travel_class VARCHAR(50) NOT NULL,
    base_fare INTEGER NOT NULL,
    tax INTEGER NOT NULL,
    total_fare INTEGER NOT NULL,
    booked_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS passengers (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    aadhar_number VARCHAR(12) NOT NULL,
    aadhar_file VARCHAR(255),
    address TEXT NOT NULL,
    passport_number VARCHAR(50),
    passport_file VARCHAR(255),
    visa_required BOOLEAN DEFAULT FALSE,
    visa_file VARCHAR(255),
    FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE
);

CREATE INDEX idx_user_email ON bookings(user_email);
CREATE INDEX idx_ticket_id ON bookings(ticket_id);
```

## Step 6: Start the App
```bash
python app.py
```

The app will run at `http://localhost:5000`

## Notes
- All sensitive data is in `.env` (don't commit it to git!)
- File uploads are still saved in the `uploads/` folder locally
- For production, upload files to Supabase Storage

## Troubleshooting

### "Failed to connect to database"
- Check DATABASE_URL in .env
- Ensure Supabase project is active
- Check network connection

### "relation does not exist"
- Run the SQL setup queries in Supabase SQL Editor
- Verify table names match exactly

### IntegrityError on register
- Email already exists in database
- User should try a different email
