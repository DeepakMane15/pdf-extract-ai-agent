from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatAskRequest, ChatAskResponse
from app.services.rag_chat import ask_with_rag

router = APIRouter()


@router.post('/ask', response_model=ChatAskResponse)
def chat_ask(
    payload: ChatAskRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ChatAskResponse:
    """
    RAG: embed the question, retrieve similar chunks, call the LLM, return an answer and source metadata.
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Chat requires OPENAI_API_KEY for embeddings and the chat model.',
        )

    try:
        return ask_with_rag(db, payload.question.strip(), top_k=payload.top_k)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'RAG pipeline failed: {exc}',
        ) from exc
