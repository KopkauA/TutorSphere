import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import text
from dotenv import load_dotenv

from backend.models import db
from backend.sql_queries import *

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db.init_app(app)


# --------------------------
# DB TEST
# --------------------------
with app.app_context():
    db.session.execute(text("SELECT 1"))
    print("DB Connection Successful")


# --------------------------
# LOGIN
# --------------------------
@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form['email']
    password = request.form['password']

    user = db.session.execute(
        text("""
            SELECT * FROM Users
            WHERE email = :email AND password = :password
        """),
        {"email": email, "password": password}
    ).fetchone()

    if user:
        session['user_email'] = email
        return redirect(url_for("search_sessions"))

    return render_template("login.html", error="Invalid credentials")


# --------------------------
# SIGNUP
# --------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        role = request.form.get('role', 'student')

        params = {
            "email": request.form['email'],
            "fname": request.form['fname'],
            "lname": request.form['lname'],
            "password": request.form['password'],
            "role": role
        }

        db.session.execute(insert_user, params)
        db.session.commit()

        if role == 'tutor':
            session['user_email'] = params['email']
            return redirect(url_for('signup_tutor'))

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route("/signup/tutor", methods=["GET", "POST"])
def signup_tutor():
    return render_template("signup_tutor.html")


# SEARCH SESSIONS
@app.route("/search", methods=["GET", "POST"])
def search_sessions():

    if 'user_email' not in session:
        return redirect(url_for('login'))

    sessions_list = []

    selected_date = None
    selected_weekday = None

    if request.method == "POST":

        subject_id = request.form.get("course")
        selected_date = request.form.get("time")

        if selected_date:
            selected_weekday = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).strftime("%A")

        query = search_sessions_query.text
        params = {}
        conditions = []

        if subject_id:
            conditions.append("c.course_id = :course_id")
            params["course_id"] = subject_id

        if selected_weekday:
            conditions.append("ta.week_day = :week_day")
            params["week_day"] = selected_weekday

        if conditions:
            query += " AND " + " AND ".join(conditions)

        sessions_list = db.session.execute(text(query), params).fetchall()

    # My sessions (REAL USER)
    my_sessions_list = db.session.execute(
        my_sessions_query,
        {"email": session['user_email']}
    ).fetchall()

    today = datetime.now().date()
    max_date = today + timedelta(days=7)

    return render_template(
        "session_search.html",
        sessions=sessions_list,
        my_sessions=my_sessions_list,
        selected_date=selected_date,
        selected_weekday=selected_weekday,
        today=today,
        max_date=max_date
    )


# BOOK SESSION
@app.route("/book", methods=["POST"])
def book_session():

    if 'user_email' not in session:
        return redirect(url_for('login'))

    availability_id = request.form.get("availability_id")
    course_id = request.form.get("course_id")
    date = request.form.get("date")
    start_time = request.form.get("start_time")
    location = request.form.get("location")

    session_datetime = datetime.strptime(
        f"{date} {start_time}",
        "%Y-%m-%d %H:%M:%S"
    )

    now = datetime.now()

    if session_datetime > now + timedelta(days=7):
        return "You can only book within 1 week.", 400

    if session_datetime < now:
        return "Cannot book past sessions.", 400

    db.session.execute(
        text("""
            INSERT INTO TutorSession
            (student_email, course_id, availability_id, session_location, session_datetime, session_status)
            VALUES (:email, :course_id, :availability_id, :location, :session_datetime, 'scheduled')
        """),
        {
            "email": session['user_email'],
            "course_id": course_id,
            "availability_id": availability_id,
            "location": location,
            "session_datetime": session_datetime
        }
    )

    db.session.commit()

    return redirect(url_for("search_sessions"))


# MY SESSIONS
@app.route("/my-sessions")
def my_sessions():

    if 'user_email' not in session:
        return redirect(url_for('login'))

    sessions = db.session.execute(
        my_sessions_query,
        {"email": session['user_email']}
    ).fetchall()

    return render_template("my_sessions.html", sessions=sessions)


if __name__ == "__main__":
    app.run(debug=True)