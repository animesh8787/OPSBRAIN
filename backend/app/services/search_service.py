import uuid

from fastapi import HTTPException, status
from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.simple_cache import SimpleBoundedCache, dense_search_cache
from app.db.postgres.models import Chunk, Document, Equipment
from app.pipeline.embedding import embed_texts
from app.schemas import SearchResult


async def _resolve_equipment_filter(db: AsyncSession, equipment_tags: list[str] | None) -> list[str] | None:
    if not equipment_tags:
        return None
    result = await db.execute(select(Equipment.id).where(Equipment.tag_number.in_(equipment_tags)))
    return [str(row) for row in result.scalars().all()]


def _distance_to_score(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - distance))


async def dense_search(
    db: AsyncSession,
    query: str,
    top_k: int,
    doc_type_filter: list[str] | None,
    equipment_filter: list[str] | None,
) -> list[SearchResult]:
    cache_payload = {
        "query": query,
        "top_k": top_k,
        "doc_type_filter": doc_type_filter,
        "equipment_filter": equipment_filter,
    }
    key = dense_search_cache.make_key(cache_payload)
    cached = dense_search_cache.get(key)
    if cached is not None:
        return cached

    vectors = await embed_texts([query])
    if not vectors:
        dense_search_cache.set(key, [])
        return []
    query_vector = vectors[0]

    equipment_uuids = await _resolve_equipment_filter(db, equipment_filter)
    if equipment_uuids is not None and len(equipment_uuids) == 0:
        dense_search_cache.set(key, [])
        return []

    distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
    stmt = (
        select(Chunk, Document, distance)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.embedding.is_not(None))
    )
    if doc_type_filter:
        stmt = stmt.where(Document.doc_type.in_(doc_type_filter))
    if equipment_uuids is not None:
        equipment_uuid_objs = [uuid.UUID(u) for u in equipment_uuids]
        stmt = stmt.where(Chunk.equipment_ids.op("&&")(equipment_uuid_objs))
    stmt = stmt.order_by(distance).limit(top_k)

    result = await db.execute(stmt)
    rows = result.all()

    search_results = [
        SearchResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            score=_distance_to_score(row_distance),
            page_number=chunk.page_number,
            section_title=chunk.section_title,
            document_filename=document.filename,
            doc_type=document.doc_type,
        )
        for chunk, document, row_distance in rows
    ]

    dense_search_cache.set(key, search_results)
    return search_results


SIBLING_SCORE_PLACEHOLDER = 1.0  # siblings are not ranked by similarity; this is a neutral placeholder, not a real score


async def get_chunk_siblings(db: AsyncSession, chunk_id: uuid.UUID) -> list[SearchResult]:
    result = await db.execute(select(Chunk).where(Chunk.id == chunk_id))
    source_chunk = result.scalar_one_or_none()
    if source_chunk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "chunk_not_found", "message": "Chunk not found"}},
        )

    if source_chunk.section_title is None:
        section_condition = Chunk.section_title.is_(None)
    else:
        section_condition = Chunk.section_title == source_chunk.section_title

    result = await db.execute(
        select(Chunk)
        .where(
            Chunk.document_id == source_chunk.document_id,
            section_condition,
            Chunk.id != chunk_id,
        )
        .order_by(Chunk.chunk_index)
    )
    sibling_chunks = result.scalars().all()

    if not sibling_chunks:
        return []

    doc_result = await db.execute(select(Document).where(Document.id == source_chunk.document_id))
    document = doc_result.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "document_not_found", "message": "Document not found"}},
        )

    return [
        SearchResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            score=SIBLING_SCORE_PLACEHOLDER,
            page_number=chunk.page_number,
            section_title=chunk.section_title,
            document_filename=document.filename,
            doc_type=document.doc_type,
        )
        for chunk in sibling_chunks
    ]


RRF_K = 60  # standard Reciprocal Rank Fusion constant from the original RRF paper


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


