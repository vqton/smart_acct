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
from infrastructure.models.cash_models import CashReceiptModel, CashPaymentModel, BankAccountModel



class AggregationMixin:
    """Mixin for Aggregation-related repository methods."""
    # ── Aggregation queries ──────────────────────────────────────────

    def get_total_cash_balance(self) -> Decimal:
        from infrastructure.models.cash_models import CashReceiptModel
        from infrastructure.models.cash_models import CashPaymentModel
        total_in = self.session.execute(
            select(func.coalesce(func.sum(CashReceiptModel.total_amount), Decimal("0")))
            .where(CashReceiptModel.status == "posted")
        ).scalar_one()
        total_out = self.session.execute(
            select(func.coalesce(func.sum(CashPaymentModel.total_amount), Decimal("0")))
            .where(CashPaymentModel.status == "posted")
        ).scalar_one()
        return _vnd(total_in - total_out)

    def get_total_bank_balance(self) -> Decimal:
        from infrastructure.models.cash_models import BankAccountModel
        result = self.session.execute(
            select(func.coalesce(func.sum(BankAccountModel.balance), Decimal("0")))
        ).scalar_one()
        return _vnd(result)

    def get_blocked_amount(self) -> Decimal:
        from infrastructure.models.cash_models import BankAccountModel
        result = self.session.execute(
            select(func.coalesce(func.sum(BankAccountModel.blocked_amount), Decimal("0")))
        ).scalar_one()
        return _vnd(result)
