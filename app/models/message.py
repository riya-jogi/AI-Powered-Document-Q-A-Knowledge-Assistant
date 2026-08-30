"""
Message model for conversation history
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Message(BaseModel):
    """Message model for user and assistant messages in a conversation"""
    __tablename__ = "messages"
    
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    conversation = relationship("Conversation", back_populates="messages")
    retrieval_logs = relationship("RetrievalLog", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}')>"
