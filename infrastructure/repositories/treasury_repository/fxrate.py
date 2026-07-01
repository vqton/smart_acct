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


class FXRateMixin:
    """Mixin for FXRate-related repository methods."""
    # ── FXRate ────────────────────────────────────────────────────────

    def _fx_rate_to_domain(self, m: FXRateModel) -> FXRate:
        d = FXRate(
            currency=m.currency,
            rate_date=m.rate_date,
            rate_buying=m.rate_buying,
            rate_selling=m.rate_selling,
            rate_avg=m.rate_avg,
            rate_source=m.rate_source,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _fx_rate_to_model(self, d: FXRate) -> FXRateModel:
        return FXRateModel(
            currency=d.currency,
            rate_date=d.rate_date,
            rate_buying=d.rate_buying,
            rate_selling=d.rate_selling,
            rate_avg=d.rate_avg,
            rate_source=d.rate_source,
        )

    def upsert_fx_rate(self, rate: FXRate) -> Result:
        existing = self.session.execute(
            select(FXRateModel).where(
                FXRateModel.currency == rate.currency,
                FXRateModel.rate_date == rate.rate_date,
                FXRateModel.rate_source == rate.rate_source,
            )
        ).scalar_one_or_none()
        if existing:
            existing.rate_buying = rate.rate_buying
            existing.rate_selling = rate.rate_selling
            existing.rate_avg = rate.rate_avg
            self.session.flush()
            return Result.success(self._fx_rate_to_domain(existing))
        model = self._fx_rate_to_model(rate)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fx_rate_to_domain(model))

    def get_fx_rate(
        self, currency: str, rate_date: date, source: str = "bank_avg",
    ) -> Optional[FXRate]:
        m = self.session.execute(
            select(FXRateModel).where(
                FXRateModel.currency == currency,
                FXRateModel.rate_date == rate_date,
                FXRateModel.rate_source == source,
            )
        ).scalar_one_or_none()
        return self._fx_rate_to_domain(m) if m else None

