# Connecting MySQL database to Flask application using SQLAlchemy ORM. The database connection is established using the DATABASE_URL environment variable, and a test query is executed to confirm the connection.
'''
Set up was aided with the following resources:
Coding With Moiz Khan - Connecting MySQL with Flask: https://www.youtube.com/watch?v=kCNfWwHyTmY
'''

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

# Test the database connection
with app.app_context():
    db.session.execute(text('SELECT 1'))
    print('DB Connection Successful')

if __name__ == '__main__':
    app.run(debug=True)
