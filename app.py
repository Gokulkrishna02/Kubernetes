from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import secrets

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = secrets.token_hex(16)

DATABASE = 'airline.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS bookings (
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
        )''')
        db.commit()

init_db()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email').lower()
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'All fields required'}), 400

    db = get_db()
    try:
        db.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                   (name, email, password))
        db.commit()
        return jsonify({'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email').lower()
    password = data.get('password')

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                      (email, password)).fetchone()

    if user:
        session['user'] = email
        return jsonify({'message': 'Login successful', 'user': email})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out'})

@app.route('/api/flights', methods=['GET'])
def get_flights():
    # Realistic flight data with airlines
    flights = [
        {
            'flight_number': 'AI 101',
            'airline': 'Air India',
            'from': 'Delhi',
            'to': 'Mumbai',
            'date': '2024-12-01',
            'departure': '06:00',
            'arrival': '08:00',
            'duration': '2h 0m',
            'price': 2500,
            'class': 'Economy'
        },
        {
            'flight_number': 'AI 102',
            'airline': 'Air India',
            'from': 'Delhi',
            'to': 'Mumbai',
            'date': '2024-12-01',
            'departure': '14:00',
            'arrival': '16:00',
            'duration': '2h 0m',
            'price': 2800,
            'class': 'Economy'
        },
        {
            'flight_number': '6E 501',
            'airline': 'IndiGo',
            'from': 'Delhi',
            'to': 'Bangalore',
            'date': '2024-12-01',
            'departure': '08:00',
            'arrival': '10:30',
            'duration': '2h 30m',
            'price': 3000,
            'class': 'Economy'
        },
        {
            'flight_number': '6E 502',
            'airline': 'IndiGo',
            'from': 'Delhi',
            'to': 'Bangalore',
            'date': '2024-12-01',
            'departure': '18:00',
            'arrival': '20:30',
            'duration': '2h 30m',
            'price': 3200,
            'class': 'Economy'
        },
        {
            'flight_number': 'UK 801',
            'airline': 'Vistara',
            'from': 'Mumbai',
            'to': 'Delhi',
            'date': '2024-12-01',
            'departure': '09:00',
            'arrival': '11:00',
            'duration': '2h 0m',
            'price': 2700,
            'class': 'Economy'
        },
        {
            'flight_number': 'UK 802',
            'airline': 'Vistara',
            'from': 'Mumbai',
            'to': 'Delhi',
            'date': '2024-12-01',
            'departure': '16:00',
            'arrival': '18:00',
            'duration': '2h 0m',
            'price': 2900,
            'class': 'Economy'
        },
        {
            'flight_number': 'SG 301',
            'airline': 'SpiceJet',
            'from': 'Bangalore',
            'to': 'Delhi',
            'date': '2024-12-01',
            'departure': '07:00',
            'arrival': '09:30',
            'duration': '2h 30m',
            'price': 2600,
            'class': 'Economy'
        },
        {
            'flight_number': 'SG 302',
            'airline': 'SpiceJet',
            'from': 'Bangalore',
            'to': 'Delhi',
            'date': '2024-12-01',
            'departure': '15:00',
            'arrival': '17:30',
            'duration': '2h 30m',
            'price': 2800,
            'class': 'Economy'
        }
    ]
    return jsonify(flights)

@app.route('/api/book', methods=['POST'])
def book_ticket():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    passenger_name = data.get('passenger_name')
    phone = data.get('phone')
    aadhar_number = data.get('aadhar_number')
    address = data.get('address')
    from_city = data.get('from')
    to_city = data.get('to')
    travel_date = data.get('date')
    seats = data.get('seats')
    travel_class = data.get('class')
    base_fare = data.get('base')
    tax = data.get('tax')
    total_fare = data.get('total')

    if not all([passenger_name, phone, aadhar_number, address, from_city, to_city, travel_date, seats, travel_class, base_fare, tax, total_fare]):
        return jsonify({'error': 'All fields required'}), 400

    # Validate Aadhar number (12 digits)
    if not aadhar_number.isdigit() or len(aadhar_number) != 12:
        return jsonify({'error': 'Invalid Aadhar number. Must be 12 digits'}), 400

    ticket_id = f"ARS{secrets.randbelow(900000) + 100000}"
    booked_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db = get_db()
    db.execute('''INSERT INTO bookings (ticket_id, user_email, passenger_name, phone, aadhar_number, address,
                   from_city, to_city, travel_date, seats, travel_class, base_fare, tax, total_fare, booked_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
               (ticket_id, session['user'], passenger_name, phone, aadhar_number, address,
                from_city, to_city, travel_date, seats, travel_class, base_fare, tax, total_fare, booked_at))
    db.commit()

    return jsonify({'message': 'Booking successful', 'ticket_id': ticket_id})

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    db = get_db()
    bookings = db.execute('SELECT * FROM bookings WHERE user_email = ? ORDER BY booked_at DESC',
                          (session['user'],)).fetchall()

    result = [dict(row) for row in bookings]
    return jsonify(result)

@app.route('/api/booking/<ticket_id>', methods=['DELETE'])
def cancel_booking(ticket_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    db = get_db()
    db.execute('DELETE FROM bookings WHERE ticket_id = ? AND user_email = ?',
               (ticket_id, session['user']))
    db.commit()

    return jsonify({'message': 'Booking cancelled'})

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    if filename in ['login.html', 'register.html', 'reservation.html', 'confirm.html', 'mybookings.html']:
        return send_from_directory('.', filename)
    elif filename.startswith('css/'):
        return send_from_directory('css', filename[4:])
    elif filename.startswith('js/'):
        return send_from_directory('js', filename[3:])
    elif filename.startswith('images/'):
        return send_from_directory('images', filename[7:])
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)