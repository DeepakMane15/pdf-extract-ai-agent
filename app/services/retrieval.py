"""Vector similarity search over document_chunks (cosine distance via pgvector)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pdf_document import DocumentChunk
from app.services.reranking import cohere_rerank


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


def retrieve_chunks_ranked(
    db: Session,
    query_text: str,
    query_embedding: list[float],
    *,
    final_k: int,
) -> list[tuple[DocumentChunk, float, float | None]]:
    """
    Stage 1: pgvector top-N pool (default pool size 20, or max(pool, final_k)).
    Stage 2: Cohere rerank to final_k when COHERE_API_KEY is set; else vector order.

    Returns (chunk, vector_cosine_distance, rerank_relevance_score or None).
    """
    if final_k < 1:
        return []

    pool = max(settings.retrieval_vector_pool_size, final_k)
    rows = search_chunks_by_embedding(db, query_embedding, top_k=pool)
    if not rows:
        return []

    chunks = [chunk for chunk, _dist in rows]
    dist_map = {chunk.id: dist for chunk, dist in rows}

    if not settings.cohere_api_key:
        return [(c, dist_map[c.id], None) for c in chunks[:final_k]]

    docs = [c.content for c in chunks]
    ranked = cohere_rerank(query_text, docs, top_n=min(final_k, len(chunks)))
    out: list[tuple[DocumentChunk, float, float | None]] = []
    for idx, score in ranked:
        c = chunks[idx]
        out.append((c, dist_map[c.id], score))
    return out
