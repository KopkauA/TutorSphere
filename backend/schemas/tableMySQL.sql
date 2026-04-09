-- Works for MySQL
-- create_tables.sql
DROP TABLE IF EXISTS TutorSession;
DROP TABLE IF EXISTS TutorAvailability;
DROP TABLE IF EXISTS Teaches;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
  email VARCHAR(100) PRIMARY KEY,
  fname VARCHAR(100) NOT NULL,
  lname VARCHAR(100) NOT NULL,
  password VARCHAR(100) NOT NULL,
  role ENUM('tutor', 'student') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Courses (
  course_id VARCHAR(20) NOT NULL PRIMARY KEY,
  course_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE Teaches (
  tutor_email VARCHAR(100) NOT NULL,
  course_id VARCHAR(20) NOT NULL,
  PRIMARY KEY (tutor_email, course_id),
  FOREIGN KEY (tutor_email) REFERENCES Users(email),
  FOREIGN KEY (course_id) REFERENCES Courses(course_id)
) ENGINE=InnoDB;

CREATE TABLE TutorAvailability (
  availability_id INT AUTO_INCREMENT PRIMARY KEY,
  tutor_email VARCHAR(100) NOT NULL,
  week_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  --Prevent duplicate entries
  UNIQUE (tutor_email, week_day, start_time, end_time),
  FOREIGN KEY (tutor_email) REFERENCES Users(email)
) ENGINE=InnoDB;

CREATE TABLE TutorSession (
  session_id INT AUTO_INCREMENT PRIMARY KEY,
  student_email VARCHAR(100) NOT NULL,
  course_id VARCHAR(20) NOT NULL,
  availability_id INT NOT NULL,
  session_location VARCHAR(100) NOT NULL,
  session_datetime DATETIME NOT NULL,
  session_status ENUM('scheduled', 'completed', 'canceled') NOT NULL,

  UNIQUE (availability_id, session_datetime),

  FOREIGN KEY (student_email) REFERENCES Users(email),
  FOREIGN KEY (course_id) REFERENCES Courses(course_id),
  FOREIGN KEY (availability_id) REFERENCES TutorAvailability(availability_id)
) ENGINE=InnoDB;

CREATE INDEX idx_tutor_availability 
ON TutorAvailability(tutor_email, week_day);

CREATE INDEX idx_session_datetime 
ON TutorSession(session_datetime);