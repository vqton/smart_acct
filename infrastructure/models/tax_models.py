from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, Date, Enum as SAEnum, ForeignKey, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from typing import Optional, List
import enum

from infrastructure.models.coa_models import Base


class TaxTypeDB(str, enum.Enum):
    VAT_DEDUCTION = "vat_deduction"
    VAT_DIRECT = "vat_direct"
    CIT = "cit"
    PIT = "pit"
    PIT_FINALIZATION = "pit_finalization"
    LICENSE = "license"
    FOREIGN_CONTRACTOR = "foreign_contractor"
    PERSONAL_RENTAL = "personal_rental"
    RESOURCE = "resource"
    IMPORT_EXPORT = "import_export"
    ENVIRONMENTAL = "environmental"
    PROPERTY = "property"
    OTHER = "other"


class DeclarationStatusDB(str, enum.Enum):
    DRAFT = "draft"
    CALCULATED = "calculated"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    AMENDED = "amended"
    CANCELLED = "cancelled"


class TaxPaymentStatusDB(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    REFUNDED = "refunded"
    PARTIAL = "partial"


class InvoiceStatusDB(str, enum.Enum):
    CREATED = "created"
    SIGNED = "signed"
    SENT = "sent"
    CANCELLED = "cancelled"
    REPLACED = "replaced"
    ADJUSTED = "adjusted"
    ERROR = "error"


class TaxDeclarationModel(Base):
    __tablename__ = "tax_declarations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tax_type = Column(SAEnum(TaxTypeDB), nullable=False)
    declaration_type = Column(String(20), default="original", nullable=False)
    form_code = Column(String(20), nullable=False)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=True)
    period_quarter = Column(Integer, nullable=True)
    status = Column(SAEnum(DeclarationStatusDB), default=DeclarationStatusDB.DRAFT, nullable=False)

    total_revenue = Column(Numeric(18, 2), default=0)
    total_tax = Column(Numeric(18, 2), default=0)
    total_deduction = Column(Numeric(18, 2), default=0)
    total_exemption = Column(Numeric(18, 2), default=0)
    total_payable = Column(Numeric(18, 2), default=0)
    previous_adjustment = Column(Numeric(18, 2), default=0)
    late_interest = Column(Numeric(18, 2), default=0)
    penalty = Column(Numeric(18, 2), default=0)
    net_payable = Column(Numeric(18, 2), default=0)

    submission_deadline = Column(Date, nullable=True)
    submitted_date = Column(Date, nullable=True)
    accepted_date = Column(Date, nullable=True)
    gdt_reference = Column(String(100), nullable=True)
    gdt_error_code = Column(String(50), nullable=True)
    etax_submission_id = Column(String(100), nullable=True)
    submission_method = Column(String(20), default="etax")

    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    lines = relationship("TaxLineModel", backref="declaration", lazy="selectin")
    payments = relationship("TaxPaymentModel", backref="declaration", lazy="selectin")

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"<TaxDeclaration(id={self.id}, form={self.form_code}, {self.period_year})>"


class TaxLineModel(Base):
    __tablename__ = "tax_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    declaration_id = Column(Integer, ForeignKey("tax_declarations.id"), nullable=False)
    line_code = Column(String(20), nullable=False)
    label = Column(String(300), nullable=False)
    amount = Column(Numeric(18, 2), default=0)
    is_calculated = Column(Boolean, default=True)
    parent_line_code = Column(String(20), nullable=True)
    sort_order = Column(Integer, default=0)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)


class TaxPaymentModel(Base):
    __tablename__ = "tax_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    declaration_id = Column(Integer, ForeignKey("tax_declarations.id"), nullable=False)
    tax_type = Column(SAEnum(TaxTypeDB), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    budget_account = Column(String(10), default="1701", nullable=False)
    payment_method = Column(String(20), default="etax")
    payment_status = Column(SAEnum(TaxPaymentStatusDB), default=TaxPaymentStatusDB.PENDING, nullable=False)
    gdt_payment_code = Column(String(100), nullable=True)
    bank_reference = Column(String(100), nullable=True)
    penalty_interest = Column(Numeric(18, 2), default=0)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)


class TaxAdjustmentModel(Base):
    __tablename__ = "tax_adjustments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_declaration_id = Column(Integer, ForeignKey("tax_declarations.id"), nullable=False)
    supplemental_declaration_id = Column(Integer, ForeignKey("tax_declarations.id"), nullable=True)
    adjustment_type = Column(String(20), nullable=False)
    reason = Column(String(1000), nullable=False)
    original_amount = Column(Numeric(18, 2), default=0)
    adjusted_amount = Column(Numeric(18, 2), default=0)
    difference = Column(Numeric(18, 2), default=0)
    late_interest = Column(Numeric(18, 2), default=0)
    penalty = Column(Numeric(18, 2), default=0)
    approval_status = Column(String(20), default="pending")
    approved_by = Column(String(100), nullable=True)
    approval_date = Column(Date, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)


class TaxIncentiveModel(Base):
    __tablename__ = "tax_incentives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tax_type = Column(SAEnum(TaxTypeDB), nullable=False)
    incentive_type = Column(String(30), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(300), nullable=False)
    legal_basis = Column(String(200), nullable=False)
    rate_value = Column(Numeric(10, 2), default=0)
    is_percentage = Column(Boolean, default=True)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)
    max_duration_months = Column(Integer, nullable=True)
    eligibility_condition = Column(Text, nullable=True)
    requires_approval = Column(Boolean, default=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)


class EInvoiceModel(Base):
    __tablename__ = "einvoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(20), nullable=False)
    invoice_series = Column(String(10), nullable=False)
    invoice_date = Column(Date, nullable=False)
    invoice_type = Column(String(20), default="sales")

    seller_tax_code = Column(String(15), nullable=False)
    seller_name = Column(String(300), nullable=False)
    seller_address = Column(String(500), nullable=True)

    buyer_tax_code = Column(String(15), nullable=True)
    buyer_name = Column(String(300), nullable=True)
    buyer_address = Column(String(500), nullable=True)
    buyer_id = Column(String(50), nullable=True)

    subtotal = Column(Numeric(18, 2), default=0)
    discount_amount = Column(Numeric(18, 2), default=0)
    vat_rate = Column(Numeric(5, 2), default=0)
    vat_amount = Column(Numeric(18, 2), default=0)
    grand_total = Column(Numeric(18, 2), default=0)

    currency = Column(String(5), default="VND")
    exchange_rate = Column(Numeric(10, 4), default=1)
    payment_method = Column(String(100), nullable=True)

    status = Column(SAEnum(InvoiceStatusDB), default=InvoiceStatusDB.CREATED, nullable=False)
    verification_code = Column(String(50), nullable=True)
    gdt_transaction_id = Column(String(100), nullable=True)
    signed_file_url = Column(String(500), nullable=True)
    digital_signature = Column(Text, nullable=True)

    adjustment_ref_id = Column(Integer, nullable=True)
    adjustment_type = Column(String(20), nullable=True)
    adjustment_reason = Column(String(500), nullable=True)
    original_invoice_ref = Column(String(50), nullable=True)

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"<EInvoice(id={self.id}, series={self.invoice_series}, num={self.invoice_number})>"


class TaxScheduleModel(Base):
    __tablename__ = "tax_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tax_type = Column(SAEnum(TaxTypeDB), nullable=False)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=True)
    period_quarter = Column(Integer, nullable=True)
    due_date = Column(Date, nullable=False)
    reminder_days_before = Column(Integer, default=7)
    status = Column(String(20), default="pending")
    assigned_to = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)
