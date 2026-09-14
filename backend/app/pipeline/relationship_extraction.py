"""Relationship extraction stage. Co-occurrence only. Populated in a later task."""

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations

from app.pipeline.entity_extraction import ExtractedEntity


@dataclass
class CandidateEquipmentConnection:
    equipment_tag_a: str
    equipment_tag_b: str
    chunk_indices: list[int] = field(default_factory=list)


@dataclass
class CandidateRegulationLink:
    equipment_tag: str
    regulation_code: str
    chunk_indices: list[int] = field(default_factory=list)


def _group_by_chunk(entities: list[ExtractedEntity]) -> dict[int, list[ExtractedEntity]]:
    grouped = defaultdict(list)
    for entity in entities:
        grouped[entity.chunk_index].append(entity)
    return dict(grouped)


def _extract_equipment_pairs(chunk_entities: list[ExtractedEntity]) -> set[tuple[str, str]]:
    equipment_tags = {
        entity.normalized_value
        for entity in chunk_entities
        if entity.entity_type == "equipment"
    }
    if len(equipment_tags) < 2:
        return set()
    sorted_tags = sorted(equipment_tags)
    return set(combinations(sorted_tags, 2))


def _extract_equipment_regulation_pairs(chunk_entities: list[ExtractedEntity]) -> set[tuple[str, str]]:
    equipment_tags = {
        entity.normalized_value
        for entity in chunk_entities
        if entity.entity_type == "equipment"
    }
    regulation_codes = {
        entity.normalized_value
        for entity in chunk_entities
        if entity.entity_type == "regulation"
    }
    if not equipment_tags or not regulation_codes:
        return set()
    return {(eq, reg) for eq in equipment_tags for reg in regulation_codes}


# Public entrypoint. Co-occurrence within a chunk implies a candidate relationship — intentionally noisier than an LLM-refined pass, per Part 4 of the build guide. No relationship is written to Postgres here; this stage only produces candidates for a later DB-writing task.
def extract_relationships_cooccurrence(entities: list[ExtractedEntity]) -> tuple[list[CandidateEquipmentConnection], list[CandidateRegulationLink]]:
    by_chunk = _group_by_chunk(entities)

    equipment_pairs: dict[tuple[str, str], list[int]] = defaultdict(list)
    regulation_pairs: dict[tuple[str, str], list[int]] = defaultdict(list)

    for chunk_index in sorted(by_chunk.keys()):
        chunk_entities = by_chunk[chunk_index]
        for tag_a, tag_b in _extract_equipment_pairs(chunk_entities):
            equipment_pairs[(tag_a, tag_b)].append(chunk_index)
        for eq_tag, reg_code in _extract_equipment_regulation_pairs(chunk_entities):
            regulation_pairs[(eq_tag, reg_code)].append(chunk_index)

    equipment_connections = [
        CandidateEquipmentConnection(
            equipment_tag_a=a,
            equipment_tag_b=b,
            chunk_indices=indices,
        )
        for (a, b), indices in equipment_pairs.items()
    ]

    regulation_links = [
        CandidateRegulationLink(
            equipment_tag=eq,
            regulation_code=reg,
            chunk_indices=indices,
        )
        for (eq, reg), indices in regulation_pairs.items()
    ]

    return equipment_connections, regulation_links
