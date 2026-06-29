from typing import List, Dict, Optional, Any, ClassVar
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, ValidationError, _quantize_vnd


class TaxType(str, Enum):
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


class VATCalculationMethod(str, Enum):
    DIRECT = "direct"
    DEDUCTION = "deduction"


class PITRateType(str, Enum):
    PROGRESSIVE = "progressive"
    FLAT_RATE = "flat_rate"
    RENTAL_RATE = "rental_rate"


class DeclarationType(str, Enum):
    ORIGINAL = "original"
    SUPPLEMENTAL = "supplemental"
    FINALIZATION = "finalization"


class DeclarationStatus(str, Enum):
    DRAFT = "draft"
    CALCULATED = "calculated"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    AMENDED = "amended"
    CANCELLED = "cancelled"


class TaxPaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    REFUNDED = "refunded"
    PARTIAL = "partial"


class InvoiceStatus(str, Enum):
    CREATED = "created"
    SIGNED = "signed"
    SENT = "sent"
    CANCELLED = "cancelled"
    REPLACED = "replaced"
    ADJUSTED = "adjusted"
    ERROR = "error"


class TaxAdjustmentType(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    CORRECTION = "correction"
    CANCELLATION = "cancellation"


class TaxAdjustmentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class IncentiveStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class ScheduleStatus(str, Enum):
    PENDING = "pending"
    DUE = "due"
    OVERDUE = "overdue"
    FILED = "filed"
    PAID = "paid"


class InvoiceType(str, Enum):
    SALES = "sales"
    ADJUSTMENT = "adjustment"
    REPLACEMENT = "replacement"
    CANCEL = "cancel"


class EInvoiceAdjustmentType(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    REPLACE = "replace"
    CANCEL = "cancel"


class TaxIncentiveType(str, Enum):
    EXEMPTION = "exemption"
    REDUCTION = "reduction"
    PREFERENTIAL_RATE = "preferential_rate"
    TAX_HOLIDAY = "tax_holiday"
    TAX_CREDIT = "tax_credit"


class TaxDeclaration(BaseModel):
    VALID_FORM_CODE_PATTERN: ClassVar[str] = r'^\d{2}/\w+(-\w+)?$'
    MAX_FORM_CODE_LENGTH: ClassVar[int] = 20

    id: Optional[int] = Field(default=None)
    tax_type: TaxType = Field(...)
    declaration_type: DeclarationType = Field(default=DeclarationType.ORIGINAL)
    form_code: str = Field(..., max_length=MAX_FORM_CODE_LENGTH, description="GDT form code")
    period_year: int = Field(..., ge=2000, le=2100)
    period_month: Optional[int] = Field(default=None, ge=1, le=12)
    period_quarter: Optional[int] = Field(default=None, ge=1, le=4)
    status: DeclarationStatus = Field(default=DeclarationStatus.DRAFT)
    total_revenue: Decimal = Field(default=Decimal("0.00"))
    total_tax: Decimal = Field(default=Decimal("0.00"))
    total_deduction: Decimal = Field(default=Decimal("0.00"))
    total_exemption: Decimal = Field(default=Decimal("0.00"))
    total_payable: Decimal = Field(default=Decimal("0.00"))
    previous_adjustment: Decimal = Field(default=Decimal("0.00"))
    late_interest: Decimal = Field(default=Decimal("0.00"))
    penalty: Decimal = Field(default=Decimal("0.00"))
    net_payable: Decimal = Field(default=Decimal("0.00"))
    submission_deadline: Optional[date] = Field(default=None)
    submitted_date: Optional[date] = Field(default=None)
    accepted_date: Optional[date] = Field(default=None)
    gdt_reference: Optional[str] = Field(default=None, max_length=100)
    gdt_error_code: Optional[str] = Field(default=None, max_length=50)
    etax_submission_id: Optional[str] = Field(default=None, max_length=100)
    submission_method: str = Field(default="etax", description="etax|htkk|manual")
    notes: Optional[str] = Field(default=None, max_length=2000)
    created_by: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator('form_code')
    @classmethod
    def validate_form_code(cls, v):
        if not v.strip():
            raise ValidationError(ErrorCodes.FORM_CODE_EMPTY)
        return v.strip()

    @field_validator('period_year')
    @classmethod
    def validate_year(cls, v):
        if v < 2000 or v > 2100:
            raise ValidationError(ErrorCodes.YEAR_RANGE)
        return v

    @field_validator('total_revenue', 'total_tax', 'total_deduction', 'total_exemption',
                     'total_payable', 'previous_adjustment', 'late_interest', 'penalty', 'net_payable')
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode='after')
    def validate_period(self):
        monthly_types = {TaxType.VAT_DEDUCTION, TaxType.PIT, TaxType.RESOURCE}
        quarterly_types = {TaxType.VAT_DIRECT, TaxType.CIT, TaxType.ENVIRONMENTAL}
        annual_types = {TaxType.LICENSE, TaxType.PIT_FINALIZATION}
        if self.tax_type in monthly_types and not self.period_month:
            raise ValidationError(f"period_month required for {self.tax_type}")
        if self.tax_type in quarterly_types and not self.period_quarter:
            raise ValidationError(f"period_quarter required for {self.tax_type}")
        if self.period_month and self.period_quarter:
            raise ValidationError(ErrorCodes.TAX_BOTH_PERIOD)
        return self


class TaxLine(BaseModel):
    id: Optional[int] = Field(default=None)
    declaration_id: int = Field(..., description="FK to TaxDeclaration")
    line_code: str = Field(..., description="GDT form line code")
    label: str = Field(..., max_length=300, description="Line description in Vietnamese")
    amount: Decimal = Field(default=Decimal("0.00"))
    is_calculated: bool = Field(default=True, description="Auto-calculated vs manual")
    parent_line_id: Optional[int] = Field(default=None, description="FK to parent TaxLine")
    sort_order: int = Field(default=0)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator('line_code', 'label')
    @classmethod
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValidationError(ErrorCodes.TAX_FIELD_EMPTY)
        return v.strip()

    @field_validator('amount')
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class TaxPayment(BaseModel):
    VALID_BUDGET_ACCOUNTS: ClassVar[dict] = {
        TaxType.VAT_DEDUCTION: "1701", TaxType.VAT_DIRECT: "1701",
        TaxType.CIT: "1702", TaxType.PIT: "1703",
        TaxType.LICENSE: "1704", TaxType.FOREIGN_CONTRACTOR: "1705",
        TaxType.RESOURCE: "1706", TaxType.ENVIRONMENTAL: "1707",
    }

    id: Optional[int] = Field(default=None)
    declaration_id: int = Field(..., description="FK to TaxDeclaration")
    tax_type: TaxType = Field(...)
    amount: Decimal = Field(..., gt=Decimal("0"))
    payment_date: date = Field(...)
    due_date: date = Field(...)
    budget_account: str = Field(default="1701", max_length=10)
    payment_method: str = Field(default="etax", description="etax|bank|direct|treasury")
    payment_status: TaxPaymentStatus = Field(default=TaxPaymentStatus.PENDING)
    gdt_payment_code: Optional[str] = Field(default=None, max_length=100)
    bank_reference: Optional[str] = Field(default=None, max_length=100)
    penalty_interest: Decimal = Field(default=Decimal("0.00"))
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator('budget_account')
    @classmethod
    def validate_budget_account(cls, v):
        valid = list(cls.VALID_BUDGET_ACCOUNTS.values())
        if v not in valid:
            raise ValidationError(f"Budget account must be one of {valid}")
        return v

    @field_validator('amount', 'penalty_interest')
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode='after')
    def validate_budget_tax_match(self):
        expected = self.VALID_BUDGET_ACCOUNTS.get(self.tax_type)
        if expected and self.budget_account != expected:
            raise ValidationError(
                f"budget_account {self.budget_account} does not match tax_type {self.tax_type} "
                f"(expected {expected})"
            )
        return self


