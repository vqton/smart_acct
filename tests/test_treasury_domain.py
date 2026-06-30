from decimal import Decimal
from datetime import date, datetime
import pytest

from domain.treasury import (
    InvestmentType, InvestmentStatus, LoanType, LoanStatus,
    ForecastHorizon, ScenarioType, FXRateSource, SweepType,
    ICSweepStatus, BatchStatus, BatchItemStatus, SyncStatus,
    FXForwardStatus, ICInterestBasis, TreasuryKPI,
    CashInTransit, SecurityInvestment, InvestmentTransaction,
    Loan, LoanPayment, FXForward, CashFlowForecast, ForecastLine,
    TreasuryPosition, FXExposure, FXRate, IntercompanyLoan,
    IntercompanySweep, PaymentBatch, PaymentBatchItem,
    BankConnectorConfig, BankSyncLog, TreasuryPolicy, TreasuryAuditLog,
)


class TestEnums:
    def test_investment_type_values(self):
        assert InvestmentType.TRADING_SECURITY.value == "trading_security"
        assert InvestmentType.TERM_DEPOSIT.value == "term_deposit"
        assert InvestmentType.BOND.value == "bond"
        assert InvestmentType.LOAN_RECEIVABLE.value == "loan_receivable"
        assert InvestmentType.OTHER_HTM.value == "other_htm"

    def test_investment_status_values(self):
        assert InvestmentStatus.ACTIVE.value == "active"
        assert InvestmentStatus.MATURED.value == "matured"
        assert InvestmentStatus.EARLY_WITHDRAWN.value == "early_withdrawn"
        assert InvestmentStatus.SOLD.value == "sold"
        assert InvestmentStatus.IMPAIRED.value == "impaired"

    def test_loan_type_values(self):
        assert LoanType.BANK_LOAN.value == "bank_loan"
        assert LoanType.BOND_PAYABLE.value == "bond_payable"
        assert LoanType.INTERCOMPANY_LOAN.value == "intercompany_loan"

    def test_loan_status_values(self):
        assert LoanStatus.ACTIVE.value == "active"
        assert LoanStatus.FULLY_PAID.value == "fully_paid"
        assert LoanStatus.DEFAULTED.value == "defaulted"
        assert LoanStatus.REFINANCED.value == "refinanced"

    def test_forecast_horizon_values(self):
        assert ForecastHorizon.DAY_7.value == "7d"
        assert ForecastHorizon.DAY_30.value == "30d"
        assert ForecastHorizon.DAY_90.value == "90d"
        assert ForecastHorizon.ANNUAL.value == "annual"

    def test_scenario_type_values(self):
        assert ScenarioType.BEST.value == "best"
        assert ScenarioType.BASE.value == "base"
        assert ScenarioType.WORST.value == "worst"

    def test_fx_rate_source_values(self):
        assert FXRateSource.SBV.value == "sbv"
        assert FXRateSource.BANK_AVG.value == "bank_avg"
        assert FXRateSource.INTERBANK.value == "interbank"

    def test_sweep_type_values(self):
        assert SweepType.ZERO_BALANCING.value == "zero_balancing"
        assert SweepType.TARGET_BALANCING.value == "target_balancing"

    def test_ic_sweep_status_values(self):
        assert ICSweepStatus.PENDING.value == "pending"
        assert ICSweepStatus.APPROVED.value == "approved"
        assert ICSweepStatus.EXECUTED.value == "executed"
        assert ICSweepStatus.REVERSED.value == "reversed"

    def test_batch_status_transitions(self):
        assert BatchStatus.DRAFT.value == "draft"
        assert BatchStatus.REVIEWED.value == "reviewed"
        assert BatchStatus.APPROVED.value == "approved"
        assert BatchStatus.SUBMITTED.value == "submitted"
        assert BatchStatus.PARTIALLY_EXECUTED.value == "partially_executed"
        assert BatchStatus.EXECUTED.value == "executed"

    def test_batch_item_status_values(self):
        assert BatchItemStatus.PENDING.value == "pending"
        assert BatchItemStatus.SUBMITTED.value == "submitted"
        assert BatchItemStatus.CONFIRMED.value == "confirmed"
        assert BatchItemStatus.REJECTED.value == "rejected"

    def test_sync_status_values(self):
        assert SyncStatus.SUCCESS.value == "success"
        assert SyncStatus.PARTIAL.value == "partial"
        assert SyncStatus.FAILED.value == "failed"

    def test_fx_forward_status_values(self):
        assert FXForwardStatus.OPEN.value == "open"
        assert FXForwardStatus.SETTLED.value == "settled"
        assert FXForwardStatus.CANCELLED.value == "cancelled"

    def test_ic_interest_basis_values(self):
        assert ICInterestBasis.ACTUAL_365.value == "actual/365"
        assert ICInterestBasis.ACTUAL_360.value == "actual/360"
        assert ICInterestBasis.THIRTY_360.value == "30/360"

    def test_treasury_kpi_values(self):
        assert TreasuryKPI.DAYS_CASH_ON_HAND.value == "days_cash_on_hand"
        assert TreasuryKPI.CASH_CONVERSION_CYCLE.value == "cash_conversion_cycle"
        assert TreasuryKPI.CURRENT_RATIO.value == "current_ratio"
        assert TreasuryKPI.QUICK_RATIO.value == "quick_ratio"
        assert TreasuryKPI.DSO.value == "dso"
        assert TreasuryKPI.DPO.value == "dpo"
        assert TreasuryKPI.LIQUIDITY_COVERAGE.value == "liquidity_coverage"
        assert TreasuryKPI.FX_EXPOSURE.value == "fx_exposure"
        assert TreasuryKPI.INVESTMENT_YIELD.value == "investment_yield"
        assert TreasuryKPI.DEBT_SERVICE_COVERAGE.value == "debt_service_coverage"
        assert TreasuryKPI.FORECAST_ACCURACY.value == "forecast_accuracy"


