from app.config import *

class Speaker(BaseModel):
    id: str
    name: str

class ListSpeakers(BaseModel):
    listSpeakers: list[Speaker]

class Statement(BaseModel):
    start: float
    end: float
    speaker: str
    text: str
    reason: str  # Tại sao cần kiểm chứng
    context: str

class ListStatement(BaseModel):
    listStatment: List[Statement]

class FactCheck(BaseModel):
    label: bool  # True = SUPPORTED, False = REFUTED