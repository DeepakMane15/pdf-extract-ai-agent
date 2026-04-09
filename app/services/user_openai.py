"""Per-user OpenAI key resolution and usage counters."""

from __future__ import annotations

from app.core.config import settings
from app.core.user_openai_crypto import encrypt_user_openai_key, mask_openai_key, try_decrypt_user_openai_key
from app.models.user import User


def get_effective_openai_key(user: User) -> str | None:
    """User-specific decrypted key, else server OPENAI_API_KEY."""
    u = try_decrypt_user_openai_key(user.openai_api_key_encrypted)
    if u:
        return u
    k = settings.openai_api_key
    return k.strip() if k else None


def set_user_openai_key(user: User, plaintext_key: str) -> None:
    user.openai_api_key_encrypted = encrypt_user_openai_key(plaintext_key)
    user.openai_key_hint = mask_openai_key(plaintext_key)


def clear_user_openai_key(user: User) -> None:
    user.openai_api_key_encrypted = None
    user.openai_key_hint = None


def add_openai_usage(
    user: User,
    *,
    embed_prompt_tokens: int = 0,
    chat_prompt_tokens: int = 0,
    chat_completion_tokens: int = 0,
) -> None:
    if embed_prompt_tokens:
        user.openai_embed_prompt_tokens_total = int(user.openai_embed_prompt_tokens_total) + embed_prompt_tokens
    if chat_prompt_tokens:
        user.openai_chat_prompt_tokens_total = int(user.openai_chat_prompt_tokens_total) + chat_prompt_tokens
    if chat_completion_tokens:
        user.openai_chat_completion_tokens_total = int(user.openai_chat_completion_tokens_total) + chat_completion_tokens


