from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserMeRead, UserOpenAIKeyUpdate, UserRead
from app.services.user_openai import clear_user_openai_key, set_user_openai_key

router = APIRouter()


@router.post('', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _user_me_read(user: User) -> UserMeRead:
    sk = (settings.openai_api_key or '').strip()
    emb = int(user.openai_embed_prompt_tokens_total)
    cp = int(user.openai_chat_prompt_tokens_total)
    cc = int(user.openai_chat_completion_tokens_total)
    return UserMeRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        openai_key_configured=bool(user.openai_api_key_encrypted),
        openai_key_hint=user.openai_key_hint,
        server_openai_configured=bool(sk),
        openai_embed_prompt_tokens_total=emb,
        openai_chat_prompt_tokens_total=cp,
        openai_chat_completion_tokens_total=cc,
        openai_tokens_grand_total=emb + cp + cc,
    )


@router.get('/me', response_model=UserMeRead)
def read_me(current_user: User = Depends(get_current_user)) -> UserMeRead:
    return _user_me_read(current_user)


@router.put('/me/openai-key', status_code=status.HTTP_204_NO_CONTENT)
def set_my_openai_key(
    payload: UserOpenAIKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    set_user_openai_key(current_user, payload.api_key)
    db.add(current_user)
    db.commit()


@router.delete('/me/openai-key', status_code=status.HTTP_204_NO_CONTENT)
def delete_my_openai_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    clear_user_openai_key(current_user)
    db.add(current_user)
    db.commit()


@router.get('', response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.auditor)),
) -> list[User]:
    return db.query(User).order_by(User.id).all()
