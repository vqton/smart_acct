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


class AuditMixin:
    """Mixin for Audit-related repository methods."""
    # ── Audit Log ──────────────────────────────────────────────────

    def log_audit(
        self,
        payroll_run_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        action: str = "",
        old_value: dict = None,
        new_value: dict = None,
        changed_by: str = None,
    ) -> Result:
        model = PayrollAuditLogModel(
            payroll_run_id=payroll_run_id,
            employee_id=employee_id,
            action=action,
            old_value=old_value or {},
            new_value=new_value or {},
            changed_by=changed_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success({
            "id": model.id,
            "action": model.action,
            "changed_at": model.changed_at,
        })

    def get_audit_logs(
        self,
        payroll_run_id: int = None,
        employee_id: int = None,
    ) -> Result:
        stmt = select(PayrollAuditLogModel).order_by(desc(PayrollAuditLogModel.changed_at))
        if payroll_run_id is not None:
            stmt = stmt.where(PayrollAuditLogModel.payroll_run_id == payroll_run_id)
        if employee_id is not None:
            stmt = stmt.where(PayrollAuditLogModel.employee_id == employee_id)
        models = self.session.execute(stmt).scalars().all()
        result = []
        for m in models:
            result.append({
                "id": m.id,
                "payroll_run_id": m.payroll_run_id,
                "employee_id": m.employee_id,
                "action": m.action,
                "old_value": m.old_value,
                "new_value": m.new_value,
                "changed_by": m.changed_by,
                "changed_at": m.changed_at,
            })
        return Result.success(result)

