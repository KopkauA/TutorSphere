import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import text
from dotenv import load_dotenv

from backend.models import db
from backend.sql_queries import *
from backend.date import date_to_weekday, weekday_to_date

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

@app.route("/")
def login():
    return render_template("login.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login_route():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = db.session.execute(
            get_user,
            {"email": email, "password": password}
        ).fetchone()

        if user:
            session['user_email'] = email
            return redirect(url_for("dashboard_route"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# SIGNUP
@app.route('/signup_route', methods=['GET', 'POST'])
def signup_route():

    if request.method == 'POST':

        role = request.form.get('role', 'student')
        email = request.form['email']

        existing_user = db.session.execute(
            text("SELECT 1 FROM Users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if existing_user:
            return render_template(
                'signup.html',
                error="There is already an account with this email."
            )

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

        return redirect(url_for('login_route'))

    return render_template('signup.html')


@app.route("/signup/tutor", methods=["GET", "POST"])
def signup_tutor_route():
    return render_template("signup_tutor.html")

@app.route("/api/courses")
def get_courses():
    q = request.args.get("q", "")

    results = db.session.execute(
        text("SELECT course_id, course_name FROM Courses WHERE course_name LIKE :q LIMIT 10"),
        {"q": f"%{q}%"}
    ).fetchall()

    return {
        "courses": [
            {"id": r.course_id, "name": r.course_name}
            for r in results
        ]
    }

# SEARCH SESSIONS
@app.route("/search", methods=["GET", "POST"])
def search_sessions_route():

    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    sessions_list = []
    course_id = None
    selected_date = None
    selected_weekday = None

    if request.method == "POST":
        course_id = request.form.get("course")
        selected_date = request.form.get("time")

        if not selected_date:
            selected_date = None

        if selected_date:
            selected_weekday = date_to_weekday(selected_date)

        params = {
            "course_id": course_id,
            "selected_date": selected_date,
            "selected_weekday": selected_weekday
        }

        results = db.session.execute(
            available_sessions_query,
            params
        ).fetchall()

        sessions_list = []

        for row in results:
            r = row._mapping

            start_dt = datetime.strptime(str(r['shift_start_time']), "%H:%M:%S")
            end_dt = datetime.strptime(str(r['shift_end_time']), "%H:%M:%S")

            # Generate 1 hour slots inside the shift
            current = start_dt

            while current + timedelta(hours=1) <= end_dt:

                slot_start = current.time()
                slot_end = (current + timedelta(hours=1)).time()

                session_dict = dict(r)
                session_dict['session_start_time'] = slot_start.strftime("%H:%M:%S")
                session_dict['session_end_time'] = slot_end.strftime("%H:%M:%S")

                # assign date
                if not selected_date:
                    generated_date = weekday_to_date(str(r['week_day']))
                    session_dict['date'] = generated_date.strftime('%Y-%m-%d')
                else:
                    session_dict['date'] = selected_date

                sessions_list.append(session_dict)

                current += timedelta(hours=1)

    today = datetime.now().date()
    max_date = today + timedelta(days=7)

    return render_template(
        "session_search.html",
        sessions=sessions_list,
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

    return render_template("my_sessions.html", my_sessions=sessions)

@app.route("/dashboard")
def dashboard_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    return render_template("dashboard.html")

@app.route("/session_confirm", methods=["GET", "POST"])
def session_confirm_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    if request.method == "POST":
        availability_id = request.form.get("availability_id")
        course_id = request.form.get("course_id")
        session_start_time = request.form.get("session_start_time")
        session_end_time = request.form.get("session_end_time")
        date = request.form.get("date")

        # Check if session already exists
        exists = db.session.execute(
            session_exists,
            {
                "availability_id": availability_id,
                "session_date": date,
                "session_start_time": session_start_time
            }
        ).fetchone()

        # Insert session
        db.session.execute(
            insert_session,
            {
                "email": session["user_email"],
                "course_id": course_id,
                "availability_id": availability_id,
                "location": "Online",
                "session_start_time": session_start_time,
                "session_end_time": session_end_time,
                "session_date": date
            }
        )

        db.session.commit()
        return redirect(url_for("session_confirm_route"))

    return render_template("session_confirm.html")

@app.route("/session_cancel", methods=["GET", "POST"])
def session_cancel_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    return render_template("my_sessions.html")


if __name__ == "__main__":
    app.run(debug=True)