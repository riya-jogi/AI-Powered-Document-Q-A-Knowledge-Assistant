"""
Question answering API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.qa import QARequest, QAResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api/v1/qa", tags=["qa"])


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask a question about a document using RAG."""
    try:
        return await rag_service.ask(
            db=db,
            question=request.question,
            document_id=request.document_id,
            user_id=current_user.id,
            top_k=request.top_k,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
