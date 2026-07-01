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


class PaymentBatchMixin:
    """Mixin for PaymentBatch-related repository methods."""
    # ── PaymentBatch ──────────────────────────────────────────────────

    def _batch_to_domain(self, m: PaymentBatchModel) -> PaymentBatch:
        d = PaymentBatch(
            batch_code=m.batch_code,
            status=m.status,
            payment_date=m.payment_date,
            currency=m.currency,
            total_amount=m.total_amount,
            item_count=m.item_count,
            approved_by=m.approved_by,
            approved_at=m.approved_at,
            submitted_at=m.submitted_at,
            bank_ref=m.bank_ref,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _batch_to_model(self, d: PaymentBatch) -> PaymentBatchModel:
        return PaymentBatchModel(
            batch_code=d.batch_code,
            status=d.status.value if hasattr(d.status, 'value') else d.status,
            payment_date=d.payment_date,
            currency=d.currency,
            total_amount=d.total_amount,
            item_count=d.item_count,
            approved_by=d.approved_by,
            approved_at=d.approved_at,
            submitted_at=d.submitted_at,
            bank_ref=d.bank_ref,
            notes=d.notes,
        )

    def create_payment_batch(self, batch: PaymentBatch) -> Result:
        existing = self.session.execute(
            select(PaymentBatchModel).where(PaymentBatchModel.batch_code == batch.batch_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="PaymentBatch", id=batch.batch_code))
        model = self._batch_to_model(batch)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._batch_to_domain(model))

    def get_payment_batch(self, batch_id: int) -> Optional[PaymentBatch]:
        m = self.session.get(PaymentBatchModel, batch_id)
        return self._batch_to_domain(m) if m else None

    def get_payment_batch_by_code(self, code: str) -> Optional[PaymentBatch]:
        m = self.session.execute(
            select(PaymentBatchModel).where(PaymentBatchModel.batch_code == code)
        ).scalar_one_or_none()
        return self._batch_to_domain(m) if m else None

    def list_payment_batches(
        self, status: Optional[str] = None, limit: int = 50, offset: int = 0,
    ) -> List[PaymentBatch]:
        stmt = select(PaymentBatchModel)
        if status:
            stmt = stmt.where(PaymentBatchModel.status == status)
        stmt = stmt.order_by(PaymentBatchModel.payment_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._batch_to_domain(m) for m in models]

    def update_payment_batch(self, batch_id: int, **updates) -> Optional[PaymentBatch]:
        model = self.session.get(PaymentBatchModel, batch_id)
        if not model:
            return None
        allowed = ("status", "payment_date", "currency", "total_amount",
                   "item_count", "approved_by", "approved_at", "submitted_at",
                   "bank_ref", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._batch_to_domain(model)

    # ── PaymentBatchItem ──────────────────────────────────────────────

    def _batch_item_to_domain(self, m: PaymentBatchItemModel) -> PaymentBatchItem:
        d = PaymentBatchItem(
            batch_id=m.batch_id,
            source_module=m.source_module,
            source_id=m.source_id,
            source_reference=m.source_reference,
            payee_name=m.payee_name,
            payee_account=m.payee_account,
            payee_bank=m.payee_bank,
            amount=m.amount,
            currency=m.currency,
            status=m.status,
            bank_txn_ref=m.bank_txn_ref,
            rejection_reason=m.rejection_reason,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _batch_item_to_model(self, d: PaymentBatchItem) -> PaymentBatchItemModel:
        return PaymentBatchItemModel(
            batch_id=d.batch_id,
            source_module=d.source_module,
            source_id=d.source_id,
            source_reference=d.source_reference,
            payee_name=d.payee_name,
            payee_account=d.payee_account,
            payee_bank=d.payee_bank,
            amount=d.amount,
            currency=d.currency,
            status=d.status.value if hasattr(d.status, 'value') else d.status,
            bank_txn_ref=d.bank_txn_ref,
            rejection_reason=d.rejection_reason,
        )

    def add_batch_item(self, item: PaymentBatchItem) -> Result:
        model = self._batch_item_to_model(item)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._batch_item_to_domain(model))

    def get_batch_items(self, batch_id: int) -> List[PaymentBatchItem]:
        models = self.session.execute(
            select(PaymentBatchItemModel).where(PaymentBatchItemModel.batch_id == batch_id)
            .order_by(PaymentBatchItemModel.created_at)
        ).scalars().all()
        return [self._batch_item_to_domain(m) for m in models]

    def update_batch_item(self, item_id: int, **updates) -> Optional[PaymentBatchItem]:
        model = self.session.get(PaymentBatchItemModel, item_id)
        if not model:
            return None
        allowed = ("status", "bank_txn_ref", "rejection_reason", "payee_name",
                   "payee_account", "payee_bank", "amount", "currency")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._batch_item_to_domain(model)

