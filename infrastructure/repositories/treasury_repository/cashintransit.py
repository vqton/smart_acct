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


class CashInTransitMixin:
    """Mixin for CashInTransit-related repository methods."""
    # ── CashInTransit ─────────────────────────────────────────────────

    def _cit_to_domain(self, m: CashInTransitModel) -> CashInTransit:
        d = CashInTransit(
            reference=m.reference,
            amount=m.amount,
            currency=m.currency,
            source_account_type=m.source_account_type,
            source_account_id=m.source_account_id,
            dest_account_type=m.dest_account_type,
            dest_account_id=m.dest_account_id,
            transfer_date=m.transfer_date,
            expected_clear_date=m.expected_clear_date,
            cleared=m.cleared,
            cleared_at=m.cleared_at,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _cit_to_model(self, d: CashInTransit) -> CashInTransitModel:
        return CashInTransitModel(
            reference=d.reference,
            amount=d.amount,
            currency=d.currency,
            source_account_type=d.source_account_type,
            source_account_id=d.source_account_id,
            dest_account_type=d.dest_account_type,
            dest_account_id=d.dest_account_id,
            transfer_date=d.transfer_date,
            expected_clear_date=d.expected_clear_date,
            cleared=d.cleared,
            cleared_at=d.cleared_at,
            notes=d.notes,
        )

    def create_cash_in_transit(self, cit: CashInTransit) -> Result:
        existing = self.session.execute(
            select(CashInTransitModel).where(CashInTransitModel.reference == cit.reference)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="CashInTransit", id=cit.reference))
        model = self._cit_to_model(cit)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._cit_to_domain(model))

    def get_cash_in_transit(self, cit_id: int) -> Optional[CashInTransit]:
        m = self.session.get(CashInTransitModel, cit_id)
        return self._cit_to_domain(m) if m else None

    def list_cash_in_transit(
        self, cleared: Optional[bool] = None, limit: int = 50, offset: int = 0,
    ) -> List[CashInTransit]:
        stmt = select(CashInTransitModel)
        if cleared is not None:
            stmt = stmt.where(CashInTransitModel.cleared == cleared)
        stmt = stmt.order_by(CashInTransitModel.transfer_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._cit_to_domain(m) for m in models]

    def update_cash_in_transit(self, cit_id: int, **updates) -> Optional[CashInTransit]:
        model = self.session.get(CashInTransitModel, cit_id)
        if not model:
            return None
        allowed = ("amount", "currency", "source_account_type", "source_account_id",
                   "dest_account_type", "dest_account_id", "transfer_date",
                   "expected_clear_date", "cleared", "cleared_at", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._cit_to_domain(model)

    def mark_cit_cleared(self, cit_id: int, cleared_at: datetime) -> Optional[CashInTransit]:
        return self.update_cash_in_transit(cit_id, cleared=True, cleared_at=cleared_at)

