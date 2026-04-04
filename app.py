from flask import Flask, request, jsonify, session, send_from_directory, g
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import secrets
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = secrets.token_hex(16)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DATABASE_URL)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create tables
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS bookings (
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
            booked_at TIMESTAMP NOT NULL
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS passengers (
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
        )''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email').lower()
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({'error': 'All fields required'}), 400

        db = get_db()
        cur = db.cursor()
        
        cur.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                   (name, email, password))
        db.commit()
        cur.close()
        return jsonify({'message': 'Registration successful'})
    except psycopg2.IntegrityError:
        db.rollback()
        return jsonify({'error': 'Email already registered'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email').lower()
        password = data.get('password')

        db = get_db()
        cur = db.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM users WHERE email = %s AND password = %s',
                  (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user'] = email
            return jsonify({'message': 'Login successful', 'user': email})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out'})

@app.route('/api/status', methods=['GET'])
def status():
    if 'user' in session:
        return jsonify({'user': session['user']})
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/flights', methods=['GET'])
def get_flights():
    # Realistic flight data with airlines
    flights = [
        {
            'flight_number': 'AI 101',
            'airline': 'Air India',
            'from': 'Delhi',
            'to': 'Mumbai',
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
            'departure': '15:00',
            'arrival': '17:30',
            'duration': '2h 30m',
            'price': 2800,
            'class': 'Economy'
        },
        {
            'flight_number': 'AI 201',
            'airline': 'Air India',
            'from': 'Chennai',
            'to': 'Mumbai',
            'date': '2026-03-27',
            'departure': '07:00',
            'arrival': '09:00',
            'duration': '2h 0m',
            'price': 2400,
            'class': 'Economy'
        },
        {
            'flight_number': '6E 601',
            'airline': 'IndiGo',
            'from': 'Chennai',
            'to': 'Mumbai',
            'date': '2026-03-27',
            'departure': '12:00',
            'arrival': '14:00',
            'duration': '2h 0m',
            'price': 2600,
            'class': 'Economy'
        },
        {
            'flight_number': 'UK 901',
            'airline': 'Vistara',
            'from': 'Chennai',
            'to': 'Delhi',
            'date': '2026-03-27',
            'departure': '08:00',
            'arrival': '10:30',
            'duration': '2h 30m',
            'price': 3500,
            'class': 'Economy'
        },
        {
            'flight_number': 'SG 401',
            'airline': 'SpiceJet',
            'from': 'Hyderabad',
            'to': 'Bangalore',
            'date': '2026-03-27',
            'departure': '10:00',
            'arrival': '11:00',
            'duration': '1h 0m',
            'price': 1800,
            'class': 'Economy'
        },
        {
            'flight_number': 'AI 301',
            'airline': 'Air India',
            'from': 'Chennai',
            'to': 'Mumbai',
            'date': '2026-03-26',
            'departure': '07:00',
            'arrival': '09:00',
            'duration': '2h 0m',
            'price': 2400,
            'class': 'Economy'
        },
        {
            'flight_number': '6E 701',
            'airline': 'IndiGo',
            'from': 'Delhi',
            'to': 'Mumbai',
            'date': '2026-03-26',
            'departure': '08:00',
            'arrival': '10:00',
            'duration': '2h 0m',
            'price': 2500,
            'class': 'Economy'
        },
        {
            'flight_number': 'SQ 501',
            'airline': 'Singapore Airlines',
            'from': 'Delhi',
            'to': 'Singapore',
            'date': '2026-03-27',
            'departure': '22:00',
            'arrival': '08:00',
            'duration': '6h 0m',
            'price': 15000,
            'class': 'Economy'
        }
    ]
    return jsonify(flights)

@app.route('/api/book', methods=['POST'])
def book_ticket():
    try:
        if 'user' not in session:
            return jsonify({'error': 'Not logged in'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        
        passengers = data.get('passengers')
        from_city = data.get('from')
        to_city = data.get('to')
        travel_date = data.get('date')
        travel_class = data.get('class')
        base_fare = data.get('base')
        tax = data.get('tax')
        total_fare = data.get('total')

        if not all([passengers, from_city, to_city, travel_date, travel_class, base_fare, tax, total_fare]):
            return jsonify({'error': 'All fields required'}), 400

        if not isinstance(passengers, list) or len(passengers) == 0:
            return jsonify({'error': 'Passengers required'}), 400

        # Validate passengers
        for p in passengers:
            if not all([p.get('name'), p.get('phone'), p.get('aadhar'), p.get('address')]):
                return jsonify({'error': 'All passenger details required'}), 400
            if not p['aadhar'].isdigit() or len(p['aadhar']) != 12:
                return jsonify({'error': 'Invalid Aadhar number. Must be 12 digits'}), 400

        ticket_id = f"ARS{secrets.randbelow(900000) + 100000}"
        booked_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Insert booking and get ID
        cursor.execute('''INSERT INTO bookings (ticket_id, user_email, from_city, to_city, travel_date, travel_class, base_fare, tax, total_fare, booked_at)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                          RETURNING id''',
                       (ticket_id, session['user'], from_city, to_city, travel_date, travel_class, base_fare, tax, total_fare, booked_at))
        booking_result = cursor.fetchone()
        booking_id = booking_result['id']

        # Insert passengers
        for p in passengers:
            cursor.execute('''INSERT INTO passengers (booking_id, name, phone, aadhar_number, aadhar_file, address, passport_number, passport_file, visa_required, visa_file)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (booking_id, p['name'], p['phone'], p['aadhar'], p.get('aadhar_file', ''), p['address'], 
                            p.get('passport', ''), p.get('passport_file', ''), p.get('visa_required', False), p.get('visa_file', '')))

        db.commit()
        cursor.close()

        return jsonify({'message': 'Booking successful', 'ticket_id': ticket_id})
    except psycopg2.IntegrityError as e:
        db.rollback()
        cursor.close()
        return jsonify({'error': 'Booking error - possible duplicate'}), 400
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Get bookings with passenger names aggregated
        cursor.execute('''SELECT b.*, STRING_AGG(p.name, '; ' ORDER BY p.id) as passenger_names
                         FROM bookings b
                         LEFT JOIN passengers p ON b.id = p.booking_id
                         WHERE b.user_email = %s
                         GROUP BY b.id
                         ORDER BY b.booked_at DESC''',
                      (session['user'],))
        bookings_rows = cursor.fetchall()

        result = []
        for booking in bookings_rows:
            booking_dict = dict(booking)
            # Get full passenger details for each booking
            cursor.execute('SELECT * FROM passengers WHERE booking_id = %s ORDER BY id',
                          (booking_dict['id'],))
            passengers = cursor.fetchall()
            booking_dict['passengers'] = [dict(p) for p in passengers]
            result.append(booking_dict)
        
        cursor.close()
        return jsonify(result)
    except Exception as e:
        cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/booking/<ticket_id>', methods=['DELETE'])
def cancel_booking(ticket_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Get booking id and verify it belongs to user
        cursor.execute('SELECT id FROM bookings WHERE ticket_id = %s AND user_email = %s',
                       (ticket_id, session['user']))
        booking = cursor.fetchone()
        
        if not booking:
            cursor.close()
            return jsonify({'error': 'Booking not found'}), 404

        # Delete booking (passengers will auto-delete via ON DELETE CASCADE)
        cursor.execute('DELETE FROM bookings WHERE ticket_id = %s AND user_email = %s',
                       (ticket_id, session['user']))
        
        db.commit()
        cursor.close()

        return jsonify({'message': 'Booking cancelled'})
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'Phone number required'}), 400
    # Mock OTP sending
    otp = '123456'  # In real app, send SMS
    session['otp'] = otp
    session['otp_phone'] = phone
    return jsonify({'message': 'OTP sent to ' + phone})

@app.route('/api/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp = data.get('otp')
    if session.get('otp') == otp and session.get('otp_phone') == data.get('phone'):
        session.pop('otp', None)
        session.pop('otp_phone', None)
        return jsonify({'message': 'OTP verified'})
    return jsonify({'error': 'Invalid OTP'}), 400

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{secrets.token_hex(8)}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return jsonify({'filename': unique_filename, 'path': file_path})
    return jsonify({'error': 'Invalid file type'}), 400

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    if filename in ['login.html', 'register.html', 'reservation.html', 'confirm.html', 'mybookings.html', 'flight_confirm.html']:
        return send_from_directory('.', filename)
    elif filename.startswith('css/'):
        return send_from_directory('css', filename[4:])
    elif filename.startswith('js/'):
        return send_from_directory('js', filename[3:])
    elif filename.startswith('images/'):
        return send_from_directory('images', filename[7:])
    return send_from_directory('.', filename)

if __name__ == '__main__':
    init_db()
    from flask import Flask, request, jsonify, session, send_from_directory, g
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import secrets
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = secrets.token_hex(16)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DATABASE_URL)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create tables
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS bookings (
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
            booked_at TIMESTAMP NOT NULL
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS passengers (
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
        )''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email').lower()
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({'error': 'All fields required'}), 400

        db = get_db()
        cur = db.cursor()
        
        cur.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                   (name, email, password))
        db.commit()
        cur.close()
        return jsonify({'message': 'Registration successful'})
    except psycopg2.IntegrityError:
        db.rollback()
        return jsonify({'error': 'Email already registered'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email').lower()
        password = data.get('password')

        db = get_db()
        cur = db.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM users WHERE email = %s AND password = %s',
                  (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user'] = email
            return jsonify({'message': 'Login successful', 'user': email})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out'})

@app.route('/api/status', methods=['GET'])
def status():
    if 'user' in session:
        return jsonify({'user': session['user']})
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/flights', methods=['GET'])
def get_flights():
    # Realistic flight data with airlines
    flights = [
        {
            'flight_number': 'AI 101',
            'airline': 'Air India',
            'from': 'Delhi',
            'to': 'Mumbai',
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
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
            'date': '2026-03-27',
            'departure': '15:00',
            'arrival': '17:30',
            'duration': '2h 30m',
            'price': 2800,
            'class': 'Economy'
        },
        {
            'flight_number': 'AI 201',
            'airline': 'Air India',
            'from': 'Chennai',
            'to': 'Mumbai',
            'date': '2026-03-27',
            'departure': '07:00',
            'arrival': '09:00',
            'duration': '2h 0m',
            'price': 2400,
            'class': 'Economy'
        },
        {
            'flight_number': '6E 601',
            'airline': 'IndiGo',
            'from': 'Chennai',
            'to': 'Mumbai',
            'date': '2026-03-27',
            'departure': '12:00',
            'arrival': '14:00',
            'duration': '2h 0m',
            'price': 2600,
            'class': 'Economy'
        },
        {
            'flight_number': 'UK 901',
            'airline': 'Vistara',
            'from': 'Chennai',
            'to': 'Delhi',
            'date': '2026-03-27',
            'departure': '08:00',
            'arrival': '10:30',
            'duration': '2h 30m',
            'price': 3500,
            'class': 'Economy'
        },
        {
            'flight_number': 'SG 401',
            'airline': 'SpiceJet',
            'from': 'Hyderabad',
            'to': 'Bangalore',
            'date': '2026-03-27',
            'departure': '10:00',
            'arrival': '11:00',
            'duration': '1h 0m',
            'price': 1800,
            'class': 'Economy'
        },
        {
            'flight_number': 'AI 301',
            'airline': 'Air India',
            'from': 'Chennai',
            'to': 'Mumbai',
            'date': '2026-03-26',
            'departure': '07:00',
            'arrival': '09:00',
            'duration': '2h 0m',
            'price': 2400,
            'class': 'Economy'
        },
        {
            'flight_number': '6E 701',
            'airline': 'IndiGo',
            'from': 'Delhi',
            'to': 'Mumbai',
            'date': '2026-03-26',
            'departure': '08:00',
            'arrival': '10:00',
            'duration': '2h 0m',
            'price': 2500,
            'class': 'Economy'
        },
        {
            'flight_number': 'SQ 501',
            'airline': 'Singapore Airlines',
            'from': 'Delhi',
            'to': 'Singapore',
            'date': '2026-03-27',
            'departure': '22:00',
            'arrival': '08:00',
            'duration': '6h 0m',
            'price': 15000,
            'class': 'Economy'
        }
    ]
    return jsonify(flights)

@app.route('/api/book', methods=['POST'])
def book_ticket():
    try:
        if 'user' not in session:
            return jsonify({'error': 'Not logged in'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        
        passengers = data.get('passengers')
        from_city = data.get('from')
        to_city = data.get('to')
        travel_date = data.get('date')
        travel_class = data.get('class')
        base_fare = data.get('base')
        tax = data.get('tax')
        total_fare = data.get('total')

        if not all([passengers, from_city, to_city, travel_date, travel_class, base_fare, tax, total_fare]):
            return jsonify({'error': 'All fields required'}), 400

        if not isinstance(passengers, list) or len(passengers) == 0:
            return jsonify({'error': 'Passengers required'}), 400

        # Validate passengers
        for p in passengers:
            if not all([p.get('name'), p.get('phone'), p.get('aadhar'), p.get('address')]):
                return jsonify({'error': 'All passenger details required'}), 400
            if not p['aadhar'].isdigit() or len(p['aadhar']) != 12:
                return jsonify({'error': 'Invalid Aadhar number. Must be 12 digits'}), 400

        ticket_id = f"ARS{secrets.randbelow(900000) + 100000}"
        booked_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Insert booking and get ID
        cursor.execute('''INSERT INTO bookings (ticket_id, user_email, from_city, to_city, travel_date, travel_class, base_fare, tax, total_fare, booked_at)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                          RETURNING id''',
                       (ticket_id, session['user'], from_city, to_city, travel_date, travel_class, base_fare, tax, total_fare, booked_at))
        booking_result = cursor.fetchone()
        booking_id = booking_result['id']

        # Insert passengers
        for p in passengers:
            cursor.execute('''INSERT INTO passengers (booking_id, name, phone, aadhar_number, aadhar_file, address, passport_number, passport_file, visa_required, visa_file)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (booking_id, p['name'], p['phone'], p['aadhar'], p.get('aadhar_file', ''), p['address'], 
                            p.get('passport', ''), p.get('passport_file', ''), p.get('visa_required', False), p.get('visa_file', '')))

        db.commit()
        cursor.close()

        return jsonify({'message': 'Booking successful', 'ticket_id': ticket_id})
    except psycopg2.IntegrityError as e:
        db.rollback()
        cursor.close()
        return jsonify({'error': 'Booking error - possible duplicate'}), 400
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Get bookings with passenger names aggregated
        cursor.execute('''SELECT b.*, STRING_AGG(p.name, '; ' ORDER BY p.id) as passenger_names
                         FROM bookings b
                         LEFT JOIN passengers p ON b.id = p.booking_id
                         WHERE b.user_email = %s
                         GROUP BY b.id
                         ORDER BY b.booked_at DESC''',
                      (session['user'],))
        bookings_rows = cursor.fetchall()

        result = []
        for booking in bookings_rows:
            booking_dict = dict(booking)
            # Get full passenger details for each booking
            cursor.execute('SELECT * FROM passengers WHERE booking_id = %s ORDER BY id',
                          (booking_dict['id'],))
            passengers = cursor.fetchall()
            booking_dict['passengers'] = [dict(p) for p in passengers]
            result.append(booking_dict)
        
        cursor.close()
        return jsonify(result)
    except Exception as e:
        cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/booking/<ticket_id>', methods=['DELETE'])
def cancel_booking(ticket_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Get booking id and verify it belongs to user
        cursor.execute('SELECT id FROM bookings WHERE ticket_id = %s AND user_email = %s',
                       (ticket_id, session['user']))
        booking = cursor.fetchone()
        
        if not booking:
            cursor.close()
            return jsonify({'error': 'Booking not found'}), 404

        # Delete booking (passengers will auto-delete via ON DELETE CASCADE)
        cursor.execute('DELETE FROM bookings WHERE ticket_id = %s AND user_email = %s',
                       (ticket_id, session['user']))
        
        db.commit()
        cursor.close()

        return jsonify({'message': 'Booking cancelled'})
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'Phone number required'}), 400
    # Mock OTP sending
    otp = '123456'  # In real app, send SMS
    session['otp'] = otp
    session['otp_phone'] = phone
    return jsonify({'message': 'OTP sent to ' + phone})

@app.route('/api/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp = data.get('otp')
    if session.get('otp') == otp and session.get('otp_phone') == data.get('phone'):
        session.pop('otp', None)
        session.pop('otp_phone', None)
        return jsonify({'message': 'OTP verified'})
    return jsonify({'error': 'Invalid OTP'}), 400

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{secrets.token_hex(8)}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return jsonify({'filename': unique_filename, 'path': file_path})
    return jsonify({'error': 'Invalid file type'}), 400

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    if filename in ['login.html', 'register.html', 'reservation.html', 'confirm.html', 'mybookings.html', 'flight_confirm.html']:
        return send_from_directory('.', filename)
    elif filename.startswith('css/'):
        return send_from_directory('css', filename[4:])
    elif filename.startswith('js/'):
        return send_from_directory('js', filename[3:])
    elif filename.startswith('images/'):
        return send_from_directory('images', filename[7:])
    return send_from_directory('.', filename)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