class TestCashInTransit:
    def test_create(self):
        t = CashInTransit(
            reference="TRF001", amount=Decimal("5000000"),
            source_account_type="bank", source_account_id=1,
            dest_account_type="petty_cash", dest_account_id=2,
            transfer_date=date(2026, 6, 1),
            expected_clear_date=date(2026, 6, 2),
        )
        assert t.reference == "TRF001"
        assert t.currency == "VND"
        assert t.cleared is False
        assert t.cleared_at is None

    def test_amount_quantized(self):
        t = CashInTransit(
            reference="TRF002", amount=Decimal("5000.123"),
            source_account_type="bank", source_account_id=1,
            dest_account_type="cash", dest_account_id=2,
            transfer_date=date(2026, 6, 1),
            expected_clear_date=date(2026, 6, 2),
        )
        assert t.amount == Decimal("5000.12")

    def test_cleared_default(self):
        t = CashInTransit(
            reference="TRF003", amount=Decimal("1000000"),
            source_account_type="bank", source_account_id=1,
            dest_account_type="bank", dest_account_id=2,
            transfer_date=date(2026, 6, 1),
            expected_clear_date=date(2026, 6, 2),
        )
        assert t.cleared is False

    def test_cleared_true(self):
        t = CashInTransit(
            reference="TRF004", amount=Decimal("2000000"),
            source_account_type="bank", source_account_id=1,
            dest_account_type="bank", dest_account_id=2,
            transfer_date=date(2026, 6, 1),
            expected_clear_date=date(2026, 6, 2),
            cleared=True,
            cleared_at=datetime(2026, 6, 2, 10, 0, 0),
        )
        assert t.cleared is True
        assert t.cleared_at is not None


class TestSecurityInvestment:
    def test_create(self):
        s = SecurityInvestment(
            investment_code="INV001",
            investment_name="Government Bond 2026",
            cost_price=Decimal("100000000"),
            total_cost=Decimal("100000000"),
            purchase_date=date(2026, 1, 1),
            coa_code="2281",
        )
        assert s.investment_type == InvestmentType.TRADING_SECURITY
        assert s.status == InvestmentStatus.ACTIVE
        assert s.coa_income_code == "515"
        assert s.coa_expense_code == "635"

    def test_code_required(self):
        with pytest.raises(ValueError):
            SecurityInvestment(
                investment_code="",
                investment_name="Test",
                cost_price=Decimal("1000"),
                total_cost=Decimal("1000"),
                purchase_date=date(2026, 1, 1),
                coa_code="2281",
            )

    def test_amount_quantized(self):
        s = SecurityInvestment(
            investment_code="INV002",
            investment_name="Corporate Bond",
            cost_price=Decimal("50000.456"),
            total_cost=Decimal("50000.456"),
            purchase_date=date(2026, 2, 1),
            coa_code="2281",
        )
        assert s.cost_price == Decimal("50000.46")
        assert s.total_cost == Decimal("50000.46")

    def test_default_coa_codes(self):
        s = SecurityInvestment(
            investment_code="INV003",
            investment_name="Test Investment",
            cost_price=Decimal("1000000"),
            total_cost=Decimal("1000000"),
            purchase_date=date(2026, 3, 1),
            coa_code="2281",
        )
        assert s.coa_income_code == "515"
        assert s.coa_expense_code == "635"

    def test_with_market_price(self):
        s = SecurityInvestment(
            investment_code="INV004",
            investment_name="Equity Holding",
            cost_price=Decimal("100000000"),
            total_cost=Decimal("100000000"),
            market_price=Decimal("110000000"),
            fair_value=Decimal("110000000"),
            purchase_date=date(2026, 1, 1),
            coa_code="2281",
        )
        assert s.market_price == Decimal("110000000.00")
        assert s.fair_value == Decimal("110000000.00")


