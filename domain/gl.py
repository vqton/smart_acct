from typing import List, Dict, Optional, Any, ClassVar
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
import re
from domain.i18n import ErrorCodes
from domain.common import (
    VASValidationError, ValidationError, DoubleEntryError, DateError,
    VASComplianceError, _quantize_vnd,
)


class JournalEntry(BaseModel):
    id: Optional[int] = Field(default=None)
    journal_number: str = Field(..., min_length=1, max_length=50, pattern=r'^JV\d{6,8}$',
                                description="Journal entry number with JV prefix")
    transaction_date: date = Field(..., description="Transaction date")
    description: str = Field(..., min_length=1, max_length=500, description="Transaction description")
    lines: List[Any] = Field(default_factory=list, description="Journal entry lines")
    is_posted: bool = Field(default=False, description="Whether the entry has been posted")
    posted_date: Optional[date] = Field(default=None, description="Date when the entry was posted")
    tolerance_difference: Optional[Decimal] = Field(default=None)
    is_valid: Optional[bool] = Field(default=None, description="Validation status")
    vat_rate: Optional[Decimal] = Field(default=None, description="VAT rate (0.00 to 1.00)")
    period: str = Field(default_factory=lambda: date.today().strftime("%Y-%m"), description="Accounting period")
    source_module: Optional[str] = Field(default=None, description="Module that created this entry")
    created_by: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    VIETNAMESE_CURRENCIES: ClassVar[list] = ["VND", "USD", "EUR", "JPY", "GBP"]
    MAX_VAT_RATE: ClassVar[Decimal] = Decimal("1.00")
    MAX_VAT_RATE_PERCENT: ClassVar[float] = 100.00
    DOUBLE_ENTRY_TOLERANCE: ClassVar[Decimal] = Decimal("0.001")
    MAX_JOURNAL_DESCRIPTION_LENGTH: ClassVar[int] = 500

    @field_validator('journal_number')
    @classmethod
    def validate_journal_number(cls, v):
        if not v.startswith('JV'):
            raise ValidationError(ErrorCodes.JOURNAL_NUMBER_PREFIX)
        suffix = v[2:]
        if not suffix.isdigit():
            raise ValidationError(ErrorCodes.JOURNAL_NUMBER_SUFFIX)
        return v

    @field_validator('transaction_date')
    @classmethod
    def validate_date(cls, v):
        if v is None:
            raise ValidationError(ErrorCodes.TRANSACTION_DATE_NONE)
        if v.year < 2000 or v.year > 2100:
            raise DateError("Transaction date must be between 2000-2100")
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v.strip():
            raise ValidationError(ErrorCodes.DESCRIPTION_EMPTY)
        if len(v) > cls.MAX_JOURNAL_DESCRIPTION_LENGTH:
            raise ValidationError(
                f"Description cannot exceed {cls.MAX_JOURNAL_DESCRIPTION_LENGTH} characters"
            )
        return v.strip()

    @field_validator('vat_rate')
    @classmethod
    def validate_vat_rate(cls, v):
        if v is not None:
            if not Decimal("0.00") <= v <= cls.MAX_VAT_RATE:
                raise ValidationError(
                    f"VAT rate must be between 0% and {cls.MAX_VAT_RATE_PERCENT}%"
                )
            return v.quantize(Decimal("0.01"))
        return v

    @field_validator('period')
    @classmethod
    def validate_period(cls, v):
        if not v:
            raise ValidationError(ErrorCodes.PERIOD_EMPTY)
        if not re.match(r'\d{4}-\d{2}', v):
            raise ValidationError(ErrorCodes.PERIOD_FORMAT)
        try:
            year, month = map(int, v.split('-'))
            if not (1 <= month <= 12):
                raise ValidationError(ErrorCodes.PERIOD_MONTH_RANGE)
            if not (2000 <= year <= 2100):
                raise ValidationError(ErrorCodes.PERIOD_YEAR_RANGE)
        except ValueError:
            raise ValidationError(ErrorCodes.PERIOD_INVALID)
        return v

    def add_line(self, account_id: str, debit: Decimal, credit: Decimal,
                 description: Optional[str] = None, vat_rate: Optional[Decimal] = None) -> Any:
        if not hasattr(self, 'lines'):
            from domain.gl import JournalLine
            self.lines = []
        line = JournalLine(
            account_id=account_id, debit=debit, credit=credit,
            description=description, vat_rate=vat_rate
        )
        self.lines.append(line)
        self.validate_double_entry()
        return line

    def validate_double_entry(self) -> bool:
        if not hasattr(self, 'lines') or not self.lines:
            raise DoubleEntryError(ErrorCodes.JOURNAL_ENTRY_NO_LINES)
        total_debit = sum(line.debit for line in self.lines)
        total_credit = sum(line.credit for line in self.lines)
        self.tolerance_difference = abs(total_debit - total_credit)
        self.is_valid = self.tolerance_difference <= self.DOUBLE_ENTRY_TOLERANCE
        if not self.is_valid:
            raise DoubleEntryError(
                f"Double-entry violation: difference of {self.tolerance_difference} "
                f"exceeds tolerance of {self.DOUBLE_ENTRY_TOLERANCE} VND"
            )
        return self.is_valid

    def calculate_vat(self) -> Dict[str, Decimal]:
        vat_amounts = {}
        for line in self.lines:
            if line.vat_rate:
                vat_amounts[line.account_id] = line.debit * line.vat_rate
        return vat_amounts

    def format_vietnamese_currency(self, amount: Decimal) -> str:
        if amount is None or amount == Decimal("0"):
            return "0,00 đ"
        if amount.is_nan():
            return "N/A"
        amount_str = str(abs(amount))
        if '.' in amount_str:
            integer_part, decimal_part = amount_str.split('.')
        else:
            integer_part, decimal_part = amount_str, "00"
        integer_part = integer_part[::-1]
        formatted_parts = []
        for i in range(0, len(integer_part), 3):
            formatted_parts.append(integer_part[i:i + 3][::-1])
        formatted_integer = ".".join(reversed(formatted_parts))
        decimal_part = decimal_part.ljust(2, '0')[:2]
        formatted_amount = f"{formatted_integer},{decimal_part}"
        if amount < 0:
            formatted_amount = f"-{formatted_amount}"
        return f"{formatted_amount} đ"

    def format_vietnamese_date(self) -> str:
        month_names_vi = {
            1: "tháng 1", 2: "tháng 2", 3: "tháng 3", 4: "tháng 4",
            5: "tháng 5", 6: "tháng 6", 7: "tháng 7", 8: "tháng 8",
            9: "tháng 9", 10: "tháng 10", 11: "tháng 11", 12: "tháng 12"
        }
        month_name = month_names_vi.get(self.date.month, f"tháng {self.date.month}")
        return f"{self.date.day} {month_name} năm {self.date.year}"

    def is_valid_vas_compliance(self) -> bool:
        try:
            self.validate_double_entry()
            for line in self.lines:
                if line.vat_rate and not Decimal("0.00") <= line.vat_rate <= Decimal("1.00"):
                    raise VASComplianceError(
                        f"VAT rate {line.vat_rate} is not compliant with Vietnamese tax regulations"
                    )
                if line.debit < 0 or line.credit < 0:
                    raise VASComplianceError("Debit and credit amounts cannot be negative")
            return self.is_valid
        except (DoubleEntryError, VASComplianceError, ValidationError):
            raise
        except Exception as e:
            raise VASValidationError(f"Unexpected error during VAS compliance validation: {e}")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"journal_number": "JV001", "date": "2024-01-15",
                 "description": "Mua hàng trả tiền mặt", "period": "2024-01", "is_valid": True},
                {"journal_number": "JV002", "date": "2024-01-16",
                 "description": "Thanh toán tiền hàng", "period": "2024-01", "vat_rate": "0.10"}
            ]
        }
    )


