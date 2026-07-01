"""Payroll repository package - entity-grouped mixins composed into PayrollRepository."""
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
from .employee import EmployeeMixin
from .contract import ContractMixin
from .dependent import DependentMixin
from .timesheet import TimesheetMixin
from .payrollline import PayrollLineMixin
from .payrollrun import PayrollRunMixin
from .adjustment import AdjustmentMixin
from .pit import PITMixin
from .si import SIMixin
from .salarypayment import SalaryPaymentMixin
from .costallocation import CostAllocationMixin
from .audit import AuditMixin


class PayrollRepository(EmployeeMixin, ContractMixin, DependentMixin, TimesheetMixin, PayrollLineMixin, PayrollRunMixin, AdjustmentMixin, PITMixin, SIMixin, SalaryPaymentMixin, CostAllocationMixin, AuditMixin):
    """Payroll repository - composed from entity-grouped mixins."""
    def __init__(self, session: Session):
        self.session = session

    # ── Aliases used by PayrollUseCases ────────────────────────────

    def create_run(self, run: PayrollRun) -> Result:
        return self.create_payroll_run(run)

    def get_run(self, run_id: int) -> Result:
        return self.get_payroll_run(run_id)

    def get_run_by_period(self, month: int, year: int) -> Result:
        return self.get_payroll_run_by_period(month, year)

    def update_run(self, run: PayrollRun) -> Result:
        m = self.session.get(PayrollRunModel, run.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PAYROLL_NOT_FOUND, id=str(run.id),
            ))
        m.period_month = run.period_month
        m.period_year = run.period_year
        m.status = run.status.value
        m.total_gross = run.total_gross
        m.total_employee_si = run.total_employee_si
        m.total_employee_hi = run.total_employee_hi
        m.total_employee_ui = run.total_employee_ui
        m.total_pit = run.total_pit
        m.total_advances = run.total_advances
        m.total_other_deductions = run.total_other_deductions
        m.total_net = run.total_net
        m.total_employer_si = run.total_employer_si
        m.total_employer_hi = run.total_employer_hi
        m.total_employer_ui = run.total_employer_ui
        m.total_employer_occ = run.total_employer_occ
        m.total_kpcd = run.total_kpcd
        m.computed_at = run.computed_at
        m.approved_at = run.approved_at
        m.approved_by = run.approved_by
        m.paid_at = run.paid_at
        m.notes = run.notes
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._payroll_run_to_domain(m))

    def list_runs(self, filters: dict = None) -> Result:
        return self.list_payroll_runs(filters)

    def get_employees_for_period(self, month: int, year: int) -> List[dict]:
        employees = self.list_employees(
            filters={"status": EmployeeStatus.ACTIVE.value},
            page=1, per_page=10000,
        )
        emp_list = []
        if employees.is_success():
            data = employees.get_data()
            if isinstance(data, dict):
                emp_list = data.get("items", [])
        result = []
        for emp in emp_list:
            contract_result = self.get_active_contract(emp.id)
            contract = contract_result.get_data() if contract_result.is_success() else None
            ts_result = self.get_employee_timesheet(emp.id, month, year)
            timesheet = ts_result.get_data() if ts_result.is_success() else None
            result.append({
                "employee": emp,
                "contract": contract,
                "timesheet": timesheet,
            })
        return result

    def update_lines_payment_status(self, run_id: int, status: PaymentStatus) -> None:
        models = self.session.execute(
            select(PayrollLineModel).where(PayrollLineModel.payroll_run_id == run_id)
        ).scalars().all()
        for m in models:
            m.payment_status = status.value
        self.session.flush()

    # ── Query helpers ──────────────────────────────────────────────

    def get_employees_by_department(self, department_id: int) -> Result:
        models = self.session.execute(
            select(EmployeeModel)
            .where(EmployeeModel.department_id == department_id)
            .order_by(EmployeeModel.employee_code)
        ).scalars().all()
        return Result.success([self._employee_to_domain(m) for m in models])

    def count_employees_by_status(self, status: str) -> int:
        count = self.session.execute(
            select(func.count()).where(EmployeeModel.status == status)
        ).scalar_one()
        return count

    def get_total_salary_by_department(self, month: int, year: int) -> Result:
        stmt = (
            select(
                EmployeeModel.department_id,
                EmployeeModel.department_name,
                func.coalesce(func.sum(PayrollLineModel.gross_salary), Decimal("0")).label("total_gross"),
                func.coalesce(func.sum(PayrollLineModel.employer_si + PayrollLineModel.employer_hi + PayrollLineModel.employer_ui + PayrollLineModel.employer_occ + PayrollLineModel.kpcd), Decimal("0")).label("total_employer_cost"),
                func.coalesce(func.sum(PayrollLineModel.net_pay), Decimal("0")).label("total_net"),
                func.count(PayrollLineModel.id.distinct()).label("employee_count"),
            )
            .join(PayrollLineModel, EmployeeModel.id == PayrollLineModel.employee_id)
            .join(PayrollRunModel, PayrollLineModel.payroll_run_id == PayrollRunModel.id)
            .where(
                PayrollRunModel.period_month == month,
                PayrollRunModel.period_year == year,
                EmployeeModel.department_id.isnot(None),
            )
            .group_by(EmployeeModel.department_id, EmployeeModel.department_name)
            .order_by(EmployeeModel.department_id)
        )
        rows = self.session.execute(stmt).all()
        result = []
        for row in rows:
            result.append({
                "department_id": row.department_id,
                "department_name": row.department_name,
                "total_gross": row.total_gross,
                "total_employer_cost": row.total_employer_cost,
                "total_net": row.total_net,
                "employee_count": row.employee_count,
            })
        return Result.success(result)

    def search_employees(self, query: str) -> Result:
        pattern = f"%{query}%"
        models = self.session.execute(
            select(EmployeeModel).where(
                or_(
                    EmployeeModel.employee_code.ilike(pattern),
                    EmployeeModel.full_name.ilike(pattern),
                    EmployeeModel.tax_code.ilike(pattern),
                )
            ).order_by(EmployeeModel.employee_code).limit(50)
        ).scalars().all()
        return Result.success([self._employee_to_domain(m) for m in models])

