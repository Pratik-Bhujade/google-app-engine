from google.appengine.ext import ndb

class UserPost(ndb.Model):
    post_date = ndb.DateTimeProperty()
    post_file = ndb.BlobKeyProperty()
    post_caption = ndb.StringProperty()
    post_user = ndb.StringProperty()