import sys
sys.path.insert(0, "/home/projects/smart_acct")

import pytest
from datetime import datetime
from pydantic import ValidationError as PydanticValidationError
from domain import (
    ChartOfAccounts, Account, JournalEntry, JournalLine,
    AccountType, DCRDirection, AccountingRegime, AccountStatus,
    Result, VASValidationError, InvalidAccountError, InvalidCurrencyError,
)


class TestChartOfAccounts:
    def test_create_valid_account(self):
        acc = ChartOfAccounts(
            code="1.1", name="Tiền mặt",
            account_type=AccountType.CASH,
            drcr_direction=DCRDirection.DEBIT,
        )
        assert acc.code == "1.1"
        assert acc.name == "Tiền mặt"
        assert acc.regime == AccountingRegime.TT99_2025
        assert acc.status == AccountStatus.ACTIVE
        assert acc.level == 1

    def test_create_with_tt99_regime(self):
        acc = ChartOfAccounts(
            code="1", name="Tài sản",
            account_type=AccountType.ASSET,
            drcr_direction=DCRDirection.DEBIT,
            regime=AccountingRegime.TT99_2025,
        )
        assert acc.regime == AccountingRegime.TT99_2025

    def test_create_with_tt133_regime(self):
        acc = ChartOfAccounts(
            code="2", name="Nợ phải trả",
            account_type=AccountType.LIABILITY,
            drcr_direction=DCRDirection.CREDIT,
            regime=AccountingRegime.TT133_2016,
        )
        assert acc.regime == AccountingRegime.TT133_2016

    def test_create_with_suspended_status(self):
        acc = ChartOfAccounts(
            code="1.1.1", name="Test",
            account_type=AccountType.ASSET,
            drcr_direction=DCRDirection.DEBIT,
            status=AccountStatus.SUSPENDED,
        )
        assert acc.status == AccountStatus.SUSPENDED

    def test_rejects_invalid_code_empty(self):
        with pytest.raises(PydanticValidationError):
            ChartOfAccounts(
                code="", name="Test",
                account_type=AccountType.ASSET,
                drcr_direction=DCRDirection.DEBIT,
            )

    def test_rejects_code_starting_with_zero(self):
        with pytest.raises((InvalidAccountError, PydanticValidationError)):
            ChartOfAccounts(
                code="0.1", name="Test",
                account_type=AccountType.ASSET,
                drcr_direction=DCRDirection.DEBIT,
            )

    def test_rejects_non_numeric_code(self):
        with pytest.raises((InvalidAccountError, PydanticValidationError)):
            ChartOfAccounts(
                code="A.1", name="Test",
                account_type=AccountType.ASSET,
                drcr_direction=DCRDirection.DEBIT,
            )

    def test_rejects_code_with_too_many_levels(self):
        with pytest.raises((InvalidAccountError, PydanticValidationError)):
            ChartOfAccounts(
                code="1.1.1.1.1", name="Test",
                account_type=AccountType.ASSET,
                drcr_direction=DCRDirection.DEBIT,
            )

    def test_rejects_invalid_currency(self):
        with pytest.raises((InvalidCurrencyError, PydanticValidationError)):
            ChartOfAccounts(
                code="1", name="Test",
                account_type=AccountType.ASSET,
                drcr_direction=DCRDirection.DEBIT,
                currency="XYZ",
            )

    def test_account_type_grouping(self):
        asset = ChartOfAccounts(code="1", name="TS", account_type=AccountType.ASSET, drcr_direction=DCRDirection.DEBIT)
        assert asset.get_account_type_group() == "assets"

        liability = ChartOfAccounts(code="2", name="NP", account_type=AccountType.LIABILITY, drcr_direction=DCRDirection.CREDIT)
        assert liability.get_account_type_group() == "liabilities"

        revenue = ChartOfAccounts(code="4", name="DT", account_type=AccountType.REVENUE, drcr_direction=DCRDirection.CREDIT)
        assert revenue.get_account_type_group() == "revenue"

        expense = ChartOfAccounts(code="5", name="CP", account_type=AccountType.EXPENSE, drcr_direction=DCRDirection.DEBIT)
        assert expense.get_account_type_group() == "expenses"


class TestAccountingRegime:
    def test_tt99_is_default(self):
        acc = ChartOfAccounts(
            code="1", name="Test",
            account_type=AccountType.ASSET,
            drcr_direction=DCRDirection.DEBIT,
        )
        assert acc.regime == AccountingRegime.TT99_2025

    def test_regime_values(self):
        values = [e.value for e in AccountingRegime]
        assert "tt99_2025" in values
        assert "tt133_2016" in values


class TestAccountStatus:
    def test_status_values(self):
        values = [e.value for e in AccountStatus]
        assert "active" in values
        assert "suspended" in values
        assert "closed" in values


class TestDCRDirection:
    def test_debit_normal_accounts(self):
        asset = ChartOfAccounts(code="1", name="TS", account_type=AccountType.ASSET, drcr_direction=DCRDirection.DEBIT)
        assert asset.drcr_direction == DCRDirection.DEBIT

        cash = ChartOfAccounts(code="1.1", name="TM", account_type=AccountType.CASH, drcr_direction=DCRDirection.DEBIT)
        assert cash.drcr_direction == DCRDirection.DEBIT

    def test_credit_normal_accounts(self):
        liability = ChartOfAccounts(code="2", name="NP", account_type=AccountType.LIABILITY, drcr_direction=DCRDirection.CREDIT)
        assert liability.drcr_direction == DCRDirection.CREDIT
