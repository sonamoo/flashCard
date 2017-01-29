from google.appengine.ext import db
from Course import Course


class Card(db.Model):
    course = db.ReferenceProperty(Course, collection_name='cards')
    name = db.StringListProperty(required=True)
    description = db.StringListProperty(required=True)
    memorized = db.





