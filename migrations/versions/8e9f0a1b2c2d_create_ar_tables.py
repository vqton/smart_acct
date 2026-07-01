"""create_ar_tables

Revision ID: 8e9f0a1b2c2d
Revises: 7d8e9f0a1b2c
Create Date: 2026-06-29 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


revision: str = '8e9f0a1b2c2d'
down_revision: Union[str, Sequence[str], None] = '7d8e9f0a1b2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CUSTOMER_TYPE_ENUM = ENUM(
    'individual', 'enterprise', 'government', 'foreign',
    name='customertypedb', create_type=False,
)
CUSTOMER_GROUP_ENUM = ENUM(
    'domestic', 'export', 'govt', 'vip',
    name='customergroupdb', create_type=False,
)
CUSTOMER_STATUS_ENUM = ENUM(
    'active', 'suspended', 'blocked', 'archived',
    name='customerstatusdb', create_type=False,
)
INVOICE_TYPE_ENUM = ENUM(
    'sales', 'credit_note', 'debit_note',
    name='invoicetypedb', create_type=False,
)
INVOICE_STATUS_ENUM = ENUM(
    'draft', 'issued', 'partially_paid', 'paid', 'overdue', 'cancelled', 'written_off',
    name='invoicestatusdb', create_type=False,
)
PAYMENT_METHOD_ENUM = ENUM(
    'cash', 'bank_transfer', 'cheque', 'credit_card', 'offline',
    name='paymentmethoddb', create_type=False,
)
ALLOCATION_STATUS_ENUM = ENUM(
    'pending', 'allocated', 'partial', 'reversed',
    name='allocationstatusdb', create_type=False,
)
DUNNING_LEVEL_ENUM = ENUM(
    'level_1', 'level_2', 'level_3', 'legal',
    name='dunningleveldb', create_type=False,
)

INDEXES = [
    sa.Index('ix_customers_code', 'customers', 'customer_code', unique=True),
    sa.Index('ix_customers_tax_code', 'customers', 'tax_code'),
    sa.Index('ix_ar_invoices_number', 'ar_invoices', 'invoice_number', unique=True),
    sa.Index('ix_ar_invoices_customer_code', 'ar_invoices', 'customer_code'),
    sa.Index('ix_ar_invoices_due_date', 'ar_invoices', 'due_date'),
    sa.Index('ix_ar_invoices_period', 'ar_invoices', 'period'),
    sa.Index('ix_ar_invoices_einvoice', 'ar_invoices', 'einvoice_id'),
    sa.Index('ix_ar_payments_number', 'ar_payments', 'payment_number', unique=True),
    sa.Index('ix_ar_payments_date', 'ar_payments', 'payment_date'),
    sa.Index('ix_ar_payments_method', 'ar_payments', 'payment_method'),
]


def _create_safe_enum(name: str, values: list) -> None:
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({','.join(f"'{v}'" for v in values)});
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """)

