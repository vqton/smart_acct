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


class ForecastMixin:
    """Mixin for Forecast-related repository methods."""
    # ── CashFlowForecast ──────────────────────────────────────────────

    def _forecast_to_domain(self, m: CashFlowForecastModel) -> CashFlowForecast:
        d = CashFlowForecast(
            forecast_name=m.forecast_name,
            horizon=m.horizon,
            scenario=m.scenario,
            currency=m.currency,
            opening_balance=m.opening_balance,
            total_inflows=m.total_inflows,
            total_outflows=m.total_outflows,
            closing_balance=m.closing_balance,
            min_balance_threshold=m.min_balance_threshold,
            min_balance_breach=m.min_balance_breach,
            surplus_threshold=m.surplus_threshold,
            surplus_identified=m.surplus_identified,
            forecast_date=m.forecast_date,
            period=m.period,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _forecast_to_model(self, d: CashFlowForecast) -> CashFlowForecastModel:
        return CashFlowForecastModel(
            forecast_name=d.forecast_name,
            horizon=d.horizon,
            scenario=d.scenario,
            currency=d.currency,
            opening_balance=d.opening_balance,
            total_inflows=d.total_inflows,
            total_outflows=d.total_outflows,
            closing_balance=d.closing_balance,
            min_balance_threshold=d.min_balance_threshold,
            min_balance_breach=d.min_balance_breach,
            surplus_threshold=d.surplus_threshold,
            surplus_identified=d.surplus_identified,
            forecast_date=d.forecast_date,
            period=d.period,
            notes=d.notes,
        )

    def create_forecast(self, forecast: CashFlowForecast) -> Result:
        model = self._forecast_to_model(forecast)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._forecast_to_domain(model))

    def get_forecast(self, forecast_id: int) -> Optional[CashFlowForecast]:
        m = self.session.get(CashFlowForecastModel, forecast_id)
        return self._forecast_to_domain(m) if m else None

    def list_forecasts(
        self,
        period: Optional[str] = None,
        horizon: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[CashFlowForecast]:
        stmt = select(CashFlowForecastModel)
        if period:
            stmt = stmt.where(CashFlowForecastModel.period == period)
        if horizon:
            stmt = stmt.where(CashFlowForecastModel.horizon == horizon)
        stmt = stmt.order_by(CashFlowForecastModel.forecast_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._forecast_to_domain(m) for m in models]

    def update_forecast(self, forecast_id: int, **updates) -> Optional[CashFlowForecast]:
        model = self.session.get(CashFlowForecastModel, forecast_id)
        if not model:
            return None
        allowed = ("forecast_name", "horizon", "scenario", "currency",
                   "opening_balance", "total_inflows", "total_outflows",
                   "closing_balance", "min_balance_threshold", "min_balance_breach",
                   "surplus_threshold", "surplus_identified", "forecast_date",
                   "period", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._forecast_to_domain(model)

    # ── ForecastLine ──────────────────────────────────────────────────

    def _fcl_to_domain(self, m: ForecastLineModel) -> ForecastLine:
        d = ForecastLine(
            forecast_id=m.forecast_id,
            line_type=m.line_type,
            description=m.description,
            expected_amount=m.expected_amount,
            expected_date=m.expected_date,
            confidence_pct=m.confidence_pct,
            source_module=m.source_module,
            source_reference=m.source_reference,
            is_manual=m.is_manual,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _fcl_to_model(self, d: ForecastLine) -> ForecastLineModel:
        return ForecastLineModel(
            forecast_id=d.forecast_id,
            line_type=d.line_type,
            description=d.description,
            expected_amount=d.expected_amount,
            expected_date=d.expected_date,
            confidence_pct=d.confidence_pct,
            source_module=d.source_module,
            source_reference=d.source_reference,
            is_manual=d.is_manual,
        )

    def add_forecast_line(self, line: ForecastLine) -> Result:
        model = self._fcl_to_model(line)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fcl_to_domain(model))

    def get_forecast_lines(self, forecast_id: int) -> List[ForecastLine]:
        models = self.session.execute(
            select(ForecastLineModel).where(ForecastLineModel.forecast_id == forecast_id)
            .order_by(ForecastLineModel.expected_date)
        ).scalars().all()
        return [self._fcl_to_domain(m) for m in models]

    def update_forecast_line(self, line_id: int, **updates) -> Optional[ForecastLine]:
        model = self.session.get(ForecastLineModel, line_id)
        if not model:
            return None
        allowed = ("line_type", "description", "expected_amount", "expected_date",
                   "confidence_pct", "source_module", "source_reference", "is_manual")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._fcl_to_domain(model)

    def remove_forecast_line(self, line_id: int) -> bool:
        model = self.session.get(ForecastLineModel, line_id)
        if not model:
            return False
        self.session.delete(model)
        return True

