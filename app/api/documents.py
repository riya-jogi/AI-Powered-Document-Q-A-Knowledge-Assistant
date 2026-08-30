"""
Document management API endpoints (v1)
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core import get_mime_type
from app.core.logging import get_logger
from app.models import Document, DocumentChunk, User
from app.schemas.document import ChunkResponse, DocumentResponse, DocumentUploadResponse
from app.services.file_storage import file_storage
from app.services.document_pipeline import document_processing_service

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document, process it, and index chunks with embeddings."""
    try:
        saved_filename, file_path, file_size = await file_storage.save_uploaded_file(
            file, user_id=current_user.id
        )

        filename = str(file.filename) if file.filename else "unknown"
        parts = filename.rsplit(".", 1) if "." in filename else [filename]
        file_type = parts[1].lower() if len(parts) > 1 else "unknown"
        mime_type = get_mime_type(filename)

        document = Document(
            user_id=current_user.id,
            filename=saved_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type,
            status="uploaded",
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        document = document_processing_service.process_document(db, document.id)

        return DocumentUploadResponse(
            id=document.id,
            filename=document.original_filename,
            original_filename=document.original_filename,
            status=document.status,
            total_pages=document.total_pages,
            total_chunks=document.total_chunks,
            message="Document uploaded and processed successfully",
        )

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents for the current user."""
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific document."""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document and its associated chunks."""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    file_storage.delete_file(document.file_path)
    db.delete(document)
    db.commit()
    return {"success": True, "message": "Document deleted successfully"}


@router.get("/{document_id}/chunks", response_model=list[ChunkResponse])
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List chunks for a document (useful for debugging)."""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )
    return chunks
