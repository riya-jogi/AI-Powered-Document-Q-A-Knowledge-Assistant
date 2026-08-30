"""Conversation schemas"""

from datetime import datetime
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    document_id: int | None = None
    title: str | None = "New Conversation"


class ConversationResponse(BaseModel):
    id: int
    title: str
    document_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    sources: list[dict] | None = None

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    document_id: int | None
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime
