from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from app.config import MONGO_URI

clientMongoDB = AsyncIOMotorClient(MONGO_URI)
db = clientMongoDB.GeoSI
fs = AsyncIOMotorGridFSBucket(db)


