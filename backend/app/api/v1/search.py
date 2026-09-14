import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.postgres import get_db
from app.db.postgres.models import User
from app.schemas import ChunkSiblingsResponse, DenseSearchRequest, HybridSearchRequest, SearchResponse
from app.services.search_service import dense_search, get_chunk_siblings, hybrid_search

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.post("/dense", response_model=SearchResponse)
async def search_dense(
    payload: DenseSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = await dense_search(
        db=db,
        query=payload.query,
        top_k=payload.top_k,
        doc_type_filter=payload.doc_type_filter,
        equipment_filter=payload.equipment_filter,
    )
    return SearchResponse(results=results, query=payload.query, total_results=len(results))


@router.post("/hybrid", response_model=SearchResponse)
async def search_hybrid(
    payload: HybridSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = await hybrid_search(
        db=db,
        query=payload.query,
        top_k=payload.top_k,
        doc_type_filter=payload.doc_type_filter,
        equipment_filter=payload.equipment_filter,
    )
    return SearchResponse(results=results, query=payload.query, total_results=len(results))


@router.get("/chunk/{chunk_id}/siblings", response_model=ChunkSiblingsResponse)
async def get_siblings(
    chunk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    siblings = await get_chunk_siblings(db, chunk_id)
    return ChunkSiblingsResponse(chunk_id=chunk_id, siblings=siblings)
