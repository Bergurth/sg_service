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
import requests
from BeautifulSoup import BeautifulSoup


from localVars import db_port, db_host, openid_url_signin, openid_url_signup, openid_request_reset, openid_test_user, allowed_origins, allowed_origins_list


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


class Root(object):
    @cherrypy.expose
    # TODO remove this in production.
    #@cherrypy.tools.json_out()
    def index(self):
            users = []
            for user in db.users.find():
                users.append(user)

            #return users
            return dumps(users)
            #return "hello this is no default site"

    #http://localhost:12315/user/?username=fred
    @cherrypy.expose
    @login_required
    @cherrypy.tools.allow(methods=['GET'])
    # TODO add case for state of particular game.
    def user(self, username=None, gamename=None):
        sess = cherrypy.session
        ses_uname = sess.get(SESSION_KEY, None)
        #   db.users.find({"username":"fred"},{"savedGames.pong":1})
        if (username == ses_uname):
            uqstring = re.sub('[$,#,<,>,{,}]','',username) # cleaning string
            if (gamename):
                # returning for specific game.  .. todo test
                gqstring = re.sub('[$,#,<,>,{,}]','',gamename) # cleaning string
                output = db.users.find({"username":uqstring},{"savedGames."+gamename:1})
                return dumps(output)
            else:
                output = db.users.find({"username":uqstring})
                return dumps(output)
        else:
            return "not logged in"


    @cherrypy.expose
    # implements own login check.
    @cherrypy.tools.allow(methods=['POST','OPTIONS'])
    @cherrypy.tools.json_in()
    def state_update(self):

        try:
            print "inside state_update"
            data = cherrypy.request.json
            print type(data)
            username = data["username"]
            newstate = data["newstate"]
            gamename = data["gamename"]

            try:
                sess = cherrypy.session
                ses_uname = sess.get(SESSION_KEY, None)
                #return ses_uname + " server secret"
            except Exception as err:
                print str(err)
                return "failed"


            if (username == ses_uname):
                if gamename:
                    update_string = "savedGames."+ gamename + ".state"
                    # todo check that newstate closes all parentasis maybe .. maybe with regex.. or do some input cleaning ..
                    # this is maybe an issue of design, could also be a check if newstate is valid json,
                    # if we decide that state should always be a json string. try if json.loads(d1.get('newstate')) gives error.
                    db.users.update({"username": username },{ "$set" :{update_string:newstate}})
                else:
                        #bad input
                        raise cherrypy.HTTPError(406)
            else:
                    #not authorized.
                    raise cherrypy.HTTPError(401)

        except Exception as e:
            print str(e)
            return "failed"


