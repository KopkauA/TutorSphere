from sqlalchemy import text

available_sessions_query = text("""
    SELECT 
        ta.availability_id,
        ta.week_day,
        ta.shift_start_time,
        ta.shift_end_time,
        ta.tutor_location,
        u.fname,
        u.lname,
        c.course_id,
        c.course_name
    FROM TutorAvailability ta
    JOIN Users u ON ta.tutor_email = u.email
    JOIN Teaches t ON u.email = t.tutor_email
    JOIN Courses c ON t.course_id = c.course_id
    WHERE c.course_id = :course_id
      AND (:selected_weekday IS NULL OR ta.week_day = :selected_weekday)
    ORDER BY FIELD(
        ta.week_day,
        'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'
    ),
    ta.shift_start_time
""")

student_sessions_query = text("""
    SELECT 
        ts.session_id,
        ts.session_date,
        ts.session_start_time,
        ts.session_end_time,
        u.fname,
        u.lname,
        c.course_name,
        ts.session_status,
        ts.session_location
    FROM TutorSession ts
    JOIN TutorAvailability ta ON ts.availability_id = ta.availability_id
    JOIN Users u ON ta.tutor_email = u.email
    JOIN Courses c ON ts.course_id = c.course_id
    WHERE ts.student_email = :email
    ORDER BY ts.session_date ASC, ts.session_start_time ASC
""")

tutor_sessions_query = text("""
    SELECT 
        ts.session_id,
        c.course_name,
        ts.session_date,
        ts.session_start_time,
        ts.session_end_time,
        u.fname,
        u.lname,
        ts.session_location,
        ts.session_status
    FROM TutorSession ts
    JOIN Courses c ON ts.course_id = c.course_id
    JOIN TutorAvailability ta ON ts.availability_id = ta.availability_id
    JOIN Users u ON ts.student_email = u.email
    WHERE ta.tutor_email = :email
    ORDER BY ts.session_date, ts.session_start_time
""")

scheduled_sessions = text("""
    SELECT COUNT(ts.session_id) as upcoming_count
    FROM TutorSession ts
    JOIN TutorAvailability ta ON ts.availability_id = ta.availability_id
    WHERE (ts.student_email = :email OR ta.tutor_email = :email)
      AND ts.session_status = 'Scheduled'
      AND ts.session_date >= CURRENT_DATE
""")

get_user = text("""
    SELECT *
    FROM Users
    WHERE email = :email AND password = :password
""")

get_course_name = text("""
    SELECT course_name
    FROM Courses
    WHERE course_id = :course_id
""")


get_courses = text("""
    SELECT course_id, course_name
    FROM Courses
    WHERE course_name LIKE :q
    ORDER BY course_name
    LIMIT 10
""")

get_role = text("""
    SELECT is_tutor FROM Users WHERE email = :email
""")

session_exists = text("""
    SELECT 1
    FROM TutorSession
    WHERE availability_id = :availability_id
      AND session_date = :session_date
      AND session_start_time = :session_start_time
      AND session_status = 'Scheduled'
""")

student_schedule_conflict = text("""
    SELECT 1 
    FROM TutorSession 
    WHERE student_email = :email
      AND session_date = :session_date
      AND session_start_time = :session_start_time
      AND session_status = 'Scheduled'
""")

insert_user = text("""
    INSERT INTO Users (email, fname, lname, password, is_tutor)
    VALUES (:email, :fname, :lname, :password, :is_tutor)
""")

insert_teaches = text("""
    INSERT INTO Teaches (tutor_email, course_id)
    VALUES (:tutor_email, :course_id)
""")

insert_availability = text("""
    INSERT INTO TutorAvailability (tutor_email, week_day, shift_start_time, shift_end_time, tutor_location)
    VALUES (:tutor_email, :week_day, :shift_start_time, :shift_end_time, :tutor_location)"""
)

insert_session = text("""
    INSERT INTO TutorSession (
        student_email,
        course_id,
        availability_id,
        session_location,
        session_start_time,
        session_end_time,
        session_date,
        session_status
    )
    VALUES (
        :email,
        :course_id,
        :availability_id,
        :location,
        :session_start_time,
        :session_end_time,
        :session_date,
        'Scheduled'
    )
""")

user_exists = text("""
    SELECT 1 
    FROM Users 
    WHERE email = :email
""")


rebook_session = text("""
    UPDATE TutorSession
    SET student_email = :email,
        course_id = :course_id,
        session_status = 'Scheduled',
        session_date = :session_date,
        session_start_time = :session_start_time,
        session_end_time = :session_end_time,
        session_location = :location
    WHERE session_id = :session_id
""")

get_canceled_session = text("""
    SELECT session_id
    FROM TutorSession
    WHERE availability_id = :availability_id
      AND session_date = :session_date
      AND session_start_time = :session_start_time
      AND session_status = 'Canceled'
""")

cancel_session = text("""
    UPDATE TutorSession
    SET session_status = 'Canceled'
    WHERE session_id = :session_id
""")

delete_teaches = text("""
    DELETE FROM Teaches WHERE tutor_email = :email
""")

delete_availability = text("""
    DELETE FROM TutorAvailability ta
    WHERE ta.tutor_email = :email
      AND NOT EXISTS (
          SELECT 1
          FROM TutorSession ts
          WHERE ts.availability_id = ta.availability_id
      )
""")

get_tutor_courses = text("""
    SELECT c.course_id, c.course_name
    FROM Teaches t
    JOIN Courses c ON t.course_id = c.course_id
    WHERE t.tutor_email = :email
""")

get_tutor_availability = text("""
    SELECT week_day, shift_start_time, shift_end_time, tutor_location
    FROM TutorAvailability
    WHERE tutor_email = :email 
""")
