import pymongo
from pymongo import Connection
from bson.objectid import ObjectId

from pymongo import MongoClient
client = MongoClient()
#db = client.test_database

db = client.sgtestdb
db.users.remove()
collection = db.users

user1 = {"username": "fred", "email":"fred@fred.com","savedGames":{"tetris": {"state":[1,2,3]},"pong":{"state":[4,1,2]}}}
user2 = {"username": "lisa", "email":"lisa@lisa.com","savedGames":{"tetris": {"state":[6,1,3]},"pong":{"state":[4,1,3]}}}
user3 = {"username": "sindy", "email":"sindy@yahoo.com","savedGames":{"tetris": {"state":[1,2,3]},"pong":{"state":[7,8,6]}}}
user4 = {"username": "charlie", "email":"charlie@fred.com","savedGames":{"tetris": {"state":[1,2,3]},"pong":{"state":[1,1,2]}}}

collection.insert(user1)
collection.insert(user2)
collection.insert(user3)
collection.insert(user4)
"""
connection = Connection()
db = connection['sg-test-db']
collection = db['sg-test-users']
"""
