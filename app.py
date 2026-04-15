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

        is_tutor = int(request.form.get('is_tutor', 0))
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
            "is_tutor": is_tutor
        }

        db.session.execute(insert_user, params)
        db.session.commit()

        if is_tutor == 1:
            session['user_email'] = params['email']
            return redirect(url_for('signup_tutor_route'))

        return redirect(url_for('login_route'))

    return render_template('signup.html')


@app.route("/signup/tutor", methods=["GET", "POST"])
def signup_tutor_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    if request.method == "POST":

        email = session['user_email']

        # courses
        course_ids = request.form.get("course_ids")

        if course_ids:
            for cid in course_ids.split(","):
                db.session.execute(
                    text("""
                        INSERT INTO Teaches (tutor_email, course_id)
                        VALUES (:email, :course_id)
                    """),
                    {"email": email, "course_id": cid}
                )

        # availability and location
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

        for day in days:
            start = request.form.get(f"{day}_start")
            end = request.form.get(f"{day}_end")
            location = request.form.get(f"{day}_location")

            if start and end and location:
                db.session.execute(
                    text("""
                        INSERT INTO TutorAvailability 
                        (tutor_email, week_day, shift_start_time, shift_end_time, tutor_location)
                        VALUES (:email, :day, :start, :end, :location)
                    """),
                    {
                        "email": email,
                        "day": day,
                        "start": start,
                        "end": end,
                        "location": location
                    }
                )
        #commit changes
        db.session.commit()

        return redirect(url_for("dashboard_route"))

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

                # Check if this specific 1-hour slot is already booked
                is_booked = db.session.execute(
                    session_exists,
                    {
                        "availability_id": r['availability_id'],
                        "session_date": session_dict['date'],
                        "session_start_time": session_dict['session_start_time']
                    }
                ).fetchone()

                if not is_booked:
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

    user = db.session.execute(
        text("SELECT fname, lname, is_tutor FROM Users WHERE email = :email"),
        {"email": session['user_email']}
    ).fetchone()

    role = "Tutor" if user.is_tutor == 1 else "Student"

    return render_template("dashboard.html", user=user, role=role)

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

        if exists:
            return render_template("session_confirm.html", error="This session slot is already booked.")

        # Check for a canceled session to re-book
        canceled_session = db.session.execute(
            get_canceled_session,
            {
                "availability_id": availability_id,
                "session_date": date,
                "session_start_time": session_start_time
            }
        ).fetchone()

        if canceled_session:
            # Re-book by updating the existing canceled session
            db.session.execute(
                rebook_session,
                {
                    "session_id": canceled_session.session_id,
                    "email": session["user_email"],
                    "course_id": course_id
                }
            )
        else:
            # Insert a new session
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

    if request.method == "POST":
        session_id = request.form.get("session_id")
        if session_id:
            db.session.execute(
                cancel_session,
                {"session_id": session_id}
            )
            db.session.commit()

    return redirect(url_for("my_sessions_route"))


if __name__ == "__main__":
    app.run(debug=True)