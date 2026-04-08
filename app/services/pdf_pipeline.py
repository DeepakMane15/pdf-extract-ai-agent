"""Run extract → clean → chunk and persist to Postgres."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pdf_document import PdfChunk, PdfDocument
from app.services.pdf_extraction import extract_text_from_pdf
from app.services.text_chunking import chunk_fixed_overlap, clean_text, strip_null_bytes


def process_pdf_file(
    db: Session,
    *,
    file_path: Path,
    original_filename: str | None,
    stored_filename: str,
    file_size_bytes: int,
) -> tuple[PdfDocument, int]:
    """
    Create a PdfDocument row, extract/clean/chunk, save chunks. Sets processing_error on failure.
    Returns (document, chunk_count).
    """
    doc = PdfDocument(
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size_bytes=file_size_bytes,
    )
    db.add(doc)
    db.flush()

    chunk_count = 0
    try:
        raw = extract_text_from_pdf(file_path)
        cleaned = clean_text(raw)
        doc.extracted_text = raw
        doc.cleaned_text = cleaned

        segments = chunk_fixed_overlap(
            cleaned,
            settings.chunk_size_chars,
            settings.chunk_overlap_chars,
        )
        chunk_count = len(segments)
        for idx, (content, start, end) in enumerate(segments):
            db.add(
                PdfChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    content=strip_null_bytes(content),
                    start_char=start,
                    end_char=end,
                )
            )
        doc.processing_error = None
    except Exception as exc:
        doc.processing_error = str(exc)
        doc.extracted_text = None
        doc.cleaned_text = None
        chunk_count = 0

    db.commit()
    db.refresh(doc)
    return doc, chunk_count
