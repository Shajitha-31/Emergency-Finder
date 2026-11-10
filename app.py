
import os
import re
import math
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY", "emergency-finder-hackathon-secret"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "resqnet.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

CATEGORIES = [
    "Fire Emergency",
    "Road Accident",
    "Medical Emergency",
    "Flood",
    "Building Collapse",
    "Other Emergencies"
]

STATUSES = ["Reported", "Assigned", "In Progress", "Resolved"]


# ==========================================
# DATABASE
# ==========================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team_code TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            phone TEXT,
            availability TEXT DEFAULT 'Available',
            created TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            affected INTEGER DEFAULT 0,
            contact TEXT,
            latitude REAL,
            longitude REAL,
            photo TEXT,
            severity TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            ai_reason TEXT,
            recommended_action TEXT,
            status TEXT DEFAULT 'Reported',
            team_id INTEGER,
            duplicate_of INTEGER,
            created TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(team_id) REFERENCES teams(id)
        )
    """)

    # Add missing columns when upgrading an older database.
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(incidents)").fetchall()
    }

    migrations = {
        "latitude": "REAL",
        "longitude": "REAL",
        "photo": "TEXT",
        "severity": "TEXT DEFAULT 'Low'",
        "score": "INTEGER DEFAULT 0",
        "ai_reason": "TEXT",
        "recommended_action": "TEXT",
        "status": "TEXT DEFAULT 'Reported'",
        "team_id": "INTEGER",
        "duplicate_of": "INTEGER"
    }

    for name, definition in migrations.items():
        if name not in columns:
            conn.execute(
                f"ALTER TABLE incidents ADD COLUMN {name} {definition}"
            )

    # Default administrator.
    admin = conn.execute(
        "SELECT id FROM users WHERE email=?",
        ("admin@resqnet.in",)
    ).fetchone()

    if not admin:
        conn.execute("""
            INSERT INTO users(name,email,password,role,created)
            VALUES(?,?,?,?,?)
        """, (
            "Administrator",
            "admin@resqnet.in",
            generate_password_hash("admin123"),
            "admin",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    # Default candidate for demonstration.
    candidate = conn.execute(
        "SELECT id FROM users WHERE email=?",
        ("candidate@resqnet.in",)
    ).fetchone()

    if not candidate:
        conn.execute("""
            INSERT INTO users(name,email,password,role,created)
            VALUES(?,?,?,?,?)
        """, (
            "Demo Candidate",
            "candidate@resqnet.in",
            generate_password_hash("candidate123"),
            "candidate",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()
    conn.close()


initialize_database()


# ==========================================
# AUTHENTICATION
# ==========================================

def login_required(role=None):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                return redirect(url_for("home"))

            if role and session.get("role") != role:
                return redirect(url_for("home"))

            return function(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please complete all required fields.")
            return redirect(url_for("register"))

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must contain at least 6 characters.")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO users(name,email,password,role,created)
                VALUES(?,?,?,?,?)
            """, (
                name,
                email,
                generate_password_hash(password),
                "candidate",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            flash("Registration successful. Please login.")

        except sqlite3.IntegrityError:
            flash("This email is already registered.")

        finally:
            conn.close()

        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    requested_role = request.form.get("role", "candidate")

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    ).fetchone()

    conn.close()

    if not user or not check_password_hash(user["password"], password):
        flash("Invalid email or password.")
        return redirect(url_for("home"))

    if user["role"] != requested_role:
        flash("This account does not have the selected role.")
        return redirect(url_for("home"))

    session.clear()

    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["email"] = user["email"]
    session["role"] = user["role"]

    if user["role"] == "admin":
        return redirect(url_for("dashboard"))

    return redirect(url_for("candidate"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ==========================================
# PAGE ROUTES
# ==========================================

@app.route("/candidate")
@login_required("candidate")
def candidate():
    return render_template(
        "candidate.html",
        name=session["name"]
    )


@app.route("/dashboard")
@login_required("admin")
def dashboard():
    return render_template(
        "dashboard.html",
        name=session["name"]
    )


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def haversine(lat1, lon1, lat2, lon2):

    radius = 6371

    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return radius * 2 * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )


def calculate_priority(category, description, affected):

    text = description.lower()

    score = 10

    category_points = {
        "Fire Emergency": 20,
        "Road Accident": 18,
        "Medical Emergency": 22,
        "Flood": 20,
        "Building Collapse": 25,
        "Other Emergencies": 10
    }

    score += category_points.get(category, 10)

    # People affected.
    if affected >= 20:
        score += 35
    elif affected >= 10:
        score += 28
    elif affected >= 5:
        score += 20
    elif affected >= 2:
        score += 12
    elif affected >= 1:
        score += 5

    # Emergency keywords.
    critical_words = [
        "trapped", "unconscious", "critical",
        "explosion", "collapsed", "life threatening",
        "severe bleeding", "multiple casualties"
    ]

    high_words = [
        "injured", "smoke", "burning", "heavy flood",
        "children", "elderly", "serious"
    ]

    reasons = []

    if any(word in text for word in critical_words):
        score += 30
        reasons.append("Critical danger keywords detected")

    elif any(word in text for word in high_words):
        score += 20
        reasons.append("High-risk emergency keywords detected")

    if affected >= 10:
        reasons.append("Large number of affected people")

    if category == "Building Collapse":
        reasons.append("Structural collapse risk")

    score = min(score, 100)

    if score >= 80:
        severity = "Critical"
        action = "Immediate emergency response required."
    elif score >= 60:
        severity = "High"
        action = "Dispatch a response team urgently."
    elif score >= 35:
        severity = "Medium"
        action = "Arrange a suitable response team."
    else:
        severity = "Low"
        action = "Monitor and review the incident."

    if not reasons:
        reasons.append("Category and affected-person count assessed")

    suggested = {
        "Fire Emergency": ["Fire Rescue"],
        "Road Accident": ["Medical Support", "Rescue Team"],
        "Medical Emergency": ["Medical Support"],
        "Flood": ["Flood Rescue"],
        "Building Collapse": ["Rescue Team", "Medical Support"],
        "Other Emergencies": ["General Response Team"]
    }

    return (
        severity,
        score,
        "; ".join(reasons),
        action,
        suggested.get(category, ["General Response Team"])
    )


def find_duplicate(category, location, title):

    conn = get_db()

    records = conn.execute("""
        SELECT id,title,location
        FROM incidents
        WHERE category=?
        ORDER BY id DESC
        LIMIT 100
    """, (category,)).fetchall()

    conn.close()

    title_words = set(re.findall(r"\w+", title.lower()))
    location_words = set(re.findall(r"\w+", location.lower()))

    for record in records:

        old_title = set(re.findall(r"\w+", record["title"].lower()))
        old_location = set(re.findall(r"\w+", record["location"].lower()))

        title_match = (
            len(title_words & old_title) /
            max(1, len(title_words | old_title))
        )

        location_match = (
            len(location_words & old_location) /
            max(1, len(location_words | old_location))
        )

        if title_match >= 0.5 and location_match >= 0.5:
            return record["id"]

    return None


def incident_dict(row):

    item = dict(row)

    team_id = item.get("team_id")

    if team_id:
        conn = get_db()

        team = conn.execute(
            "SELECT name FROM teams WHERE id=?",
            (team_id,)
        ).fetchone()

        conn.close()

        item["team"] = team["name"] if team else "Unknown"
    else:
        item["team"] = "Not Assigned"

    item["reporter"] = item.get("reporter", "Unknown")

    return item


# ==========================================
# INCIDENT REPORTING
# ==========================================

@app.route("/api/incidents", methods=["GET", "POST"])
@login_required()
def incidents_api():

    # --------------------------------------
    # GET REPORTS
    # --------------------------------------

    if request.method == "GET":

        conn = get_db()

        if session["role"] == "admin":

            rows = conn.execute("""
                SELECT incidents.*, users.name AS reporter
                FROM incidents
                JOIN users ON incidents.user_id=users.id
                ORDER BY incidents.id DESC
            """).fetchall()

        else:

            rows = conn.execute("""
                SELECT incidents.*, users.name AS reporter
                FROM incidents
                JOIN users ON incidents.user_id=users.id
                WHERE incidents.user_id=?
                ORDER BY incidents.id DESC
            """, (session["user_id"],)).fetchall()

        conn.close()

        return jsonify([incident_dict(row) for row in rows])

    # --------------------------------------
    # POST NEW REPORT
    # --------------------------------------

    if session["role"] != "candidate":
        return jsonify({"error": "Candidate access required."}), 403

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    location = request.form.get("location", "").strip()
    contact = request.form.get("contact", "").strip()

    if not title or not description or not category or not location:
        return jsonify({"error": "Complete all required fields."}), 400

    if category not in CATEGORIES:
        return jsonify({"error": "Invalid emergency category."}), 400

    try:
        affected = int(request.form.get("affected", 0))
        if affected < 0 or affected > 1000000:
            raise ValueError()
    except ValueError:
        return jsonify({"error": "Invalid affected-person count."}), 400

    latitude = request.form.get("latitude") or None
    longitude = request.form.get("longitude") or None

    try:
        latitude = float(latitude) if latitude else None
        longitude = float(longitude) if longitude else None

        if (
            (latitude is None) != (longitude is None)
            or (latitude is not None and not -90 <= latitude <= 90)
            or (longitude is not None and not -180 <= longitude <= 180)
        ):
            raise ValueError()

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid GPS coordinates."}), 400

    # Photo upload.
    photo_name = None
    photo = request.files.get("photo")

    if photo and photo.filename:

        if not allowed_file(photo.filename):
            return jsonify({"error": "Use JPG, PNG or WEBP photos."}), 400

        original = secure_filename(photo.filename)

        photo_name = (
            datetime.now().strftime("%Y%m%d%H%M%S%f")
            + "_"
            + original
        )

        photo.save(
            os.path.join(UPLOAD_FOLDER, photo_name)
        )

    severity, score, reason, action, suggested = calculate_priority(
        category, description, affected
    )

    duplicate_id = find_duplicate(category, location, title)

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO incidents(
            user_id,title,description,category,location,
            affected,contact,latitude,longitude,photo,
            severity,score,ai_reason,recommended_action,
            status,team_id,duplicate_of,created
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        session["user_id"],
        title,
        description,
        category,
        location,
        affected,
        contact,
        latitude,
        longitude,
        photo_name,
        severity,
        score,
        reason,
        action,
        "Reported",
        None,
        duplicate_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    incident_id = cursor.lastrowid

    conn.commit()
    conn.close()

    # Automatically assign a suitable team when GPS is available.
    assigned_team = None

    if latitude is not None and longitude is not None:
        try:
            assigned_team = assign_nearest_team(incident_id)
        except Exception:
            assigned_team = None

    return jsonify({
        "success": True,
        "id": incident_id,
        "severity": severity,
        "score": score,
        "reasons": reason,
        "action": action,
        "teams": suggested,
        "duplicates": (
            [{"id": duplicate_id}] if duplicate_id else []
        ),
        "assigned_team": assigned_team
    }), 201


# ==========================================
# RESPONSE TEAM MANAGEMENT
# ==========================================

@app.route("/api/teams", methods=["GET", "POST"])
@login_required("admin")
def teams_api():

    conn = get_db()

    if request.method == "GET":

        rows = conn.execute("""
            SELECT * FROM teams ORDER BY id DESC
        """).fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows])

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    team_code = str(data.get("team_code", "")).strip().upper()
    category = str(data.get("category", "")).strip()
    location = str(data.get("location", "")).strip()
    phone = str(data.get("phone", "")).strip()

    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))

        if not (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            raise ValueError()

    except (ValueError, TypeError):
        conn.close()
        return jsonify({"error": "Invalid team coordinates."}), 400

    valid_categories = CATEGORIES + ["All"]

    if (
        not name or not team_code or not location
        or category not in valid_categories
    ):
        conn.close()
        return jsonify({"error": "Complete all team details."}), 400

    try:

        cursor = conn.execute("""
            INSERT INTO teams(
                name,team_code,category,location,
                latitude,longitude,phone,availability,created
            )
            VALUES(?,?,?,?,?,?,?,?,?)
        """, (
            name,
            team_code,
            category,
            location,
            latitude,
            longitude,
            phone,
            "Available",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        team_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "id": team_id,
            "message": "Response team registered."
        }), 201

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Team ID already exists."}), 409


@app.route("/api/teams/<int:team_id>", methods=["PATCH", "DELETE"])
@login_required("admin")
def team_detail(team_id):

    conn = get_db()

    team = conn.execute(
        "SELECT * FROM teams WHERE id=?",
        (team_id,)
    ).fetchone()

    if not team:
        conn.close()
        return jsonify({"error": "Team not found."}), 404

    if request.method == "DELETE":

        active = conn.execute("""
            SELECT COUNT(*) AS total FROM incidents
            WHERE team_id=? AND status!='Resolved'
        """, (team_id,)).fetchone()["total"]

        if active:
            conn.close()
            return jsonify({
                "error": "This team has active incidents. Resolve or reassign them first."
            }), 409

        conn.execute(
            "UPDATE incidents SET team_id=NULL WHERE team_id=?",
            (team_id,)
        )

        conn.execute(
            "DELETE FROM teams WHERE id=?",
            (team_id,)
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    data = request.get_json(silent=True) or {}
    availability = data.get("availability")

    if availability not in ["Available", "Busy", "Unavailable"]:
        conn.close()
        return jsonify({"error": "Invalid availability."}), 400

    conn.execute(
        "UPDATE teams SET availability=? WHERE id=?",
        (availability, team_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ==========================================
# NEAREST TEAM ASSIGNMENT
# ==========================================

def assign_nearest_team(incident_id):

    conn = get_db()

    incident = conn.execute(
        "SELECT * FROM incidents WHERE id=?",
        (incident_id,)
    ).fetchone()

    if not incident:
        conn.close()
        raise ValueError("Incident not found.")

    if incident["latitude"] is None:
        conn.close()
        raise ValueError("Incident GPS coordinates are required.")

    if incident["status"] == "Resolved":
        conn.close()
        raise ValueError("Resolved incidents cannot be assigned.")

    if incident["team_id"]:
        conn.close()
        raise ValueError("Incident already has a team assigned.")

    teams = conn.execute("""
        SELECT * FROM teams
        WHERE availability='Available'
        AND (category='All' OR category=?)
    """, (incident["category"],)).fetchall()

    if not teams:
        conn.close()
        raise ValueError("No suitable available response team found.")

    ranked = []

    for team in teams:

        distance = haversine(
            incident["latitude"],
            incident["longitude"],
            team["latitude"],
            team["longitude"]
        )

        ranked.append((distance, team))

    ranked.sort(key=lambda x: x[0])

    distance, team = ranked[0]

    conn.execute("""
        UPDATE incidents
        SET team_id=?, status='Assigned'
        WHERE id=?
    """, (team["id"], incident_id))

    conn.execute("""
        UPDATE teams SET availability='Busy'
        WHERE id=?
    """, (team["id"],))

    conn.commit()
    conn.close()

    return {
        "id": team["id"],
        "name": team["name"],
        "distance": round(distance, 2)
    }


@app.route("/api/incidents/<int:incident_id>/assign", methods=["POST"])
@login_required("admin")
def assign_incident(incident_id):

    try:
        result = assign_nearest_team(incident_id)
        return jsonify(result)

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


# ==========================================
# INCIDENT STATUS / DELETE
# ==========================================

@app.route("/api/incidents/<int:incident_id>", methods=["PATCH", "DELETE"])
@login_required("admin")
def incident_detail(incident_id):

    conn = get_db()

    incident = conn.execute(
        "SELECT * FROM incidents WHERE id=?",
        (incident_id,)
    ).fetchone()

    if not incident:
        conn.close()
        return jsonify({"error": "Incident not found."}), 404

    if request.method == "DELETE":

        if incident["team_id"]:
            conn.execute("""
                UPDATE teams SET availability='Available'
                WHERE id=? AND availability='Busy'
            """, (incident["team_id"],))

        conn.execute(
            "DELETE FROM incidents WHERE id=?",
            (incident_id,)
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in STATUSES:
        conn.close()
        return jsonify({"error": "Invalid incident status."}), 400

    team_id = incident["team_id"]

    if status in ["Assigned", "In Progress"] and not team_id:
        conn.close()
        return jsonify({"error": "Assign a response team first."}), 400

    conn.execute(
        "UPDATE incidents SET status=? WHERE id=?",
        (status, incident_id)
    )

    if team_id and status == "Resolved":
        conn.execute("""
            UPDATE teams SET availability='Available'
            WHERE id=?
        """, (team_id,))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ==========================================
# ANALYTICS
# ==========================================

@app.route("/api/analytics")
@login_required("admin")
def analytics():

    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) AS n FROM incidents"
    ).fetchone()["n"]

    critical = conn.execute("""
        SELECT COUNT(*) AS n FROM incidents
        WHERE severity='Critical'
    """).fetchone()["n"]

    pending = conn.execute("""
        SELECT COUNT(*) AS n FROM incidents
        WHERE status IN ('Reported','Assigned','In Progress')
    """).fetchone()["n"]

    resolved = conn.execute("""
        SELECT COUNT(*) AS n FROM incidents
        WHERE status='Resolved'
    """).fetchone()["n"]

    team_counts = conn.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN availability='Available' THEN 1 ELSE 0 END) AS available,
            SUM(CASE WHEN availability='Busy' THEN 1 ELSE 0 END) AS busy,
            SUM(CASE WHEN availability='Unavailable' THEN 1 ELSE 0 END) AS unavailable
        FROM teams
    """).fetchone()

    categories = conn.execute("""
        SELECT category,COUNT(*) AS count
        FROM incidents GROUP BY category
    """).fetchall()

    severity = conn.execute("""
        SELECT severity,COUNT(*) AS count
        FROM incidents GROUP BY severity
    """).fetchall()

    conn.close()

    return jsonify({
        "total": total,
        "critical": critical,
        "pending": pending,
        "resolved": resolved,
        "teams_total": team_counts["total"] or 0,
        "teams_available": team_counts["available"] or 0,
        "teams_busy": team_counts["busy"] or 0,
        "teams_unavailable": team_counts["unavailable"] or 0,
        "categories": [dict(row) for row in categories],
        "severity": [dict(row) for row in severity]
    })


# ==========================================
# ERROR HANDLING
# ==========================================

@app.errorhandler(413)
def too_large(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Photo exceeds the 5 MB limit."}), 413
    return "File too large. Maximum allowed size is 5 MB.", 413


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "API endpoint not found."}), 404
    return "Page not found.", 404


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
