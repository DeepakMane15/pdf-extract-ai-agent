"""create users table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260408_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the enum once; use create_type=False on the column so create_table does not emit CREATE TYPE again.
    user_role = postgresql.ENUM('admin', 'user', 'auditor', name='user_role')
    user_role.create(op.get_bind(), checkfirst=True)

    role_column = postgresql.ENUM('admin', 'user', 'auditor', name='user_role', create_type=False)

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', role_column, nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    postgresql.ENUM(name='user_role').drop(op.get_bind(), checkfirst=True)
