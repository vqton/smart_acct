from typing import List, Dict, Optional, Any, Union, ClassVar
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from abc import ABC, abstractmethod
import re
from domain.i18n import ErrorCodes


class VASValidationError(Exception):
    def __init__(self, msgid: str, **params):
        self.msgid = msgid
        self.params = params
        super().__init__(msgid)


class ValidationError(VASValidationError):
    pass


class VASComplianceError(VASValidationError):
    pass


class DoubleEntryError(VASValidationError):
    pass


class InvalidCurrencyError(VASValidationError):
    pass


class CurrencyError(VASValidationError):
    pass


class InvalidAccountError(VASValidationError):
    pass


class AccountError(VASValidationError):
    pass


class ChartError(VASValidationError):
    pass


class DateError(VASValidationError):
    pass


class Result:
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


class FinancialStatementError(Exception):
    pass


class ChartOfAccountsError(VASValidationError):
    pass


class JournalEntryError(VASValidationError):
    pass


class FinancialReportError(Exception):
    pass


class VIETNAMESE_CURRENCY_SYMBOLS:
    VND = "VND"
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    GBP = "GBP"

    VIETNAMESE_FORMAT = "VND"
    COMMODITY_CURRENCIES = [USD, EUR, JPY, GBP]

    @classmethod
    def get_symbol(cls, currency: str) -> str:
        return currency.upper()

    @classmethod
    def is_vietnamese_currency(cls, currency: str) -> bool:
        return currency.upper() == "VND"

    @classmethod
    def format_vietnamese_currency(cls, amount: Decimal, currency: str = "VND") -> str:
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
        return f"{amount:,.0f}"

    @classmethod
    def format_vietnamese_percentage(cls, percentage: Decimal) -> str:
        formatted = f"{percentage:.2f}".replace('.', ',')
        return f"{formatted}%"

    @classmethod
    def format_vietnamese_date(cls, date_obj: date) -> str:
        month_names_vi = {
            1: "tháng 1", 2: "tháng 2", 3: "tháng 3", 4: "tháng 4",
            5: "tháng 5", 6: "tháng 6", 7: "tháng 7", 8: "tháng 8",
            9: "tháng 9", 10: "tháng 10", 11: "tháng 11", 12: "tháng 12"
        }
        month_name = month_names_vi.get(date_obj.month, f"tháng {date_obj.month}")
        return f"{date_obj.day} {month_name} năm {date_obj.year}"


def _quantize_vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))
