from pydantic import BaseModel, Field


class ChatAskRequest(BaseModel):
    question: str = Field(..., min_length=1, description='User question')
    top_k: int = Field(5, ge=1, le=20, description='Chunks to retrieve for context')


class SourceCitation(BaseModel):
    chunk_id: int
    document_id: int
    page_number: int | None = None
    cosine_distance: float = Field(description='Lower is closer to the query embedding')
    excerpt: str = Field(description='Short preview of chunk text')


class ChatAskResponse(BaseModel):
    answer: str
    sources: list[SourceCitation] = Field(
        description='Chunks passed to the model as context (retrieval set)'
    )
    cited_chunk_ids: list[int] = Field(
        default_factory=list,
        description='chunk_id values parsed from [chunk_id:N] markers in the answer, if any',
    )
