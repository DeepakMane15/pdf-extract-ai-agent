from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.search import SearchHit, SearchRequest, SearchResponse
from app.services.embeddings import embed_query
from app.services.retrieval import retrieve_chunks_ranked

router = APIRouter()


@router.post('/search', response_model=SearchResponse)
def semantic_search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SearchResponse:
    """
    Embed the query, take the top vector pool (default 20), optionally rerank with Cohere to top_k.
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Semantic search requires OPENAI_API_KEY.',
        )

    try:
        query_vec = embed_query(payload.query)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'Embedding request failed: {exc}',
        ) from exc

    rows = retrieve_chunks_ranked(db, payload.query.strip(), query_vec, final_k=payload.top_k)
    results = [
        SearchHit(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            chunk_text=chunk.content,
            page_number=chunk.page_number,
            cosine_distance=distance,
            rerank_score=rerank,
        )
        for chunk, distance, rerank in rows
    ]
    return SearchResponse(results=results)
