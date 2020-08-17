import webapp2
from main import *

#Url mapping i.e class to url mapping
urls = webapp2.WSGIApplication([("/", Index), ("/createboard", AddBoard), ("/viewboard", ViewBoard),
                                ("/boardlist", ViewBoardList), ("/createtask", CreateTask), ("/endtasks", EndTask),
                                ("/taskdetails", TaskDetails), ("/boarddetails", TaskBoardDetails), ("/deleteboard", DeleteBoard)],debug = True)