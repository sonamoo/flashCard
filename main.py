import logging

from google.appengine.ext import db
from flask import Flask, render_template, request, redirect, url_for

from flask import session as login_session
import random, string

from models.Course import Course
from models.Card import Card

app = Flask(__name__)
app.secret_key = 'super_secret_key'


# Create  anti forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html')



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
@app.route('/courses/<int:course_id>')
def show_cards(course_id):
    key = db.Key.from_path('Course', course_id)
    course = db.get(key)
    cards = course.cards
    if cards:
        return render_template('courseCards.html', cards=cards, course=course)
    else:
        return render_template('courseCards.html', course=course)


# Edit course's name or description.
@app.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
def edit_course(course_id):
    key = db.Key.from_path('Course', course_id)
    course = db.get(key)
    if request.method == 'POST':
        course.name = request.form['name']
        course.description = request.form['description']
        course.put()
        return redirect(url_for('show_cards', course_id=course_id))
    else:
        return render_template('editCourse.html', course=course)


# Delete a course.
@app.route('/courses/<int:course_id>/delete', methods=['GET', 'POST'])
def delete_course(course_id):
    key = db.Key.from_path('Course', course_id)
    course = db.get(key)
    if request.method == 'POST':
        course.delete()
        return redirect(url_for('my_courses'))
    else:
        return render_template('deleteCourse.html', course=course)


# Add a card.
@app.route('/courses/<int:course_id>/new', methods=['GET', 'POST'])
def new_card(course_id):
    key = db.Key.from_path('Course', course_id)
    course = db.get(key)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        key = db.Key.from_path('Course', course_id)
        course = db.get(key)
        if name and description:
            card = Card(name=name, description=description, course=course)
            card.put()
            return redirect(url_for('show_cards', course_id=course_id))
    else:
        return render_template('newCard.html', course=course)


# Edit a card
@app.route('/courses/<int:course_id>/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(course_id, card_id):
    course_key = db.Key.from_path('Course', course_id)
    card_key = db.Key.from_path('Card', card_id)
    course = db.get(course_key)
    card = db.get(card_key)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if name and description:
            card = Card(name=name, description=description, course=course)
            card.put()
            return redirect(url_for('show_cards', course=course))
    else:
        return render_template('editCard.html', course=course, card=card)


# Delete a card
@app.route('/courses/<int:course_id>/delete', methods=['GET', 'POST'])
def delete_card(course_id, card_id):
    course_key = db.Key.from_path('Course', course_id)
    card_key = db.Key.from_path('Card', card_id)
    course = db.get(course_key)
    card = db.get(card_key)
    if request.method == 'POST':
        card.delete()
        return redirect(url_for('show_cards', course_id=course_id, card_id=card_id))
    else:
        return render_template('deleteCard.html', course=course, card=card)


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
