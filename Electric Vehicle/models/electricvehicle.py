from google.appengine.ext import ndb

#Datamodel class definition
class ElectricVehicle(ndb.Model):
    vehicleName = ndb.StringProperty()
    vehicleManufacturer = ndb.StringProperty()
    year = ndb.IntegerProperty()
    batterySize = ndb.IntegerProperty()
    wltpRange = ndb.IntegerProperty()
    cost = ndb.FloatProperty()
    power = ndb.IntegerProperty()
    averageRating = ndb.FloatProperty()