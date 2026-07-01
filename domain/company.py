from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum

from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd


class DocumentType(str, Enum):
    AR_INVOICE = "ar_invoice"
    AP_INVOICE = "ap_invoice"
    CASH_RECEIPT = "cash_receipt"
    CASH_PAYMENT = "cash_payment"
    JOURNAL_ENTRY = "journal_entry"
    PURCHASE_ORDER = "purchase_order"
    SALES_ORDER = "sales_order"
    INVENTORY_RECEIPT = "inventory_receipt"
    INVENTORY_ISSUE = "inventory_issue"
    PAYMENT = "payment"
    RECEIPT = "receipt"


class SetupSection(str, Enum):
    COMPANY_INFO = "company_info"
    FISCAL_YEAR = "fiscal_year"
    CURRENCY = "currency"
    COA = "coa"
    OPENING_BALANCES = "opening_balances"
    DEPARTMENTS = "departments"
    WAREHOUSES = "warehouses"
    EMPLOYEES = "employees"
    CUSTOMERS = "customers"
    VENDORS = "vendors"
    TAX_RATES = "tax_rates"
    NUMBERING_RULES = "numbering_rules"
    USER_PERMISSIONS = "user_permissions"


class Company(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    tax_code: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    business_reg_number: Optional[str] = Field(None, max_length=50)
    date_format: str = "DD/MM/YYYY"
    currency_code: str = "VND"
    fiscal_year_start_month: int = 1
    accounting_regime: str = "TT99"
    locale: str = "vi"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.COMPANY_NAME_EMPTY)
        return v.strip()

    @field_validator("tax_code")
    @classmethod
    def validate_tax_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and (len(v) < 10 or len(v) > 14):
                raise VASValidationError(ErrorCodes.COMPANY_TAX_CODE_INVALID)
        return v

    @field_validator("fiscal_year_start_month")
    @classmethod
    def validate_fiscal_year_start_month(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise VASValidationError(ErrorCodes.FISCAL_YEAR_INVALID)
        return v

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.CURRENCY_EMPTY)
        return v.strip().upper()

    @model_validator(mode="after")
    def validate_locale(self):
        if self.locale not in ("vi", "en"):
            raise VASValidationError(ErrorCodes.AUTH_INVALID_LOCALE)
        return self


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    tax_code: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    business_reg_number: Optional[str] = Field(None, max_length=50)
    date_format: str = "DD/MM/YYYY"
    currency_code: str = "VND"
    fiscal_year_start_month: int = 1
    accounting_regime: str = "TT99"
    locale: str = "vi"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.COMPANY_NAME_EMPTY)
        return v.strip()

    @field_validator("tax_code")
    @classmethod
    def validate_tax_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and (len(v) < 10 or len(v) > 14):
                raise VASValidationError(ErrorCodes.COMPANY_TAX_CODE_INVALID)
        return v

    @field_validator("fiscal_year_start_month")
    @classmethod
    def validate_fiscal_year_start_month(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise VASValidationError(ErrorCodes.FISCAL_YEAR_INVALID)
        return v

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.CURRENCY_EMPTY)
        return v.strip().upper()


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    tax_code: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    business_reg_number: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = None
    currency_code: Optional[str] = None
    fiscal_year_start_month: Optional[int] = None
    accounting_regime: Optional[str] = None
    locale: Optional[str] = None
    is_active: Optional[bool] = None


class FiscalYearConfig(BaseModel):
    id: Optional[int] = None
    company_id: int
    fiscal_year: int = Field(..., ge=2000, le=2200)
    start_date: date
    end_date: date
    is_closed: bool = False
    is_current: bool = False

    @field_validator("fiscal_year")
    @classmethod
    def validate_fiscal_year(cls, v: int) -> int:
        return v

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start_date >= self.end_date:
            raise VASValidationError(ErrorCodes.FISCAL_YEAR_INVALID)
        if self.start_date.year != self.fiscal_year and self.end_date.year not in (self.fiscal_year, self.fiscal_year + 1):
            raise VASValidationError(ErrorCodes.FISCAL_YEAR_INVALID)
        return self


class FiscalYearCreate(BaseModel):
    fiscal_year: int = Field(..., ge=2000, le=2200)
    start_date: date
    end_date: date
    is_current: bool = False

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start_date >= self.end_date:
            raise VASValidationError(ErrorCodes.FISCAL_YEAR_INVALID)
        return self


class NumberingRule(BaseModel):
    id: Optional[int] = None
    company_id: int
    document_type: DocumentType
    prefix: str = ""
    suffix: str = ""
    next_number: int = 1
    pad_length: int = 6
    fiscal_year: int

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        if v is None:
            return ""
        return v.strip()

    @field_validator("pad_length")
    @classmethod
    def validate_pad_length(cls, v: int) -> int:
        if v < 1 or v > 20:
            raise VASValidationError(ErrorCodes.INVALID_ACCOUNT_TYPE)
        return v

    @field_validator("next_number")
    @classmethod
    def validate_next_number(cls, v: int) -> int:
        if v < 0:
            raise VASValidationError(ErrorCodes.INVALID_ACCOUNT_TYPE)
        return v


class NumberingRuleUpdate(BaseModel):
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    next_number: Optional[int] = None
    pad_length: Optional[int] = None


class SetupChecklistItem(BaseModel):
    id: Optional[int] = None
    company_id: int
    section: SetupSection
    label: str = Field(..., min_length=1, max_length=255)
    is_completed: bool = False
    sort_order: int = 0

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.MISSING_FIELD)
        return v.strip()
