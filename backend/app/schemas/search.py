from uuid import UUID

from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    content: str
    score: float
    page_number: int | None
    section_title: str | None
    document_filename: str
    doc_type: str


class DenseSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    doc_type_filter: list[str] | None = None
    equipment_filter: list[str] | None = None


class HybridSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    doc_type_filter: list[str] | None = None
    equipment_filter: list[str] | None = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    total_results: int


class ChunkSiblingsResponse(BaseModel):
    chunk_id: UUID
    siblings: list[SearchResult]
