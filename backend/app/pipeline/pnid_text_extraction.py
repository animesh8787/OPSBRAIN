"""This module extracts text-layer equipment tags from P&ID PDFs where tags are
real embedded text. It does NOT perform visual symbol recognition,
line/connectivity tracing, or diagram understanding — that requires a
vision-language model and is out of scope here.
"""

import fitz

from app.pipeline.entity_extraction import EQUIPMENT_TAG_PATTERN


def extract_pnid_tags(file_path: str) -> dict[int, list[str]]:
    """Open a PDF and extract equipment tags from the text layer of each page.

    Returns a dict mapping 1-based page number to a list of unique tag strings
    found on that page (preserving first-seen order).
    """
    doc = fitz.open(file_path)
    try:
        result: dict[int, list[str]] = {}
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            tags = EQUIPMENT_TAG_PATTERN.findall(text)
            seen = set()
            unique_tags = []
            for tag in tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)
            if unique_tags:
                result[page_num] = unique_tags
        return result
    finally:
        doc.close()


def is_likely_pnid(file_path: str) -> bool:
    """Heuristic: return True if the PDF looks like a P&ID diagram rather than
    a prose document.

    Criteria:
      - More than 40% of pages have at least 5 distinct equipment-tag matches.
      - Fewer than 100 words of normal prose text across the whole document
        (rough proxy for "mostly a diagram with tag callouts, not a text doc").
    """
    doc = fitz.open(file_path)
    try:
        total_pages = doc.page_count
        if total_pages == 0:
            return False

        pages_with_tags = 0
        total_words = 0

        for page in doc:
            text = page.get_text()
            words = text.split()
            total_words += len(words)

            tags = EQUIPMENT_TAG_PATTERN.findall(text)
            distinct_tags = len(set(tags))
            if distinct_tags >= 5:
                pages_with_tags += 1

        tag_ratio = pages_with_tags / total_pages
        return tag_ratio > 0.40 and total_words < 100
    finally:
        doc.close()
