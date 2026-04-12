import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import text
from dotenv import load_dotenv

from backend.models import db
from backend.sql_queries import *

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# DB TEST
with app.app_context():
    db.session.execute(text("SELECT 1"))
    print("DB Connection Successful")


# LOGIN
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
        return redirect(url_for("dashboard_route"))

    return render_template("login.html", error="Invalid credentials")


# SIGNUP
@app.route('/signup_route', methods=['GET', 'POST'])
def signup_route():

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
            return redirect(url_for('signup_tutor_route'))

        return redirect(url_for('login_post'))

    return render_template('signup.html')


@app.route("/signup/tutor", methods=["GET", "POST"])
def signup_tutor():
    return render_template("signup_tutor.html")


# SEARCH SESSIONS
@app.route("/search", methods=["GET", "POST"])
def search_sessions_route():

    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    sessions_list = []

    selected_date = None
    selected_weekday = None

    if request.method == "POST":
        action = request.form.get("action")

        subject_id = request.form.get("course")
        selected_date = request.form.get("time")

        if selected_date:
            selected_weekday = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).strftime("%A")

        query = search_sessions_query.text
        params = {"selected_date": selected_date if selected_date else None}
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

    # My sessions
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

# MY SESSIONS
@app.route("/my_sessions")
def my_sessions_route():

    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    sessions = db.session.execute(
        my_sessions_query,
        {"email": session['user_email']}
    ).fetchall()

    return render_template("my_sessions.html", sessions=sessions)

@app.route("/dashboard")
def dashboard_route():

    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    return render_template("dashboard.html")

@app.route("/confirm_booking", methods=["GET", "POST"])
def confirm_booking_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    if request.method == "POST":
        availability_id = request.form.get("availability_id")
        course_id = request.form.get("course_id")
        start_time = request.form.get("start_time")
        date = request.form.get("date")

        if not date:
            flash("Error: Please select a date to book this session.")
            return redirect(url_for("search_sessions_route"))

        try:
            time_str = str(start_time)
            if len(time_str.split(":")) == 2:
                time_str += ":00"

            session_datetime = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M:%S")

            exists = db.session.execute(
                session_exists,
                {"availability_id": availability_id, "session_datetime": session_datetime}
            ).fetchone()

            if exists:
                flash("Error: This session is already booked.")
                return redirect(url_for("search_sessions_route"))

            db.session.execute(
                insert_session,
                {
                    "email": session["user_email"],
                    "course_id": course_id,
                    "availability_id": availability_id,
                    "location": "Online",
                    "session_datetime": session_datetime
                }
            )
            db.session.commit()
        except ValueError:
            return redirect(url_for("dashboard_route"))
            
        return redirect(url_for("confirm_booking_route"))

    return render_template("confirm_booking.html")



if __name__ == "__main__":
    app.run(debug=True)