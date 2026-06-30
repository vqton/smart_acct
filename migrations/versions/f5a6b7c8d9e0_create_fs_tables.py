"""create_fs_tables

Revision ID: f5a6b7c8d9e0
Revises: 3fa4b5c6d7e8
Create Date: 2026-06-30 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision: str = 'f5a6b7c8d9e0'
down_revision: Union[str, None] = '3fa4b5c6d7e8'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table('fs_statements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('statement_type', sa.Enum(
            'B01_DN', 'B01_DNKLT', 'B02_DN', 'B02_DNKLT',
            'B03_DN', 'B03_DNKLT', 'B09_DN', 'B09_DNKLT',
            'B01a_DN', 'B02a_DN', 'B03a_DN', 'B09a_DN',
            'B01b_DN', 'B02b_DN', 'B03b_DN',
            name='fsstatementtypedb',
        ), nullable=False),
        sa.Column('status', sa.Enum(
            'DRAFT', 'IN_REVIEW', 'REVIEWED', 'APPROVED', 'SIGNED',
            'REJECTED', 'AMENDED',
            name='fsstatusdb',
        ), nullable=False, server_default='DRAFT'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('cash_flow_method', sa.Enum(
            'DIRECT', 'INDIRECT',
            name='fscashflowmethoddb',
        ), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approval_date', sa.Date(), nullable=True),
        sa.Column('signed_by', sa.String(length=100), nullable=True),
        sa.Column('signed_date', sa.Date(), nullable=True),
        sa.Column('generated_by', sa.String(length=100), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('is_consolidated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('consolidation_group_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fs_entity_period_type', 'fs_statements',
                    ['entity_id', 'period', 'statement_type'])
    op.create_index('ix_fs_status', 'fs_statements', ['status'])
    op.create_index('ix_fs_period', 'fs_statements', ['period'])

    op.create_table('fs_line_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fs_id', sa.Integer(), sa.ForeignKey('fs_statements.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('ma_so', sa.String(length=10), nullable=False),
        sa.Column('ten_chi_tieu', sa.String(length=500), nullable=False),
        sa.Column('so_thu_tu', sa.Integer(), nullable=False),
        sa.Column('parent_ma_so', sa.String(length=10), nullable=True),
        sa.Column('current_year', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('previous_year', sa.Numeric(18, 2), nullable=True),
        sa.Column('is_subtotal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_calculated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('calculation_formula', sa.String(length=200), nullable=True),
        sa.Column('thuyet_minh', sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fs_line_fs_id', 'fs_line_items', ['fs_id'])
    op.create_index('ix_fs_line_ma_so', 'fs_line_items', ['fs_id', 'ma_so'])

    op.create_table('fs_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fs_id', sa.Integer(), sa.ForeignKey('fs_statements.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('user', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fs_audit_fs_id', 'fs_audit_logs', ['fs_id'])

    op.create_table('fs_account_mappings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fs_ma_so', sa.String(length=10), nullable=False),
        sa.Column('account_code', sa.String(length=20), nullable=False),
        sa.Column('weight', sa.Numeric(5, 2), nullable=False, server_default='1.00'),
        sa.Column('direction', sa.String(length=10), nullable=False, server_default='both'),
        sa.Column('statement_type', sa.Enum(
            'B01_DN', 'B01_DNKLT', 'B02_DN', 'B02_DNKLT',
            'B03_DN', 'B03_DNKLT', 'B09_DN', 'B09_DNKLT',
            'B01a_DN', 'B02a_DN', 'B03a_DN', 'B09a_DN',
            'B01b_DN', 'B02b_DN', 'B03b_DN',
            name='fsstatementtypedb',
        ), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fs_mapping_account', 'fs_account_mappings', ['account_code'])
    op.create_unique_constraint('uq_fs_mapping', 'fs_account_mappings',
                                ['account_code', 'fs_ma_so', 'statement_type'])

    op.create_table('fs_consolidation_groups',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('parent_entity_id', sa.Integer(), nullable=False),
        sa.Column('consolidation_method', sa.String(length=20), nullable=False,
                  server_default='full'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('fs_consolidation_members',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('fs_consolidation_groups.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('ownership_percentage', sa.Numeric(5, 2), nullable=False, server_default='100.00'),
        sa.Column('consolidation_method', sa.String(length=20), nullable=False,
                  server_default='full'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('fs_consolidation_members')
    op.drop_table('fs_consolidation_groups')
    op.drop_table('fs_account_mappings')
    op.drop_table('fs_audit_logs')
    op.drop_table('fs_line_items')
    op.drop_table('fs_statements')

    op.execute('DROP TYPE IF EXISTS fsstatementtypedb')
    op.execute('DROP TYPE IF EXISTS fsstatusdb')
    op.execute('DROP TYPE IF EXISTS fscashflowmethoddb')
