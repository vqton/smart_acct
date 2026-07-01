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


class PolicyMixin:
    """Mixin for Policy-related repository methods."""
    # ── TreasuryPolicy ────────────────────────────────────────────────

    def _policy_to_domain(self, m: TreasuryPolicyModel) -> TreasuryPolicy:
        d = TreasuryPolicy(
            policy_code=m.policy_code,
            policy_name=m.policy_name,
            policy_type=m.policy_type,
            threshold_value=m.threshold_value,
            threshold_pct=m.threshold_pct,
            min_value=m.min_value,
            max_value=m.max_value,
            counterparty_restriction=m.counterparty_restriction,
            active=m.active,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _policy_to_model(self, d: TreasuryPolicy) -> TreasuryPolicyModel:
        return TreasuryPolicyModel(
            policy_code=d.policy_code,
            policy_name=d.policy_name,
            policy_type=d.policy_type,
            threshold_value=d.threshold_value,
            threshold_pct=d.threshold_pct,
            min_value=d.min_value,
            max_value=d.max_value,
            counterparty_restriction=d.counterparty_restriction,
            active=d.active,
            notes=d.notes,
        )

    def create_policy(self, policy: TreasuryPolicy) -> Result:
        existing = self.session.execute(
            select(TreasuryPolicyModel).where(TreasuryPolicyModel.policy_code == policy.policy_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="TreasuryPolicy", id=policy.policy_code))
        model = self._policy_to_model(policy)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._policy_to_domain(model))

    def get_policy(self, policy_id: int) -> Optional[TreasuryPolicy]:
        m = self.session.get(TreasuryPolicyModel, policy_id)
        return self._policy_to_domain(m) if m else None

    def get_policy_by_code(self, code: str) -> Optional[TreasuryPolicy]:
        m = self.session.execute(
            select(TreasuryPolicyModel).where(TreasuryPolicyModel.policy_code == code)
        ).scalar_one_or_none()
        return self._policy_to_domain(m) if m else None

    def list_policies(
        self,
        policy_type: Optional[str] = None,
        active_only: bool = False,
    ) -> List[TreasuryPolicy]:
        stmt = select(TreasuryPolicyModel)
        if policy_type:
            stmt = stmt.where(TreasuryPolicyModel.policy_type == policy_type)
        if active_only:
            stmt = stmt.where(TreasuryPolicyModel.active.is_(True))
        stmt = stmt.order_by(TreasuryPolicyModel.policy_code)
        models = self.session.execute(stmt).scalars().all()
        return [self._policy_to_domain(m) for m in models]

    def update_policy(self, policy_id: int, **updates) -> Optional[TreasuryPolicy]:
        model = self.session.get(TreasuryPolicyModel, policy_id)
        if not model:
            return None
        allowed = ("policy_name", "policy_type", "threshold_value", "threshold_pct",
                   "min_value", "max_value", "counterparty_restriction", "active", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._policy_to_domain(model)

    # ── TreasuryAuditLog ──────────────────────────────────────────────

    def _audit_to_domain(self, m: TreasuryAuditLogModel) -> TreasuryAuditLog:
        d = TreasuryAuditLog(
            entity_type=m.entity_type,
            entity_id=m.entity_id,
            action=m.action,
            old_value=m.old_value,
            new_value=m.new_value,
            performed_by=m.performed_by,
            notes=m.notes,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def log_audit(self, audit: TreasuryAuditLog) -> Result:
        model = TreasuryAuditLogModel(
            entity_type=audit.entity_type,
            entity_id=audit.entity_id,
            action=audit.action,
            old_value=audit.old_value,
            new_value=audit.new_value,
            performed_by=audit.performed_by,
            notes=audit.notes,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._audit_to_domain(model))

    def get_audit_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[TreasuryAuditLog]:
        stmt = select(TreasuryAuditLogModel)
        if entity_type:
            stmt = stmt.where(TreasuryAuditLogModel.entity_type == entity_type)
        if entity_id is not None:
            stmt = stmt.where(TreasuryAuditLogModel.entity_id == entity_id)
        stmt = stmt.order_by(TreasuryAuditLogModel.created_at.desc()).limit(limit)
        models = self.session.execute(stmt).scalars().all()
        return [self._audit_to_domain(m) for m in models]

