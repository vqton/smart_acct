from typing import List, Dict, Optional, Any, ClassVar
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
import re
from domain.i18n import ErrorCodes
from domain.common import (
    VASValidationError, ValidationError, InvalidAccountError, InvalidCurrencyError,
    ChartError, Result, _quantize_vnd,
)


class AccountType(str, Enum):
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
    INTANGIBLE_ASSETS = "intangible_assets"
    PATENT_RIGHT = "patent_right"
    COPYRIGHT = "copyright"
    SOFTWARE = "software"
    FRANCHISE = "franchise"
    GOODWILL = "goodwill"
    MARKETING_ASSETS = "marketing_assets"
    FINANCIAL_ASSETS = "financial_assets"
    SHORT_TERM_FINANCIAL_ASSETS = "short_term_financial_assets"
    LONG_TERM_FINANCIAL_ASSETS = "long_term_financial_assets"
    ADVANCE = "advance"
    ASSET_SHORTAGE = "asset_shortage"
    ASSET_SURPLUS = "asset_surplus"
    CASH_EQUIVALENT = "cash_equivalent"
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
    EQUITY = "equity"
    CAPITAL_CONTRIBUTED = "capital_contributed"
    CAPITAL_SURPLUS = "capital_surplus"
    RETAINED_EARNINGS = "retained_earnings"
    REVALUATION_SURPLUS = "revaluation_surplus"
    CAPITAL_SUBSIDIARY_ACCOUNT = "capital_subsidiary_account"
    CORPORATE_BOND_SURPLUS = "corporate_bond_surplus"
    INVESTMENT_IN_PARTNER = "investment_in_partner"
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
    DEPRECIATION_EXPENSE = "depreciation_expense"
    AMORTIZATION_EXPENSE = "amortization_expense"
    BIOLOGICAL_ASSET = "biological_asset"
    PROVISION_FOR_BIOLOGICAL_ASSET = "provision_for_biological_asset"
    SCT_IMPORTED_GOODS = "sct_imported_goods"
    GMT_CIT_EXPENSE = "gmt_cit_expense"
    VAT_INPUT = "vat_input"
    CIT_PAYMENT = "cit_payment"
    PIT_PAYMENT = "pit_payment"
    COST_OF_GOODS_SOLD = "cost_of_goods_sold"
    GROSS_PROFIT = "gross_profit"
    NET_PROFIT = "net_profit"
    EQUITY_DISTRIBUTION = "equity_distribution"


