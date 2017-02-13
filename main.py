import logging

from google.appengine.ext import db
from flask import Flask, render_template, request, redirect, url_for
from flask import session as login_session

import random
import string


# HTTP client library
import httplib2
# Provide an API for converting in memory python object to serialize representation
import json

# Models
from models.Course import Course
from models.Card import Card
from oauth2client import client, crypt

app = Flask(__name__)
app.secret_key = 'super_secret_key'

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Create  anti forgery state token
@app.route('/login')
def showLogin():    
    return render_template('login.html')


@app.route('/tokensignin', methods=['POST'])
def connect():
    try:
    idinfo = client.verify_id_token(token, CLIENT_ID)

    # Or, if multiple clients access the backend server:
    #idinfo = client.verify_id_token(token, None)
    #if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #    raise crypt.AppIdentityError("Unrecognized client.")

    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise crypt.AppIdentityError("Wrong issuer.")

    # If auth request is from a G Suite domain:
    #if idinfo['hd'] != GSUITE_DOMAIN_NAME:
    #    raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
    # Invalid token
    userid = idinfo['sub']
    

    # (Receive token by HTTPS POST)

    try:
        idinfo = client.verify_id_token(token, CLIENT_ID)

        # Or, if multiple clients access the backend server:
        #idinfo = client.verify_id_token(token, None)
        #if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #    raise crypt.AppIdentityError("Unrecognized client.")

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

        # If auth request is from a G Suite domain:
        #if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #    raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
        # Invalid token
        print "invalid token"
    userid = idinfo['sub']

    return render_template('login.html', userid=userid)






# Render courses page.
@app.route('/courses')
def my_courses():
    courses = db.GqlQuery("SELECT * FROM Course ORDER BY created")
    return render_template('myCourses.html', courses=courses)


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