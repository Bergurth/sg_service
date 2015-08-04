#!/usr/local/bin/python3.4
import cherrypy
import json
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId


connection = MongoClient()
dbList = connection.database_names()


db = connection.sgtestdb
#query1 = db.users.find().count()
users = []
for user in db.users.find():
    users.append(user)


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

class Root(object):
    @cherrypy.expose
    def index(self):
            #return users
            return dumps(users)


cherrypy.config.update({
	'/':{'request.dispatch': cherrypy.dispatch.MethodDispatcher(),},
    'environment': 'production',
    'log.screen': False,
    'server.socket_host': '127.0.0.1',
    'server.socket_port': 13336,
})
cherrypy.quickstart(Root())
