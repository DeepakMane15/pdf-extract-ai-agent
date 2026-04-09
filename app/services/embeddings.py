"""OpenAI embedding API (batch) with retries on rate limits."""

from __future__ import annotations

import time

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


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Return one embedding vector per input string, in order.
    Retries on HTTP 429 (rate limit) with exponential backoff and Retry-After.
    """
    if not texts:
        return []
    key =  settings.openai_api_key
    if not key:
        raise RuntimeError('OPENAI_API_KEY is not set')

    payload = {'model': settings.openai_embedding_model, 'input': texts}
    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    max_retries = max(1, settings.openai_embedding_max_retries)

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
            break

    data = body['data']
    data.sort(key=lambda x: x['index'])
    return [row['embedding'] for row in data]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
