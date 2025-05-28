# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from app.config import MONGO_URI
from pymongo import MongoClient
import gridfs

# clientMongoDB = AsyncIOMotorClient(MONGO_URI)
# db = clientMongoDB.GeoSI
# fs = AsyncIOMotorGridFSBucket(db)

clientMongoDB = MongoClient(MONGO_URI)
db = clientMongoDB["GeoSI"]
fs = gridfs.GridFS(db)