class JournalLine(BaseModel):
    id: Optional[int] = Field(default=None)
    journal_entry_id: int = Field(..., description="Reference to parent journal entry")
    account_id: str = Field(..., min_length=1, max_length=50, description="Account identifier")
    debit: Decimal = Field(default=Decimal("0.00"), description="Debit amount")
    credit: Decimal = Field(default=Decimal("0.00"), description="Credit amount")
    description: Optional[str] = Field(default=None, max_length=500, description="Line description")
    vat_rate: Optional[Decimal] = Field(default=None, description="VAT rate (0.00 to 1.00)")
    side: str = Field(default="debit", description="Side of transaction (debit or credit)")
    line_type: str = Field(default="regular", description="Type of journal line")
    is_taxable: bool = Field(default=False, description="Whether this line is subject to VAT")
    tax_code: Optional[str] = Field(default=None, description="Vietnamese tax code")
    period: str = Field(default_factory=lambda: date.today().strftime("%Y-%m"), description="Accounting period")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    MAX_VAT_RATE: ClassVar[Decimal] = Decimal("1.00")
    MAX_VAT_RATE_PERCENT: ClassVar[float] = 100.00
    JOURNAL_LINE_TOLERANCE: ClassVar[Decimal] = Decimal("0.001")
    VIETNAMESE_CURRENCIES: ClassVar[list] = ["VND", "USD", "EUR", "JPY", "GBP"]

    @field_validator('debit', 'credit')
    @classmethod
    def validate_amount_precision(cls, v):
        if v < 0:
            raise ValidationError(ErrorCodes.DEBIT_CREDIT_NEGATIVE)
        if abs(v) > Decimal("1000000000.00"):
            raise ValidationError(ErrorCodes.AMOUNT_MAX)
        return v.quantize(Decimal("0.01"))

    @field_validator('vat_rate')
    @classmethod
    def validate_vat_rate(cls, v):
        if v is not None:
            if not Decimal("0.00") <= v <= cls.MAX_VAT_RATE:
                raise ValidationError(
                    f"VAT rate must be between 0% and {cls.MAX_VAT_RATE_PERCENT}%"
                )
            return v.quantize(Decimal("0.01"))
        return v

    @field_validator('account_id')
    @classmethod
    def validate_account_id(cls, v):
        if not v.strip():
            raise ValidationError(ErrorCodes.ACCOUNT_ID_EMPTY)
        v_clean = v.strip()
        if v_clean.startswith('0') and len(v_clean) > 1:
            raise ValidationError("Account ID cannot start with 0 after stripping spaces")
        return v_clean

    def validate_debit_credit_tolerance(self) -> bool:
        difference = abs(self.debit - self.credit)
        return difference <= self.JOURNAL_LINE_TOLERANCE

    def calculate_vat_amount(self) -> Decimal:
        if not self.vat_rate:
            return Decimal("0.00")
        return self.debit * self.vat_rate

    def get_vi_currency_symbol(self) -> str:
        return "đ" if self.currency == "VND" else "USD"

    def format_vietnamese_currency(self, amount: Optional[Decimal] = None) -> str:
        if amount is None:
            amount = self.debit if self.debit > 0 else self.credit
        if amount == Decimal("0"):
            return "0,00"
        amount_str = str(amount)
        if '.' in amount_str:
            integer_part, decimal_part = amount_str.split('.')
        else:
            integer_part, decimal_part = amount_str, "00"
        integer_part = integer_part[::-1]
        formatted_parts = []
        for i in range(0, len(integer_part), 3):
            formatted_parts.append(integer_part[i:i + 3][::-1])
        formatted_integer = ".".join(reversed(formatted_parts))
        decimal_part = decimal_part.ljust(2, '0')[:2]
        return f"{formatted_integer},{decimal_part}"

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"account_id": "1111", "debit": "1000.00", "credit": "0.00",
                 "description": "Tiền mặt", "vat_rate": "0.10"},
                {"account_id": "2111", "debit": "0.00", "credit": "1000.00",
                 "description": "Hàng đã mua", "vat_rate": "0.00"}
            ]
        }
    )


