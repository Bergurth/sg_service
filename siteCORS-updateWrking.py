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


from localVars import db_port, db_host, openid_url_signin, openid_url_signup, openid_request_reset, openid_test_user


if not (db_host == ""):
    connection = MongoClient(db_host, db_port )
else:
    connection = MongoClient()

dbList = connection.database_names()


db = connection.sgtestdb
#query1 = db.users.find().count()


SESSION_KEY = '_cp_username'


from bson import Binary, Code
from bson.json_util import dumps

import ast

def login_required(f):
    # a decorator factory providing a logged in check.
    def _login_required(*args, **kwargs):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        if (username != None):
            print "unae hittin"
            return f(*args, **kwargs)
        else:
            return "not logged in.   maaan!"

    return _login_required


def login_required_json(f):
    # a decorator factory providing a logged in check.
    def _login_required():
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        if (username != None):
            print "unae hittin"
            return f()
        else:
            return "not logged in.   maaan!"

    return _login_required



class Root(object):
    @cherrypy.expose
    #@cherrypy.tools.json_out()
    def index(self):
            users = []
            for user in db.users.find():
                users.append(user)

            #return users
            return dumps(users)
            #return "hello this is no default site"

    @cherrypy.expose
    def hallo(self):
        return "hallo"


    #http://localhost:12315/user/?username=fred
    @cherrypy.expose
    @login_required
    #@cherrypy.tools.allow(methods=['GET'])
    # TODO add case for state of particular game.
    def user(self, username=None):
        sess = cherrypy.session
        ses_uname = sess.get(SESSION_KEY, None)
        if (username == ses_uname):
            uqstring = re.sub('[$,#,<,>,{,}]','',username) # cleaning string
            output = db.users.find({"username":uqstring})
            return dumps(output)
        else:
            return "not logged in"


    @cherrypy.expose
    #@login_required
    #@login_required_json
    #@cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_in()
    def state_update(self):
        # implements ow login required ..
        """   -- try to get session test
        try:
            sess = cherrypy.session
            ses_uname = sess.get(SESSION_KEY, None)
            return ses_uname
        except Exception as e:
            print str(e)
            return "failed"
        """

        """
        try:
            sess = cherrypy.session
            username = sess.get(SESSION_KEY, None)
        except Exception as e:
            return "no json"

        sess = cherrypy.session
        ses_uname = sess.get(SESSION_KEY, None)
        # getting json

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        # making a dictionaty out of raw json string. TODO make try catch, for when bad json comes
        d1 = dict(ast.literal_eval(rawbody))
        if (d1.get('username') == ses_uname):
            #carry on
            if (d1.get('gamename')!=None):
                #update state of game in db.
                update_string = "savedGames."+ d1.get('gamename') + ".state"
                # todo check that newstate closes all parentasis maybe .. maybe with regex.. or do some input cleaning ..
                # this is maybe an issue of design, could also be a check if newstate is valid json,
                # if we decide that state should always be a json string. try if json.loads(d1.get('newstate')) gives error.
                db.users.update({"username": d1.get('username') },{ "$set" :{update_string:d1.get('newstate')}})
            else:
                #bad input
                raise cherrypy.HTTPError(401)
        else:
            #not authorized.
            raise cherrypy.HTTPError(401)
        """
        try:
            data = cherrypy.request.json
            print type(data)
            username = data["username"]
            newstate = data["newstate"]
            gamename = data["gamename"]
            # next two lines test, working thing..
            #update_string = "savedGames."+ gamename + ".state"
            #db.users.update({"username": username },{ "$set" :{update_string:newstate}})

            sess = cherrypy.session
            ses_uname = sess.get(SESSION_KEY, None)
            # following works
            #return "after db update " + ses_uname
            if ses_uname:
                if (username == ses_uname):
                    if gamename:
                        update_string = "savedGames."+ gamename + ".state"
                        db.users.update({"username": username },{ "$set" :{update_string:newstate}})
                        return "after db update " + ses_uname + " " + gamename
                    else:
                        #bad input
                        raise cherrypy.HTTPError(401)
                else:
                    #not authorized.
                    raise cherrypy.HTTPError(401)
            else:
                raise cherrypy.HTTPError(401)
            """
            try:
                sess = cherrypy.session
                ses_uname = sess.get(SESSION_KEY, None)
            except Exception as e1:
                print str(e1)
                return "getting session failed"
            """

            """ adapted should work part
            if (username == ses_uname):
                print "first if passes"
                if (gamename!=None):
                    print "second if .."
                    update_string = "savedGames."+ gamename + ".state"
                    # todo check that newstate closes all parentasis maybe .. maybe with regex.. or do some input cleaning ..
                    # this is maybe an issue of design, could also be a check if newstate is valid json,
                    # if we decide that state should always be a json string. try if json.loads(d1.get('newstate')) gives error.

                    db.users.update({"username": username },{ "$set" :{update_string:newstate}})
                    return "success"
                else:
                    #bad input
                    raise cherrypy.HTTPError(401)
            else:
                #not authorized.
                raise cherrypy.HTTPError(401)
            """
        except Exception as e:
            print str(e)
            return "failed"

        """
    @cherrypy.expose
    @login_required
    @cherrypy.tools.allow(methods=['POST'])
    def user2(self, username=None):
        return dumps(username)
        """

