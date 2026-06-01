DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS trips;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,     
    password_hash TEXT NOT NULL     
);

CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,        
    departure_point TEXT NOT NULL,   
    destination TEXT NOT NULL,      
    travel_date DATE NOT NULL,       
    time_window_start TIME NOT NULL, 
    time_window_end TIME NOT NULL,    
    FOREIGN KEY (user_id) REFERENCES users (id)
);