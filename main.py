import logging

from google.appengine.ext import db
from flask import Flask, render_template, request, redirect, url_for

from flask import session as login_session
import random, string

# Create a flow object
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# HTTP client library
import httplib2
# Provide an API for converting in memory python object to serialize representation
import json

from flask import make_response
import requests

from models.Course import Course
from models.Card import Card

app = Flask(__name__)
app.secret_key = 'super_secret_key'

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Flash Card App"


# Create  anti forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response


    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
        json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    print "done!"
    return output

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

"""
"auth_uri":"https://accounts.google.com/o/oauth2/auth",
"token_uri":"https://accounts.google.com/o/oauth2/token",
"auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",

"""