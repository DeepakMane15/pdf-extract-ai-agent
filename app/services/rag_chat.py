"""RAG: retrieve chunks, build prompt, call chat LLM."""

from __future__ import annotations

import re
import time

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.chat import ChatAskResponse, SourceCitation
from app.services.embeddings import embed_query
from app.services.retrieval import search_chunks_by_embedding

_EXCERPT_LEN = 200

_SYSTEM_PROMPT = """You are a careful assistant for question answering over retrieved document excerpts.
Rules:
- Use ONLY the information in the provided context. If the context does not contain the answer, say clearly that you cannot find it in the documents.
- Do not invent facts.
- When you state a fact that comes from a specific excerpt, add an inline citation immediately after using exactly this form: [chunk_id:N] where N is the integer chunk_id shown in that excerpt's SOURCE header.
- You may cite multiple chunk_ids if you combine information."""


def _sleep_after_429(attempt: int, response: httpx.Response) -> None:
    ra = response.headers.get('Retry-After')
    if ra is not None:
        try:
            time.sleep(float(ra))
            return
        except ValueError:
            pass
    time.sleep(min(2**attempt, 60))


def _call_chat_completions(messages: list[dict[str, str]]) -> str:
    key = settings.openai_api_key
    if not key:
        raise RuntimeError('OPENAI_API_KEY is not set')

    payload = {
        'model': settings.openai_chat_model,
        'messages': messages,
        'temperature': settings.openai_chat_temperature,
        'max_tokens': settings.openai_chat_max_tokens,
    }
    max_retries = max(1, settings.openai_embedding_max_retries)

    with httpx.Client(timeout=120.0) as client:
        for attempt in range(max_retries):
            r = client.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
                json=payload,
            )
            if r.status_code == 429 and attempt < max_retries - 1:
                _sleep_after_429(attempt, r)
                continue
            r.raise_for_status()
            data = r.json()
            return data['choices'][0]['message']['content'].strip()

    raise RuntimeError('Chat completion failed')


def _parse_cited_chunk_ids(answer: str) -> list[int]:
    ids = [int(m) for m in re.findall(r'\[chunk_id:\s*(\d+)\]', answer, flags=re.IGNORECASE)]
    seen: set[int] = set()
    out: list[int] = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def ask_with_rag(db: Session, question: str, top_k: int) -> ChatAskResponse:
    query_vec = embed_query(question)
    rows = search_chunks_by_embedding(db, query_vec, top_k=top_k)

    if not rows:
        return ChatAskResponse(
            answer=(
                'No embedded text chunks were found. Upload PDFs with embeddings enabled '
                '(OPENAI_API_KEY) or try a lower top_k after ingesting documents.'
            ),
            sources=[],
            cited_chunk_ids=[],
        )

    context_blocks: list[str] = []
    sources: list[SourceCitation] = []

    for chunk, distance in rows:
        page = chunk.page_number
        page_label = str(page) if page is not None else 'unknown'
        context_blocks.append(
            f'[SOURCE chunk_id={chunk.id} document_id={chunk.document_id} page={page_label}]\n'
            f'{chunk.content}'
        )
        excerpt = chunk.content[:_EXCERPT_LEN] + ('…' if len(chunk.content) > _EXCERPT_LEN else '')
        sources.append(
            SourceCitation(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                page_number=chunk.page_number,
                cosine_distance=distance,
                excerpt=excerpt,
            )
        )

    context = '\n\n---\n\n'.join(context_blocks)
    user_content = (
        f'Context:\n\n{context}\n\n---\n\nQuestion: {question}\n\n'
        'Answer using only the context above. Add [chunk_id:N] citations as instructed.'
    )

    messages = [
        {'role': 'system', 'content': _SYSTEM_PROMPT},
        {'role': 'user', 'content': user_content},
    ]

    answer = _call_chat_completions(messages)
    cited = _parse_cited_chunk_ids(answer)

    return ChatAskResponse(answer=answer, sources=sources, cited_chunk_ids=cited)
