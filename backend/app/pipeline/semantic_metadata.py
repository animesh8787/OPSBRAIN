import json
import logging

from pydantic import BaseModel

from app.llm.generate import generate
from app.pipeline.chunking import ChunkData
from app.pipeline.llm_fallback_extraction import _strip_markdown_fences

logger = logging.getLogger(__name__)


class SemanticMetadataResult(BaseModel):
    summary: str | None = None
    primary_equipment: str | None = None
    revision: str | None = None


async def extract_semantic_metadata(chunks: list[ChunkData]) -> SemanticMetadataResult:
    full_text = " ".join(chunk.content for chunk in chunks)
    truncated = full_text[:4000].strip()

    if not truncated:
        return SemanticMetadataResult()

    prompt = f"""Extract semantic metadata from the following document and return ONLY valid JSON matching this exact shape:

{{
  "summary": "...",
  "primary_equipment": "...",
  "revision": "..."
}}

Field descriptions:
- summary: a 1-3 sentence summary of what the document is about.
- primary_equipment: the single most prominently discussed equipment tag or equipment name in the document, or null if none is clearly primary.
- revision: a revision/version number or date if one is explicitly stated in the document text, or null if not present.

Do not invent information not present in the text. Return ONLY the JSON object, no markdown fences, no other text.

Document:
{truncated}
"""

    try:
        raw_text = await generate(prompt, json_mode=True)
        cleaned = _strip_markdown_fences(raw_text)
        parsed = json.loads(cleaned)
        return SemanticMetadataResult.model_validate(parsed)
    except Exception as exc:
        logger.warning("Semantic metadata extraction failed: %s", exc)
        return SemanticMetadataResult()
