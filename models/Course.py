from google.appengine.ext import db


class Course(db.Model):
    name = db.StringProperty(required=True)
    description = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    created_by = db.StringProperty(required=False)
