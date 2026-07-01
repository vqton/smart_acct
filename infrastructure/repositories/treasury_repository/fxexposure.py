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


class FXExposureMixin:
    """Mixin for FXExposure-related repository methods."""
    # ── FXExposure ────────────────────────────────────────────────────

    def _fx_exp_to_domain(self, m: FXExposureModel) -> FXExposure:
        d = FXExposure(
            snapshot_date=m.snapshot_date,
            currency=m.currency,
            total_long=m.total_long,
            total_short=m.total_short,
            net_exposure=m.net_exposure,
            vnd_equivalent=m.vnd_equivalent,
            exchange_rate=m.exchange_rate,
            rate_source=m.rate_source,
            unrealized_gain_loss=m.unrealized_gain_loss,
            policy_limit=m.policy_limit,
            threshold_breached=m.threshold_breached,
            entity_id=m.entity_id,
            generated_at=m.generated_at,
        )
        d.id = m.id
        return d

    def _fx_exp_to_model(self, d: FXExposure) -> FXExposureModel:
        return FXExposureModel(
            snapshot_date=d.snapshot_date,
            currency=d.currency,
            total_long=d.total_long,
            total_short=d.total_short,
            net_exposure=d.net_exposure,
            vnd_equivalent=d.vnd_equivalent,
            exchange_rate=d.exchange_rate,
            rate_source=d.rate_source,
            unrealized_gain_loss=d.unrealized_gain_loss,
            policy_limit=d.policy_limit,
            threshold_breached=d.threshold_breached,
            entity_id=d.entity_id,
        )

    def create_fx_exposure(self, fx: FXExposure) -> Result:
        model = self._fx_exp_to_model(fx)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fx_exp_to_domain(model))

    def get_latest_fx_exposure(
        self, currency: str, entity_id: Optional[str] = None,
    ) -> Optional[FXExposure]:
        stmt = select(FXExposureModel).where(
            FXExposureModel.currency == currency
        ).order_by(FXExposureModel.snapshot_date.desc())
        if entity_id:
            stmt = stmt.where(FXExposureModel.entity_id == entity_id)
        stmt = stmt.limit(1)
        m = self.session.execute(stmt).scalars().first()
        return self._fx_exp_to_domain(m) if m else None

    def list_fx_exposures(
        self, snapshot_date: Optional[date] = None,
    ) -> List[FXExposure]:
        stmt = select(FXExposureModel)
        if snapshot_date:
            stmt = stmt.where(FXExposureModel.snapshot_date == snapshot_date)
        stmt = stmt.order_by(FXExposureModel.currency)
        models = self.session.execute(stmt).scalars().all()
        return [self._fx_exp_to_domain(m) for m in models]

