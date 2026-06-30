from typing import List, Optional, ClassVar, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum

from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd


class InvestmentType(str, Enum):
    TRADING_SECURITY = "trading_security"
    TERM_DEPOSIT = "term_deposit"
    BOND = "bond"
    LOAN_RECEIVABLE = "loan_receivable"
    OTHER_HTM = "other_htm"


class InvestmentStatus(str, Enum):
    ACTIVE = "active"
    MATURED = "matured"
    EARLY_WITHDRAWN = "early_withdrawn"
    SOLD = "sold"
    IMPAIRED = "impaired"


class LoanType(str, Enum):
    BANK_LOAN = "bank_loan"
    BOND_PAYABLE = "bond_payable"
    INTERCOMPANY_LOAN = "intercompany_loan"


class LoanStatus(str, Enum):
    ACTIVE = "active"
    FULLY_PAID = "fully_paid"
    DEFAULTED = "defaulted"
    REFINANCED = "refinanced"


class ForecastHorizon(str, Enum):
    DAY_7 = "7d"
    DAY_30 = "30d"
    DAY_90 = "90d"
    ANNUAL = "annual"


class ScenarioType(str, Enum):
    BEST = "best"
    BASE = "base"
    WORST = "worst"


class FXRateSource(str, Enum):
    SBV = "sbv"
    BANK_AVG = "bank_avg"
    INTERBANK = "interbank"


class SweepType(str, Enum):
    ZERO_BALANCING = "zero_balancing"
    TARGET_BALANCING = "target_balancing"


class ICSweepStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    REVERSED = "reversed"


class BatchStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    PARTIALLY_EXECUTED = "partially_executed"
    EXECUTED = "executed"


class BatchItemStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class SyncStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class ICInterestBasis(str, Enum):
    ACTUAL_365 = "actual/365"
    ACTUAL_360 = "actual/360"
    THIRTY_360 = "30/360"


class TreasuryKPI(str, Enum):
    DAYS_CASH_ON_HAND = "days_cash_on_hand"
    CASH_CONVERSION_CYCLE = "cash_conversion_cycle"
    CURRENT_RATIO = "current_ratio"
    QUICK_RATIO = "quick_ratio"
    DSO = "dso"
    DPO = "dpo"
    LIQUIDITY_COVERAGE = "liquidity_coverage"
    FX_EXPOSURE = "fx_exposure"
    INVESTMENT_YIELD = "investment_yield"
    DEBT_SERVICE_COVERAGE = "debt_service_coverage"
    FORECAST_ACCURACY = "forecast_accuracy"


