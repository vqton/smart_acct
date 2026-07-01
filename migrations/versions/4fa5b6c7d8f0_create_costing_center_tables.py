"""create_costing_center_tables

Revision ID: 4fa5b6c7d8f0
Revises: 3fa4b5c6d7e9
Create Date: 2026-06-30 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4fa5b6c7d8f0'
down_revision: Union[str, Sequence[str], None] = '3fa4b5c6d7e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cost_centers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('name_en', sa.String(length=200), nullable=True),
        sa.Column('cost_center_type', sa.Enum('COST', 'PROFIT', 'INVESTMENT', 'SERVICE', 'ADMIN', 'SELLING', 'PRODUCTION', 'PROJECT', 'VIRTUAL', name='costcentertypedb'), nullable=False),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('path', sa.String(length=500), nullable=False, server_default=''),
        sa.Column('manager_employee_id', sa.Integer(), nullable=True),
        sa.Column('gl_account_code', sa.String(length=20), nullable=True),
        sa.Column('department_code', sa.String(length=50), nullable=True),
        sa.Column('is_cost_collector', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('valid_from', sa.Date(), nullable=False),
        sa.Column('valid_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cost_centers_code', 'cost_centers', ['code'])
    op.create_index('ix_cost_centers_parent_id', 'cost_centers', ['parent_id'])

    op.create_table('cost_drivers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('driver_type', sa.Enum('QUANTITY', 'PERCENTAGE', 'RATE', 'ACTUAL', name='drivertypedb'), nullable=False),
        sa.Column('source_module', sa.String(length=50), nullable=True),
        sa.Column('source_account_code', sa.String(length=20), nullable=True),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=True),
        sa.Column('formula', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_cost_drivers_code', 'cost_drivers', ['code'])

    op.create_table('cost_allocation_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rule_code', sa.String(length=20), nullable=False),
        sa.Column('rule_name', sa.String(length=200), nullable=False),
        sa.Column('source_cost_center_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=False),
        sa.Column('driver_id', sa.Integer(), sa.ForeignKey('cost_drivers.id'), nullable=True),
        sa.Column('allocation_method', sa.Enum('DIRECT', 'PERCENTAGE', 'PROPORTIONAL', name='allocationmethoddb_cc'), nullable=False),
        sa.Column('gl_debit_account_code', sa.String(length=20), nullable=False),
        sa.Column('gl_credit_account_code', sa.String(length=20), nullable=False),
        sa.Column('priority_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('approval_status', sa.Enum('DRAFT', 'PENDING', 'APPROVED', 'REJECTED', 'ARCHIVED', name='ruleapprovalstatusdb'), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rule_code'),
    )
    op.create_index('ix_cost_allocation_rules_rule_code', 'cost_allocation_rules', ['rule_code'])

    op.create_table('cost_allocation_rule_targets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rule_id', sa.Integer(), sa.ForeignKey('cost_allocation_rules.id'), nullable=False),
        sa.Column('target_cost_center_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=False),
        sa.Column('percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rule_id', 'target_cost_center_id', name='uq_rule_target'),
    )

    op.create_table('cost_allocation_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_code', sa.String(length=30), nullable=False),
        sa.Column('period_key', sa.String(length=6), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=False),
        sa.Column('run_date', sa.DateTime(), nullable=False),
        sa.Column('run_by', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'POSTED', 'REVERSED', name='allocationrunstatusdb'), nullable=False),
        sa.Column('total_allocated_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_code'),
    )
    op.create_index('ix_cost_allocation_runs_period_key', 'cost_allocation_runs', ['period_key'])

    op.create_table('cost_allocation_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_id', sa.Integer(), sa.ForeignKey('cost_allocation_runs.id'), nullable=False),
        sa.Column('source_cost_center_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=False),
        sa.Column('target_cost_center_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=False),
        sa.Column('rule_id', sa.Integer(), sa.ForeignKey('cost_allocation_rules.id'), nullable=True),
        sa.Column('driver_id', sa.Integer(), sa.ForeignKey('cost_drivers.id'), nullable=True),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('original_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('allocated_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('driver_quantity', sa.Numeric(18, 2), nullable=True),
        sa.Column('driver_rate', sa.Numeric(18, 2), nullable=True),
        sa.Column('allocation_basis_description', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('cost_objects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('object_type', sa.Enum('PRODUCT', 'PROJECT', 'SALES_ORDER', 'CAMPAIGN', 'CUSTOMER', 'DEPARTMENT', name='costobjecttypedb'), nullable=False),
        sa.Column('parent_object_id', sa.Integer(), sa.ForeignKey('cost_objects.id'), nullable=True),
        sa.Column('gl_account_code', sa.String(length=20), nullable=True),
        sa.Column('external_ref_id', sa.Integer(), nullable=True),
        sa.Column('external_ref_type', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('custom_attributes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_cost_objects_code', 'cost_objects', ['code'])

    op.create_table('cost_accumulations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cost_object_id', sa.Integer(), sa.ForeignKey('cost_objects.id'), nullable=False),
        sa.Column('cost_center_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=False),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('period_key', sa.String(length=6), nullable=False),
        sa.Column('direct_cost_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('allocated_cost_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('source_type', sa.String(length=20), nullable=True),
        sa.Column('source_reference', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cost_object_id', 'cost_center_id', 'gl_account_code', 'period_key', name='uq_cost_acc'),
    )

    op.create_table('cost_center_budgets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cost_center_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('period_key', sa.String(length=6), nullable=False),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('budget_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('revised_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('budget_version_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cost_center_id', 'period_key', 'gl_account_code', name='uq_cost_budget'),
    )

    op.create_table('cost_center_actuals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cost_center_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=False),
        sa.Column('period_key', sa.String(length=6), nullable=False),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('actual_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('commitment_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('allocated_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('source_reference', sa.String(length=100), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cost_center_id', 'period_key', 'gl_account_code', name='uq_cost_actual'),
    )

    op.create_table('cost_center_variances',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cost_center_id', sa.Integer(), sa.ForeignKey('cost_centers.id'), nullable=False),
        sa.Column('period_key', sa.String(length=6), nullable=False),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('budget_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('actual_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('variance_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('variance_type', sa.Enum('FAVORABLE', 'UNFAVORABLE', 'NEUTRAL', name='variancetypedb'), nullable=True),
        sa.Column('annotation', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cost_center_id', 'period_key', 'gl_account_code', name='uq_cost_variance'),
    )

    op.create_table('costing_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(length=30), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=30), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_costing_audit_logs_entity', 'costing_audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_costing_audit_logs_created_at', 'costing_audit_logs', ['created_at'])


def downgrade() -> None:
    op.drop_table('costing_audit_logs')
    op.drop_table('cost_center_variances')
    op.drop_table('cost_center_actuals')
    op.drop_table('cost_center_budgets')
    op.drop_table('cost_accumulations')
    op.drop_table('cost_objects')
    op.drop_table('cost_allocation_lines')
    op.drop_table('cost_allocation_runs')
    op.drop_table('cost_allocation_rule_targets')
    op.drop_table('cost_allocation_rules')
    op.drop_table('cost_drivers')
    op.drop_table('cost_centers')
