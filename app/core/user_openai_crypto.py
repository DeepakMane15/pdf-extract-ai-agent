"""Encrypt/decrypt per-user OpenAI API keys at rest (Fernet).

One-way password hashing cannot be used here: the server must recover the key to call OpenAI.
"""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def _fernet() -> Fernet:
    seed = (settings.openai_user_key_secret or settings.jwt_secret_key).encode('utf-8')
    key = base64.urlsafe_b64encode(hashlib.sha256(seed).digest())
    return Fernet(key)


def encrypt_user_openai_key(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.strip().encode('utf-8')).decode('ascii')


def decrypt_user_openai_key(ciphertext: str) -> str:
    return _fernet().decrypt(ciphertext.encode('ascii')).decode('utf-8')


def try_decrypt_user_openai_key(ciphertext: str | None) -> str | None:
    if not ciphertext:
        return None
    try:
        return decrypt_user_openai_key(ciphertext)
    except (InvalidToken, ValueError, UnicodeError):
        return None


def mask_openai_key(plaintext: str) -> str:
    s = plaintext.strip()
    if len(s) <= 8:
        return '••••••••'
    return f'{s[:4]}…{s[-4:]}'
