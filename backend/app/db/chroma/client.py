import chromadb

from app.config import settings

_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)


def get_collection():
    return _client.get_or_create_collection(
        name="industrial_knowledge",
        metadata={"hnsw:space": "cosine"},
    )
