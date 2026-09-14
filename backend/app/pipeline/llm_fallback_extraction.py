import json
import logging

from pydantic import BaseModel

from app.llm.generate import generate

logger = logging.getLogger(__name__)


class LLMFailureMode(BaseModel):
    description: str
    category: str | None = None


class LLMMaintenanceEvent(BaseModel):
    action: str
    event_date: str | None = None


class LLMFallbackResult(BaseModel):
    failure_modes: list[LLMFailureMode] = []
    maintenance_events: list[LLMMaintenanceEvent] = []
    regulations: list[str] = []


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


async def extract_llm_fallback(chunk_text: str) -> LLMFallbackResult:
    truncated = chunk_text[:2000]

    prompt = f"""Extract structured information from the following text and return ONLY valid JSON matching this exact shape:

{{
  "failure_modes": [
    {{"description": "...", "category": "..."}}
  ],
  "maintenance_events": [
    {{"action": "...", "event_date": "..."}}
  ],
  "regulations": ["..."]
}}

Field descriptions:
- failure_modes: equipment failures or malfunctions described in the text. Each has a short description and an optional category like "mechanical", "corrosion", or "electrical".
- maintenance_events: maintenance actions performed. Each has an action description and an event_date if a date is mentioned in the text, otherwise null.
- regulations: any regulation or standard codes mentioned, as plain strings.

If none are present for a field, return an empty list for that field. Do not invent information that is not in the text. Return ONLY the JSON object, no other text, no markdown code fences.

Text:
{truncated}
"""

    try:
        raw_text = await generate(prompt, json_mode=True)
        cleaned = _strip_markdown_fences(raw_text)
        parsed = json.loads(cleaned)
        return LLMFallbackResult.model_validate(parsed)
    except Exception as exc:
        logger.warning(
            "LLM fallback extraction failed: %s (chunk: %s)",
            exc,
            truncated[:80],
        )
        return LLMFallbackResult()
