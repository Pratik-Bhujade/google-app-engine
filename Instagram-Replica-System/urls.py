import webapp2
from main import *

#Url mapping i.e class to url mapping
urls = webapp2.WSGIApplication([("/", Index), ("/createpost", CreatePost), ("/userprofile", Profile),
                                ("/usersearch", Search),("/image", GetImage),("/follow", Follow),("/unfollow", Unfollow),
                                ("/following", FollowingList), ("/followers", FollowerList),("/submitcomment", Comment),("/viewpost", ViewPost)],debug = True)