class Auth(object):
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST','OPTIONS'])
    @cherrypy.tools.json_in()
    def login(self):
        # login in a user. Creating a session key with username.
        if (cherrypy.request.method == 'OPTIONS'):
            """  --  shows cookie
            c1 = cherrypy.request.cookie
            for name in c1.keys():
                print "name: %s , value: %s " % (name, str(c1[name]))

            """
            return {}

        cj = cookielib.CookieJar()

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        # getting json
        """   ---  former method, before cp.json_in
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        # making a dictionaty out of raw json string. TODO make try catch, for when bad json comes
        d1 = dict(ast.literal_eval(rawbody))
        """
        # this seems to acomplish login, but only for the tab/site in question.
        try:
            d1 = cherrypy.request.json
            if (not (d1.get('email') and d1.get('password1') and d1.get('password2') and d1.get('username'))):
                url = openid_url_signin
                open_url = urllib2.urlopen(url)
                html = open_url.read()



                doc = BeautifulSoup(html)
                csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
                csrf_token = csrf_input['value']
                params = urllib.urlencode(dict(username=d1['username'], password=d1['password'],csrfmiddlewaretoken=csrf_token))
                post_url = urllib2.urlopen(url, params)
                openid_user = json.loads(post_url.read())
                #cherrypy.session[SESSION_KEY] = cherrypy.request.login = openid_user['username']
                try:
                    cherrypy.session[SESSION_KEY] = openid_user['username']
                    # following line is for debuging purposes, could return somthing else ..like {}
                    #return openid_user['username'], cherrypy.session[SESSION_KEY]
                    return {}
                except Exception as err:
                    return str(err)


            else:
                # this is case of new user.
                url = openid_url_signup
                open_url = urllib2.urlopen(url)
                html = open_url.read()
                # getting csrf token from openid
                doc = BeautifulSoup(html)
                csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
                csrf_token = csrf_input['value']
                params = urllib.urlencode(dict(username = d1['username'],
                                               email =  d1['email'],
                                               password1 = d1['password1'],
                                               password2 = d1['password2'],
                                               csrfmiddlewaretoken = csrf_token))

                # This is a blocking call for some crazy unknown reason.  TODO FIX
                post_url = urllib2.urlopen(url, params)
                # getting user from openid
                openid_user = json.loads(post_url.read())
                # here check if openid returns a user, if so make user coresponding here in the sg db
                if "username" in openid_user:
                    # enter user coresponding here in the sg db.
                    db.users.insert(openid_user)
                    #establish the session.
                    cherrypy.session[SESSION_KEY] = cherrypy.request.login = openid_user['username']
                    return {}
                else:
                    raise cherrypy.HTTPError(status=406, message=openid_user.get('err', {}))

        except Exception as e:
            return str(e)


    @cherrypy.expose
    #@cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_in()
    def openid_reset(self, email=None):
        # TODO perform reset password.
        if (cherrypy.request.method == 'OPTIONS'):
            return {}

        """
        Perform a reset password feature. Asks for an email address which will be
        submitted to the openid server
        """

        url       = openid_request_reset
        urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        urllib2.install_opener(urlopener)
        print "after urllib2 thing"


        stream   = urllib2.urlopen(url)
        document = BeautifulSoup(stream.read())
        stream.close()

        token  = document.find(attrs={'name': 'csrfmiddlewaretoken'}).get('value')
        # getting json
        try:
            d1 = cherrypy.request.json
            params = urllib.urlencode({'email': d1.get('email'), 'csrfmiddlewaretoken': token})
            print params

            stream = urllib2.urlopen(url, params)
            result = stream.read()
            stream.close()

            try:
                result = json.loads(result)
            except ValueError:
                pass

            return result

        except Exception as e:
            return str(e)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET','OPTIONS'])
    def username(self):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        if username:
            return username
        else:
            return {}


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def logout(self, from_page=None):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            #self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/static")



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
    try:
        r_origin = cherrypy.request.headers['Origin']
        if (not r_origin in allowed_origins_list):
            raise cherrypy.HTTPError(401)
        else:
            cherrypy.response.headers["Access-Control-Allow-Origin"] = r_origin
            cherrypy.response.headers["Access-Control-Allow-Credentials"] = "true"
    except Exception as e:
        return str(e)


    cherrypy.response.headers['Access-Control-Allow-Headers'] = 'X-Auth-Token,Content-Type,Accept,csrftoken,sessionid,_ga,session_id,Origin, X-Requested-With, Content-Type, Accept'
    cherrypy.response.headers['Connection'] = 'keep-alive'
    cherrypy.response.headers['Access-Control-Max-Age'] = '1440'

cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)

# static served, login test
import os
cwd = os.getcwd()
path_client = os.path.abspath(os.path.dirname('/test_client/test_client_basic.html'))
stat_path = cwd + path_client


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
        'tools.sessions.clean_freq': None,
        'tools.CORS.on': True,
        # cherrypy_cors
        #'cors.expose.on': True,

        #'tools.response_headers.on': True,
        #'tools.response_headers.headers': [('Content-Type', 'text/plain')],

        #'tools.staticdir.on': True,
        #'cors.expose.on' : True,

        #'tools.response_headers.on': True,
    },
}




cherrypy.config.update(config)

cherrypy.tree.mount(Root(), '/', config=config)
cherrypy.tree.mount(Auth(), '/auth', config=config)

# local client
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

