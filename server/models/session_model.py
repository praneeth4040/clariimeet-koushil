from pydantic import BaseModel
from typing import List

class SessionData(BaseModel):
    title: str
    summary: str
    transcription: str
    participants: List[str] = []