from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add relationship with FacebookPage
    facebook_pages = relationship("FacebookPage", back_populates="user")
    
    # Add relationship with Chat
    chats = relationship("Chat", back_populates="user")

    @property
    def fb_page_token(self):
        if self.facebook_pages:
            return self.facebook_pages[0].access_token
        return None
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"