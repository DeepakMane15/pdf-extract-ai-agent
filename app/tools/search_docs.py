"""Search ingested document chunks via embeddings + optional rerank."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.user import UserRole
from app.tools.base import BaseTool
from app.tools.context import ToolContext
from app.services.embeddings import embed_query
from app.services.retrieval import retrieve_chunks_ranked


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
        if not settings.openai_api_key:
            raise RuntimeError('Semantic search requires OPENAI_API_KEY.')
        data = inputs if isinstance(inputs, SearchDocsInput) else SearchDocsInput.model_validate(inputs)
        vec = embed_query(data.query)
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
