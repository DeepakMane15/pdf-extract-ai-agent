"""Run extract → clean → chunk → embeddings and persist to Postgres."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pdf_document import EMBEDDING_DIMENSIONS, DocumentChunk, PdfDocument
from app.models.user import User
from app.services.embeddings import embed_texts
from app.services.user_openai import add_openai_usage, get_effective_openai_key
from app.services.pdf_extraction import extract_text_from_pdf
from app.services.text_chunking import chunk_fixed_overlap, clean_text, strip_null_bytes


def process_pdf_file(
    db: Session,
    *,
    file_path: Path,
    original_filename: str | None,
    stored_filename: str,
    file_size_bytes: int,
    uploader: User | None = None,
) -> tuple[PdfDocument, int]:
    """
    Create a PdfDocument row, extract/clean/chunk, save chunks, optionally embed.
    Returns (document, chunk_count).
    """
    doc = PdfDocument(
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size_bytes=file_size_bytes,
        uploaded_by_user_id=uploader.id if uploader else None,
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

        embed_key = get_effective_openai_key(uploader) if uploader else (settings.openai_api_key or '').strip() or None
        if embed_key and chunk_objs:
            try:
                texts = [c.content for c in chunk_objs]
                batch_size = max(1, settings.openai_embedding_batch_size)
                all_vecs: list[list[float]] = []
                total_embed_prompt = 0
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    batch_vecs, usage = embed_texts(batch, api_key=embed_key)
                    total_embed_prompt += int(usage.get('prompt_tokens', usage.get('total_tokens', 0)))
                    all_vecs.extend(batch_vecs)
                for c, vec in zip(chunk_objs, all_vecs):
                    if len(vec) != EMBEDDING_DIMENSIONS:
                        raise ValueError(
                            f'Expected embedding dim {EMBEDDING_DIMENSIONS}, got {len(vec)}'
                        )
                    c.embedding = vec
                if uploader and total_embed_prompt:
                    add_openai_usage(uploader, embed_prompt_tokens=total_embed_prompt)
            except Exception as embed_exc:
                doc.processing_error = f'Embedding failed: {embed_exc}'
        elif chunk_objs and not embed_key:
            doc.processing_error = 'Embeddings skipped: no OpenAI API key (add yours in the app or set OPENAI_API_KEY)'

    except Exception as exc:
        doc.processing_error = str(exc)
        doc.extracted_text = None
        doc.cleaned_text = None
        chunk_count = 0

    db.commit()
    db.refresh(doc)
    return doc, chunk_count
