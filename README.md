# Airline Reservation Backend

This is a Python Flask backend for an airline reservation system.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the server:
   ```
   python app.py
   ```

The server will run on http://127.0.0.1:5000/

## Access the Application

Open your web browser and go to: http://127.0.0.1:5000/

The Flask server now serves all static files (HTML, CSS, JS, images) and handles the API requests.

## API Endpoints

### Authentication
- `POST /api/register` - Register a new user
- `POST /api/login` - Login user
- `POST /api/logout` - Logout user

### Flights
- `GET /api/flights` - Get available flights

### Bookings
- `POST /api/book` - Create a new booking
- `GET /api/bookings` - Get user's bookings
- `DELETE /api/booking/<ticket_id>` - Cancel a booking

## Database

Uses SQLite database `airline.db` with tables:
- `users` - User accounts
- `bookings` - Flight bookings

## Features

- User registration and login with session management
- Flight search and booking
- View and cancel bookings
- Data persistence with SQLite
- CORS enabled for frontend integration