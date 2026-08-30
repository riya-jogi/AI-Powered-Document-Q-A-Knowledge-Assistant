"""
Document model for storing uploaded document metadata
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Document(BaseModel):
    """Document model for storing uploaded files"""
    __tablename__ = "documents"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, etc.
    mime_type = Column(String(100))
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    total_pages = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    document_metadata = Column(Text)  # JSON string for additional metadata

    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="document", cascade="all, delete-orphan")

    @property
    def is_ready_for_qna(self) -> bool:
        """Return whether this document is fully indexed and ready for Q&A."""
        return self.status == "completed" and (self.total_chunks is None or self.total_chunks > 0)

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"