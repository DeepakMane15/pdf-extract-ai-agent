"""OpenAI embedding API (batch) with retries on rate limits."""

from __future__ import annotations

import time
from typing import Any

import httpx

from app.core.config import settings


def _sleep_after_429(attempt: int, response: httpx.Response) -> None:
    retry_after = response.headers.get('Retry-After')
    if retry_after is not None:
        try:
            time.sleep(float(retry_after))
            return
        except ValueError:
            pass
    time.sleep(min(2**attempt, 60))


def _merge_usage(a: dict[str, int], b: dict[str, Any]) -> dict[str, int]:
    pt = int(a.get('prompt_tokens', 0)) + int(b.get('prompt_tokens', 0))
    tt = int(a.get('total_tokens', 0)) + int(b.get('total_tokens', 0))
    if tt == 0 and pt:
        tt = pt
    return {'prompt_tokens': pt, 'total_tokens': tt}


def embed_texts(
    texts: list[str],
    *,
    api_key: str | None = None,
) -> tuple[list[list[float]], dict[str, int]]:
    """
    Return (vectors, usage) where usage has prompt_tokens and total_tokens from OpenAI (summed per batch).
    """
    if not texts:
        return [], {'prompt_tokens': 0, 'total_tokens': 0}

    key = (api_key or settings.openai_api_key or '').strip()
    if not key:
        raise RuntimeError('OPENAI_API_KEY is not set and no user key provided')

    payload = {'model': settings.openai_embedding_model, 'input': texts}
    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    max_retries = max(1, settings.openai_embedding_max_retries)

    usage_total: dict[str, int] = {'prompt_tokens': 0, 'total_tokens': 0}
    all_vecs: list[list[float]] = []

    with httpx.Client(timeout=120.0) as client:
        for attempt in range(max_retries):
            r = client.post(
                'https://api.openai.com/v1/embeddings',
                headers=headers,
                json=payload,
            )
            if r.status_code == 429 and attempt < max_retries - 1:
                _sleep_after_429(attempt, r)
                continue
            r.raise_for_status()
            body = r.json()
            u = body.get('usage') or {}
            usage_total = _merge_usage(
                usage_total,
                {
                    'prompt_tokens': u.get('prompt_tokens', 0),
                    'total_tokens': u.get('total_tokens', u.get('prompt_tokens', 0)),
                },
            )
            data = body['data']
            data.sort(key=lambda x: x['index'])
            all_vecs = [row['embedding'] for row in data]
            break

    return all_vecs, usage_total


def embed_query(text: str, *, api_key: str | None = None) -> tuple[list[float], dict[str, int]]:
    vecs, usage = embed_texts([text], api_key=api_key)
    return vecs[0], usage
