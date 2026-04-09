"""Search ingested document chunks via embeddings + optional rerank."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from app.models.user import UserRole
from app.tools.base import BaseTool
from app.tools.context import ToolContext
from app.services.embeddings import embed_query
from app.services.retrieval import retrieve_chunks_ranked
from app.services.user_openai import add_openai_usage, get_effective_openai_key


class SearchDocsInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(5, ge=1, le=20)


class SearchDocsTool(BaseTool):
    name: ClassVar[str] = 'search_docs'
    description: ClassVar[str] = 'Retrieve top relevant document chunks for a query (RAG retrieval).'
    allowed_roles: ClassVar[frozenset[UserRole]] = frozenset(
        {UserRole.admin, UserRole.user, UserRole.auditor}
    )

    @classmethod
    def input_model(cls) -> type[BaseModel]:
        return SearchDocsInput

    def execute(self, ctx: ToolContext, inputs: BaseModel) -> Any:
        key = get_effective_openai_key(ctx.user)
        if not key:
            raise RuntimeError(
                'No OpenAI API key: add yours in the dashboard or set OPENAI_API_KEY on the server.'
            )
        data = inputs if isinstance(inputs, SearchDocsInput) else SearchDocsInput.model_validate(inputs)
        vec, usage = embed_query(data.query, api_key=key)
        add_openai_usage(
            ctx.user,
            embed_prompt_tokens=int(usage.get('prompt_tokens', usage.get('total_tokens', 0))),
        )
        rows = retrieve_chunks_ranked(ctx.db, data.query, vec, final_k=data.top_k)
        return {
            'hits': [
                {
                    'chunk_id': c.id,
                    'document_id': c.document_id,
                    'page_number': c.page_number,
                    'cosine_distance': dist,
                    'rerank_score': rer,
                    'excerpt': c.content[:300] + ('…' if len(c.content) > 300 else ''),
                }
                for c, dist, rer in rows
            ]
        }
