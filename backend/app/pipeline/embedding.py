"""Embedding stage. bge-large-en-v1.5 via sentence-transformers. Populated in a later task."""

import asyncio

from sentence_transformers import SentenceTransformer

from app.db.chroma import get_collection
from app.db.postgres.models import Chunk, Document

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    return _model


def _embed_texts_sync(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return await asyncio.to_thread(_embed_texts_sync, texts)


# Public entrypoint. Mutates chunk.embedding_id in place but does not commit — caller owns the transaction.
async def embed_and_store(document: Document, chunks: list[Chunk]) -> None:
    if not chunks:
        return
    texts = [c.content for c in chunks]
    vectors = await embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk.embedding_id = str(chunk.id)
    ids = [str(c.id) for c in chunks]
    embeddings = vectors
    documents = [c.content for c in chunks]
    metadatas = [
        {
            "document_id": str(chunk.document_id),
            "doc_type": document.doc_type,
            "equipment_tags": ",".join(str(eid) for eid in (chunk.equipment_ids or [])),
            "page_number": chunk.page_number if chunk.page_number is not None else -1,
            "section_title": chunk.section_title or "",
        }
        for chunk in chunks
    ]
    collection = get_collection()
    await asyncio.to_thread(
        collection.add,
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
