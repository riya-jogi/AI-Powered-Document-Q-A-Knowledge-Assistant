"""
Semantic search API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.retrieval_service import retrieval_service

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Perform semantic search over document chunks."""
    try:
        results = retrieval_service.search(
            db=db,
            query=request.query,
            document_id=request.document_id,
            user_id=current_user.id,
            top_k=request.top_k,
        )
        return SearchResponse(
            query=request.query,
            results=[
                SearchResult(
                    chunk_id=r.chunk_id,
                    page=r.page_number,
                    score=r.score,
                    content=r.content,
                )
                for r in results
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
