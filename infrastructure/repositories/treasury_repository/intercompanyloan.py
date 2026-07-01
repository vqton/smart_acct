from typing import Optional, List, Any, Dict
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, desc

from domain.treasury import (
    CashInTransit, SecurityInvestment, InvestmentTransaction,
    Loan, LoanPayment, FXForward, CashFlowForecast, ForecastLine,
    TreasuryPosition, FXExposure, FXRate,
    IntercompanyLoan, IntercompanySweep,
    PaymentBatch, PaymentBatchItem,
    BankConnectorConfig, BankSyncLog,
    TreasuryPolicy, TreasuryAuditLog,
    InvestmentType, InvestmentStatus, LoanType, LoanStatus,
    FXForwardStatus, SweepType,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd
from infrastructure.models.treasury_models import (
    CashInTransitModel, SecurityInvestmentModel, InvestmentTransactionModel,
    LoanModel, LoanPaymentModel, FXForwardModel,
    CashFlowForecastModel, ForecastLineModel,
    TreasuryPositionModel, FXExposureModel, FXRateModel,
    IntercompanyLoanModel, IntercompanySweepModel,
    PaymentBatchModel, PaymentBatchItemModel,
    BankConnectorConfigModel, BankSyncLogModel,
    TreasuryPolicyModel, TreasuryAuditLogModel,
    InvestmentTypeDB, InvestmentStatusDB, LoanTypeDB, LoanStatusDB,
    SweepTypeDB, ICSweepStatusDB, BatchStatusDB, BatchItemStatusDB,
    SyncStatusDB, FXForwardStatusDB,
)


class IntercompanyLoanMixin:
    """Mixin for IntercompanyLoan-related repository methods."""
    # ── IntercompanyLoan ──────────────────────────────────────────────

    def _ic_loan_to_domain(self, m: IntercompanyLoanModel) -> IntercompanyLoan:
        d = IntercompanyLoan(
            loan_code=m.loan_code,
            lender_entity_id=m.lender_entity_id,
            borrower_entity_id=m.borrower_entity_id,
            principal=m.principal,
            outstanding_balance=m.outstanding_balance,
            interest_rate=m.interest_rate,
            interest_basis=m.interest_basis,
            currency=m.currency,
            start_date=m.start_date,
            maturity_date=m.maturity_date,
            status=m.status,
            coa_receivable_code=m.coa_receivable_code,
            coa_payable_code=m.coa_payable_code,
            agreement_ref=m.agreement_ref,
            transfer_pricing_compliant=m.transfer_pricing_compliant,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _ic_loan_to_model(self, d: IntercompanyLoan) -> IntercompanyLoanModel:
        return IntercompanyLoanModel(
            loan_code=d.loan_code,
            lender_entity_id=d.lender_entity_id,
            borrower_entity_id=d.borrower_entity_id,
            principal=d.principal,
            outstanding_balance=d.outstanding_balance,
            interest_rate=d.interest_rate,
            interest_basis=d.interest_basis,
            currency=d.currency,
            start_date=d.start_date,
            maturity_date=d.maturity_date,
            status=d.status,
            coa_receivable_code=d.coa_receivable_code,
            coa_payable_code=d.coa_payable_code,
            agreement_ref=d.agreement_ref,
            transfer_pricing_compliant=d.transfer_pricing_compliant,
            notes=d.notes,
        )

    def create_ic_loan(self, loan: IntercompanyLoan) -> Result:
        existing = self.session.execute(
            select(IntercompanyLoanModel).where(IntercompanyLoanModel.loan_code == loan.loan_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="IntercompanyLoan", id=loan.loan_code))
        model = self._ic_loan_to_model(loan)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._ic_loan_to_domain(model))

    def get_ic_loan(self, loan_id: int) -> Optional[IntercompanyLoan]:
        m = self.session.get(IntercompanyLoanModel, loan_id)
        return self._ic_loan_to_domain(m) if m else None

    def get_ic_loan_by_code(self, code: str) -> Optional[IntercompanyLoan]:
        m = self.session.execute(
            select(IntercompanyLoanModel).where(IntercompanyLoanModel.loan_code == code)
        ).scalar_one_or_none()
        return self._ic_loan_to_domain(m) if m else None

    def list_ic_loans(
        self,
        lender: Optional[str] = None,
        borrower: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[IntercompanyLoan]:
        stmt = select(IntercompanyLoanModel)
        if lender:
            stmt = stmt.where(IntercompanyLoanModel.lender_entity_id == lender)
        if borrower:
            stmt = stmt.where(IntercompanyLoanModel.borrower_entity_id == borrower)
        if status:
            stmt = stmt.where(IntercompanyLoanModel.status == status)
        stmt = stmt.order_by(IntercompanyLoanModel.start_date.desc())
        models = self.session.execute(stmt).scalars().all()
        return [self._ic_loan_to_domain(m) for m in models]

    def update_ic_loan(self, loan_id: int, **updates) -> Optional[IntercompanyLoan]:
        model = self.session.get(IntercompanyLoanModel, loan_id)
        if not model:
            return None
        allowed = ("principal", "outstanding_balance", "interest_rate",
                   "interest_basis", "currency", "start_date", "maturity_date",
                   "status", "coa_receivable_code", "coa_payable_code",
                   "agreement_ref", "transfer_pricing_compliant", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._ic_loan_to_domain(model)

