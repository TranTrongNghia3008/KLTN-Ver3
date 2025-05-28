# For extracting site and keyword data
from pydantic import BaseModel

# For Q&A
from typing_extensions import override
from openai import AssistantEventHandler

# For FastAPI
from typing import List, Optional

class SearchQuery(BaseModel):
    site: str
    query: str

class Location(BaseModel):
    administrative_area: str
    country: str
    continent: str
    lat: float
    lon: float
    links: Optional[List[str]] = []
    summaries: Optional[List[str]] = []
    sentiment: str

class ListLocation(BaseModel):
    listLocation: List[Location]
    
class LocationFromBot(BaseModel):
    administrative_area: str
    country: str
    continent: str
    lat: float
    lon: float
    summary: str
    sentiment: str

class ListLocationFromBot(BaseModel):
    listLocation: List[LocationFromBot]
    
class LinkArticle(BaseModel):
    title: str
    link: str
    local: Optional[ListLocation] = []

class LocationRequest(BaseModel):
    link_articles: List[LinkArticle]
    files_path: List[str]
    conversationsessionsID: str

class ResponseRequest(BaseModel):
    text: str
    isCrawl: bool
    linkSpecific: str
    topK: int
    conversationsessionsID: str
    
class ResponseModel(BaseModel):
    textAnswer: str
    links: List[str]
    locations: List[Location]
    status: str

class EventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.result = None

    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_message_done(self, message) -> None:
        self.result = message.content[0].text.value 

class SentenceMapping(BaseModel):
    sentence: str
    referenced_segment: str  # The sentence is referenced
    label: bool  # True = SUPPORTED, False = REFUTED
    explanation: str
    evidence_urls: List[str]
    revised_sentence: str

class FactCheck(BaseModel):
    sentence: str
    label: bool  # True = SUPPORTED, False = REFUTED
    explanation: str
    revised_sentence: str
