from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description='Natural-language query')
    top_k: int = Field(5, ge=1, le=50, description='Number of chunks to return')


class SearchHit(BaseModel):
    chunk_id: int
    document_id: int
    chunk_text: str
    page_number: int | None = None
    cosine_distance: float = Field(
        description='pgvector cosine distance (<=>); lower is more similar'
    )


class SearchResponse(BaseModel):
    results: list[SearchHit]
