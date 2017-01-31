from google.appengine.ext import db
from Course import Course


class Card(db.Model):
    course = db.ReferenceProperty(Course, collection_name='cards')
    name = db.StringProperty(required=True)
    description = db.TextProperty(required=True)





