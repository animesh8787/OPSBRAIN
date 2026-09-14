"""Email archive ingestion for .eml files.

Extracts headers, plain-text body, and attachment metadata from email messages.
"""

import email
import email.policy
import logging
from html.parser import HTMLParser
from pathlib import Path

from app.pipeline.parsing import ParsedLine, ParsedPage

logger = logging.getLogger(__name__)


class _HTMLStripper(HTMLParser):
    """Minimal HTML tag stripper using only the standard library."""

    def __init__(self) -> None:
        super().__init__()
        self.text_parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)

    def get_text(self) -> str:
        return " ".join("".join(self.text_parts).split())


def _strip_html(html: str) -> str:
    stripper = _HTMLStripper()
    try:
        stripper.feed(html)
    except Exception:
        # If HTML is malformed, return it as-is after basic whitespace cleanup
        return " ".join(html.split())
    return stripper.get_text()


def needs_email_parsing(file_path: str) -> bool:
    return Path(file_path).suffix.lower() == ".eml"


def parse_email(file_path: str) -> list[ParsedPage]:
    ext = Path(file_path).suffix.lower()
    if ext == ".msg":
        raise NotImplementedError("MSG format not yet supported, convert to EML first.")
    if ext != ".eml":
        raise ValueError(f"Unsupported email extension: {ext}")

    with open(file_path, "rb") as f:
        data = f.read()

    msg = email.message_from_bytes(data, policy=email.policy.default)

    subject = msg.get("Subject", "No Subject")
    from_addr = msg.get("From", "")
    to_addr = msg.get("To", "")
    date = msg.get("Date", "")

    # Extract body and attachment metadata
    body_text = ""
    attachments: list[str] = []
    html_body: str | None = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = part.get_content_disposition()
            filename = part.get_filename()

            if disposition == "attachment" or filename:
                size = len(part.get_payload(decode=True) or b"")
                attachments.append(f"[Attachment: {filename or 'unnamed'}, {content_type}, {size} bytes]")
            elif content_type == "text/plain" and not body_text:
                body_text = part.get_content()
            elif content_type == "text/html" and html_body is None:
                html_body = part.get_content()
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            body_text = msg.get_content()
        elif content_type == "text/html":
            html_body = msg.get_content()

    # Fallback: if no plain text but HTML exists, strip tags
    if not body_text and html_body is not None:
        body_text = _strip_html(html_body)

    lines = [
        f"From: {from_addr}",
        f"To: {to_addr}",
        f"Date: {date}",
        "",
        body_text,
    ]
    if attachments:
        lines.append("")
        lines.extend(attachments)

    full_text = "\n".join(lines)
    parsed_lines = [ParsedLine(text=line, font_size=None) for line in lines if line or line == ""]

    return [
        ParsedPage(
            page_number=1,
            text=full_text,
            font_sizes=[],
            lines=parsed_lines,
            page_bbox=[0, 0, 0, 0],
        )
    ]
