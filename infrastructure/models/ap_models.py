import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal

from infrastructure.models.coa_models import Base


class VendorTypeDB(str, enum.Enum):
    INDIVIDUAL = "individual"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    FOREIGN = "foreign"


class VendorGroupDB(str, enum.Enum):
    DOMESTIC = "domestic"
    IMPORT = "import"
    VIP = "vip"
    GOVT = "govt"


class VendorStatusDB(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class APInvoiceTypeDB(str, enum.Enum):
    PO_BASED = "po_based"
    NON_PO = "non_po"
    PREPAYMENT = "prepayment"


class APInvoiceStatusDB(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    WAITING_RECEIPT = "waiting_receipt"
    MATCHED = "matched"
    APPROVED = "approved"
    PAID_PARTIAL = "paid_partial"
    PAID_FULL = "paid_full"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    WRITTEN_OFF = "written_off"


class APPaymentStatusDB(str, enum.Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTING = "executing"
    EXECUTED = "executed"
    POSTED = "posted"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class APPaymentMethodDB(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CARD = "card"


class FCTMethodDB(str, enum.Enum):
    DIRECT = "direct"
    DEDUCTION = "deduction"
    HYBRID = "hybrid"


class FCTStatusDB(str, enum.Enum):
    PENDING = "pending"
    DECLARED = "declared"
    REMITTED = "remitted"
    OVERDUE = "overdue"


class PrepaymentStatusDB(str, enum.Enum):
    PENDING = "pending"
    APPLIED = "applied"
    CANCELLED = "cancelled"


class ProvisionStatusDB(str, enum.Enum):
    ACTIVE = "active"
    PARTIALLY_WRITTEN_OFF = "partially_written_off"
    FULLY_WRITTEN_OFF = "fully_written_off"


class VendorModel(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_code = Column(String(20), unique=True, nullable=False, index=True)
    vendor_name = Column(String(300), nullable=False)
    legal_name = Column(String(300), nullable=True)
    tax_code = Column(String(20), nullable=True, index=True)
    vendor_type = Column(SAEnum(VendorTypeDB), default=VendorTypeDB.ENTERPRISE, nullable=False)
    vendor_group = Column(SAEnum(VendorGroupDB), default=VendorGroupDB.DOMESTIC, nullable=False)
    status = Column(SAEnum(VendorStatusDB), default=VendorStatusDB.ACTIVE, nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(3), default="VN", nullable=False)
    contact_person = Column(String(100), nullable=True)
    payment_terms = Column(String(20), default="net_30", nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    bank_name = Column(String(200), nullable=True)
    bank_account = Column(String(50), nullable=True)
    bank_swift = Column(String(20), nullable=True)
    credit_limit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    coa_code = Column(String(20), nullable=True, index=True)
    foreign_ct_type = Column(String(20), nullable=True)
    foreign_vat_rate = Column(Numeric(5, 4), nullable=True)
    foreign_cit_rate = Column(Numeric(5, 4), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    invoices = relationship("APInvoiceModel", back_populates="vendor")

    def __repr__(self) -> str:
        return f"<VendorModel(id={self.id}, code='{self.vendor_code}', name='{self.vendor_name}')>"


class APInvoiceModel(Base):
    __tablename__ = "ap_invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(20), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    vendor_code = Column(String(20), nullable=True)
    vendor_name = Column(String(300), nullable=True)
    invoice_type = Column(SAEnum(APInvoiceTypeDB), default=APInvoiceTypeDB.NON_PO, nullable=False)
    status = Column(SAEnum(APInvoiceStatusDB), default=APInvoiceStatusDB.DRAFT, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    discount_date = Column(Date, nullable=True)
    discount_percent = Column(Numeric(5, 4), nullable=True)
    posted_date = Column(Date, nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    discount_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    tax_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    paid_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    written_off_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    balance_due = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    fx_rate = Column(Numeric(18, 6), nullable=True)
    fx_gl_rate = Column(Numeric(18, 6), nullable=True)
    po_number = Column(String(20), nullable=True, index=True)
    gr_number = Column(String(20), nullable=True)
    reference = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    period = Column(String(10), nullable=True, index=True)
    coa_code = Column(String(20), default="331", nullable=False)
    created_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    vendor = relationship("VendorModel", back_populates="invoices")
    lines = relationship("APInvoiceLineModel", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("APPaymentModel", back_populates="invoice")
    credit_notes = relationship("APCreditNoteModel", back_populates="original_invoice", foreign_keys="APCreditNoteModel.original_invoice_id")
    debit_notes = relationship("APDebitNoteModel", back_populates="original_invoice", foreign_keys="APDebitNoteModel.original_invoice_id")

    __table_args__ = (
        Index("ix_ap_invoice_vendor_number", "vendor_id", "invoice_number", unique=True),
    )

    def __repr__(self) -> str:
        return f"<APInvoiceModel(id={self.id}, number='{self.invoice_number}', status='{self.status}')>"


class APInvoiceLineModel(Base):
    __tablename__ = "ap_invoice_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ap_invoice_id = Column(Integer, ForeignKey("ap_invoices.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    unit_price = Column(Numeric(18, 2), nullable=False)
    line_amount = Column(Numeric(18, 2), nullable=False)
    tax_rate = Column(Numeric(8, 4), default=Decimal("0.10"), nullable=False)
    tax_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    coa_code = Column(String(20), nullable=True)
    po_line_number = Column(Integer, nullable=True)
    gr_line_number = Column(Integer, nullable=True)

    invoice = relationship("APInvoiceModel", back_populates="lines")

    def __repr__(self) -> str:
        return f"<APInvoiceLineModel(id={self.id}, invoice_id={self.ap_invoice_id}, line={self.line_number})>"


class APCreditNoteModel(Base):
    __tablename__ = "ap_credit_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    credit_note_number = Column(String(20), unique=True, nullable=False, index=True)
    original_invoice_id = Column(Integer, ForeignKey("ap_invoices.id", ondelete="RESTRICT"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    reason = Column(Text, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    tax_adjustment = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    credit_note_date = Column(Date, nullable=False)
    reference = Column(String(100), nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    original_invoice = relationship("APInvoiceModel", back_populates="credit_notes", foreign_keys=[original_invoice_id])
    vendor = relationship("VendorModel")

    def __repr__(self) -> str:
        return f"<APCreditNoteModel(id={self.id}, invoice={self.original_invoice_id}, amount={self.amount})>"


class APDebitNoteModel(Base):
    __tablename__ = "ap_debit_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    debit_note_number = Column(String(20), unique=True, nullable=False, index=True)
    original_invoice_id = Column(Integer, ForeignKey("ap_invoices.id", ondelete="RESTRICT"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    reason = Column(Text, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    debit_note_date = Column(Date, nullable=False)
    reference = Column(String(100), nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    original_invoice = relationship("APInvoiceModel", back_populates="debit_notes", foreign_keys=[original_invoice_id])
    vendor = relationship("VendorModel")

    def __repr__(self) -> str:
        return f"<APDebitNoteModel(id={self.id}, invoice={self.original_invoice_id}, amount={self.amount})>"


class APPaymentModel(Base):
    __tablename__ = "ap_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_number = Column(String(20), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id", ondelete="RESTRICT"), nullable=True)
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    discount_taken = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    net_amount = Column(Numeric(18, 2), nullable=False)
    payment_method = Column(SAEnum(APPaymentMethodDB), nullable=False, index=True)
    bank_account_id = Column(Integer, nullable=True)
    reference = Column(String(100), nullable=True)
    status = Column(SAEnum(APPaymentStatusDB), default=APPaymentStatusDB.DRAFT, nullable=False)
    is_batch_payment = Column(Boolean, default=False, nullable=False)
    batch_id = Column(Integer, nullable=True, index=True)
    approval_by = Column(String(100), nullable=True)
    approval_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    vendor = relationship("VendorModel")
    invoice = relationship("APInvoiceModel", back_populates="payments")

    def __repr__(self) -> str:
        return f"<APPaymentModel(id={self.id}, number='{self.payment_number}', amount={self.amount})>"


class APPaymentAllocationModel(Base):
    __tablename__ = "ap_payment_allocations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ap_payment_id = Column(Integer, ForeignKey("ap_payments.id", ondelete="CASCADE"), nullable=False)
    ap_invoice_id = Column(Integer, ForeignKey("ap_invoices.id", ondelete="RESTRICT"), nullable=False)
    allocated_amount = Column(Numeric(18, 2), nullable=False)
    is_adjustment = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    payment = relationship("APPaymentModel")
    invoice = relationship("APInvoiceModel")

    def __repr__(self) -> str:
        return f"<APPaymentAllocationModel(payment={self.ap_payment_id}, invoice={self.ap_invoice_id})>"


class VendorPrepaymentModel(Base):
    __tablename__ = "ap_prepayments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    unapplied_balance = Column(Numeric(18, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    expected_invoice_date = Column(Date, nullable=True)
    reference = Column(String(100), nullable=True)
    status = Column(SAEnum(PrepaymentStatusDB), default=PrepaymentStatusDB.PENDING, nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    vendor = relationship("VendorModel")

    def __repr__(self) -> str:
        return f"<VendorPrepaymentModel(id={self.id}, vendor={self.vendor_id}, amount={self.amount})>"


class APProvisionModel(Base):
    __tablename__ = "ap_provisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    period = Column(String(10), nullable=False, index=True)
    provision_percent = Column(Numeric(5, 2), nullable=False)
    overdue_days = Column(Integer, nullable=False)
    invoice_total = Column(Numeric(18, 2), nullable=False)
    provision_amount = Column(Numeric(18, 2), nullable=False)
    status = Column(SAEnum(ProvisionStatusDB), default=ProvisionStatusDB.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    vendor = relationship("VendorModel")

    def __repr__(self) -> str:
        return f"<APProvisionModel(id={self.id}, vendor={self.vendor_id}, period={self.period})>"


class APAgingSnapshotModel(Base):
    __tablename__ = "ap_aging_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(10), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    vendor_code = Column(String(20), nullable=False)
    vendor_name = Column(String(300), nullable=False)
    current_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    bucket_1_30 = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    bucket_31_60 = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    bucket_61_90 = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    bucket_91_180 = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    bucket_181_365 = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    bucket_365_plus = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_outstanding = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    locked = Column(Boolean, default=False, nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    vendor = relationship("VendorModel")

    __table_args__ = (
        Index("ix_ap_aging_period_vendor", "period", "vendor_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<APAgingSnapshotModel(period={self.period}, vendor={self.vendor_code})>"


class FCTDeclarationModel(Base):
    __tablename__ = "ap_fct_declarations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    period = Column(String(10), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id", ondelete="RESTRICT"), nullable=False)
    fct_method = Column(SAEnum(FCTMethodDB), nullable=False)
    vat_rate = Column(Numeric(5, 4), nullable=False)
    cit_rate = Column(Numeric(5, 4), nullable=False)
    gross_amount = Column(Numeric(18, 2), nullable=False)
    vat_amount = Column(Numeric(18, 2), nullable=False)
    cit_amount = Column(Numeric(18, 2), nullable=False)
    net_amount = Column(Numeric(18, 2), nullable=False)
    status = Column(SAEnum(FCTStatusDB), default=FCTStatusDB.PENDING, nullable=False)
    declared_at = Column(DateTime, nullable=True)
    remitted_at = Column(DateTime, nullable=True)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    vendor = relationship("VendorModel")
    invoice = relationship("APInvoiceModel")

    def __repr__(self) -> str:
        return f"<FCTDeclarationModel(id={self.id}, vendor={self.vendor_id}, period={self.period})>"


class IntercompanyInvoiceModel(Base):
    __tablename__ = "ap_intercompany_invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_entity_code = Column(String(20), nullable=False, index=True)
    to_entity_code = Column(String(20), nullable=False, index=True)
    invoice_number = Column(String(20), nullable=False)
    invoice_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    description = Column(Text, nullable=False)
    reference = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<IntercompanyInvoiceModel(id={self.id}, from={self.from_entity_code}, to={self.to_entity_code})>"
