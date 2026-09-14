import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.postgres import get_db
from app.db.postgres.models import User
from app.schemas import ConversationCreateRequest, ConversationResponse, MessageCreateRequest, MessageResponse
from app.services.conversation_service import create_conversation, create_message, list_messages

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation_route(
    payload: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_conversation(db, user_id=current_user.id)


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_message_route(
    conversation_id: uuid.UUID,
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_message(
        db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        role=payload.role,
        content=payload.content,
        citations=payload.citations,
    )


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages_route(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_messages(db, conversation_id=conversation_id, user_id=current_user.id)
