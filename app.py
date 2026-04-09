# to run, use python app.py

import os
from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
from backend.models import db, User

load_dotenv()  # Load environment variables from .env file

#FOR TESTING PURPOSES
STUDENT_EMAIL = "student1@example.com"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)

# Test the database connection
with app.app_context():
    db.session.execute(text('SELECT 1'))
    print('DB Connection Successful')

# -------- PAGE ROUTES -------- #
@app.route("/")
def login():
    return render_template("login.html")

# login page 
@app.route("/login", methods=["POST"])
def login_post():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        return redirect(url_for('menu'))
    
    return render_template("login.html", error="Invalid email or password")


@app.route("/signup", methods=["GET", "POST"])
def signup_student():
    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['fname']   
        lname = request.form['lname']   
        password = request.form['password']
        role = request.form["role"]   #(student or tutor)

        query = """
            INSERT INTO Users (email, fname, lname, password, role)
            VALUES (:email, :fname, :lname, :password, :role)
            """

        params = {
            "email": email,
            "fname": fname,
            "lname": lname,
            "password": password,
            "role": role
        }

        db.session.execute(text(query), params)
        db.session.commit()

        if role == "tutor":
            return redirect(url_for("tutor_setup", email=email))
        
        return redirect(url_for('login'))
    return render_template('signup.html')

# after signup, initial tutor setup 
@app.route("/tutor/setup/<email>", methods=["GET", "POST"])
def tutor_setup(email):
    if request.method == "POST":

        course_ids = request.form["course_ids"].split(",")
        available_time = request.form["available_time"]

        # insert multiple subjects
        for cid in course_ids:
            cid = cid.strip()
            if cid == "":
                continue

            db.session.execute(text("""
                INSERT INTO Teaches (tutor_email, course_id)
                VALUES (:email, :course_id)
            """), {
                "email": email,
                "course_id": cid
            })

        # insert availability
        db.session.execute(text("""
            INSERT INTO TutorAvailability (tutor_email, available_time, tutor_status)
            VALUES (:email, :time, 'available')
        """), {
            "email": email,
            "time": available_time
        })

        db.session.commit()

        return redirect(url_for("login"))

    return render_template("tutor_setup.html", email=email)

# autocomplete course bar 
@app.route("/api/courses")
def get_courses():
    q = request.args.get("q", "")

    query = """
    SELECT course_id, course_name
    FROM Courses
    WHERE course_name LIKE :q
    ORDER BY course_name
    LIMIT 10
    """

    results = db.session.execute(text(query), {
        "q": f"%{q}%"
    }).fetchall()

    return jsonify({
        "courses": [
            {
                "id": r.course_id,        # (stored)
                "name": r.course_name     # (shown)
            }
            for r in results
        ]
    })

# website main menu 
@app.route("/menu")
def dashboard():
    return "<h1>You are logged in.</h1>"

# search for sessions
@app.route("/search", methods=["GET", "POST"])
def search_sessions():
    sessions = []  # empty default
    my_sessions = []  # optional, for sidebar

    if request.method == "POST":
        course_id = request.form.get("course")
        tutor = request.form.get("tutor")
        time = request.form.get("time")

        query = """
        SELECT ta.availability_id, ta.available_time,
               u.fname, u.lname,
               c.course_id, c.course_name
        FROM TutorAvailability ta
        JOIN Users u ON ta.tutor_email = u.email
        JOIN Teaches t ON u.email = t.tutor_email
        JOIN Courses c ON t.course_id = c.course_id
        WHERE ta.tutor_status = 'available'
        """
        params = {}

        if course_id:
            query += " AND c.course_id = :course_id"
            params["course_id"] = course_id

        if tutor:
            query += " AND (u.fname LIKE :tutor OR u.lname LIKE :tutor)"
            params["tutor"] = f"%{tutor}%"

        if time:
            query += " AND DATE(ta.available_time) = :time"
            params["time"] = time

        sessions = db.session.execute(text(query), params).fetchall()

    return render_template("session_search.html", sessions=sessions, my_sessions=my_sessions)

# view personal user's sessions 
@app.route("/book/<int:availability_id>", methods=["POST"])
def book_session(availability_id):
    db.session.execute(
        text("" \
        "UPDATE TutorAvailability " \
        "SET tutor_status = 'booked' " \
        "WHERE availability_id = :id"),
        {"id": availability_id}
    )
    db.session.commit()
    return redirect(url_for("search_sessions"))

# for looking at personal active/completed/cancelled sessions
@app.route("/my-sessions")
def my_sessions():
    status = request.args.get("status")  # active/completed/cancelled

    query = """
    SELECT ts.session_id,
           ts.session_status,
           ts.session_location,
           ts.course_id,
           ta.available_time,
           u.fname,
           u.lname
    FROM TutorSession ts
    JOIN TutorAvailability ta ON ts.availability_id = ta.availability_id
    JOIN Users u ON ts.tutor_email = u.email
    WHERE ts.student_email = :email
    """

    params = {"email": STUDENT_EMAIL}

    if status:
        query += " AND ts.session_status = :status"
        params["status"] = status

    query += " ORDER BY ta.available_time DESC"

    sessions = db.session.execute(text(query), params).fetchall()

    return render_template("my_sessions.html", sessions=sessions)

# run
if __name__ == "__main__":
    app.run(debug=True)
    