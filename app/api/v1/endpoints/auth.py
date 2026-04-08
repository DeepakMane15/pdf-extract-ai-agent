from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.token import Token
from app.services.auth_service import authenticate_user, issue_token_for_user

router = APIRouter()


@router.post('/login', response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """OAuth2-compatible login: use `username` for email (Swagger Authorize uses this form)."""
    user = authenticate_user(db=db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    return Token(access_token=issue_token_for_user(user))
