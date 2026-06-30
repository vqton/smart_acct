"""add bank sub_account_type + last_reconciled_period

Revision ID: 3fa4b5c6d7e8
Revises: 2fa3b4c5d6e7
Create Date: 2026-06-30 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3fa4b5c6d7e8'
down_revision: Union[str, Sequence[str], None] = '2fa3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('bank_accounts', sa.Column('sub_account_type', sa.String(length=3), nullable=True))
    op.add_column('bank_accounts', sa.Column('last_reconciled_period', sa.String(length=7), nullable=True))


def downgrade() -> None:
    op.drop_column('bank_accounts', 'last_reconciled_period')
    op.drop_column('bank_accounts', 'sub_account_type')
