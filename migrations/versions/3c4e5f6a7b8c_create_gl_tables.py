"""create_gl_tables

Revision ID: 3c4e5f6a7b8c
Revises: 6e53c00a09f4
Create Date: 2026-06-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3c4e5f6a7b8c'
down_revision: Union[str, Sequence[str], None] = '6e53c00a09f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('journal_entries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('journal_number', sa.String(length=50), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('is_posted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('posted_date', sa.DateTime(), nullable=True),
        sa.Column('source_module', sa.String(length=50), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('journal_number')
    )
    op.create_index(op.f('ix_journal_entries_journal_number'), 'journal_entries', ['journal_number'])
    op.create_index(op.f('ix_journal_entries_period'), 'journal_entries', ['period'])

    op.create_table('journal_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('journal_entry_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.String(length=20), nullable=False),
        sa.Column('debit', sa.Numeric(precision=18, scale=2), nullable=False, server_default=sa.text('0.00')),
        sa.Column('credit', sa.Numeric(precision=18, scale=2), nullable=False, server_default=sa.text('0.00')),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('vat_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('line_type', sa.String(length=20), nullable=False, server_default=sa.text("'regular'")),
        sa.Column('is_taxable', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('tax_code', sa.String(length=20), nullable=True),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.code'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_journal_lines_journal_entry_id'), 'journal_lines', ['journal_entry_id'])
    op.create_index(op.f('ix_journal_lines_account_id'), 'journal_lines', ['account_id'])


def downgrade() -> None:
    op.drop_table('journal_lines')
    op.drop_table('journal_entries')
