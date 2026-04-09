# import.py
import csv
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- USERS ----------------
def import_users(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for email, fname, lname, password, role in reader:
            exists = db.session.execute(
                text("SELECT 1 FROM Users WHERE email=:email"),
                {"email": email}
            ).fetchone()

            if exists:
                continue

            db.session.execute(text("""
                INSERT INTO Users (email, fname, lname, password, role)
                VALUES (:email, :fname, :lname, :password, :role)
            """), {
                "email": email,
                "fname": fname,
                "lname": lname,
                "password": password,
                "role": role
            })

    db.session.commit()
    print(" Users imported")


# ---------------- COURSES ----------------
def import_courses(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for course_id, course_name in reader:
            exists = db.session.execute(
                text("SELECT 1 FROM Courses WHERE course_id=:id"),
                {"id": course_id}
            ).fetchone()

            if exists:
                continue

            db.session.execute(text("""
                INSERT INTO Courses (course_id, course_name)
                VALUES (:id, :name)
            """), {
                "id": course_id,
                "name": course_name
            })

    db.session.commit()
    print(" Courses imported")


# ---------------- TEACHES ----------------
def import_teaches(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for tutor_email, course_id in reader:
            exists = db.session.execute(text("""
                SELECT 1 FROM Teaches 
                WHERE tutor_email=:t AND course_id=:c
            """), {"t": tutor_email, "c": course_id}).fetchone()

            if exists:
                continue

            db.session.execute(text("""
                INSERT INTO Teaches (tutor_email, course_id)
                VALUES (:t, :c)
            """), {"t": tutor_email, "c": course_id})

    db.session.commit()
    print(" Teaches imported")


# ---------------- AVAILABILITY ----------------
def import_tutor_availability(file_path):
    """Import TutorAvailability CSV - skip header row."""
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            availability_id, tutor_email, week_day, start_time, end_time = row
            availability_id = int(availability_id)
            
            # Check if availability already exists
            exists = db.session.execute(
                text("SELECT 1 FROM TutorAvailability WHERE availability_id = :id"),
                {"id": availability_id}
            ).fetchone()
            if exists:
                print(f"Availability {availability_id} already exists, skipping...")
                continue
            
            # Verify tutor exists
            tutor = db.session.execute(
                text("SELECT 1 FROM Users WHERE email = :email AND role = 'tutor'"),
                {"email": tutor_email}
            ).fetchone()
            if not tutor:
                print(f" Warning: {tutor_email} is not a valid tutor, skipping availability {availability_id}...")
                continue
            
            # Insert availability (without tutor_status)
            db.session.execute(
                text("""
                    INSERT INTO TutorAvailability 
                    (availability_id, tutor_email, week_day, start_time, end_time)
                    VALUES (:id, :email, :week_day, :start, :end)
                """),
                {
                    "id": availability_id,
                    "email": tutor_email,
                    "week_day": week_day,
                    "start": start_time,
                    "end": end_time
                }
            )
            print(f"Imported availability: ID {availability_id} for {tutor_email} on {week_day} {start_time}-{end_time}")
    
    db.session.commit()
    print("TutorAvailability imported successfully.\n")

# ---------------- SESSIONS ----------------
def import_tutor_session(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            (
                session_id,
                student_email,
                course_id,
                availability_id,
                session_location,
                session_datetime,
                session_status
            ) = row

            exists = db.session.execute(text("""
                SELECT 1 FROM TutorSession WHERE session_id=:id
            """), {"id": session_id}).fetchone()

            if exists:
                continue

            db.session.execute(text("""
                INSERT INTO TutorSession
                (session_id, student_email, course_id, availability_id,
                 session_location, session_datetime, session_status)
                VALUES (:sid, :student, :course, :aid, :loc, :dt, :status)
            """), {
                "sid": int(session_id),
                "student": student_email,
                "course": course_id,
                "aid": int(availability_id),
                "loc": session_location,
                "dt": session_datetime,
                "status": session_status
            })

    db.session.commit()
    print("Sessions imported")


# ---------------- CLEAR ----------------
def clear_all():
    db.session.execute(text("DELETE FROM TutorSession"))
    db.session.execute(text("DELETE FROM TutorAvailability"))
    db.session.execute(text("DELETE FROM Teaches"))
    db.session.execute(text("DELETE FROM Courses"))
    db.session.execute(text("DELETE FROM Users"))
    db.session.commit()
    print(" Database cleared")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    with app.app_context():
        base = os.path.dirname(os.path.abspath(__file__))

        users = os.path.join(base, "Users.csv")
        courses = os.path.join(base, "Courses.csv")
        teaches = os.path.join(base, "Teaches.csv")
        availability = os.path.join(base, "TutorAvailability.csv")
        sessions = os.path.join(base, "TutorSession.csv")

        if input("Clear DB first? (y/n): ").lower() == "y":
            clear_all()

        print("\nImporting...\n")

        import_users(users)
        import_courses(courses)
        import_teaches(teaches)
        import_tutor_availability(availability)
        import_tutor_session(sessions)

        print("\n DONE")