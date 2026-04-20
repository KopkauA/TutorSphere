from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------------- USERS ----------------
class User(db.Model):
    __tablename__ = 'Users'

    email = db.Column(db.String(100), primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_tutor = db.Column(db.SmallInteger, nullable=False, default=0)


# ---------------- COURSES ----------------
class Course(db.Model):
    __tablename__ = 'Courses'

    course_id = db.Column(db.String(20), primary_key=True)
    course_name = db.Column(db.String(100), unique=True, nullable=False)


# ---------------- TEACHES ----------------
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


# ---------------- AVAILABILITY ----------------
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

    tutor_location = db.Column(db.String(50))
    shift_start_time = db.Column(db.Time, nullable=False)
    shift_end_time = db.Column(db.Time, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            'tutor_email',
            'week_day',
            'shift_start_time',
            'shift_end_time',
            name='unique_availability'
        ),
    )


# ---------------- SESSIONS ----------------
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

    session_date = db.Column(db.Date, nullable=False)
    session_start_time = db.Column(db.Time, nullable=False)
    session_end_time = db.Column(db.Time, nullable=False)

    session_status = db.Column(
        db.Enum('Scheduled', 'Completed', 'Canceled'),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            'availability_id',
            'session_date',
            'session_start_time',
            name='unique_session_slot'
        ),
    )