"""create budget module tables (structure, dimensions, calendar,
templates, versions, plans, approvals, adjustments, control, consolidation, audit)

Revision ID: 4fa5b6c7d8e9
Revises: 3fa4b5c6d7e8
Create Date: 2026-06-30 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
import sqlalchemy.types as types

revision: str = '4fa5b6c7d8e9'
down_revision: Union[str, Sequence[str], None] = '3fa4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── budget_structures ────────────────────────────────────────────
    op.create_table('budget_structures',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('budget_types', JSON, nullable=False),
        sa.Column('dimensions', JSON, nullable=False),
        sa.Column('period_type', sa.String(length=20), server_default='monthly'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_structures_fy', 'budget_structures', ['fiscal_year'])

    # ── budget_dimensions ────────────────────────────────────────────
    op.create_table('budget_dimensions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('structure_id', sa.Integer(), sa.ForeignKey('budget_structures.id'), nullable=False),
        sa.Column('dimension_type', sa.String(length=50), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_dimensions_structure', 'budget_dimensions', ['structure_id', 'dimension_type', 'code'], unique=True)

    # ── budget_categories ─────────────────────────────────────────────
    op.create_table('budget_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('structure_id', sa.Integer(), sa.ForeignKey('budget_structures.id'), nullable=False),
        sa.Column('budget_type', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category_type', sa.String(length=20), server_default='variable'),
        sa.Column('gl_account_codes', JSON, nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_calendars ──────────────────────────────────────────────
    op.create_table('budget_calendars',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False, unique=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_calendars_fy', 'budget_calendars', ['fiscal_year'])

    # ── budget_calendar_phases ─────────────────────────────────────────
    op.create_table('budget_calendar_phases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('calendar_id', sa.Integer(), sa.ForeignKey('budget_calendars.id'), nullable=False),
        sa.Column('phase_name', sa.String(length=200), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('phase_order', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_periods ────────────────────────────────────────────────
    op.create_table('budget_periods',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('calendar_id', sa.Integer(), sa.ForeignKey('budget_calendars.id'), nullable=False),
        sa.Column('period_key', sa.String(length=20), nullable=False),
        sa.Column('period_type', sa.String(length=20), server_default='monthly'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_open', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_periods_calendar_key', 'budget_periods', ['calendar_id', 'period_key'], unique=True)

    # ── budget_versions ───────────────────────────────────────────────
    op.create_table('budget_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.String(length=20), nullable=False),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='draft'),
        sa.Column('parent_version_id', sa.Integer(), sa.ForeignKey('budget_versions.id'), nullable=True),
        sa.Column('is_locked', sa.Boolean(), server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_versions_fy_status', 'budget_versions', ['fiscal_year', 'status'])

    # ── budget_templates ──────────────────────────────────────────────
    op.create_table('budget_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('budget_type', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_template_lines ─────────────────────────────────────────
    op.create_table('budget_template_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('template_id', sa.Integer(), sa.ForeignKey('budget_templates.id'), nullable=False),
        sa.Column('line_order', sa.Integer(), server_default='0'),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category_type', sa.String(length=20), server_default='variable'),
        sa.Column('formula', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), server_default='false'),
        sa.Column('default_amount', sa.Numeric(18, 2), server_default='0'),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_template_lines_template', 'budget_template_lines', ['template_id', 'line_order'])

    # ── budget_plans ──────────────────────────────────────────────────
    op.create_table('budget_plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('version_id', sa.Integer(), sa.ForeignKey('budget_versions.id'), nullable=False),
        sa.Column('structure_id', sa.Integer(), sa.ForeignKey('budget_structures.id'), nullable=False),
        sa.Column('dimension_type', sa.String(length=50), nullable=False),
        sa.Column('dimension_code', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_plans_version_dim', 'budget_plans', ['version_id', 'dimension_type', 'dimension_code'])

    # ── budget_plan_lines ─────────────────────────────────────────────
    op.create_table('budget_plan_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('budget_plans.id'), nullable=False),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category_type', sa.String(length=20), server_default='variable'),
        sa.Column('amounts', JSON, nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_plan_drivers ───────────────────────────────────────────
    op.create_table('budget_plan_drivers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plan_line_id', sa.Integer(), sa.ForeignKey('budget_plan_lines.id'), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 2), server_default='0'),
        sa.Column('unit_rate', sa.Numeric(18, 2), server_default='0'),
        sa.Column('driver_name', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_approval_workflows ─────────────────────────────────────
    op.create_table('budget_approval_workflows',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('budget_plans.id'), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_approval_steps ─────────────────────────────────────────
    op.create_table('budget_approval_steps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('workflow_id', sa.Integer(), sa.ForeignKey('budget_approval_workflows.id'), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('approver_role', sa.String(length=100), nullable=False),
        sa.Column('approver_name', sa.String(length=200), nullable=True),
        sa.Column('min_approvers', sa.Integer(), server_default='1'),
        sa.Column('status', sa.String(length=30), server_default='pending'),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('acted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_approval_logs ──────────────────────────────────────────
    op.create_table('budget_approval_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('workflow_id', sa.Integer(), sa.ForeignKey('budget_approval_workflows.id'), nullable=False),
        sa.Column('step_id', sa.Integer(), sa.ForeignKey('budget_approval_steps.id'), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('actor', sa.String(length=200), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_adjustments ────────────────────────────────────────────
    op.create_table('budget_adjustments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('version_id', sa.Integer(), sa.ForeignKey('budget_versions.id'), nullable=False),
        sa.Column('adjustment_type', sa.String(length=30), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='pending'),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_adjustment_lines ───────────────────────────────────────
    op.create_table('budget_adjustment_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('adjustment_id', sa.Integer(), sa.ForeignKey('budget_adjustments.id'), nullable=False),
        sa.Column('source_plan_line_id', sa.Integer(), sa.ForeignKey('budget_plan_lines.id'), nullable=True),
        sa.Column('target_plan_line_id', sa.Integer(), sa.ForeignKey('budget_plan_lines.id'), nullable=True),
        sa.Column('amount', sa.Numeric(18, 2), server_default='0'),
        sa.Column('period_key', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_commitments ────────────────────────────────────────────
    op.create_table('budget_commitments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plan_line_id', sa.Integer(), sa.ForeignKey('budget_plan_lines.id'), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), server_default='0'),
        sa.Column('period_key', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_commitments_source', 'budget_commitments', ['source_type', 'source_id'])

    # ── budget_control_rules ──────────────────────────────────────────
    op.create_table('budget_control_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('structure_id', sa.Integer(), sa.ForeignKey('budget_structures.id'), nullable=False),
        sa.Column('gl_account_code', sa.String(length=20), nullable=True),
        sa.Column('dimension_type', sa.String(length=50), nullable=True),
        sa.Column('dimension_code', sa.String(length=50), nullable=True),
        sa.Column('control_level', sa.String(length=20), server_default='hard_block'),
        sa.Column('warning_threshold_pct', sa.Numeric(5, 2), server_default='80'),
        sa.Column('soft_block_threshold_pct', sa.Numeric(5, 2), server_default='90'),
        sa.Column('hard_block_threshold_pct', sa.Numeric(5, 2), server_default='100'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_overrides ──────────────────────────────────────────────
    op.create_table('budget_overrides',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('control_rule_id', sa.Integer(), sa.ForeignKey('budget_control_rules.id'), nullable=False),
        sa.Column('override_code', sa.String(length=20), nullable=False),
        sa.Column('requested_by', sa.String(length=100), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_block_logs ─────────────────────────────────────────────
    op.create_table('budget_block_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('control_rule_id', sa.Integer(), sa.ForeignKey('budget_control_rules.id'), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('dimension_code', sa.String(length=50), nullable=True),
        sa.Column('attempted_amount', sa.Numeric(18, 2), server_default='0'),
        sa.Column('utilization_pct', sa.Numeric(5, 2), server_default='0'),
        sa.Column('control_level', sa.String(length=20), nullable=False),
        sa.Column('was_blocked', sa.Boolean(), server_default='true'),
        sa.Column('override_id', sa.Integer(), sa.ForeignKey('budget_overrides.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_consolidations ─────────────────────────────────────────
    op.create_table('budget_consolidations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('parent_entity_code', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_consolidation_entities ─────────────────────────────────
    op.create_table('budget_consolidation_entities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('consolidation_id', sa.Integer(), sa.ForeignKey('budget_consolidations.id'), nullable=False),
        sa.Column('entity_code', sa.String(length=50), nullable=False),
        sa.Column('entity_name', sa.String(length=200), nullable=False),
        sa.Column('version_id', sa.Integer(), sa.ForeignKey('budget_versions.id'), nullable=False),
        sa.Column('fx_rate', sa.Numeric(10, 4), server_default='1'),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_ic_transactions ────────────────────────────────────────
    op.create_table('budget_ic_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('consolidation_id', sa.Integer(), sa.ForeignKey('budget_consolidations.id'), nullable=False),
        sa.Column('from_entity_code', sa.String(length=50), nullable=False),
        sa.Column('to_entity_code', sa.String(length=50), nullable=False),
        sa.Column('gl_account_code', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── budget_audit_logs ─────────────────────────────────────────────
    op.create_table('budget_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('changes', JSON, nullable=True),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_budget_audit_logs_entity', 'budget_audit_logs', ['entity_type', 'entity_id'])


def downgrade() -> None:
    op.drop_table('budget_audit_logs')
    op.drop_table('budget_ic_transactions')
    op.drop_table('budget_consolidation_entities')
    op.drop_table('budget_consolidations')
    op.drop_table('budget_block_logs')
    op.drop_table('budget_overrides')
    op.drop_table('budget_control_rules')
    op.drop_table('budget_commitments')
    op.drop_table('budget_adjustment_lines')
    op.drop_table('budget_adjustments')
    op.drop_table('budget_approval_logs')
    op.drop_table('budget_approval_steps')
    op.drop_table('budget_approval_workflows')
    op.drop_table('budget_plan_drivers')
    op.drop_table('budget_plan_lines')
    op.drop_table('budget_plans')
    op.drop_table('budget_template_lines')
    op.drop_table('budget_templates')
    op.drop_table('budget_versions')
    op.drop_table('budget_periods')
    op.drop_table('budget_calendar_phases')
    op.drop_table('budget_calendars')
    op.drop_table('budget_categories')
    op.drop_table('budget_dimensions')
    op.drop_table('budget_structures')
