from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMBase


class ConversationCreateRequest(BaseModel):
    pass


class ConversationResponse(ORMBase):
    id: UUID
    user_id: UUID | None
    created_at: datetime


class MessageCreateRequest(BaseModel):
    role: str  # values are "user" or "assistant"
    content: str
    citations: dict | None = None  # e.g. {"1": {"document_id": "...", "page_number": 12, "filename": "..."}} — shape is owned by the caller, not validated here


class MessageResponse(ORMBase):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    citations: dict | None
    created_at: datetime
