from google.appengine.ext import ndb

class UserComment(ndb.Model):
    user_email = ndb.StringProperty()
    user_post = ndb.StringProperty()
    user_comment = ndb.StringProperty()
    user_commentdate = ndb.DateTimeProperty()