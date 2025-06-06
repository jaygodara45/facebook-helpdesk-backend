from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

from app.core.database import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    fb_user_id = Column(String(255))  # Facebook user ID
    fb_user_name = Column(String(255))  # Facebook user name
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="chat")
    user = relationship("User", back_populates="chats")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    content = Column(Text)
    message_type = Column(String(50))  # 'incoming' or 'outgoing'
    fb_message_id = Column(String(255))  # Facebook message ID
    timestamp = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))

    # Relationships
    chat = relationship("Chat", back_populates="messages") 