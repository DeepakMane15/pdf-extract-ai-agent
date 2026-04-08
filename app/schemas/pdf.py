from pydantic import BaseModel, Field


class PdfUploadResponse(BaseModel):
    document_id: int = Field(description='Primary key of the stored PDF record')
    original_filename: str | None = Field(description='Name provided by the client')
    stored_filename: str = Field(description='Filename on disk under the upload directory')
    content_type: str | None = None
    size_bytes: int
    extracted_char_count: int | None = Field(default=None, description='Length of raw extracted text')
    cleaned_char_count: int | None = Field(default=None, description='Length of cleaned text used for chunking')
    chunk_count: int = Field(description='Number of stored text chunks')
    processing_error: str | None = Field(default=None, description='Set if extraction/chunking failed')
