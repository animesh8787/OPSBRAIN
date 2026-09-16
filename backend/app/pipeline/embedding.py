"""Embedding stage. bge-large-en-v1.5 via HF's hosted Inference API, stored in Postgres via pgvector."""

import math

import httpx

from app.config import settings
from app.db.postgres.models import Chunk

_INFERENCE_URL = f"https://router.huggingface.co/hf-inference/models/{settings.embedding_model}/pipeline/feature-extraction"


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _INFERENCE_URL,
            headers={"Authorization": f"Bearer {settings.hf_token}"},
            json={"inputs": texts, "options": {"wait_for_model": True}},
            timeout=60.0,
        )
        resp.raise_for_status()
    # bge-large-en-v1.5 has no built-in Normalize module, so the raw API
    # response is unnormalized - dense_search's cosine_distance is scale
    # invariant so this wouldn't change ranking either way, but normalizing
    # here keeps stored vectors consistent with what the old local
    # normalize_embeddings=True path produced.
    return [_normalize(v) for v in resp.json()]


# Public entrypoint. Mutates chunk.embedding in place but does not commit — caller owns the transaction.
async def embed_and_store(chunks: list[Chunk]) -> None:
    if not chunks:
        return
    texts = [c.content for c in chunks]
    vectors = await embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk.embedding = vector