class TestInvestmentTransaction:
    def test_create(self):
        t = InvestmentTransaction(
            investment_id=1,
            transaction_type="buy",
            transaction_date=date(2026, 1, 15),
            price=Decimal("95000"),
            total_amount=Decimal("95000000"),
        )
        assert t.fee == Decimal("0")
        assert t.quantity is None
        assert t.gain_loss is None

    def test_fee_default(self):
        t = InvestmentTransaction(
            investment_id=1,
            transaction_type="sell",
            transaction_date=date(2026, 6, 1),
            price=Decimal("100000"),
            total_amount=Decimal("100000000"),
        )
        assert t.fee == Decimal("0.00")

    def test_with_fee_and_gain(self):
        t = InvestmentTransaction(
            investment_id=1,
            transaction_type="sell",
            transaction_date=date(2026, 6, 1),
            quantity=Decimal("100"),
            price=Decimal("100000"),
            total_amount=Decimal("10000000"),
            fee=Decimal("50000"),
            gain_loss=Decimal("500000"),
        )
        assert t.fee == Decimal("50000.00")
        assert t.gain_loss == Decimal("500000.00")

    def test_amounts_quantized(self):
        t = InvestmentTransaction(
            investment_id=1,
            transaction_type="buy",
            transaction_date=date(2026, 1, 15),
            price=Decimal("95000.456"),
            total_amount=Decimal("95000000.789"),
        )
        assert t.price == Decimal("95000.46")
        assert t.total_amount == Decimal("95000000.79")


class TestLoan:
    def test_create(self):
        l = Loan(
            loan_code="LN001", loan_name="Bank Loan 2026",
            principal=Decimal("5000000000"),
            outstanding_balance=Decimal("5000000000"),
            interest_rate=Decimal("8.5"),
            drawdown_date=date(2026, 1, 1),
            maturity_date=date(2031, 1, 1),
        )
        assert l.loan_type == LoanType.BANK_LOAN
        assert l.status == LoanStatus.ACTIVE
        assert l.coa_code == "341"
        assert l.coa_interest_code == "635"
        assert l.interest_basis == ICInterestBasis.ACTUAL_365
        assert l.repayment_frequency == "monthly"
        assert l.repayment_day == 1

    def test_code_required(self):
        with pytest.raises(ValueError):
            Loan(
                loan_code="", loan_name="Test",
                principal=Decimal("1000000"),
                outstanding_balance=Decimal("1000000"),
                interest_rate=Decimal("5"),
                drawdown_date=date(2026, 1, 1),
                maturity_date=date(2027, 1, 1),
            )

    def test_default_coa_code(self):
        l = Loan(
            loan_code="LN002", loan_name="Bond Payable",
            loan_type=LoanType.BOND_PAYABLE,
            principal=Decimal("10000000000"),
            outstanding_balance=Decimal("10000000000"),
            interest_rate=Decimal("7.5"),
            drawdown_date=date(2026, 3, 1),
            maturity_date=date(2031, 3, 1),
        )
        assert l.coa_code == "341"
        assert l.coa_interest_code == "635"

    def test_outstanding_balance_defaults(self):
        l = Loan(
            loan_code="LN003", loan_name="Test Loan",
            principal=Decimal("100000000"),
            outstanding_balance=Decimal("100000000"),
            interest_rate=Decimal("6"),
            drawdown_date=date(2026, 5, 1),
            maturity_date=date(2028, 5, 1),
        )
        assert l.outstanding_balance == Decimal("100000000.00")
        assert l.principal == Decimal("100000000.00")

    def test_amounts_quantized(self):
        l = Loan(
            loan_code="LN004", loan_name="Quantized",
            principal=Decimal("1000.456"),
            outstanding_balance=Decimal("1000.456"),
            interest_rate=Decimal("8.1234"),
            drawdown_date=date(2026, 1, 1),
            maturity_date=date(2027, 1, 1),
        )
        assert l.principal == Decimal("1000.46")
        assert l.outstanding_balance == Decimal("1000.46")
        assert l.interest_rate == Decimal("8.12")


