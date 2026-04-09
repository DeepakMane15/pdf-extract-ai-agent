"""pgvector extension, rename pdf_chunks to document_chunks, add embedding + page_number

Revision ID: 20260408_0003
Revises: 20260408_0002
Create Date: 2026-04-08

"""
from alembic import op
import sqlalchemy as sa


revision = '20260408_0003'
down_revision = '20260408_0002'
branch_labels = None
depends_on = None

EMBED_DIM = 1536


def upgrade() -> None:
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS vector'))
    op.rename_table('pdf_chunks', 'document_chunks')
    op.add_column('document_chunks', sa.Column('page_number', sa.Integer(), nullable=True))
    op.execute(sa.text(f'ALTER TABLE document_chunks ADD COLUMN embedding vector({EMBED_DIM})'))
    op.execute(
        sa.text(
            'CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_cosine '
            'ON document_chunks USING hnsw (embedding vector_cosine_ops)'
        )
    )


def downgrade() -> None:
    op.execute(sa.text('DROP INDEX IF EXISTS ix_document_chunks_embedding_cosine'))
    op.drop_column('document_chunks', 'embedding')
    op.drop_column('document_chunks', 'page_number')
    op.rename_table('document_chunks', 'pdf_chunks')
