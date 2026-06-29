from typing import List, Optional, ClassVar
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum

from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd


class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    FOREIGN = "foreign"


class CustomerGroup(str, Enum):
    DOMESTIC = "domestic"
    EXPORT = "export"
    GOVT = "govt"
    VIP = "vip"


class CustomerStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class ARInvoiceType(str, Enum):
    SALES = "sales"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"


class ARInvoiceStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class ARPaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CREDIT_CARD = "credit_card"
    OFFLINE = "offline"


class ARAllocationStatus(str, Enum):
    PENDING = "pending"
    ALLOCATED = "allocated"
    PARTIAL = "partial"
    REVERSED = "reversed"


class ARDunningLevel(str, Enum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    LEGAL = "legal"


class Customer(BaseModel):
    id: Optional[int] = None
    customer_code: str = Field(..., min_length=1, max_length=20)
    customer_name: str = Field(..., min_length=1, max_length=300)
    legal_name: Optional[str] = Field(None, max_length=300)
    tax_code: Optional[str] = Field(None, max_length=20)
    customer_type: CustomerType = CustomerType.ENTERPRISE
    customer_group: CustomerGroup = CustomerGroup.DOMESTIC
    status: CustomerStatus = CustomerStatus.ACTIVE
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    country: str = "VN"
    contact_person: Optional[str] = Field(None, max_length=100)
    credit_limit: Decimal = Decimal("0")
    outstanding_balance: Decimal = Decimal("0")
    coa_account_code: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("credit_limit", "outstanding_balance")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class InvoiceLine(BaseModel):
    id: Optional[int] = None
    line_number: int
    description: str = Field(..., max_length=500)
    quantity: Decimal
    unit_price: Decimal
    line_amount: Decimal
    tax_rate: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    coa_code: Optional[str] = Field(None, max_length=20)

    @field_validator("quantity", "unit_price", "line_amount", "tax_rate", "tax_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class ARInvoice(BaseModel):
    id: Optional[int] = None
    invoice_number: str = Field(..., min_length=1, max_length=20)
    customer_id: int
    customer_code: str
    customer_name: str
    invoice_type: ARInvoiceType = ARInvoiceType.SALES
    status: ARInvoiceStatus = ARInvoiceStatus.DRAFT
    issue_date: date
    due_date: date
    amount: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal
    paid_amount: Decimal = Decimal("0")
    written_off_amount: Decimal = Decimal("0")
    balance_due: Decimal
    payment_terms_days: int = 30
    reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    period: Optional[str] = Field(None, max_length=10)
    posted_at: Optional[datetime] = None
    posted_by: Optional[str] = Field(None, max_length=50)
    coa_code: Optional[str] = Field(None, max_length=20)
    einvoice_id: Optional[int] = None
    lines: List[InvoiceLine] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount", "discount_amount", "tax_amount", "total_amount", "paid_amount",
                     "written_off_amount", "balance_due")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class ARPayment(BaseModel):
    id: Optional[int] = None
    payment_number: str = Field(..., min_length=1, max_length=20)
    invoice_id: int
    payment_date: date
    amount: Decimal
    payment_method: ARPaymentMethod
    reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    received_by: Optional[str] = Field(None, max_length=50)
    bank_account_id: Optional[int] = None
    coa_code: Optional[str] = Field(None, max_length=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class GLAllocation(BaseModel):
    id: Optional[int] = None
    payment_id: int
    entry_id: Optional[int] = None
    debit_account: str = Field(..., max_length=20)
    credit_account: str = Field(..., max_length=20)
    amount: Decimal
    description: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)
