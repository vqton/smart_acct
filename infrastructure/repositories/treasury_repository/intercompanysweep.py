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


class IntercompanySweepMixin:
    """Mixin for IntercompanySweep-related repository methods."""
    # ── IntercompanySweep ─────────────────────────────────────────────

    def _ic_sweep_to_domain(self, m: IntercompanySweepModel) -> IntercompanySweep:
        d = IntercompanySweep(
            sweep_type=SweepType(m.sweep_type),
            status=m.status,
            sweep_date=m.sweep_date,
            source_entity_id=m.source_entity_id,
            target_entity_id=m.target_entity_id,
            amount=m.amount,
            source_acct_type=m.source_acct_type,
            source_acct_id=m.source_acct_id,
            target_acct_type=m.target_acct_type,
            target_acct_id=m.target_acct_id,
            target_balance_after=m.target_balance_after,
            ic_loan_id=m.ic_loan_id,
            approved_by=m.approved_by,
            executed_at=m.executed_at,
            notes=m.notes,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _ic_sweep_to_model(self, d: IntercompanySweep) -> IntercompanySweepModel:
        return IntercompanySweepModel(
            sweep_type=d.sweep_type.value,
            status=d.status.value if hasattr(d.status, 'value') else d.status,
            sweep_date=d.sweep_date,
            source_entity_id=d.source_entity_id,
            target_entity_id=d.target_entity_id,
            amount=d.amount,
            source_acct_type=d.source_acct_type,
            source_acct_id=d.source_acct_id,
            target_acct_type=d.target_acct_type,
            target_acct_id=d.target_acct_id,
            target_balance_after=d.target_balance_after,
            ic_loan_id=d.ic_loan_id,
            approved_by=d.approved_by,
            executed_at=d.executed_at,
            notes=d.notes,
        )

    def create_ic_sweep(self, sweep: IntercompanySweep) -> Result:
        model = self._ic_sweep_to_model(sweep)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._ic_sweep_to_domain(model))

    def get_ic_sweep(self, sweep_id: int) -> Optional[IntercompanySweep]:
        m = self.session.get(IntercompanySweepModel, sweep_id)
        return self._ic_sweep_to_domain(m) if m else None

    def list_ic_sweeps(
        self,
        entity_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[IntercompanySweep]:
        stmt = select(IntercompanySweepModel)
        if entity_id:
            stmt = stmt.where(
                (IntercompanySweepModel.source_entity_id == entity_id) |
                (IntercompanySweepModel.target_entity_id == entity_id)
            )
        if status:
            stmt = stmt.where(IntercompanySweepModel.status == status)
        stmt = stmt.order_by(IntercompanySweepModel.sweep_date.desc()).limit(limit)
        models = self.session.execute(stmt).scalars().all()
        return [self._ic_sweep_to_domain(m) for m in models]

    def update_ic_sweep(self, sweep_id: int, **updates) -> Optional[IntercompanySweep]:
        model = self.session.get(IntercompanySweepModel, sweep_id)
        if not model:
            return None
        allowed = ("sweep_type", "status", "sweep_date", "source_entity_id",
                   "target_entity_id", "amount", "source_acct_type", "source_acct_id",
                   "target_acct_type", "target_acct_id", "target_balance_after",
                   "ic_loan_id", "approved_by", "executed_at", "notes")
        for k, v in updates.items():
            if k in allowed:
                if isinstance(v, SweepType):
                    setattr(model, k, v.value)
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._ic_sweep_to_domain(model)

