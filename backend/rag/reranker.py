def rerank(query: str, results: list) -> list:
    """
    Phase 3 stretch interface stub. Real cross-encoder reranking is
    deliberately not implemented — this exists so the pipeline's
    architecture includes the interface, without adding a second model
    to load into memory alongside the embedding model and Ollama's LLM.
    Currently a pure identity passthrough: returns results unchanged,
    in their existing order.
    """
    return results
