from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

EMBEDDING_DIMENSIONS = 1536


class PdfDocument(Base):
    __tablename__ = 'pdf_documents'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uploaded_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    original_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    stored_filename: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    cleaned_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    uploaded_by = relationship('User', back_populates='uploaded_pdfs')

    chunks: Mapped[list['DocumentChunk']] = relationship(
        back_populates='document',
        cascade='all, delete-orphan',
        order_by='DocumentChunk.chunk_index',
    )


class DocumentChunk(Base):
    """Stored text segment from a PDF with optional embedding for semantic search (pgvector)."""

    __tablename__ = 'document_chunks'
    __table_args__ = (UniqueConstraint('document_id', 'chunk_index', name='uq_pdf_chunk_document_index'),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('pdf_documents.id', ondelete='CASCADE'), index=True, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=True)

    document: Mapped[PdfDocument] = relationship(back_populates='chunks')
