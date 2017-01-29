import logging

from google.appengine.ext import db
from flask import Flask, render_template, request

from models.Course import Course
from models.Card import Card

app = Flask(__name__)


# Fake courses
courses = [{'id':1, 'name':'CS-151', 'description':'This is my first class at UIC'},
           {'id':2, 'name':'CS-141', 'description': 'Computer Science Program Design II'}]

@app.route('/')
def hello():
    return 'Hello World!'


# Render courses page.
@app.route('/courses')
def my_courses():

    return render_template('myCourses.html', courses=courses)


# Edit course's name or description.
@app.route('/courses/<int:course_id>/edit')
def edit_course(course_id):

    return 'edit here'

# Delete a course.
@app.route('/courses/<int:course_id>/delete')
def delete_course():
    return 'Are you sure you want to delete this course?'

# See the course's cards.
@app.route('/courses/<int:course_id>')
def show_cards(course_id):

    return



@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
