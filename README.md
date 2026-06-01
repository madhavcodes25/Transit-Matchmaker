# Transit Matchmaker 🚗💨
### *A Campus Ridesharing & Carpooling Matchmaker for SVNIT Students*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: Flask](https://img.shields.io/badge/Framework-Flask-000000?style=flat&logo=flask)](https://flask.palletsprojects.com/)
[![Frontend: Bootstrap 5](https://img.shields.io/badge/Frontend-Bootstrap%205-7952B3?style=flat&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Database: SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org/)

---

## 🔗 Project Links
- **Live Production URL:** https://transit-matchmaker.onrender.com/
- **Video Demo Walkthrough:** [YouTube URL]

---

## 📖 Project Overview
**Transit Matchmaker** is a full-stack web application designed for college campuses to resolve a pervasive commuter pain point: splitting transit fares. Students frequently travel from campus to major local transit hubs such as railway stations, airports, or central bus stands individually, resulting in high costs for auto rickshaws or private cabs. 

This platform allows students to securely register, log in, post their upcoming travel plans (departure points, destinations, dates, and flexible departure time windows), and run a **custom relational matching algorithm** to find other students traveling along the exact same route within a synchronized timeframe. By providing immediate email links, it bridges the gap between disconnected campus commuters, effectively reducing individual travel expenses and the student carbon footprint.

This project was built from scratch as a comprehensive capstone showcasing a solid understanding of backend MVC architecture, relational database design, secure session state management, production deployment pipelines, and responsive user interfaces.

---

## ⚡ Key Features
- **Secure Authentication & Session Security:** Complete implementation of user registration, login, and session tracking. Passwords are secure and never stored in plain text; they are protected using robust cryptographic PBKDF2 hashing algorithms via `werkzeug.security`.
- **Dynamic User Dashboard (Full CRUD):** Unauthenticated visitors are greeted with a clean, conversion-focused landing page. Once authenticated, the dashboard dynamically updates to query, display, and manage the user's active travel itineraries.
- **The Matchmaker Engine (Relational SQL JOIN):** A custom backend query parses the database to locate matches. It isolates travel schedules matching the exact destination and date, ensures users cannot match with themselves, and sorts results sequentially based on the departure time window.
- **Form Interception & Server-Side Validation:** Form inputs are heavily verified on the backend. The app protects database integrity by intercepting chronological logic errors such as preventing a user from setting a 'Latest Departure Time' that precedes their 'Earliest Departure Time'.
- **Modern Theme-Aware UI (Bootstrap 5 & LocalStorage):** Fully optimized using modern components (Cards, Forms, Navbars, Grid System) making the tool 100% mobile responsive. Features a seamless **Dark Mode toggle** that syncs with the browser's native `localStorage` API to maintain state across page refreshes without any flashing.
- **Asynchronous User Feedback:** Implements Flask Flash Alert routing mapped directly to Bootstrap's dismissible utility classes, utilizing customized JavaScript hooks to automatically fade out alerts after 3 seconds for a cleaner user experience while leaving critical persistent warnings untouched.

---

## 🛠️ Tech Stack & Architecture

### **Backend Core:**
- **Python / Flask:** Handles HTTP routing, request parsing, cookie based session management, validation, and core application business logic.
- **Gunicorn:** Actively handles production WSGI server processes for stable cloud deployment.
- **SQLite3:** A lightweight, dependable relational database used for transactional storage of user profiles and travel schedules.

### **Frontend Core:**
- **Jinja2 Template Engine:** Used for server side layout inheritance, template segmentation, and dynamic data binding.
- **Bootstrap 5.3:** Acts as the presentation layer framework, supplying grid mechanics, dark/light utility classes, and system component styling.
- **JavaScript:** Powers client side interactivity, theme persistence loops via `localStorage`, and asynchronous UI animations.

---

## 💾 Database Schema Design
The application utilizes a relational schema to cleanly handle multi-table dependencies with cascading deletions:

```sql
-- 1. Users Entity Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- 2. Trips Transactional Table
CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    departure_point TEXT NOT NULL,
    destination TEXT NOT NULL,
    travel_date TEXT NOT NULL,
    time_window_start TEXT NOT NULL,
    time_window_end TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```
## 📂 Codebase File Structure

```
transit-matchmaker/
│
├── app.py                 # Core controller, route configurations, and validation engine
├── schema.sql             # Relational database initialization script
├── transit.db             # SQLite binary database file (Generated runtime instance)
├── requirements.txt       # Production dependencies list
├── .gitignore             # Explicit environment and operating system file exclusion rules
│
├── static/
│   ├── css/
│   │   └── styles.css     # Theme extension styles and custom visual overrides
│   └── js/
│       └── script.js      # Dark Mode state logic and flash alert auto dismiss timers
│
└── templates/
    ├── layout.html        # Master boilerplate layout containing HTML head, responsive navbar, and scripts
    ├── index.html         # Smart welcome landing / authenticated user dashboard grid
    ├── login.html         # Secure session entry form card
    ├── register.html      # User identity provisioning form card
    ├── add_trip.html      # Transactional travel schedule submission form
    └── matches.html       # Dynamic match collection and contact generation view
```

## 🚀 Installation & Local Environment Setup
Follow these steps to spin up the development environment on your local system:

1. **Clone the Repository:**

```Bash
git clone https://github.com/madhavcodes25/transit-matchmaker.git
cd transit-matchmaker
```
2. **Initialize Python Virtual Environment:**
```Bash
python3 -m venv venv
source venv/bin/activate
```
3. **Install Dependencies:**
```Bash
pip install -r requirements.txt
```
4. **Construct the Database Instance:**

```Bash
sqlite3 transit.db < schema.sql
```

5. **Fire up the Development Server:**
```Bash
python3 app.py
```
6. **Access App:** 

Open your web browser and navigate to http://127.0.0.1:5000.
