# TutorSphere

Authors: Aubrey Kopkau and Chloe Robinson

Tutor scheduling website created using a SQL database
# Setup Guide

This guide walks you through setting up the database and running the application locally.

---

## 1. Install MySQL

- Download and install **MySQL Community Edition**
- During installation, **set your root password**
---

## 2. Create the Database

1. Open **MySQL 8.0 Command Line Client**
2. Enter your password
3. Run the following commands:

```sql
CREATE DATABASE tutor_sphere;
USE tutor_sphere;
```

---

## 3. Create Tables

1. Open **Command Prompt (CMD on Windows)**

2. Run:

```bash
mysql -u <username> -p tutor_sphere < /path/to/tablesMySQL.sql
```

### If `mysql` command is not recognized:

Add MySQL to PATH. For example:

```
C:\Program Files\MySQL\MySQL Server 8.0\bin
```

---

## 4. Verify Tables

Inside the MySQL command line:

```sql
USE tutor_sphere;

SHOW TABLES;

DESCRIBE USERS;
DESCRIBE SUBJECTS;
```

---

## 5. Connect MySQL to the App

1. In the **project root directory**, create a `.env` file

2. Add the following line (replace with your MySQL password):

```
DATABASE_URL=mysql://root:password@localhost/tutor_sphere
```

**Format:**

```
mysql://username:password@localhost/database
```

---

## 6. Import Test Data

1. Navigate to:

```
\backend\schemas\relation
```

2. Open CMD in that directory

3. Run:

```bash
python import.py
```

---

## 7. Run the Application

1. Go back to the **project root directory**

2. Run:

```bash
python app.py
```
---

## Notes

- Ensure MySQL is running before starting the app  
- Double-check your `.env` credentials if connection fails  
- Use `SHOW TABLES;` to confirm successful setup


## Resources
Resources used to help navigate and connect database to app

[1]Coding With Moiz Khan, “How to Connect MySQL Database with Flask | Step-by-Step Guide for Beginners,” YouTube, Aug. 17, 2024. https://www.youtube.com/watch?v=kCNfWwHyTmY (accessed Apr. 03, 2026).

‌[2]“MySQL :: MySQL 8.4 Reference Manual :: 15.1.12 CREATE DATABASE Statement,” Mysql.com, 2025. https://dev.mysql.com/doc/refman/8.4/en/create-database.html

[3]GeeksforGeeks, “Templating With Jinja2 in Flask,” GeeksforGeeks, Dec. 28, 2022. https://www.geeksforgeeks.org/python/templating-with-jinja2-in-flask/

‌[4]W3Schools. (n.d.). Python Dates. Www.w3schools.com. https://www.w3schools.com/python/python_datetime.asp

‌[5]W3Schools. (n.d.). MySQL DATE_ADD() Function. Www.w3schools.com. https://www.w3schools.com/sql/func_mysql_date_add.asp

[6]AB, D. S. (2024, October 17). DbVisualizer. DbVisualizer; DbVis Software AB. https://www.dbvis.com/thetable/a-complete-guide-to-the-mysql-boolean-type/