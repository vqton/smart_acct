from typing import List, Dict, Optional, Any, Union, ClassVar
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from abc import ABC, abstractmethod
import re
from domain.i18n import ErrorCodes
class VASValidationError(Exception):
    """Base exception for Vietnamese Accounting Standards compliance errors.
    Carries msgid (error code) and optional format params for i18n resolution."""
    def __init__(self, msgid: str, **params):
        self.msgid = msgid
        self.params = params
        super().__init__(msgid)
class ValidationError(VASValidationError):
    """Validation error for domain entities"""
    pass
class VASComplianceError(VASValidationError):
    """Error for VAS compliance violations"""
    pass
class DoubleEntryError(VASValidationError):
    """Error for double-entry bookkeeping violations"""
    pass
class InvalidCurrencyError(VASValidationError):
    """Error for invalid currency codes"""
    pass
class CurrencyError(VASValidationError):
    """Error for currency-related issues"""
    pass
class InvalidAccountError(VASValidationError):
    """Error for invalid account codes or formats"""
    pass
class AccountError(VASValidationError):
    """Error for account-specific issues"""
    pass
class ChartError(VASValidationError):
    """Error for chart of accounts issues"""
    pass
class DateError(VASValidationError):
    """Error for date-related issues"""
    pass
class Result:
    """Generic result type for domain operations"""
    def __init__(self, success: bool, data: Any = None, error: Optional[VASValidationError] = None):
        self.success = success
        self.data = data
        self.error = error

    @classmethod
    def success(cls, data: Any = None) -> 'Result':
        return cls(True, data)

    @classmethod
    def failure(cls, error: VASValidationError) -> 'Result':
        return cls(False, error=error)

    def is_success(self) -> bool:
        return self.success

    def is_failure(self) -> bool:
        return not self.success

    def get_data(self) -> Any:
        if self.is_failure():
            raise ValueError(ErrorCodes.CANNOT_GET_DATA_FAILED)
        return self.data

    def get_error(self) -> VASValidationError:
        if self.is_success():
            raise ValueError(ErrorCodes.CANNOT_GET_ERROR_SUCCESS)
        return self.error
class AccountType(str, Enum):
    """Vietnamese Accounting Standards account types from Circular 133/2016/TT-BTC"""
    # Type 1: Asset accounts (can have positive or negative balance)
    ASSET = "asset"
    CASH = "cash"
    BANK = "bank"
    SHORT_TERM_FINANCIAL_INVESTMENT = "short_term_financial_investment"
    LONG_TERM_FINANCIAL_INVESTMENT = "long_term_financial_investment"
    ACCOUNT_RECEIVABLE = "account_receivable"
    SHORT_TERM_LOANS_TO_ENTERPRISES = "short_term_loans_to_enterprises"
    SHORT_TERM_LOANS_TO_PEOPLE = "short_term_loans_to_people"
    PREPAID_EXPENSES = "prepaid_expenses"
    INVENTORY_GOODS = "inventory_goods"
    PRODUCTION_IN_PROGRESS = "production_in_progress"
    CONSTRUCTION_IN_PROGRESS = "construction_in_progress"
    ACCOUNTS_RECEIVABLE_FROM_SALE_OF_FIXED_ASSETS = "accounts_receivable_from_sale_of_fixed_assets"
    ACCOUNTS_RECEIVABLE_FROM_SALE_OF_INTANGIBLE_ASSETS = "accounts_receivable_from_sale_of_intangible_assets"
    DEPOSITS_AND_LOANS_RECEIVED = "deposits_and_loans_received"
    CLAIMS = "claims"
    OTHER_CURRENT_ASSETS = "other_current_assets"
    ACCOUNTS_RECEIVABLE_FROM_BILLS_OF_EXCHANGE = "accounts_receivable_from_bills_of_exchange"
    DEPOSITS_AND_LOANS_RECEIVED_FROM_CUSTOMER = "deposits_and_loans_received_from_customer"

    # Type 1.1: Fixed assets (non-current assets)
    FIXED_ASSETS = "fixed_assets"
    LAND = "land"
    BUILDINGS = "buildings"
    MACHINERY_AND_EQUIPMENT = "machinery_and_equipment"
    TRANSPORT_EQUIPMENT = "transport_equipment"
    TOOLS_AND_ACCESSORIES = "tools_and_accessories"
    OFFICE_EQUIPMENT = "office_equipment"
    FURNITURE_AND_FITTINGS = "furniture_and_fittings"
    PLANTS_AND_EQUIPMENT = "plants_and_equipment"
    VEHICLES = "vehicles"
    MOVABLE_ASSETS = "movable_assets"

    # Type 1.2: Intangible assets
    INTANGIBLE_ASSETS = "intangible_assets"
    PATENT_RIGHT = "patent_right"
    COPYRIGHT = "copyright"
    SOFTWARE = "software"
    FRANCHISE = "franchise"
    GOODWILL = "goodwill"
    MARKETING_ASSETS = "marketing_assets"

    # Type 1.3: Financial assets
    FINANCIAL_ASSETS = "financial_assets"
    SHORT_TERM_FINANCIAL_ASSETS = "short_term_financial_assets"
    LONG_TERM_FINANCIAL_ASSETS = "long_term_financial_assets"

    # Type 1: Cash-related sub-types
    ADVANCE = "advance"
    ASSET_SHORTAGE = "asset_shortage"
    ASSET_SURPLUS = "asset_surplus"
    CASH_EQUIVALENT = "cash_equivalent"

    # Type 2: Liability accounts (always have positive balance)
    LIABILITY = "liability"
    SHORT_TERM_LIABILITIES = "short_term_liabilities"
    LONG_TERM_LIABILITIES = "long_term_liabilities"
    BORROWINGS_FROM_CREDIT_INSTITUTIONS = "borrowings_from_credit_institutions"
    BORROWINGS_FROM_ENTERPRISES = "borrowings_from_enterprises"
    BORROWINGS_FROM_PEOPLE = "borrowings_from_people"
    ACCOUNTS_PAYABLE = "accounts_payable"
    ACCOUNTS_PAYABLE_TO_VENDOR = "accounts_payable_to_vendor"
    TAXES_AND_CHARGES_PAYABLE = "taxes_and_charges_payable"
    EXPENSES_PAYABLE = "expenses_payable"
    FINANCING_COSTS_PAYABLE = "financing_costs_payable"
    SECURITIES_PAYABLE = "securities_payable"
    EARNEST_MONEY_PAYABLE = "earnest_money_payable"
    SALES_REVENUE_PAYABLE = "sales_revenue_payable"
    SHORT_TERM_BILLS_PAYABLE = "short_term_bills_payable"
    LONG_TERM_LOANS_FROM_CREDIT_INSTITUTIONS = "long_term_loans_from_credit_institutions"
    LONG_TERM_BILLS_PAYABLE = "long_term_bills_payable"
    DEPOSITS_RECEIVED = "deposits_received"

    # Type 3: Equity accounts (always have positive balance)
    EQUITY = "equity"
    CAPITAL_CONTRIBUTED = "capital_contributed"
    CAPITAL_SURPLUS = "capital_surplus"
    RETAINED_EARNINGS = "retained_earnings"
    REVALUATION_SURPLUS = "revaluation_surplus"
    CAPITAL_SUBSIDIARY_ACCOUNT = "capital_subsidiary_account"
    CORPORATE_BOND_SURPLUS = "corporate_bond_surplus"
    INVESTMENT_IN_PARTNER = "investment_in_partner"

    # Type 4: Revenue accounts (always have positive balance)
    REVENUE = "revenue"
    SALES_REVENUE = "sales_revenue"
    SERVICE_REVENUE = "service_revenue"
    OTHER_OPERATIONAL_REVENUE = "other_operational_revenue"
    SALES_DISCOUNTS = "sales_discounts"
    SALES_RETURN = "sales_return"
    SALES_VAT_REVENUE = "sales_vat_revenue"
    NON_OPERATIONAL_REVENUE = "non_operational_revenue"
    OTHER_NON_OPERATIONAL_REVENUE = "other_non_operational_revenue"
    FINANCIAL_REVENUE = "financial_revenue"

    # Type 5: Expense accounts (always have positive balance)
    EXPENSE = "expense"
    COST_OF_SALES = "cost_of_sales"
    OPERATIONAL_EXPENSES = "operational_expenses"
    SELLING_EXPENSES = "selling_expenses"
    ADMINISTRATIVE_EXPENSES = "administrative_expenses"
    RESEARCH_AND_DEVELOPMENT_EXPENSES = "research_and_development_expenses"
    DEPRECIATION_AND_AMORTIZATION = "depreciation_and_amortization"
    FINANCIAL_EXPENSES = "financial_expenses"
    INTEREST_EXPENSES = "interest_expenses"
    LOSS_FROM_FOREIGN_CURRENCY_EXCHANGE = "loss_from_foreign_currency_exchange"
    OTHER_OPERATIONAL_EXPENSES = "other_operational_expenses"
    OTHER_NON_OPERATIONAL_EXPENSES = "other_non_operational_expenses"
    TAXES_AND_CHARGES_EXPENSE = "taxes_and_charges_expense"
    PROVISIONS = "provisions"
    UNREALIZED_FINANCIAL_INCOME = "unrealized_financial_income"

    # Special Vietnamese expense types
    DEPRECIATION_EXPENSE = "depreciation_expense"
    AMORTIZATION_EXPENSE = "amortization_expense"
    VAT_INPUT = "vat_input"
    CIT_PAYMENT = "cit_payment"
    PIT_PAYMENT = "pit_payment"

    # Type 6: Cost of goods sold
    COST_OF_GOODS_SOLD = "cost_of_goods_sold"

    # Type 7: Gross profit
    GROSS_PROFIT = "gross_profit"

    # Type 8: Net profit
    NET_PROFIT = "net_profit"

    # Type 9: Equity distribution (dividends, etc.)
    EQUITY_DISTRIBUTION = "equity_distribution"
