"""Treasury repository package - entity-grouped mixins composed into TreasuryRepository."""
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
from .cashintransit import CashInTransitMixin
from .investment import InvestmentMixin
from .loan import LoanMixin
from .loanpayment import LoanPaymentMixin
from .fxforward import FXForwardMixin
from .forecast import ForecastMixin
from .position import PositionMixin
from .fxexposure import FXExposureMixin
from .fxrate import FXRateMixin
from .intercompanyloan import IntercompanyLoanMixin
from .intercompanysweep import IntercompanySweepMixin
from .paymentbatch import PaymentBatchMixin
from .connector import ConnectorMixin
from .policy import PolicyMixin
from .aggregation import AggregationMixin


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class TreasuryRepository(CashInTransitMixin, InvestmentMixin, LoanMixin, LoanPaymentMixin, FXForwardMixin, ForecastMixin, PositionMixin, FXExposureMixin, FXRateMixin, IntercompanyLoanMixin, IntercompanySweepMixin, PaymentBatchMixin, ConnectorMixin, PolicyMixin, AggregationMixin):
    """Treasury repository - composed from entity-grouped mixins."""
    def __init__(self, session: Session):
        self.session = session


