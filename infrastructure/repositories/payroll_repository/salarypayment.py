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


class SalaryPaymentMixin:
    """Mixin for SalaryPayment-related repository methods."""
    # ── SalaryPayment mappings ─────────────────────────────────────

    def _salary_payment_to_domain(self, m: SalaryPaymentModel) -> SalaryPayment:
        p = SalaryPayment(
            payroll_run_id=m.payroll_run_id,
            payment_date=m.payment_date,
            payment_method=PaymentMethodPR(m.payment_method),
            total_amount=m.total_amount or Decimal("0"),
            bank_transaction_ref=m.bank_transaction_ref,
            notes=m.notes,
            created_at=m.created_at or datetime.now(timezone.utc),
            created_by=m.created_by,
        )
        p.id = m.id
        return p

    def _salary_payment_to_model(self, d: SalaryPayment) -> SalaryPaymentModel:
        return SalaryPaymentModel(
            payroll_run_id=d.payroll_run_id,
            payment_date=d.payment_date,
            payment_method=d.payment_method.value,
            total_amount=d.total_amount,
            bank_transaction_ref=d.bank_transaction_ref,
            notes=d.notes,
            created_by=d.created_by,
        )

    # ── SalaryPayment CRUD ─────────────────────────────────────────

    def create_salary_payment(self, payment: SalaryPayment) -> Result:
        model = self._salary_payment_to_model(payment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._salary_payment_to_domain(model))

    def get_run_payments(self, run_id: int) -> Result:
        models = self.session.execute(
            select(SalaryPaymentModel)
            .where(SalaryPaymentModel.payroll_run_id == run_id)
            .order_by(SalaryPaymentModel.payment_date)
        ).scalars().all()
        return Result.success([self._salary_payment_to_domain(m) for m in models])

