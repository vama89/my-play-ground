#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#Template Jinja Imports and Fresh Startup
import webapp2
import jinja2
import os

#Database Addition
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.render("welcome.html")

class UserDashboard(Handler):
    def get(self):
        #get the JSON from the database
        self.render("userdashboard.html")
        
class Vote(Handler):
    def get(self):
        pass

class Results(Handler):
    def get(self):
        pass

class CreateEvent(Handler):
    def get(self):
        self.render("createevent.html")
    def post(self):
        #get information here
        #save it as a JSON
        #then save it to the database
        pass

class Register(Handler):
    def get(self):
        self.render("register.html")

    def post(self):
        self.request.get("username")
        self.request.get("password")
        self.request.get("email")

        self.render("userDashboard.html")

class Login(Handler):
    def get(self):
        self.render("login.html")

class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)

class Event(ndb.Model):
    eventInfoJson = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(required=True)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/Login', Login),
    ('/Register', Register),
    ('/UserDashboard', UserDashboard),
    ('/CreateEvent', CreateEvent)
], debug=True)
