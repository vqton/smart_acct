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


class AdjustmentMixin:
    """Mixin for Adjustment-related repository methods."""
    # ── PayrollAdjustment mappings ─────────────────────────────────

    def _adjustment_to_domain(self, m: PayrollAdjustmentModel) -> PayrollAdjustment:
        a = PayrollAdjustment(
            payroll_run_id=m.payroll_run_id,
            employee_id=m.employee_id,
            adjustment_type=AdjustmentType(m.adjustment_type),
            amount=m.amount or Decimal("0"),
            delta_gross=m.delta_gross or Decimal("0"),
            delta_si_base=m.delta_si_base or Decimal("0"),
            delta_pit=m.delta_pit or Decimal("0"),
            delta_net=m.delta_net or Decimal("0"),
            reason=m.reason,
            approved_by=m.approved_by,
            approved_at=m.approved_at,
            status=PayrollRunStatus(m.status) if m.status else PayrollRunStatus.DRAFT,
            created_at=m.created_at,
            created_by=m.created_by,
        )
        a.id = m.id
        return a

    def _adjustment_to_model(self, d: PayrollAdjustment) -> PayrollAdjustmentModel:
        return PayrollAdjustmentModel(
            payroll_run_id=d.payroll_run_id,
            employee_id=d.employee_id,
            adjustment_type=d.adjustment_type.value,
            amount=d.amount,
            delta_gross=d.delta_gross,
            delta_si_base=d.delta_si_base,
            delta_pit=d.delta_pit,
            delta_net=d.delta_net,
            reason=d.reason,
            approved_by=d.approved_by,
            approved_at=d.approved_at,
            status=d.status.value,
            created_by=d.created_by,
        )

    # ── PayrollAdjustment CRUD ─────────────────────────────────────

    def create_adjustment(self, adj: PayrollAdjustment) -> Result:
        model = self._adjustment_to_model(adj)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._adjustment_to_domain(model))

    def get_adjustment(self, adj_id: int) -> Result:
        m = self.session.get(PayrollAdjustmentModel, adj_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_ADJUSTMENT_NOT_FOUND, id=str(adj_id),
            ))
        return Result.success(self._adjustment_to_domain(m))

    def update_adjustment(self, adj: PayrollAdjustment) -> Result:
        m = self.session.get(PayrollAdjustmentModel, adj.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_ADJUSTMENT_NOT_FOUND, id=str(adj.id),
            ))
        m.adjustment_type = adj.adjustment_type.value
        m.amount = adj.amount
        m.delta_gross = adj.delta_gross
        m.delta_si_base = adj.delta_si_base
        m.delta_pit = adj.delta_pit
        m.delta_net = adj.delta_net
        m.reason = adj.reason
        m.approved_by = adj.approved_by
        m.approved_at = adj.approved_at
        m.status = adj.status.value
        self.session.flush()
        return Result.success(self._adjustment_to_domain(m))

    def list_run_adjustments(self, run_id: int) -> Result:
        models = self.session.execute(
            select(PayrollAdjustmentModel)
            .where(PayrollAdjustmentModel.payroll_run_id == run_id)
            .order_by(PayrollAdjustmentModel.created_at)
        ).scalars().all()
        return Result.success([self._adjustment_to_domain(m) for m in models])

    def approve_adjustment(self, adj_id: int, approved_by: str) -> Result:
        m = self.session.get(PayrollAdjustmentModel, adj_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_ADJUSTMENT_NOT_FOUND, id=str(adj_id),
            ))
        m.status = PayrollRunStatus.APPROVED.value
        m.approved_by = approved_by
        m.approved_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._adjustment_to_domain(m))

