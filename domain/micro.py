from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, ValidationError, _quantize_vnd


class MicroTaxMethod(str, Enum):
    BOTH_PCT_ON_REVENUE = "both_pct_revenue"
    GTGT_PCT_TNDN_INCOME = "gtgt_pct_revenue_tndn_income"
    GTGT_DEDUCTION_TNDN_PCT = "gtgt_deduction_tndn_pct_revenue"
    GTGT_DEDUCTION_TNDN_INCOME = "gtgt_deduction_tndn_income"


class MicroBookType(str, Enum):
    REVENUE_BOOK = "revenue_book"
    EXPENSE_BOOK = "expense_book"
    MATERIAL_BOOK = "material_book"
    CASH_BOOK = "cash_book"
    VAT_TRACKING = "vat_tracking"


class MicroBCTCFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class MicroEnterpriseSetup(BaseModel):
    id: Optional[int] = None
    enterprise_name: str = Field(..., min_length=1, max_length=300)
    tax_code: str = Field(..., min_length=10, max_length=20)
    tax_method: MicroTaxMethod = Field(...)
    address: Optional[str] = Field(default=None, max_length=500)
    representative: Optional[str] = Field(default=None, max_length=100)
    accountant: Optional[str] = Field(default=None, max_length=100)
    uses_external_accounting: bool = False
    has_chief_accountant: bool = False
    bctc_frequency: MicroBCTCFrequency = MicroBCTCFrequency.ANNUAL
    fiscal_year_start: date = Field(default_factory=lambda: date(date.today().year, 1, 1))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class MicroRevenueBook(BaseModel):
    id: Optional[int] = None
    enterprise_id: int = Field(...)
    period: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    product_group: str = Field(..., max_length=200)
    invoice_ref: Optional[str] = Field(default=None, max_length=100)
    revenue_amount: Decimal = Field(default=Decimal("0"))
    gtgt_rate_pct: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("100"))
    gtgt_tax: Decimal = Field(default=Decimal("0"))
    tndn_rate_pct: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("100"))
    tndn_tax: Decimal = Field(default=Decimal("0"))
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("revenue_amount", "gtgt_tax", "tndn_tax")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class MicroExpenseBook(BaseModel):
    id: Optional[int] = None
    enterprise_id: int = Field(...)
    period: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    expense_category: str = Field(..., max_length=200)
    expense_amount: Decimal = Field(default=Decimal("0"))
    is_deductible: bool = True
    invoice_ref: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("expense_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class MicroCashBook(BaseModel):
    id: Optional[int] = None
    enterprise_id: int = Field(...)
    transaction_date: date = Field(...)
    description: str = Field(..., max_length=500)
    receipt_amount: Decimal = Field(default=Decimal("0"))
    payment_amount: Decimal = Field(default=Decimal("0"))
    running_balance: Decimal = Field(default=Decimal("0"))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("receipt_amount", "payment_amount", "running_balance")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class MicroMaterialBook(BaseModel):
    id: Optional[int] = None
    enterprise_id: int = Field(...)
    period: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    material_name: str = Field(..., max_length=200)
    opening_quantity: Decimal = Field(default=Decimal("0"))
    opening_value: Decimal = Field(default=Decimal("0"))
    import_quantity: Decimal = Field(default=Decimal("0"))
    import_value: Decimal = Field(default=Decimal("0"))
    export_quantity: Decimal = Field(default=Decimal("0"))
    export_value: Decimal = Field(default=Decimal("0"))
    closing_quantity: Decimal = Field(default=Decimal("0"))
    closing_value: Decimal = Field(default=Decimal("0"))
    unit: str = Field(default="cái", max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("opening_value", "import_value", "export_value", "closing_value")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class MicroBCTCSimplified(BaseModel):
    b01_dnsn_items: List[dict] = Field(default_factory=lambda: [
        {"ma_so": "100", "ten": "Tiền", "amount": "0"},
        {"ma_so": "200", "ten": "Tổng tài sản", "amount": "0"},
        {"ma_so": "300", "ten": "Nợ phải trả", "amount": "0"},
        {"ma_so": "400", "ten": "Vốn chủ sở hữu", "amount": "0"},
    ])
    b02_dnsn_items: List[dict] = Field(default_factory=lambda: [
        {"ma_so": "01", "ten": "Doanh thu", "amount": "0"},
        {"ma_so": "02", "ten": "Chi phí", "amount": "0"},
        {"ma_so": "03", "ten": "Lợi nhuận", "amount": "0"},
        {"ma_so": "04", "ten": "Thuế TNDN phải nộp", "amount": "0"},
    ])
    period: str = Field(..., pattern=r"^\d{4}(-\d{2})?$")
    enterprise_name: str = Field(..., max_length=300)
    tax_code: str = Field(..., max_length=20)
    tax_method: MicroTaxMethod = Field(...)


class MicroTaxCalculation(BaseModel):
    enterprise_id: int = Field(...)
    period: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    tax_method: MicroTaxMethod = Field(...)
    total_revenue: Decimal = Field(default=Decimal("0"))
    total_expenses: Decimal = Field(default=Decimal("0"))
    taxable_income: Decimal = Field(default=Decimal("0"))
    gtgt_rate_pct: Decimal = Field(default=Decimal("0"))
    gtgt_payable: Decimal = Field(default=Decimal("0"))
    gtgt_input: Decimal = Field(default=Decimal("0"))
    gtgt_output: Decimal = Field(default=Decimal("0"))
    tndn_rate_pct: Decimal = Field(default=Decimal("0"))
    tndn_payable: Decimal = Field(default=Decimal("0"))
    notes: Optional[str] = None

    @field_validator("total_revenue", "total_expenses", "taxable_income",
                     "gtgt_payable", "gtgt_input", "gtgt_output", "tndn_payable")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    def compute_taxes(self) -> Dict[str, Decimal]:
        if self.tax_method in (MicroTaxMethod.BOTH_PCT_ON_REVENUE,
                               MicroTaxMethod.GTGT_PCT_TNDN_INCOME):
            self.gtgt_payable = (self.total_revenue * self.gtgt_rate_pct / Decimal("100")).quantize(Decimal("0.01"))
        else:
            self.gtgt_payable = max(self.gtgt_output - self.gtgt_input, Decimal("0"))

        if self.tax_method in (MicroTaxMethod.BOTH_PCT_ON_REVENUE,
                               MicroTaxMethod.GTGT_DEDUCTION_TNDN_PCT):
            self.tndn_payable = (self.total_revenue * self.tndn_rate_pct / Decimal("100")).quantize(Decimal("0.01"))
        else:
            self.taxable_income = max(self.total_revenue - self.total_expenses, Decimal("0"))
            self.tndn_payable = (self.taxable_income * self.tndn_rate_pct / Decimal("100")).quantize(Decimal("0.01"))

        return {
            "gtgt_payable": self.gtgt_payable,
            "tndn_payable": self.tndn_payable,
            "taxable_income": self.taxable_income,
            "total_tax": (self.gtgt_payable + self.tndn_payable).quantize(Decimal("0.01")),
        }
