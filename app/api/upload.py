"""
Document upload API endpoints
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core import get_mime_type
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.logging import get_logger
from app.models import Document, User
from app.services.file_storage import file_storage

logger = get_logger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Upload a document for processing.

    Args:
        file: The document file to upload
        db: Database session

    Returns:
        Dictionary with upload status and document information
    """
    try:
        logger.info(f"Received file upload request: {file.filename}")

        # Save file using storage service
        saved_filename, file_path, file_size = await file_storage.save_uploaded_file(
            file, user_id=current_user.id
        )

        # Get file type and MIME type
        filename = file.filename if isinstance(file.filename, str) else str(file.filename)
        logger.info(f"Processing file: {filename}, type: {type(filename)}")

        parts = filename.rsplit('.', 1) if '.' in filename else [filename]
        file_type = parts[1].lower() if len(parts) > 1 else 'unknown'
        mime_type = get_mime_type(filename)

        logger.info(f"File details: type={file_type}, mime={mime_type}, size={file_size}")

        # Create database record
        original_filename = file.filename if isinstance(file.filename, str) else str(file.filename)
        logger.info(f"Creating document record with original_filename: {original_filename}")

        document = Document(
            user_id=current_user.id,
            filename=saved_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type,
            status="uploaded",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        logger.info(f"Document created in database: ID={document.id}")

        return {
            "success": True,
            "message": "Document uploaded successfully",
            "document": {
                "id": document.id,
                "filename": document.filename,
                "original_filename": document.original_filename,
                "file_size": document.file_size,
                "file_type": document.file_type,
                "status": document.status,
                "created_at": document.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback

        logger.error(f"Error uploading document: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.get("/documents")
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    List uploaded documents for the current user.

    Args:
        db: Database session

    Returns:
        Dictionary with list of documents
    """
    try:
        documents = (
            db.query(Document)
            .filter(Document.user_id == current_user.id)
            .order_by(Document.created_at.desc())
            .all()
        )

        document_list = [
            {
                "id": doc.id,
                "filename": doc.filename,
                "original_filename": doc.original_filename,
                "file_size": doc.file_size,
                "file_type": doc.file_type,
                "status": doc.status,
                "total_pages": doc.total_pages,
                "total_chunks": doc.total_chunks,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
            }
            for doc in documents
        ]

        return {
            "success": True,
            "count": len(document_list),
            "documents": document_list,
        }

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")


@router.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get details of a specific document.

    Args:
        document_id: ID of the document
        db: Database session

    Returns:
        Dictionary with document details
    """
    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id, Document.user_id == current_user.id)
            .first()
        )

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return {
            "success": True,
            "document": {
                "id": document.id,
                "filename": document.filename,
                "original_filename": document.original_filename,
                "file_path": document.file_path,
                "file_size": document.file_size,
                "file_type": document.file_type,
                "mime_type": document.mime_type,
                "status": document.status,
                "total_pages": document.total_pages,
                "total_chunks": document.total_chunks,
                "document_metadata": document.document_metadata,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Delete a document and its file.

    Args:
        document_id: ID of the document to delete
        db: Database session

    Returns:
        Dictionary with deletion status
    """
    try:
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

        logger.info(f"Document deleted: ID={document_id}")

        return {
            "success": True,
            "message": "Document deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete document")