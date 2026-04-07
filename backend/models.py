from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'Users'
    email = db.Column(db.String(100), primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.Enum('tutor', 'student'))


class Subject(db.Model):
    __tablename__ = 'Subjects'
    subject_id = db.Column(db.String(20), primary_key=True)
    subject_name = db.Column(db.String(100), unique=True)


class Teaches(db.Model):
    __tablename__ = 'Teaches'
    tutor_email = db.Column(db.String(100), db.ForeignKey('Users.email'), primary_key=True)
    subject_id = db.Column(db.String(20), db.ForeignKey('Subjects.subject_id'), primary_key=True)


class TutorAvailability(db.Model):
    __tablename__ = 'TutorAvailability'
    availability_id = db.Column(db.Integer, primary_key=True)
    tutor_email = db.Column(db.String(100), db.ForeignKey('Users.email'))
    available_time = db.Column(db.DateTime)
    tutor_status = db.Column(db.Enum('available', 'booked'))


class TutorSession(db.Model):
    __tablename__ = 'TutorSession'
    session_id = db.Column(db.Integer, primary_key=True)
    tutor_email = db.Column(db.String(100), db.ForeignKey('Users.email'))
    student_email = db.Column(db.String(100), db.ForeignKey('Users.email'))
    subject_id = db.Column(db.String(20), db.ForeignKey('Subjects.subject_id'))
    availability_id = db.Column(
        db.Integer,
        db.ForeignKey('TutorAvailability.availability_id'),
        unique=True
    )
    session_location = db.Column(db.String(100))
    session_status = db.Column(db.Enum('scheduled', 'completed', 'canceled'))