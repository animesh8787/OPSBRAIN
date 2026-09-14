import aiofiles
import asyncio
import base64
import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status
import fitz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.postgres.models import Document


def validate_upload(file: UploadFile) -> None:
    if file.content_type not in settings.allowed_upload_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "invalid_file_type",
                    "message": f"File type {file.content_type} is not allowed",
                }
            },
        )


async def save_upload_file(file: UploadFile, document_id: uuid.UUID) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    dest_path = Path(settings.upload_dir) / f"{document_id}.pdf"
    total_bytes = 0
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    try:
        async with aiofiles.open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": {
                                "code": "file_too_large",
                                "message": f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
                            }
                        },
                    )
                await out.write(chunk)
    except HTTPException:
        if dest_path.exists():
            dest_path.unlink()
        raise

    return str(dest_path)


async def create_document_record(
    db: AsyncSession, filename: str, doc_type: str, file_path: str, uploaded_by: uuid.UUID
) -> Document:
    document = Document(
        filename=filename,
        doc_type=doc_type,
        file_path=file_path,
        uploaded_by=uploaded_by,
        upload_status="pending",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def get_document_by_id(db: AsyncSession, document_id: uuid.UUID) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()


async def get_documents_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.uploaded_by == user_id)
        .order_by(Document.uploaded_at.desc())
    )
    return result.scalars().all()


async def get_document_page(db: AsyncSession, document_id: uuid.UUID, page_number: int) -> tuple[str, str, int | None]:
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "document_not_found", "message": "Document not found"}},
        )
    if page_number < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "invalid_page_number", "message": "Page number must be 1 or greater"}},
        )

    def _extract_page_sync(file_path: str, page_number: int) -> tuple[str, str]:
        doc = fitz.open(file_path)
        if page_number > doc.page_count:
            doc.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "page_not_found",
                        "message": f"Document has {doc.page_count} pages; page {page_number} does not exist",
                    }
                },
            )
        page = doc[page_number - 1]
        text = page.get_text()
        pix = page.get_pixmap(dpi=150)
        png_bytes = pix.tobytes("png")
        doc.close()
        image_data_uri = "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")
        return text, image_data_uri

    try:
        text, image_data_uri = await asyncio.to_thread(_extract_page_sync, document.file_path, page_number)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "page_extraction_failed", "message": "Failed to extract the requested page"}},
        )

    return text, image_data_uri, document.page_count
