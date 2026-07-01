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


class TimesheetMixin:
    """Mixin for Timesheet-related repository methods."""
    # ── Timesheet mappings ─────────────────────────────────────────

    def _timesheet_to_domain(self, m: TimesheetModel) -> Timesheet:
        t = Timesheet(
            employee_id=m.employee_id,
            period_month=m.period_month,
            period_year=m.period_year,
            working_days=m.working_days or Decimal("0"),
            standard_days=m.standard_days or Decimal("26"),
            overtime_weekday_hours=m.overtime_weekday_hours or Decimal("0"),
            overtime_weekend_hours=m.overtime_weekend_hours or Decimal("0"),
            overtime_holiday_hours=m.overtime_holiday_hours or Decimal("0"),
            sick_leave_days=m.sick_leave_days or Decimal("0"),
            unpaid_leave_days=m.unpaid_leave_days or Decimal("0"),
            paid_leave_days=m.paid_leave_days or Decimal("0"),
            notes=m.notes,
            created_at=m.created_at,
        )
        t.id = m.id
        return t

    def _timesheet_to_model(self, d: Timesheet) -> TimesheetModel:
        return TimesheetModel(
            employee_id=d.employee_id,
            period_month=d.period_month,
            period_year=d.period_year,
            working_days=d.working_days,
            standard_days=d.standard_days,
            overtime_weekday_hours=d.overtime_weekday_hours,
            overtime_weekend_hours=d.overtime_weekend_hours,
            overtime_holiday_hours=d.overtime_holiday_hours,
            sick_leave_days=d.sick_leave_days,
            unpaid_leave_days=d.unpaid_leave_days,
            paid_leave_days=d.paid_leave_days,
            notes=d.notes,
        )

    # ── Timesheet CRUD ─────────────────────────────────────────────

    def upsert_timesheet(self, timesheet: Timesheet) -> Result:
        existing = self.session.execute(
            select(TimesheetModel).where(
                TimesheetModel.employee_id == timesheet.employee_id,
                TimesheetModel.period_month == timesheet.period_month,
                TimesheetModel.period_year == timesheet.period_year,
            )
        ).scalar_one_or_none()
        if existing:
            existing.working_days = timesheet.working_days
            existing.standard_days = timesheet.standard_days
            existing.overtime_weekday_hours = timesheet.overtime_weekday_hours
            existing.overtime_weekend_hours = timesheet.overtime_weekend_hours
            existing.overtime_holiday_hours = timesheet.overtime_holiday_hours
            existing.sick_leave_days = timesheet.sick_leave_days
            existing.unpaid_leave_days = timesheet.unpaid_leave_days
            existing.paid_leave_days = timesheet.paid_leave_days
            existing.notes = timesheet.notes
            self.session.flush()
            return Result.success(self._timesheet_to_domain(existing))
        model = self._timesheet_to_model(timesheet)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._timesheet_to_domain(model))

    def get_timesheet(self, timesheet_id: int) -> Result:
        m = self.session.get(TimesheetModel, timesheet_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_TIMESHEET_EMPLOYEE_NOT_FOUND, id=str(timesheet_id),
            ))
        return Result.success(self._timesheet_to_domain(m))

    def get_employee_timesheet(self, employee_id: int, month: int, year: int) -> Result:
        m = self.session.execute(
            select(TimesheetModel).where(
                TimesheetModel.employee_id == employee_id,
                TimesheetModel.period_month == month,
                TimesheetModel.period_year == year,
            )
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_TIMESHEET_MISSING,
                employee_id=str(employee_id),
                period=f"{month}/{year}",
            ))
        return Result.success(self._timesheet_to_domain(m))

    def list_period_timesheets(self, month: int, year: int) -> Result:
        models = self.session.execute(
            select(TimesheetModel).where(
                TimesheetModel.period_month == month,
                TimesheetModel.period_year == year,
            )
        ).scalars().all()
        return Result.success([self._timesheet_to_domain(m) for m in models])

