from typing import List, Optional, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, ValidationError, _quantize_vnd


class BankAccountStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    BLOCKED = "blocked"


class BankSubAccountType(str, Enum):
    VND = "1121"
    FC = "1122"


class ReconciliationDiscrepancyType(str, Enum):
    DEPOSIT_IN_TRANSIT = "deposit_in_transit"
    OUTSTANDING_CHECK = "outstanding_check"
    BANK_CHARGE = "bank_charge"
    BANK_INTEREST = "bank_interest"
    ERROR = "error"


class BankAccount(BaseModel):
    id: Optional[int] = None
    bank_name: str = Field(..., min_length=1, max_length=200)
    branch: str = Field(..., min_length=1, max_length=200)
    account_number: str = Field(..., min_length=1, max_length=50)
    account_holder: str = Field(..., min_length=1, max_length=300)
    currency: str = "VND"
    coa_code: str
    sub_account_type: Optional[BankSubAccountType] = None
    swift_code: Optional[str] = None
    iban: Optional[str] = None
    opening_balance: Decimal = Decimal("0")
    status: BankAccountStatus = BankAccountStatus.ACTIVE
    signatories: List[str] = Field(default_factory=list)
    authorization_limit: Decimal = Decimal("0")
    last_reconciled_period: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("opening_balance", "authorization_limit")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @field_validator("sub_account_type", mode="before")
    @classmethod
    def coerce_sub_account_type(cls, v):
        if v is None or isinstance(v, BankSubAccountType):
            return v
        if isinstance(v, str):
            return BankSubAccountType(v)
        raise ValueError(f"Invalid sub_account_type: {v}")

    @model_validator(mode="after")
    def check_sub_account_consistency(self):
        if self.sub_account_type and not self.coa_code.startswith("112"):
            raise ValueError(f"sub_account_type={self.sub_account_type.value} requires coa_code starting with 112, got {self.coa_code}")
        return self


class BankTransaction(BaseModel):
    id: Optional[int] = None
    bank_account_id: int
    transaction_date: date
    value_date: Optional[date] = None
    amount: Decimal
    is_debit: bool
    reference: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    matched_entry_id: Optional[int] = None
    statement_id: Optional[int] = None

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class BankStatement(BaseModel):
    id: Optional[int] = None
    bank_account_id: int
    statement_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    transactions: List[BankTransaction] = Field(default_factory=list)
    imported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(..., pattern=r'^(mt940|csv|pdf|api)$')

    @field_validator("opening_balance", "closing_balance")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class ReconciliationDiscrepancy(BaseModel):
    id: Optional[int] = None
    reconciliation_id: int
    discrepancy_type: ReconciliationDiscrepancyType
    amount: Decimal
    entry_side: str = Field(..., pattern=r'^(book|bank)$')
    reference: Optional[str] = None
    description: Optional[str] = None
    status: str = "unresolved"
    resolution_entry_id: Optional[int] = None

    @field_validator("amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class BankReconciliation(BaseModel):
    id: Optional[int] = None
    bank_account_id: int
    period: str
    book_balance: Decimal
    bank_balance: Decimal
    deposits_in_transit: Decimal = Decimal("0")
    outstanding_checks: Decimal = Decimal("0")
    unrecorded_credits: Decimal = Decimal("0")
    unrecorded_debits: Decimal = Decimal("0")
    adjusted_book_balance: Decimal = Decimal("0")
    adjusted_bank_balance: Decimal = Decimal("0")
    is_balanced: bool = False
    reconciled_at: Optional[datetime] = None
    reconciled_by: Optional[str] = None
    discrepancies: List[ReconciliationDiscrepancy] = Field(default_factory=list)

    @field_validator("book_balance", "bank_balance", "deposits_in_transit",
                     "outstanding_checks", "unrecorded_credits", "unrecorded_debits",
                     "adjusted_book_balance", "adjusted_bank_balance")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode="after")
    def compute_adjusted_balances(self):
        self.adjusted_book_balance = self.book_balance - self.outstanding_checks + self.deposits_in_transit
        self.adjusted_bank_balance = self.bank_balance - self.unrecorded_debits + self.unrecorded_credits
        self.is_balanced = abs(self.adjusted_book_balance - self.adjusted_bank_balance) <= Decimal("0.001")
        return self
