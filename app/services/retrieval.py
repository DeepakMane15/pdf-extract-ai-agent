"""Vector similarity search over document_chunks (cosine distance via pgvector)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pdf_document import DocumentChunk


def search_chunks_by_embedding(
    db: Session,
    query_embedding: list[float],
    *,
    top_k: int = 5,
) -> list[tuple[DocumentChunk, float]]:
    """
    Return (chunk, cosine_distance) rows ordered by ascending distance (best first).
    """
    if top_k < 1:
        return []

    dist = DocumentChunk.embedding.cosine_distance(query_embedding)
    stmt = (
        select(DocumentChunk, dist.label('distance'))
        .where(DocumentChunk.embedding.isnot(None))
        .order_by(dist)
        .limit(top_k)
    )
    return [(row[0], float(row[1])) for row in db.execute(stmt).all()]
