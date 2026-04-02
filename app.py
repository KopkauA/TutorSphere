# to run, use python app.py

from flask import Flask, render_template, request, redirect

app = Flask(__name__)


# page routes
@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/signup")
def signup_choice():
    return render_template("signup_choice.html")


@app.route("/signup/student")
def signup_student():
    return render_template("signup_student.html")


@app.route("/signup/tutor")
def signup_tutor():
    return render_template("signup_tutor.html")


# run
if __name__ == "__main__":
    app.run(debug=True)