"""Per-user encrypted OpenAI key + token usage counters

Revision ID: 20260408_0005
Revises: 20260408_0004
Create Date: 2026-04-08

"""
from alembic import op
import sqlalchemy as sa


revision = '20260408_0005'
down_revision = '20260408_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('openai_api_key_encrypted', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('openai_key_hint', sa.String(length=64), nullable=True))
    op.add_column(
        'users',
        sa.Column('openai_embed_prompt_tokens_total', sa.BigInteger(), server_default='0', nullable=False),
    )
    op.add_column(
        'users',
        sa.Column('openai_chat_prompt_tokens_total', sa.BigInteger(), server_default='0', nullable=False),
    )
    op.add_column(
        'users',
        sa.Column('openai_chat_completion_tokens_total', sa.BigInteger(), server_default='0', nullable=False),
    )


def downgrade() -> None:
    op.drop_column('users', 'openai_chat_completion_tokens_total')
    op.drop_column('users', 'openai_chat_prompt_tokens_total')
    op.drop_column('users', 'openai_embed_prompt_tokens_total')
    op.drop_column('users', 'openai_key_hint')
    op.drop_column('users', 'openai_api_key_encrypted')
