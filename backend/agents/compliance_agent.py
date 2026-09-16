from app.llm.generate import generate
from app.schemas import EquipmentNeighborhoodItem, SearchResult

NO_EQUIPMENT_MESSAGE = (
    "I couldn't find a specific equipment tag with linked regulations for this query. "
    "Mention an equipment tag (e.g. P-101A) so I can look up the regulations that apply "
    "to it and its connected equipment."
)


def _build_regulations_block(graph_context: list[EquipmentNeighborhoodItem]) -> str:
    lines = [
        f"{item.tag_number}: {', '.join(item.regulations)}"
        for item in graph_context
        if item.regulations
    ]
    return "\n".join(lines)


def _build_context_block(chunks: list[SearchResult]) -> str:
    return "\n".join(
        f'[{i}] ({chunk.document_filename}, p.{chunk.page_number}): "{chunk.content}"'
        for i, chunk in enumerate(chunks, start=1)
    )


async def generate_compliance_answer(
    query: str,
    graph_context: list[EquipmentNeighborhoodItem] | None,
    retrieved_chunks: list[SearchResult],
) -> str:
    """
    Compliance answers are grounded in the regulations table (populated during
    ingestion from real code/equipment links, e.g. API-570 tied to a pressure
    vessel tag) rather than free-text retrieval alone - a regulation code is
    either on record for the equipment in the query or it isn't. Document
    chunks are only used to fill in explanatory detail around those codes.
    """
    if not graph_context or not any(item.regulations for item in graph_context):
        return NO_EQUIPMENT_MESSAGE

    regulations_block = _build_regulations_block(graph_context)
    context_block = _build_context_block(retrieved_chunks)

    prompt = f"""You are a compliance assistant for industrial equipment.

Regulations on record for the equipment involved (from verified equipment records):
{regulations_block}

Supporting document context:
{context_block}

Answer using ONLY the regulations and context above. Cite every factual claim about document content with [n], matching the bracketed numbers in the context. If a regulation is listed but not explained in the supporting context, state its code and say that no further detail is available in the ingested documents. Keep the answer concise and direct.

Question: {query}"""

    try:
        return (await generate(prompt, json_mode=False)).strip()
    except Exception as exc:
        raise RuntimeError(f"Ollama generation failed: {exc}") from exc
