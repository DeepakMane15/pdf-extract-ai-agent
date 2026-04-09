"""Cross-encoder style reranking via Cohere Rerank API."""

from __future__ import annotations

import time

import httpx

from app.core.config import settings


def _sleep_after_429(attempt: int, response: httpx.Response) -> None:
    ra = response.headers.get('Retry-After')
    if ra is not None:
        try:
            time.sleep(float(ra))
            return
        except ValueError:
            pass
    time.sleep(min(2**attempt, 60))


def cohere_rerank(
    query: str,
    documents: list[str],
    top_n: int,
) -> list[tuple[int, float]]:
    """
    Call Cohere /v1/rerank. Returns (original_index, relevance_score) in reranked order.
    """
    key = settings.cohere_api_key
    if not key:
        raise RuntimeError('COHERE_API_KEY is not set')

    if not documents:
        return []

    top_n = min(top_n, len(documents))
    payload = {
        'model': settings.cohere_rerank_model,
        'query': query,
        'documents': documents,
        'top_n': top_n,
    }
    max_retries = max(1, settings.openai_embedding_max_retries)

    with httpx.Client(timeout=60.0) as client:
        for attempt in range(max_retries):
            r = client.post(
                'https://api.cohere.com/v1/rerank',
                headers={
                    'Authorization': f'Bearer {key}',
                    'Content-Type': 'application/json',
                },
                json=payload,
            )
            if r.status_code == 429 and attempt < max_retries - 1:
                _sleep_after_429(attempt, r)
                continue
            r.raise_for_status()
            data = r.json()

    out: list[tuple[int, float]] = []
    for item in data['results']:
        out.append((int(item['index']), float(item['relevance_score'])))
    return out