class TestLoanPayment:
    def test_create(self):
        p = LoanPayment(
            loan_id=1,
            payment_date=date(2026, 2, 1),
            principal_amount=Decimal("50000000"),
            interest_amount=Decimal("3541667"),
            total_amount=Decimal("53541667"),
        )
        assert p.is_scheduled is True
        assert p.is_early_repayment is False
        assert p.early_repayment_penalty == Decimal("0")
        assert p.status == "pending"

    def test_early_repayment_default(self):
        p = LoanPayment(
            loan_id=1,
            payment_date=date(2026, 3, 1),
            principal_amount=Decimal("100000000"),
            interest_amount=Decimal("5000000"),
            total_amount=Decimal("105000000"),
            is_early_repayment=True,
            early_repayment_penalty=Decimal("1000000"),
        )
        assert p.is_early_repayment is True
        assert p.early_repayment_penalty == Decimal("1000000.00")

    def test_amounts_quantized(self):
        p = LoanPayment(
            loan_id=1,
            payment_date=date(2026, 2, 1),
            principal_amount=Decimal("50000.456"),
            interest_amount=Decimal("3541.678"),
            total_amount=Decimal("53542.134"),
        )
        assert p.principal_amount == Decimal("50000.46")
        assert p.interest_amount == Decimal("3541.68")
        assert p.total_amount == Decimal("53542.13")


class TestFXForward:
    def test_create(self):
        f = FXForward(
            contract_number="FWD001",
            target_currency="USD",
            amount=Decimal("100000"),
            forward_rate=Decimal("25400"),
            value_date=date(2026, 7, 1),
            maturity_date=date(2026, 9, 1),
            counterparty="Vietcombank",
        )
        assert f.base_currency == "VND"
        assert f.status == FXForwardStatus.OPEN
        assert f.settlement_amount is None

    def test_default_status(self):
        f = FXForward(
            contract_number="FWD002",
            target_currency="EUR",
            amount=Decimal("50000"),
            forward_rate=Decimal("27500"),
            value_date=date(2026, 8, 1),
            maturity_date=date(2026, 10, 1),
            counterparty="Techcombank",
        )
        assert f.status == FXForwardStatus.OPEN

    def test_contract_required(self):
        with pytest.raises(ValueError):
            FXForward(
                target_currency="USD",
                amount=Decimal("1000"),
                forward_rate=Decimal("25000"),
                value_date=date(2026, 1, 1),
                maturity_date=date(2026, 3, 1),
                counterparty="Bank",
            )

    def test_settled_status(self):
        f = FXForward(
            contract_number="FWD003",
            target_currency="JPY",
            amount=Decimal("10000000"),
            forward_rate=Decimal("170"),
            value_date=date(2026, 5, 1),
            maturity_date=date(2026, 7, 1),
            counterparty="BIDV",
            status=FXForwardStatus.SETTLED,
            settlement_amount=Decimal("1050000000"),
        )
        assert f.status == FXForwardStatus.SETTLED
        assert f.settlement_amount == Decimal("1050000000.00")

    def test_amounts_quantized(self):
        f = FXForward(
            contract_number="FWD004",
            target_currency="USD",
            amount=Decimal("1000.456"),
            forward_rate=Decimal("25400.789"),
            value_date=date(2026, 6, 1),
            maturity_date=date(2026, 8, 1),
            counterparty="Bank",
        )
        assert f.amount == Decimal("1000.46")
        assert f.forward_rate == Decimal("25400.79")


class TestCashFlowForecast:
    def test_create(self):
        f = CashFlowForecast(
            forecast_name="Jun 2026 Forecast",
            opening_balance=Decimal("50000000"),
            closing_balance=Decimal("45000000"),
            forecast_date=date(2026, 6, 1),
        )
        assert f.horizon == ForecastHorizon.DAY_30
        assert f.scenario == ScenarioType.BASE
        assert f.total_inflows == Decimal("0")
        assert f.total_outflows == Decimal("0")
        assert f.min_balance_breach is False
        assert f.surplus_identified is False

    def test_default_horizon(self):
        f = CashFlowForecast(
            forecast_name="Weekly Forecast",
            opening_balance=Decimal("10000000"),
            closing_balance=Decimal("8000000"),
            forecast_date=date(2026, 6, 7),
        )
        assert f.horizon == ForecastHorizon.DAY_30

    def test_min_balance_breach_default(self):
        f = CashFlowForecast(
            forecast_name="Test Forecast",
            opening_balance=Decimal("20000000"),
            closing_balance=Decimal("15000000"),
            forecast_date=date(2026, 6, 15),
        )
        assert f.min_balance_breach is False

    def test_with_inflows_outflows(self):
        f = CashFlowForecast(
            forecast_name="Detailed Forecast",
            horizon=ForecastHorizon.DAY_90,
            scenario=ScenarioType.WORST,
            opening_balance=Decimal("50000000"),
            total_inflows=Decimal("100000000"),
            total_outflows=Decimal("120000000"),
            closing_balance=Decimal("30000000"),
            min_balance_threshold=Decimal("10000000"),
            min_balance_breach=False,
            forecast_date=date(2026, 6, 1),
            period="2026-Q2",
        )
        assert f.horizon == ForecastHorizon.DAY_90
        assert f.scenario == ScenarioType.WORST
        assert f.total_inflows == Decimal("100000000.00")

    def test_amounts_quantized(self):
        f = CashFlowForecast(
            forecast_name="Quantized Test",
            opening_balance=Decimal("50000.456"),
            closing_balance=Decimal("45000.789"),
            forecast_date=date(2026, 6, 1),
        )
        assert f.opening_balance == Decimal("50000.46")
        assert f.closing_balance == Decimal("45000.79")


