"""pdf documents and text chunks

Revision ID: 20260408_0002
Revises: 20260408_0001
Create Date: 2026-04-08

"""
from alembic import op
import sqlalchemy as sa


revision = '20260408_0002'
down_revision = '20260408_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pdf_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('original_filename', sa.String(length=512), nullable=True),
        sa.Column('stored_filename', sa.String(length=512), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('cleaned_text', sa.Text(), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_pdf_documents_id'), 'pdf_documents', ['id'], unique=False)
    op.create_index(op.f('ix_pdf_documents_stored_filename'), 'pdf_documents', ['stored_filename'], unique=True)

    op.create_table(
        'pdf_chunks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('start_char', sa.Integer(), nullable=False),
        sa.Column('end_char', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['pdf_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'chunk_index', name='uq_pdf_chunk_document_index'),
    )
    op.create_index(op.f('ix_pdf_chunks_document_id'), 'pdf_chunks', ['document_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_pdf_chunks_document_id'), table_name='pdf_chunks')
    op.drop_table('pdf_chunks')
    op.drop_index(op.f('ix_pdf_documents_stored_filename'), table_name='pdf_documents')
    op.drop_index(op.f('ix_pdf_documents_id'), table_name='pdf_documents')
    op.drop_table('pdf_documents')
