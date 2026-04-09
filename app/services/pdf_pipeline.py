"""Run extract → clean → chunk → embeddings and persist to Postgres."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pdf_document import EMBEDDING_DIMENSIONS, DocumentChunk, PdfDocument
from app.services.embeddings import embed_texts
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
    Create a PdfDocument row, extract/clean/chunk, save chunks, optionally embed.
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
    chunk_objs: list[DocumentChunk] = []
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
            row = DocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=strip_null_bytes(content),
                start_char=start,
                end_char=end,
                page_number=None,
            )
            db.add(row)
            chunk_objs.append(row)

        doc.processing_error = None

        if settings.openai_api_key and chunk_objs:
            try:
                texts = [c.content for c in chunk_objs]
                batch_size = max(1, settings.openai_embedding_batch_size)
                all_vecs: list[list[float]] = []
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    all_vecs.extend(embed_texts(batch))
                for c, vec in zip(chunk_objs, all_vecs):
                    if len(vec) != EMBEDDING_DIMENSIONS:
                        raise ValueError(
                            f'Expected embedding dim {EMBEDDING_DIMENSIONS}, got {len(vec)}'
                        )
                    c.embedding = vec
            except Exception as embed_exc:
                doc.processing_error = f'Embedding failed: {embed_exc}'
        elif chunk_objs and not settings.openai_api_key:
            doc.processing_error = 'Embeddings skipped: OPENAI_API_KEY not set'

    except Exception as exc:
        doc.processing_error = str(exc)
        doc.extracted_text = None
        doc.cleaned_text = None
        chunk_count = 0

    db.commit()
    db.refresh(doc)
    return doc, chunk_count
