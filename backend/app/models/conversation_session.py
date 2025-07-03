from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ConversationSession(BaseModel):
    UserID: str
    Title: str
    History: List[str]
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    
class RenameConversationRequest(BaseModel):
    title: str
