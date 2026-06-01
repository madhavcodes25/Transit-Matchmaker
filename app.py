import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'dev_fallback_key_for_local_testing')

DATABASE = 'transit.db'

# Database Connection Helper
def get_db():
    """Opens a new database connection if there is none yet for the current request context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Automatically Close Database Connection
@app.teardown_appcontext
def close_connection(exception):
    """Closes the database again at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Homepage
@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        user_trips = db.execute("""
            SELECT * FROM trips 
            WHERE user_id = ? 
            ORDER BY travel_date ASC, time_window_start ASC
        """, (user_id,)).fetchall()
        return render_template('index.html', trips=user_trips)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                       (name, email, hashed_pw))
            db.commit() 
            return redirect('/')
            
        except sqlite3.IntegrityError:
            return "Error: That email is already registered."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user is None or not check_password_hash(user['password_hash'], password):
            return "Error: Invalid email and/or password."
        session['user_id'] = user['id']
        flash("Successfully logged in!", "success")
        return redirect('/')

    return render_template('login.html')

@app.route('/add_trip', methods=['GET', 'POST'])
def add_trip():
    # SECURITY CHECK: Kick them out if they aren't logged in
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        departure_point = request.form.get('departure_point')
        destination = request.form.get('destination')
        travel_date = request.form.get('travel_date')
        time_window_start = request.form.get('time_window_start')
        time_window_end = request.form.get('time_window_end')
        
        if time_window_end <= time_window_start:
            flash("Error: Your latest departure time must be after your earliest departure time!", "error")
            return redirect('/add_trip')
        user_id = session['user_id']

        db = get_db()
        db.execute("""
            INSERT INTO trips 
            (user_id, departure_point, destination, travel_date, time_window_start, time_window_end) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, departure_point, destination, travel_date, time_window_start, time_window_end))
        
        db.commit()
        
        flash("Your travel plans have been posted!", "success")
        return redirect('/')
    return render_template('add_trip.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect('/')

@app.route('/find_matches/<int:trip_id>')
def find_matches(trip_id):
    # SECURITY: Must be logged in
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    user_id = session['user_id']
    my_trip = db.execute("SELECT * FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id)).fetchone()
    if my_trip is None:
        return "Error: Trip not found or access denied.", 404
    matches = db.execute("""
        SELECT trips.*, users.name, users.email 
        FROM trips 
        JOIN users ON trips.user_id = users.id
        WHERE trips.destination = ? 
          AND trips.travel_date = ? 
          AND trips.user_id != ? 
        ORDER BY trips.time_window_start ASC
    """, (my_trip['destination'], my_trip['travel_date'], user_id)).fetchall()
    return render_template('matches.html', my_trip=my_trip, matches=matches)

@app.route('/delete_trip/<int:trip_id>', methods=['POST'])
def delete_trip(trip_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    db = get_db()
    trip = db.execute("SELECT * FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id)).fetchone()

    if trip is None:
        return "Error: Trip not found or you don't have permission to delete it.", 403

    db.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    db.commit()
    flash("Trip successfully canceled.", "success")
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)