class FXForwardStatus(str, Enum):
    OPEN = "open"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class CashInTransit(BaseModel):
    id: Optional[int] = None
    reference: str = Field(..., min_length=1, max_length=50)
    amount: Decimal
    currency: str = "VND"
    source_account_type: str = Field(..., max_length=20)
    source_account_id: int
    dest_account_type: str = Field(..., max_length=20)
    dest_account_id: int
    transfer_date: date
    expected_clear_date: date
    cleared: bool = False
    cleared_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class SecurityInvestment(BaseModel):
    id: Optional[int] = None
    investment_code: str = Field(..., min_length=1, max_length=30)
    investment_name: str = Field(..., min_length=1, max_length=300)
    investment_type: InvestmentType = InvestmentType.TRADING_SECURITY
    status: InvestmentStatus = InvestmentStatus.ACTIVE
    quantity: Optional[Decimal] = None
    cost_price: Decimal
    market_price: Optional[Decimal] = None
    total_cost: Decimal
    fair_value: Optional[Decimal] = None
    counterparty_name: Optional[str] = Field(None, max_length=300)
    counterparty_id: Optional[str] = Field(None, max_length=50)
    purchase_date: date
    maturity_date: Optional[date] = None
    interest_rate: Optional[Decimal] = None
    interest_basis: Optional[str] = Field(None, max_length=20)
    coa_code: str = Field(..., max_length=20)
    coa_income_code: str = "515"
    coa_expense_code: str = "635"
    period: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("cost_price", "total_cost", "market_price", "fair_value", "interest_rate")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class InvestmentTransaction(BaseModel):
    id: Optional[int] = None
    investment_id: int
    transaction_type: str = Field(..., max_length=20)
    transaction_date: date
    quantity: Optional[Decimal] = None
    price: Decimal
    total_amount: Decimal
    fee: Decimal = Decimal("0")
    gain_loss: Optional[Decimal] = None
    counterparty_ref: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("price", "total_amount", "fee", "gain_loss")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class Loan(BaseModel):
    id: Optional[int] = None
    loan_code: str = Field(..., min_length=1, max_length=30)
    loan_name: str = Field(..., min_length=1, max_length=300)
    loan_type: LoanType = LoanType.BANK_LOAN
    status: LoanStatus = LoanStatus.ACTIVE
    principal: Decimal
    outstanding_balance: Decimal
    interest_rate: Decimal
    interest_basis: ICInterestBasis = ICInterestBasis.ACTUAL_365
    drawdown_date: date
    maturity_date: date
    repayment_frequency: str = Field(default="monthly", max_length=20)
    repayment_day: int = Field(default=1, ge=1, le=31)
    lender_name: Optional[str] = Field(None, max_length=300)
    lender_id: Optional[str] = Field(None, max_length=50)
    currency: str = "VND"
    coa_code: str = "341"
    coa_interest_code: str = "635"
    covenant_dscr_min: Optional[Decimal] = None
    covenant_icr_min: Optional[Decimal] = None
    covenant_ltv_max: Optional[Decimal] = None
    notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("principal", "outstanding_balance", "interest_rate")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class LoanPayment(BaseModel):
    id: Optional[int] = None
    loan_id: int
    payment_date: date
    principal_amount: Decimal
    interest_amount: Decimal
    total_amount: Decimal
    is_scheduled: bool = True
    is_early_repayment: bool = False
    early_repayment_penalty: Decimal = Decimal("0")
    status: str = "pending"
    reference: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("principal_amount", "interest_amount", "total_amount", "early_repayment_penalty")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class FXForward(BaseModel):
    id: Optional[int] = None
    contract_number: str = Field(..., max_length=50)
    base_currency: str = "VND"
    target_currency: str
    amount: Decimal
    forward_rate: Decimal
    value_date: date
    maturity_date: date
    counterparty: str = Field(..., max_length=200)
    status: FXForwardStatus = FXForwardStatus.OPEN
    settlement_amount: Optional[Decimal] = None
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount", "forward_rate", "settlement_amount")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class CashFlowForecast(BaseModel):
    id: Optional[int] = None
    forecast_name: str = Field(..., max_length=100)
    horizon: ForecastHorizon = ForecastHorizon.DAY_30
    scenario: ScenarioType = ScenarioType.BASE
    currency: str = "VND"
    opening_balance: Decimal
    total_inflows: Decimal = Decimal("0")
    total_outflows: Decimal = Decimal("0")
    closing_balance: Decimal
    min_balance_threshold: Decimal = Decimal("0")
    min_balance_breach: bool = False
    surplus_threshold: Optional[Decimal] = None
    surplus_identified: bool = False
    forecast_date: date
    period: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("opening_balance", "total_inflows", "total_outflows", "closing_balance",
                     "min_balance_threshold", "surplus_threshold")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class ForecastLine(BaseModel):
    id: Optional[int] = None
    forecast_id: int
    line_type: str = Field(..., max_length=50)
    description: str = Field(..., max_length=300)
    expected_amount: Decimal
    expected_date: date
    confidence_pct: int = Field(default=80, ge=0, le=100)
    source_module: Optional[str] = Field(None, max_length=50)
    source_reference: Optional[str] = Field(None, max_length=100)
    is_manual: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("expected_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class TreasuryPosition(BaseModel):
    id: Optional[int] = None
    snapshot_date: date
    currency: str = "VND"
    total_cash: Decimal
    total_bank: Decimal
    total_cash_in_transit: Decimal = Decimal("0")
    total_blocked: Decimal = Decimal("0")
    total_available: Decimal
    total_investments: Decimal = Decimal("0")
    total_loans: Decimal = Decimal("0")
    net_liquidity: Decimal
    entity_id: Optional[str] = Field(None, max_length=50)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("total_cash", "total_bank", "total_cash_in_transit", "total_blocked",
                     "total_available", "total_investments", "total_loans", "net_liquidity")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class FXExposure(BaseModel):
    id: Optional[int] = None
    snapshot_date: date
    currency: str
    total_long: Decimal
    total_short: Decimal
    net_exposure: Decimal
    vnd_equivalent: Decimal
    exchange_rate: Decimal
    rate_source: FXRateSource = FXRateSource.BANK_AVG
    unrealized_gain_loss: Decimal = Decimal("0")
    policy_limit: Optional[Decimal] = None
    threshold_breached: bool = False
    entity_id: Optional[str] = Field(None, max_length=50)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("total_long", "total_short", "net_exposure", "vnd_equivalent",
                     "exchange_rate", "unrealized_gain_loss", "policy_limit")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class FXRate(BaseModel):
    id: Optional[int] = None
    currency: str
    rate_date: date
    rate_buying: Optional[Decimal] = None
    rate_selling: Optional[Decimal] = None
    rate_avg: Decimal
    rate_source: FXRateSource = FXRateSource.BANK_AVG
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("rate_buying", "rate_selling", "rate_avg")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class IntercompanyLoan(BaseModel):
    id: Optional[int] = None
    loan_code: str = Field(..., min_length=1, max_length=30)
    lender_entity_id: str = Field(..., max_length=50)
    borrower_entity_id: str = Field(..., max_length=50)
    principal: Decimal
    outstanding_balance: Decimal
    interest_rate: Decimal
    interest_basis: ICInterestBasis = ICInterestBasis.ACTUAL_365
    currency: str = "VND"
    start_date: date
    maturity_date: date
    status: str = "active"
    coa_receivable_code: str = "1368"
    coa_payable_code: str = "3368"
    agreement_ref: Optional[str] = Field(None, max_length=100)
    transfer_pricing_compliant: bool = True
    notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("principal", "outstanding_balance", "interest_rate")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class IntercompanySweep(BaseModel):
    id: Optional[int] = None
    sweep_type: SweepType = SweepType.ZERO_BALANCING
    status: ICSweepStatus = ICSweepStatus.PENDING
    sweep_date: date
    source_entity_id: str = Field(..., max_length=50)
    target_entity_id: str = Field(..., max_length=50)
    amount: Decimal
    source_acct_type: str = "bank"
    source_acct_id: int
    target_acct_type: str = "bank"
    target_acct_id: int
    target_balance_after: Optional[Decimal] = None
    ic_loan_id: Optional[int] = None
    approved_by: Optional[str] = Field(None, max_length=100)
    executed_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount", "target_balance_after")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class PaymentBatch(BaseModel):
    id: Optional[int] = None
    batch_code: str = Field(..., min_length=1, max_length=30)
    status: BatchStatus = BatchStatus.DRAFT
    payment_date: date
    currency: str = "VND"
    total_amount: Decimal
    item_count: int = 0
    approved_by: Optional[str] = Field(None, max_length=100)
    approved_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    bank_ref: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("total_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class PaymentBatchItem(BaseModel):
    id: Optional[int] = None
    batch_id: int
    source_module: str = Field(..., max_length=50)
    source_id: int
    source_reference: str = Field(..., max_length=50)
    payee_name: str = Field(..., max_length=300)
    payee_account: Optional[str] = Field(None, max_length=50)
    payee_bank: Optional[str] = Field(None, max_length=100)
    amount: Decimal
    currency: str = "VND"
    status: BatchItemStatus = BatchItemStatus.PENDING
    bank_txn_ref: Optional[str] = Field(None, max_length=100)
    rejection_reason: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class BankConnectorConfig(BaseModel):
    id: Optional[int] = None
    bank_code: str = Field(..., max_length=20)
    bank_name: str = Field(..., max_length=200)
    api_endpoint: Optional[str] = Field(None, max_length=500)
    api_version: Optional[str] = Field(None, max_length=20)
    auth_type: str = "api_key"
    credentials_encrypted: Optional[str] = None
    sync_frequency_minutes: int = 60
    last_sync_at: Optional[datetime] = None
    is_active: bool = True
    supports_balance: bool = True
    supports_transactions: bool = True
    supports_statements: bool = True
    ip_whitelist: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class BankSyncLog(BaseModel):
    id: Optional[int] = None
    connector_id: int
    sync_type: str = Field(..., max_length=50)
    sync_status: SyncStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    transactions_fetched: int = 0
    transactions_matched: int = 0
    transactions_unmatched: int = 0
    error_message: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TreasuryPolicy(BaseModel):
    id: Optional[int] = None
    policy_code: str = Field(..., min_length=1, max_length=30)
    policy_name: str = Field(..., min_length=1, max_length=300)
    policy_type: str = Field(..., max_length=50)
    threshold_value: Optional[Decimal] = None
    threshold_pct: Optional[Decimal] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    counterparty_restriction: Optional[str] = Field(None, max_length=500)
    active: bool = True
    notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("threshold_value", "threshold_pct", "min_value", "max_value")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class TreasuryAuditLog(BaseModel):
    id: Optional[int] = None
    entity_type: str = Field(..., max_length=50)
    entity_id: int
    action: str = Field(..., max_length=50)
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    performed_by: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
