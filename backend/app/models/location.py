from pydantic import BaseModel
from typing import List

class LocationModel(BaseModel):
    SessionID: str = None
    administrative_area: str
    country: str
    continent: str
    lat: float
    lon: float
    links: List[str]
    summaries: List[str]
    sentiment: str