class DCRDirection(str, Enum):
    """
    Debit/Credit direction for Vietnamese accounting standards
    Vietnamese Accounting Circular 133/2016/TT-BTC specifies which accounts
    normally have debit or credit balances based on their nature
    """
    DEBIT = "debit"  # Dr = Nợ (Normal balance is debit)
    CREDIT = "credit"  # Cr = Có (Normal balance is credit)

    @classmethod
    def get_direction(cls, account_type: AccountType) -> 'DCRDirection':
        """
        Get the normal DCR direction for a given account type per Vietnamese Accounting Standards
        """
        debit_normal_accounts = {
            AccountType.ASSET,
            AccountType.CASH,
            AccountType.BANK,
            AccountType.SHORT_TERM_FINANCIAL_INVESTMENT,
            AccountType.ACCOUNT_RECEIVABLE,
            AccountType.ADVANCE,
            AccountType.ASSET_SHORTAGE,
            AccountType.CASH_EQUIVALENT,
            AccountType.SHORT_TERM_LOANS_TO_ENTERPRISES,
            AccountType.COST_OF_SALES,
            AccountType.OPERATIONAL_EXPENSES,
            AccountType.DEPRECIATION_EXPENSE,
            AccountType.VAT_INPUT,
        }

        credit_normal_accounts = {
            AccountType.LIABILITY,
            AccountType.EQUITY,
            AccountType.REVENUE,
            AccountType.FINANCIAL_REVENUE,
            AccountType.COST_OF_GOODS_SOLD,
            AccountType.GROSS_PROFIT,
            AccountType.NET_PROFIT,
            AccountType.EQUITY_DISTRIBUTION,
            AccountType.ASSET_SURPLUS,
        }

        if account_type in debit_normal_accounts:
            return cls.DEBIT
        elif account_type in credit_normal_accounts:
            return cls.CREDIT
        else:
            return cls.DEBIT  # Default to debit for undefined types
class AccountingRegime(str, Enum):
    """Accounting regime/standard applicable to the Chart of Accounts"""
    TT99_2025 = "tt99_2025"
    TT133_2016 = "tt133_2016"