class TestForecastLine:
    def test_create(self):
        l = ForecastLine(
            forecast_id=1,
            line_type="inflow",
            description="Customer payment",
            expected_amount=Decimal("50000000"),
            expected_date=date(2026, 6, 15),
        )
        assert l.confidence_pct == 80
        assert l.is_manual is False
        assert l.source_module is None

    def test_confidence_default(self):
        l = ForecastLine(
            forecast_id=1,
            line_type="outflow",
            description="Supplier payment",
            expected_amount=Decimal("30000000"),
            expected_date=date(2026, 6, 20),
        )
        assert l.confidence_pct == 80

    def test_confidence_range(self):
        l = ForecastLine(
            forecast_id=1,
            line_type="inflow",
            description="High confidence",
            expected_amount=Decimal("10000000"),
            expected_date=date(2026, 6, 10),
            confidence_pct=95,
            is_manual=True,
        )
        assert l.confidence_pct == 95
        assert l.is_manual is True

    def test_amount_quantized(self):
        l = ForecastLine(
            forecast_id=1,
            line_type="outflow",
            description="Test",
            expected_amount=Decimal("5000.456"),
            expected_date=date(2026, 6, 5),
        )
        assert l.expected_amount == Decimal("5000.46")


class TestTreasuryPosition:
    def test_create(self):
        p = TreasuryPosition(
            snapshot_date=date(2026, 6, 1),
            total_cash=Decimal("10000000"),
            total_bank=Decimal("50000000"),
            total_available=Decimal("60000000"),
            net_liquidity=Decimal("60000000"),
        )
        assert p.currency == "VND"
        assert p.total_cash_in_transit == Decimal("0")
        assert p.total_blocked == Decimal("0")
        assert p.total_investments == Decimal("0")
        assert p.total_loans == Decimal("0")
        assert p.entity_id is None

    def test_net_liquidity_default(self):
        p = TreasuryPosition(
            snapshot_date=date(2026, 6, 1),
            total_cash=Decimal("20000000"),
            total_bank=Decimal("80000000"),
            total_available=Decimal("100000000"),
            net_liquidity=Decimal("100000000"),
        )
        assert p.net_liquidity == Decimal("100000000.00")

    def test_with_investments_and_loans(self):
        p = TreasuryPosition(
            snapshot_date=date(2026, 6, 1),
            total_cash=Decimal("10000000"),
            total_bank=Decimal("50000000"),
            total_cash_in_transit=Decimal("5000000"),
            total_blocked=Decimal("2000000"),
            total_available=Decimal("53000000"),
            total_investments=Decimal("200000000"),
            total_loans=Decimal("500000000"),
            net_liquidity=Decimal("-447000000"),
            entity_id="VN-001",
        )
        assert p.total_cash_in_transit == Decimal("5000000.00")
        assert p.total_investments == Decimal("200000000.00")
        assert p.entity_id == "VN-001"

    def test_amounts_quantized(self):
        p = TreasuryPosition(
            snapshot_date=date(2026, 6, 1),
            total_cash=Decimal("10000.456"),
            total_bank=Decimal("50000.789"),
            total_available=Decimal("60001.245"),
            net_liquidity=Decimal("60001.245"),
        )
        assert p.total_cash == Decimal("10000.46")
        assert p.total_bank == Decimal("50000.79")
        assert p.total_available == Decimal("60001.24")
        assert p.net_liquidity == Decimal("60001.24")


