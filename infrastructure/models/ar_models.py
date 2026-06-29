import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal

from infrastructure.models.coa_models import Base


class CustomerTypeDB(str, enum.Enum):
    INDIVIDUAL = "individual"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    FOREIGN = "foreign"


class CustomerGroupDB(str, enum.Enum):
    DOMESTIC = "domestic"
    EXPORT = "export"
    GOVT = "govt"
    VIP = "vip"


class CustomerStatusDB(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class InvoiceTypeDB(str, enum.Enum):
    SALES = "sales"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"


class InvoiceStatusDB(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class PaymentMethodDB(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CREDIT_CARD = "credit_card"
    OFFLINE = "offline"


class AllocationStatusDB(str, enum.Enum):
    PENDING = "pending"
    ALLOCATED = "allocated"
    PARTIAL = "partial"
    REVERSED = "reversed"


class DunningLevelDB(str, enum.Enum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    LEGAL = "legal"


class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_code = Column(String(20), unique=True, nullable=False, index=True)
    customer_name = Column(String(300), nullable=False)
    legal_name = Column(String(300), nullable=True)
    tax_code = Column(String(20), nullable=True, index=True)
    customer_type = Column(SAEnum(CustomerTypeDB), default=CustomerTypeDB.ENTERPRISE, nullable=False)
    customer_group = Column(SAEnum(CustomerGroupDB), default=CustomerGroupDB.DOMESTIC, nullable=False)
    status = Column(SAEnum(CustomerStatusDB), default=CustomerStatusDB.ACTIVE, nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(3), default="VN", nullable=False)
    contact_person = Column(String(100), nullable=True)
    credit_limit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    outstanding_balance = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    coa_account_code = Column(String(20), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    invoices = relationship("ARInvoiceModel", back_populates="customer")

    def __repr__(self) -> str:
        return f"<CustomerModel(id={self.id}, code='{self.customer_code}', name='{self.customer_name}')>"


class ARInvoiceModel(Base):
    __tablename__ = "ar_invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(20), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    customer_code = Column(String(20), nullable=False, index=True)
    customer_name = Column(String(300), nullable=False)
    invoice_type = Column(SAEnum(InvoiceTypeDB), default=InvoiceTypeDB.SALES, nullable=False)
    status = Column(SAEnum(InvoiceStatusDB), default=InvoiceStatusDB.DRAFT, nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    discount_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    tax_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    paid_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    written_off_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    balance_due = Column(Numeric(18, 2), nullable=False)
    payment_terms_days = Column(Integer, default=30, nullable=False)
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    period = Column(String(10), nullable=True, index=True)
    posted_at = Column(DateTime, nullable=True)
    posted_by = Column(String(50), nullable=True)
    coa_code = Column(String(20), nullable=True, index=True)
    einvoice_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    customer = relationship("CustomerModel", back_populates="invoices")
    lines = relationship("ARInvoiceLineModel", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("ARPaymentModel", back_populates="invoice")

    def __repr__(self) -> str:
        return f"<ARInvoiceModel(id={self.id}, number='{self.invoice_number}', status='{self.status}')>"


class ARInvoiceLineModel(Base):
    __tablename__ = "ar_invoice_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("ar_invoices.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    unit_price = Column(Numeric(18, 2), nullable=False)
    line_amount = Column(Numeric(18, 2), nullable=False)
    tax_rate = Column(Numeric(8, 4), default=Decimal("0"), nullable=False)
    tax_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    coa_code = Column(String(20), nullable=True)

    invoice = relationship("ARInvoiceModel", back_populates="lines")

    def __repr__(self) -> str:
        return f"<ARInvoiceLineModel(id={self.id}, invoice_id={self.invoice_id}, line={self.line_number})>"


class ARPaymentModel(Base):
    __tablename__ = "ar_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_number = Column(String(20), unique=True, nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("ar_invoices.id", ondelete="RESTRICT"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    payment_method = Column(SAEnum(PaymentMethodDB), nullable=False, index=True)
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    received_by = Column(String(50), nullable=True)
    bank_account_id = Column(Integer, nullable=True)
    coa_code = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    invoice = relationship("ARInvoiceModel", back_populates="payments")

    def __repr__(self) -> str:
        return f"<ARPaymentModel(id={self.id}, number='{self.payment_number}', amount={self.amount})>"

