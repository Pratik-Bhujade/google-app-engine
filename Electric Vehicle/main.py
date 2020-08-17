import webapp2
from constants import *
import urls
from google.appengine.api import users
import logging
from google.appengine.ext import ndb
from models.electricvehicle import ElectricVehicle
from models.review import Review
from datetime import datetime

#Class definition
class Index(webapp2.RequestHandler):
    #GET request definition 
    def get(self):
        #Set content type to text/html
        self.response.headers["Content-Type"] = "text/html"
        #Get logged in user
        user = users.get_current_user()
        if user:
            #generate logout user
            url = users.create_logout_url(self.request.uri)
            user = users.get_current_user()
            message = "<p>Hope you are having a good day!</p><p><a href='/addvehicle'>Add vehicle</a> | <a href='/filtervehicle'>Search vehicle</a> | <a href='/comparevehicle'>Compare vehicles</a> | <a href='/reviewvehicle'>Review vehicles</a> | <a href='"+ url +"'>Logout</a></p>"
        else:
            #generate login user
            url = users.create_login_url(self.request.uri)
            message = "<p>Hope you are having a good day!</p><p><a href='"+ url +"'>Login</a> | <a href='/filtervehicle'>Search</a>"
        template_values = { "user" : user, "message" : message }
        #Get template to render
        template = JINJA_ENVIRONMENT.get_template("templates/index.html")
        #Render template
        self.response.write(template.render(template_values))

#Class definition
class AddVehicle(webapp2.RequestHandler):
    #GET request definition
    def get(self):
        #Set content type to text/html
        self.response.headers["Content-Type"] = "text/html"
        #Get logged in user
        user = users.get_current_user()
        if user:
            template_values = { "user" : user, "message" : "message" }
        else:
            #generate login user
            url = users.create_login_url(self.request.uri)
            message = "Kindly <a href='"+ url +"'>login</a> to add vehicles!"
            template_values = { "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/addVehicle.html")
        #Render template
        self.response.write(template.render(template_values))

    #POST request definition
    def post(self):
        #Set content type to text/html
        self.response.headers["Content-Type"] = "text/html"
        #Get logged in user
        user = users.get_current_user()

        if user:
            #Query for vehicle
            ev = ElectricVehicle.query(ndb.AND(ElectricVehicle.year == int(self.request.get("year")),
                                    ElectricVehicle.vehicleManufacturer == self.request.get("vehicle_manufacturer"),
                                    ElectricVehicle.vehicleName == self.request.get("vehicle_name"))).get()

            if ev is None:
                #Creat vehicle object
                vehicle = ElectricVehicle(vehicleName = self.request.get("vehicle_name"),
                                          vehicleManufacturer = self.request.get("vehicle_manufacturer"),
                                          year = int(self.request.get("year")),
                                          batterySize = int(self.request.get("battery")),
                                          wltpRange = int(self.request.get("wltp")),
                                          cost = float(self.request.get("cost")),
                                          power = int(self.request.get("power")),
                                          averageRating = 0.0)

                if vehicle is not None:
                    #Save object to database
                    vehicle.put()
                    self.redirect("/")

