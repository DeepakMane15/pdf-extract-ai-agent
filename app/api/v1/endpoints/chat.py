from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatAskRequest, ChatAskResponse
from app.services.rag_chat import ask_with_rag
from app.services.user_openai import get_effective_openai_key

router = APIRouter()


@router.post('/ask', response_model=ChatAskResponse)
def chat_ask(
    payload: ChatAskRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatAskResponse:
    """
    RAG: embed the question, retrieve similar chunks, call the LLM, return an answer and source metadata.
    """
    if not get_effective_openai_key(user):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Chat requires an OpenAI API key (save yours under your profile or set OPENAI_API_KEY).',
        )

    try:
        return ask_with_rag(db, payload.question.strip(), top_k=payload.top_k, user=user)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'RAG pipeline failed: {exc}',
        ) from exc
