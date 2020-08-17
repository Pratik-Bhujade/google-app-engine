from google.appengine.ext import ndb

class TaskBoard(ndb.Model):
    taskBoardName = ndb.StringProperty()
    taskBoardTask = ndb.StringProperty(repeated = True)