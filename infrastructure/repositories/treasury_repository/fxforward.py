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


class FXForwardMixin:
    """Mixin for FXForward-related repository methods."""
    # ── FXForward ─────────────────────────────────────────────────────

    def _fxfwd_to_domain(self, m: FXForwardModel) -> FXForward:
        d = FXForward(
            contract_number=m.contract_number,
            base_currency=m.base_currency,
            target_currency=m.target_currency,
            amount=m.amount,
            forward_rate=m.forward_rate,
            value_date=m.value_date,
            maturity_date=m.maturity_date,
            counterparty=m.counterparty,
            status=FXForwardStatus(m.status),
            settlement_amount=m.settlement_amount,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _fxfwd_to_model(self, d: FXForward) -> FXForwardModel:
        return FXForwardModel(
            contract_number=d.contract_number,
            base_currency=d.base_currency,
            target_currency=d.target_currency,
            amount=d.amount,
            forward_rate=d.forward_rate,
            value_date=d.value_date,
            maturity_date=d.maturity_date,
            counterparty=d.counterparty,
            status=d.status.value,
            settlement_amount=d.settlement_amount,
            notes=d.notes,
        )

    def create_fx_forward(self, ff: FXForward) -> Result:
        existing = self.session.execute(
            select(FXForwardModel).where(FXForwardModel.contract_number == ff.contract_number)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="FXForward", id=ff.contract_number))
        model = self._fxfwd_to_model(ff)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fxfwd_to_domain(model))

    def get_fx_forward(self, fx_id: int) -> Optional[FXForward]:
        m = self.session.get(FXForwardModel, fx_id)
        return self._fxfwd_to_domain(m) if m else None

    def list_fx_forwards(
        self, status: Optional[str] = None, limit: int = 50, offset: int = 0,
    ) -> List[FXForward]:
        stmt = select(FXForwardModel)
        if status:
            stmt = stmt.where(FXForwardModel.status == status)
        stmt = stmt.order_by(FXForwardModel.value_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._fxfwd_to_domain(m) for m in models]

    def update_fx_forward(self, fx_id: int, **updates) -> Optional[FXForward]:
        model = self.session.get(FXForwardModel, fx_id)
        if not model:
            return None
        allowed = ("base_currency", "target_currency", "amount", "forward_rate",
                   "value_date", "maturity_date", "counterparty", "status",
                   "settlement_amount", "notes")
        for k, v in updates.items():
            if k in allowed:
                if isinstance(v, FXForwardStatus):
                    setattr(model, k, v.value)
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._fxfwd_to_domain(model)

