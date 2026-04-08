"""Extract raw text from PDF files using pdfplumber."""

from pathlib import Path

import pdfplumber

from app.services.text_chunking import strip_null_bytes


def extract_text_from_pdf(path: Path) -> str:
    """Concatenate text from all pages; empty string if no extractable text."""
    parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                parts.append(strip_null_bytes(text))
    return strip_null_bytes('\n\n'.join(parts))
