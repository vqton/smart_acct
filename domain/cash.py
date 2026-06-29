from typing import List, Dict, Optional, Any, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, ValidationError, InvalidCurrencyError, _quantize_vnd


class CashReceiptType(str, Enum):
    SALES = "sales"
    COLLECTION = "collection"
    BANK_WITHDRAWAL = "bank_withdrawal"
    ADVANCE_RETURN = "advance_return"
    OTHER = "other"


class CashPaymentType(str, Enum):
    EXPENSE = "expense"
    PURCHASE = "purchase"
    SALARY = "salary"
    ADVANCE = "advance"
    SETTLEMENT = "settlement"
    BANK_DEPOSIT = "bank_deposit"
    OTHER = "other"


class CashVoucherStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class PettyCashFundStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class CashTransferStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    FAILED = "failed"


class CashReceipt(BaseModel):
    id: Optional[int] = None
    receipt_number: str = Field(..., pattern=r'^PT-\d{6}-\d{5}$', description="PT-YYYYMM-NNNNN")
    receipt_date: date
    receipt_type: CashReceiptType
    payer_name: str = Field(..., min_length=1, max_length=300)
    amount: Decimal = Field(..., gt=Decimal("0"))
    amount_in_words: str = Field(..., min_length=1, max_length=500)
    currency: str = "VND"
    fx_rate: Optional[Decimal] = None
    account_code: str
    counter_account: str
    reference_number: Optional[str] = None
    description: str = Field(..., min_length=1, max_length=500)
    status: CashVoucherStatus = CashVoucherStatus.DRAFT
    created_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        return _quantize_vnd(v)


class CashPayment(BaseModel):
    id: Optional[int] = None
    payment_number: str = Field(..., pattern=r'^PC-\d{6}-\d{5}$', description="PC-YYYYMM-NNNNN")
    payment_date: date
    payment_type: CashPaymentType
    receiver_name: str = Field(..., min_length=1, max_length=300)
    amount: Decimal = Field(..., gt=Decimal("0"))
    amount_in_words: str = Field(..., min_length=1, max_length=500)
    currency: str = "VND"
    fx_rate: Optional[Decimal] = None
    account_code: str
    counter_account: str
    reference_number: Optional[str] = None
    supporting_doc_ref: Optional[str] = None
    description: str = Field(..., min_length=1, max_length=500)
    status: CashVoucherStatus = CashVoucherStatus.DRAFT
    created_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        return _quantize_vnd(v)


class PettyCashFund(BaseModel):
    id: Optional[int] = None
    fund_code: str = Field(..., min_length=1, max_length=50)
    custodian: str = Field(..., min_length=1, max_length=200)
    limit_amount: Decimal = Field(..., gt=Decimal("0"))
    current_balance: Decimal = Decimal("0")
    currency: str = "VND"
    established_date: date
    status: PettyCashFundStatus = PettyCashFundStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("limit_amount", "current_balance")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v):
        if v.upper() not in ["VND", "USD", "EUR", "JPY", "GBP"]:
            raise InvalidCurrencyError(ErrorCodes.CASH_CURRENCY_NOT_SUPPORTED)
        return v.upper()


class PettyCashTransaction(BaseModel):
    id: Optional[int] = None
    fund_id: int
    transaction_date: date
    amount: Decimal
    is_replenishment: bool
    reference_number: Optional[str] = None
    description: str = Field(..., max_length=500)
    receipt_ref: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class CashTransfer(BaseModel):
    id: Optional[int] = None
    source_account: str
    destination_account: str
    amount: Decimal = Field(..., gt=Decimal("0"))
    transfer_date: date
    fx_rate: Optional[Decimal] = None
    reference: str = Field(..., max_length=100)
    status: CashTransferStatus = CashTransferStatus.PENDING
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode="after")
    def validate_no_self_transfer(self):
        if self.source_account == self.destination_account:
            raise ValidationError(ErrorCodes.TRANSFER_SAME_ACCOUNT)
        return self


class ChequeBook(BaseModel):
    id: Optional[int] = None
    bank_account_id: int
    start_number: str = Field(..., min_length=1, max_length=20)
    end_number: str = Field(..., min_length=1, max_length=20)
    issued_date: date
    status: str = "active"

    @model_validator(mode="after")
    def validate_range(self):
        if self.start_number >= self.end_number:
            raise ValidationError(ErrorCodes.CHEQUE_END_GREATER)
        return self


class ChequeStatus(str, Enum):
    NEW = "new"
    ISSUED = "issued"
    CLEARED = "cleared"
    CANCELLED = "cancelled"
    STOPPED = "stopped"
    BOUNCED = "bounced"


class Cheque(BaseModel):
    id: Optional[int] = None
    cheque_number: str = Field(..., min_length=1, max_length=20)
    cheque_book_id: int
    payee: str = Field(..., min_length=1, max_length=300)
    amount: Decimal = Field(..., gt=Decimal("0"))
    issue_date: date
    status: ChequeStatus = ChequeStatus.NEW
    bank_account_id: int
    cleared_date: Optional[date] = None
    cancelled_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class CashForecast(BaseModel):
    id: Optional[int] = None
    period_start: date
    period_end: date
    projected_inflows: Decimal = Decimal("0")
    projected_outflows: Decimal = Decimal("0")
    net_cash_flow: Decimal = Decimal("0")
    opening_balance: Decimal = Decimal("0")
    closing_balance: Decimal = Decimal("0")
    currency: str = "VND"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("projected_inflows", "projected_outflows", "net_cash_flow",
                     "opening_balance", "closing_balance")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class CashForecastLine(BaseModel):
    id: Optional[int] = None
    forecast_id: int
    date: date
    description: str = Field(..., max_length=500)
    amount: Decimal
    is_inflow: bool
    category: str = Field(..., max_length=100)

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class DailyCashCount(BaseModel):
    id: Optional[int] = None
    count_date: date
    account_code: str
    expected_balance: Decimal
    actual_balance: Decimal
    difference: Decimal = Decimal("0")
    denomination_breakdown: Dict[str, int] = Field(default_factory=dict)
    notes: Optional[str] = None
    counted_by: str
    witnessed_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("expected_balance", "actual_balance", "difference")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode="after")
    def compute_difference(self):
        self.difference = self.actual_balance - self.expected_balance
        return self


class Advance(BaseModel):
    id: Optional[int] = None
    employee_name: str = Field(..., min_length=1, max_length=200)
    employee_id: str = Field(..., min_length=1, max_length=50)
    amount: Decimal = Field(..., gt=Decimal("0"))
    advance_date: date
    purpose: str = Field(..., min_length=1, max_length=500)
    settlement_deadline: date
    settlement_amount: Decimal = Decimal("0")
    remaining_balance: Decimal = Decimal("0")
    status: str = "outstanding"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("amount", "settlement_amount", "remaining_balance")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode="after")
    def compute_remaining(self):
        self.remaining_balance = self.amount - self.settlement_amount
        return self
