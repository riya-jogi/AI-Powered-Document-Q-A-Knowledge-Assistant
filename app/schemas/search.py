"""Search schemas"""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: int
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    chunk_id: int
    page: int | None
    score: float
    content: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
