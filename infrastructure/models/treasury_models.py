from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal

from infrastructure.models.coa_models import Base


class InvestmentTypeDB(str, SAEnum):
    TRADING_SECURITY = "trading_security"
    TERM_DEPOSIT = "term_deposit"
    BOND = "bond"
    LOAN_RECEIVABLE = "loan_receivable"
    OTHER_HTM = "other_htm"


class InvestmentStatusDB(str, SAEnum):
    ACTIVE = "active"
    MATURED = "matured"
    EARLY_WITHDRAWN = "early_withdrawn"
    SOLD = "sold"
    IMPAIRED = "impaired"


class LoanTypeDB(str, SAEnum):
    BANK_LOAN = "bank_loan"
    BOND_PAYABLE = "bond_payable"
    INTERCOMPANY_LOAN = "intercompany_loan"


class LoanStatusDB(str, SAEnum):
    ACTIVE = "active"
    FULLY_PAID = "fully_paid"
    DEFAULTED = "defaulted"
    REFINANCED = "refinanced"


class SweepTypeDB(str, SAEnum):
    ZERO_BALANCING = "zero_balancing"
    TARGET_BALANCING = "target_balancing"


class ICSweepStatusDB(str, SAEnum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    REVERSED = "reversed"


class BatchStatusDB(str, SAEnum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    PARTIALLY_EXECUTED = "partially_executed"
    EXECUTED = "executed"


class BatchItemStatusDB(str, SAEnum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class SyncStatusDB(str, SAEnum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class FXForwardStatusDB(str, SAEnum):
    OPEN = "open"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class CashInTransitModel(Base):
    __tablename__ = "trs_cash_in_transit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reference = Column(String(50), unique=True, nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), default="VND", nullable=False)
    source_account_type = Column(String(20), nullable=False)
    source_account_id = Column(Integer, nullable=False)
    dest_account_type = Column(String(20), nullable=False)
    dest_account_id = Column(Integer, nullable=False)
    transfer_date = Column(Date, nullable=False)
    expected_clear_date = Column(Date, nullable=False)
    cleared = Column(Boolean, default=False, nullable=False)
    cleared_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<CashInTransitModel(id={self.id}, ref='{self.reference}', amount={self.amount})>"


class SecurityInvestmentModel(Base):
    __tablename__ = "trs_security_investments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investment_code = Column(String(30), unique=True, nullable=False, index=True)
    investment_name = Column(String(300), nullable=False)
    investment_type = Column(String(30), default="trading_security", nullable=False)
    status = Column(String(20), default="active", nullable=False)
    quantity = Column(Numeric(18, 4), nullable=True)
    cost_price = Column(Numeric(18, 2), nullable=False)
    market_price = Column(Numeric(18, 2), nullable=True)
    total_cost = Column(Numeric(18, 2), nullable=False)
    fair_value = Column(Numeric(18, 2), nullable=True)
    counterparty_name = Column(String(300), nullable=True)
    counterparty_id = Column(String(50), nullable=True)
    purchase_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=True)
    interest_rate = Column(Numeric(8, 4), nullable=True)
    interest_basis = Column(String(20), nullable=True)
    coa_code = Column(String(20), nullable=False)
    coa_income_code = Column(String(20), default="515", nullable=False)
    coa_expense_code = Column(String(20), default="635", nullable=False)
    period = Column(String(10), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    __table_args__ = (
        Index("ix_trs_investment_type_status", "investment_type", "status"),
    )

    def __repr__(self) -> str:
        return f"<SecurityInvestmentModel(id={self.id}, code='{self.investment_code}')>"


class InvestmentTransactionModel(Base):
    __tablename__ = "trs_investment_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investment_id = Column(Integer, ForeignKey("trs_security_investments.id", ondelete="RESTRICT"), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    transaction_date = Column(Date, nullable=False)
    quantity = Column(Numeric(18, 4), nullable=True)
    price = Column(Numeric(18, 2), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    fee = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    gain_loss = Column(Numeric(18, 2), nullable=True)
    counterparty_ref = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    investment = relationship("SecurityInvestmentModel")

    def __repr__(self) -> str:
        return f"<InvestmentTransactionModel(investment={self.investment_id}, type={self.transaction_type})>"


class LoanModel(Base):
    __tablename__ = "trs_loans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_code = Column(String(30), unique=True, nullable=False, index=True)
    loan_name = Column(String(300), nullable=False)
    loan_type = Column(String(30), default="bank_loan", nullable=False)
    status = Column(String(20), default="active", nullable=False)
    principal = Column(Numeric(18, 2), nullable=False)
    outstanding_balance = Column(Numeric(18, 2), nullable=False)
    interest_rate = Column(Numeric(8, 4), nullable=False)
    interest_basis = Column(String(20), default="actual/365", nullable=False)
    drawdown_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=False)
    repayment_frequency = Column(String(20), default="monthly", nullable=False)
    repayment_day = Column(Integer, default=1, nullable=False)
    lender_name = Column(String(300), nullable=True)
    lender_id = Column(String(50), nullable=True)
    currency = Column(String(3), default="VND", nullable=False)
    coa_code = Column(String(20), default="341", nullable=False)
    coa_interest_code = Column(String(20), default="635", nullable=False)
    covenant_dscr_min = Column(Numeric(8, 4), nullable=True)
    covenant_icr_min = Column(Numeric(8, 4), nullable=True)
    covenant_ltv_max = Column(Numeric(8, 4), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<LoanModel(id={self.id}, code='{self.loan_code}', status='{self.status}')>"


class LoanPaymentModel(Base):
    __tablename__ = "trs_loan_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey("trs_loans.id", ondelete="RESTRICT"), nullable=False)
    payment_date = Column(Date, nullable=False)
    principal_amount = Column(Numeric(18, 2), nullable=False)
    interest_amount = Column(Numeric(18, 2), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    is_scheduled = Column(Boolean, default=True, nullable=False)
    is_early_repayment = Column(Boolean, default=False, nullable=False)
    early_repayment_penalty = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    loan = relationship("LoanModel")

    __table_args__ = (
        Index("ix_trs_loan_payment_loan_date", "loan_id", "payment_date"),
    )

    def __repr__(self) -> str:
        return f"<LoanPaymentModel(loan={self.loan_id}, date={self.payment_date}, amount={self.total_amount})>"


class FXForwardModel(Base):
    __tablename__ = "trs_fx_forwards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    base_currency = Column(String(3), default="VND", nullable=False)
    target_currency = Column(String(3), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    forward_rate = Column(Numeric(18, 6), nullable=False)
    value_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=False)
    counterparty = Column(String(200), nullable=False)
    status = Column(String(20), default="open", nullable=False)
    settlement_amount = Column(Numeric(18, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<FXForwardModel(contract='{self.contract_number}', status='{self.status}')>"


class CashFlowForecastModel(Base):
    __tablename__ = "trs_cash_flow_forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    forecast_name = Column(String(100), nullable=False)
    horizon = Column(String(10), default="30d", nullable=False)
    scenario = Column(String(10), default="base", nullable=False)
    currency = Column(String(3), default="VND", nullable=False)
    opening_balance = Column(Numeric(18, 2), nullable=False)
    total_inflows = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_outflows = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    closing_balance = Column(Numeric(18, 2), nullable=False)
    min_balance_threshold = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    min_balance_breach = Column(Boolean, default=False, nullable=False)
    surplus_threshold = Column(Numeric(18, 2), nullable=True)
    surplus_identified = Column(Boolean, default=False, nullable=False)
    forecast_date = Column(Date, nullable=False)
    period = Column(String(10), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    lines = relationship("ForecastLineModel", back_populates="forecast", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CashFlowForecastModel(id={self.id}, name='{self.forecast_name}', horizon='{self.horizon}')>"


class ForecastLineModel(Base):
    __tablename__ = "trs_forecast_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    forecast_id = Column(Integer, ForeignKey("trs_cash_flow_forecasts.id", ondelete="CASCADE"), nullable=False)
    line_type = Column(String(50), nullable=False)
    description = Column(String(300), nullable=False)
    expected_amount = Column(Numeric(18, 2), nullable=False)
    expected_date = Column(Date, nullable=False)
    confidence_pct = Column(Integer, default=80, nullable=False)
    source_module = Column(String(50), nullable=True)
    source_reference = Column(String(100), nullable=True)
    is_manual = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    forecast = relationship("CashFlowForecastModel", back_populates="lines")

    __table_args__ = (
        Index("ix_trs_forecast_line_type_date", "forecast_id", "line_type", "expected_date"),
    )

    def __repr__(self) -> str:
        return f"<ForecastLineModel(forecast={self.forecast_id}, type='{self.line_type}', amount={self.expected_amount})>"


class TreasuryPositionModel(Base):
    __tablename__ = "trs_treasury_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    currency = Column(String(3), default="VND", nullable=False)
    total_cash = Column(Numeric(18, 2), nullable=False)
    total_bank = Column(Numeric(18, 2), nullable=False)
    total_cash_in_transit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_blocked = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_available = Column(Numeric(18, 2), nullable=False)
    total_investments = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_loans = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    net_liquidity = Column(Numeric(18, 2), nullable=False)
    entity_id = Column(String(50), nullable=True, index=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_trs_position_date_entity", "snapshot_date", "entity_id"),
    )

    def __repr__(self) -> str:
        return f"<TreasuryPositionModel(date={self.snapshot_date}, avail={self.total_available})>"


class FXExposureModel(Base):
    __tablename__ = "trs_fx_exposures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    currency = Column(String(3), nullable=False)
    total_long = Column(Numeric(18, 2), nullable=False)
    total_short = Column(Numeric(18, 2), nullable=False)
    net_exposure = Column(Numeric(18, 2), nullable=False)
    vnd_equivalent = Column(Numeric(18, 2), nullable=False)
    exchange_rate = Column(Numeric(18, 6), nullable=False)
    rate_source = Column(String(20), default="bank_avg", nullable=False)
    unrealized_gain_loss = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    policy_limit = Column(Numeric(18, 2), nullable=True)
    threshold_breached = Column(Boolean, default=False, nullable=False)
    entity_id = Column(String(50), nullable=True, index=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_trs_fx_date_currency", "snapshot_date", "currency", "entity_id"),
    )

    def __repr__(self) -> str:
        return f"<FXExposureModel(date={self.snapshot_date}, ccy='{self.currency}', net={self.net_exposure})>"


class FXRateModel(Base):
    __tablename__ = "trs_fx_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String(3), nullable=False)
    rate_date = Column(Date, nullable=False)
    rate_buying = Column(Numeric(18, 6), nullable=True)
    rate_selling = Column(Numeric(18, 6), nullable=True)
    rate_avg = Column(Numeric(18, 6), nullable=False)
    rate_source = Column(String(20), default="bank_avg", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_trs_fx_rate_currency_date", "currency", "rate_date", "rate_source", unique=True),
    )

    def __repr__(self) -> str:
        return f"<FXRateModel(ccy='{self.currency}', date={self.rate_date}, avg={self.rate_avg})>"


class IntercompanyLoanModel(Base):
    __tablename__ = "trs_intercompany_loans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_code = Column(String(30), unique=True, nullable=False, index=True)
    lender_entity_id = Column(String(50), nullable=False)
    borrower_entity_id = Column(String(50), nullable=False)
    principal = Column(Numeric(18, 2), nullable=False)
    outstanding_balance = Column(Numeric(18, 2), nullable=False)
    interest_rate = Column(Numeric(8, 4), nullable=False)
    interest_basis = Column(String(20), default="actual/365", nullable=False)
    currency = Column(String(3), default="VND", nullable=False)
    start_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=False)
    status = Column(String(20), default="active", nullable=False)
    coa_receivable_code = Column(String(20), default="1368", nullable=False)
    coa_payable_code = Column(String(20), default="3368", nullable=False)
    agreement_ref = Column(String(100), nullable=True)
    transfer_pricing_compliant = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<IntercompanyLoanModel(id={self.id}, code='{self.loan_code}')>"


class IntercompanySweepModel(Base):
    __tablename__ = "trs_intercompany_sweeps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sweep_type = Column(String(20), default="zero_balancing", nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    sweep_date = Column(Date, nullable=False)
    source_entity_id = Column(String(50), nullable=False)
    target_entity_id = Column(String(50), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    source_acct_type = Column(String(20), default="bank", nullable=False)
    source_acct_id = Column(Integer, nullable=False)
    target_acct_type = Column(String(20), default="bank", nullable=False)
    target_acct_id = Column(Integer, nullable=False)
    target_balance_after = Column(Numeric(18, 2), nullable=True)
    ic_loan_id = Column(Integer, ForeignKey("trs_intercompany_loans.id", ondelete="SET NULL"), nullable=True)
    approved_by = Column(String(100), nullable=True)
    executed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<IntercompanySweepModel(id={self.id}, from='{self.source_entity_id}', amount={self.amount})>"


class PaymentBatchModel(Base):
    __tablename__ = "trs_payment_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_code = Column(String(30), unique=True, nullable=False, index=True)
    status = Column(String(20), default="draft", nullable=False)
    payment_date = Column(Date, nullable=False)
    currency = Column(String(3), default="VND", nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    item_count = Column(Integer, default=0, nullable=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    bank_ref = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    items = relationship("PaymentBatchItemModel", back_populates="batch", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<PaymentBatchModel(id={self.id}, code='{self.batch_code}', status='{self.status}')>"


class PaymentBatchItemModel(Base):
    __tablename__ = "trs_payment_batch_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("trs_payment_batches.id", ondelete="CASCADE"), nullable=False)
    source_module = Column(String(50), nullable=False)
    source_id = Column(Integer, nullable=False)
    source_reference = Column(String(50), nullable=False)
    payee_name = Column(String(300), nullable=False)
    payee_account = Column(String(50), nullable=True)
    payee_bank = Column(String(100), nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), default="VND", nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    bank_txn_ref = Column(String(100), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    batch = relationship("PaymentBatchModel", back_populates="items")

    __table_args__ = (
        Index("ix_trs_batch_item_module_ref", "source_module", "source_id"),
    )

    def __repr__(self) -> str:
        return f"<PaymentBatchItemModel(batch={self.batch_id}, ref='{self.source_reference}')>"


class BankConnectorConfigModel(Base):
    __tablename__ = "trs_bank_connector_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_code = Column(String(20), unique=True, nullable=False, index=True)
    bank_name = Column(String(200), nullable=False)
    api_endpoint = Column(String(500), nullable=True)
    api_version = Column(String(20), nullable=True)
    auth_type = Column(String(20), default="api_key", nullable=False)
    credentials_encrypted = Column(Text, nullable=True)
    sync_frequency_minutes = Column(Integer, default=60, nullable=False)
    last_sync_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    supports_balance = Column(Boolean, default=True, nullable=False)
    supports_transactions = Column(Boolean, default=True, nullable=False)
    supports_statements = Column(Boolean, default=True, nullable=False)
    ip_whitelist = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<BankConnectorConfigModel(id={self.id}, bank='{self.bank_code}', active={self.is_active})>"


class BankSyncLogModel(Base):
    __tablename__ = "trs_bank_sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    connector_id = Column(Integer, ForeignKey("trs_bank_connector_configs.id", ondelete="CASCADE"), nullable=False)
    sync_type = Column(String(50), nullable=False)
    sync_status = Column(String(20), nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    transactions_fetched = Column(Integer, default=0, nullable=False)
    transactions_matched = Column(Integer, default=0, nullable=False)
    transactions_unmatched = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    connector = relationship("BankConnectorConfigModel")

    def __repr__(self) -> str:
        return f"<BankSyncLogModel(connector={self.connector_id}, status='{self.sync_status}')>"


class TreasuryPolicyModel(Base):
    __tablename__ = "trs_treasury_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_code = Column(String(30), unique=True, nullable=False, index=True)
    policy_name = Column(String(300), nullable=False)
    policy_type = Column(String(50), nullable=False)
    threshold_value = Column(Numeric(18, 2), nullable=True)
    threshold_pct = Column(Numeric(8, 4), nullable=True)
    min_value = Column(Numeric(18, 2), nullable=True)
    max_value = Column(Numeric(18, 2), nullable=True)
    counterparty_restriction = Column(String(500), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<TreasuryPolicyModel(id={self.id}, code='{self.policy_code}')>"


class TreasuryAuditLogModel(Base):
    __tablename__ = "trs_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    performed_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_trs_audit_entity", "entity_type", "entity_id"),
    )

    def __repr__(self) -> str:
        return f"<TreasuryAuditLogModel(entity={self.entity_type}/{self.entity_id}, action='{self.action}')>"
