"""OCR stage. Tesseract-based OCR for scanned PDFs only. Populated in a later task."""

import asyncio
import io
import logging

import fitz
import pytesseract
from PIL import Image

from app.pipeline.parsing import ParsedLine, ParsedPage

logger = logging.getLogger(__name__)


def _run_ocr_sync(pdf_path: str) -> list[ParsedPage]:
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        try:
            page_bbox = list(page.rect)
        except Exception:
            page_bbox = [0.0, 0.0, 0.0, 0.0]
        try:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
            lines = [
                ParsedLine(text=line.strip(), font_size=None)
                for line in text.splitlines()
                if line.strip()
            ]
        except Exception:
            # One page failing OCR should not fail the whole document — degrade gracefully per page.
            logger.exception(f"OCR failed for page {page_num} of {pdf_path}")
            text = ""
            lines = []
        pages.append(
            ParsedPage(
                page_number=page_num,
                text=text,
                font_sizes=[],
                lines=lines,
                page_bbox=page_bbox,
            )
        )
    doc.close()
    return pages


async def run_ocr(pdf_path: str) -> list[ParsedPage]:
    return await asyncio.to_thread(_run_ocr_sync, pdf_path)