class FinancialStatement(BaseModel):
    id: Optional[int] = Field(default=None)
    period: str = Field(..., pattern=r'\d{4}-\d{2}', description="Accounting period (YYYY-MM)")
    statement_type: str = Field(..., description="Statement type: balance_sheet, income_statement, cash_flow")
    assets: Dict[str, Decimal] = Field(default_factory=dict, description="Assets by category")
    liabilities: Dict[str, Decimal] = Field(default_factory=dict, description="Liabilities by category")
    equity: Dict[str, Decimal] = Field(default_factory=dict, description="Equity by category")
    revenue: Dict[str, Decimal] = Field(default_factory=dict, description="Revenue by category")
    expenses: Dict[str, Decimal] = Field(default_factory=dict, description="Expenses by category")
    is_approved: bool = Field(default=False)
    approved_by: Optional[str] = Field(default=None)
    approval_date: Optional[date] = Field(default=None)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by: Optional[str] = Field(default=None)
    remarks: Optional[str] = Field(default=None, max_length=1000)

    VIETNAMESE_CURRENCY: ClassVar[str] = "VND"
    VIETNAMESE_LOCALE: ClassVar[str] = "vi_VN"
    STATEMENT_TYPES: ClassVar[list] = ["balance_sheet", "income_statement", "cash_flow"]

    @field_validator('period')
    @classmethod
    def validate_period(cls, v):
        if not v:
            raise ValidationError(ErrorCodes.PERIOD_FS_EMPTY)
        if not re.match(r'\d{4}-\d{2}', v):
            raise ValidationError(ErrorCodes.PERIOD_FS_FORMAT)
        try:
            year, month = map(int, v.split('-'))
            if not (1 <= month <= 12):
                raise ValidationError(ErrorCodes.PERIOD_FS_MONTH)
        except ValueError:
            raise ValidationError(ErrorCodes.PERIOD_FS_INVALID)
        return v

    @field_validator('statement_type')
    @classmethod
    def validate_statement_type(cls, v):
        if v not in cls.STATEMENT_TYPES:
            raise ValidationError(ErrorCodes.STATEMENT_TYPE_INVALID)
        return v

    def calculate_balance_sheet_totals(self) -> Dict[str, Decimal]:
        assets_total = sum(self.assets.values())
        liabilities_total = sum(self.liabilities.values())
        equity_total = sum(self.equity.values())
        return {
            "assets_total": assets_total,
            "liabilities_total": liabilities_total,
            "equity_total": equity_total,
            "balance": equity_total - liabilities_total,
        }

    def calculate_income_statement_totals(self) -> Dict[str, Decimal]:
        revenue_total = sum(self.revenue.values())
        expenses_total = sum(self.expenses.values())
        net_income = revenue_total - expenses_total
        return {
            "revenue_total": revenue_total,
            "expenses_total": expenses_total,
            "net_income": net_income,
        }

    def format_vietnamese_amount(self, amount: Decimal) -> str:
        if amount == Decimal("0"):
            return "0,00 VND"
        amount_str = str(abs(amount))
        if '.' in amount_str:
            integer_part, decimal_part = amount_str.split('.')
        else:
            integer_part, decimal_part = amount_str, "00"
        integer_part = integer_part[::-1]
        formatted_parts = []
        for i in range(0, len(integer_part), 3):
            formatted_parts.append(integer_part[i:i + 3][::-1])
        formatted_integer = ".".join(reversed(formatted_parts))
        decimal_part = decimal_part.ljust(2, '0')[:2]
        formatted_amount = f"{formatted_integer},{decimal_part}"
        currency_symbol = "VND" if self.period.endswith("-12") or self.get_current_month() == 12 else "đ"
        if amount < 0:
            formatted_amount = f"-{formatted_amount}"
        return f"{formatted_amount} {currency_symbol}"

    def generate_monthly_summary(self, period: str) -> Dict[str, Any]:
        summary = {
            "period": period,
            "statement_type": self.statement_type,
            "assets": {k: self.format_vietnamese_amount(v) for k, v in self.assets.items()},
            "liabilities": {k: self.format_vietnamese_amount(v) for k, v in self.liabilities.items()},
            "equity": {k: self.format_vietnamese_amount(v) for k, v in self.equity.items()},
            "revenue": {k: self.format_vietnamese_amount(v) for k, v in self.revenue.items()},
            "expenses": {k: self.format_vietnamese_amount(v) for k, v in self.expenses.items()},
            "totals": self.calculate_balance_sheet_totals() if self.statement_type == "balance_sheet"
                     else self.calculate_income_statement_totals(),
            "formatted_totals": self.calculate_balance_sheet_totals() if self.statement_type == "balance_sheet"
                                else self.calculate_income_statement_totals(),
        }
        return summary

    @classmethod
    def generate_monthly(cls, period: str, ledger_accounts: Dict[str, Any]) -> 'FinancialStatement':
        fs = cls(period=period, statement_type="balance_sheet")
        assets_total = Decimal("0.00")
        liabilities_total = Decimal("0.00")
        equity_total = Decimal("0.00")
        for account_id, ledger in ledger_accounts.items():
            balance = ledger.get_balance(period)
            if account_id.startswith('1'):
                fs.assets["Current Assets"] = fs.assets.get("Current Assets", Decimal("0.00")) + balance
                assets_total += balance
            elif account_id.startswith('2'):
                fs.liabilities["Current Liabilities"] = fs.liabilities.get("Current Liabilities", Decimal("0.00")) + balance
                liabilities_total += balance
            elif account_id.startswith('3'):
                fs.equity["Owner's Equity"] = fs.equity.get("Owner's Equity", Decimal("0.00")) + balance
                equity_total += balance
        return fs

    def get_current_month(self) -> int:
        try:
            return int(self.period.split('-')[1])
        except (ValueError, IndexError):
            return date.today().month

    def is_vas_compliant(self) -> bool:
        try:
            if not self.period:
                raise VASValidationError(ErrorCodes.FS_PERIOD_REQUIRED)
            if self.statement_type not in self.STATEMENT_TYPES:
                raise VASValidationError(f"Statement type {self.statement_type} is not valid per VAS")
            if self.statement_type == "balance_sheet":
                totals = self.calculate_balance_sheet_totals()
                if totals["assets_total"] < 0:
                    raise VASValidationError(ErrorCodes.FS_ASSET_NEGATIVE)
            return True
        except (VASValidationError, ValidationError):
            raise
        except Exception as e:
            raise VASValidationError(f"Unexpected error during VAS compliance validation: {e}")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"period": "2024-01", "statement_type": "balance_sheet",
                 "assets": {"cash": "10000.00", "accounts_receivable": "5000.00"},
                 "liabilities": {"accounts_payable": "3000.00"},
                 "equity": {"capital": "12000.00"}, "revenue": {}, "expenses": {}},
                {"period": "2024-02", "statement_type": "income_statement",
                 "assets": {}, "liabilities": {}, "equity": {},
                 "revenue": {"sales": "50000.00"}, "expenses": {"cost_of_sales": "30000.00"}}
            ]
        },
        frozen=True,
    )
    __init__ = None
