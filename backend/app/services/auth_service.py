from app.database.connect import db
from app.utils.security import hash_password, verify_password, create_access_token
from bson.objectid import ObjectId
from datetime import datetime

async def register_user(user):
    existing = await db.users.find_one({"Email": user.Email})
    if existing:
        return None
    
    now = datetime.utcnow()
    user_dict = user.dict()
    user_dict["Password"] = hash_password(user_dict["Password"])
    user_dict["createdAt"] = now
    user_dict["updatedAt"] = now
    
    if not user_dict.get("Email"):
        raise ValueError("Email is required")

    result = await db.users.insert_one(user_dict)
    return str(result.inserted_id)

async def authenticate_user(Email: str, Password: str):
    user = await db.users.find_one({"Email": Email})
    if not user:
        return None
    if not verify_password(Password, user["Password"]):
        return None
    return user