async def _fetch_candidate_chunks(
    db: AsyncSession, doc_type_filter: list[str] | None, equipment_filter_tags: list[str] | None
) -> list[Chunk]:
    query = select(Chunk).join(Document, Chunk.document_id == Document.id)

    if doc_type_filter:
        query = query.where(Document.doc_type.in_(doc_type_filter))

    if equipment_filter_tags:
        equipment_uuids = await _resolve_equipment_filter(db, equipment_filter_tags)
        if not equipment_uuids:
            return []
        # Convert to UUID objects for correct type matching against the UUID[] column
        uuid_list = [uuid.UUID(u) for u in equipment_uuids]
        query = query.where(Chunk.equipment_ids.op("&&")(uuid_list))

    query = query.limit(500)
    result = await db.execute(query)
    return result.scalars().all()


# ── BM25 index caching ───────────────────────────────────────────────────────
# Cache the candidate corpus + BM25Okapi object per (filters, version) combo.
# Invalidated by bumping _chunks_version when new documents are ingested.
_bm25_index_cache = SimpleBoundedCache(max_size=20)
_chunks_version: int = 0


def bump_chunks_version() -> None:
    global _chunks_version
    _chunks_version += 1


def get_chunks_version() -> int:
    return _chunks_version


async def _get_cached_bm25_index(
    db: AsyncSession,
    doc_type_filter: list[str] | None,
    equipment_filter_tags: list[str] | None,
) -> tuple[list[Chunk], BM25Okapi | None]:
    key_payload = {
        "doc_type_filter": doc_type_filter,
        "equipment_filter": equipment_filter_tags,
        "version": get_chunks_version(),
    }
    key = _bm25_index_cache.make_key(key_payload)
    cached = _bm25_index_cache.get(key)
    if cached is not None:
        return cached

    candidates = await _fetch_candidate_chunks(db, doc_type_filter, equipment_filter_tags)
    if not candidates:
        result: tuple[list[Chunk], BM25Okapi | None] = (candidates, None)
        _bm25_index_cache.set(key, result)
        return result

    corpus = [_tokenize(c.content) for c in candidates]
    bm25 = BM25Okapi(corpus)
    result = (candidates, bm25)
    _bm25_index_cache.set(key, result)
    return result


def _bm25_rank_with_index(query: str, candidates: list[Chunk], bm25: BM25Okapi | None) -> list[uuid.UUID]:
    if not candidates or bm25 is None:
        return []
    scores = bm25.get_scores(_tokenize(query))
    ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
    return [c.id for c, score in ranked]


def _reciprocal_rank_fusion(
    dense_ranked_ids: list[uuid.UUID], bm25_ranked_ids: list[uuid.UUID]
) -> list[uuid.UUID]:
    fused_scores: dict[uuid.UUID, float] = {}
    for rank, chunk_id in enumerate(dense_ranked_ids, start=1):
        fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
    for rank, chunk_id in enumerate(bm25_ranked_ids, start=1):
        fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
    return sorted(fused_scores.keys(), key=lambda cid: fused_scores[cid], reverse=True)


async def hybrid_search(
    db: AsyncSession,
    query: str,
    top_k: int,
    doc_type_filter: list[str] | None,
    equipment_filter: list[str] | None,
) -> list[SearchResult]:
    dense_results = await dense_search(
        db, query, top_k=max(top_k * 3, 30), doc_type_filter=doc_type_filter, equipment_filter=equipment_filter
    )
    dense_ranked_ids = [r.chunk_id for r in dense_results]

    bm25_candidates, bm25_index = await _get_cached_bm25_index(db, doc_type_filter, equipment_filter)
    bm25_ranked_ids = _bm25_rank_with_index(query, bm25_candidates, bm25_index)

    fused_ids = _reciprocal_rank_fusion(dense_ranked_ids, bm25_ranked_ids)

    dense_lookup = {r.chunk_id: r for r in dense_results}

    # MVP simplification: BM25-only hits (not present in dense results) are not included in fused output,
    # since building their SearchResult requires a full second metadata lookup path. In practice the dense
    # candidate pool (top_k*3) is large enough that this rarely excludes anything the fusion would have ranked highly.
    filtered_ids = [cid for cid in fused_ids if cid in dense_lookup]
    return [dense_lookup[cid] for cid in filtered_ids[:top_k]]