class TaxAdjustment(BaseModel):
    id: Optional[int] = Field(default=None)
    declaration_id: int = Field(..., description="FK to original TaxDeclaration")
    adjustment_type: TaxAdjustmentType = Field(...)
    supplemental_declaration_id: Optional[int] = Field(default=None)
    reason: str = Field(..., max_length=1000)
    original_amount: Decimal = Field(default=Decimal("0.00"))
    adjusted_amount: Decimal = Field(default=Decimal("0.00"))
    difference_amount: Decimal = Field(default=Decimal("0.00"))
    penalty_interest: Decimal = Field(default=Decimal("0.00"))
    penalty: Decimal = Field(default=Decimal("0.00"))
    status: TaxAdjustmentStatus = Field(default=TaxAdjustmentStatus.PENDING)
    review_notes: Optional[str] = Field(default=None, max_length=2000)
    reviewed_by: Optional[str] = Field(default=None, max_length=100)
    reviewed_at: Optional[datetime] = Field(default=None)
    created_by: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator('original_amount', 'adjusted_amount', 'difference_amount', 'penalty_interest', 'penalty')
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if not v.strip():
            raise ValueError(ErrorCodes.REASON_EMPTY)
        return v.strip()

    @model_validator(mode='after')
    def calculate_difference(self):
        self.difference_amount = self.adjusted_amount - self.original_amount
        return self


