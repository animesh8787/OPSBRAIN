import json
import logging
import os

from app.llm.generate import generate
from app.pipeline.llm_fallback_extraction import _strip_markdown_fences

logger = logging.getLogger(__name__)


async def refine_relationships_llm(
    equipment_connections: list,
    regulation_links: list,
    chunks_data: list,
) -> tuple[list, list]:
    """
    Optional LLM pass to filter coincidental co-occurrence noise from
    genuine equipment relationships and regulation links.

    Opt-in via ENABLE_LLM_RELATIONSHIP_REFINEMENT env var.
    Fails open: any LLM or parsing error returns the original inputs unchanged.
    """
    enabled = os.environ.get("ENABLE_LLM_RELATIONSHIP_REFINEMENT", "false").lower() == "true"
    if not enabled:
        return equipment_connections, regulation_links

    if not equipment_connections and not regulation_links:
        return equipment_connections, regulation_links

    # Build chunk index -> content lookup for context
    chunk_index_to_content = {c.chunk_index: c.content for c in chunks_data}

    # Assemble prompt
    lines = [
        "You are reviewing candidate equipment relationships and regulation links extracted from industrial documents.",
        "Some candidates represent genuine relationships; others are coincidental co-occurrences.",
        "",
        "Equipment connections (co-occurrence candidates):",
    ]
    for i, conn in enumerate(equipment_connections):
        lines.append(f"{i}: {conn.equipment_tag_a} <-> {conn.equipment_tag_b} (chunks: {conn.chunk_indices})")
        for ci in conn.chunk_indices[:2]:  # limit context to first 2 chunks per candidate
            text = chunk_index_to_content.get(ci, "")
            lines.append(f"   chunk {ci}: {text[:200]}")

    lines.append("")
    lines.append("Regulation links:")
    for i, link in enumerate(regulation_links):
        lines.append(f"{i}: {link.equipment_tag} <-> {link.regulation_code} (chunks: {link.chunk_indices})")
        for ci in link.chunk_indices[:2]:
            text = chunk_index_to_content.get(ci, "")
            lines.append(f"   chunk {ci}: {text[:200]}")

    lines.append("")
    lines.append("Return ONLY valid JSON with this exact shape:")
    lines.append('{')
    lines.append('  "genuine_equipment_connections": [0, 2],  // list of indices from the equipment connections above that are genuine')
    lines.append('  "genuine_regulation_links": [1]           // list of indices from the regulation links above that are genuine')
    lines.append('}')
    lines.append("")
    lines.append("If none are genuine for a category, return an empty list. Do not invent indices. Return ONLY the JSON object, no other text, no markdown code fences.")

    prompt = "\n".join(lines)

    try:
        raw_text = await generate(prompt, json_mode=True)
        cleaned = _strip_markdown_fences(raw_text)
        parsed = json.loads(cleaned)

        genuine_eq = set(parsed.get("genuine_equipment_connections", []))
        genuine_reg = set(parsed.get("genuine_regulation_links", []))

        filtered_eq = [conn for i, conn in enumerate(equipment_connections) if i in genuine_eq]
        filtered_reg = [link for i, link in enumerate(regulation_links) if i in genuine_reg]

        return filtered_eq, filtered_reg
    except Exception as exc:
        logger.warning(f"LLM relationship refinement failed, keeping all co-occurrence candidates: {exc}")
        return equipment_connections, regulation_links
