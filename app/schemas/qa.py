"""Question answering schemas"""

from pydantic import BaseModel, Field


class QARequest(BaseModel):
    question: str = Field(..., min_length=1)
    document_id: int
    top_k: int = Field(default=5, ge=1, le=20)


class QASource(BaseModel):
    document: str
    page: int | None
    score: float
    chunk_id: int
    excerpt: str


class QAResponse(BaseModel):
    answer: str
    sources: list[QASource]
