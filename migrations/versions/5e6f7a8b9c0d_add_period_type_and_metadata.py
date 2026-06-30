"""add_period_type_and_metadata

Revision ID: 5e6f7a8b9c0d
Revises: 4d5e6f7a8b9c
Create Date: 2026-06-29 14:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5e6f7a8b9c0d'
down_revision: Union[str, Sequence[str], None] = '4d5e6f7a8b9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE periodtype AS ENUM ('MONTHLY', 'QUARTERLY', 'YEARLY')")
    op.add_column('accounting_periods',
        sa.Column('type', sa.Enum('MONTHLY', 'QUARTERLY', 'YEARLY', name='periodtype', create_type=False), nullable=False,
                  server_default='MONTHLY')
    )
    op.add_column('accounting_periods',
        sa.Column('start_date', sa.Date(), nullable=True)
    )
    op.add_column('accounting_periods',
        sa.Column('end_date', sa.Date(), nullable=True)
    )
    op.add_column('accounting_periods',
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
    op.add_column('accounting_periods',
        sa.Column('needs_reconciliation', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
    op.add_column('accounting_periods',
        sa.Column('parent_period', sa.String(length=10), nullable=True)
    )
    op.create_index(op.f('ix_accounting_periods_parent_period'), 'accounting_periods', ['parent_period'])


def downgrade() -> None:
    op.drop_index(op.f('ix_accounting_periods_parent_period'), table_name='accounting_periods')
    op.drop_column('accounting_periods', 'parent_period')
    op.drop_column('accounting_periods', 'needs_reconciliation')
    op.drop_column('accounting_periods', 'is_current')
    op.drop_column('accounting_periods', 'end_date')
    op.drop_column('accounting_periods', 'start_date')
    op.drop_column('accounting_periods', 'type')
    op.execute('DROP TYPE IF EXISTS periodtype')
