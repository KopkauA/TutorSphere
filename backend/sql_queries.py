from sqlalchemy import text

available_sessions_query = text("""
    SELECT 
        ta.availability_id,
        ta.week_day,
        ta.shift_start_time,
        ta.shift_end_time,
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
      AND NOT EXISTS (
            SELECT 1
            FROM TutorSession ts
            WHERE ts.availability_id = ta.availability_id
              AND ts.session_status = 'scheduled'
              AND (
                    (:selected_date IS NOT NULL AND ts.session_date = :selected_date)
                    OR
                    (:selected_date IS NULL AND ts.session_date >= CURRENT_DATE 
                        AND ts.session_date < DATE_ADD(CURRENT_DATE, INTERVAL 7 DAY))
              )
      )
    ORDER BY FIELD(
        ta.week_day,
        'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'
    ),
    ta.shift_start_time
""")

my_sessions_query = text("""
    SELECT 
        ts.session_id,
        ts.session_date,
        ts.session_start_time,
        ts.session_end_time,
        u.fname,
        u.lname,
        c.course_name,
        ts.session_status
    FROM TutorSession ts
    JOIN TutorAvailability ta ON ts.availability_id = ta.availability_id
    JOIN Users u ON ta.tutor_email = u.email
    JOIN Teaches t ON u.email = t.tutor_email
    JOIN Courses c ON t.course_id = c.course_id
    WHERE ts.student_email = :email
    ORDER BY ts.session_date ASC, ts.session_start_time ASC
""")

scheduled_sessions = text("""
    SELECT COUNT(ts.session_id) as upcoming_count
    FROM TutorSession ts
    JOIN TutorAvailability ta ON ts.availability_id = ta.availability_id
    WHERE (ts.student_email = :email OR ta.tutor_email = :email)
      AND ts.session_status = 'scheduled'
      AND ts.session_date >= CURRENT_DATE
""")

get_user = text("""
    SELECT *
    FROM Users
    WHERE email = :email AND password = :password
""")

get_courses = text("""
    SELECT course_id, course_name
    FROM Courses
    WHERE course_name LIKE :q
    ORDER BY course_name
    LIMIT 10
""")

session_exists = text("""
    SELECT 1
    FROM TutorSession
    WHERE availability_id = :availability_id
      AND session_date = :session_date
      AND session_start_time = :session_start_time
      AND session_status = 'scheduled'
""")

insert_user = text("""
    INSERT INTO Users (email, fname, lname, password, role)
    VALUES (:email, :fname, :lname, :password, :role)
""")

insert_teaches = text("""
    INSERT INTO Teaches (tutor_email, course_id)
    VALUES (:tutor_email, :course_id)
""")

insert_availability = text("""
    INSERT INTO TutorAvailability (tutor_email, week_day, session_start_time, session_end_time)
    VALUES (:tutor_email, :week_day, :session_start_time, :session_end_time)
""")

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
        'scheduled'
    )
""")

cancel_session = text("""
    UPDATE TutorSession
    SET session_status = 'canceled'
    WHERE session_id = :session_id
""")