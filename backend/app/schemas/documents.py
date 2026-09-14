from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMBase


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    status: str = "pending"


class DocumentResponse(ORMBase):
    id: UUID
    filename: str
    doc_type: str
    page_count: int | None
    upload_status: str
    uploaded_at: datetime
    processed_at: datetime | None
    error_message: str | None


class DocumentStatusResponse(BaseModel):
    document_id: UUID
    status: str
    error_message: str | None = None


class DocumentPageResponse(BaseModel):
    document_id: UUID
    page_number: int
    page_count: int | None
    text: str | None
    image_url: str | None
