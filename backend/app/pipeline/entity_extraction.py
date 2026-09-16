"""Entity extraction stage. Regex-first, LLM fallback for ambiguous prose. Populated in a later task."""

import logging
import re
from dataclasses import dataclass

from app.pipeline.chunking import ChunkData
from app.pipeline.llm_fallback_extraction import extract_llm_fallback, LLMFallbackResult

logger = logging.getLogger(__name__)

EQUIPMENT_TAG_PATTERN = re.compile(r'\b[A-Z]{1,3}-\d{2,4}[A-Z]?\b')
REGULATION_PATTERN = re.compile(r'\b(?:OSHA|API|ASME|ISO)[\s-]?\d{3,5}[-\w]*\b')

REGEX_MATCH_CONFIDENCE = 0.95


@dataclass
class ExtractedEntity:
    chunk_index: int          # which chunk this entity came from, by chunk_index
    entity_type: str          # "equipment" or "regulation"
    entity_text: str          # raw matched text, as it appeared in the source
    normalized_value: str     # uppercased, whitespace-stripped version of entity_text
    confidence: float


def _extract_regex_entities(chunk: ChunkData) -> list[ExtractedEntity]:
    seen = set()
    entities = []

    for match in EQUIPMENT_TAG_PATTERN.finditer(chunk.content):
        normalized = match.group().strip().upper()
        key = ("equipment", normalized)
        if key not in seen:
            seen.add(key)
            entities.append(
                ExtractedEntity(
                    chunk_index=chunk.chunk_index,
                    entity_type="equipment",
                    entity_text=match.group(),
                    normalized_value=normalized,
                    confidence=REGEX_MATCH_CONFIDENCE,
                )
            )

    for match in REGULATION_PATTERN.finditer(chunk.content):
        normalized = match.group().strip().upper()
        key = ("regulation", normalized)
        if key not in seen:
            seen.add(key)
            entities.append(
                ExtractedEntity(
                    chunk_index=chunk.chunk_index,
                    entity_type="regulation",
                    entity_text=match.group(),
                    normalized_value=normalized,
                    confidence=REGEX_MATCH_CONFIDENCE,
                )
            )

    return entities


# STUB — real Ollama call is separate infra work, added in a later task. Control flow is wired now so that becomes a small isolated change rather than a redesign.
async def _extract_llm_fallback(chunk: ChunkData) -> list[ExtractedEntity]:
    logger.info(f"[entity extraction stub] LLM fallback would run here for chunk_index={chunk.chunk_index} — not implemented yet")
    return []


# Public entrypoint. Regex-first per chunk; LLM fallback only triggers for chunks with zero regex hits (Part 4 of the build guide).
async def extract_entities(chunks: list[ChunkData]) -> list[ExtractedEntity]:
    all_entities = []
    for chunk in chunks:
        regex_entities = _extract_regex_entities(chunk)
        if regex_entities:
            all_entities.extend(regex_entities)
        else:
            llm_entities = await _extract_llm_fallback(chunk)
            all_entities.extend(llm_entities)
    return all_entities


async def extract_llm_structured_data(chunks: list[ChunkData]) -> dict[int, LLMFallbackResult]:
    results: dict[int, LLMFallbackResult] = {}
    for chunk in chunks:
        regex_entities = _extract_regex_entities(chunk)
        if not regex_entities:
            llm_result = await extract_llm_fallback(chunk.content)
            results[chunk.chunk_index] = llm_result
    return results