#Class definition
class FilterVehicle(webapp2.RequestHandler):
    #GET request definition
    def get(self):
        #Set content type to text/html
        self.response.headers["Content-Type"] = "text/html"
        template = JINJA_ENVIRONMENT.get_template("templates/filter.html")
        self.response.write(template.render())

    #POST request definition
    def post(self):
        #Set content type to text/html
        self.response.headers["Content-Type"] = "text/html"
        #Fetch all vehicles
        vehicles = ElectricVehicle.query()
        #Logic for filtering
        if self.request.get("vehicle_name"):
            vehicles = vehicles.filter(ElectricVehicle.vehicleName == self.request.get("vehicle_name"))
        if self.request.get("vehicle_manufacturer"):
            vehicles = vehicles.filter(ElectricVehicle.vehicleManufacturer == self.request.get("vehicle_manufacturer"))
        
        list_of_values = []
        if self.request.get("lyear") and self.request.get("hyear"):
            list_of_values.append("year")
        if self.request.get("lbatterySize") and self.request.get("hbatterySize"):
            list_of_values.append("batterySize")
        if self.request.get("lwltpRange") and self.request.get("hwltpRange"):
            list_of_values.append("wltpRange")
        if self.request.get("lcost") and self.request.get("hcost"):
            list_of_values.append("cost")
        if self.request.get("lpower") and self.request.get("hpower"):
            list_of_values.append("power")

        return_list = vehicles.fetch()
       
        for vehicle in return_list:
            counter = 0
            for value in list_of_values:
                if value != "cost":
                    if getattr(vehicle,value) >= int(self.request.get("l" + value)) and getattr(vehicle,value) <= int(self.request.get("h" + value)):
                        counter += 1
                elif getattr(vehicle,value) >= float(self.request.get("l" + value)) and getattr(vehicle,value) <= float(self.request.get("h" + value)):
                    counter += 1
            
            if counter != len(list_of_values):
                return_list.remove(vehicle)
       
        messages = []
        if return_list:
            for vehicle in return_list:
                if users.get_current_user():
                    messages.append("<div class=\"text-center\"><h3>Click for more info &nbsp<a href='/details?vehicle=" + vehicle.vehicleName + "'>" + vehicle.vehicleName + "</a></h3></div>")
                else:
                    messages.append("<div class=\"text-center\"><h3>Click for more info </p>&nbsp<a href='/details?vehicle=" + vehicle.vehicleName + "&type=info'>" + vehicle.vehicleName + "</a></h3></div>")
        else:
            messages.append("<div class=\"text-center\"><h3>No vehicles found</h3></div>")
        template_values = { "messages" : messages }
        template = JINJA_ENVIRONMENT.get_template("templates/filter.html")
        self.response.write(template.render(template_values))

#Class definition
class EditVehicle(webapp2.RequestHandler):
    #GET request definition
    def get(self):
        #Set content type to text/html
        self.response.headers["Content-Type"] = "text/html"
        user = users.get_current_user()
        vehicle = ElectricVehicle.query(ElectricVehicle.vehicleName == self.request.get("vehicle")).get()
        #Get type of request
        type_of_request = self.request.get("type")
        #Fetch reviews
        reviews = Review.query(Review.vehicle == self.request.get("vehicle")).order(-Review.date).fetch()
        template_values = { "user" : user, "vehicle" : vehicle, "type" : type_of_request, "reviews" : reviews }
        template = JINJA_ENVIRONMENT.get_template("templates/vehicleinfo.html")
        #Render template
        self.response.write(template.render(template_values))
    
    #POST request definition
    def post(self):
        #Set content type text/html
        self.response.headers["Content-Type"] = "text/html"
        user = users.get_current_user()

        if user:
            #Logic to update vehicle
            vehicle = ElectricVehicle.query(ElectricVehicle.vehicleName == self.request.get("vehicle")).get()
            logging.info(self.request.get("action"))
            if self.request.get("action") == "Submit":
                logging.info(self.request.get("year"))
                if self.request.get("year"):
                    vehicle.year = int(self.request.get("year"))
                if self.request.get("battery"):
                    vehicle.batterySize = int(self.request.get("battery"))
                if self.request.get("wltp"):
                    vehicle.wltpRange = int(self.request.get("wltp"))
                if self.request.get("cost"):
                    vehicle.cost = float(self.request.get("cost"))
                if self.request.get("power"):
                    vehicle.power = int(self.request.get("power"))
                vehicle.put()
            else:
                vehicle.key.delete()
            self.redirect("/")

