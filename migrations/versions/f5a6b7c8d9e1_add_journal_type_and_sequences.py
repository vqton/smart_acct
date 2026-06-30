"""Add journal_type columns and journal_type_sequences table

Revision ID: f5a6b7c8d9e1
Revises: f5a6b7c8d9e0
Create Date: 2026-06-30 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "f5a6b7c8d9e1"
down_revision: Union[str, Sequence[str], None] = "f5a6b7c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("journal_entries", sa.Column("journal_type", sa.String(20), server_default="general", nullable=False))
    op.add_column("journal_entries", sa.Column("approved_by", sa.String(100), nullable=True))
    op.add_column("journal_entries", sa.Column("is_approved", sa.Boolean, server_default=sa.text("false"), nullable=False))
    op.add_column("journal_entries", sa.Column("approval_date", sa.DateTime(), nullable=True))
    op.add_column("journal_entries", sa.Column("correction_method", sa.String(20), nullable=True))
    op.add_column("journal_entries", sa.Column("ref_journal_number", sa.String(50), nullable=True))

    op.create_table(
        "subsidiary_ledger",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subsidiary_type", sa.String(20), nullable=False),
        sa.Column("account_code", sa.String(20), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("entity_name", sa.String(200), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("doc_ref", sa.String(50), nullable=False),
        sa.Column("doc_type", sa.String(30), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("debit", sa.Numeric(18, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("credit", sa.Numeric(18, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("balance", sa.Numeric(18, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("journal_entry_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["account_code"], ["chart_of_accounts.code"]),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"]),
    )
    op.create_index("idx_subledger_type_period", "subsidiary_ledger", ["subsidiary_type", "period"])
    op.create_index("idx_subledger_entity", "subsidiary_ledger", ["subsidiary_type", "entity_id", "period"])

    op.create_table(
        "journal_type_sequences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("journal_type", sa.String(20), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("last_sequence", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("prefix", sa.String(4), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("journal_type", "fiscal_year", name="uq_journal_type_fiscal_year"),
    )


def downgrade() -> None:
    op.drop_index("idx_subledger_entity", table_name="subsidiary_ledger")
    op.drop_index("idx_subledger_type_period", table_name="subsidiary_ledger")
    op.drop_table("subsidiary_ledger")
    op.drop_table("journal_type_sequences")
    op.drop_column("journal_entries", "ref_journal_number")
    op.drop_column("journal_entries", "correction_method")
    op.drop_column("journal_entries", "approval_date")
    op.drop_column("journal_entries", "is_approved")
    op.drop_column("journal_entries", "approved_by")
    op.drop_column("journal_entries", "journal_type")
