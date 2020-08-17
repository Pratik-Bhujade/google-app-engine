import webapp2
from constants import *
import urls
from google.appengine.api import users
import logging
from google.appengine.ext import ndb
from datetime import datetime
from models.user import User
from models.taskboard import TaskBoard
from models.task import Task

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
            obj = ndb.Key("User",user.user_id()).get()
            if obj == None:
                obj = User(id = user.user_id(), user_email = user.email())
                obj.put()
            message = "<p>Hope you are having a good day!</p> <p><a href='/createboard'>Create Board</a> | <a href='/boardlist'>View Boards</a> | <a href='"+ url +"'>Logout</a></p>"
        else:
            #generate login user
            url = users.create_login_url(self.request.uri)
            message = "<p>Hope you are having a good day!</p><p><a href='"+ url +"'>Login</a>"
        template_values = { "user" : user, "message" : message }
        #Get template to render
        template = JINJA_ENVIRONMENT.get_template("templates/index.html")
        #Render template
        self.response.write(template.render(template_values))

class AddBoard(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.headers["Content-Type"] = "text/html"
        template_values = {}
        if user:
            template_values["user"] = user
        else:
            url = users.create_login_url(self.request.uri)
            message = "Kindly <a href='"+ url +"'>login</a> to create task boards!"
            template_values["message"] = message 
        template = JINJA_ENVIRONMENT.get_template("templates/addtaskboard.html")
        self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()
        if user:
            taskboard = TaskBoard.query(TaskBoard.taskBoardName == self.request.get("board_name")).get()
            if taskboard == None:
                taskboard = TaskBoard(taskBoardName = self.request.get("board_name"))
                taskboard.put()
                obj = ndb.Key("User",user.user_id()).get()
                obj.created_boards.append(str(taskboard.key.id()))
                obj.put()
                self.redirect("/viewboard?board=" + str(taskboard.key.id()))
            else:
                self.response.headers["Content-Type"] = "text/html"                
                url = users.create_login_url(self.request.uri)
                message = "<p>Cannot create task board with the same name!</p><p><a href='/'>Home</a></p>"
                template_values = { "message" : message }
                template = JINJA_ENVIRONMENT.get_template("templates/addtaskboard.html")
                self.response.write(template.render(template_values))

class ViewBoard(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {}
        if user:
            obj = ndb.Key("User",user.user_id()).get()
            if self.request.get("board") in obj.created_boards or self.request.get("board") in obj.added_boards :
                taskboard = ndb.Key("TaskBoard", int(self.request.get("board"))).get()
                template_values["taskboard"] = taskboard
                template_values["user"] = obj
                template_values["user_list"] = User.query().fetch()
                task_list = []
                for key in taskboard.taskBoardTask:
                    task = ndb.Key("Task", int(key)).get()
                    if task:
                        if task.taskFlag == True:
                            task_list.append(task)
                template_values["tasks"] = task_list
                template_values["completed"] = len(Task.query(ndb.AND(Task.taskBoard == self.request.get("board"), Task.taskFlag == False)).fetch())
                template_values["active"] = len(Task.query(ndb.AND(Task.taskBoard == self.request.get("board"), Task.taskFlag == True)).fetch())
                template_values["completed_today"] = len(Task.query(ndb.AND(Task.taskBoard == self.request.get("board"), Task.taskFlag == False, Task.taskFinishDate == datetime.now())).fetch())
                template_values["total"] = len(Task.query(Task.taskBoard == self.request.get("board")).fetch())
            else:
                message = "<p>User not authorized to view this board!</p><p><a href='/'>Home</a></p>"
                template_values = { "message" : message }
        else:
            url = users.create_login_url(self.request.uri)
            message = "Kindly <a href='"+ url +"'>login</a> to create task boards!"
            template_values["message"] = message 
        template = JINJA_ENVIRONMENT.get_template("templates/viewtaskboard.html")
        self.response.write(template.render(template_values))

    def post(self):
        obj = ndb.Key("User", self.request.get("userlist")).get()
        obj.added_boards.append(self.request.get("board"))
        obj.put()
        self.redirect("/")

class ViewBoardList(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {}
        if user:
            obj = ndb.Key("User",user.user_id()).get()
            taskboard_list = []
            for key in obj.created_boards:
                if ndb.Key("TaskBoard", int(key)).get() is not None:
                    taskboard_list.append(ndb.Key("TaskBoard", int(key)).get())
            for key in obj.added_boards:
                if ndb.Key("TaskBoard", int(key)).get() is not None:
                    taskboard_list.append(ndb.Key("TaskBoard", int(key)).get())
            if len(taskboard_list) != 0:
                template_values["taskboards"] = taskboard_list
            else:
                message = "No boards!"
                template_values["message"] = message 
            template_values["user"] = obj
        else:
            url = users.create_login_url(self.request.uri)
            message = "Kindly <a href='"+ url +"'>login</a> to create task boards!"
            template_values["message"] = message 
        template = JINJA_ENVIRONMENT.get_template("templates/viewboardlist.html")
        self.response.write(template.render(template_values))

class CreateTask(webapp2.RequestHandler):
    def post(self):
        taskboard = ndb.Key("TaskBoard", int(self.request.get("board"))).get()
        task = Task.query(ndb.AND(Task.taskDescription == self.request.get("task_title"),Task.taskBoard == self.request.get("board"))).get()
        if task == None:
            task = Task(taskDescription = self.request.get("task_title"),
                        taskDueDate = datetime.strptime(self.request.get("task_duedate"), "%Y-%m-%d"),
                        taskFlag = True,
                        taskUser = ndb.Key("User",self.request.get("userlist")).get().user_email,
                        taskBoard = self.request.get("board"))
            task.put()
            taskboard.taskBoardTask.append(str(task.key.id()))
            taskboard.put()
            self.redirect("/viewboard?board=" + self.request.get("board"))
        else:
            self.response.headers["Content-Type"] = "text/html"                
            message = "<p>Cannot create task with the same name!</p><p><a href='/'>Home</a></p>"
            template_values = { "message" : message }
            template = JINJA_ENVIRONMENT.get_template("templates/viewtaskboard.html")
            self.response.write(template.render(template_values))

class EndTask(webapp2.RequestHandler):
    def post(self):
        tasklist = self.request.get_all("tasklist")
        
        for task_key in tasklist:
            task = ndb.Key("Task", int(task_key)).get()
            task.taskFlag = False
            task.taskFinishDate = datetime.now().date()
            task.put()
        self.redirect("/viewboard?board=" + self.request.get("board"))

class TaskDetails(webapp2.RequestHandler):
    def get(self):
        task = ndb.Key("Task", int(self.request.get("task"))).get()
        taskboard = TaskBoard.query(TaskBoard.taskBoardTask.IN([self.request.get("task")])).get()
        user_list = User.query().fetch()
        template_values = { "task" : task, "taskboard" : taskboard, "user_list" : user_list, "user" : users.get_current_user() }
        template = JINJA_ENVIRONMENT.get_template("templates/edittask.html")
        self.response.write(template.render(template_values))

    def post(self):
        if self.request.get("action") == "Submit":
            task = ndb.Key("Task", int(self.request.get("task"))).get()
            if self.request.get("userlist") != "":
                task.taskUser = self.request.get("userlist")
            task.taskDueDate = datetime.strptime(self.request.get("task_duedate"), "%Y-%m-%d")
            task.put()
        else:
            task = ndb.Key("Task", int(self.request.get("task"))).get()
            ndb.Key("Task", int(self.request.get("task"))).delete()
        self.redirect("/")  

class TaskBoardDetails(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            obj = ndb.Key("User",user.user_id()).get()
            template_values = {}
            if self.request.get("board") in obj.created_boards:
                taskboard = ndb.Key("TaskBoard", int(self.request.get("board"))).get()
                template_values["taskboard"] = taskboard
                template_values["user"] = obj
                user_list = User.query(User.added_boards.IN([self.request.get("board")])).fetch()
                template_values["user_list"] = user_list
            else:
                message = "<p>User not authorized to edit this board</p><p><a href='/'>Home</a></p>"
                template_values["message"] = message
            template = JINJA_ENVIRONMENT.get_template("templates/edittaskboard.html")
            self.response.write(template.render(template_values))

    def post(self):
        taskboard = ndb.Key("TaskBoard", int(self.request.get("board"))).get()
        if self.request.get("taskboard_name"):
            taskboard.taskBoardName = self.request.get("taskboard_name")
            taskboard.put()
        if self.request.get("userlist"):
            obj = ndb.Key("User",self.request.get("userlist")).get()
            obj.added_boards.remove(self.request.get("board"))
            obj.put()
            tasks = Task.query(Task.taskUser == obj.user_email).fetch()
            for task in tasks:
                task.taskUser = None
                task.put()
        self.redirect("/")
    
class DeleteBoard(webapp2.RequestHandler):
    def post(self):
        taskboard = ndb.Key("TaskBoard", int(self.request.get("board"))).get()
        user = users.get_current_user()
        obj = ndb.Key("User",user.user_id()).get()
        user_list = User.query(User.added_boards.IN([self.request.get("board")])).fetch()
        if len(user_list) == 0:
            tasks = Task.query(ndb.AND(Task.taskBoard == self.request.get("board"),Task.taskFlag == True)).fetch()
            if len(tasks) == 0:
                ndb.Key("TaskBoard", int(self.request.get("board"))).delete()
                obj.created_boards.remove(self.request.get("board"))
                user_list = User.query(User.added_boards.IN([self.request.get("board")])).fetch()
                for user in user_list:
                    user.added_boards.remove(self.request.get("board"))
                    user.put()
                self.redirect("/")
            else:
                message = "<p>End all tasks to delete task board </p><p><a href='/'>Home</a></p>"
                template_values = { "message" : message }
                template = JINJA_ENVIRONMENT.get_template("templates/edittaskboard.html")
                self.response.write(template.render(template_values))
        else:
            message = "<p>Remove all users to delete task board </p><p><a href='/'>Home</a></p>"
            template_values = { "message" : message }
            template = JINJA_ENVIRONMENT.get_template("templates/edittaskboard.html")
            self.response.write(template.render(template_values))