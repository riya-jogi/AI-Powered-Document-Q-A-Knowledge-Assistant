"""
Retrieval-Augmented Generation (RAG) pipeline
"""

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import Message, RetrievalLog
from app.schemas.qa import QAResponse, QASource
from app.services.llm_service import llm_service
from app.services.retrieval_service import RetrievalResult, retrieval_service

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.3


class RAGService:
    """Combine retrieval and LLM generation for document Q&A."""

    async def ask(
        self,
        db: Session,
        question: str,
        document_id: int,
        user_id: int,
        top_k: int = 5,
    ) -> QAResponse:
        """Answer a question using RAG over a specific document."""
        results = retrieval_service.search(
            db=db,
            query=question,
            document_id=document_id,
            user_id=user_id,
            top_k=top_k,
        )

        if not results or all(r.score < SIMILARITY_THRESHOLD for r in results):
            return QAResponse(
                answer="I couldn't find this information in the uploaded documents.",
                sources=[],
            )

        context = self._build_context(results)
        answer = await llm_service.generate_answer(question, context)

        sources = [
            QASource(
                document=r.document_name,
                page=r.page_number,
                score=r.score,
                chunk_id=r.chunk_id,
                excerpt=r.content[:300] + ("..." if len(r.content) > 300 else ""),
            )
            for r in results
        ]

        return QAResponse(answer=answer, sources=sources)

    async def ask_in_conversation(
        self,
        db: Session,
        question: str,
        document_id: int,
        user_id: int,
        conversation_id: int,
        top_k: int = 5,
    ) -> tuple[str, list[QASource], int]:
        """Ask a question within a conversation and persist messages."""
        qa_response = await self.ask(
            db=db,
            question=question,
            document_id=document_id,
            user_id=user_id,
            top_k=top_k,
        )

        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=question,
        )
        db.add(user_message)
        db.flush()

        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=qa_response.answer,
        )
        db.add(assistant_message)
        db.flush()

        for rank, source in enumerate(qa_response.sources, start=1):
            db.add(
                RetrievalLog(
                    message_id=assistant_message.id,
                    chunk_id=source.chunk_id,
                    similarity_score=source.score,
                    rank=rank,
                )
            )

        db.commit()
        return qa_response.answer, qa_response.sources, assistant_message.id

    @staticmethod
    def _build_context(results: list[RetrievalResult]) -> str:
        """Build context string from retrieved chunks."""
        parts = []
        for i, result in enumerate(results, start=1):
            page_info = f"Page {result.page_number}" if result.page_number else "Unknown page"
            parts.append(
                f"[Chunk {i} — {result.document_name}, {page_info}, relevance: {result.score:.2f}]\n"
                f"{result.content}"
            )
        return "\n\n".join(parts)


rag_service = RAGService()
