from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    content: str
    message_type: str
    fb_message_id: Optional[str] = None
    timestamp: datetime

class MessageCreate(MessageBase):
    chat_id: int

class MessageResponse(MessageBase):
    id: int
    chat_id: int

    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    fb_user_id: str
    fb_user_name: str

class ChatCreate(ChatBase):
    user_id: int

class ChatResponse(ChatBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class SendMessageRequest(BaseModel):
    content: str 