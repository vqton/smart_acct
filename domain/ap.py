from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum

from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd


class VendorType(str, Enum):
    INDIVIDUAL = "individual"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    FOREIGN = "foreign"


class VendorGroup(str, Enum):
    DOMESTIC = "domestic"
    IMPORT = "import"
    VIP = "vip"
    GOVT = "govt"


class VendorStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class APInvoiceType(str, Enum):
    PO_BASED = "po_based"
    NON_PO = "non_po"
    PREPAYMENT = "prepayment"


class APInvoiceStatus(str, Enum):
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


class APPaymentStatus(str, Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTING = "executing"
    EXECUTED = "executed"
    POSTED = "posted"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class APPaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CARD = "card"


class FCTMethod(str, Enum):
    DIRECT = "direct"
    DEDUCTION = "deduction"
    HYBRID = "hybrid"


class FCTStatus(str, Enum):
    PENDING = "pending"
    DECLARED = "declared"
    REMITTED = "remitted"
    OVERDUE = "overdue"


class PrepaymentStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    CANCELLED = "cancelled"


class ProvisionStatus(str, Enum):
    ACTIVE = "active"
    PARTIALLY_WRITTEN_OFF = "partially_written_off"
    FULLY_WRITTEN_OFF = "fully_written_off"


class Vendor(BaseModel):
    id: Optional[int] = None
    vendor_code: str = Field(..., min_length=1, max_length=20)
    vendor_name: str = Field(..., min_length=1, max_length=300)
    legal_name: Optional[str] = Field(None, max_length=300)
    tax_code: Optional[str] = Field(None, max_length=20)
    vendor_type: VendorType = VendorType.ENTERPRISE
    vendor_group: VendorGroup = VendorGroup.DOMESTIC
    status: VendorStatus = VendorStatus.ACTIVE
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    country: str = "VN"
    contact_person: Optional[str] = Field(None, max_length=100)
    payment_terms: str = "net_30"
    currency: str = "VND"
    bank_name: Optional[str] = Field(None, max_length=200)
    bank_account: Optional[str] = Field(None, max_length=50)
    bank_swift: Optional[str] = Field(None, max_length=20)
    credit_limit: Decimal = Decimal("0")
    coa_code: Optional[str] = Field(None, max_length=20)
    foreign_ct_type: Optional[str] = Field(None, max_length=20)
    foreign_vat_rate: Optional[Decimal] = None
    foreign_cit_rate: Optional[Decimal] = None
    notes: Optional[str] = Field(None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("credit_limit")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class APInvoiceLine(BaseModel):
    id: Optional[int] = None
    ap_invoice_id: Optional[int] = None
    line_number: int
    description: str = Field(..., max_length=500)
    quantity: Decimal
    unit_price: Decimal
    line_amount: Decimal
    tax_rate: Decimal = Decimal("0.10")
    tax_amount: Decimal = Decimal("0")
    coa_code: Optional[str] = Field(None, max_length=20)
    po_line_number: Optional[int] = None
    gr_line_number: Optional[int] = None

    @field_validator("quantity", "unit_price", "line_amount", "tax_rate", "tax_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class APInvoice(BaseModel):
    id: Optional[int] = None
    invoice_number: str = Field(..., min_length=1, max_length=20)
    vendor_id: int
    vendor_code: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_type: APInvoiceType = APInvoiceType.NON_PO
    status: APInvoiceStatus = APInvoiceStatus.DRAFT
    invoice_date: date
    due_date: date
    discount_date: Optional[date] = None
    discount_percent: Optional[Decimal] = None
    posted_date: Optional[date] = None
    amount: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal
    paid_amount: Decimal = Decimal("0")
    written_off_amount: Decimal = Decimal("0")
    balance_due: Decimal
    currency: str = "VND"
    fx_rate: Optional[Decimal] = None
    fx_gl_rate: Optional[Decimal] = None
    po_number: Optional[str] = Field(None, max_length=20)
    gr_number: Optional[str] = Field(None, max_length=20)
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    period: Optional[str] = Field(None, max_length=10)
    coa_code: str = Field(default="331", max_length=20)
    created_by: Optional[str] = Field(None, max_length=100)
    approved_by: Optional[str] = Field(None, max_length=100)
    approved_at: Optional[datetime] = None
    lines: List[APInvoiceLine] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount", "discount_amount", "tax_amount", "total_amount", "paid_amount",
                     "written_off_amount", "balance_due")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class APPayment(BaseModel):
    id: Optional[int] = None
    payment_number: str = Field(..., min_length=1, max_length=20)
    vendor_id: int
    payment_date: date
    amount: Decimal
    discount_taken: Decimal = Decimal("0")
    net_amount: Decimal
    payment_method: APPaymentMethod
    bank_account_id: Optional[int] = None
    reference: Optional[str] = Field(None, max_length=100)
    status: APPaymentStatus = APPaymentStatus.DRAFT
    is_batch_payment: bool = False
    batch_id: Optional[int] = None
    approval_by: Optional[str] = Field(None, max_length=100)
    approval_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount", "discount_taken", "net_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class APPaymentAllocation(BaseModel):
    id: Optional[int] = None
    ap_payment_id: int
    ap_invoice_id: int
    allocated_amount: Decimal
    is_adjustment: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("allocated_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class VendorPrepayment(BaseModel):
    id: Optional[int] = None
    vendor_id: int
    amount: Decimal
    unapplied_balance: Decimal
    payment_date: date
    expected_invoice_date: Optional[date] = None
    reference: Optional[str] = Field(None, max_length=100)
    status: PrepaymentStatus = PrepaymentStatus.PENDING
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount", "unapplied_balance")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class APProvision(BaseModel):
    id: Optional[int] = None
    vendor_id: int
    period: str = Field(..., max_length=10)
    provision_percent: Decimal
    overdue_days: int
    invoice_total: Decimal
    provision_amount: Decimal
    status: ProvisionStatus = ProvisionStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("invoice_total", "provision_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class APAgingSnapshot(BaseModel):
    id: Optional[int] = None
    period: str = Field(..., max_length=10)
    vendor_id: int
    vendor_code: str = Field(..., max_length=20)
    vendor_name: str = Field(..., max_length=300)
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


class FCTDeclaration(BaseModel):
    id: Optional[int] = None
    vendor_id: int
    period: str = Field(..., max_length=10)
    invoice_id: int
    fct_method: FCTMethod
    vat_rate: Decimal
    cit_rate: Decimal
    gross_amount: Decimal
    vat_amount: Decimal
    cit_amount: Decimal
    net_amount: Decimal
    status: FCTStatus = FCTStatus.PENDING
    declared_at: Optional[datetime] = None
    remitted_at: Optional[datetime] = None
    due_date: date
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("gross_amount", "vat_amount", "cit_amount", "net_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class IntercompanyInvoice(BaseModel):
    id: Optional[int] = None
    from_entity_code: str = Field(..., max_length=20)
    to_entity_code: str = Field(..., max_length=20)
    invoice_number: str = Field(..., max_length=20)
    invoice_date: date
    amount: Decimal
    currency: str = "VND"
    description: str = Field(..., max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)
