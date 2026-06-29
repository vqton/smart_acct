"""create_accounting_periods

Revision ID: 4d5e6f7a8b9c
Revises: 3c4e5f6a7b8c
Create Date: 2026-06-29 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d5e6f7a8b9c'
down_revision: Union[str, Sequence[str], None] = '3c4e5f6a7b8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('accounting_periods',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('closed_by', sa.String(length=100), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period')
    )
    op.create_index(op.f('ix_accounting_periods_period'), 'accounting_periods', ['period'])


def downgrade() -> None:
    op.drop_table('accounting_periods')
