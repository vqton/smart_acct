"""create_cash_tables

Revision ID: 7d8e9f0a1b2c
Revises: 6c8d9f0a1b2d
Create Date: 2026-06-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '7d8e9f0a1b2c'
down_revision: Union[str, Sequence[str], None] = '6c8d9f0a1b2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('bank_accounts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bank_name', sa.String(length=200), nullable=False),
        sa.Column('branch', sa.String(length=200), nullable=False),
        sa.Column('account_number', sa.String(length=50), nullable=False),
        sa.Column('account_holder', sa.String(length=300), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('coa_code', sa.String(length=20), nullable=False),
        sa.Column('swift_code', sa.String(length=20), nullable=True),
        sa.Column('iban', sa.String(length=50), nullable=True),
        sa.Column('opening_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'CLOSED', 'BLOCKED', name='bankaccountstatusdb'), nullable=False),
        sa.Column('signatories', sa.JSON(), nullable=True),
        sa.Column('authorization_limit', sa.Numeric(18, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('cash_receipts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('receipt_number', sa.String(length=20), nullable=False),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('receipt_type', sa.String(length=30), nullable=False),
        sa.Column('payer_name', sa.String(length=300), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('amount_in_words', sa.String(length=500), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('fx_rate', sa.Numeric(18, 6), nullable=True),
        sa.Column('account_code', sa.String(length=20), nullable=False),
        sa.Column('counter_account', sa.String(length=20), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'PAID', 'CANCELLED', name='cashvoucherstatusdb'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('receipt_number'),
    )
    op.create_index('ix_cash_receipts_receipt_number', 'cash_receipts', ['receipt_number'])
    op.create_table('cash_payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payment_number', sa.String(length=20), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_type', sa.String(length=30), nullable=False),
        sa.Column('receiver_name', sa.String(length=300), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('amount_in_words', sa.String(length=500), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('fx_rate', sa.Numeric(18, 6), nullable=True),
        sa.Column('account_code', sa.String(length=20), nullable=False),
        sa.Column('counter_account', sa.String(length=20), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('supporting_doc_ref', sa.String(length=100), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'PAID', 'CANCELLED', name='cashvoucherstatusdb'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_number'),
    )
    op.create_index('ix_cash_payments_payment_number', 'cash_payments', ['payment_number'])
    op.create_table('cash_transfers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_account', sa.String(length=20), nullable=False),
        sa.Column('destination_account', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('transfer_date', sa.Date(), nullable=False),
        sa.Column('fx_rate', sa.Numeric(18, 6), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'IN_TRANSIT', 'COMPLETED', 'FAILED', name='cashtransferstatusdb'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('cheque_books',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('start_number', sa.String(length=20), nullable=False),
        sa.Column('end_number', sa.String(length=20), nullable=False),
        sa.Column('issued_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cheque_books_bank_account_id', 'cheque_books', ['bank_account_id'])
    op.create_table('daily_cash_counts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('count_date', sa.Date(), nullable=False),
        sa.Column('account_code', sa.String(length=20), nullable=False),
        sa.Column('expected_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('actual_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('difference', sa.Numeric(18, 2), nullable=False),
        sa.Column('denomination_breakdown', sa.JSON(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('counted_by', sa.String(length=100), nullable=False),
        sa.Column('witnessed_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_daily_cash_counts_count_date', 'daily_cash_counts', ['count_date'])
    op.create_table('petty_cash_funds',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fund_code', sa.String(length=50), nullable=False),
        sa.Column('custodian', sa.String(length=200), nullable=False),
        sa.Column('limit_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('current_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('established_date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', 'CLOSED', name='pettycashfundstatusdb'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('fund_code'),
    )
    op.create_index('ix_petty_cash_funds_fund_code', 'petty_cash_funds', ['fund_code'])
    op.create_table('advances',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_name', sa.String(length=200), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('advance_date', sa.Date(), nullable=False),
        sa.Column('purpose', sa.String(length=500), nullable=False),
        sa.Column('settlement_deadline', sa.Date(), nullable=False),
        sa.Column('settlement_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('remaining_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_advances_employee_id', 'advances', ['employee_id'])
    op.create_table('bank_statements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('statement_date', sa.Date(), nullable=False),
        sa.Column('opening_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('closing_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('imported_at', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_bank_statements_bank_account_id', 'bank_statements', ['bank_account_id'])
    op.create_table('bank_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('statement_id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('value_date', sa.Date(), nullable=True),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('is_debit', sa.Boolean(), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('matched_entry_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_bank_transactions_bank_account_id', 'bank_transactions', ['bank_account_id'])
    op.create_index('ix_bank_transactions_statement_id', 'bank_transactions', ['statement_id'])
    op.create_index('ix_bank_transactions_matched_entry_id', 'bank_transactions', ['matched_entry_id'])
    op.create_table('bank_reconciliations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('book_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('bank_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('deposits_in_transit', sa.Numeric(18, 2), nullable=False),
        sa.Column('outstanding_checks', sa.Numeric(18, 2), nullable=False),
        sa.Column('unrecorded_credits', sa.Numeric(18, 2), nullable=False),
        sa.Column('unrecorded_debits', sa.Numeric(18, 2), nullable=False),
        sa.Column('adjusted_book_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('adjusted_bank_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('is_balanced', sa.Boolean(), nullable=False),
        sa.Column('reconciled_at', sa.DateTime(), nullable=True),
        sa.Column('reconciled_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_bank_reconciliations_bank_account_id', 'bank_reconciliations', ['bank_account_id'])
    op.create_index('ix_bank_reconciliations_period', 'bank_reconciliations', ['period'])
    op.create_table('reconciliation_discrepancies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('reconciliation_id', sa.Integer(), nullable=False),
        sa.Column('discrepancy_type', sa.String(length=30), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('entry_side', sa.String(length=10), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('resolution_entry_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_reconciliation_discrepancies_reconciliation_id', 'reconciliation_discrepancies', ['reconciliation_id'])
    op.create_table('petty_cash_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fund_id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('is_replenishment', sa.Boolean(), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('receipt_ref', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_petty_cash_transactions_fund_id', 'petty_cash_transactions', ['fund_id'])
    op.create_table('cheques',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cheque_number', sa.String(length=20), nullable=False),
        sa.Column('cheque_book_id', sa.Integer(), nullable=False),
        sa.Column('payee', sa.String(length=300), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('NEW', 'ISSUED', 'CLEARED', 'CANCELLED', 'STOPPED', 'BOUNCED', name='chequestatusdb'), nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('cleared_date', sa.Date(), nullable=True),
        sa.Column('cancelled_reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cheques_cheque_number', 'cheques', ['cheque_number'])
    op.create_index('ix_cheques_cheque_book_id', 'cheques', ['cheque_book_id'])
    op.create_index('ix_cheques_bank_account_id', 'cheques', ['bank_account_id'])
    op.create_table('cash_forecasts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('projected_inflows', sa.Numeric(18, 2), nullable=False),
        sa.Column('projected_outflows', sa.Numeric(18, 2), nullable=False),
        sa.Column('net_cash_flow', sa.Numeric(18, 2), nullable=False),
        sa.Column('opening_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('closing_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('cash_forecasts')
    op.drop_table('cheques')
    op.drop_table('petty_cash_transactions')
    op.drop_table('reconciliation_discrepancies')
    op.drop_table('bank_reconciliations')
    op.drop_table('bank_transactions')
    op.drop_table('bank_statements')
    op.drop_table('advances')
    op.drop_table('petty_cash_funds')
    op.drop_table('daily_cash_counts')
    op.drop_table('cheque_books')
    op.drop_table('cash_transfers')
    op.drop_table('cash_payments')
    op.drop_table('cash_receipts')
    op.drop_table('bank_accounts')
    op.execute('DROP TYPE IF EXISTS bankaccountstatusdb')
    op.execute('DROP TYPE IF EXISTS cashvoucherstatusdb')
    op.execute('DROP TYPE IF EXISTS cashtransferstatusdb')
    op.execute('DROP TYPE IF EXISTS pettycashfundstatusdb')
    op.execute('DROP TYPE IF EXISTS chequestatusdb')
