import logging

from google.appengine.ext import db
from flask import Flask, render_template, request, redirect, url_for

from models.Course import Course
from models.Card import Card

app = Flask(__name__)


# Fake courses

# Fake cards
"""
cards = [{'id': 1, 'name': 'Algorithm', 'courseId': 1, 'description': 'a process or set of rules to be followed in calculations or other problem-solving operations, especially by a computer'},
         {'id': 2, 'name': 'Data Structure', 'courseId': 1, 'description': 'In computer science, a data structure is a particular way of organizing data in a computer so that it can be used efficiently.'},
         {'id': 3, 'name': 'CRUD', 'courseId': 2, 'description': 'In computer programming, create, read, update and delete (as an acronym CRUD)'},
         {'id': 4, 'name': 'AJAX', 'courseId': 2, 'description': 'AJAX stands for Asynchronous JavaScript and XML. In a nutshell, it is the use of the XMLHttpRequest object to communicate with server-side scripts. It can send as well as receive information in a variety of formats, including JSON, XML, HTML, and even text files.'}]
"""

@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/courses/new', methods=['GET', 'POST'])
def new_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if name and description:
            c = Course(name=name, description=description)
            c.put()
            return redirect(url_for('my_courses'))
    else:
        return render_template('newCourse.html')


# Render courses page.
@app.route('/courses')
def my_courses():
    courses = db.GqlQuery("SELECT * FROM Course ORDER BY created")
    return render_template('myCourses.html', courses=courses)


# See the course's cards.
@app.route('/courses/<string:course_name>')
def show_cards(course_name):
    cards = Card.gql("WHERE course = 'course_name'").get()
    if cards:
        return render_template('courseCards.html', cards=cards)
    else:
        return render_template('courseCards.html', course=course_name)


# Edit course's name or description.
@app.route('/courses/<int:course_id>/edit')
def edit_course(course_id):
    return render_template('editCourse.html')


# Delete a course.
@app.route('/courses/<int:course_id>/delete')
def delete_course(course_id):
    return render_template('deleteCourse.html')


# Add a card.
@app.route('/courses/<string:course_name>/new')
def new_card(course_name):
    return render_template('newCard.html', course_name)

    """
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        course = course_name
        if name and description:
            newCard = Card(name=name, description=description, course=course_name)
            return redirect(url_for('show_cards'))
    """




@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
