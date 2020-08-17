from google.appengine.ext import ndb

class User(ndb.Model):
    user_email = ndb.StringProperty()
    user_followers = ndb.StringProperty(repeated = True)
    user_following = ndb.StringProperty(repeated = True)
    user_posts = ndb.StringProperty(repeated = True)