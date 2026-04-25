from sqlalchemy import text

# Gets available tutoring sessions
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
      AND ta.tutor_email != :user_email
      AND ta.is_active = 1
                                
    ORDER BY FIELD(
        ta.week_day,
        'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'
    ),
    ta.shift_start_time
""")

# Get sessions student attends
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

# Gets sessions tutors conduct
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

# Gets user's information given email and password
get_user = text("""
    SELECT *
    FROM Users
    WHERE email = :email AND password = :password
""")

# Gets course name given course id
get_course_name = text("""
    SELECT course_name
    FROM Courses
    WHERE course_id = :course_id
""")

# Autocomplete course name
get_courses = text("""
    SELECT course_id, course_name
    FROM Courses
    WHERE course_name LIKE :q
    ORDER BY course_name
    LIMIT 10
""")

# Get user's role
get_role = text("""
    SELECT is_tutor FROM Users 
    WHERE email = :email
""")

# Determine if a session exists
session_exists = text("""
    SELECT 1
    FROM TutorSession
    WHERE availability_id = :availability_id
      AND session_date = :session_date
      AND session_start_time < :session_end_time
      AND session_end_time > :session_start_time
      AND session_status != 'Canceled'
""")

# Check if student booked another session during that timeslot
student_schedule_conflict = text("""
    SELECT 1 
    FROM TutorSession 
    WHERE student_email = :email
      AND session_date = :session_date
      AND session_start_time < :session_end_time
      AND session_end_time > :session_start_time
      AND session_status = 'Scheduled'
""")

# Check if a session overlaps with the tutor's shift
tutor_shift_conflict = text("""
    SELECT 1 
    FROM TutorAvailability 
    WHERE tutor_email = :email
      AND is_active = 1
      AND week_day = :week_day
      AND shift_start_time < :session_end_time
      AND shift_end_time > :session_start_time
""")

# Insert user
insert_user = text("""
    INSERT INTO Users (email, fname, lname, password, is_tutor)
    VALUES (:email, :fname, :lname, :password, :is_tutor)
""")

# Insert what tutor teaches
insert_teaches = text("""
    INSERT INTO Teaches (tutor_email, course_id)
    VALUES (:tutor_email, :course_id)
""")

# Insert tutor's availability
insert_availability = text("""
    INSERT INTO TutorAvailability (tutor_email, week_day, shift_start_time, shift_end_time, tutor_location, is_active)
    VALUES (:tutor_email, :week_day, :shift_start_time, :shift_end_time, :tutor_location, 1)
    ON DUPLICATE KEY UPDATE 
        tutor_location = VALUES(tutor_location), 
        is_active = 1
""")

# Insert session
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

# Determine if user exists
user_exists = text("""
    SELECT 1 
    FROM Users 
    WHERE email = :email
""")

# Mark session as canceled
cancel_session = text("""
    UPDATE TutorSession
    SET session_status = 'Canceled'
    WHERE session_id = :session_id 
      AND session_status = 'Scheduled'
      AND (student_email = :email OR availability_id IN (
          SELECT availability_id FROM TutorAvailability WHERE tutor_email = :email
      ))
""")

# Mark session as complete
complete_session = text("""
    UPDATE TutorSession
    SET session_status = 'Completed'
    WHERE session_id = :session_id
""")

# Delete teaches row from Teaches
delete_teaches = text("""
    DELETE FROM Teaches WHERE tutor_email = :email
""")

# Change tutor's availability
delete_availability = text("""
    UPDATE TutorAvailability
    SET is_active = 0
    WHERE tutor_email = :email
""")

# Get courses a tutor teaches
get_tutor_courses = text("""
    SELECT c.course_id, c.course_name
    FROM Teaches t
    JOIN Courses c ON t.course_id = c.course_id
    WHERE t.tutor_email = :email
""")

# Get tutor's availability
get_tutor_availability = text("""
    SELECT 
        week_day, 
        shift_start_time, 
        shift_end_time, 
        tutor_location
    FROM TutorAvailability
    WHERE tutor_email = :email AND is_active = 1
    ORDER BY FIELD(
        week_day,
        'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'
    ),
    shift_start_time
""")