class DCRDirection(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"

    @classmethod
    def get_direction(cls, account_type: AccountType) -> 'DCRDirection':
        debit_normal_accounts = {
            AccountType.ASSET, AccountType.CASH, AccountType.BANK,
            AccountType.SHORT_TERM_FINANCIAL_INVESTMENT, AccountType.ACCOUNT_RECEIVABLE,
            AccountType.ADVANCE, AccountType.ASSET_SHORTAGE, AccountType.CASH_EQUIVALENT,
            AccountType.SHORT_TERM_LOANS_TO_ENTERPRISES, AccountType.COST_OF_SALES,
            AccountType.OPERATIONAL_EXPENSES, AccountType.DEPRECIATION_EXPENSE, AccountType.VAT_INPUT,
            AccountType.BIOLOGICAL_ASSET, AccountType.SCT_IMPORTED_GOODS, AccountType.GMT_CIT_EXPENSE,
        }
        credit_normal_accounts = {
            AccountType.LIABILITY, AccountType.EQUITY, AccountType.REVENUE,
            AccountType.FINANCIAL_REVENUE, AccountType.COST_OF_GOODS_SOLD, AccountType.GROSS_PROFIT,
            AccountType.NET_PROFIT, AccountType.EQUITY_DISTRIBUTION, AccountType.ASSET_SURPLUS,
            AccountType.PROVISION_FOR_BIOLOGICAL_ASSET,
        }
        if account_type in debit_normal_accounts:
            return cls.DEBIT
        elif account_type in credit_normal_accounts:
            return cls.CREDIT
        else:
            return cls.DEBIT


class AccountingRegime(str, Enum):
    TT99_2025 = "tt99_2025"
    TT133_2016 = "tt133_2016"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class ChartOfAccounts(BaseModel):
    code: str = Field(
        ...,
        min_length=1, max_length=20,
        pattern=r'^[1-9](?:\.[0-9]+)*$|^[1-9][0-9]{3,5}$',
        description="VAS account code: dotted (1, 1.1, 1.1.1) or flat numeric (1111, 11111)"
    )
    name: str = Field(..., min_length=1, max_length=300, description="Vietnamese account name")
    account_type: AccountType = Field(..., description="Account type per VAS (Type 1-9)")
    regime: AccountingRegime = Field(default=AccountingRegime.TT99_2025, description="Accounting regime")
    vas_compliant: bool = Field(default=True, description="Whether the account code follows VAS rules")
    drcr_direction: DCRDirection = Field(..., description="Normal balance direction")
    level: int = Field(default=1, ge=1, le=4, description="Hierarchy level (1-4)")
    status: AccountStatus = Field(default=AccountStatus.ACTIVE, description="Account lifecycle status")
    currency: str = Field(default="VND", description="Default currency")
    unit: str = Field(default="VND", description="Accounting unit")
    parent_code: Optional[str] = Field(default=None, description="Parent account code")
    description: Optional[str] = Field(default=None, max_length=500, description="Account description")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    @field_validator('code')
    @classmethod
    def validate_account_code(cls, v):
        if not v:
            raise ValidationError(ErrorCodes.ACCOUNT_CODE_EMPTY)
        code_clean = v.replace('.', '')
        if not code_clean.isdigit():
            raise InvalidAccountError(ErrorCodes.ACCOUNT_CODE_NUMERIC)
        if len(code_clean) > 6:
            raise InvalidAccountError(ErrorCodes.ACCOUNT_CODE_MAX_DIGITS)
        if '.' in v:
            max_level = len(v.split('.'))
            if max_level > 4:
                raise InvalidAccountError(ErrorCodes.ACCOUNT_CODE_MAX_LEVELS)
        first_char = v[0]
        if first_char < '1' or first_char > '9':
            raise InvalidAccountError(ErrorCodes.ACCOUNT_CODE_FIRST_DIGIT)
        if v.startswith('0'):
            raise InvalidAccountError(ErrorCodes.ACCOUNT_CODE_NO_ZERO)
        return v

    @field_validator('name')
    @classmethod
    def validate_account_name(cls, v):
        if not v.strip():
            raise ValidationError(ErrorCodes.ACCOUNT_NAME_EMPTY)
        return v.strip()

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        valid_currencies = ["VND", "USD", "EUR", "JPY", "GBP"]
        if v.upper() not in valid_currencies:
            raise InvalidCurrencyError(f"Currency must be one of {valid_currencies}")
        return v.upper()

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v):
        if not v:
            raise ValidationError(ErrorCodes.UNIT_EMPTY)
        return v.upper()

    def calculate_balance(self, drcr_direction: DCRDirection, transaction_amount: Decimal) -> Decimal:
        if drcr_direction == DCRDirection.DEBIT:
            return transaction_amount
        return -transaction_amount

    def get_translation(self, target_language: str = "vi") -> str:
        if target_language == "vi":
            return self.name
        return f"{self.name} (Account {self.code})"

    def is_asset_type(self) -> bool:
        return self.account_type in [
            AccountType.ASSET, AccountType.CASH, AccountType.BANK,
            AccountType.SHORT_TERM_FINANCIAL_INVESTMENT, AccountType.LONG_TERM_FINANCIAL_INVESTMENT,
            AccountType.ACCOUNT_RECEIVABLE, AccountType.SHORT_TERM_LOANS_TO_ENTERPRISES,
            AccountType.PREPAID_EXPENSES, AccountType.INVENTORY_GOODS,
            AccountType.PRODUCTION_IN_PROGRESS, AccountType.CONSTRUCTION_IN_PROGRESS
        ]

    def is_liability_type(self) -> bool:
        return self.account_type in [
            AccountType.LIABILITY, AccountType.SHORT_TERM_LIABILITIES, AccountType.LONG_TERM_LIABILITIES
        ]

    def is_equity_type(self) -> bool:
        return self.account_type in [
            AccountType.EQUITY, AccountType.CAPITAL_CONTRIBUTED, AccountType.CAPITAL_SURPLUS,
            AccountType.RETAINED_EARNINGS, AccountType.REVALUATION_SURPLUS, AccountType.EQUITY_DISTRIBUTION,
        ]

    def is_revenue_type(self) -> bool:
        return self.account_type in [AccountType.REVENUE, AccountType.FINANCIAL_REVENUE]

    def is_expense_type(self) -> bool:
        return self.account_type in [AccountType.EXPENSE, AccountType.DEPRECIATION_EXPENSE]

    def get_account_type_group(self) -> str:
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
                {"code": "1.1.1", "name": "Tài sản ngắn hạn", "account_type": AccountType.ASSET,
                 "vas_compliant": True, "drcr_direction": DCRDirection.DEBIT, "currency": "VND"},
                {"code": "2.1.1", "name": "Nguồn vốn chủ sở hữu", "account_type": AccountType.EQUITY,
                 "vas_compliant": True, "drcr_direction": DCRDirection.CREDIT, "currency": "VND"},
                {"code": "4.1.1", "name": "Doanh thu bán hàng", "account_type": AccountType.SALES_REVENUE,
                 "vas_compliant": True, "drcr_direction": DCRDirection.CREDIT, "currency": "VND"},
            ]
        },
    )


