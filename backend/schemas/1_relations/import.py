# app_import.py
import csv
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def import_users(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            email, fname, lname, password, role = row
            exists = db.session.execute(
                text("SELECT 1 FROM Users WHERE email = :email"),
                {"email": email}
            ).fetchone()
            if exists:
                continue
            db.session.execute(
                text("""
                    INSERT INTO Users (email, fname, lname, password, role)
                    VALUES (:email, :fname, :lname, :password, :role)
                """),
                {"email": email, "fname": fname, "lname": lname, "password": password, "role": role}
            )
    db.session.commit()
    print("Users imported.")

def import_subjects(file_path):
    """Import Subjects CSV."""
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            subject_id, subject_name = row
            exists = db.session.execute(
                text("SELECT 1 FROM Subjects WHERE subject_id = :id"),
                {"id": subject_id}
            ).fetchone()
            if exists:
                continue
            db.session.execute(
                text("INSERT INTO Subjects (subject_id, subject_name) VALUES (:id, :name)"),
                {"id": subject_id, "name": subject_name}
            )
    db.session.commit()
    print("Subjects imported.")

def import_teaches(file_path):
    """Import Teaches CSV."""
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            tutor_email, subject_id = row
            exists = db.session.execute(
                text("SELECT 1 FROM Teaches WHERE tutor_email = :tutor AND subject_id = :subject"),
                {"tutor": tutor_email, "subject": subject_id}
            ).fetchone()
            if exists:
                continue
            db.session.execute(
                text("INSERT INTO Teaches (tutor_email, subject_id) VALUES (:tutor, :subject)"),
                {"tutor": tutor_email, "subject": subject_id}
            )
    db.session.commit()
    print("Teaches imported.")

def import_tutor_availability(file_path):
    """Import TutorAvailability CSV."""
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            availability_id, tutor_email, available_time, tutor_status = row
            availability_id = int(availability_id)
            exists = db.session.execute(
                text("SELECT 1 FROM TutorAvailability WHERE availability_id = :id"),
                {"id": availability_id}
            ).fetchone()
            if exists:
                continue
            db.session.execute(
                text("""
                    INSERT INTO TutorAvailability
                    (availability_id, tutor_email, available_time, tutor_status)
                    VALUES (:id, :email, :time, :status)
                """),
                {"id": availability_id, "email": tutor_email, "time": available_time, "status": tutor_status}
            )
    db.session.commit()
    print("TutorAvailability imported.")

def import_tutor_session(file_path):
    """Import TutorSession CSV."""
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=[
            "session_id", "tutor_email", "student_email",
            "subject_id", "availability_id", "session_location", "session_status"
        ])
        for row in reader:
            session_id = int(row["session_id"])
            exists = db.session.execute(
                text("SELECT 1 FROM TutorSession WHERE session_id = :id"),
                {"id": session_id}
            ).fetchone()
            if exists:
                continue
            db.session.execute(
                text("""
                    INSERT INTO TutorSession
                    (session_id, tutor_email, student_email, subject_id, availability_id, session_location, session_status)
                    VALUES (:session_id, :tutor_email, :student_email, :subject_id, :availability_id, :location, :status)
                """),
                {
                    "session_id": session_id,
                    "tutor_email": row["tutor_email"],
                    "student_email": row["student_email"],
                    "subject_id": row["subject_id"],
                    "availability_id": int(row["availability_id"]),
                    "location": row["session_location"],
                    "status": row["session_status"]
                }
            )
    db.session.commit()
    print("TutorSession imported.")

if __name__ == "__main__":
    with app.app_context():
        import_users("Users.csv")
        import_subjects("Subjects.csv")
        import_teaches("Teaches.csv")
        import_tutor_availability("TutorAvailability.csv")
        import_tutor_session("TutorSession.csv")
        print("All mock data imported successfully!")