import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum
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
    transaction_date = Column(Date, nullable=False)
    description = Column(String(500), nullable=False)
    period = Column(String(7), nullable=False, index=True)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_date = Column(DateTime, nullable=True)
    source_module = Column(String(50), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    lines = relationship("JournalLineModel", back_populates="entry", lazy="selectin",
                         cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<JournalEntryModel(id={self.id}, journal_number='{self.journal_number}')>"


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
