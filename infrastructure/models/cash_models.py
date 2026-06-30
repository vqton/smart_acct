import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from infrastructure.models.coa_models import Base


class CashVoucherStatusDB(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class BankAccountStatusDB(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    BLOCKED = "blocked"


class ChequeStatusDB(str, enum.Enum):
    NEW = "new"
    ISSUED = "issued"
    CLEARED = "cleared"
    CANCELLED = "cancelled"
    STOPPED = "stopped"
    BOUNCED = "bounced"


class CashTransferStatusDB(str, enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    FAILED = "failed"


class PettyCashFundStatusDB(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class CashReceiptModel(Base):
    __tablename__ = "cash_receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_number = Column(String(20), unique=True, nullable=False, index=True)
    receipt_date = Column(Date, nullable=False)
    receipt_type = Column(String(30), nullable=False)
    payer_name = Column(String(300), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    amount_in_words = Column(String(500), nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    fx_rate = Column(Numeric(18, 6), nullable=True)
    account_code = Column(String(20), nullable=False)
    counter_account = Column(String(20), nullable=False)
    reference_number = Column(String(100), nullable=True)
    description = Column(String(500), nullable=False)
    status = Column(SAEnum(CashVoucherStatusDB), default=CashVoucherStatusDB.DRAFT, nullable=False)
    created_by = Column(String(100), nullable=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<CashReceiptModel(id={self.id}, number='{self.receipt_number}')>"


class CashPaymentModel(Base):
    __tablename__ = "cash_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_number = Column(String(20), unique=True, nullable=False, index=True)
    payment_date = Column(Date, nullable=False)
    payment_type = Column(String(30), nullable=False)
    receiver_name = Column(String(300), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    amount_in_words = Column(String(500), nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    fx_rate = Column(Numeric(18, 6), nullable=True)
    account_code = Column(String(20), nullable=False)
    counter_account = Column(String(20), nullable=False)
    reference_number = Column(String(100), nullable=True)
    supporting_doc_ref = Column(String(100), nullable=True)
    description = Column(String(500), nullable=False)
    status = Column(SAEnum(CashVoucherStatusDB), default=CashVoucherStatusDB.DRAFT, nullable=False)
    created_by = Column(String(100), nullable=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<CashPaymentModel(id={self.id}, number='{self.payment_number}')>"


class BankSubAccountTypeDB(str, enum.Enum):
    VND = "1121"
    FC = "1122"


class BankAccountModel(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_name = Column(String(200), nullable=False)
    branch = Column(String(200), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_holder = Column(String(300), nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    coa_code = Column(String(20), nullable=False)
    sub_account_type = Column(String(3), nullable=True)
    swift_code = Column(String(20), nullable=True)
    iban = Column(String(50), nullable=True)
    opening_balance = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    status = Column(SAEnum(BankAccountStatusDB), default=BankAccountStatusDB.ACTIVE, nullable=False)
    signatories = Column(JSON, default=list, nullable=True)
    authorization_limit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    last_reconciled_period = Column(String(7), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<BankAccountModel(id={self.id}, number='{self.account_number}')>"


class BankStatementModel(Base):
    __tablename__ = "bank_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False, index=True)
    statement_date = Column(Date, nullable=False)
    opening_balance = Column(Numeric(18, 2), nullable=False)
    closing_balance = Column(Numeric(18, 2), nullable=False)
    imported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    source = Column(String(20), nullable=False)

    transactions = relationship("BankTransactionModel", back_populates="statement", lazy="selectin",
                                cascade="all, delete-orphan")
    bank_account = relationship("BankAccountModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<BankStatementModel(id={self.id}, date={self.statement_date})>"


class BankTransactionModel(Base):
    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False, index=True)
    statement_id = Column(Integer, ForeignKey("bank_statements.id"), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False)
    value_date = Column(Date, nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    is_debit = Column(Boolean, nullable=False)
    reference = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    matched_entry_id = Column(Integer, nullable=True, index=True)

    statement = relationship("BankStatementModel", back_populates="transactions", lazy="selectin")
    bank_account = relationship("BankAccountModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<BankTransactionModel(id={self.id}, ref='{self.reference}')>"


class BankReconciliationModel(Base):
    __tablename__ = "bank_reconciliations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False, index=True)
    period = Column(String(7), nullable=False, index=True)
    book_balance = Column(Numeric(18, 2), nullable=False)
    bank_balance = Column(Numeric(18, 2), nullable=False)
    deposits_in_transit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    outstanding_checks = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unrecorded_credits = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unrecorded_debits = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    adjusted_book_balance = Column(Numeric(18, 2), nullable=False)
    adjusted_bank_balance = Column(Numeric(18, 2), nullable=False)
    is_balanced = Column(Boolean, default=False, nullable=False)
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    discrepancies = relationship("ReconciliationDiscrepancyModel", back_populates="reconciliation",
                                  lazy="selectin", cascade="all, delete-orphan")
    bank_account = relationship("BankAccountModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<BankReconciliationModel(id={self.id}, period='{self.period}')>"


class ReconciliationDiscrepancyModel(Base):
    __tablename__ = "reconciliation_discrepancies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reconciliation_id = Column(Integer, ForeignKey("bank_reconciliations.id"), nullable=False, index=True)
    discrepancy_type = Column(String(30), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    entry_side = Column(String(10), nullable=False)
    reference = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    status = Column(String(20), default="unresolved", nullable=False)
    resolution_entry_id = Column(Integer, nullable=True)

    reconciliation = relationship("BankReconciliationModel", back_populates="discrepancies", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ReconciliationDiscrepancyModel(id={self.id}, type='{self.discrepancy_type}')>"


class PettyCashFundModel(Base):
    __tablename__ = "petty_cash_funds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_code = Column(String(50), unique=True, nullable=False, index=True)
    custodian = Column(String(200), nullable=False)
    limit_amount = Column(Numeric(18, 2), nullable=False)
    current_balance = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    established_date = Column(Date, nullable=False)
    status = Column(SAEnum(PettyCashFundStatusDB), default=PettyCashFundStatusDB.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    transactions = relationship("PettyCashTransactionModel", back_populates="fund",
                                 lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<PettyCashFundModel(id={self.id}, code='{self.fund_code}')>"


class PettyCashTransactionModel(Base):
    __tablename__ = "petty_cash_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("petty_cash_funds.id"), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    is_replenishment = Column(Boolean, nullable=False)
    reference_number = Column(String(100), nullable=True)
    description = Column(String(500), nullable=False)
    receipt_ref = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    fund = relationship("PettyCashFundModel", back_populates="transactions", lazy="selectin")

    def __repr__(self) -> str:
        return f"<PettyCashTransactionModel(id={self.id}, fund={self.fund_id})>"


class CashTransferModel(Base):
    __tablename__ = "cash_transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_account = Column(String(20), nullable=False)
    destination_account = Column(String(20), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    transfer_date = Column(Date, nullable=False)
    fx_rate = Column(Numeric(18, 6), nullable=True)
    reference = Column(String(100), nullable=False)
    status = Column(SAEnum(CashTransferStatusDB), default=CashTransferStatusDB.PENDING, nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<CashTransferModel(id={self.id}, ref='{self.reference}')>"


class ChequeBookModel(Base):
    __tablename__ = "cheque_books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False, index=True)
    start_number = Column(String(20), nullable=False)
    end_number = Column(String(20), nullable=False)
    issued_date = Column(Date, nullable=False)
    status = Column(String(20), default="active", nullable=False)

    cheques = relationship("ChequeModel", back_populates="cheque_book", lazy="selectin",
                           cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChequeBookModel(id={self.id}, start={self.start_number})>"


class ChequeModel(Base):
    __tablename__ = "cheques"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cheque_number = Column(String(20), nullable=False, index=True)
    cheque_book_id = Column(Integer, ForeignKey("cheque_books.id"), nullable=False, index=True)
    payee = Column(String(300), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    issue_date = Column(Date, nullable=False)
    status = Column(SAEnum(ChequeStatusDB), default=ChequeStatusDB.NEW, nullable=False)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False, index=True)
    cleared_date = Column(Date, nullable=True)
    cancelled_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    cheque_book = relationship("ChequeBookModel", back_populates="cheques", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ChequeModel(id={self.id}, number='{self.cheque_number}')>"


class DailyCashCountModel(Base):
    __tablename__ = "daily_cash_counts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    count_date = Column(Date, nullable=False, index=True)
    account_code = Column(String(20), nullable=False)
    expected_balance = Column(Numeric(18, 2), nullable=False)
    actual_balance = Column(Numeric(18, 2), nullable=False)
    difference = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    denomination_breakdown = Column(JSON, default=dict, nullable=True)
    notes = Column(String(500), nullable=True)
    counted_by = Column(String(100), nullable=False)
    witnessed_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<DailyCashCountModel(id={self.id}, date={self.count_date})>"


class AdvanceModel(Base):
    __tablename__ = "advances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String(200), nullable=False)
    employee_id = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    advance_date = Column(Date, nullable=False)
    purpose = Column(String(500), nullable=False)
    settlement_deadline = Column(Date, nullable=False)
    settlement_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    remaining_balance = Column(Numeric(18, 2), nullable=False)
    status = Column(String(20), default="outstanding", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<AdvanceModel(id={self.id}, employee='{self.employee_name}')>"
