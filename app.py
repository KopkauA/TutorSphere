# to run, use python app.py

import os
from flask import Flask, render_template, request, redirect
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

# page routes
@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        return redirect(url_for('dashboard'))
    
    return render_template("login.html", error="Invalid email or password")


@app.route("/dashboard")
def dashboard():
    return "<h1>You are logged in.</h1>"

@app.route("/signup")
def signup_choice():
    return render_template("signup_choice.html")


@app.route('/signup/student', methods=['GET', 'POST'])
def signup_student():
    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['fname']   
        lname = request.form['lname']   
        password = request.form['password']

        new_user = User(
            email=email,
            fname=fname,
            lname=lname,
            password=password,
            role='student'
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup_student.html')

STUDENT_EMAIL = "student1@example.com"


@app.route("/signup/tutor")
def signup_tutor():
    return render_template("signup_tutor.html")

@app.route("/search", methods=["GET", "POST"])
def search_sessions():
    sessions = []  # empty default
    my_sessions = []  # optional, for sidebar

    if request.method == "POST":
        subject_id = request.form.get("subject")
        tutor = request.form.get("tutor")
        time = request.form.get("time")

        query = """
        SELECT ta.availability_id, ta.available_time,
               u.fname, u.lname,
               s.subject_id, s.subject_name
        FROM TutorAvailability ta
        JOIN Users u ON ta.tutor_email = u.email
        JOIN Teaches t ON u.email = t.tutor_email
        JOIN Subjects s ON t.subject_id = s.subject_id
        WHERE ta.tutor_status = 'available'
        """
        params = {}

        if subject_id:
            query += " AND s.subject_id = :subject_id"
            params["subject_id"] = subject_id

        if tutor:
            query += " AND (u.fname LIKE :tutor OR u.lname LIKE :tutor)"
            params["tutor"] = f"%{tutor}%"

        if time:
            query += " AND DATE(ta.available_time) = :time"
            params["time"] = time

        sessions = db.session.execute(text(query), params).fetchall()

    return render_template("session_search.html", sessions=sessions, my_sessions=my_sessions)

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
    