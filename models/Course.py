from google.appengine.ext import db


class Course(db.Model):
    name = db.StringListProperty(required=True)
    description = db.StringListProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    created_by = db.StringProperty(required=False)
