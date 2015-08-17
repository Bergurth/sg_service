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


def login_required(f):
    # a decorator factory providing a logged in check.
    def _login_required(*args, **kwargs):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        print "=========================="
        print username
        if (username != None):
            return f(*args, **kwargs)
        else:
            return "not logged in."

    return _login_required



class Root(object):
    @cherrypy.expose
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
        uname = sess.get(SESSION_KEY, None)
        print "BBBBBBBBBBBBBBBBBBBBBBBBBBBB"
        print uname
        if (username == uname):
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
        """
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)

        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")
        """
        #Fields = parse_submit(request)
        #print Fields
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        #url = settings.AUTH_OPENID_URLS['signin']
        url = openid_url

        open_url = urllib2.urlopen(url)
        html = open_url.read()

        doc = BeautifulSoup(html)
        csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
        csrf_token = csrf_input['value']

        print "hello"
        #input_json = cherrypy.request.json
        #print input_json

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        ctype = cherrypy.request.headers['content-type']
        print ctype

        """ this doesnt work
        jsn1 = cherrypy.request.body.json
        print jsn1
        """


        """
        body = simplejson.loads(rawbody)
        print body
        """
        #pre_openid_user = json.loads(rawbody)
        print rawbody
        #body = json.loads(rawbody)
        #print type(rawbody)



        params = urllib.urlencode(dict(username=username, password=password,csrfmiddlewaretoken=csrf_token))




        print params
        # This is a blocking call for some crazy unknown reason.  TODO FIX
        post_url = urllib2.urlopen(url, params)

        print post_url

        openid_user = json.loads(post_url.read())

        print openid_user['username']
        #print openid_user.username

        # here the sessin is being established
        cherrypy.session[SESSION_KEY] = cherrypy.request.login = openid_user['username']

        print "now the session"
        print "---------------------"
        print cherrypy.session[SESSION_KEY]
        print cherrypy.request.login


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