#Class definition
class CompareVehicle(webapp2.RequestHandler):
    #GET request definition
    def get(self):
        self.response.headers["Countent-Type"] = "text/html"
        vehicles = ElectricVehicle.query().fetch()
        template_values = { "vehicles" : vehicles }
        template = JINJA_ENVIRONMENT.get_template("templates/comparevehicle.html")
        self.response.write(template.render(template_values))

    #POST request definition
    def post(self):
        self.response.headers["Content-Type"] = "text/html"
        #Get all vehicles to compare
        vehicles_name = self.request.get_all("vehicles")
        vehicles = []
        #Logic to compare vehicles
        for name in vehicles_name:
            vehicles.append(ElectricVehicle.query(ElectricVehicle.vehicleName == name).get())
        
        table = "<br><br><table class=\"table table-bordered\" style=\"color:white;\">"

        headings = [ "vehicleName", "vehicleManufacturer", "year", "batterySize", "wltpRange", "cost", "power", "averageRating" ]
        headings_to_display = [ "Vehicle Name", "Vehicle Manufacturer", "Year", "Battery Size", "Wltp Range", "Cost", "Power", "Average Rating" ]
        for heading in headings:
            table += "<tr>"
            table += "<td>" + headings_to_display[headings.index(heading)] + "</td>"
            values = []
            max_value = None
            min_value = None
            for vehicle in vehicles:
                values.append(getattr(vehicle,heading))
            if heading not in [ "vehicleName", "vehicleManufacturer" ]:
                max_value = max(values)
                min_value = min(values)
            
            for value in values:
                color1 = "green"
                color2 = "red"
                if heading == "cost":
                    color1 = "red"
                    color2 = "green"
                if max_value != min_value:
                    if max_value == value:
                        table += "<td style=\"background:" + color1 + "\">" + str(value) + "</td>"
                    elif min_value == value:
                        table += "<td style=\"background:" + color2 + "\">" + str(value) + "</td>"
                    else:
                        if heading == "vehicleName":
                            table += "<td><a href=\"/details?vehicle=" + str(value) + "&type=info\">" + str(value) + "</a></td>"
                        else:
                            table += "<td>" + str(value) + "</td>"
                else:
                    if heading == "vehicleName":
                            table += "<td><a href=\"/details?vehicle=" + str(value) + "&type=info\">" + str(value) + "</a></td>"
                    else:
                        table += "<td>" + str(value) + "</td>"
            table += "</tr>"
        table += "</table>"
        vehicles = ElectricVehicle.query().fetch()
        template_values = { "table" : table, "vehicles" : vehicles }
        template = JINJA_ENVIRONMENT.get_template("templates/comparevehicle.html")
        self.response.write(template.render(template_values))

#Class definition
class ReviewVehicle(webapp2.RequestHandler):
    #GET request definition
    def get(self):
        #Set content type to text/html
        self.response.headers["Countent-Type"] = "text/html"
        user = users.get_current_user()

        if user:
            vehicles = ElectricVehicle.query().fetch()
            template_values = { "user" : user, "vehicles" : vehicles }
        else:
            url = users.create_login_url(self.request.uri)
            message = "Kindly <a href='"+ url +"'>login</a> to review vehicles!"
            template_values = { "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/reviewvehicle.html")
        self.response.write(template.render(template_values))
    
    #POST request definition
    def post(self):
        self.response.headers["Content-Type"] = "text/html"
        vehicle = ElectricVehicle.query(ElectricVehicle.vehicleName == self.request.get("vehicleList")).get()
        logging.info(datetime.now())
        #Create Review object
        review = Review(user = users.get_current_user().email(),
                        vehicle = self.request.get("vehicleList"),
                        review = self.request.get("review"),
                        rating = int(self.request.get("rating")),
                        date = datetime.now())
        #Store Review object to database
        review.put()
        #Logic to calculate average rating of vehicle
        reviews = Review.query(Review.vehicle == self.request.get("vehicleList")).fetch()
        rating = review.rating
        for rev in reviews:
            rating += rev.rating
        logging.info(reviews)
        logging.info(rating)
        vehicle.averageRating = round(float(rating)/(len(reviews) + 1),2)
        vehicle.put()
        self.redirect("/")
        
