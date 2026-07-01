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


class PositionMixin:
    """Mixin for Position-related repository methods."""
    # ── TreasuryPosition ──────────────────────────────────────────────

    def _pos_to_domain(self, m: TreasuryPositionModel) -> TreasuryPosition:
        d = TreasuryPosition(
            snapshot_date=m.snapshot_date,
            currency=m.currency,
            total_cash=m.total_cash,
            total_bank=m.total_bank,
            total_cash_in_transit=m.total_cash_in_transit,
            total_blocked=m.total_blocked,
            total_available=m.total_available,
            total_investments=m.total_investments,
            total_loans=m.total_loans,
            net_liquidity=m.net_liquidity,
            entity_id=m.entity_id,
            generated_at=m.generated_at,
        )
        d.id = m.id
        return d

    def _pos_to_model(self, d: TreasuryPosition) -> TreasuryPositionModel:
        return TreasuryPositionModel(
            snapshot_date=d.snapshot_date,
            currency=d.currency,
            total_cash=d.total_cash,
            total_bank=d.total_bank,
            total_cash_in_transit=d.total_cash_in_transit,
            total_blocked=d.total_blocked,
            total_available=d.total_available,
            total_investments=d.total_investments,
            total_loans=d.total_loans,
            net_liquidity=d.net_liquidity,
            entity_id=d.entity_id,
        )

    def create_treasury_position(self, pos: TreasuryPosition) -> Result:
        model = self._pos_to_model(pos)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._pos_to_domain(model))

    def get_treasury_position(self, pos_id: int) -> Optional[TreasuryPosition]:
        m = self.session.get(TreasuryPositionModel, pos_id)
        return self._pos_to_domain(m) if m else None

    def get_latest_position(self, entity_id: Optional[str] = None) -> Optional[TreasuryPosition]:
        stmt = select(TreasuryPositionModel).order_by(TreasuryPositionModel.snapshot_date.desc())
        if entity_id:
            stmt = stmt.where(TreasuryPositionModel.entity_id == entity_id)
        stmt = stmt.limit(1)
        m = self.session.execute(stmt).scalars().first()
        return self._pos_to_domain(m) if m else None

    def list_positions(
        self,
        snapshot_date: Optional[date] = None,
        entity_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TreasuryPosition]:
        stmt = select(TreasuryPositionModel)
        if snapshot_date:
            stmt = stmt.where(TreasuryPositionModel.snapshot_date == snapshot_date)
        if entity_id:
            stmt = stmt.where(TreasuryPositionModel.entity_id == entity_id)
        stmt = stmt.order_by(TreasuryPositionModel.snapshot_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._pos_to_domain(m) for m in models]

