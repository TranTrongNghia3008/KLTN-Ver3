from fastapi import APIRouter
from app.database.connect import db
from datetime import datetime

router = APIRouter()

@router.get("/start_session")
async def start_session(user_id: str):
    session_data = {
        "UserID": user_id,
        "History": [],
        "VectorStoreID": None,
        "AssistantID": None,  
        "Title": "New Chat",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    session = db.conversationsessions.insert_one(session_data)
    return {"session_id": str(session.inserted_id)}
