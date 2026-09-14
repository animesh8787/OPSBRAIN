"""Spreadsheet ingestion for .xlsx / .csv files.

Turns tabular data into a list of ParsedPage objects so that the existing
chunk_document pipeline can process spreadsheets without modification.
"""

import csv
import logging
from pathlib import Path

import openpyxl

from app.pipeline.parsing import ParsedLine, ParsedPage

logger = logging.getLogger(__name__)

WINDOW_SIZE = 50


def needs_spreadsheet_parsing(file_path: str) -> bool:
    ext = Path(file_path).suffix.lower()
    return ext in {".xlsx", ".xls", ".csv"}


def _render_window_lines(headers: list[str], rows: list[list[str]]) -> list[ParsedLine]:
    """Build ParsedLine objects for one window: header line + one line per row."""
    lines: list[ParsedLine] = []
    if headers:
        lines.append(ParsedLine(text=" | ".join(headers), font_size=None))
    for row in rows:
        # Pair each header with its value; if row is shorter than headers, pad with empty string
        pairs = []
        for i, h in enumerate(headers):
            v = row[i] if i < len(row) else ""
            pairs.append(f"{h}: {v}")
        lines.append(ParsedLine(text=" | ".join(pairs), font_size=None))
    return lines


def _parse_xlsx(file_path: str) -> list[ParsedPage]:
    workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    try:
        pages: list[ParsedPage] = []
        page_counter = 1
        for sheet in workbook:
            # Read all rows into a list of lists (skip completely empty rows)
            all_rows: list[list[str]] = []
            for row in sheet.iter_rows(values_only=True):
                if row is None:
                    continue
                str_row = [str(cell) if cell is not None else "" for cell in row]
                if not any(str_row):
                    continue
                all_rows.append(str_row)

            if not all_rows:
                continue  # skip sheets with zero data rows

            headers = all_rows[0]
            data_rows = all_rows[1:]

            # Build 50-row windows
            for start in range(0, len(data_rows), WINDOW_SIZE):
                window = data_rows[start : start + WINDOW_SIZE]
                end = start + len(window)
                lines = _render_window_lines(headers, window)
                full_text = "\n".join(line.text for line in lines)
                pages.append(
                    ParsedPage(
                        page_number=page_counter,
                        text=full_text,
                        font_sizes=[],
                        lines=lines,
                        page_bbox=[0, 0, 0, 0],
                    )
                )
                page_counter += 1
        return pages
    finally:
        workbook.close()


def _parse_csv(file_path: str) -> list[ParsedPage]:
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        all_rows: list[list[str]] = []
        for row in reader:
            if not any(cell.strip() for cell in row):
                continue
            all_rows.append(row)

    if not all_rows:
        return []

    headers = all_rows[0]
    data_rows = all_rows[1:]
    pages: list[ParsedPage] = []
    page_counter = 1
    for start in range(0, len(data_rows), WINDOW_SIZE):
        window = data_rows[start : start + WINDOW_SIZE]
        end = start + len(window)
        lines = _render_window_lines(headers, window)
        full_text = "\n".join(line.text for line in lines)
        pages.append(
            ParsedPage(
                page_number=page_counter,
                text=full_text,
                font_sizes=[],
                lines=lines,
                page_bbox=[0, 0, 0, 0],
            )
        )
        page_counter += 1
    return pages


def parse_spreadsheet(file_path: str) -> list[ParsedPage]:
    ext = Path(file_path).suffix.lower()
    try:
        if ext in {".xlsx", ".xls"}:
            return _parse_xlsx(file_path)
        if ext == ".csv":
            return _parse_csv(file_path)
        raise ValueError(f"Unsupported spreadsheet extension: {ext}")
    except Exception:
        logger.exception(f"Failed to parse spreadsheet: {file_path}")
        raise
