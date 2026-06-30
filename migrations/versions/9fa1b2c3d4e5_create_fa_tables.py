"""create_fa_tables

Revision ID: 9fa1b2c3d4e5
Revises: 8e9f0a1b2c3d
Create Date: 2026-06-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9fa1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = '8e9f0a1b2c3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('fa_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('asset_type', sa.Enum('tangible', 'intangible', 'finance_lease', 'biological', 'investment_property', name='assettypedb'), nullable=False),
        sa.Column('asset_classification', sa.Enum('buildings_structures', 'machinery_equipment', 'transport_transmission', 'management_equipment', 'perennial_plants_livestock', 'soe_infrastructure', 'other', name='assetclassificationdb'), nullable=False),
        sa.Column('default_depreciation_method', sa.Enum('straight_line', 'declining_balance', 'units_of_production', name='depreciationmethoddb'), nullable=False),
        sa.Column('default_useful_life_min', sa.Integer(), nullable=False),
        sa.Column('default_useful_life_max', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_fa_categories_code', 'fa_categories', ['code'])

    op.create_table('fa_assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('asset_type', sa.Enum('tangible', 'intangible', 'finance_lease', 'biological', 'investment_property', name='assettypedb'), nullable=False),
        sa.Column('asset_classification', sa.Enum('buildings_structures', 'machinery_equipment', 'transport_transmission', 'management_equipment', 'perennial_plants_livestock', 'soe_infrastructure', 'other', name='assetclassificationdb'), nullable=False),
        sa.Column('original_cost', sa.Numeric(18, 2), nullable=False),
        sa.Column('accumulated_depreciation', sa.Numeric(18, 2), nullable=False),
        sa.Column('residual_value', sa.Numeric(18, 2), nullable=False),
        sa.Column('useful_life_months', sa.Integer(), nullable=False),
        sa.Column('depreciation_method', sa.Enum('straight_line', 'declining_balance', 'units_of_production', name='depreciationmethoddb'), nullable=False),
        sa.Column('acquisition_date', sa.Date(), nullable=False),
        sa.Column('in_use_date', sa.Date(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('status', sa.Enum('active', 'suspended', 'fully_depreciated', 'disposed', 'held_for_sale', name='assetstatusdb'), nullable=False),
        sa.Column('fund_source', sa.Enum('owners_equity', 'loan', 'government_grant', 'welfare_fund', 'rd_fund', 'capital_construction', 'other', name='fundsourcedb'), nullable=False),
        sa.Column('use_type', sa.Enum('production', 'administration', 'selling', 'construction', 'welfare', 'rd', name='usetypedb'), nullable=False),
        sa.Column('supplier', sa.String(length=300), nullable=True),
        sa.Column('invoice_ref', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_foreign_key('fk_asset_category', 'fa_assets', 'fa_categories', ['category_id'], ['id'])
    op.create_index('ix_fa_assets_code', 'fa_assets', ['code'])
    op.create_index('ix_fa_assets_category', 'fa_assets', ['category_id'])
    op.create_index('ix_fa_assets_department', 'fa_assets', ['department_id'])
    op.create_index('ix_fa_assets_status', 'fa_assets', ['status'])

    op.create_table('fa_depreciation_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('depreciation_amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('accumulated_total', sa.Numeric(18, 2), nullable=True),
        sa.Column('nbv', sa.Numeric(18, 2), nullable=True),
        sa.Column('is_posted', sa.Boolean(), nullable=False),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_id', 'period'),
    )
    op.create_foreign_key('fk_depreciation_asset', 'fa_depreciation_records', 'fa_assets', ['asset_id'], ['id'])
    op.create_index('ix_fa_depreciation_period', 'fa_depreciation_records', ['period'])
    op.create_index('ix_fa_depreciation_asset_period', 'fa_depreciation_records', ['asset_id', 'period'])

    op.create_table('fa_adjustments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('adjustment_type', sa.Enum('upgrade', 'partial_dismantle', 'cost_correction', 'impairment', 'revaluation', name='adjustmenttypedb'), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('previous_cost', sa.Numeric(18, 2), nullable=True),
        sa.Column('new_cost', sa.Numeric(18, 2), nullable=True),
        sa.Column('previous_depreciation', sa.Numeric(18, 2), nullable=True),
        sa.Column('new_depreciation', sa.Numeric(18, 2), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('document_ref', sa.String(length=100), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('appraised_by', sa.String(length=100), nullable=True),
        sa.Column('appraisal_date', sa.Date(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('fk_adjustment_asset', 'fa_adjustments', 'fa_assets', ['asset_id'], ['id'])

    op.create_table('fa_disposals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('disposal_type', sa.Enum('sale', 'liquidation', 'donation', 'theft', 'destruction', name='disposaltypedb'), nullable=False),
        sa.Column('disposal_date', sa.Date(), nullable=False),
        sa.Column('proceeds', sa.Numeric(18, 2), nullable=True),
        sa.Column('costs', sa.Numeric(18, 2), nullable=True),
        sa.Column('nbv_at_disposal', sa.Numeric(18, 2), nullable=True),
        sa.Column('gain_loss', sa.Numeric(18, 2), nullable=True),
        sa.Column('buyer_info', sa.String(length=500), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('document_ref', sa.String(length=100), nullable=True),
        sa.Column('is_vat_applied', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('fk_disposal_asset', 'fa_disposals', 'fa_assets', ['asset_id'], ['id'])

    op.create_table('fa_inventories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('inventory_date', sa.Date(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('asset_count_book', sa.Integer(), nullable=False),
        sa.Column('asset_count_physical', sa.Integer(), nullable=False),
        sa.Column('surplus_count', sa.Integer(), nullable=False),
        sa.Column('deficit_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('open', 'resolved', 'cancelled', name='inventorystatusdb'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('fa_inventory_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('inventory_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('book_quantity', sa.Integer(), nullable=False),
        sa.Column('physical_quantity', sa.Integer(), nullable=False),
        sa.Column('difference', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('resolution', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('fk_invline_inventory', 'fa_inventory_lines', 'fa_inventories', ['inventory_id'], ['id'])
    op.create_foreign_key('fk_invline_asset', 'fa_inventory_lines', 'fa_assets', ['asset_id'], ['id'])

    op.create_table('fa_transfers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('from_department_id', sa.Integer(), nullable=True),
        sa.Column('to_department_id', sa.Integer(), nullable=True),
        sa.Column('from_location', sa.String(length=200), nullable=True),
        sa.Column('to_location', sa.String(length=200), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('fk_transfer_asset', 'fa_transfers', 'fa_assets', ['asset_id'], ['id'])

    op.create_table('fa_spare_parts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('value', sa.Numeric(18, 2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('fk_sparepart_asset', 'fa_spare_parts', 'fa_assets', ['asset_id'], ['id'])

    op.create_table('fa_components',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('original_cost', sa.Numeric(18, 2), nullable=True),
        sa.Column('useful_life_months', sa.Integer(), nullable=True),
        sa.Column('depreciation_method', sa.Enum('straight_line', 'declining_balance', 'units_of_production', name='depreciationmethoddb'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('fk_component_asset', 'fa_components', 'fa_assets', ['asset_id'], ['id'])

    op.create_table('fa_biological_assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('biological_type', sa.Enum('periodic_producer_long_term', 'one_time_product', 'seasonal_crop', name='biologicaltypedb'), nullable=False),
        sa.Column('growth_stage', sa.Enum('immature', 'mature', name='growthstagedb'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('planting_date', sa.Date(), nullable=False),
        sa.Column('expected_harvest_date', sa.Date(), nullable=True),
        sa.Column('provision_amount', sa.Numeric(18, 2), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('fk_bio_asset', 'fa_biological_assets', 'fa_assets', ['asset_id'], ['id'])
    op.create_index('ix_fa_biological_assets_type', 'fa_biological_assets', ['biological_type'])

    op.create_table('fa_biological_provisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('biological_asset_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=True),
        sa.Column('provision_amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('provision_type', sa.Enum('new', 'reversal', name='provisiontypedb'), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('fk_bio_provision', 'fa_biological_provisions', 'fa_biological_assets', ['biological_asset_id'], ['id'])


def downgrade() -> None:
    op.drop_table('fa_biological_provisions')
    op.drop_table('fa_biological_assets')
    op.drop_table('fa_components')
    op.drop_table('fa_spare_parts')
    op.drop_table('fa_transfers')
    op.drop_table('fa_inventory_lines')
    op.drop_table('fa_inventories')
    op.drop_table('fa_disposals')
    op.drop_table('fa_adjustments')
    op.drop_table('fa_depreciation_records')
    op.drop_table('fa_assets')
    op.drop_table('fa_categories')
    op.execute('DROP TYPE IF EXISTS assettypedb')
    op.execute('DROP TYPE IF EXISTS assetclassificationdb')
    op.execute('DROP TYPE IF EXISTS depreciationmethoddb')
    op.execute('DROP TYPE IF EXISTS assetstatusdb')
    op.execute('DROP TYPE IF EXISTS fundsourcedb')
    op.execute('DROP TYPE IF EXISTS usetypedb')
    op.execute('DROP TYPE IF EXISTS adjustmenttypedb')
    op.execute('DROP TYPE IF EXISTS disposaltypedb')
    op.execute('DROP TYPE IF EXISTS inventorystatusdb')
    op.execute('DROP TYPE IF EXISTS biologicaltypedb')
    op.execute('DROP TYPE IF EXISTS growthstagedb')
    op.execute('DROP TYPE IF EXISTS provisiontypedb')
