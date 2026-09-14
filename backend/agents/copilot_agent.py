from app.llm.generate import generate
from app.schemas import SearchResult

MIN_CHUNK_WORDS = 8  # chunks shorter than this are almost always heading/section-title fragments, not real content - exclude them from context to avoid polluting the prompt with noise


def _filter_meaningful_chunks(chunks: list[SearchResult]) -> list[SearchResult]:
    """
    Drop chunks that are too short to be real answer content (typically
    section headings or fragments from chunking, e.g. "4.1 Multi-Hop
    Equipment Relationships" on its own). If filtering would remove every
    chunk, fall back to the original unfiltered list rather than sending
    the LLM an empty context - a noisy answer is better than no context
    at all in that edge case.
    """
    filtered = [c for c in chunks if len(c.content.split()) >= MIN_CHUNK_WORDS]
    return filtered if filtered else chunks


def _build_context_block(chunks: list[SearchResult]) -> str:
    lines = []
    for i, chunk in enumerate(chunks, start=1):
        lines.append(f'[{i}] ({chunk.document_filename}, p.{chunk.page_number}): "{chunk.content}"')
    return "\n".join(lines)


async def generate_answer(query: str, retrieved_chunks: list[SearchResult]) -> str:
    """
    Real generation via a locally running Ollama instance. Strictly
    grounded in retrieved_chunks via the prompt below - the model is
    explicitly instructed not to answer beyond the provided context, and
    to say so plainly if the context is insufficient. citation.py's
    extract_and_verify_citations still runs after this and will strip any
    [n] marker that doesn't correspond to a real retrieved chunk index,
    so a hallucinated citation number is caught downstream even if the
    model produces one.
    """
    if not retrieved_chunks:
        return "I don't have enough information in the available documents to answer that."

    meaningful_chunks = _filter_meaningful_chunks(retrieved_chunks)
    context_block = _build_context_block(meaningful_chunks)

    prompt = f"""Context:
{context_block}

Answer using ONLY the context above. Cite every factual claim with [n], matching the bracketed numbers in the context. If the context doesn't fully answer the question, say so explicitly rather than guessing. Keep the answer concise and direct.

Question: {query}"""

    try:
        return (await generate(prompt, json_mode=False)).strip()
    except Exception as exc:
        # If Ollama is unreachable, the model isn't pulled, or generation
        # otherwise fails, surface a clear message rather than letting this
        # exception propagate as an opaque 500 - api/chat.py's own generic
        # exception handler would catch this anyway, but this specific
        # message is more actionable for debugging during a demo.
        raise RuntimeError(f"Ollama generation failed: {exc}") from exc


def generate_answer_fallback_stub(query: str, retrieved_chunks: list[SearchResult]) -> str:
    """
    STUB generation step. Does not call a real LLM. Assembles a deterministic
    answer by quoting the first sentence of each retrieved chunk's content,
    with an [n] marker per chunk, in retrieval order. This exists so the
    graph can be tested end-to-end today; replace this function's body with
    a real Ollama call in a future task without changing its signature or
    how orchestrator.py calls it.
    """
    if not retrieved_chunks:
        return "I don't have enough information in the available documents to answer that."

    parts = [f'Based on the available documents, regarding "{query}":']
    for i, chunk in enumerate(retrieved_chunks, start=1):
        first_sentence = chunk.content.split(". ")[0].strip().rstrip(".") + "."
        parts.append(f"{first_sentence} [{i}]")

    return " ".join(parts)
