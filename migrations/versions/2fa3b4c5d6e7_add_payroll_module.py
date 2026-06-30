"""add payroll module (employees, contracts, timesheets, payroll_runs,
lines, adjustments, pit, si, payments, allocations, audit)

Revision ID: 2fa3b4c5d6e7
Revises: 1fa2b3c4d5e6
Create Date: 2026-06-30 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2fa3b4c5d6e7'
down_revision: Union[str, Sequence[str], None] = '1fa2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── employees ────────────────────────────────────────────────────
    op.create_table('employees',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_code', sa.String(length=20), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('id_number', sa.String(length=20), nullable=True),
        sa.Column('id_issue_date', sa.Date(), nullable=True),
        sa.Column('id_issue_place', sa.String(length=100), nullable=True),
        sa.Column('tax_code', sa.String(length=20), nullable=True),
        sa.Column('si_book_number', sa.String(length=50), nullable=True),
        sa.Column('bank_account', sa.String(length=50), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('department_name', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=20), nullable=False, server_default='region_1'),
        sa.Column('dependent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='active'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_code'),
        sa.UniqueConstraint('si_book_number'),
    )
    op.create_index('ix_employees_tax_code', 'employees', ['tax_code'])

    # ── employee_contracts ────────────────────────────────────────────
    op.create_table('employee_contracts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('contract_type', sa.String(length=30), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('base_salary', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('position_allowance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('meal_allowance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('phone_allowance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('transport_allowance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('housing_allowance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('responsibility_allowance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('other_allowance', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_employee_contracts_employee_id', 'employee_contracts', ['employee_id'])

    # ── employee_dependents ───────────────────────────────────────────
    op.create_table('employee_dependents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('relationship', sa.String(length=50), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('tax_code', sa.String(length=20), nullable=True),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_employee_dependents_employee_id', 'employee_dependents', ['employee_id'])

    # ── timesheets ────────────────────────────────────────────────────
    op.create_table('timesheets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=False),
        sa.Column('period_year', sa.Integer(), nullable=False),
        sa.Column('working_days', sa.Numeric(5, 1), nullable=False, server_default='0'),
        sa.Column('standard_days', sa.Numeric(5, 1), nullable=False, server_default='26'),
        sa.Column('overtime_weekday_hours', sa.Numeric(8, 1), nullable=False, server_default='0'),
        sa.Column('overtime_weekend_hours', sa.Numeric(8, 1), nullable=False, server_default='0'),
        sa.Column('overtime_holiday_hours', sa.Numeric(8, 1), nullable=False, server_default='0'),
        sa.Column('sick_leave_days', sa.Numeric(5, 1), nullable=False, server_default='0'),
        sa.Column('unpaid_leave_days', sa.Numeric(5, 1), nullable=False, server_default='0'),
        sa.Column('paid_leave_days', sa.Numeric(5, 1), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'period_month', 'period_year',
                            name='uq_timesheet_employee_period'),
    )
    op.create_index('ix_timesheets_employee_id', 'timesheets', ['employee_id'])
    op.create_index('ix_timesheets_period', 'timesheets', ['period_month', 'period_year'])

    # ── payroll_runs ──────────────────────────────────────────────────
    op.create_table('payroll_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=False),
        sa.Column('period_year', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='draft'),
        sa.Column('total_gross', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employee_si', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employee_hi', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employee_ui', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_pit', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_advances', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_other_deductions', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_net', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_si', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_hi', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_ui', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_occ', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_kpcd', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('computed_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period_month', 'period_year',
                            name='uq_payroll_run_period'),
    )
    op.create_index('ix_payroll_runs_period', 'payroll_runs', ['period_month', 'period_year'])
    op.create_index('ix_payroll_runs_status', 'payroll_runs', ['status'])

    # ── payroll_lines ─────────────────────────────────────────────────
    op.create_table('payroll_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payroll_run_id', sa.Integer(), sa.ForeignKey('payroll_runs.id'), nullable=False),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('employee_code', sa.String(length=20), nullable=True),
        sa.Column('employee_name', sa.String(length=100), nullable=True),
        sa.Column('base_salary', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('working_days', sa.Numeric(5, 1), nullable=False, server_default='0'),
        sa.Column('standard_days', sa.Numeric(5, 1), nullable=False, server_default='26'),
        sa.Column('prorated_salary', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('overtime_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('allowances_total', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('bonus_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('gross_salary', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('si_base_salary', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('employee_si', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('employee_hi', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('employee_ui', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('advance_deduction', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('other_deductions', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('exempt_income', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('personal_relief', sa.Numeric(18, 2), nullable=False, server_default='15500000'),
        sa.Column('dependent_relief', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('additional_deductions', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('taxable_income', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('pit_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('net_pay', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('employer_si', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('employer_hi', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('employer_ui', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('employer_occ', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('kpcd', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('payment_method', sa.String(length=30), nullable=False, server_default='bank_transfer'),
        sa.Column('payment_status', sa.String(length=30), nullable=False, server_default='pending'),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('bank_transaction_ref', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payroll_run_id', 'employee_id',
                            name='uq_payroll_line_employee'),
    )
    op.create_index('ix_payroll_lines_run_id', 'payroll_lines', ['payroll_run_id'])
    op.create_index('ix_payroll_lines_employee_id', 'payroll_lines', ['employee_id'])
    op.create_index('ix_payroll_lines_payment_status', 'payroll_lines', ['payment_status'])

    # ── payroll_adjustments ───────────────────────────────────────────
    op.create_table('payroll_adjustments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payroll_run_id', sa.Integer(), sa.ForeignKey('payroll_runs.id'), nullable=False),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('adjustment_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('delta_gross', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('delta_si_base', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('delta_pit', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('delta_net', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_payroll_adjustments_run_id', 'payroll_adjustments', ['payroll_run_id'])
    op.create_index('ix_payroll_adjustments_employee_id', 'payroll_adjustments', ['employee_id'])

    # ── pit_declarations ──────────────────────────────────────────────
    op.create_table('pit_declarations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('declaration_type', sa.String(length=20), nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=True),
        sa.Column('period_quarter', sa.Integer(), nullable=True),
        sa.Column('period_year', sa.Integer(), nullable=False),
        sa.Column('submission_type', sa.String(length=30), nullable=False, server_default='initial'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='draft'),
        sa.Column('total_income', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_exempt_income', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_deductions', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_personal_relief', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_dependent_relief', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_taxable_income', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_pit', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_pit_withheld', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_pit_paid', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('submission_date', sa.DateTime(), nullable=True),
        sa.Column('tax_authority_response', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_pit_declarations_period', 'pit_declarations',
                    ['period_year', 'period_month'])
    op.create_index('ix_pit_declarations_status', 'pit_declarations', ['status'])

    # ── si_insurance_records ──────────────────────────────────────────
    op.create_table('si_insurance_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payroll_run_id', sa.Integer(), sa.ForeignKey('payroll_runs.id'), nullable=True),
        sa.Column('period_month', sa.Integer(), nullable=False),
        sa.Column('period_year', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='draft'),
        sa.Column('total_si_base', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employee_si', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employee_hi', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employee_ui', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_si', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_hi', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_ui', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_occ', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_kpcd', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_payable', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('submission_date', sa.DateTime(), nullable=True),
        sa.Column('confirmation_ref', sa.String(length=100), nullable=True),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period_month', 'period_year',
                            name='uq_si_insurance_period'),
    )
    op.create_index('ix_si_insurance_records_run_id', 'si_insurance_records', ['payroll_run_id'])
    op.create_index('ix_si_insurance_records_period', 'si_insurance_records',
                    ['period_month', 'period_year'])

    # ── salary_payments ───────────────────────────────────────────────
    op.create_table('salary_payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payroll_run_id', sa.Integer(), sa.ForeignKey('payroll_runs.id'), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(length=30), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('bank_transaction_ref', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_salary_payments_run_id', 'salary_payments', ['payroll_run_id'])

    # ── payroll_cost_allocations ──────────────────────────────────────
    op.create_table('payroll_cost_allocations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payroll_run_id', sa.Integer(), sa.ForeignKey('payroll_runs.id'), nullable=False),
        sa.Column('cost_center', sa.String(length=10), nullable=False),
        sa.Column('total_salary_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_employer_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('gl_journal_entry_ref', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_payroll_cost_allocations_run_id', 'payroll_cost_allocations',
                    ['payroll_run_id'])

    # ── payroll_audit_logs ────────────────────────────────────────────
    op.create_table('payroll_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payroll_run_id', sa.Integer(), sa.ForeignKey('payroll_runs.id'), nullable=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('changed_by', sa.String(length=100), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_payroll_audit_logs_run_id', 'payroll_audit_logs', ['payroll_run_id'])
    op.create_index('ix_payroll_audit_logs_employee_id', 'payroll_audit_logs', ['employee_id'])
    op.create_index('ix_payroll_audit_logs_action', 'payroll_audit_logs', ['action'])


def downgrade() -> None:
    op.drop_table('payroll_audit_logs')
    op.drop_table('payroll_cost_allocations')
    op.drop_table('salary_payments')
    op.drop_table('si_insurance_records')
    op.drop_table('pit_declarations')
    op.drop_table('payroll_adjustments')
    op.drop_table('payroll_lines')
    op.drop_table('payroll_runs')
    op.drop_table('timesheets')
    op.drop_table('employee_dependents')
    op.drop_table('employee_contracts')
    op.drop_table('employees')
