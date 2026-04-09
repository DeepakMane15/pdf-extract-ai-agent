"""pdf_documents.uploaded_by_user_id

Revision ID: 20260408_0006
Revises: 20260408_0005
Create Date: 2026-04-08

"""
from alembic import op
import sqlalchemy as sa


revision = '20260408_0006'
down_revision = '20260408_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'pdf_documents',
        sa.Column('uploaded_by_user_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_pdf_documents_uploaded_by_user_id_users',
        'pdf_documents',
        'users',
        ['uploaded_by_user_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index(op.f('ix_pdf_documents_uploaded_by_user_id'), 'pdf_documents', ['uploaded_by_user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_pdf_documents_uploaded_by_user_id'), table_name='pdf_documents')
    op.drop_constraint('fk_pdf_documents_uploaded_by_user_id_users', 'pdf_documents', type_='foreignkey')
    op.drop_column('pdf_documents', 'uploaded_by_user_id')
