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


class LoanMixin:
    """Mixin for Loan-related repository methods."""
    # ── Loan ──────────────────────────────────────────────────────────

    def _loan_to_domain(self, m: LoanModel) -> Loan:
        d = Loan(
            loan_code=m.loan_code,
            loan_name=m.loan_name,
            loan_type=LoanType(m.loan_type),
            status=LoanStatus(m.status),
            principal=m.principal,
            outstanding_balance=m.outstanding_balance,
            interest_rate=m.interest_rate,
            interest_basis=m.interest_basis,
            drawdown_date=m.drawdown_date,
            maturity_date=m.maturity_date,
            repayment_frequency=m.repayment_frequency,
            repayment_day=m.repayment_day,
            lender_name=m.lender_name,
            lender_id=m.lender_id,
            currency=m.currency,
            coa_code=m.coa_code,
            coa_interest_code=m.coa_interest_code,
            covenant_dscr_min=m.covenant_dscr_min,
            covenant_icr_min=m.covenant_icr_min,
            covenant_ltv_max=m.covenant_ltv_max,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _loan_to_model(self, d: Loan) -> LoanModel:
        return LoanModel(
            loan_code=d.loan_code,
            loan_name=d.loan_name,
            loan_type=d.loan_type.value,
            status=d.status.value,
            principal=d.principal,
            outstanding_balance=d.outstanding_balance,
            interest_rate=d.interest_rate,
            interest_basis=d.interest_basis,
            drawdown_date=d.drawdown_date,
            maturity_date=d.maturity_date,
            repayment_frequency=d.repayment_frequency,
            repayment_day=d.repayment_day,
            lender_name=d.lender_name,
            lender_id=d.lender_id,
            currency=d.currency,
            coa_code=d.coa_code,
            coa_interest_code=d.coa_interest_code,
            covenant_dscr_min=d.covenant_dscr_min,
            covenant_icr_min=d.covenant_icr_min,
            covenant_ltv_max=d.covenant_ltv_max,
            notes=d.notes,
        )

    def create_loan(self, loan: Loan) -> Result:
        existing = self.session.execute(
            select(LoanModel).where(LoanModel.loan_code == loan.loan_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="Loan", id=loan.loan_code))
        model = self._loan_to_model(loan)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._loan_to_domain(model))

    def get_loan(self, loan_id: int) -> Optional[Loan]:
        m = self.session.get(LoanModel, loan_id)
        return self._loan_to_domain(m) if m else None

    def get_loan_by_code(self, code: str) -> Optional[Loan]:
        m = self.session.execute(
            select(LoanModel).where(LoanModel.loan_code == code)
        ).scalar_one_or_none()
        return self._loan_to_domain(m) if m else None

    def list_loans(
        self,
        loan_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Loan]:
        stmt = select(LoanModel)
        if loan_type:
            stmt = stmt.where(LoanModel.loan_type == loan_type)
        if status:
            stmt = stmt.where(LoanModel.status == status)
        stmt = stmt.order_by(LoanModel.drawdown_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._loan_to_domain(m) for m in models]

    def update_loan(self, loan_id: int, **updates) -> Optional[Loan]:
        model = self.session.get(LoanModel, loan_id)
        if not model:
            return None
        allowed = ("loan_name", "loan_type", "status", "principal",
                   "outstanding_balance", "interest_rate", "interest_basis",
                   "drawdown_date", "maturity_date", "repayment_frequency",
                   "repayment_day", "lender_name", "lender_id", "currency",
                   "coa_code", "coa_interest_code",
                   "covenant_dscr_min", "covenant_icr_min", "covenant_ltv_max", "notes")
        for k, v in updates.items():
            if k in allowed:
                if isinstance(v, (LoanType, LoanStatus)):
                    setattr(model, k, v.value)
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._loan_to_domain(model)

    def get_total_outstanding_loans(self) -> Decimal:
        result = self.session.execute(
            select(func.coalesce(func.sum(LoanModel.outstanding_balance), Decimal("0")))
            .where(LoanModel.status.in_(["active", "refinanced"]))
        ).scalar_one()
        return _vnd(result)

