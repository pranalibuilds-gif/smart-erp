"""adjust_auth_models_for_step_3

Revision ID: 844dec4d1f2a
Revises: 180faf0450cb
Create Date: 2026-06-20 19:32:22.486943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '844dec4d1f2a'
down_revision: Union[str, Sequence[str], None] = '180faf0450cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add columns to refresh_tokens
    op.add_column('refresh_tokens', sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')))
    op.add_column('refresh_tokens', sa.Column('user_agent', sa.String(length=500), nullable=True))
    op.add_column('refresh_tokens', sa.Column('ip_address', sa.String(length=100), nullable=True))

    # 2. Adjust user_company_roles Primary Key
    # First drop constraints that rely on role_id being in PK/Unique
    op.drop_constraint('uq_user_company_role', 'user_company_roles', type_='unique')
    op.drop_constraint('pk_user_company_roles', 'user_company_roles', type_='primary')

    # Add the new PRIMARY KEY
    op.create_primary_key('pk_user_company_roles', 'user_company_roles', ['user_id', 'company_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Revert user_company_roles constraints
    op.drop_constraint('pk_user_company_roles', 'user_company_roles', type_='primary')

    # Re-add old constraints
    op.create_primary_key('pk_user_company_roles', 'user_company_roles', ['user_id', 'company_id', 'role_id'])
    op.create_unique_constraint('uq_user_company_role', 'user_company_roles', ['user_id', 'company_id', 'role_id'])

    # 2. Remove columns from refresh_tokens
    op.drop_column('refresh_tokens', 'ip_address')
    op.drop_column('refresh_tokens', 'user_agent')
    op.drop_column('refresh_tokens', 'last_used_at')
