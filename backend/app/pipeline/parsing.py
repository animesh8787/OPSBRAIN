"""Parsing stage. PyMuPDF/pdfplumber text extraction. Populated in a later task."""

import asyncio
from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass
class ParsedLine:
    text: str
    font_size: float | None


@dataclass
class ParsedPage:
    page_number: int
    text: str
    font_sizes: list[float]
    lines: list[ParsedLine]
    page_bbox: list[float]


def needs_ocr(pdf_path: str) -> bool:
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    result = len(text.strip()) < 50 * doc.page_count
    doc.close()
    return result


def _extract_native_text_sync(pdf_path: str) -> list[ParsedPage]:
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        page_bbox = list(page.rect)
        font_sizes = []
        lines = []
        try:
            text_dict = page.get_text("dict")
            sizes = set()
            for block in text_dict.get("blocks", []):
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue
                    joined_text = " ".join(span["text"] for span in spans)
                    line_sizes = []
                    for span in spans:
                        size = span.get("size")
                        if size is not None:
                            line_sizes.append(float(size))
                            sizes.add(float(size))
                    max_size = max(line_sizes) if line_sizes else None
                    lines.append(ParsedLine(text=joined_text, font_size=max_size))
            font_sizes = sorted(list(sizes))
        except Exception:
            font_sizes = []
            lines = []
        pages.append(
            ParsedPage(
                page_number=page_num,
                text=text,
                font_sizes=font_sizes,
                lines=lines,
                page_bbox=page_bbox,
            )
        )
    doc.close()
    return pages


async def parse_native_pdf(pdf_path: str) -> list[ParsedPage]:
    return await asyncio.to_thread(_extract_native_text_sync, pdf_path)


# Single entrypoint used by the ingestion orchestrator. Callers should never call parse_native_pdf or run_ocr directly.
async def parse_document(pdf_path: str) -> list[ParsedPage]:
    if needs_ocr(pdf_path):
        from app.pipeline.ocr import run_ocr
        return await run_ocr(pdf_path)
    return await parse_native_pdf(pdf_path)
