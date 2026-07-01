from typing import Optional, List, Dict, Any
from datetime import datetime, date, timezone
from decimal import Decimal
from math import ceil
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.exc import IntegrityError

from domain.payroll import (
    Employee, EmployeeContract, EmployeeDependent, Timesheet,
    PayrollRun, PayrollLine, PayrollAdjustment, PITDeclaration,
    SIInsuranceRecord, SalaryPayment, PayrollCostAllocation,
    EmployeeStatus, ContractType, PayrollRunStatus, PaymentMethodPR,
    PaymentStatus, DeclarationStatus, DeclarationType, AdjustmentType,
    CostCenter, Region,
)
from domain.i18n import ErrorCodes
from domain.common import Result, VASValidationError
from infrastructure.models.payroll_models import (
    EmployeeModel, EmployeeContractModel, EmployeeDependentModel,
    TimesheetModel, PayrollRunModel, PayrollLineModel,
    PayrollAdjustmentModel, PITDeclarationModel, SIInsuranceRecordModel,
    SalaryPaymentModel, PayrollCostAllocationModel, PayrollAuditLogModel,
)


class PayrollLineMixin:
    """Mixin for PayrollLine-related repository methods."""
    # ── PayrollLine mappings ───────────────────────────────────────

    def _payroll_line_to_domain(self, m: PayrollLineModel) -> PayrollLine:
        pl = PayrollLine(
            payroll_run_id=m.payroll_run_id,
            employee_id=m.employee_id,
            employee_code=m.employee_code,
            employee_name=m.employee_name,
            base_salary=m.base_salary or Decimal("0"),
            working_days=m.working_days or Decimal("0"),
            standard_days=m.standard_days or Decimal("26"),
            prorated_salary=m.prorated_salary or Decimal("0"),
            overtime_amount=m.overtime_amount or Decimal("0"),
            allowances_total=m.allowances_total or Decimal("0"),
            bonus_amount=m.bonus_amount or Decimal("0"),
            gross_salary=m.gross_salary or Decimal("0"),
            si_base_salary=m.si_base_salary or Decimal("0"),
            employee_si=m.employee_si or Decimal("0"),
            employee_hi=m.employee_hi or Decimal("0"),
            employee_ui=m.employee_ui or Decimal("0"),
            advance_deduction=m.advance_deduction or Decimal("0"),
            other_deductions=m.other_deductions or Decimal("0"),
            exempt_income=m.exempt_income or Decimal("0"),
            personal_relief=m.personal_relief or Decimal("15500000"),
            dependent_relief=m.dependent_relief or Decimal("0"),
            additional_deductions=m.additional_deductions or Decimal("0"),
            taxable_income=m.taxable_income or Decimal("0"),
            pit_amount=m.pit_amount or Decimal("0"),
            net_pay=m.net_pay or Decimal("0"),
            employer_si=m.employer_si or Decimal("0"),
            employer_hi=m.employer_hi or Decimal("0"),
            employer_ui=m.employer_ui or Decimal("0"),
            employer_occ=m.employer_occ or Decimal("0"),
            kpcd=m.kpcd or Decimal("0"),
            payment_method=PaymentMethodPR(m.payment_method) if m.payment_method else PaymentMethodPR.BANK_TRANSFER,
            payment_status=PaymentStatus(m.payment_status) if m.payment_status else PaymentStatus.PENDING,
            payment_date=m.payment_date,
            bank_transaction_ref=m.bank_transaction_ref,
            notes=m.notes,
        )
        pl.id = m.id
        return pl

    def _payroll_line_to_model(self, d: PayrollLine, payroll_run_id: int) -> PayrollLineModel:
        return PayrollLineModel(
            payroll_run_id=payroll_run_id,
            employee_id=d.employee_id,
            employee_code=d.employee_code,
            employee_name=d.employee_name,
            base_salary=d.base_salary,
            working_days=d.working_days,
            standard_days=d.standard_days,
            prorated_salary=d.prorated_salary,
            overtime_amount=d.overtime_amount,
            allowances_total=d.allowances_total,
            bonus_amount=d.bonus_amount,
            gross_salary=d.gross_salary,
            si_base_salary=d.si_base_salary,
            employee_si=d.employee_si,
            employee_hi=d.employee_hi,
            employee_ui=d.employee_ui,
            advance_deduction=d.advance_deduction,
            other_deductions=d.other_deductions,
            exempt_income=d.exempt_income,
            personal_relief=d.personal_relief,
            dependent_relief=d.dependent_relief,
            additional_deductions=d.additional_deductions,
            taxable_income=d.taxable_income,
            pit_amount=d.pit_amount,
            net_pay=d.net_pay,
            employer_si=d.employer_si,
            employer_hi=d.employer_hi,
            employer_ui=d.employer_ui,
            employer_occ=d.employer_occ,
            kpcd=d.kpcd,
            payment_method=d.payment_method.value,
            payment_status=d.payment_status.value,
            payment_date=d.payment_date,
            bank_transaction_ref=d.bank_transaction_ref,
            notes=d.notes,
        )