class TaxIncentive(BaseModel):
    id: Optional[int] = Field(default=None)
    tax_type: TaxType = Field(...)
    incentive_type: TaxIncentiveType = Field(...)
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=300)
    legal_basis: str = Field(..., max_length=200)
    rate_value: Decimal = Field(default=Decimal("0"))
    is_percentage: bool = Field(default=True)
    valid_from: date = Field(...)
    valid_to: Optional[date] = Field(default=None)
    max_duration_months: Optional[int] = Field(default=None)
    eligibility_condition: Optional[str] = Field(default=None, max_length=2000)
    requires_approval: bool = Field(default=False)
    status: IncentiveStatus = Field(default=IncentiveStatus.ACTIVE)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.strip():
            raise ValidationError(ErrorCodes.INCENTIVE_CODE_EMPTY)
        return v.strip().upper()

    @field_validator('rate_value')
    @classmethod
    def validate_rate(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode='after')
    def validate_date_range(self):
        if self.valid_to and self.valid_from and self.valid_to <= self.valid_from:
            raise ValidationError(ErrorCodes.VALID_TO_AFTER_FROM)
        return self


class EInvoice(BaseModel):
    VAT_RATE_DECIMAL_PLACES: ClassVar[int] = 4

    id: Optional[int] = Field(default=None)
    invoice_number: str = Field(..., max_length=20)
    invoice_series: str = Field(..., max_length=10)
    invoice_date: date = Field(...)
    invoice_type: InvoiceType = Field(default=InvoiceType.SALES)
    seller_tax_code: str = Field(..., max_length=15, pattern=r'^\d{10}(-\d{3})?$')
    seller_name: str = Field(..., max_length=300)
    seller_address: Optional[str] = Field(default=None, max_length=500)
    buyer_tax_code: Optional[str] = Field(default=None, max_length=15)
    buyer_name: Optional[str] = Field(default=None, max_length=300)
    buyer_address: Optional[str] = Field(default=None, max_length=500)
    buyer_id: Optional[str] = Field(default=None, max_length=50)

    subtotal: Decimal = Field(default=Decimal("0.00"))
    discount_amount: Decimal = Field(default=Decimal("0.00"))
    vat_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("1"))
    vat_amount: Decimal = Field(default=Decimal("0.00"))
    grand_total: Decimal = Field(default=Decimal("0.00"))

    currency: str = Field(default="VND")
    exchange_rate: Decimal = Field(default=Decimal("1"))
    payment_method: Optional[str] = Field(default=None, max_length=100)
    status: InvoiceStatus = Field(default=InvoiceStatus.CREATED)
    verification_code: Optional[str] = Field(default=None, max_length=50)
    gdt_transaction_id: Optional[str] = Field(default=None, max_length=100)
    signed_file_url: Optional[str] = Field(default=None, max_length=500)
    digital_signature: Optional[str] = Field(default=None)

    adjustment_ref_id: Optional[int] = Field(default=None)
    adjustment_type: Optional[EInvoiceAdjustmentType] = Field(default=None)
    adjustment_reason: Optional[str] = Field(default=None, max_length=500)
    original_invoice_ref: Optional[str] = Field(default=None, max_length=50)

    lines: List[Dict[str, Any]] = Field(default_factory=list)
    created_by: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator('seller_tax_code')
    @classmethod
    def validate_tax_code(cls, v):
        if not v.strip():
            raise ValidationError(ErrorCodes.TAX_CODE_EMPTY)
        return v.strip()

    @field_validator('subtotal', 'discount_amount', 'vat_amount', 'grand_total')
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @field_validator('vat_rate')
    @classmethod
    def validate_vat_rate(cls, v):
        return v.quantize(Decimal("0." + "0" * cls.VAT_RATE_DECIMAL_PLACES))


class EInvoiceLine(BaseModel):
    id: Optional[int] = Field(default=None)
    invoice_id: int = Field(...)
    line_number: int = Field(default=1, ge=1)
    product_code: Optional[str] = Field(default=None, max_length=50)
    product_name: str = Field(..., max_length=500)
    unit: str = Field(default="cái", max_length=50)
    quantity: Decimal = Field(default=Decimal("1"), gt=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    discount_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("1"))
    discount_amount: Decimal = Field(default=Decimal("0"))
    vat_rate: Decimal = Field(default=Decimal("0.1"), ge=Decimal("0"), le=Decimal("1"))
    vat_amount: Decimal = Field(default=Decimal("0"))
    total_line_amount: Decimal = Field(default=Decimal("0"))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator('unit_price', 'discount_amount', 'vat_amount', 'total_line_amount')
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @field_validator('vat_rate', 'discount_rate')
    @classmethod
    def validate_rate(cls, v):
        return v.quantize(Decimal("0.0001"))


class TaxSchedule(BaseModel):
    id: Optional[int] = Field(default=None)
    tax_type: TaxType = Field(...)
    period_year: int = Field(..., ge=2000, le=2100)
    period_month: Optional[int] = Field(default=None, ge=1, le=12)
    period_quarter: Optional[int] = Field(default=None, ge=1, le=4)
    due_date: date = Field(...)
    reminder_days_before: int = Field(default=7)
    status: ScheduleStatus = Field(default=ScheduleStatus.PENDING)
    assigned_to: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
