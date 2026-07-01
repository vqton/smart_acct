"""create approval workflow tables

Revision ID: d3e4f5g6h7i8
Revises: f5a6b7c8d9e2
Create Date: 2026-07-01 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd3e4f5g6h7i8'
down_revision: Union[str, None] = 'f5a6b7c8d9e2'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table('approval_workflows',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('object_type', sa.String(length=50), nullable=False),
        sa.Column('strategy', sa.String(length=20), nullable=False, server_default='sequential'),
        sa.Column('quorum_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_workflows_object_type', 'approval_workflows', ['object_type'])

    op.create_table('approval_steps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('workflow_id', sa.Integer(),
                  sa.ForeignKey('approval_workflows.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(length=200), nullable=False),
        sa.Column('approver_role', sa.String(length=100), nullable=True),
        sa.Column('approver_user_id', sa.Integer(), nullable=True),
        sa.Column('min_amount', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('max_amount', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_steps_workflow_id', 'approval_steps', ['workflow_id'])
    op.create_index('ix_approval_steps_workflow_order', 'approval_steps', ['workflow_id', 'step_order'])

    op.create_table('approval_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('workflow_id', sa.Integer(),
                  sa.ForeignKey('approval_workflows.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('object_type', sa.String(length=50), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('object_reference', sa.String(length=200), nullable=True),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('submitted_by', sa.Integer(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('current_step_order', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_requests_object_type', 'approval_requests', ['object_type'])
    op.create_index('ix_approval_requests_object', 'approval_requests', ['object_type', 'object_id'])
    op.create_index('ix_approval_requests_status', 'approval_requests', ['status'])
    op.create_index('ix_approval_requests_submitted_by', 'approval_requests', ['submitted_by'])

    op.create_table('approval_actions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('request_id', sa.Integer(),
                  sa.ForeignKey('approval_requests.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('step_id', sa.Integer(),
                  sa.ForeignKey('approval_steps.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('acted_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('delegate_from', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_actions_request_step', 'approval_actions', ['request_id', 'step_order'])
    op.create_index('ix_approval_actions_approver', 'approval_actions', ['approver_id'])

    op.create_table('approval_delegates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('delegate_to', sa.Integer(), nullable=False),
        sa.Column('object_type', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_delegates_user_id', 'approval_delegates', ['user_id'])
    op.create_index('ix_approval_delegates_delegate_to', 'approval_delegates', ['delegate_to'])


def downgrade() -> None:
    op.drop_table('approval_delegates')
    op.drop_table('approval_actions')
    op.drop_table('approval_requests')
    op.drop_table('approval_steps')
    op.drop_table('approval_workflows')
