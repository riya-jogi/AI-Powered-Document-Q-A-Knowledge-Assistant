"""
Vector similarity search using pgvector
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models import Document, DocumentChunk
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    chunk_id: int
    document_id: int
    page_number: int | None
    content: str
    score: float
    document_name: str


class RetrievalService:
    """Semantic search over document chunks using pgvector."""

    def search(
        self,
        db: Session,
        query: str,
        document_id: int,
        user_id: int,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """
        Search for relevant chunks in a document owned by the user.

        Uses cosine distance; score is converted to similarity (1 - distance).
        """
        top_k = top_k or settings.TOP_K_RESULTS

        document = (
            db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .first()
        )
        if not document:
            raise ValueError("Document not found or access denied")

        if document.status != "completed":
            raise ValueError("Document is still processing or failed")

        query_embedding = embedding_service.embed_query(query)

        results = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.embedding.isnot(None),
            )
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )

        retrieval_results: list[RetrievalResult] = []
        for rank, chunk in enumerate(results):
            distance = self._cosine_distance(query_embedding, chunk.embedding)
            similarity = max(0.0, 1.0 - distance)
            retrieval_results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    score=round(similarity, 4),
                    document_name=document.original_filename,
                )
            )

        logger.info(
            f"Retrieved {len(retrieval_results)} chunks for document {document_id}"
        )
        return retrieval_results

    @staticmethod
    def _cosine_distance(vec_a: list[float], vec_b) -> float:
        """Compute cosine distance between two vectors."""
        import numpy as np

        a = np.array(vec_a)
        b = np.array(vec_b)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 1.0
        cosine_sim = dot / (norm_a * norm_b)
        return 1.0 - cosine_sim


retrieval_service = RetrievalService()
