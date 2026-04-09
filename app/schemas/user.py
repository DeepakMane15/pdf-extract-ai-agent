from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.user


class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool

    model_config = {'from_attributes': True}


class UserMeRead(UserRead):
    """Current user profile including OpenAI usage (no raw API key is ever returned)."""

    openai_key_configured: bool = Field(description='True if a personal OpenAI key is stored (encrypted).')
    openai_key_hint: str | None = Field(None, description='Masked hint such as sk-p…xYz0')
    server_openai_configured: bool = Field(
        description='True if the server has OPENAI_API_KEY for fallback when no personal key is set.',
    )
    openai_embed_prompt_tokens_total: int
    openai_chat_prompt_tokens_total: int
    openai_chat_completion_tokens_total: int
    openai_tokens_grand_total: int = Field(
        description='Sum of embedding prompt + chat prompt + chat completion tokens recorded for this account.',
    )


class UserOpenAIKeyUpdate(BaseModel):
    api_key: str = Field(..., min_length=10, description='OpenAI API key (stored encrypted at rest, not hashed).')
