"""Chunking stage. Section-aware, fixed-size with overlap. Populated in a later task."""

from collections import Counter
from dataclasses import dataclass
from itertools import groupby

from app.pipeline.parsing import ParsedPage

TARGET_TOKENS = 512
OVERLAP_RATIO = 0.15
HEADING_SIZE_RATIO = 1.15
HEADING_MAX_WORDS = 12


@dataclass
class ChunkData:
    chunk_index: int
    content: str
    page_number: int
    bbox: list[float] | None
    section_title: str | None


def _flatten_to_tokens(pages: list[ParsedPage]) -> list[dict]:
    tokens = []
    for page in pages:
        for line in page.lines:
            words = line.text.split()
            for i, word in enumerate(words):
                if word:
                    tokens.append(
                        {
                            "word": word,
                            "page_number": page.page_number,
                            "page_bbox": page.page_bbox,
                            "line_font_size": line.font_size,
                            "is_line_start": i == 0,
                            "line_text": line.text,
                        }
                    )
    return tokens


def _compute_body_font_size(pages: list[ParsedPage]) -> float | None:
    sizes = []
    for page in pages:
        for line in page.lines:
            if line.font_size is not None:
                sizes.append(round(line.font_size))
    if not sizes:
        return None
    return float(Counter(sizes).most_common(1)[0][0])


def _assign_sections(pages: list[ParsedPage], body_font_size: float | None) -> list[dict]:
    tokens = _flatten_to_tokens(pages)
    if body_font_size is None:
        for token in tokens:
            token["section_title"] = None
        return tokens

    current_section_title = None
    for token in tokens:
        if token["is_line_start"]:
            if (
                token["line_font_size"] is not None
                and token["line_font_size"] >= body_font_size * HEADING_SIZE_RATIO
                and len(token["line_text"].split()) <= HEADING_MAX_WORDS
            ):
                current_section_title = token["line_text"].strip()
        token["section_title"] = current_section_title
    return tokens


def _window_tokens(tokens: list[dict], start_index: int) -> tuple[list[ChunkData], int]:
    if not tokens:
        return [], start_index
    step = TARGET_TOKENS - round(TARGET_TOKENS * OVERLAP_RATIO)
    chunks = []
    i = 0
    while True:
        window = tokens[i : i + TARGET_TOKENS]
        if not window:
            break
        chunks.append(
            ChunkData(
                chunk_index=start_index,
                content=" ".join(t["word"] for t in window),
                page_number=window[0]["page_number"],
                bbox=window[0]["page_bbox"],
                section_title=window[0]["section_title"],
            )
        )
        start_index += 1
        if i + TARGET_TOKENS >= len(tokens):
            break
        i += step
    return chunks, start_index


# MVP simplification: bbox is the full page rectangle of the chunk's starting page, not a precise per-chunk bounding box. Word-count is used as a token-count approximation, not a real tokenizer.
def chunk_document(pages: list[ParsedPage]) -> list[ChunkData]:
    body_font_size = _compute_body_font_size(pages)
    tokens = _assign_sections(pages, body_font_size)
    if not tokens:
        return []

    chunks = []
    next_index = 0
    for _, group in groupby(tokens, key=lambda t: t["section_title"]):
        group_tokens = list(group)
        section_chunks, next_index = _window_tokens(group_tokens, next_index)
        chunks.extend(section_chunks)

    return chunks
