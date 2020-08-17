from google.appengine.ext import ndb

class User(ndb.Model):
    user_email = ndb.StringProperty()
    created_boards = ndb.StringProperty(repeated = True)
    added_boards = ndb.StringProperty(repeated = True)