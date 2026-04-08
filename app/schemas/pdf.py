from pydantic import BaseModel, Field


class PdfUploadResponse(BaseModel):
    original_filename: str | None = Field(description='Name provided by the client')
    stored_filename: str = Field(description='Filename on disk under the upload directory')
    content_type: str | None = None
    size_bytes: int
