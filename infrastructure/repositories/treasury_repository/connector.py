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


class ConnectorMixin:
    """Mixin for Connector-related repository methods."""
    # ── BankConnectorConfig ───────────────────────────────────────────

    def _connector_to_domain(self, m: BankConnectorConfigModel) -> BankConnectorConfig:
        d = BankConnectorConfig(
            bank_code=m.bank_code,
            bank_name=m.bank_name,
            api_endpoint=m.api_endpoint,
            api_version=m.api_version,
            auth_type=m.auth_type,
            credentials_encrypted=m.credentials_encrypted,
            sync_frequency_minutes=m.sync_frequency_minutes,
            last_sync_at=m.last_sync_at,
            is_active=m.is_active,
            supports_balance=m.supports_balance,
            supports_transactions=m.supports_transactions,
            supports_statements=m.supports_statements,
            ip_whitelist=m.ip_whitelist,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _connector_to_model(self, d: BankConnectorConfig) -> BankConnectorConfigModel:
        return BankConnectorConfigModel(
            bank_code=d.bank_code,
            bank_name=d.bank_name,
            api_endpoint=d.api_endpoint,
            api_version=d.api_version,
            auth_type=d.auth_type,
            credentials_encrypted=d.credentials_encrypted,
            sync_frequency_minutes=d.sync_frequency_minutes,
            last_sync_at=d.last_sync_at,
            is_active=d.is_active,
            supports_balance=d.supports_balance,
            supports_transactions=d.supports_transactions,
            supports_statements=d.supports_statements,
            ip_whitelist=d.ip_whitelist,
        )

    def create_connector(self, config: BankConnectorConfig) -> Result:
        existing = self.session.execute(
            select(BankConnectorConfigModel).where(BankConnectorConfigModel.bank_code == config.bank_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="BankConnectorConfig", id=config.bank_code))
        model = self._connector_to_model(config)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._connector_to_domain(model))

    def get_connector(self, connector_id: int) -> Optional[BankConnectorConfig]:
        m = self.session.get(BankConnectorConfigModel, connector_id)
        return self._connector_to_domain(m) if m else None

    def get_connector_by_code(self, code: str) -> Optional[BankConnectorConfig]:
        m = self.session.execute(
            select(BankConnectorConfigModel).where(BankConnectorConfigModel.bank_code == code)
        ).scalar_one_or_none()
        return self._connector_to_domain(m) if m else None

    def list_connectors(self, active_only: bool = False) -> List[BankConnectorConfig]:
        stmt = select(BankConnectorConfigModel)
        if active_only:
            stmt = stmt.where(BankConnectorConfigModel.is_active.is_(True))
        stmt = stmt.order_by(BankConnectorConfigModel.bank_code)
        models = self.session.execute(stmt).scalars().all()
        return [self._connector_to_domain(m) for m in models]

    def update_connector(self, connector_id: int, **updates) -> Optional[BankConnectorConfig]:
        model = self.session.get(BankConnectorConfigModel, connector_id)
        if not model:
            return None
        allowed = ("bank_name", "api_endpoint", "api_version", "auth_type",
                   "credentials_encrypted", "sync_frequency_minutes", "last_sync_at",
                   "is_active", "supports_balance", "supports_transactions",
                   "supports_statements", "ip_whitelist")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._connector_to_domain(model)

    # ── BankSyncLog ───────────────────────────────────────────────────

    def _sync_log_to_domain(self, m: BankSyncLogModel) -> BankSyncLog:
        d = BankSyncLog(
            connector_id=m.connector_id,
            sync_type=m.sync_type,
            sync_status=m.sync_status,
            started_at=m.started_at,
            completed_at=m.completed_at,
            transactions_fetched=m.transactions_fetched,
            transactions_matched=m.transactions_matched,
            transactions_unmatched=m.transactions_unmatched,
            error_message=m.error_message,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _sync_log_to_model(self, d: BankSyncLog) -> BankSyncLogModel:
        return BankSyncLogModel(
            connector_id=d.connector_id,
            sync_type=d.sync_type,
            sync_status=d.sync_status.value if hasattr(d.sync_status, 'value') else d.sync_status,
            started_at=d.started_at,
            completed_at=d.completed_at,
            transactions_fetched=d.transactions_fetched,
            transactions_matched=d.transactions_matched,
            transactions_unmatched=d.transactions_unmatched,
            error_message=d.error_message,
        )

    def create_sync_log(self, log: BankSyncLog) -> Result:
        model = self._sync_log_to_model(log)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._sync_log_to_domain(model))

    def get_sync_logs(self, connector_id: int, limit: int = 50) -> List[BankSyncLog]:
        models = self.session.execute(
            select(BankSyncLogModel).where(BankSyncLogModel.connector_id == connector_id)
            .order_by(BankSyncLogModel.started_at.desc()).limit(limit)
        ).scalars().all()
        return [self._sync_log_to_domain(m) for m in models]

