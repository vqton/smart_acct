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


class PayrollRunMixin:
    """Mixin for PayrollRun-related repository methods."""
    # ── PayrollRun mappings ────────────────────────────────────────

    def _payroll_run_to_domain(self, m: PayrollRunModel) -> PayrollRun:
        run = PayrollRun(
            period_month=m.period_month,
            period_year=m.period_year,
            status=PayrollRunStatus(m.status) if m.status else PayrollRunStatus.DRAFT,
            lines=[self._payroll_line_to_domain(l) for l in m.lines],
            total_gross=m.total_gross or Decimal("0"),
            total_employee_si=m.total_employee_si or Decimal("0"),
            total_employee_hi=m.total_employee_hi or Decimal("0"),
            total_employee_ui=m.total_employee_ui or Decimal("0"),
            total_pit=m.total_pit or Decimal("0"),
            total_advances=m.total_advances or Decimal("0"),
            total_other_deductions=m.total_other_deductions or Decimal("0"),
            total_net=m.total_net or Decimal("0"),
            total_employer_si=m.total_employer_si or Decimal("0"),
            total_employer_hi=m.total_employer_hi or Decimal("0"),
            total_employer_ui=m.total_employer_ui or Decimal("0"),
            total_employer_occ=m.total_employer_occ or Decimal("0"),
            total_kpcd=m.total_kpcd or Decimal("0"),
            computed_at=m.computed_at,
            approved_at=m.approved_at,
            approved_by=m.approved_by,
            paid_at=m.paid_at,
            notes=m.notes,
            created_at=m.created_at or datetime.now(timezone.utc),
            updated_at=m.updated_at or datetime.now(timezone.utc),
            created_by=m.created_by,
        )
        run.id = m.id
        return run

    def _payroll_run_to_model(self, d: PayrollRun) -> PayrollRunModel:
        return PayrollRunModel(
            period_month=d.period_month,
            period_year=d.period_year,
            status=d.status.value,
            total_gross=d.total_gross,
            total_employee_si=d.total_employee_si,
            total_employee_hi=d.total_employee_hi,
            total_employee_ui=d.total_employee_ui,
            total_pit=d.total_pit,
            total_advances=d.total_advances,
            total_other_deductions=d.total_other_deductions,
            total_net=d.total_net,
            total_employer_si=d.total_employer_si,
            total_employer_hi=d.total_employer_hi,
            total_employer_ui=d.total_employer_ui,
            total_employer_occ=d.total_employer_occ,
            total_kpcd=d.total_kpcd,
            computed_at=d.computed_at,
            approved_at=d.approved_at,
            approved_by=d.approved_by,
            paid_at=d.paid_at,
            notes=d.notes,
            created_by=d.created_by,
        )

    # ── PayrollRun CRUD ────────────────────────────────────────────

    def create_payroll_run(self, run: PayrollRun) -> Result:
        existing = self.session.execute(
            select(PayrollRunModel).where(
                PayrollRunModel.period_month == run.period_month,
                PayrollRunModel.period_year == run.period_year,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_ALREADY_EXISTS,
                period=f"{run.period_month}/{run.period_year}",
            ))
        model = self._payroll_run_to_model(run)
        self.session.add(model)
        self.session.flush()
        for line in run.lines:
            line_model = self._payroll_line_to_model(line, model.id)
            self.session.add(line_model)
        self.session.flush()
        return Result.success(self._payroll_run_to_domain(model))

    def get_payroll_run(self, run_id: int) -> Result:
        m = self.session.get(PayrollRunModel, run_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_NOT_FOUND, id=str(run_id),
            ))
        return Result.success(self._payroll_run_to_domain(m))

    def get_payroll_run_by_period(self, month: int, year: int) -> Result:
        m = self.session.execute(
            select(PayrollRunModel).where(
                PayrollRunModel.period_month == month,
                PayrollRunModel.period_year == year,
            )
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_NOT_FOUND,
                period=f"{month}/{year}",
            ))
        return Result.success(self._payroll_run_to_domain(m))

    def list_payroll_runs(self, filters: dict = None) -> Result:
        f = filters or {}
        stmt = select(PayrollRunModel).order_by(
            desc(PayrollRunModel.period_year),
            desc(PayrollRunModel.period_month),
        )
        status_val = f.get("status")
        if status_val:
            stmt = stmt.where(PayrollRunModel.status == status_val)
        year_val = f.get("period_year")
        if year_val is not None:
            stmt = stmt.where(PayrollRunModel.period_year == year_val)
        month_val = f.get("period_month")
        if month_val is not None:
            stmt = stmt.where(PayrollRunModel.period_month == month_val)
        models = self.session.execute(stmt).scalars().all()
        return Result.success([self._payroll_run_to_domain(m) for m in models])

    def update_payroll_run_status(self, run_id: int, status: str, **extra) -> Result:
        m = self.session.get(PayrollRunModel, run_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_NOT_FOUND, id=str(run_id),
            ))
        m.status = status
        allowed_extra = {
            "computed_at", "approved_at", "approved_by",
            "paid_at", "notes", "total_gross", "total_employee_si",
            "total_employee_hi", "total_employee_ui", "total_pit",
            "total_advances", "total_other_deductions", "total_net",
            "total_employer_si", "total_employer_hi", "total_employer_ui",
            "total_employer_occ", "total_kpcd",
        }
        for k, v in extra.items():
            if k in allowed_extra:
                setattr(m, k, v)
        self.session.flush()
        return Result.success(self._payroll_run_to_domain(m))

    def save_payroll_lines(self, run_id: int, lines: List[PayrollLine]) -> Result:
        existing = self.session.execute(
            select(PayrollLineModel).where(PayrollLineModel.payroll_run_id == run_id)
        ).scalars().all()
        for line in existing:
            self.session.delete(line)
        self.session.flush()
        for line in lines:
            model = self._payroll_line_to_model(line, run_id)
            self.session.add(model)
        self.session.flush()
        return Result.success(None)

