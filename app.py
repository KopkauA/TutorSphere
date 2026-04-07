# to run, use python app.py

import os
from flask import Flask, render_template, request, redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
from backend.models import db, User

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)

# Test the database connection
with app.app_context():
    db.session.execute(text('SELECT 1'))
    print('DB Connection Successful')


# page routes
@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup_choice():
    return render_template("signup_choice.html")


@app.route('/signup/student', methods=['GET', 'POST'])
def signup_student():
    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['fname']   
        lname = request.form['lname']   
        password = request.form['password']

        new_user = User(
            email=email,
            fname=fname,
            lname=lname,
            password=password,
            role='student'
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup_student.html')


@app.route("/signup/tutor")
def signup_tutor():
    return render_template("signup_tutor.html")

# run
if __name__ == "__main__":
    app.run(debug=True)
    