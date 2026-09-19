import sqlite3
import os
from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_fallback_key_for_local_testing')

DATABASE = 'transit.db'


# ── Database helpers ──────────────────────────────────────────────────────────

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def migrate_db():
    """Add new columns to existing DB without dropping data."""
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # users.phone (optional WhatsApp number)
    try:
        cur.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except sqlite3.OperationalError:
        pass  # column already exists

    # trips.is_recurring
    try:
        cur.execute("ALTER TABLE trips ADD COLUMN is_recurring INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


migrate_db()


# ── Helpers ───────────────────────────────────────────────────────────────────

def advance_recurring_trips(db, user_id):
    """Move past recurring trips forward by 7-day increments until >= today."""
    today = str(date.today())
    old = db.execute(
        "SELECT id, travel_date FROM trips WHERE user_id = ? AND is_recurring = 1 AND travel_date < ?",
        (user_id, today)
    ).fetchall()
    for trip in old:
        trip_date = date.fromisoformat(trip['travel_date'])
        while str(trip_date) < today:
            trip_date += timedelta(weeks=1)
        db.execute("UPDATE trips SET travel_date = ? WHERE id = ?", (str(trip_date), trip['id']))
    if old:
        db.commit()


def get_match_counts(db, trips, user_id):
    """Return {trip_id: match_count} using the overlap filter."""
    counts = {}
    for trip in trips:
        row = db.execute("""
            SELECT COUNT(*) AS cnt FROM trips
            WHERE destination = ?
              AND travel_date  = ?
              AND user_id     != ?
              AND time_window_start < ?
              AND time_window_end   > ?
        """, (
            trip['destination'], trip['travel_date'], user_id,
            trip['time_window_end'], trip['time_window_start']
        )).fetchone()
        counts[trip['id']] = row['cnt']
    return counts


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()

        # Advance any stale recurring trips before fetching
        advance_recurring_trips(db, user_id)

        today = str(date.today())
        # Show trips that haven't passed, plus all recurring ones (already advanced above)
        user_trips = db.execute("""
            SELECT * FROM trips
            WHERE user_id = ?
              AND (travel_date >= ? OR is_recurring = 1)
            ORDER BY travel_date ASC, time_window_start ASC
        """, (user_id, today)).fetchall()

        match_counts = get_match_counts(db, user_trips, user_id)
        return render_template('index.html', trips=user_trips, match_counts=match_counts)
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name      = request.form.get('name', '').strip()
        email     = request.form.get('email', '').strip()
        password  = request.form.get('password', '')
        phone_raw = request.form.get('phone', '').strip()
        # Sanitize phone: digits only, prepend country code if missing
        phone = ''.join(filter(str.isdigit, phone_raw)) or None

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        db = get_db()
        try:
            cur = db.execute(
                "INSERT INTO users (name, email, password_hash, phone) VALUES (?, ?, ?, ?)",
                (name, email, hashed_pw, phone)
            )
            db.commit()
            # Auto-login after registration
            session['user_id'] = cur.lastrowid
            flash(f"Welcome, {name}! Your account has been created.", "success")
            return redirect('/')
        except sqlite3.IntegrityError:
            flash("That email is already registered. Please log in instead.", "error")
            return redirect('/register')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        email    = request.form.get('email', '')
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user is None or not check_password_hash(user['password_hash'], password):
            flash("Invalid email or password.", "error")
            return redirect('/login')
        session['user_id'] = user['id']
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect('/')
    return render_template('login.html')


@app.route('/add_trip', methods=['GET', 'POST'])
def add_trip():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        departure_point   = request.form.get('departure_point', '').strip()
        destination       = request.form.get('destination', '')
        travel_date       = request.form.get('travel_date', '')
        time_window_start = request.form.get('time_window_start', '')
        time_window_end   = request.form.get('time_window_end', '')
        is_recurring      = 1 if request.form.get('is_recurring') else 0

        if time_window_end <= time_window_start:
            flash("Latest departure must be after earliest departure.", "error")
            return redirect('/add_trip')

        user_id = session['user_id']
        db = get_db()
        db.execute("""
            INSERT INTO trips
              (user_id, departure_point, destination, travel_date,
               time_window_start, time_window_end, is_recurring)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, departure_point, destination, travel_date,
              time_window_start, time_window_end, is_recurring))
        db.commit()

        label = "Recurring trip" if is_recurring else "Trip"
        flash(f"{label} posted! We'll find you buddies.", "success")
        return redirect('/')

    return render_template('add_trip.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect('/')


@app.route('/find_matches/<int:trip_id>')
def find_matches(trip_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    user_id = session['user_id']
    my_trip = db.execute(
        "SELECT * FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id)
    ).fetchone()

    if my_trip is None:
        flash("Trip not found or access denied.", "error")
        return redirect('/')

    # Overlap filter: their window must intersect my window
    matches = db.execute("""
        SELECT trips.*, users.name, users.email, users.phone
        FROM trips
        JOIN users ON trips.user_id = users.id
        WHERE trips.destination       = ?
          AND trips.travel_date       = ?
          AND trips.user_id          != ?
          AND trips.time_window_start < ?
          AND trips.time_window_end   > ?
        ORDER BY trips.time_window_start ASC
    """, (
        my_trip['destination'], my_trip['travel_date'], user_id,
        my_trip['time_window_end'], my_trip['time_window_start']
    )).fetchall()

    return render_template('matches.html', my_trip=my_trip, matches=matches)


@app.route('/delete_trip/<int:trip_id>', methods=['POST'])
def delete_trip(trip_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()
    trip = db.execute(
        "SELECT * FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id)
    ).fetchone()

    if trip is None:
        flash("Trip not found or you don't have permission to delete it.", "error")
        return redirect('/')

    db.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    db.commit()
    flash("Trip cancelled successfully.", "success")
    return redirect('/')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)