from sqlalchemy import text

search_sessions_query = text("""
    SELECT 
        ta.availability_id,
        ta.week_day,
        ta.start_time,
        ta.end_time,
        CONCAT(ta.week_day, ' ', ta.start_time) AS session_datetime,
        u.fname,
        u.lname,
        c.course_id,
        c.course_name
    FROM TutorAvailability ta
    JOIN Users u ON ta.tutor_email = u.email
    JOIN Teaches t ON u.email = t.tutor_email
    JOIN Courses c ON t.course_id = c.course_id
    WHERE 1=1
""")
my_sessions_query = text("""
    SELECT ts.session_id,
           ts.session_datetime,
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
      AND ts.session_status = 'scheduled'
    ORDER BY ts.session_datetime ASC
""")

available_sessions_query = text("""
    SELECT ta.availability_id,
           ta.week_day,
           ta.start_time,
           ta.end_time,
           CONCAT(ta.week_day, ' ', ta.start_time) AS display_time,
           u.fname,
           u.lname,
           c.course_id,
           c.course_name
    FROM TutorAvailability ta
    JOIN Users u ON ta.tutor_email = u.email
    JOIN Teaches t ON u.email = t.tutor_email
    JOIN Courses c ON t.course_id = c.course_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM TutorSession ts
        WHERE ts.availability_id = ta.availability_id
          AND ts.session_status = 'scheduled'
    )
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
    INSERT INTO TutorAvailability (tutor_email, week_day, start_time, end_time)
    VALUES (:tutor_email, :week_day, :start_time, :end_time)
""")

get_courses = text("""
    SELECT course_id, course_name
    FROM Courses
    WHERE course_name LIKE :q
    ORDER BY course_name
    LIMIT 10
""")