class TestFXExposure:
    def test_create(self):
        e = FXExposure(
            snapshot_date=date(2026, 6, 1),
            currency="USD",
            total_long=Decimal("500000"),
            total_short=Decimal("200000"),
            net_exposure=Decimal("300000"),
            vnd_equivalent=Decimal("7620000000"),
            exchange_rate=Decimal("25400"),
        )
        assert e.rate_source == FXRateSource.BANK_AVG
        assert e.unrealized_gain_loss == Decimal("0")
        assert e.threshold_breached is False
        assert e.entity_id is None

    def test_threshold_breach_default(self):
        e = FXExposure(
            snapshot_date=date(2026, 6, 1),
            currency="EUR",
            total_long=Decimal("100000"),
            total_short=Decimal("50000"),
            net_exposure=Decimal("50000"),
            vnd_equivalent=Decimal("1375000000"),
            exchange_rate=Decimal("27500"),
        )
        assert e.threshold_breached is False

    def test_with_breach_and_limit(self):
        e = FXExposure(
            snapshot_date=date(2026, 6, 1),
            currency="USD",
            total_long=Decimal("1000000"),
            total_short=Decimal("100000"),
            net_exposure=Decimal("900000"),
            vnd_equivalent=Decimal("22860000000"),
            exchange_rate=Decimal("25400"),
            rate_source=FXRateSource.SBV,
            unrealized_gain_loss=Decimal("50000000"),
            policy_limit=Decimal("500000"),
            threshold_breached=True,
        )
        assert e.rate_source == FXRateSource.SBV
        assert e.threshold_breached is True
        assert e.policy_limit == Decimal("500000.00")

    def test_amounts_quantized(self):
        e = FXExposure(
            snapshot_date=date(2026, 6, 1),
            currency="JPY",
            total_long=Decimal("1000.456"),
            total_short=Decimal("200.789"),
            net_exposure=Decimal("799.667"),
            vnd_equivalent=Decimal("135943.39"),
            exchange_rate=Decimal("170.1234"),
        )
        assert e.total_long == Decimal("1000.46")
        assert e.net_exposure == Decimal("799.67")
        assert e.exchange_rate == Decimal("170.12")


class TestFXRate:
    def test_create(self):
        r = FXRate(
            currency="USD",
            rate_date=date(2026, 6, 1),
            rate_avg=Decimal("25400"),
        )
        assert r.rate_source == FXRateSource.BANK_AVG
        assert r.rate_buying is None
        assert r.rate_selling is None

    def test_unique_rate(self):
        r = FXRate(
            currency="EUR",
            rate_date=date(2026, 6, 1),
            rate_buying=Decimal("27400"),
            rate_selling=Decimal("27600"),
            rate_avg=Decimal("27500"),
            rate_source=FXRateSource.INTERBANK,
        )
        assert r.rate_buying == Decimal("27400.00")
        assert r.rate_selling == Decimal("27600.00")
        assert r.rate_avg == Decimal("27500.00")
        assert r.rate_source == FXRateSource.INTERBANK

    def test_amounts_quantized(self):
        r = FXRate(
            currency="USD",
            rate_date=date(2026, 6, 1),
            rate_avg=Decimal("25400.456"),
        )
        assert r.rate_avg == Decimal("25400.46")


class TestIntercompanyLoan:
    def test_create(self):
        l = IntercompanyLoan(
            loan_code="ICL001",
            lender_entity_id="VN-HQ",
            borrower_entity_id="VN-HCM",
            principal=Decimal("500000000"),
            outstanding_balance=Decimal("500000000"),
            interest_rate=Decimal("5"),
            start_date=date(2026, 1, 1),
            maturity_date=date(2027, 1, 1),
        )
        assert l.currency == "VND"
        assert l.status == "active"
        assert l.coa_receivable_code == "1368"
        assert l.coa_payable_code == "3368"
        assert l.transfer_pricing_compliant is True
        assert l.interest_basis == ICInterestBasis.ACTUAL_365

    def test_default_coa_codes(self):
        l = IntercompanyLoan(
            loan_code="ICL002",
            lender_entity_id="VN-HN",
            borrower_entity_id="VN-DN",
            principal=Decimal("200000000"),
            outstanding_balance=Decimal("200000000"),
            interest_rate=Decimal("4.5"),
            start_date=date(2026, 3, 1),
            maturity_date=date(2028, 3, 1),
        )
        assert l.coa_receivable_code == "1368"
        assert l.coa_payable_code == "3368"

    def test_transfer_pricing_default(self):
        l = IntercompanyLoan(
            loan_code="ICL003",
            lender_entity_id="VN-HQ",
            borrower_entity_id="VN-HCM",
            principal=Decimal("100000000"),
            outstanding_balance=Decimal("100000000"),
            interest_rate=Decimal("5"),
            start_date=date(2026, 6, 1),
            maturity_date=date(2027, 6, 1),
        )
        assert l.transfer_pricing_compliant is True

    def test_transfer_pricing_disabled(self):
        l = IntercompanyLoan(
            loan_code="ICL004",
            lender_entity_id="VN-HQ",
            borrower_entity_id="VN-HCM",
            principal=Decimal("100000000"),
            outstanding_balance=Decimal("100000000"),
            interest_rate=Decimal("3"),
            start_date=date(2026, 6, 1),
            maturity_date=date(2027, 6, 1),
            transfer_pricing_compliant=False,
        )
        assert l.transfer_pricing_compliant is False

    def test_amounts_quantized(self):
        l = IntercompanyLoan(
            loan_code="ICL005",
            lender_entity_id="A", borrower_entity_id="B",
            principal=Decimal("1000.456"),
            outstanding_balance=Decimal("1000.456"),
            interest_rate=Decimal("5.6789"),
            start_date=date(2026, 1, 1),
            maturity_date=date(2027, 1, 1),
        )
        assert l.principal == Decimal("1000.46")
        assert l.outstanding_balance == Decimal("1000.46")
        assert l.interest_rate == Decimal("5.68")


