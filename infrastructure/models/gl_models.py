import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from infrastructure.models.coa_models import Base


class PeriodType(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AccountingPeriodModel(Base):
    __tablename__ = "accounting_periods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(10), unique=True, nullable=False, index=True)
    type = Column(SAEnum(PeriodType), default=PeriodType.MONTHLY, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_closed = Column(Boolean, default=False, nullable=False)
    closed_by = Column(String(100), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)
    is_current = Column(Boolean, default=False, nullable=False)
    needs_reconciliation = Column(Boolean, default=False, nullable=False)
    parent_period = Column(String(10), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<AccountingPeriodModel(period='{self.period}', is_closed={self.is_closed})>"


class PeriodAuditLogModel(Base):
    __tablename__ = "period_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(10), nullable=False, index=True)
    event_type = Column(String(30), nullable=False)
    user = Column(String(100), nullable=False)
    details = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<PeriodAuditLog(period='{self.period}', event='{self.event_type}', user='{self.user}')>"


class JournalEntryModel(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    journal_number = Column(String(50), unique=True, nullable=False, index=True)
    journal_type = Column(String(20), default="general", nullable=False)
    transaction_date = Column(Date, nullable=False)
    description = Column(String(500), nullable=False)
    period = Column(String(7), nullable=False, index=True)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_date = Column(DateTime, nullable=True)
    source_module = Column(String(50), nullable=True)
    created_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    is_approved = Column(Boolean, default=False, nullable=False)
    approval_date = Column(DateTime, nullable=True)
    correction_method = Column(String(20), nullable=True)
    ref_journal_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    lines = relationship("JournalLineModel", back_populates="entry", lazy="selectin",
                         cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<JournalEntryModel(id={self.id}, journal_number='{self.journal_number}')>"


class SubsidiaryLedgerModel(Base):
    __tablename__ = "subsidiary_ledger"
    __table_args__ = (
        Index("idx_subledger_type_period", "subsidiary_type", "period"),
        Index("idx_subledger_entity", "subsidiary_type", "entity_id", "period"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    subsidiary_type = Column(String(20), nullable=False, index=True)
    account_code = Column(String(20), ForeignKey("chart_of_accounts.code"), nullable=False)
    entity_id = Column(Integer, nullable=False)
    entity_name = Column(String(200), nullable=False)
    transaction_date = Column(Date, nullable=False)
    doc_ref = Column(String(50), nullable=False)
    doc_type = Column(String(30), nullable=False)
    description = Column(String(500), nullable=False)
    debit = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    credit = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    balance = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    period = Column(String(7), nullable=False, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<SubsidiaryLedgerModel(type='{self.subsidiary_type}', entity={self.entity_id}, period='{self.period}')>"


class JournalTypeSequenceModel(Base):
    __tablename__ = "journal_type_sequences"
    __table_args__ = (UniqueConstraint("journal_type", "fiscal_year", name="uq_journal_type_fiscal_year"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    journal_type = Column(String(20), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    last_sequence = Column(Integer, default=0, nullable=False)
    prefix = Column(String(4), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<JournalTypeSequenceModel(type='{self.journal_type}', year={self.fiscal_year}, seq={self.last_sequence})>"


class JournalLineModel(Base):
    __tablename__ = "journal_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(String(20), ForeignKey("chart_of_accounts.code"), nullable=False)
    debit = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    credit = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    description = Column(String(500), nullable=True)
    vat_rate = Column(Numeric(5, 2), nullable=True)
    line_type = Column(String(20), default="regular", nullable=False)
    is_taxable = Column(Boolean, default=False, nullable=False)
    tax_code = Column(String(20), nullable=True)
    period = Column(String(7), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    entry = relationship("JournalEntryModel", back_populates="lines", lazy="selectin")
    account = relationship("COAModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<JournalLineModel(id={self.id}, account='{self.account_id}', debit={self.debit}, credit={self.credit})>"
