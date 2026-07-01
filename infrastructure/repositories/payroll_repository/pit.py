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


class PITMixin:
    """Mixin for PIT-related repository methods."""
    # ── PITDeclaration mappings ────────────────────────────────────

    def _pit_declaration_to_domain(self, m: PITDeclarationModel) -> PITDeclaration:
        d = PITDeclaration(
            declaration_type=DeclarationType(m.declaration_type),
            period_month=m.period_month,
            period_quarter=m.period_quarter,
            period_year=m.period_year,
            submission_type=m.submission_type or "initial",
            status=DeclarationStatus(m.status) if m.status else DeclarationStatus.DRAFT,
            total_income=m.total_income or Decimal("0"),
            total_exempt_income=m.total_exempt_income or Decimal("0"),
            total_deductions=m.total_deductions or Decimal("0"),
            total_personal_relief=m.total_personal_relief or Decimal("0"),
            total_dependent_relief=m.total_dependent_relief or Decimal("0"),
            total_taxable_income=m.total_taxable_income or Decimal("0"),
            total_pit=m.total_pit or Decimal("0"),
            total_pit_withheld=m.total_pit_withheld or Decimal("0"),
            total_pit_paid=m.total_pit_paid or Decimal("0"),
            submission_date=m.submission_date,
            tax_authority_response=m.tax_authority_response,
            created_at=m.created_at or datetime.now(timezone.utc),
            updated_at=m.updated_at or datetime.now(timezone.utc),
            created_by=m.created_by,
        )
        d.id = m.id
        return d

    def _pit_declaration_to_model(self, d: PITDeclaration) -> PITDeclarationModel:
        return PITDeclarationModel(
            declaration_type=d.declaration_type.value,
            period_month=d.period_month,
            period_quarter=d.period_quarter,
            period_year=d.period_year,
            submission_type=d.submission_type,
            status=d.status.value,
            total_income=d.total_income,
            total_exempt_income=d.total_exempt_income,
            total_deductions=d.total_deductions,
            total_personal_relief=d.total_personal_relief,
            total_dependent_relief=d.total_dependent_relief,
            total_taxable_income=d.total_taxable_income,
            total_pit=d.total_pit,
            total_pit_withheld=d.total_pit_withheld,
            total_pit_paid=d.total_pit_paid,
            submission_date=d.submission_date,
            tax_authority_response=d.tax_authority_response,
            created_by=d.created_by,
        )

    # ── PITDeclaration CRUD ────────────────────────────────────────

    def create_pit_declaration(self, decl: PITDeclaration) -> Result:
        model = self._pit_declaration_to_model(decl)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._pit_declaration_to_domain(model))

    def get_pit_declaration(self, decl_id: int) -> Result:
        m = self.session.get(PITDeclarationModel, decl_id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PIT_DECLARATION_NOT_FOUND, id=str(decl_id),
            ))
        return Result.success(self._pit_declaration_to_domain(m))

    def update_pit_declaration(self, decl: PITDeclaration) -> Result:
        m = self.session.get(PITDeclarationModel, decl.id)
        if not m:
            return Result.failure(VASValidationError(
                ErrorCodes.PR_PIT_DECLARATION_NOT_FOUND, id=str(decl.id),
            ))
        m.declaration_type = decl.declaration_type.value
        m.period_month = decl.period_month
        m.period_quarter = decl.period_quarter
        m.period_year = decl.period_year
        m.submission_type = decl.submission_type
        m.status = decl.status.value
        m.total_income = decl.total_income
        m.total_exempt_income = decl.total_exempt_income
        m.total_deductions = decl.total_deductions
        m.total_personal_relief = decl.total_personal_relief
        m.total_dependent_relief = decl.total_dependent_relief
        m.total_taxable_income = decl.total_taxable_income
        m.total_pit = decl.total_pit
        m.total_pit_withheld = decl.total_pit_withheld
        m.total_pit_paid = decl.total_pit_paid
        m.submission_date = decl.submission_date
        m.tax_authority_response = decl.tax_authority_response
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._pit_declaration_to_domain(m))

    def list_pit_declarations(self, filters: dict = None) -> Result:
        f = filters or {}
        stmt = select(PITDeclarationModel).order_by(desc(PITDeclarationModel.created_at))
        status_val = f.get("status")
        if status_val:
            stmt = stmt.where(PITDeclarationModel.status == status_val)
        year_val = f.get("period_year")
        if year_val is not None:
            stmt = stmt.where(PITDeclarationModel.period_year == year_val)
        decl_type = f.get("declaration_type")
        if decl_type:
            stmt = stmt.where(PITDeclarationModel.declaration_type == decl_type)
        models = self.session.execute(stmt).scalars().all()
        return Result.success([self._pit_declaration_to_domain(m) for m in models])

