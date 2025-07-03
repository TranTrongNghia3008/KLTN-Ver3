from fastapi import APIRouter, Request, HTTPException
from app.models.conversation_session import *
from app.models.location import LocationModel
from app.database.connect import db
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter(prefix="/q-and-a", tags=["Conversations"])

# GET /q-and-a/{user_id}
@router.get("/{user_id}")
async def show(user_id: str):
    try:
        object_user_id = ObjectId(user_id)
    except Exception:
        return {"error": "Invalid user_id format"}

    sessions = db.conversationsessions.find(
        {"UserID": object_user_id},
        {"Title": 1, "updatedAt": 1}
    ).sort("updatedAt", -1)
    result = []
    for s in sessions:
        result.append({
            "_id": str(s["_id"]),
            "Title": s.get("Title", "Untitled") 
        })
    return result


# GET /q-and-a/conversations/{id}
@router.get("/conversations/{id}", response_model=List[str])
async def get_history(id: str):
    session = db.conversationsessions.find_one({"_id": ObjectId(id)})
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [h if isinstance(h, str) else str(h) for h in session.get("History", [])]


# POST /q-and-a/conversations/new
@router.post("/conversations/new")
async def create_chat(session: ConversationSession):
    try:
        doc = session.dict()
        doc["UserID"] = ObjectId(doc["UserID"])  
        doc["createdAt"] = datetime.utcnow()
        doc["updatedAt"] = datetime.utcnow()

        result = db.conversationsessions.insert_one(doc)    

        return {"_id": str(result.inserted_id), "Title": doc["Title"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


# DELETE /q-and-a/conversations/{id}
@router.delete("/conversations/{id}")
async def delete_conversation(id: str):
    result = db.conversationsessions.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return {"message": "Conversation deleted successfully"}
    raise HTTPException(status_code=404, detail="Conversation not found")


# PUT /q-and-a/conversations/{id}/updateHistory
@router.put("/conversations/{id}/updateHistory")
async def update_history(id: str, history: List[str]):
    result = db.conversationsessions.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"History": {"$each": history}}, "$set": {"updatedAt": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "History updated successfully"}


# PUT /q-and-a/conversations/{id}/updateLocations
@router.put("/conversations/{id}/updateLocations")
async def update_locations(id: str, locations: List[LocationModel]):
    db.locations.delete_many({"SessionID": ObjectId(id)})
    for loc in locations:
        loc_dict = loc.dict()
        loc_dict["SessionID"] = ObjectId(id)  # ép gán lại
        db.locations.insert_one(loc_dict)
    return {"message": "Locations updated successfully"}


# GET /q-and-a/conversations/{id}/locations
@router.get("/conversations/{id}/locations", response_model=List[LocationModel])
async def load_locations(id: str):
    
    results = list(db.locations.find({"SessionID": ObjectId(id)}))
    mapped = []
    for loc in results:
        mapped.append(LocationModel(
            SessionID=str(loc["SessionID"]),
            administrative_area=loc["administrative_area"],
            country=loc["country"],
            continent=loc["continent"],
            lat=loc["lat"],
            lon=loc["lon"],
            links=loc["links"],
            summaries=loc["summaries"],
            sentiment=loc["sentiment"]
        ))
    return mapped


# PUT /q-and-a/conversations/{id}/renameConversation
@router.put("/conversations/{id}/renameConversation")
async def rename_conversation(id: str, req: RenameConversationRequest):
    result = db.conversationsessions.update_one(
        {"_id": ObjectId(id)}, {"$set": {"Title": req.title, "updatedAt": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Title updated successfully"}