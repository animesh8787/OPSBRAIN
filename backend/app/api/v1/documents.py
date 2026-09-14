import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.postgres import get_db
from app.db.postgres.models import User
from app.pipeline.ingestion_orchestrator import ingest_document
from app.schemas import DocumentPageResponse, DocumentResponse, DocumentStatusResponse, DocumentUploadResponse
from app.services.document_service import (
    create_document_record,
    get_document_by_id,
    get_document_page,
    get_documents_by_user,
    save_upload_file,
    validate_upload,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_upload(file)

    document = await create_document_record(
        db=db,
        filename=file.filename,
        doc_type=doc_type,
        file_path="",  # placeholder, updated below once we know the final path
        uploaded_by=current_user.id,
    )

    try:
        file_path = await save_upload_file(file, document.id)
        document.file_path = file_path
        await db.commit()
    except HTTPException:
        document.upload_status = "failed"
        document.error_message = "File upload failed validation or size limits"
        await db.commit()
        raise

    background_tasks.add_task(ingest_document, document.id)

    return DocumentUploadResponse(document_id=document.id, status="pending")


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = await get_documents_by_user(db, current_user.id)
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "document_not_found", "message": "Document not found"}},
        )
    return document


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "document_not_found", "message": "Document not found"}},
        )
    return DocumentStatusResponse(
        document_id=document.id,
        status=document.upload_status,
        error_message=document.error_message,
    )


@router.get("/{document_id}/page/{page_number}", response_model=DocumentPageResponse)
async def get_document_page_route(
    document_id: uuid.UUID,
    page_number: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    text, image_data_uri, page_count = await get_document_page(db, document_id, page_number)
    return DocumentPageResponse(
        document_id=document_id,
        page_number=page_number,
        page_count=page_count,
        text=text,
        image_url=image_data_uri,
    )
