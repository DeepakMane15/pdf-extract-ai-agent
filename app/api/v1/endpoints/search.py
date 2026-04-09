from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.pdf_document import PdfDocument
from app.models.user import User
from app.schemas.search import SearchHit, SearchRequest, SearchResponse
from app.services.embeddings import embed_query
from app.services.retrieval import retrieve_chunks_ranked
from app.services.user_openai import add_openai_usage, get_effective_openai_key

router = APIRouter()


@router.post('/search', response_model=SearchResponse)
def semantic_search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SearchResponse:
    """
    Embed the query, take the top vector pool (default 20), optionally rerank with Cohere to top_k.
    """
    key = get_effective_openai_key(user)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Semantic search requires an OpenAI API key (save yours under your profile or set OPENAI_API_KEY).',
        )

    try:
        query_vec, usage = embed_query(payload.query, api_key=key)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'Embedding request failed: {exc}',
        ) from exc

    add_openai_usage(
        user,
        embed_prompt_tokens=int(usage.get('prompt_tokens', usage.get('total_tokens', 0))),
    )
    db.commit()

    rows = retrieve_chunks_ranked(db, payload.query.strip(), query_vec, final_k=payload.top_k)
    doc_ids = {chunk.document_id for chunk, _, _ in rows}
    id_to_name: dict[int, str | None] = {}
    if doc_ids:
        for d in db.query(PdfDocument).filter(PdfDocument.id.in_(doc_ids)).all():
            id_to_name[d.id] = d.original_filename

    results = [
        SearchHit(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            document_original_filename=id_to_name.get(chunk.document_id),
            chunk_text=chunk.content,
            page_number=chunk.page_number,
            cosine_distance=distance,
            rerank_score=rerank,
        )
        for chunk, distance, rerank in rows
    ]
    return SearchResponse(results=results)