class TestIntercompanySweep:
    def test_create(self):
        s = IntercompanySweep(
            sweep_date=date(2026, 6, 1),
            source_entity_id="VN-HQ",
            target_entity_id="VN-HCM",
            amount=Decimal("50000000"),
            source_acct_id=1,
            target_acct_id=2,
        )
        assert s.sweep_type == SweepType.ZERO_BALANCING
        assert s.status == ICSweepStatus.PENDING
        assert s.source_acct_type == "bank"
        assert s.target_acct_type == "bank"
        assert s.ic_loan_id is None

    def test_default_sweep_type(self):
        s = IntercompanySweep(
            sweep_date=date(2026, 6, 1),
            source_entity_id="VN-HN",
            target_entity_id="VN-DN",
            amount=Decimal("10000000"),
            source_acct_id=1,
            target_acct_id=2,
        )
        assert s.sweep_type == SweepType.ZERO_BALANCING

    def test_target_balancing(self):
        s = IntercompanySweep(
            sweep_type=SweepType.TARGET_BALANCING,
            status=ICSweepStatus.APPROVED,
            sweep_date=date(2026, 6, 15),
            source_entity_id="VN-HQ",
            target_entity_id="VN-HCM",
            amount=Decimal("75000000"),
            source_acct_id=1,
            target_acct_id=2,
            target_balance_after=Decimal("100000000"),
            approved_by="Manager",
        )
        assert s.sweep_type == SweepType.TARGET_BALANCING
        assert s.status == ICSweepStatus.APPROVED
        assert s.target_balance_after == Decimal("100000000.00")
        assert s.approved_by == "Manager"


class TestPaymentBatch:
    def test_create(self):
        b = PaymentBatch(
            batch_code="BATCH001",
            payment_date=date(2026, 6, 15),
            total_amount=Decimal("50000000"),
        )
        assert b.status == BatchStatus.DRAFT
        assert b.item_count == 0
        assert b.currency == "VND"
        assert b.approved_by is None

    def test_default_status(self):
        b = PaymentBatch(
            batch_code="BATCH002",
            payment_date=date(2026, 6, 20),
            total_amount=Decimal("100000000"),
        )
        assert b.status == BatchStatus.DRAFT

    def test_item_count_default(self):
        b = PaymentBatch(
            batch_code="BATCH003",
            payment_date=date(2026, 6, 25),
            total_amount=Decimal("75000000"),
        )
        assert b.item_count == 0

    def test_approved_status(self):
        b = PaymentBatch(
            batch_code="BATCH004",
            status=BatchStatus.APPROVED,
            payment_date=date(2026, 6, 10),
            total_amount=Decimal("20000000"),
            item_count=5,
            approved_by="NV001",
        )
        assert b.status == BatchStatus.APPROVED
        assert b.item_count == 5
        assert b.approved_by == "NV001"

    def test_amount_quantized(self):
        b = PaymentBatch(
            batch_code="BATCH005",
            payment_date=date(2026, 6, 30),
            total_amount=Decimal("50000.456"),
        )
        assert b.total_amount == Decimal("50000.46")


class TestPaymentBatchItem:
    def test_create(self):
        i = PaymentBatchItem(
            batch_id=1,
            source_module="ap",
            source_id=100,
            source_reference="INV-2026-001",
            payee_name="Cong ty TNHH ABC",
            amount=Decimal("10000000"),
        )
        assert i.status == BatchItemStatus.PENDING
        assert i.currency == "VND"
        assert i.payee_account is None
        assert i.bank_txn_ref is None

    def test_default_status(self):
        i = PaymentBatchItem(
            batch_id=1,
            source_module="ap",
            source_id=101,
            source_reference="INV-2026-002",
            payee_name="Cong ty XYZ",
            amount=Decimal("5000000"),
        )
        assert i.status == BatchItemStatus.PENDING

    def test_confirmed_status(self):
        i = PaymentBatchItem(
            batch_id=1,
            source_module="payroll",
            source_id=200,
            source_reference="PR-2026-06",
            payee_name="Nhan vien A",
            amount=Decimal("15000000"),
            status=BatchItemStatus.CONFIRMED,
            bank_txn_ref="BIDV123456",
        )
        assert i.status == BatchItemStatus.CONFIRMED
        assert i.bank_txn_ref == "BIDV123456"

    def test_amount_quantized(self):
        i = PaymentBatchItem(
            batch_id=1,
            source_module="ap",
            source_id=102,
            source_reference="INV-2026-003",
            payee_name="Test",
            amount=Decimal("5000.456"),
        )
        assert i.amount == Decimal("5000.46")


