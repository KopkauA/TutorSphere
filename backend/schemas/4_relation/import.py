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


def import_users(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for email, fname, lname, password, is_tutor in reader:
            email = email.strip()
            fname = fname.strip()
            lname = lname.strip()
            password = password.strip()
            is_tutor = int(is_tutor.strip())

            exists = db.session.execute(
                text("SELECT 1 FROM Users WHERE email=:email"),
                {"email": email}
            ).fetchone()

            if exists:
                continue

            db.session.execute(text("""
                INSERT INTO Users (email, fname, lname, password, is_tutor)
                VALUES (:email, :fname, :lname, :password, :is_tutor)
            """), {
                "email": email,
                "fname": fname,
                "lname": lname,
                "password": password,
                "is_tutor": is_tutor
            })

    db.session.commit()


def import_courses(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for course_id, course_name in reader:
            course_id = course_id.strip()
            course_name = course_name.strip()

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


def import_teaches(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for tutor_email, course_id in reader:
            tutor_email = tutor_email.strip()
            course_id = course_id.strip()

            tutor = db.session.execute(text("""
                SELECT 1 FROM Users
                WHERE email=:email AND is_tutor=1
            """), {"email": tutor_email}).fetchone()

            course = db.session.execute(text("""
                SELECT 1 FROM Courses WHERE course_id=:id
            """), {"id": course_id}).fetchone()

            if not tutor or not course:
                continue

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


def import_tutor_availability(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            availability_id, tutor_email, week_day, start_time, end_time, tutor_location = [x.strip() for x in row]

            availability_id = int(availability_id)

            tutor = db.session.execute(text("""
                SELECT 1 FROM Users
                WHERE email=:email AND is_tutor=1
            """), {"email": tutor_email}).fetchone()

            if not tutor:
                continue

            exists = db.session.execute(text("""
                SELECT 1 FROM TutorAvailability
                WHERE availability_id=:id
            """), {"id": availability_id}).fetchone()

            if exists:
                continue

            db.session.execute(text("""
                INSERT INTO TutorAvailability
                (availability_id, tutor_email, week_day, shift_start_time, shift_end_time, tutor_location)
                VALUES (:id, :email, :day, :start, :end, :loc)
            """), {
                "id": availability_id,
                "email": tutor_email,
                "day": week_day,
                "start": start_time,
                "end": end_time,
                "loc": tutor_location
            })

    db.session.commit()


def import_tutor_session(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            session_id, student_email, course_id, availability_id, session_location, session_start_time, session_end_time, session_date, session_status = [x.strip() for x in row]

            session_id = int(session_id)
            availability_id = int(availability_id)

            student = db.session.execute(text("""
                SELECT 1 FROM Users WHERE email=:email
            """), {"email": student_email}).fetchone()

            course = db.session.execute(text("""
                SELECT 1 FROM Courses WHERE course_id=:id
            """), {"id": course_id}).fetchone()

            availability = db.session.execute(text("""
                SELECT 1 FROM TutorAvailability WHERE availability_id=:id
            """), {"id": availability_id}).fetchone()

            if not student or not course or not availability:
                continue

            exists = db.session.execute(text("""
                SELECT 1 FROM TutorSession
                WHERE session_id=:id
            """), {"id": session_id}).fetchone()

            if exists:
                continue

            db.session.execute(text("""
                INSERT INTO TutorSession
                (session_id, student_email, course_id, availability_id,
                 session_location, session_start_time, session_end_time,
                 session_date, session_status)
                VALUES
                (:sid, :student, :course, :aid, :loc,
                 :start, :end, :date, :status)
            """), {
                "sid": session_id,
                "student": student_email,
                "course": course_id,
                "aid": availability_id,
                "loc": session_location,
                "start": session_start_time,
                "end": session_end_time,
                "date": session_date,
                "status": session_status
            })

    db.session.commit()


def clear_all():
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    db.session.execute(text("DELETE FROM TutorSession"))
    db.session.execute(text("DELETE FROM TutorAvailability"))
    db.session.execute(text("DELETE FROM Teaches"))
    db.session.execute(text("DELETE FROM Courses"))
    db.session.execute(text("DELETE FROM Users"))
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    db.session.commit()


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

        import_users(users)
        import_courses(courses)
        import_teaches(teaches)
        import_tutor_availability(availability)
        import_tutor_session(sessions)

        print("DONE")