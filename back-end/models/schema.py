from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None

class FileUpload(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_token: int
    file_type: str
    file_path: str

class Conversation(BaseModel):
    id: str
    user_id: str
    title: str

class Chat(BaseModel):
    id: str
    conversation_id: str
    content: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)