def upgrade() -> None:
    # Create ENUM types safely (ignore if already exists)
    for enum_name, values in [
        ('customertypedb', ['individual', 'enterprise', 'government', 'foreign']),
        ('customergroupdb', ['domestic', 'export', 'govt', 'vip']),
        ('customerstatusdb', ['active', 'suspended', 'blocked', 'archived']),
        ('invoicetypedb', ['sales', 'credit_note', 'debit_note']),
        ('invoicestatusdb', ['draft', 'issued', 'partially_paid', 'paid', 'overdue', 'cancelled', 'written_off']),
        ('paymentmethoddb', ['cash', 'bank_transfer', 'cheque', 'credit_card', 'offline']),
        ('allocationstatusdb', ['pending', 'allocated', 'partial', 'reversed']),
        ('dunningleveldb', ['level_1', 'level_2', 'level_3', 'legal']),
    ]:
        _create_safe_enum(enum_name, values)
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('customer_code', sa.String(length=20), nullable=False),
        sa.Column('customer_name', sa.String(length=300), nullable=False),
        sa.Column('legal_name', sa.String(length=300), nullable=True),
        sa.Column('tax_code', sa.String(length=20), nullable=True),
        sa.Column('customer_type', CUSTOMER_TYPE_ENUM, nullable=False),
        sa.Column('customer_group', CUSTOMER_GROUP_ENUM, nullable=False),
        sa.Column('status', CUSTOMER_STATUS_ENUM, nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=3), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('credit_limit', sa.Numeric(18, 2), nullable=False),
        sa.Column('outstanding_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('coa_account_code', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_code'),
    )

    op.create_table(
        'ar_invoices',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_number', sa.String(length=20), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('customer_code', sa.String(length=20), nullable=False),
        sa.Column('customer_name', sa.String(length=300), nullable=False),
        sa.Column('invoice_type', INVOICE_TYPE_ENUM, nullable=False),
        sa.Column('status', INVOICE_STATUS_ENUM, nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('paid_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('written_off_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('balance_due', sa.Numeric(18, 2), nullable=False),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('period', sa.String(length=10), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('posted_by', sa.String(length=50), nullable=True),
        sa.Column('coa_code', sa.String(length=20), nullable=True),
        sa.Column('einvoice_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['einvoice_id'], ['einvoices.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number'),
        sa.Index('ix_ar_invoices_customer_id', 'customer_id', unique=False),
    )

    op.create_table(
        'ar_invoice_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 4), nullable=False),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False),
        sa.Column('line_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(8, 4), nullable=False),
        sa.Column('tax_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('coa_code', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['ar_invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_ar_invoice_lines_invoice_id', 'invoice_id', unique=False),
    )

    op.create_table(
        'ar_payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payment_number', sa.String(length=20), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('payment_method', PAYMENT_METHOD_ENUM, nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('received_by', sa.String(length=50), nullable=True),
        sa.Column('bank_account_id', sa.Integer(), nullable=True),
        sa.Column('coa_code', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['ar_invoices.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_number'),
        sa.Index('ix_ar_payments_invoice_id', 'invoice_id', unique=False),
    )

    op.create_index('ix_customers_code', 'customers', ['customer_code'], unique=True)
    op.create_index('ix_customers_tax_code', 'customers', ['tax_code'])
    op.create_index('ix_ar_invoices_number', 'ar_invoices', ['invoice_number'], unique=True)
    op.create_index('ix_ar_invoices_customer_code', 'ar_invoices', ['customer_code'])
    op.create_index('ix_ar_invoices_due_date', 'ar_invoices', ['due_date'])
    op.create_index('ix_ar_invoices_period', 'ar_invoices', ['period'])
    op.create_index('ix_ar_invoices_einvoice', 'ar_invoices', ['einvoice_id'])
    op.create_index('ix_ar_payments_number', 'ar_payments', ['payment_number'], unique=True)
    op.create_index('ix_ar_payments_date', 'ar_payments', ['payment_date'])
    op.create_index('ix_ar_payments_method', 'ar_payments', ['payment_method'])


def downgrade() -> None:
    op.drop_index('ix_ar_payments_method', table_name='ar_payments')
    op.drop_index('ix_ar_payments_date', table_name='ar_payments')
    op.drop_index('ix_ar_payments_number', table_name='ar_payments')
    op.drop_index('ix_ar_invoices_einvoice', table_name='ar_invoices')
    op.drop_index('ix_ar_invoices_period', table_name='ar_invoices')
    op.drop_index('ix_ar_invoices_due_date', table_name='ar_invoices')
    op.drop_index('ix_ar_invoices_customer_code', table_name='ar_invoices')
    op.drop_index('ix_ar_invoices_number', table_name='ar_invoices')
    op.drop_index('ix_customers_tax_code', table_name='customers')
    op.drop_index('ix_customers_code', table_name='customers')

    op.drop_table('ar_payments')
    op.drop_table('ar_invoice_lines')
    op.drop_table('ar_invoices')
    op.drop_table('customers')

    for enum_name in (
        'dunningleveldb', 'allocationstatusdb', 'paymentmethoddb',
        'invoicestatusdb', 'invoicetypedb', 'customerstatusdb',
        'customergroupdb', 'customertypedb',
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