class TestBankConnectorConfig:
    def test_create(self):
        c = BankConnectorConfig(
            bank_code="BIDV",
            bank_name="Bank for Investment and Development",
        )
        assert c.auth_type == "api_key"
        assert c.sync_frequency_minutes == 60
        assert c.is_active is True
        assert c.supports_balance is True
        assert c.supports_transactions is True
        assert c.supports_statements is True

    def test_default_sync_frequency(self):
        c = BankConnectorConfig(
            bank_code="VCB",
            bank_name="Vietcombank",
        )
        assert c.sync_frequency_minutes == 60

    def test_custom_sync_frequency(self):
        c = BankConnectorConfig(
            bank_code="TCB",
            bank_name="Techcombank",
            sync_frequency_minutes=30,
            is_active=False,
            supports_statements=False,
        )
        assert c.sync_frequency_minutes == 30
        assert c.is_active is False
        assert c.supports_statements is False


class TestBankSyncLog:
    def test_create(self):
        l = BankSyncLog(
            connector_id=1,
            sync_type="balance",
            sync_status=SyncStatus.SUCCESS,
            started_at=datetime(2026, 6, 1, 8, 0, 0),
        )
        assert l.transactions_fetched == 0
        assert l.transactions_matched == 0
        assert l.transactions_unmatched == 0
        assert l.completed_at is None

    def test_transaction_counts_default(self):
        l = BankSyncLog(
            connector_id=1,
            sync_type="transactions",
            sync_status=SyncStatus.SUCCESS,
            started_at=datetime(2026, 6, 1, 9, 0, 0),
            completed_at=datetime(2026, 6, 1, 9, 0, 30),
        )
        assert l.transactions_fetched == 0
        assert l.transactions_matched == 0
        assert l.transactions_unmatched == 0

    def test_with_counts(self):
        l = BankSyncLog(
            connector_id=1,
            sync_type="transactions",
            sync_status=SyncStatus.PARTIAL,
            started_at=datetime(2026, 6, 1, 10, 0, 0),
            completed_at=datetime(2026, 6, 1, 10, 1, 15),
            transactions_fetched=150,
            transactions_matched=120,
            transactions_unmatched=30,
            error_message="30 transactions could not be matched",
        )
        assert l.transactions_fetched == 150
        assert l.sync_status == SyncStatus.PARTIAL

    def test_failed_status(self):
        l = BankSyncLog(
            connector_id=1,
            sync_type="statement",
            sync_status=SyncStatus.FAILED,
            started_at=datetime(2026, 6, 1, 11, 0, 0),
            error_message="Connection timeout",
        )
        assert l.sync_status == SyncStatus.FAILED
        assert l.error_message == "Connection timeout"


class TestTreasuryPolicy:
    def test_create(self):
        p = TreasuryPolicy(
            policy_code="POL001",
            policy_name="Cash Concentration Limit",
            policy_type="cash_limit",
        )
        assert p.active is True
        assert p.threshold_value is None
        assert p.min_value is None
        assert p.max_value is None

    def test_active_default(self):
        p = TreasuryPolicy(
            policy_code="POL002",
            policy_name="FX Exposure Limit",
            policy_type="fx_limit",
        )
        assert p.active is True

    def test_inactive_policy(self):
        p = TreasuryPolicy(
            policy_code="POL003",
            policy_name="Old Policy",
            policy_type="investment",
            active=False,
        )
        assert p.active is False

    def test_with_thresholds(self):
        p = TreasuryPolicy(
            policy_code="POL004",
            policy_name="Counterparty Limit",
            policy_type="counterparty",
            threshold_value=Decimal("50000000000"),
            max_value=Decimal("100000000000"),
            counterparty_restriction="No single counterparty > 20%",
        )
        assert p.threshold_value == Decimal("50000000000.00")
        assert p.max_value == Decimal("100000000000.00")


class TestTreasuryAuditLog:
    def test_create(self):
        l = TreasuryAuditLog(
            entity_type="SecurityInvestment",
            entity_id=1,
            action="CREATE",
        )
        assert l.old_value is None
        assert l.new_value is None
        assert l.performed_by is None

    def test_log_created(self):
        l = TreasuryAuditLog(
            entity_type="Loan",
            entity_id=42,
            action="UPDATE",
            old_value='{"status": "active"}',
            new_value='{"status": "defaulted"}',
            performed_by="NV001",
            notes="Loan default triggered",
        )
        assert l.entity_type == "Loan"
        assert l.entity_id == 42
        assert l.action == "UPDATE"
        assert l.performed_by == "NV001"

    def test_delete_action(self):
        l = TreasuryAuditLog(
            entity_type="CashFlowForecast",
            entity_id=10,
            action="DELETE",
            old_value='{"forecast_name": "Test"}',
            performed_by="NV002",
        )
        assert l.action == "DELETE"
        assert l.new_value is None
