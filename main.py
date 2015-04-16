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

#Sign-in import Code will go here:
import re
import random
import hashlib
import hmac
from string import letters

#Database Addition
from google.appengine.ext import ndb

import json

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

secret = 'fart'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val  

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    
class MainHandler(BlogHandler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        #visits = self.request.cookies.get('visits', 0)
        #self.write(visits)
        self.render("welcome.html")

class UserDashboard(BlogHandler):
    def get(self):
        #if user is logged in:
            #get the JSON from the database
            #self.render(userdashboard.html, json=json)
            #just parse the json on the html page. Display it there.

        self.render("userdashboard.html") #I think ship the JSON as a var.
        #self.render("userdashboard.html", eventInfoJson)
        
class Vote(BlogHandler):
    def get(self):
        pass

class Results(BlogHandler):
    def get(self):
        #get JSON from the specified user and pass this on

        #Did everyone vote?

        #If not:

        event = {
        "event" : "name is the name",
        "Two's" : 4
        }
        self.render("results.html")

class CreateEvent(BlogHandler):
    def get(self):
        self.render("createevent.html")
    def post(self):

        userCreated = "Joe"
        eventName = self.request.get("event")
        description = self.request.get("description")

        #get all of friends
        #count-up the total number of friends
        friend1 = self.request.get("friend1")
        friend2 = self.request.get("friend2")
        friend3 = self.request.get("friend3")

        #get all the hangout dates
        date1 = self.request.get("date1")
        time1 = self.request.get("time1")
        locationname1 = self.request.get("locationname1")
        date2 = self.request.get("date2")
        time2 = self.request.get("time2")
        locationname2 = self.request.get("locationname2")
        date3 = self.request.get("date3")
        time3 = self.request.get("time3")
        locationname3 = self.request.get("locationname3")

        #get the closing date of voting
        dateclose = self.request.get("dateclose")

        #JSON the information for database saving
        
        #Save the JSON into the Database
        #eventInfoJson.put()
        #wait for a second
        eventInfoJson={
            "eventName" : eventName,
            "description": description,
            "groupTotal" : 3,
            "groupCounter" : 0,
            "waitFlag" : 0,
            "eventCreator" : userCreated,
            "groupMembers" : [friend1, friend2, friend3],
            "groupVoteRanks" :[],
            "userConfirmations" : [],
            "Hangouts" :
                {
                    "option1" : {
                        "date": date1,
                        "time": time1,
                        "place": locationname1,
                        "address": "16789 Du Pont Rd, Chino, Ca"},
                    "option2" :{
                        "date": date2,
                        "time": time2,
                        "place": locationname2,
                        "address": "16789 Du Pont Rd, Ch"},
                    "option3" :{
                        "date": date3,
                        "time": time3,
                        "place": locationname3,
                        "address": "16789 Du Pont Rd, Ch"}
                    },
            "dateclose" : dateclose,
            "results" : []
        }

        information = json.dumps(eventInfoJson)
        databaseInput = Event(eventInfoJson=information)
        databaseInput.put()

        self.redirect("/UserDashboard")

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('register.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('register.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.render('welcome.html', username=self.username)

class Login(BlogHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.render("welcome.html", username=username)
        else:
            msg = 'Invalid login'
            self.render('register.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')


#DataBase Addition
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return ndb.Key('users', group)

class User(ndb.Model):
    name = ndb.StringProperty(required = True)
    pw_hash = ndb.StringProperty(required = True)
    email = ndb.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.query().filter(User.name == name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

class Event(ndb.Model):
    eventInfoJson = ndb.TextProperty(required=True)
    #gets an error with auto add now
    #created = ndb.DateTimeProperty(auto_add_now=True)
    
    #somehow have pictures for the event
        #each event is to have some group photo

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/Login', Login),
    ('/Register', Register),
    ('/Logout', Logout),
    ('/UserDashboard', UserDashboard),
    ('/CreateEvent', CreateEvent),
    ('/Results', Results)
], debug=True)
