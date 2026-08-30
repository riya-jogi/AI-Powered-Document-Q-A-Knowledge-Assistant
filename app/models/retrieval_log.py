"""
Retrieval log model for debugging and evaluation
"""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RetrievalLog(BaseModel):
    """Log of chunks retrieved for a given assistant message"""
    __tablename__ = "retrieval_logs"
    
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    
    message = relationship("Message", back_populates="retrieval_logs")
    chunk = relationship("DocumentChunk")
    
    def __repr__(self):
        return f"<RetrievalLog(message_id={self.message_id}, chunk_id={self.chunk_id}, rank={self.rank})>"
