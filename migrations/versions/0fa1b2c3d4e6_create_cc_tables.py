"""create_cc_tables

Revision ID: 0fa1b2c3d4e6
Revises: 9fa1b2c3d4e5
Create Date: 2026-06-30 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0fa1b2c3d4e6'
down_revision: Union[str, Sequence[str], None] = '9fa1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cc_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_allocation_method', sa.Enum('ONE_TIME', 'TWO_TIME', 'MULTI_PERIOD', name='allocationmethoddb'), nullable=False),
        sa.Column('default_useful_life_months', sa.Integer(), nullable=True),
        sa.Column('gl_asset_account', sa.String(length=20), nullable=False, server_default='153'),
        sa.Column('gl_alloc_account', sa.String(length=20), nullable=True),
        sa.Column('gl_expense_account', sa.String(length=20), nullable=False, server_default='627'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_cc_categories_code', 'cc_categories', ['code'])

    op.create_table('cc_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('cc_categories.id'), nullable=False),
        sa.Column('cc_type', sa.Enum('TOOL', 'EQUIPMENT', 'MOLD', 'JIG', 'PATTERN', 'CONTAINER', 'PROTECTIVE_GEAR', 'INSTRUMENT', 'FIXTURE', 'OTHER', name='ccdctypedb'), nullable=False),
        sa.Column('status', sa.Enum('IN_STOCK', 'IN_USE', 'DAMAGED', 'DISPOSED', 'TRANSFERRED', name='ccdcstatusdb'), nullable=False),
        sa.Column('allocation_method', sa.Enum('ONE_TIME', 'TWO_TIME', 'MULTI_PERIOD', name='allocationmethoddb'), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False, server_default='1'),
        sa.Column('unit', sa.String(length=50), nullable=False, server_default='cái'),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('allocated_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('remaining_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('allocation_status', sa.Enum('PENDING', 'PARTIALLY_ALLOCATED', 'FULLY_ALLOCATED', name='allocationstatusdb'), nullable=False),
        sa.Column('useful_life_months', sa.Integer(), nullable=True),
        sa.Column('allocation_start_period', sa.String(length=7), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('supplier', sa.String(length=300), nullable=True),
        sa.Column('invoice_ref', sa.String(length=100), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('in_use_date', sa.Date(), nullable=True),
        sa.Column('warranty_expiry', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('responsibility_type', sa.Enum('USER', 'KEEPER', 'MANAGER', name='responsibilitytypedb'), nullable=False),
        sa.Column('responsible_person', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_cc_items_code', 'cc_items', ['code'])
    op.create_index('ix_cc_items_category_id', 'cc_items', ['category_id'])

    op.create_table('cc_allocations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('cc_items.id'), nullable=False),
        sa.Column('allocation_method', sa.Enum('ONE_TIME', 'TWO_TIME', 'MULTI_PERIOD', name='allocationmethoddb'), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('allocated_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('remaining_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('start_period', sa.String(length=7), nullable=False),
        sa.Column('end_period', sa.String(length=7), nullable=True),
        sa.Column('total_periods', sa.Integer(), nullable=True),
        sa.Column('amount_per_period', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('PENDING', 'PARTIALLY_ALLOCATED', 'FULLY_ALLOCATED', name='allocationstatusdb'), nullable=False),
        sa.Column('gl_account_credit', sa.String(length=20), nullable=False, server_default='153'),
        sa.Column('gl_account_debit', sa.String(length=20), nullable=False, server_default='627'),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cc_allocations_item_id', 'cc_allocations', ['item_id'])

    op.create_table('cc_allocation_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('allocation_id', sa.Integer(), sa.ForeignKey('cc_allocations.id'), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('cc_items.id'), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('planned_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('actual_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('is_posted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('gl_journal_ref', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cc_allocation_lines_allocation_id', 'cc_allocation_lines', ['allocation_id'])
    op.create_index('ix_cc_allocation_lines_item_id', 'cc_allocation_lines', ['item_id'])
    op.create_index('ix_cc_allocation_lines_period', 'cc_allocation_lines', ['period'])

    op.create_table('cc_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('cc_items.id'), nullable=False),
        sa.Column('transaction_type', sa.Enum('RECEIPT', 'ISSUANCE', 'RETURN_TO_STOCK', 'DISPOSAL', 'TRANSFER_OUT', 'TRANSFER_IN', name='transactiontypedb'), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.Column('reference_doc', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cc_transactions_item_id', 'cc_transactions', ['item_id'])
    op.create_index('ix_cc_transactions_period', 'cc_transactions', ['period'])

    op.create_table('cc_transfers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('cc_items.id'), nullable=False),
        sa.Column('from_department_id', sa.Integer(), nullable=True),
        sa.Column('to_department_id', sa.Integer(), nullable=True),
        sa.Column('from_employee_id', sa.Integer(), nullable=True),
        sa.Column('to_employee_id', sa.Integer(), nullable=True),
        sa.Column('from_location', sa.String(length=200), nullable=True),
        sa.Column('to_location', sa.String(length=200), nullable=True),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False, server_default='1'),
        sa.Column('transfer_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cc_transfers_item_id', 'cc_transfers', ['item_id'])

    op.create_table('cc_inventories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('inventory_date', sa.Date(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'COMPLETED', 'RESOLVED', name='ccinventorystatusdb'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cc_inventories_inventory_date', 'cc_inventories', ['inventory_date'])

    op.create_table('cc_inventory_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('inventory_id', sa.Integer(), sa.ForeignKey('cc_inventories.id'), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('cc_items.id'), nullable=False),
        sa.Column('book_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('physical_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('difference', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('difference_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cc_inventory_lines_inventory_id', 'cc_inventory_lines', ['inventory_id'])
    op.create_index('ix_cc_inventory_lines_item_id', 'cc_inventory_lines', ['item_id'])

    op.create_table('cc_write_offs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('cc_items.id'), nullable=False),
        sa.Column('write_off_date', sa.Date(), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False, server_default='1'),
        sa.Column('remaining_value', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('disposal_method', sa.String(length=100), nullable=True),
        sa.Column('proceeds', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('loss_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('document_ref', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cc_write_offs_item_id', 'cc_write_offs', ['item_id'])

    op.create_table('cc_spare_parts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('cc_items.id'), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('unit', sa.String(length=50), nullable=False, server_default='cái'),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_value', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cc_spare_parts_item_id', 'cc_spare_parts', ['item_id'])
    op.create_index('ix_cc_spare_parts_code', 'cc_spare_parts', ['code'])

    op.create_table('cc_import_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('filename', sa.String(length=300), nullable=False),
        sa.Column('import_type', sa.String(length=50), nullable=False),
        sa.Column('import_date', sa.DateTime(), nullable=False),
        sa.Column('total_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('cc_import_logs')
    op.drop_table('cc_spare_parts')
    op.drop_table('cc_write_offs')
    op.drop_table('cc_inventory_lines')
    op.drop_table('cc_inventories')
    op.drop_table('cc_transfers')
    op.drop_table('cc_transactions')
    op.drop_table('cc_allocation_lines')
    op.drop_table('cc_allocations')
    op.drop_table('cc_items')
    op.drop_table('cc_categories')
