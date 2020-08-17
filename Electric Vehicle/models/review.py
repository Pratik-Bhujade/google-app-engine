from google.appengine.ext import ndb
from models.electricvehicle import ElectricVehicle
from google.appengine.api import users

#Datamodel class definition
class Review(ndb.Model):
    user = ndb.StringProperty()
    vehicle = ndb.StringProperty()
    review = ndb.StringProperty()
    rating = ndb.IntegerProperty()
    date = ndb.DateTimeProperty()