class Account(BaseModel):
    account_number: str = Field(..., min_length=4, max_length=20, pattern=r'^[0-9]{4,20}$',
                                description="Unique account number (4-20 digits)")
    name: str = Field(..., min_length=1, max_length=300, description="Vietnamese account name")
    account_type: AccountType = Field(..., description="Account type per VAS (Type 1-9)")
    chart_code: str = Field(..., description="Reference to Chart of Accounts code")
    currency: str = Field(default="VND", description="Currency with Vietnamese locale")
    drcr_direction: DCRDirection = Field(..., description="Normal balance direction")
    exchange_rate: Decimal = Field(default=Decimal("1.000"), description="Exchange rate")
    opening_balance: Decimal = Field(default=Decimal("0.00"), description="Opening balance")
    balance: Decimal = Field(default=Decimal("0.00"), description="Current account balance")
    monthly_balances: Dict[str, Decimal] = Field(default_factory=dict, description="Monthly balances")
    is_active: bool = Field(default=True, description="Whether this account is currently active")
    description: Optional[str] = Field(default=None, max_length=500, description="Extended description")
    last_updated: Optional[datetime] = Field(default=None, description="Last update timestamp")
    created_by: Optional[str] = Field(default=None, description="User who created the account")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    VIETNAMESE_CURRENCIES: ClassVar[list] = ["VND", "USD", "EUR", "JPY", "GBP"]
    VIETNAMESE_LOCALE: ClassVar[str] = "vi_VN"

    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v):
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
        if not v.strip():
            raise ValidationError(ErrorCodes.ACCOUNT_NAME_EMPTY)
        return v.strip()

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if not v:
            raise ValidationError(ErrorCodes.CURRENCY_EMPTY)
        v_upper = v.upper()
        if v_upper not in cls.VIETNAMESE_CURRENCIES:
            raise InvalidCurrencyError(f"Currency must be one of {cls.VIETNAMESE_CURRENCIES}")
        if v_upper != "VND" and v_upper not in ["USD", "EUR", "JPY", "GBP"]:
            raise InvalidCurrencyError(ErrorCodes.CURRENCY_SME_ONLY)
        return v_upper

    @field_validator('opening_balance', 'balance')
    @classmethod
    def validate_balance_precision(cls, v):
        if v is None:
            raise ValidationError(ErrorCodes.BALANCE_NONE)
        if abs(v) > Decimal("10000000000.00"):
            raise ValidationError("Balance cannot exceed 10 billion VND")
        return v.quantize(Decimal("0.01"))

    @field_validator('exchange_rate')
    @classmethod
    def validate_exchange_rate(cls, v):
        if v <= 0:
            raise ValidationError(ErrorCodes.EXCHANGE_RATE_POSITIVE)
        return v.quantize(Decimal("0.001"))

    @field_validator('drcr_direction')
    @classmethod
    def validate_drcr_direction(cls, v):
        if not v:
            raise ValidationError(ErrorCodes.DCR_DIRECTION_EMPTY)
        valid_directions = [direction.value for direction in DCRDirection]
        if v.lower() not in valid_directions:
            raise ValidationError(f"DCR direction must be one of {valid_directions}")
        return DCRDirection(v.lower()).value

    @field_validator('chart_code')
    @classmethod
    def validate_chart_code(cls, v):
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
        if amount is None:
            amount = self.balance
        if amount is None or amount == Decimal("0"):
            return "0,00 đ"
        amount_float = float(amount)
        formatted_number = f"{amount_float:,.2f}"
        formatted_number = formatted_number.replace(",", ".")
        formatted_number = formatted_number.replace(".", ".", formatted_number.count(".") - 2)
        return f"{formatted_number} đ"

    def format_vietnamese_number(self, amount: Decimal) -> str:
        formatted_number = f"{amount:,.0f}"
        return formatted_number.replace(",", ".")

    def add_monthly_balance(self, month: str, amount: Decimal):
        if not isinstance(month, str) or not re.match(r'\d{4}-\d{2}', month):
            raise ValidationError("Month must be in YYYY-MM format")
        if month not in self.monthly_balances:
            self.monthly_balances[month] = Decimal("0.00")
        self.monthly_balances[month] += amount
        self.balance = self.calculate_running_balance()

    def calculate_running_balance(self) -> Decimal:
        if not self.monthly_balances:
            return self.opening_balance
        last_month = sorted(self.monthly_balances.keys())[-1]
        total_monthly_changes = sum(self.monthly_balances.values())
        return self.opening_balance + total_monthly_changes

    def is_asset_account(self) -> bool:
        asset_types = {
            AccountType.ASSET, AccountType.CASH, AccountType.BANK,
            AccountType.SHORT_TERM_FINANCIAL_INVESTMENT, AccountType.LONG_TERM_FINANCIAL_INVESTMENT,
            AccountType.ACCOUNT_RECEIVABLE, AccountType.SHORT_TERM_LOANS_TO_ENTERPRISES,
            AccountType.PREPAID_EXPENSES, AccountType.INVENTORY_GOODS,
            AccountType.PRODUCTION_IN_PROGRESS, AccountType.CONSTRUCTION_IN_PROGRESS
        }
        return self.account_type in asset_types

    def is_liability_account(self) -> bool:
        liability_types = {
            AccountType.LIABILITY, AccountType.SHORT_TERM_LIABILITIES, AccountType.LONG_TERM_LIABILITIES
        }
        return self.account_type in liability_types

    def is_equity_account(self) -> bool:
        equity_types = {
            AccountType.EQUITY, AccountType.CAPITAL_CONTRIBUTED, AccountType.CAPITAL_SURPLUS,
            AccountType.RETAINED_EARNINGS
        }
        return self.account_type in equity_types

    def is_revenue_account(self) -> bool:
        revenue_types = {AccountType.REVENUE, AccountType.SALES_REVENUE, AccountType.SERVICE_REVENUE}
        return self.account_type in revenue_types

    def is_expense_account(self) -> bool:
        expense_types = {AccountType.EXPENSE, AccountType.COST_OF_SALES}
        return self.account_type in expense_types

    def get_normal_balance(self) -> Decimal:
        if self.is_asset_account() or self.is_expense_account():
            return Decimal("0.00")
        else:
            return Decimal("0.00")

    def validate_vas_compliance(self) -> bool:
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
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.balance = self.calculate_running_balance()
        self.last_updated = datetime.now(timezone.utc)

    def to_domain_dict(self) -> Dict[str, Any]:
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
                {"account_number": "1111", "name": "Tài khoản tiền mặt", "account_type": AccountType.ASSET,
                 "chart_code": "1.1.1", "currency": "VND", "drcr_direction": "debit", "opening_balance": "10000.00"},
                {"account_number": "2111", "name": "Các khoản phải trả", "account_type": AccountType.LIABILITY,
                 "chart_code": "2.1.1", "currency": "VND", "drcr_direction": "credit", "opening_balance": "5000.00"},
                {"account_number": "4111", "name": "Doanh thu bán hàng", "account_type": AccountType.SALES_REVENUE,
                 "chart_code": "4.1.1", "currency": "VND", "drcr_direction": "credit", "opening_balance": "0.00"},
            ]
        },
    )


class IFRSMapping(BaseModel):
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
