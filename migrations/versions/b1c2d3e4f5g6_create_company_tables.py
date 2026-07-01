"""create company tables (company, fiscal_years, numbering_rules, setup_checklist)

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2026-07-01 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table('companies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('tax_code', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('business_reg_number', sa.String(length=50), nullable=True),
        sa.Column('date_format', sa.String(length=20), nullable=False, server_default='DD/MM/YYYY'),
        sa.Column('currency_code', sa.String(length=3), nullable=False, server_default='VND'),
        sa.Column('fiscal_year_start_month', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('accounting_regime', sa.String(length=10), nullable=False, server_default='TT99'),
        sa.Column('locale', sa.String(length=10), nullable=False, server_default='vi'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('company_fiscal_years',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'fiscal_year', name='uq_company_fiscal_year'),
    )
    op.create_index('ix_fiscal_year_company', 'company_fiscal_years', ['company_id', 'fiscal_year'])
    op.create_index('ix_company_fiscal_years_company_id', 'company_fiscal_years', ['company_id'])

    op.create_table('company_numbering_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('document_type', sa.Enum(
            'ar_invoice', 'ap_invoice', 'cash_receipt', 'cash_payment',
            'journal_entry', 'purchase_order', 'sales_order',
            'inventory_receipt', 'inventory_issue', 'payment', 'receipt',
            name='compdocumenttypedb',
        ), nullable=False),
        sa.Column('prefix', sa.String(length=10), nullable=False, server_default=''),
        sa.Column('suffix', sa.String(length=10), nullable=False, server_default=''),
        sa.Column('next_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('pad_length', sa.Integer(), nullable=False, server_default='6'),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'document_type', 'fiscal_year',
                            name='uq_company_doc_type_fiscal_year'),
    )
    op.create_index('ix_numbering_rule_company', 'company_numbering_rules',
                    ['company_id', 'document_type', 'fiscal_year'])
    op.create_index('ix_company_numbering_rules_company_id', 'company_numbering_rules', ['company_id'])

    op.create_table('company_setup_checklist',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('section', sa.Enum(
            'company_info', 'fiscal_year', 'currency', 'coa',
            'opening_balances', 'departments', 'warehouses',
            'employees', 'customers', 'vendors',
            'tax_rates', 'numbering_rules', 'user_permissions',
            name='setupsectiondb',
        ), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'section', name='uq_company_setup_section'),
    )
    op.create_index('ix_setup_checklist_company', 'company_setup_checklist',
                    ['company_id', 'section'])
    op.create_index('ix_company_setup_checklist_company_id', 'company_setup_checklist', ['company_id'])


def downgrade() -> None:
    op.drop_table('company_setup_checklist')
    op.drop_table('company_numbering_rules')
    op.drop_table('company_fiscal_years')
    op.drop_table('companies')

    op.execute('DROP TYPE IF EXISTS compdocumenttypedb')
    op.execute('DROP TYPE IF EXISTS setupsectiondb')
