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


class EmployeeMixin:
    """Mixin for Employee-related repository methods."""
    # ── Employee mappings ──────────────────────────────────────────

    def _employee_to_domain(self, m: EmployeeModel) -> Employee:
        e = Employee(
            employee_code=m.employee_code,
            full_name=m.full_name,
            date_of_birth=m.date_of_birth,
            gender=m.gender,
            id_number=m.id_number,
            id_issue_date=m.id_issue_date,
            id_issue_place=m.id_issue_place,
            tax_code=m.tax_code,
            si_book_number=m.si_book_number,
            bank_account=m.bank_account,
            bank_name=m.bank_name,
            department_id=m.department_id,
            department_name=m.department_name,
            position=m.position,
            region=Region(m.region) if m.region else Region.REGION_1,
            dependent_count=m.dependent_count or 0,
            status=EmployeeStatus(m.status) if m.status else EmployeeStatus.ACTIVE,
            start_date=m.start_date,
            termination_date=m.termination_date,
            created_at=m.created_at,
            updated_at=m.updated_at,
            created_by=m.created_by,
            updated_by=m.updated_by,
        )
        e.id = m.id
        return e

    def _employee_to_model(self, d: Employee) -> EmployeeModel:
        return EmployeeModel(
            employee_code=d.employee_code,
            full_name=d.full_name,
            date_of_birth=d.date_of_birth,
            gender=d.gender,
            id_number=d.id_number,
            id_issue_date=d.id_issue_date,
            id_issue_place=d.id_issue_place,
            tax_code=d.tax_code,
            si_book_number=d.si_book_number,
            bank_account=d.bank_account,
            bank_name=d.bank_name,
            department_id=d.department_id,
            department_name=d.department_name,
            position=d.position,
            region=d.region.value,
            dependent_count=d.dependent_count,
            status=d.status.value,
            start_date=d.start_date,
            termination_date=d.termination_date,
            created_at=d.created_at,
            updated_at=d.updated_at,
            created_by=d.created_by,
            updated_by=d.updated_by,
        )

    # ── Employee CRUD ──────────────────────────────────────────────

    def create_employee(self, employee: Employee) -> Result:
        existing_code = self.session.execute(
            select(EmployeeModel).where(EmployeeModel.employee_code == employee.employee_code)
        ).scalar_one_or_none()
        if existing_code:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_CODE_DUPLICATE, code=employee.employee_code,
            ))
        if employee.si_book_number:
            existing_si = self.session.execute(
                select(EmployeeModel).where(EmployeeModel.si_book_number == employee.si_book_number)
            ).scalar_one_or_none()
            if existing_si:
                return Result.failure(VASValidationError(
                    ErrorCodes.PR_SI_BOOK_DUPLICATE, si_book=employee.si_book_number,
                ))
        try:
            model = self._employee_to_model(employee)
            self.session.add(model)
            self.session.flush()
            return Result.success(self._employee_to_domain(model))
        except IntegrityError:
            self.session.rollback()
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_CODE_DUPLICATE, code=employee.employee_code,
            ))

    def get_employee(self, employee_id: int) -> Result:
        m = self.session.get(EmployeeModel, employee_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_NOT_FOUND, id=str(employee_id),
            ))
        return Result.success(self._employee_to_domain(m))

    def get_employee_by_code(self, code: str) -> Result:
        m = self.session.execute(
            select(EmployeeModel).where(EmployeeModel.employee_code == code)
        ).scalar_one_or_none()
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_NOT_FOUND, id=code,
            ))
        return Result.success(self._employee_to_domain(m))

    def update_employee(self, employee: Employee) -> Result:
        m = self.session.get(EmployeeModel, employee.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_NOT_FOUND, id=str(employee.id),
            ))
        m.employee_code = employee.employee_code
        m.full_name = employee.full_name
        m.date_of_birth = employee.date_of_birth
        m.gender = employee.gender
        m.id_number = employee.id_number
        m.id_issue_date = employee.id_issue_date
        m.id_issue_place = employee.id_issue_place
        m.tax_code = employee.tax_code
        m.si_book_number = employee.si_book_number
        m.bank_account = employee.bank_account
        m.bank_name = employee.bank_name
        m.department_id = employee.department_id
        m.department_name = employee.department_name
        m.position = employee.position
        m.region = employee.region.value
        m.dependent_count = employee.dependent_count
        m.status = employee.status.value
        m.start_date = employee.start_date
        m.termination_date = employee.termination_date
        m.updated_by = employee.updated_by
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._employee_to_domain(m))

    def delete_employee(self, employee_id: int) -> Result:
        m = self.session.get(EmployeeModel, employee_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_EMPLOYEE_NOT_FOUND, id=str(employee_id),
            ))
        m.status = EmployeeStatus.TERMINATED.value
        m.termination_date = date.today()
        self.session.flush()
        return Result.success(None)

    def list_employees(self, filters: dict = None, page: int = 1, per_page: int = 20) -> Result:
        f = filters or {}
        stmt = select(EmployeeModel)
        status_val = f.get("status")
        if status_val:
            stmt = stmt.where(EmployeeModel.status == status_val)
        dept_id = f.get("department_id")
        if dept_id is not None:
            stmt = stmt.where(EmployeeModel.department_id == dept_id)
        search = f.get("search")
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    EmployeeModel.employee_code.ilike(pattern),
                    EmployeeModel.full_name.ilike(pattern),
                    EmployeeModel.tax_code.ilike(pattern),
                )
            )
        total = self.session.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar_one()
        stmt = stmt.order_by(EmployeeModel.employee_code)
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        models = self.session.execute(stmt).scalars().all()
        return Result.success({
            "items": [self._employee_to_domain(m) for m in models],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": ceil(total / per_page) if total else 0,
        })

