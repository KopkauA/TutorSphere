import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from backend.sql_queries import *
from backend.date import date_to_weekday, weekday_to_date

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# DB TEST
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
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
        
        with SessionLocal() as db:
            user = db.execute(
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

        with SessionLocal() as db:
            existing_user = db.execute(
                user_exists,
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

            db.execute(insert_user, params)
            db.commit()

        session['user_email'] = email

        if is_tutor == 1:
            return redirect(url_for('signup_tutor_route'))

        return redirect(url_for('dashboard_route'))

    return render_template('signup.html')


@app.route("/signup/tutor", methods=["GET", "POST"])
def signup_tutor_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    if request.method == "POST":

        email = session['user_email']

        with SessionLocal() as db:

            course_ids = request.form.get("course_ids")

            if course_ids:
                for cid in course_ids.split(","):
                    db.execute(
                        insert_teaches,
                        {"tutor_email": email, "course_id": cid}
                    )

            days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

            for day in days:
                start = request.form.get(f"{day}_start")
                end = request.form.get(f"{day}_end")
                location = request.form.get(f"{day}_location")

                if start and end and location:
                    db.execute(
                        insert_availability,
                        {
                            "tutor_email": email,
                            "week_day": day,
                            "shift_start_time": start,
                            "shift_end_time": end,
                            "tutor_location": location
                        }
                    )

            db.commit()

        return redirect(url_for("dashboard_route"))

    return render_template("signup_tutor.html")


@app.route("/api/courses")
def get_courses_route():
    q = request.args.get("q", "")

    with SessionLocal() as db:
        results = db.execute(
            get_courses,
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
    course_name = None
    selected_date = None
    selected_weekday = None

    if request.method == "POST":
        course_id = request.form.get("course")
        selected_date = request.form.get("time")

        if course_id:
            with SessionLocal() as db:
                c = db.execute(
                    get_course_name,
                    {"course_id": course_id}
                ).fetchone()
                if c:
                    course_name = c.course_name

        if selected_date:
            selected_weekday = date_to_weekday(selected_date)

        params = {
            "course_id": course_id,
            "selected_date": selected_date,
            "selected_weekday": selected_weekday,
            "user_email": session["user_email"]
        }

        with SessionLocal() as db:
            results = db.execute(
                available_sessions_query,
                params
            ).fetchall()

        sessions_list = []

        for row in results:
            r = row._mapping

            start_dt = datetime.strptime(str(r['shift_start_time']), "%H:%M:%S")
            end_dt = datetime.strptime(str(r['shift_end_time']), "%H:%M:%S")

            current = start_dt

            while current + timedelta(hours=1) <= end_dt:

                slot_start = current.time()
                slot_end = (current + timedelta(hours=1)).time()

                session_dict = dict(r)
                session_dict['session_start_time'] = slot_start.strftime("%H:%M:%S")
                session_dict['session_end_time'] = slot_end.strftime("%H:%M:%S")

                if not selected_date:
                    generated_date = weekday_to_date(str(r['week_day']))
                    session_dict['date'] = generated_date.strftime('%Y-%m-%d')
                else:
                    session_dict['date'] = selected_date

                with SessionLocal() as db:
                    is_booked = db.execute(
                        session_exists,
                        {
                            "availability_id": r['availability_id'],
                            "session_date": session_dict['date'],
                            "session_start_time": session_dict['session_start_time'],
                            "session_end_time": session_dict['session_end_time']
                        }
                    ).fetchone()

                    shift_conflict = db.execute(
                        tutor_shift_conflict,
                        {
                            "email": session["user_email"],
                            "week_day": str(r['week_day']),
                            "session_start_time": session_dict['session_start_time'],
                            "session_end_time": session_dict['session_end_time']
                        }
                    ).fetchone()

                if not is_booked and not shift_conflict:
                    sessions_list.append(session_dict)

                current += timedelta(hours=1)

    today = datetime.now().date()
    max_date = today + timedelta(days=7)

    return render_template(
        "session_search.html",
        sessions=sessions_list,
        course_id=course_id,
        course_name=course_name,
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

    email = session['user_email']

    with SessionLocal() as db:
        sessions = db.execute(
            student_sessions_query,
            {"email": email}
        ).fetchall()

        user = db.execute(
            get_role,
            {"email": email}
        ).fetchone()

        is_tutor = user.is_tutor if user else 0
        tutor_sessions = []

        if is_tutor == 1:
            tutor_sessions = db.execute(
                tutor_sessions_query,
                {"email": email}
            ).fetchall()

    return render_template("my_sessions.html", my_sessions=sessions, is_tutor=is_tutor, tutor_sessions=tutor_sessions)

@app.route("/dashboard")
def dashboard_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    with SessionLocal() as db:
        user = db.execute(
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
        session_location = request.form.get("session_location")
        date = request.form.get("date")

        with SessionLocal() as db:

            student_conflict = db.execute(
                student_schedule_conflict,
                {
                    "email": session["user_email"],
                    "session_date": date,
                    "session_start_time": session_start_time,
                    "session_end_time": session_end_time
                }
            ).fetchone()

            if student_conflict:
                return render_template("session_confirm.html", error="Schedule Conflict: Another session booked at this date and time")

            weekday = date_to_weekday(date)

            shift_conflict = db.execute(
                tutor_shift_conflict,
                {
                    "email": session["user_email"],
                    "week_day": weekday,
                    "session_start_time": session_start_time,
                    "session_end_time": session_end_time
                }
            ).fetchone()

            if shift_conflict:
                return render_template("session_confirm.html", error="Schedule Conflict: You are scheduled to tutor during this time.")

            exists = db.execute(
                session_exists,
                {
                    "availability_id": availability_id,
                    "session_date": date,
                    "session_start_time": session_start_time,
                    "session_end_time": session_end_time
                }
            ).fetchone()

            if exists:
                return render_template("session_confirm.html", error="This session slot is already booked.")

            db.execute(
                insert_session,{
                    "email": session["user_email"],
                    "course_id": course_id,
                    "availability_id": availability_id,
                    "location": session_location,
                    "session_start_time": session_start_time,
                    "session_end_time": session_end_time,
                    "session_date": date
                }
            )

            db.commit()

        return redirect(url_for("session_confirm_route"))

    return render_template("session_confirm.html")


@app.route("/session_cancel", methods=["GET", "POST"])
def session_cancel_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    if request.method == "POST":
        session_id = request.form.get("session_id")
        if session_id:
            with SessionLocal() as db:
                db.execute(
                    cancel_session,
                    {"session_id": session_id, "email": session['user_email']}
                )
                db.commit()

    return redirect(url_for("my_sessions_route"))


@app.route("/session_complete", methods=["POST"])
def session_complete_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    session_id = request.form.get("session_id")

    if session_id:
        with SessionLocal() as db:
            db.execute(
                complete_session,
                {"session_id": session_id}
            )
            db.commit()

    return redirect(url_for("my_sessions_route"))


@app.route("/myprofile", methods=["GET", "POST"])
def view_my_profile_route():
    if 'user_email' not in session:
        return redirect(url_for('login_route'))

    email = session['user_email']

    with SessionLocal() as db:

        user = db.execute(
            text("SELECT fname, lname, email, is_tutor FROM Users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if request.method == "POST" and user.is_tutor == 1:

            course_ids = request.form.get("course_ids", "")
            course_list = [c for c in course_ids.split(",") if c]

            db.execute(delete_teaches, {"email": email})

            for cid in course_list:
                existing = db.execute(text("""
                    SELECT 1 FROM Teaches
                    WHERE tutor_email = :email
                    AND course_id = :cid
                """), {
                    "email": email,
                    "cid": cid
                }).fetchone()

                if not existing:
                    db.execute(
                        insert_teaches,
                        {"tutor_email": email, "course_id": cid}
                    )

            db.execute(delete_availability, {"email": email})

            days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

            for day in days:
                start = request.form.get(f"{day}_start")
                end = request.form.get(f"{day}_end")
                location = request.form.get(f"{day}_location")

                if start and end and location:
                    db.execute(
                        insert_availability,
                        {
                            "tutor_email": email,
                            "week_day": day,
                            "shift_start_time": start,
                            "shift_end_time": end,
                            "tutor_location": location
                        }
                    )

            db.commit()
            return redirect(url_for("view_my_profile_route"))

        courses = []
        availability = []

        if user.is_tutor == 1:
            courses = db.execute(
                get_tutor_courses,
                {"email": user.email}
            ).fetchall()

            availability = db.execute(
                get_tutor_availability,
                {"email": user.email}
            ).fetchall()

    return render_template(
        "myprofile.html",
        user=user,
        courses=courses,
        availability=availability
    )


@app.route("/logout")
def logout_route():
    session.clear()
    return redirect(url_for("login_route"))

# get past data for profile
@app.route("/api/profile")
def api_profile():
    if 'user_email' not in session:
        return {"error": "not logged in"}, 401

    email = session['user_email']

    with SessionLocal() as db:

        courses = db.execute(
            get_tutor_courses,
            {"email": email}
        ).fetchall()

        availability_raw = db.execute(
            get_tutor_availability,
            {"email": email}
        ).fetchall()

    availability = []
    for a in availability_raw:
        row = dict(a._mapping)

        row["shift_start_time"] = str(row["shift_start_time"])[:-3]
        row["shift_end_time"] = str(row["shift_end_time"])[:-3]

        availability.append(row)

    return {
        "courses": [dict(c._mapping) for c in courses],
        "availability": availability
    }

if __name__ == "__main__":
    app.run(debug=True)