class Auth(object):
    @cherrypy.expose
    #@cherrypy.tools.allow(methods=['POST'])
    #@cherrypy.tools.json_out()
    #@cherrypy.tools.json_in()
    def login(self, username=None, password=None , password1=None, password2=None, email=None):
        # login in a user. Creating a session key with username.
        print "login started"
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        cherrypy.response.headers["Access-Control-Allow-Credentials"] = "*"
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        print "just bfr getting json"
        # getting json
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        # making a dictionaty out of raw json string. TODO make try catch, for when bad json comes
        d1 = dict(ast.literal_eval(rawbody))
        print "after dict made"
        print d1['username']
        if (not (d1.get('email') and d1.get('password1') and d1.get('password2') and d1.get('username'))):
            # this is case of regular login.
            url = openid_url_signin
            open_url = urllib2.urlopen(url)
            html = open_url.read()
            # getting csrf token from openid
            doc = BeautifulSoup(html)
            csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
            csrf_token = csrf_input['value']
            params = urllib.urlencode(dict(username=d1['username'], password=d1['password'],csrfmiddlewaretoken=csrf_token))

            print url
            print params
            # This is a blocking call for some crazy unknown reason.  TODO FIX
            try:
                post_url = urllib2.urlopen(url, params)
            except:
                pass
            # getting user from openid
            openid_user = json.loads(post_url.read())
            # here the sessin is being established
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = openid_user['username']
            # TODO some error handling here.
            return {}

        else:
            print "create hittin"
            # this is case of new user.
            url = openid_url_signup
            open_url = urllib2.urlopen(url)
            html = open_url.read()
            # getting csrf token from openid
            doc = BeautifulSoup(html)
            csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
            csrf_token = csrf_input['value']
            print "oken gotten"
            params = urllib.urlencode(dict(username = d1['username'],
                                           email =  d1['email'],
                                           password1 = d1['password1'],
                                           password2 = d1['password2'],
                                           csrfmiddlewaretoken = csrf_token))

            print params
            print "just before crazy blocking call"
            # This is a blocking call for some crazy unknown reason.  TODO FIX
            try:
                post_url = urllib2.urlopen(url, params)
            except:
                pass
            print "just after"
            # getting user from openid
            openid_user = json.loads(post_url.read())
            # here check if openid returns a user, if so make user coresponding here in the sg db
            if "username" in openid_user:
                print openid_user
                # enter user coresponding here in the sg db.
                db.users.insert(openid_user)
                #establish the session.
                cherrypy.session[SESSION_KEY] = cherrypy.request.login = openid_user['username']
                return {}

            else:
                print "openid user not hittin"
                #raise cherrypy.HTTPError(status=406, message=openid_user.get('err', {}))
                raise cherrypy.HTTPError(406)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def openid_reset(self, email=None):
        # TODO perform reset password.

        # from menntg
        """
        Perform a reset password feature. Asks for an email address which will be
        submitted to the openid server
        """
        url       = openid_request_reset
        urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        urllib2.install_opener(urlopener)

        stream   = urllib2.urlopen(url)
        document = BeautifulSoup(stream.read())
        stream.close()

        token  = document.find(attrs={'name': 'csrfmiddlewaretoken'}).get('value')
        #fields = parse_submit(request)
        # getting json
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        # making a dictionaty out of raw json string. TODO make try catch, for when bad json comes
        d1 = dict(ast.literal_eval(rawbody))

        params = urllib.urlencode({'email': d1.get('email'), 'csrfmiddlewaretoken': token})

        stream = urllib2.urlopen(url, params)
        result = stream.read()
        stream.close()

        try:
            result = json.loads(result)
        except ValueError:
            pass

        return result

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
        #raise cherrypy.HTTPRedirect(from_page or "/static")
        raise cherrypy.HTTPRedirect("/static")


class Protected(object):
    @cherrypy.expose
    @login_required
    def index(self):
            return dumps(users)

"""
import cherrypy_cors
cherrypy_cors.install()
"""
def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept"

cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)

# static served, login test
import os
cwd = os.getcwd()
path_client = os.path.abspath(os.path.dirname('/test_client/test_client_basic.html'))
stat_path = cwd + path_client
print stat_path

class Static(object):pass

class Supdate(object):pass


# session timeout should probably be longer.
config = {
    'global':{
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 12315,
        'tools.CORS.on': True,
    },
    '/':{
        #'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'environment': 'production',
        'log.screen': False,
        'tools.sessions.on': True,
        'tools.sessions.persistent': True,
        'tools.sessions.timeout': 60,
        'tools.CORS.on': True,

        #'tools.response_headers.on': True,
        #'tools.response_headers.headers': [('Content-Type', 'text/plain')],

        #'tools.staticdir.on': True,
        #'cors.expose.on' : True,

        #'tools.response_headers.on': True,
    },
}


configAuth = {
    'global':{
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 12315,

    },
    '/':{
        #'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'environment': 'production',
        'log.screen': False,
        'tools.sessions.on': True,
        'tools.sessions.persistent': True,
        'tools.sessions.timeout': 60,


        #'tools.response_headers.on': True,
        #'tools.response_headers.headers': [('Content-Type', 'text/plain')],

        #'tools.staticdir.on': True,
        #'cors.expose.on' : True,

        #'tools.response_headers.on': True,
    },
}



cherrypy.config.update(config)

cherrypy.tree.mount(Root(), '/', config=config)
cherrypy.tree.mount(Auth(), '/auth', config=configAuth)
#cherrypy.tree.mount(Protected(), '/protected', config=config)

cherrypy.tree.mount(Static(), '/static',config={'/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': stat_path,
                'tools.staticdir.index': 'test_client_basic.html',
            },})

cherrypy.tree.mount(Supdate(), '/supdate',config={'/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': stat_path,
                'tools.staticdir.index': 'updater.html',
            },})


cherrypy.engine.start()
cherrypy.engine.block()

#cherrypy.quickstart(Root())
