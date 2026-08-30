"""
Conversation model for chat history
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Conversation(BaseModel):
    """Conversation model linking users to document Q&A sessions"""
    __tablename__ = "conversations"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), default="New Conversation")
    
    user = relationship("User", back_populates="conversations")
    document = relationship("Document", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"
