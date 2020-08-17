import webapp2
from main import *

#Url mapping i.e class to url mapping
urls = webapp2.WSGIApplication([("/", Index), 
                                ("/addvehicle", AddVehicle),
                                ("/filtervehicle", FilterVehicle),
                                ("/details", EditVehicle),
                                ("/comparevehicle", CompareVehicle),
                                ("/reviewvehicle", ReviewVehicle)],debug = True)