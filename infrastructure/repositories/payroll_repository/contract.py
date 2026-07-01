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


class ContractMixin:
    """Mixin for Contract-related repository methods."""
    # ── Contract mappings ──────────────────────────────────────────

    def _contract_to_domain(self, m: EmployeeContractModel) -> EmployeeContract:
        c = EmployeeContract(
            employee_id=m.employee_id,
            contract_type=ContractType(m.contract_type),
            start_date=m.start_date,
            end_date=m.end_date,
            base_salary=m.base_salary or Decimal("0"),
            position_allowance=m.position_allowance or Decimal("0"),
            meal_allowance=m.meal_allowance or Decimal("0"),
            phone_allowance=m.phone_allowance or Decimal("0"),
            transport_allowance=m.transport_allowance or Decimal("0"),
            housing_allowance=m.housing_allowance or Decimal("0"),
            responsibility_allowance=m.responsibility_allowance or Decimal("0"),
            other_allowance=m.other_allowance or Decimal("0"),
            is_active=m.is_active if m.is_active is not None else True,
            created_at=m.created_at or datetime.now(timezone.utc),
            updated_at=m.updated_at or datetime.now(timezone.utc),
        )
        c.id = m.id
        return c

    def _contract_to_model(self, d: EmployeeContract) -> EmployeeContractModel:
        return EmployeeContractModel(
            employee_id=d.employee_id,
            contract_type=d.contract_type.value,
            start_date=d.start_date,
            end_date=d.end_date,
            base_salary=d.base_salary,
            position_allowance=d.position_allowance,
            meal_allowance=d.meal_allowance,
            phone_allowance=d.phone_allowance,
            transport_allowance=d.transport_allowance,
            housing_allowance=d.housing_allowance,
            responsibility_allowance=d.responsibility_allowance,
            other_allowance=d.other_allowance,
            is_active=d.is_active,
        )

    # ── Contract CRUD ──────────────────────────────────────────────

    def create_contract(self, contract: EmployeeContract) -> Result:
        if contract.is_active:
            existing_active = self.session.execute(
                select(EmployeeContractModel).where(
                    EmployeeContractModel.employee_id == contract.employee_id,
                    EmployeeContractModel.is_active.is_(True),
                )
            ).scalar_one_or_none()
            if existing_active:
                return Result.failure(VASValidationError(
                    ErrorCodes.PR_ACTIVE_CONTRACT_EXISTS,
                    employee_id=str(contract.employee_id),
                ))
        model = self._contract_to_model(contract)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._contract_to_domain(model))

    def get_contract(self, contract_id: int) -> Result:
        m = self.session.get(EmployeeContractModel, contract_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_CONTRACT_NOT_FOUND, id=str(contract_id),
            ))
        return Result.success(self._contract_to_domain(m))

    def get_active_contract(self, employee_id: int) -> Result:
        m = self.session.execute(
            select(EmployeeContractModel).where(
                EmployeeContractModel.employee_id == employee_id,
                EmployeeContractModel.is_active.is_(True),
            )
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_CONTRACT_NOT_FOUND,
                id=f"active_contract_{employee_id}",
            ))
        return Result.success(self._contract_to_domain(m))

    def list_employee_contracts(self, employee_id: int) -> Result:
        models = self.session.execute(
            select(EmployeeContractModel)
            .where(EmployeeContractModel.employee_id == employee_id)
            .order_by(desc(EmployeeContractModel.start_date))
        ).scalars().all()
        return Result.success([self._contract_to_domain(m) for m in models])

    def update_contract(self, contract: EmployeeContract) -> Result:
        m = self.session.get(EmployeeContractModel, contract.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_CONTRACT_NOT_FOUND, id=str(contract.id),
            ))
        m.contract_type = contract.contract_type.value
        m.start_date = contract.start_date
        m.end_date = contract.end_date
        m.base_salary = contract.base_salary
        m.position_allowance = contract.position_allowance
        m.meal_allowance = contract.meal_allowance
        m.phone_allowance = contract.phone_allowance
        m.transport_allowance = contract.transport_allowance
        m.housing_allowance = contract.housing_allowance
        m.responsibility_allowance = contract.responsibility_allowance
        m.other_allowance = contract.other_allowance
        m.is_active = contract.is_active
        self.session.flush()
        return Result.success(self._contract_to_domain(m))

    def terminate_contract(self, contract_id: int) -> Result:
        m = self.session.get(EmployeeContractModel, contract_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_CONTRACT_NOT_FOUND, id=str(contract_id),
            ))
        m.is_active = False
        self.session.flush()
        return Result.success(self._contract_to_domain(m))

