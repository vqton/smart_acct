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


class SIMixin:
    """Mixin for SI-related repository methods."""
    # ── SIInsuranceRecord mappings ─────────────────────────────────

    def _si_record_to_domain(self, m: SIInsuranceRecordModel) -> SIInsuranceRecord:
        r = SIInsuranceRecord(
            payroll_run_id=m.payroll_run_id,
            period_month=m.period_month,
            period_year=m.period_year,
            status=DeclarationStatus(m.status) if m.status else DeclarationStatus.DRAFT,
            total_si_base=m.total_si_base or Decimal("0"),
            total_employee_si=m.total_employee_si or Decimal("0"),
            total_employee_hi=m.total_employee_hi or Decimal("0"),
            total_employee_ui=m.total_employee_ui or Decimal("0"),
            total_employer_si=m.total_employer_si or Decimal("0"),
            total_employer_hi=m.total_employer_hi or Decimal("0"),
            total_employer_ui=m.total_employer_ui or Decimal("0"),
            total_employer_occ=m.total_employer_occ or Decimal("0"),
            total_kpcd=m.total_kpcd or Decimal("0"),
            total_payable=m.total_payable or Decimal("0"),
            submission_date=m.submission_date,
            confirmation_ref=m.confirmation_ref,
            payment_date=m.payment_date,
            created_at=m.created_at or datetime.now(timezone.utc),
            updated_at=m.updated_at or datetime.now(timezone.utc),
            created_by=m.created_by,
        )
        r.id = m.id
        return r

    def _si_record_to_model(self, d: SIInsuranceRecord) -> SIInsuranceRecordModel:
        return SIInsuranceRecordModel(
            payroll_run_id=d.payroll_run_id,
            period_month=d.period_month,
            period_year=d.period_year,
            status=d.status.value,
            total_si_base=d.total_si_base,
            total_employee_si=d.total_employee_si,
            total_employee_hi=d.total_employee_hi,
            total_employee_ui=d.total_employee_ui,
            total_employer_si=d.total_employer_si,
            total_employer_hi=d.total_employer_hi,
            total_employer_ui=d.total_employer_ui,
            total_employer_occ=d.total_employer_occ,
            total_kpcd=d.total_kpcd,
            total_payable=d.total_payable,
            submission_date=d.submission_date,
            confirmation_ref=d.confirmation_ref,
            payment_date=d.payment_date,
            created_by=d.created_by,
        )

    # ── SI Record CRUD ─────────────────────────────────────────────

    def create_si_record(self, record: SIInsuranceRecord) -> Result:
        model = self._si_record_to_model(record)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._si_record_to_domain(model))

    def get_si_record(self, record_id: int) -> Result:
        m = self.session.get(SIInsuranceRecordModel, record_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_SI_RECORD_NOT_FOUND, id=str(record_id),
            ))
        return Result.success(self._si_record_to_domain(m))

    def update_si_record(self, record: SIInsuranceRecord) -> Result:
        m = self.session.get(SIInsuranceRecordModel, record.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_SI_RECORD_NOT_FOUND, id=str(record.id),
            ))
        m.period_month = record.period_month
        m.period_year = record.period_year
        m.status = record.status.value
        m.total_si_base = record.total_si_base
        m.total_employee_si = record.total_employee_si
        m.total_employee_hi = record.total_employee_hi
        m.total_employee_ui = record.total_employee_ui
        m.total_employer_si = record.total_employer_si
        m.total_employer_hi = record.total_employer_hi
        m.total_employer_ui = record.total_employer_ui
        m.total_employer_occ = record.total_employer_occ
        m.total_kpcd = record.total_kpcd
        m.total_payable = record.total_payable
        m.submission_date = record.submission_date
        m.confirmation_ref = record.confirmation_ref
        m.payment_date = record.payment_date
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._si_record_to_domain(m))

    def get_si_record_by_period(self, month: int, year: int) -> Result:
        m = self.session.execute(
            select(SIInsuranceRecordModel).where(
                SIInsuranceRecordModel.period_month == month,
                SIInsuranceRecordModel.period_year == year,
            )
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_SI_RECORD_NOT_FOUND, period=f"{month}/{year}",
            ))
        return Result.success(self._si_record_to_domain(m))

