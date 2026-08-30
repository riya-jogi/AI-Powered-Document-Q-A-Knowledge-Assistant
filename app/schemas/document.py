"""Document schemas"""

from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str | None
    status: str
    total_pages: int
    total_chunks: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    status: str
    total_pages: int
    total_chunks: int
    message: str


class ChunkResponse(BaseModel):
    id: int
    chunk_index: int
    page_number: int | None
    token_count: int
    content: str

    class Config:
        from_attributes = True
