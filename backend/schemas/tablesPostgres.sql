-- Works for postgreSQL
-- create_tables.sql
DROP TABLE IF EXISTS TutorSession;
DROP TABLE IF EXISTS TutorAvailability;
DROP TABLE IF EXISTS Teaches;
DROP TABLE IF EXISTS Subjects;
DROP TABLE IF EXISTS Users;

CREATE TYPE tutor_status_enum AS ENUM ('available', 'booked');
CREATE TYPE session_status_enum AS ENUM ('scheduled', 'completed', 'canceled');

CREATE TABLE Users (
  email         VARCHAR(100) PRIMARY KEY,
  fname         VARCHAR(100) NOT NULL,
  lname         VARCHAR(100) NOT NULL,
  password      VARCHAR(100) NOT NULL,
  role          VARCHAR(10) NOT NULL,
  CHECK         (role IN ('tutor', 'student'))
);

CREATE TABLE Subjects (
  subject_id         INTEGER PRIMARY KEY,
  subject_name       VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Teaches (
  tutor_email        VARCHAR(100) NOT NULL REFERENCES Users(email),
  subject_id         INTEGER NOT NULL REFERENCES Subjects(subject_id),
  PRIMARY KEY        (tutor_email, subject_id)
);

CREATE TABLE TutorAvailability (
  availability_id   INTEGER  NOT NULL PRIMARY KEY ,
  tutor_email       VARCHAR(100) NOT NULL REFERENCES Users(email),
  available_time    TIMESTAMP NOT NULL,
  tutor_status      tutor_status_enum NOT NULL
);

CREATE TABLE TutorSession
 (
  session_id        INTEGER PRIMARY KEY,
  tutor_email       VARCHAR(100) NOT NULL REFERENCES Users(email),
  student_email     VARCHAR(100) NOT NULL REFERENCES Users(email),
  subject_id        INTEGER NOT NULL REFERENCES Subjects(subject_id),
  availability_id   INTEGER NOT NULL UNIQUE  REFERENCES TutorAvailability(availability_id),
  session_location  VARCHAR(100) NOT NULL,
  session_status    session_status_enum NOT NULL
);