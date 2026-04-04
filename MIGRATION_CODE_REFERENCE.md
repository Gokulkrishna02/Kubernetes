# PostgreSQL Migration - Code Changes Reference

## Quick Summary of Changes

All SQL operations have been converted from SQLite to PostgreSQL syntax and are now using the psycopg2 driver with proper connection management.

---

## 1. /api/book Endpoint Changes

### Key Changes:
- ✅ Use `cursor_factory=RealDictCursor` 
- ✅ Change `?` placeholders to `%s`
- ✅ Use `RETURNING id` instead of `cursor.lastrowid`
- ✅ Add try-catch for `psycopg2.IntegrityError`
- ✅ Always call `cursor.close()` and `db.rollback()` on error

### Before (SQLite):
```python
cursor = db.cursor()
cursor.execute('INSERT INTO bookings VALUES (?, ?, ...)', (val1, val2, ...))
booking_id = cursor.lastrowid
```

### After (PostgreSQL):
```python
cursor = db.cursor(cursor_factory=RealDictCursor)
cursor.execute('INSERT INTO bookings VALUES (%s, %s, ...) RETURNING id', (val1, val2, ...))
booking_result = cursor.fetchone()
booking_id = booking_result['id']
```

---

## 2. /api/bookings Endpoint Changes

### Key Changes:
- ✅ Replace `GROUP_CONCAT(p.name, '; ')` with `STRING_AGG(p.name, '; ' ORDER BY p.id)`
- ✅ Use `%s` instead of `?`
- ✅ Use `cursor.fetchall()` instead of `db.execute().fetchall()`
- ✅ Convert rows to dict with `dict(row)` for RealDictCursor

### Before (SQLite):
```python
bookings = db.execute('''SELECT b.*, GROUP_CONCAT(p.name, '; ')
                         FROM bookings b
                         LEFT JOIN passengers p ON b.id = p.booking_id
                         WHERE b.user_email = ?''', (user,)).fetchall()
```

### After (PostgreSQL):
```python
cursor = db.cursor(cursor_factory=RealDictCursor)
cursor.execute('''SELECT b.*, STRING_AGG(p.name, '; ' ORDER BY p.id)
                  FROM bookings b
                  LEFT JOIN passengers p ON b.id = p.booking_id
                  WHERE b.user_email = %s
                  GROUP BY b.id''', (user,))
bookings = cursor.fetchall()
```

---

## 3. /api/booking/<id> DELETE Endpoint Changes

### Key Changes:
- ✅ Use `%s` instead of `?`
- ✅ Remove manual passenger deletion (cascading handled by FOREIGN KEY)
- ✅ Use `cursor.fetchone()` instead of `db.execute().fetchone()`
- ✅ Add error handling with try-catch

### Before (SQLite):
```python
booking = db.execute('SELECT id FROM bookings WHERE ticket_id = ? AND user_email = ?',
                     (ticket_id, user)).fetchone()
if not booking:
    return error
db.execute('DELETE FROM passengers WHERE booking_id = ?', (booking['id'],))
db.execute('DELETE FROM bookings WHERE ticket_id = ?', (ticket_id,))
db.commit()
```

### After (PostgreSQL):
```python
cursor = db.cursor(cursor_factory=RealDictCursor)
cursor.execute('SELECT id FROM bookings WHERE ticket_id = %s AND user_email = %s',
               (ticket_id, user))
booking = cursor.fetchone()
if not booking:
    cursor.close()
    return error

# No need to delete passengers - FOREIGN KEY handles it
cursor.execute('DELETE FROM bookings WHERE ticket_id = %s AND user_email = %s',
               (ticket_id, user))
db.commit()
cursor.close()
```

---

## Connection Management Pattern

All endpoints now follow this pattern:

```python
@app.route('/api/example', methods=['POST'])
def example():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Your SQL operations here
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        row = cursor.fetchone()
        
        # For INSERT/UPDATE/DELETE
        db.commit()
        cursor.close()
        
        return jsonify({'result': dict(row)})
    except psycopg2.IntegrityError:
        db.rollback()
        cursor.close()
        return jsonify({'error': 'Duplicate entry'}), 400
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500
```

---

## SQL Syntax Differences

| Operation | SQLite | PostgreSQL |
|-----------|--------|-----------|
| Placeholder | `?` | `%s` |
| Get last ID | `cursor.lastrowid` | `RETURNING id` clause |
| String concat | `GROUP_CONCAT(col, sep)` | `STRING_AGG(col, sep ORDER BY sort_col)` |
| Boolean | `0 / 1` | `FALSE / TRUE` |
| Cursor creation | `db.cursor()` | `db.cursor(cursor_factory=RealDictCursor)` |
| Get all rows | `.fetchall()` | `.fetchall()` |
| Get one row | `.fetchone()` | `.fetchone()` |

---

## Environment Configuration

Create `.env` file:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

In Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
```

---

## Testing Your Migration

1. **Test Connection:**
   ```bash
   python -c "import psycopg2; conn = psycopg2.connect(os.getenv('DATABASE_URL')); print('Connected!')"
   ```

2. **Test Register:**
   ```bash
   curl -X POST http://localhost:5000/api/register \
     -H "Content-Type: application/json" \
     -d '{"name":"John","email":"john@test.com","password":"pass123"}'
   ```

3. **Test Login:**
   ```bash
   curl -X POST http://localhost:5000/api/login \
     -H "Content-Type: application/json" \
     -d '{"email":"john@test.com","password":"pass123"}'
   ```

4. **Test Bookings:**
   ```bash
   curl http://localhost:5000/api/bookings
   ```

---

## Remaining Endpoints (No Changes Needed)

These endpoints don't interact with the database:
- `/api/flights` - Returns hardcoded list
- `/api/send_otp` - Uses session only
- `/api/verify_otp` - Uses session only  
- `/api/upload` - File handling only
- `/api/status` - Session check only

---

## Database Schema (PostgreSQL)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
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

CREATE TABLE passengers (
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
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_email ON bookings(user_email);
CREATE INDEX idx_ticket_id ON bookings(ticket_id);
```

---

## All Changes Complete ✅

Your Airline Reservation System is now fully migrated to PostgreSQL and ready for production deployment on Supabase!
