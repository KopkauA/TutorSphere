from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'Users'

    email = db.Column(db.String(100), primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('tutor', 'student'), nullable=False)


class Course(db.Model):
    __tablename__ = 'Courses'

    course_id = db.Column(db.String(20), primary_key=True)
    course_name = db.Column(db.String(100), unique=True, nullable=False)


class Teaches(db.Model):
    __tablename__ = 'Teaches'

    tutor_email = db.Column(
        db.String(100),
        db.ForeignKey('Users.email'),
        primary_key=True
    )
    course_id = db.Column(
        db.String(20),
        db.ForeignKey('Courses.course_id'),
        primary_key=True
    )


class TutorAvailability(db.Model):
    __tablename__ = 'TutorAvailability'

    availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    tutor_email = db.Column(
        db.String(100),
        db.ForeignKey('Users.email'),
        nullable=False
    )

    week_day = db.Column(
        db.Enum(
            'Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday'
        ),
        nullable=False
    )

    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            'tutor_email', 'week_day', 'start_time', 'end_time',
            name='unique_availability'
        ),
    )


class TutorSession(db.Model):
    __tablename__ = 'TutorSession'

    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    student_email = db.Column(
        db.String(100),
        db.ForeignKey('Users.email'),
        nullable=False
    )

    course_id = db.Column(
        db.String(20),
        db.ForeignKey('Courses.course_id'),
        nullable=False
    )

    availability_id = db.Column(
        db.Integer,
        db.ForeignKey('TutorAvailability.availability_id'),
        nullable=False
    )

    session_location = db.Column(db.String(100), nullable=False)

    session_datetime = db.Column(db.DateTime, nullable=False)

    session_status = db.Column(
        db.Enum('scheduled', 'completed', 'canceled'),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            'availability_id', 'session_datetime',
            name='unique_session_slot'
        ),
    )