''' The Wrapper for accessing the mongo DB '''
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

mngserv = {
    "ip":"129.192.68.68",
    "port": 27017
}

client = MongoClient(mngserv['ip'],mngserv['port'])

# Creating a database (or using it if exists)
db = client.wlth2
cl = db.jobs


def postJob(jobData):
    cl.insert(jobData)

def getDocumentById(id):
    return cl.find_one({"id":id})

def updateDocumentStatus(id, status):
    cl.update_one({"id":id},{"$set": {
        "status":status}})