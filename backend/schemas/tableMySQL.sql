-- Works for MySQL
-- create_tables.sql
DROP TABLE IF EXISTS TutorSession;
DROP TABLE IF EXISTS TutorAvailability;
DROP TABLE IF EXISTS Teaches;
DROP TABLE IF EXISTS Subjects;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
  email VARCHAR(100) PRIMARY KEY,
  fname VARCHAR(100) NOT NULL,
  lname VARCHAR(100) NOT NULL,
  password VARCHAR(100) NOT NULL,
  role ENUM('tutor', 'student') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Subjects (
  subject_id VARCHAR(20) NOT NULL PRIMARY KEY,
  subject_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE Teaches (
  tutor_email VARCHAR(100) NOT NULL,
  subject_id VARCHAR(20) NOT NULL,
  PRIMARY KEY (tutor_email, subject_id),
  FOREIGN KEY (tutor_email) REFERENCES Users(email),
  FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id)
) ENGINE=InnoDB;

CREATE TABLE TutorAvailability (
  availability_id INT NOT NULL PRIMARY KEY,
  tutor_email VARCHAR(100) NOT NULL,
  available_time DATETIME NOT NULL UNIQUE,
  tutor_status ENUM('available', 'booked') NOT NULL,
  FOREIGN KEY (tutor_email) REFERENCES Users(email)
) ENGINE=InnoDB;

CREATE TABLE TutorSession (
  session_id INT NOT NULL PRIMARY KEY,
  tutor_email VARCHAR(100) NOT NULL,
  student_email VARCHAR(100) NOT NULL,
  subject_id VARCHAR(20) NOT NULL,
  availability_id INT NOT NULL UNIQUE,
  session_location VARCHAR(100) NOT NULL,
  session_status ENUM('scheduled', 'completed', 'canceled') NOT NULL,
  FOREIGN KEY (tutor_email) REFERENCES Users(email),
  FOREIGN KEY (student_email) REFERENCES Users(email),
  FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id),
  FOREIGN KEY (availability_id) REFERENCES TutorAvailability(availability_id)
) ENGINE=InnoDB;
