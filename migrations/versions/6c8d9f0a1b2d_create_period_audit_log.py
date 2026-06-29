"""create_period_audit_log

Revision ID: 6c8d9f0a1b2d
Revises: 5e6f7a8b9c0d
Create Date: 2026-06-29 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c8d9f0a1b2d'
down_revision: Union[str, Sequence[str], None] = '5e6f7a8b9c0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('period_audit_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('period', sa.String(length=10), nullable=False),
        sa.Column('event_type', sa.String(length=30), nullable=False),
        sa.Column('user', sa.String(length=100), nullable=False),
        sa.Column('details', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_period_audit_log_period'), 'period_audit_log', ['period'])


def downgrade() -> None:
    op.drop_table('period_audit_log')
