from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ProjectCreate(BaseModel):
    name: str
    genre: Optional[str] = None
    mood: Optional[str] = None
    bpm: Optional[int] = None
    musical_key: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    genre: Optional[str] = None
    mood: Optional[str] = None
    bpm: Optional[int] = None
    musical_key: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True