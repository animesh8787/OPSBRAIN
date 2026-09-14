"""Scanned-forms structured extraction.

Operates on already-OCR'd page text. Detects form-style "Label: value" pages
and restructures them into a clean markdown-style block.
"""

import re

_FORM_FIELD_PATTERN = re.compile(r"^[A-Za-z0-9 /_-]{2,40}:\s*.+$")


def is_structured_form(page_text: str) -> bool:
    """Heuristic: True if the page contains at least 3 'Label: value' lines."""
    matches = sum(1 for line in page_text.splitlines() if _FORM_FIELD_PATTERN.match(line))
    return matches >= 3


def extract_form_fields(page_text: str) -> dict[str, str]:
    """Extract {label: value} pairs from lines matching the form-field pattern."""
    fields: dict[str, str] = {}
    for line in page_text.splitlines():
        match = _FORM_FIELD_PATTERN.match(line)
        if not match:
            continue
        # Split on the FIRST colon only
        label, _, value = line.partition(":")
        label = label.strip()
        value = value.strip()
        if label:
            fields[label] = value
    return fields


def structure_form_page(page_text: str, page_number: int) -> str:
    """Render form fields as a markdown-style block. Falls back to raw text
    if no fields are detected.
    """
    fields = extract_form_fields(page_text)
    if not fields:
        return page_text
    lines = [f"Form fields (page {page_number}):"]
    for k, v in fields.items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)
