from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base

class FacebookPage(Base):
    __tablename__ = "facebook_pages"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    picture_url = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationship with User model
    user = relationship("User", back_populates="facebook_pages") 