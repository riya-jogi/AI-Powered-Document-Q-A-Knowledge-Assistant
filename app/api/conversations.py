"""
Conversation management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Conversation, Document, Message, User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new conversation, optionally linked to a document."""
    if data.document_id is not None:
        document = (
            db.query(Document)
            .filter(Document.id == data.document_id, Document.user_id == current_user.id)
            .first()
        )
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

    conversation = Conversation(
        user_id=current_user.id,
        document_id=data.document_id,
        title=data.title or "New Conversation",
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all conversations for the current user."""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return conversations


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get conversation with full message history."""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at,
        )
        for m in sorted(conversation.messages, key=lambda x: x.created_at)
    ]

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        document_id=conversation.document_id,
        messages=messages,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a question in a conversation and get an AI response."""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.document_id:
        raise HTTPException(
            status_code=400,
            detail="Conversation is not linked to a document",
        )

    try:
        answer, sources, message_id = await rag_service.ask_in_conversation(
            db=db,
            question=data.content,
            document_id=conversation.document_id,
            user_id=current_user.id,
            conversation_id=conversation_id,
            top_k=data.top_k,
        )

        message = db.query(Message).filter(Message.id == message_id).first()

        return MessageResponse(
            id=message.id,
            role="assistant",
            content=answer,
            created_at=message.created_at,
            sources=[s.model_dump() for s in sources],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
