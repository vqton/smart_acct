from typing import List, Optional, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator
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
    LEVEL_4 = "level_4"
    LEVEL_5 = "legal"


class WriteOffRequestStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


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
    credit_limit_override: bool = False
    credit_limit_override_expires: Optional[date] = None
    credit_rating: Optional[str] = Field(None, max_length=10)
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
    dunning_level: int = 0
    next_dunning_date: Optional[date] = None
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
    customer_id: Optional[int] = None
    invoice_id: int
    payment_date: date
    amount: Decimal
    payment_method: ARPaymentMethod
    reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    received_by: Optional[str] = Field(None, max_length=50)
    bank_account_id: Optional[int] = None
    coa_code: Optional[str] = Field(None, max_length=20)
    amount_applied: Decimal = Decimal("0")
    amount_unapplied: Decimal = Decimal("0")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount", "amount_applied", "amount_unapplied")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class ARPaymentAllocation(BaseModel):
    id: Optional[int] = None
    ar_payment_id: int
    ar_invoice_id: int
    allocated_amount: Decimal
    is_adjustment: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("allocated_amount")
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


class ARAgingSnapshot(BaseModel):
    id: Optional[int] = None
    period: str = Field(..., max_length=10)
    customer_id: int
    customer_code: str = Field(..., max_length=20)
    customer_name: str = Field(..., max_length=300)
    current_amount: Decimal = Decimal("0")
    bucket_1_30: Decimal = Decimal("0")
    bucket_31_60: Decimal = Decimal("0")
    bucket_61_90: Decimal = Decimal("0")
    bucket_91_180: Decimal = Decimal("0")
    bucket_181_365: Decimal = Decimal("0")
    bucket_365_plus: Decimal = Decimal("0")
    total_outstanding: Decimal = Decimal("0")
    locked: bool = False
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("current_amount", "bucket_1_30", "bucket_31_60", "bucket_61_90",
                     "bucket_91_180", "bucket_181_365", "bucket_365_plus", "total_outstanding")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class ARDunningLog(BaseModel):
    id: Optional[int] = None
    ar_invoice_id: int
    dunning_level: int
    dunning_date: date
    dunning_method: str = Field(default="email", max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)
    performed_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BadDebtProvision(BaseModel):
    id: Optional[int] = None
    customer_id: int
    ar_invoice_id: int
    period: str = Field(..., max_length=10)
    provision_percent: Decimal = Decimal("0")
    invoice_amount: Decimal = Decimal("0")
    provision_amount: Decimal = Decimal("0")
    is_written_off: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("invoice_amount", "provision_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class BadDebtWriteOffRequest(BaseModel):
    id: Optional[int] = None
    ar_invoice_id: int
    customer_id: int
    reason: str = Field(..., max_length=1000)
    supporting_docs: Optional[str] = Field(None, max_length=500)
    status: WriteOffRequestStatus = WriteOffRequestStatus.PENDING_APPROVAL
    approval_by: Optional[str] = Field(None, max_length=100)
    approval_notes: Optional[str] = Field(None, max_length=1000)
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class CEIReport(BaseModel):
    period: str = Field(..., max_length=10)
    beginning_ar: Decimal = Decimal("0")
    credit_sales: Decimal = Decimal("0")
    ending_ar: Decimal = Decimal("0")
    bad_debt: Decimal = Decimal("0")
    cei: Decimal = Decimal("0")
    dso: Decimal = Decimal("0")
    days_in_period: int = 30
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("beginning_ar", "credit_sales", "ending_ar", "bad_debt", "cei", "dso")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)
