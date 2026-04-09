"""tool_execution_logs for AI tool invocations

Revision ID: 20260408_0004
Revises: 20260408_0003
Create Date: 2026-04-08

"""
from alembic import op
import sqlalchemy as sa


revision = '20260408_0004'
down_revision = '20260408_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tool_execution_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tool_name', sa.String(length=128), nullable=False),
        sa.Column('input_args', sa.JSON(), nullable=False),
        sa.Column('output_text', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tool_execution_logs_id'), 'tool_execution_logs', ['id'], unique=False)
    op.create_index(op.f('ix_tool_execution_logs_tool_name'), 'tool_execution_logs', ['tool_name'], unique=False)
    op.create_index(op.f('ix_tool_execution_logs_success'), 'tool_execution_logs', ['success'], unique=False)
    op.create_index(op.f('ix_tool_execution_logs_user_id'), 'tool_execution_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tool_execution_logs_user_id'), table_name='tool_execution_logs')
    op.drop_index(op.f('ix_tool_execution_logs_success'), table_name='tool_execution_logs')
    op.drop_index(op.f('ix_tool_execution_logs_tool_name'), table_name='tool_execution_logs')
    op.drop_index(op.f('ix_tool_execution_logs_id'), table_name='tool_execution_logs')
    op.drop_table('tool_execution_logs')
