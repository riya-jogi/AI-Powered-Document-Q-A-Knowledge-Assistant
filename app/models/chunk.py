"""
DocumentChunk model for storing text chunks and embeddings
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.models.base import BaseModel


class DocumentChunk(BaseModel):
    """DocumentChunk model for storing text chunks with embeddings"""
    __tablename__ = "document_chunks"
    
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    content = Column(Text, nullable=False)
    page_number = Column(Integer)  # Page number from original document
    token_count = Column(Integer, default=0)
    chunk_type = Column(String(50), default="text")  # text, table, image, etc.
    chunk_metadata = Column(Text)  # JSON string for additional metadata (section headers, etc.)
    embedding = Column(Vector(384))  # all-MiniLM-L6-v2 produces 384-dimensional vectors
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"