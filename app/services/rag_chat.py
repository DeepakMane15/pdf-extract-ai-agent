"""RAG: retrieve chunks, build prompt, call chat LLM."""

from __future__ import annotations

import re
import time
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.chat import ChatAskResponse, SourceCitation
from app.services.embeddings import embed_query
from app.services.retrieval import retrieve_chunks_ranked
from app.services.user_openai import add_openai_usage, get_effective_openai_key

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


def _call_chat_completions(
    messages: list[dict[str, str]],
    *,
    api_key: str,
) -> tuple[str, dict[str, int]]:
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
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json=payload,
            )
            if r.status_code == 429 and attempt < max_retries - 1:
                _sleep_after_429(attempt, r)
                continue
            r.raise_for_status()
            data = r.json()
            content = data['choices'][0]['message']['content'].strip()
            u: dict[str, Any] = data.get('usage') or {}
            usage = {
                'prompt_tokens': int(u.get('prompt_tokens', 0)),
                'completion_tokens': int(u.get('completion_tokens', 0)),
            }
            return content, usage

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


def ask_with_rag(db: Session, question: str, top_k: int, user: User) -> ChatAskResponse:
    key = get_effective_openai_key(user)
    if not key:
        return ChatAskResponse(
            answer=(
                'No OpenAI API key is available. Add your key in the dashboard or set OPENAI_API_KEY on the server.'
            ),
            sources=[],
            cited_chunk_ids=[],
        )

    query_vec, emb_usage = embed_query(question, api_key=key)
    add_openai_usage(
        user,
        embed_prompt_tokens=int(emb_usage.get('prompt_tokens', emb_usage.get('total_tokens', 0))),
    )
    db.commit()

    rows = retrieve_chunks_ranked(db, question.strip(), query_vec, final_k=top_k)

    if not rows:
        return ChatAskResponse(
            answer=(
                'No embedded text chunks were found. Upload PDFs with embeddings enabled '
                'or try a lower top_k after ingesting documents.'
            ),
            sources=[],
            cited_chunk_ids=[],
        )

    context_blocks: list[str] = []
    sources: list[SourceCitation] = []

    for chunk, distance, rerank in rows:
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
                rerank_score=rerank,
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

    answer, chat_usage = _call_chat_completions(messages, api_key=key)
    add_openai_usage(
        user,
        chat_prompt_tokens=chat_usage.get('prompt_tokens', 0),
        chat_completion_tokens=chat_usage.get('completion_tokens', 0),
    )
    db.commit()

    cited = _parse_cited_chunk_ids(answer)

    return ChatAskResponse(answer=answer, sources=sources, cited_chunk_ids=cited)
