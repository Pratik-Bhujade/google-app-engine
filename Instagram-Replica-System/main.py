import webapp2
from constants import *
import urls
from google.appengine.api import users
import logging
from google.appengine.ext import ndb
from models.user import User
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from models.post import UserPost
from datetime import datetime
from operator import itemgetter
from models.usercomment import UserComment

#Class definition
class Index(webapp2.RequestHandler):
    #GET request definition 
    def get(self):
        #Set content type to text/html
        self.response.headers["Content-Type"] = "text/html"
        #Get logged in user
        user = users.get_current_user()
        post_list = []
        post_comments = []
        if user:
            #generate logout user
            url = users.create_logout_url(self.request.uri)
            obj = ndb.Key("User",user.user_id()).get()
            if obj == None:
                obj = User(id = user.user_id(), user_email = user.email())
                obj.put()
            message = "<a class=\"navlink nav-link\" href='"+ url +"'>Logout</a></p>"
            post_users = []
            for following in obj.user_following:
                f_obj = ndb.Key("User",following).get()
                post_users.append(f_obj.user_email)
            post_users.append(obj.user_email)
            post_list = UserPost.query(UserPost.post_user.IN(post_users)).order(-UserPost.post_date).fetch()  
             
            for post_obj in post_list: 
                post_comments.append(UserComment.query(UserComment.user_post == str(post_obj.key.id())).order(-UserComment.user_commentdate).fetch())
        else:
            #generate login user
            url = users.create_login_url(self.request.uri)
            message = "<p>Hope you are having a good day!</p><p><a href='"+ url +"'>Login</a>"
        template_values = { "user" : user, "message" : message, "posts" : post_list[0:51], "post_comments" : post_comments }
        #Get template to render
        template = JINJA_ENVIRONMENT.get_template("templates/index.html")
        #Render template
        self.response.write(template.render(template_values))

class CreatePost(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.headers["Content-Type"] = "text/html"
            upload_url = blobstore.create_upload_url("/createpost")
            
            template_values = { "user" : user ,"upload_url" : upload_url }
        else:
            url = users.create_login_url(self.request.uri)
            message = "<h4>Kindly <a href='"+ url +"'>login</a> to continue!</h4>"
            template_values = { "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/createPost.html")
        self.response.write(template.render(template_values))

    def post(self):
        blob = self.get_uploads()
        user = users.get_current_user()
        obj = ndb.Key("User", user.user_id()).get()
        userPost = UserPost(post_date = datetime.now(),
                            post_file = blob[0].key(),
                            post_caption = self.request.get("post_caption"),
                            post_user = obj.user_email)
        userPost.put()
        obj.user_posts.append(str(userPost.key.id()))
        obj.put()
        self.redirect("/")

class Profile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            key = self.request.get("user")
            template_values = {}
            posts = []
            post_comments = []
            profile_user = ndb.Key("User", str(key)).get()
            for post_key in reversed(profile_user.user_posts):
                posts.append(ndb.Key("UserPost", int(post_key)).get())
            for post_obj in posts:
                post_comments.append(UserComment.query(UserComment.user_post == str(post_obj.key.id())).order(-UserComment.user_commentdate).fetch())
            template_values["userposts"] = posts
            template_values["post_comments"] = post_comments
            if user.user_id() != key:
                template_values["profile_user"] = profile_user
                template_values["logged_user"] = ndb.Key("User", str(user.user_id())).get()
            else:
                template_values["logged_user"] = profile_user
            template_values["posts"] = posts
            template_values["user"] = user
        else:
            url = users.create_login_url(self.request.uri)
            message = "<h4>Kindly <a href='"+ url +"'>login</a> to continue!</h4>"
            template_values = { "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/userprofile.html")
        self.response.write(template.render(template_values))

class Search(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template_values = { "user" : user, "message" : "" }
        else:
            url = users.create_login_url(self.request.uri)
            message = "<h4>Kindly <a href='"+ url +"'>login</a> to continue!</h4>"
            template_values = { "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/searchprofile.html")
        self.response.write(template.render(template_values))
    
    def post(self):
        user = users.get_current_user()
        user_name = self.request.get("user_name")
        users_all = User.query().fetch()
        result = []
        for obj in users_all:
            if obj.user_email.find(user_name) != -1:
                result.append(obj)
        if len(result) == 0:
            message = "-No Results found-"
        else:
            message = ""
        template_values = { "result" : result, "user" : user, "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/searchprofile.html")
        self.response.write(template.render(template_values))

class GetImage(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        userPost = ndb.Key("UserPost", int(self.request.get("post"))).get()
        self.send_blob(userPost.post_file)
    
class Follow(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        obj = ndb.Key("User", str(user.user_id())).get()
        obj.user_following.append(self.request.get("user"))
        obj.put()
        other_user = ndb.Key("User", self.request.get("user")).get()
        other_user.user_followers.append(user.user_id())
        other_user.put()
        self.redirect("/")

class Unfollow(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        obj = ndb.Key("User", str(user.user_id())).get()
        obj.user_following.remove(self.request.get("user"))
        obj.put()
        other_user = ndb.Key("User", self.request.get("user")).get()
        other_user.user_followers.remove(user.user_id())
        other_user.put()
        self.redirect("/")

class FollowingList(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            obj = ndb.Key("User", self.request.get("user")).get()
            user_list = []
            for key in obj.user_following:
                user_list.append(ndb.Key("User", str(key)).get())
            logging.info(obj)
            template_values = { "users" : user_list,"user" : user, "message" : "Following" }
        else:
            url = users.create_login_url(self.request.uri)
            message = "<h4>Kindly <a href='"+ url +"'>login</a> to continue!</h4>"
            template_values = { "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/followerlist.html")
        self.response.write(template.render(template_values))

class FollowerList(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            obj = ndb.Key("User", self.request.get("user")).get()
            user_list = []
            for key in obj.user_followers:
                user_list.append(ndb.Key("User", str(key)).get())
            logging.info(user_list)
            template_values = { "users" : user_list,"user" : user, "message" : "Followers" }
        else:
            url = users.create_login_url(self.request.uri)
            message = "<h4>Kindly <a href='"+ url +"'>login</a> to continue!</h4>"
            template_values = { "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/followerlist.html")
        self.response.write(template.render(template_values))

class Comment(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        obj = ndb.Key("User", str(user.user_id())).get()
        usercomment = UserComment(user_email = obj.user_email,
                                  user_post = self.request.get("post"),
                                  user_comment = self.request.get("usercomment"),
                                  user_commentdate = datetime.now())
        usercomment.put()
        self.redirect("/")

class ViewPost(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            post_obj = ndb.Key("UserPost", int(self.request.get("post"))).get()
            comments = UserComment.query(UserComment.user_post == str(post_obj.key.id())).order(-UserComment.user_commentdate).fetch()
            template_values = { "post" : post_obj, "comments" : comments, "user" : user }
        else:
            url = users.create_login_url(self.request.uri)
            message = "<h4>Kindly <a href='"+ url +"'>login</a> to continue!</h4>"
            template_values = { "message" : message }
        template = JINJA_ENVIRONMENT.get_template("templates/postdetails.html")
        self.response.write(template.render(template_values))