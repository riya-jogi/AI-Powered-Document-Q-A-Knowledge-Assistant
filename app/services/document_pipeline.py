"""
Document processing pipeline: extract, chunk, embed, and store
"""

import json

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import Document, DocumentChunk
from app.services.document_processor import document_processor
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)


class DocumentProcessingService:
    """Orchestrate the full document indexing pipeline."""

    def process_document(self, db: Session, document_id: int) -> Document:
        """
        Process an uploaded document: extract text, chunk, embed, and store.

        Updates document status throughout the pipeline.
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        try:
            document.status = "processing"
            db.commit()

            logger.info(f"Processing document {document_id}: {document.original_filename}")

            chunks, total_pages = document_processor.process_file(
                document.file_path, document.file_type
            )

            texts = [c.content for c in chunks]
            embeddings = embedding_service.embed_texts(texts)

            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

            for chunk, embedding in zip(chunks, embeddings):
                db.add(
                    DocumentChunk(
                        document_id=document_id,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        page_number=chunk.page_number,
                        token_count=chunk.token_count,
                        chunk_metadata=json.dumps(chunk.metadata),
                        embedding=embedding,
                    )
                )

            document.total_pages = total_pages
            document.total_chunks = len(chunks)
            document.status = "completed"
            db.commit()
            db.refresh(document)

            logger.info(
                f"Document {document_id} processed: {total_pages} pages, {len(chunks)} chunks"
            )
            return document

        except Exception as e:
            logger.error(f"Document processing failed for {document_id}: {e}")
            document.status = "failed"
            db.commit()
            raise


document_processing_service = DocumentProcessingService()
