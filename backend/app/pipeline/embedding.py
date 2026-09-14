"""Embedding stage. bge-large-en-v1.5 via sentence-transformers, stored in Postgres via pgvector."""

import asyncio

from sentence_transformers import SentenceTransformer

from app.db.postgres.models import Chunk

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


# Public entrypoint. Mutates chunk.embedding in place but does not commit — caller owns the transaction.
async def embed_and_store(chunks: list[Chunk]) -> None:
    if not chunks:
        return
    texts = [c.content for c in chunks]
    vectors = await embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk.embedding = vector
