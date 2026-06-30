"""create_ap_tables

Revision ID: 8e9f0a1b2c3d
Revises: 7d8e9f0a1b2c
Create Date: 2026-06-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8e9f0a1b2c3d'
down_revision: Union[str, Sequence[str], None] = '7d8e9f0a1b2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('vendors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vendor_code', sa.String(length=20), nullable=False),
        sa.Column('vendor_name', sa.String(length=300), nullable=False),
        sa.Column('legal_name', sa.String(length=300), nullable=True),
        sa.Column('tax_code', sa.String(length=20), nullable=True),
        sa.Column('vendor_type', sa.Enum('INDIVIDUAL', 'ENTERPRISE', 'GOVERNMENT', 'FOREIGN', name='vendortypedb'), nullable=False),
        sa.Column('vendor_group', sa.Enum('DOMESTIC', 'IMPORT', 'VIP', 'GOVT', name='vendorgroupdb'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', 'BLOCKED', 'ARCHIVED', name='vendorstatusdb'), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=3), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('payment_terms', sa.String(length=20), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('bank_name', sa.String(length=200), nullable=True),
        sa.Column('bank_account', sa.String(length=50), nullable=True),
        sa.Column('bank_swift', sa.String(length=20), nullable=True),
        sa.Column('credit_limit', sa.Numeric(18, 2), nullable=False),
        sa.Column('coa_code', sa.String(length=20), nullable=True),
        sa.Column('foreign_ct_type', sa.String(length=20), nullable=True),
        sa.Column('foreign_vat_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('foreign_cit_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vendor_code'),
    )
    op.create_index('ix_vendors_vendor_code', 'vendors', ['vendor_code'])
    op.create_index('ix_vendors_tax_code', 'vendors', ['tax_code'])
    op.create_index('ix_vendors_coa_code', 'vendors', ['coa_code'])

    op.create_table('ap_invoices',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_number', sa.String(length=20), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('vendor_code', sa.String(length=20), nullable=True),
        sa.Column('vendor_name', sa.String(length=300), nullable=True),
        sa.Column('invoice_type', sa.Enum('PO_BASED', 'NON_PO', 'PREPAYMENT', name='apinvoicetypedb'), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'SUBMITTED', 'WAITING_RECEIPT', 'MATCHED', 'APPROVED', 'PAID_PARTIAL', 'PAID_FULL', 'OVERDUE', 'CANCELLED', 'REJECTED', 'WRITTEN_OFF', name='apinvoicestatusdb'), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('discount_date', sa.Date(), nullable=True),
        sa.Column('discount_percent', sa.Numeric(5, 4), nullable=True),
        sa.Column('posted_date', sa.Date(), nullable=True),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('paid_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('written_off_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('balance_due', sa.Numeric(18, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('fx_rate', sa.Numeric(18, 6), nullable=True),
        sa.Column('fx_gl_rate', sa.Numeric(18, 6), nullable=True),
        sa.Column('po_number', sa.String(length=20), nullable=True),
        sa.Column('gr_number', sa.String(length=20), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('period', sa.String(length=10), nullable=True),
        sa.Column('coa_code', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ap_invoices_invoice_number', 'ap_invoices', ['invoice_number'])
    op.create_index('ix_ap_invoices_due_date', 'ap_invoices', ['due_date'])
    op.create_index('ix_ap_invoices_po_number', 'ap_invoices', ['po_number'])
    op.create_index('ix_ap_invoices_period', 'ap_invoices', ['period'])
    op.create_index('ix_ap_invoice_vendor_number', 'ap_invoices', ['vendor_id', 'invoice_number'], unique=True)

    op.create_table('ap_invoice_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ap_invoice_id', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 4), nullable=False),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False),
        sa.Column('line_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(8, 4), nullable=False),
        sa.Column('tax_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('coa_code', sa.String(length=20), nullable=True),
        sa.Column('po_line_number', sa.Integer(), nullable=True),
        sa.Column('gr_line_number', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('ap_credit_notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('credit_note_number', sa.String(length=20), nullable=False),
        sa.Column('original_invoice_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_adjustment', sa.Numeric(18, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('credit_note_date', sa.Date(), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('credit_note_number'),
    )
    op.create_index('ix_ap_credit_notes_credit_note_number', 'ap_credit_notes', ['credit_note_number'])

    op.create_table('ap_debit_notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('debit_note_number', sa.String(length=20), nullable=False),
        sa.Column('original_invoice_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('debit_note_date', sa.Date(), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('debit_note_number'),
    )
    op.create_index('ix_ap_debit_notes_debit_note_number', 'ap_debit_notes', ['debit_note_number'])

    op.create_table('ap_payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payment_number', sa.String(length=20), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=True),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('discount_taken', sa.Numeric(18, 2), nullable=False),
        sa.Column('net_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('payment_method', sa.Enum('CASH', 'BANK_TRANSFER', 'CHEQUE', 'CARD', name='appaymentmethoddb'), nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'PROPOSED', 'APPROVED', 'EXECUTING', 'EXECUTED', 'POSTED', 'FAILED', 'CANCELLED', 'REJECTED', name='appaymentstatusdb'), nullable=False),
        sa.Column('is_batch_payment', sa.Boolean(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('approval_by', sa.String(length=100), nullable=True),
        sa.Column('approval_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_number'),
    )
    op.create_index('ix_ap_payments_payment_number', 'ap_payments', ['payment_number'])
    op.create_index('ix_ap_payments_payment_method', 'ap_payments', ['payment_method'])
    op.create_index('ix_ap_payments_batch_id', 'ap_payments', ['batch_id'])

    op.create_table('ap_payment_allocations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ap_payment_id', sa.Integer(), nullable=False),
        sa.Column('ap_invoice_id', sa.Integer(), nullable=False),
        sa.Column('allocated_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('is_adjustment', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('ap_prepayments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('unapplied_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('expected_invoice_date', sa.Date(), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPLIED', 'CANCELLED', name='prepaymentstatusdb'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('ap_provisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=10), nullable=False),
        sa.Column('provision_percent', sa.Numeric(5, 2), nullable=False),
        sa.Column('overdue_days', sa.Integer(), nullable=False),
        sa.Column('invoice_total', sa.Numeric(18, 2), nullable=False),
        sa.Column('provision_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'PARTIALLY_WRITTEN_OFF', 'FULLY_WRITTEN_OFF', name='provisionstatusdb'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ap_provisions_period', 'ap_provisions', ['period'])

    op.create_table('ap_aging_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('period', sa.String(length=10), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('vendor_code', sa.String(length=20), nullable=False),
        sa.Column('vendor_name', sa.String(length=300), nullable=False),
        sa.Column('current_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('bucket_1_30', sa.Numeric(18, 2), nullable=False),
        sa.Column('bucket_31_60', sa.Numeric(18, 2), nullable=False),
        sa.Column('bucket_61_90', sa.Numeric(18, 2), nullable=False),
        sa.Column('bucket_91_180', sa.Numeric(18, 2), nullable=False),
        sa.Column('bucket_181_365', sa.Numeric(18, 2), nullable=False),
        sa.Column('bucket_365_plus', sa.Numeric(18, 2), nullable=False),
        sa.Column('total_outstanding', sa.Numeric(18, 2), nullable=False),
        sa.Column('locked', sa.Boolean(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ap_aging_snapshots_period', 'ap_aging_snapshots', ['period'])
    op.create_index('ix_ap_aging_period_vendor', 'ap_aging_snapshots', ['period', 'vendor_id'], unique=True)

    op.create_table('ap_fct_declarations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=10), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('fct_method', sa.Enum('DIRECT', 'DEDUCTION', 'HYBRID', name='fctmethoddb'), nullable=False),
        sa.Column('vat_rate', sa.Numeric(5, 4), nullable=False),
        sa.Column('cit_rate', sa.Numeric(5, 4), nullable=False),
        sa.Column('gross_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('vat_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('cit_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('net_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'DECLARED', 'REMITTED', 'OVERDUE', name='fctstatusdb'), nullable=False),
        sa.Column('declared_at', sa.DateTime(), nullable=True),
        sa.Column('remitted_at', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ap_fct_declarations_period', 'ap_fct_declarations', ['period'])

    op.create_table('ap_intercompany_invoices',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('from_entity_code', sa.String(length=20), nullable=False),
        sa.Column('to_entity_code', sa.String(length=20), nullable=False),
        sa.Column('invoice_number', sa.String(length=20), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ap_intercompany_invoices_from_entity_code', 'ap_intercompany_invoices', ['from_entity_code'])
    op.create_index('ix_ap_intercompany_invoices_to_entity_code', 'ap_intercompany_invoices', ['to_entity_code'])


def downgrade() -> None:
    op.drop_table('ap_intercompany_invoices')
    op.drop_table('ap_fct_declarations')
    op.drop_table('ap_aging_snapshots')
    op.drop_table('ap_provisions')
    op.drop_table('ap_prepayments')
    op.drop_table('ap_payment_allocations')
    op.drop_table('ap_payments')
    op.drop_table('ap_debit_notes')
    op.drop_table('ap_credit_notes')
    op.drop_table('ap_invoice_lines')
    op.drop_table('ap_invoices')
    op.drop_table('vendors')
    op.execute('DROP TYPE IF EXISTS vendortypedb')
    op.execute('DROP TYPE IF EXISTS vendorgroupdb')
    op.execute('DROP TYPE IF EXISTS vendorstatusdb')
    op.execute('DROP TYPE IF EXISTS apinvoicetypedb')
    op.execute('DROP TYPE IF EXISTS apinvoicestatusdb')
    op.execute('DROP TYPE IF EXISTS appaymentmethoddb')
    op.execute('DROP TYPE IF EXISTS appaymentstatusdb')
    op.execute('DROP TYPE IF EXISTS fctmethoddb')
    op.execute('DROP TYPE IF EXISTS fctstatusdb')
    op.execute('DROP TYPE IF EXISTS prepaymentstatusdb')
    op.execute('DROP TYPE IF EXISTS provisionstatusdb')