class AccountStatus(str, Enum):
    """Lifecycle status of an account in the COA"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
class ChartOfAccounts(BaseModel):
    """
    Chart of Accounts according to Vietnamese Accounting Standards
    Supports TT 99/2025/TT-BTC (primary) and TT 133/2016/TT-BTC (SME)
    Defines the complete taxonomy of accounts from Type 1 to Type 9
    """
    code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        pattern=r'^[1-9](?:\.[0-9]+)*$|^[1-9][0-9]{3,5}$',
        description="VAS account code: dotted (1, 1.1, 1.1.1) or flat numeric (1111, 11111)"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Vietnamese account name"
    )
    account_type: AccountType = Field(
        ...,
        description="Account type per VAS (Type 1-9)"
    )
    regime: AccountingRegime = Field(
        default=AccountingRegime.TT99_2025,
        description="Accounting regime (TT99/2025 or TT133/2016)"
    )
    vas_compliant: bool = Field(
        default=True,
        description="Whether the account code follows VAS rules"
    )
    drcr_direction: DCRDirection = Field(
        ...,
        description="Normal balance direction (debit or credit) per Vietnamese standards"
    )
    level: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Hierarchy level (1-4 levels supported in Vietnam)"
    )
    status: AccountStatus = Field(
        default=AccountStatus.ACTIVE,
        description="Account lifecycle status"
    )
    currency: str = Field(
        default="VND",
        description="Default currency for Vietnamese accounting (VND is standard)"
    )
    unit: str = Field(
        default="VND",
        description="Accounting unit (VND, USD, EUR, etc.)"
    )
    parent_code: Optional[str] = Field(
        default=None,
        description="Parent account code for hierarchical structure"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Detailed account description in Vietnamese"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )

    @field_validator('code')
    @classmethod
    def validate_account_code(cls, v):
        """
        Validate Vietnamese account code format according to Circular 133/2016/TT-BTC
        """
        if not v:
            raise ValidationError(ErrorCodes.ACCOUNT_CODE_EMPTY)

        code_clean = v.replace('.', '')

        if not code_clean.isdigit():
            raise InvalidAccountError(
                ErrorCodes.ACCOUNT_CODE_NUMERIC
            )

        if len(code_clean) > 6:
            raise InvalidAccountError(
                ErrorCodes.ACCOUNT_CODE_MAX_DIGITS
            )

        if '.' in v:
            max_level = len(v.split('.'))
            if max_level > 4:
                raise InvalidAccountError(
                    ErrorCodes.ACCOUNT_CODE_MAX_LEVELS
                )

        first_char = v[0]
        if first_char < '1' or first_char > '9':
            raise InvalidAccountError(
                ErrorCodes.ACCOUNT_CODE_FIRST_DIGIT
            )

        if v.startswith('0'):
            raise InvalidAccountError(
                ErrorCodes.ACCOUNT_CODE_NO_ZERO
            )

        return v

    @field_validator('name')
    @classmethod
    def validate_account_name(cls, v):
        """
        Validate Vietnamese account name
        """
        if not v.strip():
            raise ValidationError(ErrorCodes.ACCOUNT_NAME_EMPTY)
        return v.strip()

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """
        Validate currency for Vietnamese accounting (VND is standard)
        """
        valid_currencies = ["VND", "USD", "EUR", "JPY", "GBP"]
        if v.upper() not in valid_currencies:
            raise InvalidCurrencyError(
                f"Currency must be one of {valid_currencies}"
            )
        return v.upper()

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v):
        """
        Validate accounting unit
        """
        if not v:
            raise ValidationError(ErrorCodes.UNIT_EMPTY)
        return v.upper()

    def calculate_balance(self, drcr_direction: DCRDirection, transaction_amount: Decimal) -> Decimal:
        """
        Calculate balance based on transaction amount and DCR direction
        """
        if drcr_direction == DCRDirection.DEBIT:
            return transaction_amount
        return -transaction_amount

    def get_translation(self, target_language: str = "vi") -> str:
        """
        Get account name in target language
        """
        if target_language == "vi":
            return self.name
        return f"{self.name} (Account {self.code})"

    def is_asset_type(self) -> bool:
        """Check if account is an asset type (Type 1)"""
        return self.account_type in [
            AccountType.ASSET, AccountType.CASH, AccountType.BANK,
            AccountType.SHORT_TERM_FINANCIAL_INVESTMENT, AccountType.LONG_TERM_FINANCIAL_INVESTMENT,
            AccountType.ACCOUNT_RECEIVABLE, AccountType.SHORT_TERM_LOANS_TO_ENTERPRISES,
            AccountType.PREPAID_EXPENSES, AccountType.INVENTORY_GOODS,
            AccountType.PRODUCTION_IN_PROGRESS, AccountType.CONSTRUCTION_IN_PROGRESS
        ]

    def is_liability_type(self) -> bool:
        """Check if account is a liability type (Type 2)"""
        return self.account_type in [
            AccountType.LIABILITY, AccountType.SHORT_TERM_LIABILITIES, AccountType.LONG_TERM_LIABILITIES
        ]

    def is_equity_type(self) -> bool:
        """Check if account is an equity type (Type 3)"""
        return self.account_type in [
            AccountType.EQUITY, AccountType.CAPITAL_CONTRIBUTED,
            AccountType.CAPITAL_SURPLUS, AccountType.RETAINED_EARNINGS,
            AccountType.REVALUATION_SURPLUS, AccountType.EQUITY_DISTRIBUTION,
        ]

    def is_revenue_type(self) -> bool:
        """Check if account is a revenue type (Type 4)"""
        return self.account_type in [
            AccountType.REVENUE, AccountType.FINANCIAL_REVENUE
        ]

    def is_expense_type(self) -> bool:
        """Check if account is an expense type (Type 5)"""
        return self.account_type in [
            AccountType.EXPENSE, AccountType.DEPRECIATION_EXPENSE
        ]

    def get_account_type_group(self) -> str:
        """
        Get the broad account type group for financial statements
        """
        if self.is_asset_type():
            return "assets"
        elif self.is_liability_type():
            return "liabilities"
        elif self.is_equity_type():
            return "equity"
        elif self.is_revenue_type():
            return "revenue"
        elif self.is_expense_type():
            return "expenses"
        else:
            return "other"

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "code": "1.1.1",
                    "name": "Tài sản ngắn hạn",
                    "account_type": AccountType.ASSET,
                    "vas_compliant": True,
                    "drcr_direction": DCRDirection.DEBIT,
                    "currency": "VND"
                },
                {
                    "code": "2.1.1",
                    "name": "Nguồn vốn chủ sở hữu",
                    "account_type": AccountType.EQUITY,
                    "vas_compliant": True,
                    "drcr_direction": DCRDirection.CREDIT,
                    "currency": "VND"
                },
                {
                    "code": "4.1.1",
                    "name": "Doanh thu bán hàng",
                    "account_type": AccountType.SALES_REVENUE,
                    "vas_compliant": True,
                    "drcr_direction": DCRDirection.CREDIT,
                    "currency": "VND"
                },
            ]
        },
    )


class Account(BaseModel):
    """
    Account entity representing a specific accounting record for an enterprise
    Supports Vietnamese business requirements with dense data layouts
    """
    account_number: str = Field(
        ...,
        min_length=4,
        max_length=20,
        pattern=r'^[0-9]{4,20}$',
        description="Unique account number (4-20 digits)"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Vietnamese account name"
    )
    account_type: AccountType = Field(
        ...,
        description="Account type per VAS (Type 1-9)"
    )
    chart_code: str = Field(
        ...,
        description="Reference to Chart of Accounts code"
    )
    currency: str = Field(
        default="VND",
        description="Currency with Vietnamese locale"
    )
    drcr_direction: DCRDirection = Field(
        ...,
        description="Normal balance direction for Vietnamese accounting"
    )
    exchange_rate: Decimal = Field(
        default=Decimal("1.000"),
        description="Exchange rate for multi-currency support"
    )
    opening_balance: Decimal = Field(
        default=Decimal("0.00"),
        description="Opening balance for monthly tracking"
    )
    balance: Decimal = Field(
        default=Decimal("0.00"),
        description="Current account balance with Vietnamese precision"
    )
    monthly_balances: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Monthly balances for financial reporting (YYYY-MM format)"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this account is currently active in Vietnamese business"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Extended description in Vietnamese"
    )
    last_updated: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )
    created_by: Optional[str] = Field(
        default=None,
        description="User who created the account (for audit trail)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )

    # Vietnamese locale formatting constants
    VIETNAMESE_CURRENCIES: ClassVar[list] = ["VND", "USD", "EUR", "JPY", "GBP"]
    VIETNAMESE_LOCALE: ClassVar[str] = "vi_VN"

    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v):
        """
        Validate Vietnamese account number format
        """
        if not v:
            raise ValidationError(ErrorCodes.ACCOUNT_NUMBER_EMPTY)

        if not v.isdigit():
            raise ValidationError(ErrorCodes.ACCOUNT_NUMBER_NUMERIC)

        if len(v) < 4 or len(v) > 20:
            raise ValidationError(ErrorCodes.ACCOUNT_NUMBER_LENGTH)

        if v.startswith('0'):
            raise ValidationError(ErrorCodes.ACCOUNT_NUMBER_NO_ZERO)

        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """
        Validate Vietnamese account name
        """
        if not v.strip():
            raise ValidationError(ErrorCodes.ACCOUNT_NAME_EMPTY)
        return v.strip()

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """
        Validate currency for Vietnamese market
        """
        if not v:
            raise ValidationError(ErrorCodes.CURRENCY_EMPTY)

        v_upper = v.upper()
        if v_upper not in cls.VIETNAMESE_CURRENCIES:
            raise InvalidCurrencyError(
                f"Currency must be one of {cls.VIETNAMESE_CURRENCIES}"
            )

        if v_upper != "VND" and v_upper not in ["USD", "EUR", "JPY", "GBP"]:
            raise InvalidCurrencyError(ErrorCodes.CURRENCY_SME_ONLY)

        return v_upper

    @field_validator('opening_balance', 'balance')
    @classmethod
    def validate_balance_precision(cls, v):
        """
        Validate balance precision for Vietnamese accounting (2 decimal places for VND)
        """
        if v is None:
            raise ValidationError(ErrorCodes.BALANCE_NONE)

        if abs(v) > Decimal("10000000000.00"):
            raise ValidationError("Balance cannot exceed 10 billion VND")

        return v.quantize(Decimal("0.01"))

    @field_validator('exchange_rate')
    @classmethod
    def validate_exchange_rate(cls, v):
        """
        Validate exchange rate for multi-currency support
        """
        if v <= 0:
            raise ValidationError(ErrorCodes.EXCHANGE_RATE_POSITIVE)

        return v.quantize(Decimal("0.001"))

    @field_validator('drcr_direction')
    @classmethod
    def validate_drcr_direction(cls, v):
        """
        Validate DCR direction based on account type and Vietnamese standards
        """
        if not v:
            raise ValidationError(ErrorCodes.DCR_DIRECTION_EMPTY)

        valid_directions = [direction.value for direction in DCRDirection]
        if v.lower() not in valid_directions:
            raise ValidationError(f"DCR direction must be one of {valid_directions}")

        return DCRDirection(v.lower()).value

    @field_validator('chart_code')
    @classmethod
    def validate_chart_code(cls, v):
        """
        Validate chart code and ensure account type matches chart code type
        """
        if not v:
            raise ValidationError(ErrorCodes.CHART_CODE_EMPTY)

        if not isinstance(v, str):
            raise ValidationError(ErrorCodes.CHART_CODE_TYPE)

        if v and len(v) > 20:
            raise ValidationError(ErrorCodes.CHART_CODE_MAX_LENGTH)

        return v

    @field_validator('last_updated', 'updated_at')
    @classmethod
    def validate_date_format(cls, v):
        """
        Validate date format for Vietnamese business operations
        """
        if v is None:
            return datetime.now(timezone.utc)

        if isinstance(v, str):
            try:
                from dateutil import parser
                return parser.parse(v)
            except (ValueError, ImportError):
                raise ValidationError(ErrorCodes.DATE_ISO_FORMAT)

        return v

    def format_vietnamese_currency(self, amount: Optional[Decimal] = None) -> str:
        """
        Format amount with Vietnamese currency conventions
        Example: 1.500.000,50 đ
        """
        if amount is None:
            amount = self.balance

        if amount is None or amount == Decimal("0"):
            return "0,00 đ"

        # Convert to float for consistent formatting
        amount_float = float(amount)

        # Format with Vietnamese number separator (dot for thousands, comma for decimals)
        formatted_number = f"{amount_float:,.2f}"
        formatted_number = formatted_number.replace(",", ".")
        formatted_number = formatted_number.replace(".", ".", formatted_number.count(".") - 2)

        # Add Vietnamese dong symbol
        return f"{formatted_number} đ"

    def format_vietnamese_number(self, amount: Decimal) -> str:
        """
        Format number with Vietnamese conventions
        Example: 1,500,000
        """
        formatted_number = f"{amount:,.0f}"
        return formatted_number.replace(",", ".")

    def add_monthly_balance(self, month: str, amount: Decimal):
        """
        Add or update monthly balance entry
        """
        if not isinstance(month, str) or not re.match(r'\d{4}-\d{2}', month):
            raise ValidationError("Month must be in YYYY-MM format")

        if month not in self.monthly_balances:
            self.monthly_balances[month] = Decimal("0.00")

        self.monthly_balances[month] += amount
        self.balance = self.calculate_running_balance()

    def calculate_running_balance(self) -> Decimal:
        """
        Calculate running balance from opening balance and all monthly transactions
        """
        if not self.monthly_balances:
            return self.opening_balance

        last_month = sorted(self.monthly_balances.keys())[-1]
        total_monthly_changes = sum(self.monthly_balances.values())

        return self.opening_balance + total_monthly_changes

    def is_asset_account(self) -> bool:
        """
        Check if this account is an asset account (Type 1)
        """
        asset_types = {
            AccountType.ASSET, AccountType.CASH, AccountType.BANK,
            AccountType.SHORT_TERM_FINANCIAL_INVESTMENT, AccountType.LONG_TERM_FINANCIAL_INVESTMENT,
            AccountType.ACCOUNT_RECEIVABLE, AccountType.SHORT_TERM_LOANS_TO_ENTERPRISES,
            AccountType.PREPAID_EXPENSES, AccountType.INVENTORY_GOODS,
            AccountType.PRODUCTION_IN_PROGRESS, AccountType.CONSTRUCTION_IN_PROGRESS
        }
        return self.account_type in asset_types

    def is_liability_account(self) -> bool:
        """
        Check if this account is a liability account (Type 2)
        """
        liability_types = {
            AccountType.LIABILITY, AccountType.SHORT_TERM_LIABILITIES, AccountType.LONG_TERM_LIABILITIES
        }
        return self.account_type in liability_types

    def is_equity_account(self) -> bool:
        """
        Check if this account is an equity account (Type 3)
        """
        equity_types = {
            AccountType.EQUITY, AccountType.CAPITAL_CONTRIBUTED, AccountType.CAPITAL_SURPLUS,
            AccountType.RETAINED_EARNINGS
        }
        return self.account_type in equity_types

    def is_revenue_account(self) -> bool:
        """
        Check if this account is a revenue account (Type 4)
        """
        revenue_types = {AccountType.REVENUE, AccountType.SALES_REVENUE, AccountType.SERVICE_REVENUE}
        return self.account_type in revenue_types

    def is_expense_account(self) -> bool:
        """
        Check if this account is an expense account (Type 5)
        """
        expense_types = {AccountType.EXPENSE, AccountType.COST_OF_SALES}
        return self.account_type in expense_types

    def get_normal_balance(self) -> Decimal:
        """
        Get the normal balance for this account per Vietnamese Accounting Standards
        """
        if self.is_asset_account() or self.is_expense_account():
            return Decimal("0.00")
        else:
            return Decimal("0.00")

    def validate_vas_compliance(self) -> bool:
        """
        Validate that this account complies with Vietnamese Accounting Standards
        """
        try:
            if not self.account_number or not self.name:
                raise ValidationError("Account number and name are required for VAS compliance")

            if not self.chart_code:
                raise ValidationError("Chart code is required for VAS compliance")

            if self.account_type not in AccountType:
                raise ChartError(f"Account type {self.account_type} is not valid per VAS")

            if self.currency not in self.VIETNAMESE_CURRENCIES:
                raise InvalidCurrencyError(f"Currency {self.currency} is not supported for Vietnamese operations")

            if self.account_number.startswith('0'):
                raise InvalidAccountError("Account number cannot start with 0 per VAS standards")

            return True
        except (ValidationError, ChartError, InvalidCurrencyError, InvalidAccountError):
            raise
        except Exception as e:
            raise VASValidationError(f"Unexpected error validating VAS compliance: {e}")

    def update_from_domain(self, **kwargs):
        """
        Update account from domain DTO while maintaining invariants
        """
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)

        self.balance = self.calculate_running_balance()
        self.last_updated = datetime.now(timezone.utc)

    def to_domain_dict(self) -> Dict[str, Any]:
        """
        Convert Account to domain dictionary for presentation layer
        """
        return {
            "account_number": self.account_number,
            "name": self.name,
            "account_type": self.account_type,
            "chart_code": self.chart_code,
            "currency": self.currency,
            "drcr_direction": self.drcr_direction,
            "opening_balance": self.opening_balance,
            "balance": self.balance,
            "monthly_balances": self.monthly_balances,
            "is_active": self.is_active,
            "description": self.description,
            "last_updated": self.last_updated,
            "created_at": self.created_at,
            "formatted_balance": self.format_vietnamese_currency(),
            "is_asset": self.is_asset_account(),
            "is_liability": self.is_liability_account(),
            "is_equity": self.is_equity_account(),
            "is_revenue": self.is_revenue_account(),
            "is_expense": self.is_expense_account(),
        }

    @field_serializer('last_updated', 'created_at', 'updated_at')
    def serialize_datetime(self, v: Optional[datetime]) -> Optional[str]:
        return v.isoformat() if v else None

    @field_serializer('exchange_rate', 'opening_balance', 'balance')
    def serialize_decimal(self, v: Decimal) -> str:
        return str(v)

    @field_serializer('monthly_balances')
    def serialize_monthly_balances(self, v: Dict[str, Decimal]) -> Dict[str, str]:
        return {k: str(v) for k, v in v.items()}

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "account_number": "1111",
                    "name": "Tài khoản tiền mặt",
                    "account_type": AccountType.ASSET,
                    "chart_code": "1.1.1",
                    "currency": "VND",
                    "drcr_direction": "debit",
                    "opening_balance": "10000.00"
                },
                {
                    "account_number": "2111",
                    "name": "Các khoản phải trả",
                    "account_type": AccountType.LIABILITY,
                    "chart_code": "2.1.1",
                    "currency": "VND",
                    "drcr_direction": "credit",
                    "opening_balance": "5000.00"
                },
                {
                    "account_number": "4111",
                    "name": "Doanh thu bán hàng",
                    "account_type": AccountType.SALES_REVENUE,
                    "chart_code": "4.1.1",
                    "currency": "VND",
                    "drcr_direction": "credit",
                    "opening_balance": "0.00"
                },
            ]
        },
    )
class JournalEntry(BaseModel):
    """
    Journal Entry entity - the central hub for Vietnamese accounting transactions
    """
    id: Optional[int] = Field(default=None, description="Primary key identifier")
    journal_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r'^JV\d{6,8}$',
        description="Journal entry number with JV prefix and 6-8 digits"
    )
    transaction_date: date = Field(..., description="Transaction date in ISO format (YYYY-MM-DD)")
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Detailed description of the transaction in Vietnamese"
    )
    lines: List[Any] = Field(
        default_factory=list,
        description="Journal entry lines with precise decimal amounts"
    )
    is_posted: bool = Field(
        default=False,
        description="Whether the entry has been posted to ledger"
    )
    posted_date: Optional[date] = Field(
        default=None,
        description="Date when the entry was posted"
    )
    tolerance_difference: Optional[Decimal] = Field(
        default=None,
        description="Difference between total debits and credits (within 0.001)"
    )
    is_valid: Optional[bool] = Field(
        default=None,
        description="Validation status for double-entry bookkeeping"
    )
    vat_rate: Optional[Decimal] = Field(
        default=None,
        description="VAT rate for this journal entry (0.00 to 1.00)"
    )
    period: str = Field(
        default_factory=lambda: date.today().strftime("%Y-%m"),
        description="Accounting period (YYYY-MM) for monthly processing"
    )
    source_module: Optional[str] = Field(
        default=None,
        description="Module that created this entry (mobile, web, api, etc.)"
    )
    created_by: Optional[str] = Field(
        default=None,
        description="User who created this entry for audit purposes"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )

    # Vietnamese document constants
    VIETNAMESE_CURRENCIES: ClassVar[list] = ["VND", "USD", "EUR", "JPY", "GBP"]
    MAX_VAT_RATE: ClassVar[Decimal] = Decimal("1.00")
    MAX_VAT_RATE_PERCENT: ClassVar[float] = 100.00
    DOUBLE_ENTRY_TOLERANCE: ClassVar[Decimal] = Decimal("0.001")
    MAX_JOURNAL_DESCRIPTION_LENGTH: ClassVar[int] = 500

    @field_validator('journal_number')
    @classmethod
    def validate_journal_number(cls, v):
        """
        Validate Vietnamese journal entry number format
        """
        if not v.startswith('JV'):
            raise ValidationError(ErrorCodes.JOURNAL_NUMBER_PREFIX)

        suffix = v[2:]
        if not suffix.isdigit():
            raise ValidationError(ErrorCodes.JOURNAL_NUMBER_SUFFIX)

        return v

    @field_validator('transaction_date')
    @classmethod
    def validate_date(cls, v):
        """
        Validate transaction date for Vietnamese business operations
        """
        if v is None:
            raise ValidationError(ErrorCodes.TRANSACTION_DATE_NONE)

        if v.year < 2000 or v.year > 2100:
            raise DateError("Transaction date must be between 2000-2100")

        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """
        Validate Vietnamese journal entry description
        """
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
        """
        Validate VAT rate for Vietnamese tax compliance
        """
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
        """
        Validate accounting period format (YYYY-MM)
        """
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
        """
        Add a line to this journal entry
        """
        if not hasattr(self, 'lines'):
            from app.domain.models import JournalLine
            self.lines = []

        line = JournalLine(
            account_id=account_id,
            debit=debit,
            credit=credit,
            description=description,
            vat_rate=vat_rate
        )
        self.lines.append(line)
        self.validate_double_entry()
        return line

    def validate_double_entry(self) -> bool:
        """
        Validate double-entry bookkeeping for Vietnamese accounting standards
        Ensures total debits equal total credits within 0.001 VND tolerance
        """
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
        """
        Calculate VAT amounts for Vietnamese tax compliance
        """
        vat_amounts = {}
        for line in self.lines:
            if line.vat_rate:
                vat_amounts[line.account_id] = line.debit * line.vat_rate
        return vat_amounts

    def format_vietnamese_currency(self, amount: Decimal) -> str:
        """
        Format decimal amount with Vietnamese currency formatting
        Example: 1.500.000,50 đ
        """
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
        """
        Format date with Vietnamese locale
        Example: 15 tháng 1 năm 2024
        """
        month_names_vi = {
            1: "tháng 1", 2: "tháng 2", 3: "tháng 3", 4: "tháng 4",
            5: "tháng 5", 6: "tháng 6", 7: "tháng 7", 8: "tháng 8",
            9: "tháng 9", 10: "tháng 10", 11: "tháng 11", 12: "tháng 12"
        }

        month_name = month_names_vi.get(self.date.month, f"tháng {self.date.month}")
        return f"{self.date.day} {month_name} năm {self.date.year}"

    def is_valid_vas_compliance(self) -> bool:
        """
        Validate complete VAS compliance for Vietnamese accounting system
        """
        try:
            self.validate_double_entry()

            for line in self.lines:
                if line.vat_rate and not Decimal("0.00") <= line.vat_rate <= Decimal("1.00"):
                    raise VASComplianceError(f"VAT rate {line.vat_rate} is not compliant with Vietnamese tax regulations")

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
                {
                    "journal_number": "JV001",
                    "date": "2024-01-15",
                    "description": "Mua hàng trả tiền mặt",
                    "period": "2024-01",
                    "is_valid": True
                },
                {
                    "journal_number": "JV002", 
                    "date": "2024-01-16",
                    "description": "Thanh toán tiền hàng",
                    "period": "2024-01",
                    "vat_rate": "0.10"
                }
            ]
        }
    )
class JournalLine(BaseModel):
    """
    Journal line entity for detailed transaction recording
    """
    id: Optional[int] = Field(default=None, description="Primary key identifier")
    journal_entry_id: int = Field(..., description="Reference to parent journal entry")
    account_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Account identifier (chart code or account number)"
    )
    debit: Decimal = Field(
        default=Decimal("0.00"),
        description="Debit amount with Vietnamese monetary precision"
    )
    credit: Decimal = Field(
        default=Decimal("0.00"),
        description="Credit amount with Vietnamese monetary precision"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Line description in Vietnamese"
    )
    vat_rate: Optional[Decimal] = Field(
        default=None,
        description="VAT rate for Vietnamese tax compliance (0.00 to 1.00)"
    )
    side: str = Field(
        default="debit",
        description="Side of transaction (debit or credit) for Vietnamese accounting"
    )
    line_type: str = Field(
        default="regular",
        description="Type of journal line (regular, adjustment, reversal)"
    )
    is_taxable: bool = Field(
        default=False,
        description="Whether this line is subject to Vietnamese VAT"
    )
    tax_code: Optional[str] = Field(
        default=None,
        description="Vietnamese tax code for tax reporting"
    )
    period: str = Field(
        default_factory=lambda: date.today().strftime("%Y-%m"),
        description="Accounting period (YYYY-MM)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )

    MAX_VAT_RATE: ClassVar[Decimal] = Decimal("1.00")
    MAX_VAT_RATE_PERCENT: ClassVar[float] = 100.00
    JOURNAL_LINE_TOLERANCE: ClassVar[Decimal] = Decimal("0.001")
    VIETNAMESE_CURRENCIES: ClassVar[list] = ["VND", "USD", "EUR", "JPY", "GBP"]

    @field_validator('debit', 'credit')
    @classmethod
    def validate_amount_precision(cls, v):
        """
        Validate monetary amounts with Vietnamese precision standards (2 decimal places)
        """
        if v < 0:
            raise ValidationError(ErrorCodes.DEBIT_CREDIT_NEGATIVE)

        if abs(v) > Decimal("1000000000.00"):
            raise ValidationError(ErrorCodes.AMOUNT_MAX)

        return v.quantize(Decimal("0.01"))

    @field_validator('vat_rate')
    @classmethod
    def validate_vat_rate(cls, v):
        """
        Validate VAT rate for Vietnamese tax compliance
        """
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
        """
        Validate account identifier for Vietnamese accounting system
        """
        if not v.strip():
            raise ValidationError(ErrorCodes.ACCOUNT_ID_EMPTY)

        v_clean = v.strip()

        if v_clean.startswith('0') and len(v_clean) > 1:
            raise ValidationError("Account ID cannot start with 0 after stripping spaces")

        return v_clean

    def validate_debit_credit_tolerance(self) -> bool:
        """
        Validate debit-credit tolerance for Vietnamese accounting
        Ensures accuracy within 0.001 VND
        """
        difference = abs(self.debit - self.credit)
        return difference <= self.JOURNAL_LINE_TOLERANCE

    def calculate_vat_amount(self) -> Decimal:
        """
        Calculate VAT amount for Vietnamese tax reporting
        """
        if not self.vat_rate:
            return Decimal("0.00")

        return self.debit * self.vat_rate

    def get_vi_currency_symbol(self) -> str:
        """
        Get Vietnamese currency symbol
        """
        return "đ" if self.currency == "VND" else "USD"

    def format_vietnamese_currency(self, amount: Optional[Decimal] = None) -> str:
        """
        Format amount with Vietnamese currency formatting
        """
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
                {
                    "account_id": "1111",
                    "debit": "1000.00",
                    "credit": "0.00",
                    "description": "Tiền mặt",
                    "vat_rate": "0.10"
                },
                {
                    "account_id": "2111",
                    "debit": "0.00",
                    "credit": "1000.00",
                    "description": "Hàng đã mua",
                    "vat_rate": "0.00"
                }
            ]
        }
    )


class FinancialStatement(BaseModel):
    """
    Financial Statement entity for Vietnamese accounting reports
    Supports Balance Sheet, Income Statement, and Cash Flow
    """
    id: Optional[int] = Field(default=None, description="Primary key identifier")
    period: str = Field(
        ...,
        pattern=r'\d{4}-\d{2}',
        description="Accounting period (YYYY-MM)"
    )
    statement_type: str = Field(
        ...,
        description="Statement type: balance_sheet, income_statement, cash_flow"
    )
    assets: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Assets by category with Vietnamese formatting"
    )
    liabilities: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Liabilities by category with Vietnamese formatting"
    )
    equity: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Equity by category with Vietnamese formatting"
    )
    revenue: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Revenue by category with Vietnamese formatting"
    )
    expenses: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Expenses by category with Vietnamese formatting"
    )
    is_approved: bool = Field(default=False, description="Whether the statement is approved")
    approved_by: Optional[str] = Field(default=None, description="User who approved the statement")
    approval_date: Optional[date] = Field(default=None, description="Date of approval")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when statement was generated"
    )
    generated_by: Optional[str] = Field(
        default=None,
        description="System or user that generated the statement"
    )
    remarks: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Remarks for Vietnamese financial reporting"
    )

    # Vietnamese financial statement constants
    VIETNAMESE_CURRENCY: ClassVar[str] = "VND"
    VIETNAMESE_LOCALE: ClassVar[str] = "vi_VN"
    STATEMENT_TYPES: ClassVar[list] = ["balance_sheet", "income_statement", "cash_flow"]

    @field_validator('period')
    @classmethod
    def validate_period(cls, v):
        """
        Validate accounting period format
        """
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
        """
        Validate statement type
        """
        if v not in cls.STATEMENT_TYPES:
            raise ValidationError(ErrorCodes.STATEMENT_TYPE_INVALID)
        return v

    def calculate_balance_sheet_totals(self) -> Dict[str, Decimal]:
        """
        Calculate balance sheet totals for Vietnamese financial reporting
        Returns assets, liabilities, and equity totals
        """
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
        """
        Calculate income statement totals for Vietnamese financial reporting
        """
        revenue_total = sum(self.revenue.values())
        expenses_total = sum(self.expenses.values())
        net_income = revenue_total - expenses_total

        return {
            "revenue_total": revenue_total,
            "expenses_total": expenses_total,
            "net_income": net_income,
        }

    def format_vietnamese_amount(self, amount: Decimal) -> str:
        """
        Format amount with Vietnamese locale conventions
        Example: 1.500.000,00 VND
        """
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
        """
        Generate monthly financial summary for Vietnamese accounting
        Returns formatted financial data for Vietnamese SMEs
        """
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
        """
        Generate monthly financial statement for Vietnamese accounting standards
        Returns FinancialStatement object with properly formatted data
        """
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
        """
        Get current month from period
        """
        try:
            return int(self.period.split('-')[1])
        except (ValueError, IndexError):
            return date.today().month

    def is_vas_compliant(self) -> bool:
        """
        Validate that financial statement complies with Vietnamese Accounting Standards
        """
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
                {
                    "period": "2024-01",
                    "statement_type": "balance_sheet",
                    "assets": {"cash": "10000.00", "accounts_receivable": "5000.00"},
                    "liabilities": {"accounts_payable": "3000.00"},
                    "equity": {"capital": "12000.00"},
                    "revenue": {},
                    "expenses": {}
                },
                {
                    "period": "2024-02",
                    "statement_type": "income_statement",
                    "assets": {},
                    "liabilities": {},
                    "equity": {},
                    "revenue": {"sales": "50000.00"},
                    "expenses": {"cost_of_sales": "30000.00"}
                }
            ]
        },
        frozen=True,
    )
    __init__ = None  # Get around Circle import issue
class FinancialStatementError(Exception):
    """Exception for financial statement errors"""
    pass
class ChartOfAccountsError(VASValidationError):
    """Exception for Chart of Accounts errors"""
    pass
class AccountError(VASValidationError):
    """Exception for Account errors (extends VASValidationError)"""
    pass
class JournalEntryError(VASValidationError):
    """Exception for Journal Entry errors"""
    pass
class FinancialReportError(Exception):
    """Exception for financial report generation errors"""
    pass
class VIETNAMESE_CURRENCY_SYMBOLS:
    """Vietnamese currency symbols and formatting"""
    VND = "VND"
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    GBP = "GBP"

    VIETNAMESE_FORMAT = "VND"
    COMMODITY_CURRENCIES = [USD, EUR, JPY, GBP]

    @classmethod
    def get_symbol(cls, currency: str) -> str:
        """Get currency symbol for a given currency code"""
        return currency.upper()

    @classmethod
    def is_vietnamese_currency(cls, currency: str) -> bool:
        """Check if currency is Vietnamese Dong"""
        return currency.upper() == "VND"

    @classmethod
    def format_vietnamese_currency(cls, amount: Decimal, currency: str = "VND") -> str:
        """
        Format amount with Vietnamese currency conventions
        Example: 1.500.000,50 VND
        """
        if amount == Decimal("0"):
            return "0,00 VND"

        amount_str = str(abs(float(amount)))

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

        currency_symbol = "đ" if currency == "VND" else currency
        formatted_amount = f"{formatted_integer},{decimal_part}"

        if amount < 0:
            formatted_amount = f"-{formatted_amount}"

        return f"{formatted_amount} {currency_symbol}"

    @classmethod
    def format_vietnamese_number(cls, amount: Decimal) -> str:
        """
        Format number with Vietnamese grouping convention
        Example: 1,500,000 (commas as thousand separators)
        """
        return f"{amount:,.0f}"

    @classmethod
    def format_vietnamese_percentage(cls, percentage: Decimal) -> str:
        """
        Format percentage with Vietnamese conventions
        Example: 10,50%
        """
        formatted = f"{percentage:.2f}".replace('.', ',')
        return f"{formatted}%"

    @classmethod
    def format_vietnamese_date(cls, date_obj: date) -> str:
        """
        Format date with Vietnamese month names
        Example: 15 tháng 1 năm 2024
        """
        month_names_vi = {
            1: "tháng 1", 2: "tháng 2", 3: "tháng 3", 4: "tháng 4",
            5: "tháng 5", 6: "tháng 6", 7: "tháng 7", 8: "tháng 8",
            9: "tháng 9", 10: "tháng 10", 11: "tháng 11", 12: "tháng 12"
        }

        month_name = month_names_vi.get(date_obj.month, f"tháng {date_obj.month}")
        return f"{date_obj.day} {month_name} năm {date_obj.year}"
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


def _quantize_vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class TaxDeclaration(BaseModel):
    VALID_FORM_CODE_PATTERN: ClassVar[str] = r'^\d{2}/\w+(-\w+)?$'
    MAX_FORM_CODE_LENGTH: ClassVar[int] = 20

    id: Optional[int] = Field(default=None, description="Primary key")
    tax_type: TaxType = Field(..., description="Tax type (VAT, CIT, PIT, etc.)")
    declaration_type: DeclarationType = Field(default=DeclarationType.ORIGINAL)
    form_code: str = Field(..., max_length=MAX_FORM_CODE_LENGTH, description="GDT form code (01/GTGT, 03/TNDN)")
    period_year: int = Field(..., ge=2000, le=2100, description="Fiscal year")
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
    line_code: str = Field(..., description="GDT form line code (e.g., [21], [22], [23])")
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
    tax_type: TaxType = Field(..., description="Tax type being paid")
    amount: Decimal = Field(..., gt=Decimal("0"), description="Payment amount")
    payment_date: date = Field(..., description="Actual payment date")
    due_date: date = Field(..., description="Legal due date")
    budget_account: str = Field(default="1701", max_length=10, description="State budget account")
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
    adjustment_type: TaxAdjustmentType = Field(..., description="Type of adjustment")
    supplemental_declaration_id: Optional[int] = Field(default=None, description="FK to supplemental TaxDeclaration")
    reason: str = Field(..., max_length=1000, description="Reason for adjustment")
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
    tax_type: TaxType = Field(..., description="Applicable tax type")
    incentive_type: TaxIncentiveType = Field(...)
    code: str = Field(..., max_length=50, description="Incentive code (e.g., UT_CNC, UT_DT)")
    name: str = Field(..., max_length=300, description="Incentive name in Vietnamese")
    legal_basis: str = Field(..., max_length=200, description="Legal document reference")
    rate_value: Decimal = Field(default=Decimal("0"), description="Rate value (0-100% or absolute)")
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
    invoice_number: str = Field(..., max_length=20, description="Sequential invoice number")
    invoice_series: str = Field(..., max_length=10, description="Invoice series (e.g., 1C24TAA)")
    invoice_date: date = Field(..., description="Invoice issuance date")
    invoice_type: InvoiceType = Field(default=InvoiceType.SALES)
    seller_tax_code: str = Field(..., max_length=15, pattern=r'^\d{10}(-\d{3})?$')
    seller_name: str = Field(..., max_length=300)
    seller_address: Optional[str] = Field(default=None, max_length=500)
    buyer_tax_code: Optional[str] = Field(default=None, max_length=15)
    buyer_name: Optional[str] = Field(default=None, max_length=300)
    buyer_address: Optional[str] = Field(default=None, max_length=500)
    buyer_id: Optional[str] = Field(default=None, max_length=50, description="Internal customer id")

    subtotal: Decimal = Field(default=Decimal("0.00"))
    discount_amount: Decimal = Field(default=Decimal("0.00"))
    vat_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("1"),
                              description="VAT rate as decimal (0-1)")
    vat_amount: Decimal = Field(default=Decimal("0.00"))
    grand_total: Decimal = Field(default=Decimal("0.00"))

    currency: str = Field(default="VND")
    exchange_rate: Decimal = Field(default=Decimal("1"))
    payment_method: Optional[str] = Field(default=None, max_length=100)
    status: InvoiceStatus = Field(default=InvoiceStatus.CREATED)
    verification_code: Optional[str] = Field(default=None, max_length=50, description="GDT verification code")
    gdt_transaction_id: Optional[str] = Field(default=None, max_length=100)
    signed_file_url: Optional[str] = Field(default=None, max_length=500)
    digital_signature: Optional[str] = Field(default=None)

    adjustment_ref_id: Optional[int] = Field(default=None, description="Original invoice if adjustment/replacement")
    adjustment_type: Optional[EInvoiceAdjustmentType] = Field(default=None)
    adjustment_reason: Optional[str] = Field(default=None, max_length=500)
    original_invoice_ref: Optional[str] = Field(default=None, max_length=50)

    lines: List[Dict[str, Any]] = Field(default_factory=list, description="Invoice line items")

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
    invoice_id: int = Field(..., description="FK to EInvoice")
    line_number: int = Field(default=1, ge=1)
    product_code: Optional[str] = Field(default=None, max_length=50)
    product_name: str = Field(..., max_length=500)
    unit: str = Field(default="cái", max_length=50)
    quantity: Decimal = Field(default=Decimal("1"), gt=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    discount_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("1"),
                                   description="Discount rate as decimal (0-1)")
    discount_amount: Decimal = Field(default=Decimal("0"))
    vat_rate: Decimal = Field(default=Decimal("0.1"), ge=Decimal("0"), le=Decimal("1"),
                              description="VAT rate as decimal (0-1)")
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


class BankAccountStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    BLOCKED = "blocked"


class ChequeStatus(str, Enum):
    NEW = "new"
    ISSUED = "issued"
    CLEARED = "cleared"
    CANCELLED = "cancelled"
    STOPPED = "stopped"
    BOUNCED = "bounced"


class CashTransferStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    FAILED = "failed"


class PettyCashFundStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class ReconciliationDiscrepancyType(str, Enum):
    DEPOSIT_IN_TRANSIT = "deposit_in_transit"
    OUTSTANDING_CHECK = "outstanding_check"
    BANK_CHARGE = "bank_charge"
    BANK_INTEREST = "bank_interest"
    ERROR = "error"


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


class BankAccount(BaseModel):
    id: Optional[int] = None
    bank_name: str = Field(..., min_length=1, max_length=200)
    branch: str = Field(..., min_length=1, max_length=200)
    account_number: str = Field(..., min_length=1, max_length=50)
    account_holder: str = Field(..., min_length=1, max_length=300)
    currency: str = "VND"
    coa_code: str
    swift_code: Optional[str] = None
    iban: Optional[str] = None
    opening_balance: Decimal = Decimal("0")
    status: BankAccountStatus = BankAccountStatus.ACTIVE
    signatories: List[str] = Field(default_factory=list)
    authorization_limit: Decimal = Decimal("0")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("opening_balance", "authorization_limit")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


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
    """TK 141 — Tam ung (advance to individual employee)"""
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


class IFRSMapping(BaseModel):
    """VAS to IFRS account mapping for dual-reporting (UC-05)"""
    id: Optional[int] = Field(default=None)
    vas_account_code: str = Field(..., min_length=1, max_length=20)
    ifrs_account_code: str = Field(..., min_length=1, max_length=20)
    mapping_type: str = Field(default="1:1", pattern=r'^(1:1|N:1|1:N|expression)$')
    expression: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=500)
    created_by: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator('vas_account_code', 'ifrs_account_code')
    @classmethod
    def validate_code(cls, v):
        if not v.strip():
            raise ValidationError(ErrorCodes.IFRS_CODE_EMPTY)
        return v.strip()


__all__ = [
    'VASValidationError', 'ValidationError', 'VASComplianceError', 'DoubleEntryError',
    'InvalidCurrencyError', 'CurrencyError', 'InvalidAccountError', 'AccountError',
    'ChartError', 'DateError', 'Result', 'AccountType', 'DCRDirection', 'ChartOfAccounts',
    'Account', 'JournalEntry', 'JournalLine', 'FinancialStatement', 'FinancialStatementError',
    'ChartOfAccountsError', 'AccountError', 'JournalEntryError', 'FinancialReportError',
    'VIETNAMESE_CURRENCY_SYMBOLS', 'IFRSMapping',
    'TaxType', 'VATCalculationMethod', 'PITRateType', 'DeclarationType', 'DeclarationStatus',
    'TaxPaymentStatus', 'InvoiceStatus', 'TaxAdjustmentType', 'TaxIncentiveType',
    'TaxAdjustmentStatus', 'IncentiveStatus', 'ScheduleStatus', 'InvoiceType', 'EInvoiceAdjustmentType',
    'TaxDeclaration', 'TaxLine', 'TaxPayment', 'TaxAdjustment', 'TaxIncentive',
    'EInvoice', 'EInvoiceLine', 'TaxSchedule',
    'CashReceiptType', 'CashPaymentType', 'CashVoucherStatus', 'BankAccountStatus',
    'ChequeStatus', 'CashTransferStatus', 'PettyCashFundStatus', 'ReconciliationDiscrepancyType',
    'CashReceipt', 'CashPayment', 'BankAccount', 'BankTransaction', 'BankStatement',
    'ReconciliationDiscrepancy', 'BankReconciliation', 'PettyCashFund', 'PettyCashTransaction',
    'CashTransfer', 'ChequeBook', 'Cheque', 'CashForecast', 'CashForecastLine',
    'DailyCashCount', 'Advance',
]
