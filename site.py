#!/usr/local/bin/python3.4
import cherrypy
import json
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup


from localVars import db_port, db_host, openid_url, openid_test_user


if not (db_host == ""):
    connection = MongoClient(db_host, db_port )
else:
    connection = MongoClient()

dbList = connection.database_names()


db = connection.sgtestdb
#query1 = db.users.find().count()
users = []
for user in db.users.find():
    users.append(user)


SESSION_KEY = '_cp_username'


"""

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

"""

#print users

from bson import Binary, Code
from bson.json_util import dumps

import ast

def login_required(f):
    # a decorator factory providing a logged in check.
    def _login_required(*args, **kwargs):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        if (username != None):
            return f(*args, **kwargs)
        else:
            return "not logged in."

    return _login_required



class Root(object):
    @cherrypy.expose
    #@cherrypy.tools.json_out()
    def index(self):
            #return users
            return dumps(users)
            #return "hello this is no default site"

    @cherrypy.expose
    def hallo(self):
        return "hallo"


    #http://localhost:12315/user/?username=fred
    @cherrypy.expose
    @login_required
    @cherrypy.tools.allow(methods=['GET'])
    def user(self, username=None):
        sess = cherrypy.session
        ses_uname = sess.get(SESSION_KEY, None)
        if (username == ses_uname):
            uqstring = re.sub('[$,#,<,>,{,}]','',username) # cleaning string
            output = db.users.find({"username":uqstring})
            return dumps(output)
        else:
            return "not logged in"


        """
    @cherrypy.expose
    @login_required
    @cherrypy.tools.allow(methods=['POST'])
    def user2(self, username=None):
        return dumps(username)
        """




class Auth(object):
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    #@cherrypy.tools.json_out()
    #@cherrypy.tools.json_in()
    def login(self, username=None, password=None):
        # login in a user. Creating a session key with username.
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        url = openid_url
        open_url = urllib2.urlopen(url)
        html = open_url.read()
        # getting csrf token from openid
        doc = BeautifulSoup(html)
        csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
        csrf_token = csrf_input['value']
        # getting json
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))  
        # making a dictionaty out of raw json string.   
        d1 = dict(ast.literal_eval(rawbody))
        params = urllib.urlencode(dict(username=d1['username'], password=d1['password'],csrfmiddlewaretoken=csrf_token))
        # This is a blocking call for some crazy unknown reason.  TODO FIX
        post_url = urllib2.urlopen(url, params)
        openid_user = json.loads(post_url.read())
        # here the sessin is being established
        cherrypy.session[SESSION_KEY] = cherrypy.request.login = openid_user['username']

        return {}


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            #self.on_logout(username)
            print cherrypy.session[SESSION_KEY]
            print cherrypy.request.login
        raise cherrypy.HTTPRedirect(from_page or "/")


class Protected(object):
    @cherrypy.expose
    @login_required
    def index(self):
            return dumps(users)




cherrypy.config.update({
    '/':{'request.dispatch': cherrypy.dispatch.MethodDispatcher(),},
    'environment': 'production',
    'log.screen': False,
    'server.socket_host': '127.0.0.1',
    'server.socket_port': 12315,
    'tools.sessions.on': True,
    'tools.sessions.persistent': True,
    'tools.sessions.timeout': 60
})



cherrypy.tree.mount(Root(), '/')
cherrypy.tree.mount(Auth(), '/auth')
cherrypy.tree.mount(Protected(), '/protected')


cherrypy.engine.start()
cherrypy.engine.block()

#cherrypy.quickstart(Root())
