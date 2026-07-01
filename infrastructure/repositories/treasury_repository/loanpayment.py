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


class LoanPaymentMixin:
    """Mixin for LoanPayment-related repository methods."""
    # ── LoanPayment ───────────────────────────────────────────────────

    def _loan_pmt_to_domain(self, m: LoanPaymentModel) -> LoanPayment:
        d = LoanPayment(
            loan_id=m.loan_id,
            payment_date=m.payment_date,
            principal_amount=m.principal_amount,
            interest_amount=m.interest_amount,
            total_amount=m.total_amount,
            is_scheduled=m.is_scheduled,
            is_early_repayment=m.is_early_repayment,
            early_repayment_penalty=m.early_repayment_penalty,
            status=m.status,
            reference=m.reference,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _loan_pmt_to_model(self, d: LoanPayment) -> LoanPaymentModel:
        return LoanPaymentModel(
            loan_id=d.loan_id,
            payment_date=d.payment_date,
            principal_amount=d.principal_amount,
            interest_amount=d.interest_amount,
            total_amount=d.total_amount,
            is_scheduled=d.is_scheduled,
            is_early_repayment=d.is_early_repayment,
            early_repayment_penalty=d.early_repayment_penalty,
            status=d.status,
            reference=d.reference,
        )

    def create_loan_payment(self, payment: LoanPayment) -> Result:
        model = self._loan_pmt_to_model(payment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._loan_pmt_to_domain(model))

    def get_loan_payments(self, loan_id: int) -> List[LoanPayment]:
        models = self.session.execute(
            select(LoanPaymentModel).where(LoanPaymentModel.loan_id == loan_id)
            .order_by(LoanPaymentModel.payment_date)
        ).scalars().all()
        return [self._loan_pmt_to_domain(m) for m in models]

    def get_upcoming_loan_payments(self, days: int = 30) -> List[LoanPayment]:
        from datetime import timedelta
        today = date.today()
        end = today + timedelta(days=days)
        models = self.session.execute(
            select(LoanPaymentModel)
            .where(LoanPaymentModel.payment_date.between(today, end))
            .where(LoanPaymentModel.status == "pending")
            .order_by(LoanPaymentModel.payment_date)
        ).scalars().all()
        return [self._loan_pmt_to_domain(m) for m in models]

    def update_loan_payment(self, payment_id: int, **updates) -> Optional[LoanPayment]:
        model = self.session.get(LoanPaymentModel, payment_id)
        if not model:
            return None
        allowed = ("principal_amount", "interest_amount", "total_amount",
                   "is_scheduled", "is_early_repayment", "early_repayment_penalty",
                   "status", "reference")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._loan_pmt_to_domain(model)

