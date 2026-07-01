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


class DependentMixin:
    """Mixin for Dependent-related repository methods."""
    # ── Dependent mappings ─────────────────────────────────────────

    def _dependent_to_domain(self, m: EmployeeDependentModel) -> EmployeeDependent:
        d = EmployeeDependent(
            employee_id=m.employee_id,
            full_name=m.full_name,
            relationship=m.relationship_type,
            date_of_birth=m.date_of_birth,
            tax_code=m.tax_code,
            from_date=m.from_date,
            to_date=m.to_date,
            is_active=m.is_active if m.is_active is not None else True,
        )
        d.id = m.id
        return d

    def _dependent_to_model(self, d: EmployeeDependent) -> EmployeeDependentModel:
        return EmployeeDependentModel(
            employee_id=d.employee_id,
            full_name=d.full_name,
            relationship_type=d.relationship,
            date_of_birth=d.date_of_birth,
            tax_code=d.tax_code,
            from_date=d.from_date,
            to_date=d.to_date,
            is_active=d.is_active,
        )

    # ── Dependent CRUD ─────────────────────────────────────────────

    def create_dependent(self, dependent: EmployeeDependent) -> Result:
        model = self._dependent_to_model(dependent)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._dependent_to_domain(model))

    def list_employee_dependents(self, employee_id: int) -> Result:
        models = self.session.execute(
            select(EmployeeDependentModel)
            .where(EmployeeDependentModel.employee_id == employee_id)
            .order_by(EmployeeDependentModel.full_name)
        ).scalars().all()
        return Result.success([self._dependent_to_domain(m) for m in models])

    def update_dependent(self, dependent: EmployeeDependent) -> Result:
        m = self.session.get(EmployeeDependentModel, dependent.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_DEPENDENT_INVALID, id=str(dependent.id),
            ))
        m.full_name = dependent.full_name
        m.relationship_type = dependent.relationship
        m.date_of_birth = dependent.date_of_birth
        m.tax_code = dependent.tax_code
        m.from_date = dependent.from_date
        m.to_date = dependent.to_date
        m.is_active = dependent.is_active
        self.session.flush()
        return Result.success(self._dependent_to_domain(m))

    def deactivate_dependent(self, dependent_id: int) -> Result:
        m = self.session.get(EmployeeDependentModel, dependent_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_DEPENDENT_INVALID, id=str(dependent_id),
            ))
        m.is_active = False
        self.session.flush()
        return Result.success(None)

