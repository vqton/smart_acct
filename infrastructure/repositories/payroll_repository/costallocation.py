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


class CostAllocationMixin:
    """Mixin for CostAllocation-related repository methods."""
    # ── PayrollCostAllocation mappings ─────────────────────────────

    def _cost_allocation_to_domain(self, m: PayrollCostAllocationModel) -> PayrollCostAllocation:
        a = PayrollCostAllocation(
            payroll_run_id=m.payroll_run_id,
            cost_center=CostCenter(m.cost_center),
            total_salary_cost=m.total_salary_cost or Decimal("0"),
            total_employer_cost=m.total_employer_cost or Decimal("0"),
            total_cost=m.total_cost or Decimal("0"),
            gl_journal_entry_ref=m.gl_journal_entry_ref,
            created_at=m.created_at or datetime.now(timezone.utc),
        )
        a.id = m.id
        return a

    def _cost_allocation_to_model(self, d: PayrollCostAllocation) -> PayrollCostAllocationModel:
        return PayrollCostAllocationModel(
            payroll_run_id=d.payroll_run_id,
            cost_center=d.cost_center.value,
            total_salary_cost=d.total_salary_cost,
            total_employer_cost=d.total_employer_cost,
            total_cost=d.total_cost,
            gl_journal_entry_ref=d.gl_journal_entry_ref,
        )

    # ── Cost Allocation CRUD ───────────────────────────────────────

    def create_cost_allocation(self, alloc: PayrollCostAllocation) -> Result:
        model = self._cost_allocation_to_model(alloc)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._cost_allocation_to_domain(model))

    def get_run_cost_allocations(self, run_id: int) -> Result:
        models = self.session.execute(
            select(PayrollCostAllocationModel)
            .where(PayrollCostAllocationModel.payroll_run_id == run_id)
            .order_by(PayrollCostAllocationModel.cost_center)
        ).scalars().all()
        return Result.success([self._cost_allocation_to_domain(m) for m in models])

