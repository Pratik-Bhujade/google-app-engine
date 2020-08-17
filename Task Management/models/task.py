from google.appengine.ext import ndb

class Task(ndb.Model):
    taskDescription = ndb.StringProperty()
    taskDueDate = ndb.DateProperty()
    taskFlag = ndb.BooleanProperty()
    taskUser = ndb.StringProperty()
    taskFinishDate = ndb.DateProperty()
    taskBoard = ndb.StringProperty()