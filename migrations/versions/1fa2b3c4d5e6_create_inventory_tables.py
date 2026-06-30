"""create_inventory_tables

Revision ID: 1fa2b3c4d5e6
Revises: 0fa1b2c3d4e6
Create Date: 2026-06-30 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '1fa2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '0fa1b2c3d4e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── inv_categories ──────────────────────────────────────────────
    op.create_table('inv_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('inv_categories.id'), nullable=True),
        sa.Column('inventory_type',
                  sa.Enum('RAW_MATERIAL', 'MATERIAL', 'SEMI_FINISHED', 'FINISHED_GOOD',
                          'MERCHANDISE', 'PACKAGING', 'FUEL', 'SPARE_PART', 'EQUIPMENT',
                          'WASTE', 'OTHER', name='inventorytypedb'),
                  nullable=False),
        sa.Column('valuation_method',
                  sa.Enum('SPECIFIC', 'FIFO', 'LIFO', 'WEIGHTED_AVERAGE', 'MOVING_AVERAGE',
                          'STANDARD', 'RETAIL', name='valuationmethoddb'),
                  nullable=False),
        sa.Column('gl_inventory_account', sa.String(length=20), nullable=False, server_default='152'),
        sa.Column('gl_receipt_account', sa.String(length=20), nullable=False, server_default='331'),
        sa.Column('gl_issue_account', sa.String(length=20), nullable=False, server_default='621'),
        sa.Column('gl_sales_account', sa.String(length=20), nullable=False, server_default='632'),
        sa.Column('gl_cost_of_sales', sa.String(length=20), nullable=False, server_default='632'),
        sa.Column('gl_return_account', sa.String(length=20), nullable=False, server_default='521'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_inv_categories_code', 'inv_categories', ['code'])

    # ── inv_warehouses ──────────────────────────────────────────────
    op.create_table('inv_warehouses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('allow_negative_stock', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('check_method',
                  sa.Enum('PERIODIC', 'PERPETUAL', name='checkmethoddb'),
                  nullable=False),
        sa.Column('gl_inventory_account', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_inv_warehouses_code', 'inv_warehouses', ['code'])

    # ── inv_items ───────────────────────────────────────────────────
    op.create_table('inv_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('inv_categories.id'), nullable=False),
        sa.Column('default_warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=True),
        sa.Column('inventory_type', sa.Enum('RAW_MATERIAL', 'MATERIAL', 'SEMI_FINISHED',
                                            'FINISHED_GOOD', 'MERCHANDISE', 'PACKAGING',
                                            'FUEL', 'SPARE_PART', 'EQUIPMENT', 'WASTE',
                                            'OTHER', name='inventorytypedb'),
                  nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'DISCONTINUED', name='inventorystatusdb'),
                  nullable=False, server_default='ACTIVE'),
        sa.Column('valuation_method', sa.Enum('SPECIFIC', 'FIFO', 'LIFO', 'WEIGHTED_AVERAGE',
                                              'MOVING_AVERAGE', 'STANDARD', 'RETAIL',
                                              name='valuationmethoddb'), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=False, server_default='cái'),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('cost_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('selling_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('min_stock', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('max_stock', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('reorder_point', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('reorder_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('current_stock', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('reserved_stock', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('available_stock', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('batch_tracking', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('serial_tracking', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expiry_tracking', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('weight', sa.Numeric(18, 4), nullable=True),
        sa.Column('volume', sa.Numeric(18, 4), nullable=True),
        sa.Column('hs_code', sa.String(length=20), nullable=True),
        sa.Column('barcode', sa.String(length=100), nullable=True),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, server_default='10'),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('gl_inventory_account', sa.String(length=20), nullable=True),
        sa.Column('gl_receipt_account', sa.String(length=20), nullable=True),
        sa.Column('gl_issue_account', sa.String(length=20), nullable=True),
        sa.Column('gl_sales_account', sa.String(length=20), nullable=True),
        sa.Column('gl_cost_of_sales', sa.String(length=20), nullable=True),
        sa.Column('gl_return_account', sa.String(length=20), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_inv_items_code', 'inv_items', ['code'])
    op.create_index('ix_inv_items_category', 'inv_items', ['category_id'])

    # ── inv_batches ────────────────────────────────────────────────
    op.create_table('inv_batches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('inv_items.id'), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=True),
        sa.Column('batch_code', sa.String(length=100), nullable=False),
        sa.Column('manufacturing_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('received_date', sa.Date(), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('remaining_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('unit_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('status',
                  sa.Enum('ACTIVE', 'EXPIRED', 'QUARANTINED', 'DISPOSED', name='batchstatusdb'),
                  nullable=False, server_default='ACTIVE'),
        sa.Column('supplier_batch', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inv_batches_item', 'inv_batches', ['item_id'])

    # ── inv_serials ─────────────────────────────────────────────────
    op.create_table('inv_serials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('inv_items.id'), nullable=False),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('inv_batches.id'), nullable=True),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=True),
        sa.Column('serial_code', sa.String(length=100), nullable=False),
        sa.Column('status',
                  sa.Enum('IN_STOCK', 'ISSUED', 'RETURNED', 'SCRAPPED', 'QUARANTINED',
                          name='serialstatusdb'),
                  nullable=False, server_default='IN_STOCK'),
        sa.Column('receipt_date', sa.Date(), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inv_serials_item', 'inv_serials', ['item_id'])

    # ── inv_receipts ────────────────────────────────────────────────
    op.create_table('inv_receipts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('receipt_code', sa.String(length=50), nullable=False),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('supplier_invoice_ref', sa.String(length=100), nullable=True),
        sa.Column('reference_doc', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_posted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('gl_journal_ref', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('receipt_code'),
    )
    op.create_index('ix_inv_receipts_code', 'inv_receipts', ['receipt_code'])
    op.create_index('ix_inv_receipts_wh', 'inv_receipts', ['warehouse_id'])

    # ── inv_receipt_lines ───────────────────────────────────────────
    op.create_table('inv_receipt_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('inv_receipts.id'), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('inv_items.id'), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('inv_batches.id'), nullable=True),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('line_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inv_receipt_lines_receipt', 'inv_receipt_lines', ['receipt_id'])

    # ── inv_issues ──────────────────────────────────────────────────
    op.create_table('inv_issues',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('issue_code', sa.String(length=50), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('recipient_name', sa.String(length=200), nullable=True),
        sa.Column('reference_doc', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_posted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('gl_journal_ref', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('issue_code'),
    )
    op.create_index('ix_inv_issues_code', 'inv_issues', ['issue_code'])
    op.create_index('ix_inv_issues_wh', 'inv_issues', ['warehouse_id'])

    # ── inv_issue_lines ─────────────────────────────────────────────
    op.create_table('inv_issue_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('issue_id', sa.Integer(), sa.ForeignKey('inv_issues.id'), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('inv_items.id'), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('inv_batches.id'), nullable=True),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('line_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('cost_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inv_issue_lines_issue', 'inv_issue_lines', ['issue_id'])

    # ── inv_transfers ───────────────────────────────────────────────
    op.create_table('inv_transfers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('transfer_code', sa.String(length=50), nullable=False),
        sa.Column('transfer_date', sa.Date(), nullable=False),
        sa.Column('from_warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('to_warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('status',
                  sa.Enum('DRAFT', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED', name='transferstatusdb'),
                  nullable=False, server_default='DRAFT'),
        sa.Column('reference_doc', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_posted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('gl_journal_ref', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transfer_code'),
    )
    op.create_index('ix_inv_transfers_code', 'inv_transfers', ['transfer_code'])

    # ── inv_transfer_lines ──────────────────────────────────────────
    op.create_table('inv_transfer_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('transfer_id', sa.Integer(), sa.ForeignKey('inv_transfers.id'), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('inv_items.id'), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 2), nullable=False),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('line_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inv_transfer_lines_transfer', 'inv_transfer_lines', ['transfer_id'])

    # ── inv_stock_cards ─────────────────────────────────────────────
    op.create_table('inv_stock_cards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('inv_items.id'), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('opening_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('opening_value', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('receipt_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('receipt_value', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('issue_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('issue_value', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('closing_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('closing_value', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('unit_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inv_stock_cards_composite', 'inv_stock_cards', ['item_id', 'warehouse_id', 'period'])

    # ── inv_checks ──────────────────────────────────────────────────
    op.create_table('inv_checks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('check_code', sa.String(length=50), nullable=False),
        sa.Column('check_date', sa.Date(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('status',
                  sa.Enum('DRAFT', 'IN_PROGRESS', 'COMPLETED', 'APPROVED', 'CANCELLED',
                          name='inventorycheckstatusdb'),
                  nullable=False, server_default='DRAFT'),
        sa.Column('reference_doc', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('check_code'),
    )
    op.create_index('ix_inv_checks_code', 'inv_checks', ['check_code'])
    op.create_index('ix_inv_checks_wh', 'inv_checks', ['warehouse_id'])

    # ── inv_check_lines ─────────────────────────────────────────────
    op.create_table('inv_check_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('check_id', sa.Integer(), sa.ForeignKey('inv_checks.id'), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('inv_items.id'), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('inv_batches.id'), nullable=True),
        sa.Column('book_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('physical_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('difference_quantity', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('difference_value', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('resolution', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inv_check_lines_check', 'inv_check_lines', ['check_id'])

    # ── inv_adjustments ─────────────────────────────────────────────
    op.create_table('inv_adjustments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('adjustment_code', sa.String(length=50), nullable=False),
        sa.Column('adjustment_date', sa.Date(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('adjustment_type',
                  sa.Enum('WRITE_OFF', 'WRITE_ON', 'DAMAGE', 'THEFT', 'DONATION',
                          'SAMPLE', 'ERROR_CORRECTION', 'REVALUATION', 'OTHER',
                          name='adjustmenttypedb'),
                  nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('reference_doc', sa.String(length=100), nullable=True),
        sa.Column('is_posted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('gl_journal_ref', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('adjustment_code'),
    )
    op.create_index('ix_inv_adjustments_code', 'inv_adjustments', ['adjustment_code'])
    op.create_index('ix_inv_adjustments_wh', 'inv_adjustments', ['warehouse_id'])

    # ── inv_adjustment_lines ────────────────────────────────────────
    op.create_table('inv_adjustment_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('adjustment_id', sa.Integer(), sa.ForeignKey('inv_adjustments.id'), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('inv_items.id'), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('inv_warehouses.id'), nullable=False),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('inv_batches.id'), nullable=True),
        sa.Column('quantity_change', sa.Numeric(18, 2), nullable=False),
        sa.Column('unit_price', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('line_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inv_adj_lines_adj', 'inv_adjustment_lines', ['adjustment_id'])


def downgrade() -> None:
    op.drop_table('inv_adjustment_lines')
    op.drop_table('inv_adjustments')
    op.drop_table('inv_check_lines')
    op.drop_table('inv_checks')
    op.drop_table('inv_stock_cards')
    op.drop_table('inv_transfer_lines')
    op.drop_table('inv_transfers')
    op.drop_table('inv_issue_lines')
    op.drop_table('inv_issues')
    op.drop_table('inv_receipt_lines')
    op.drop_table('inv_receipts')
    op.drop_table('inv_serials')
    op.drop_table('inv_batches')
    op.drop_table('inv_items')
    op.drop_table('inv_warehouses')
    op.drop_table('inv_categories')

    op.execute("DROP TYPE IF EXISTS inventorytypedb")
    op.execute("DROP TYPE IF EXISTS inventorystatusdb")
    op.execute("DROP TYPE IF EXISTS valuationmethoddb")
    op.execute("DROP TYPE IF EXISTS checkmethoddb")
    op.execute("DROP TYPE IF EXISTS inventorycheckstatusdb")
    op.execute("DROP TYPE IF EXISTS batchstatusdb")
    op.execute("DROP TYPE IF EXISTS serialstatusdb")
    op.execute("DROP TYPE IF EXISTS adjustmenttypedb")
    op.execute("DROP TYPE IF EXISTS transferstatusdb")
