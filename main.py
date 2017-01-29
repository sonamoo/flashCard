import logging

from google.appengine.ext import db
from flask import Flask, render_template, request

from models.Course import Course
from models.Card import Card

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello World!'


# Render courses page.
@app.route('/courses')
def my_courses():
    courses = db.GqlQuery("SELECT * FROM Course ORDER BY created")
    return render_template('myCourses.html', courses=courses)


# Edit course's name or description.
@app.route('/courses/<int:course_id>/edit')
def edit_course():
    aCourse = db.GqlQuery("SELECT ")


# See the course's cards.
@app.route('/courses/<int:course_id>')



@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
