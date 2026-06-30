from decimal import Decimal
from datetime import date, datetime, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain.treasury import (
    CashInTransit, SecurityInvestment, InvestmentType, InvestmentStatus,
    InvestmentTransaction, Loan, LoanType, LoanStatus, LoanPayment,
    FXForward, CashFlowForecast, ForecastHorizon, ScenarioType,
    ForecastLine, TreasuryPosition, FXExposure, FXRate, FXRateSource,
    IntercompanyLoan, IntercompanySweep, SweepType, ICSweepStatus,
    PaymentBatch, PaymentBatchItem, BatchStatus,
    BankConnectorConfig, BankSyncLog, SyncStatus,
    TreasuryPolicy, TreasuryAuditLog, ICInterestBasis,
)
from infrastructure.models.coa_models import Base
from use_cases.treasury import TreasuryUseCases

from infrastructure.models.treasury_models import (
    CashInTransitModel, SecurityInvestmentModel, InvestmentTransactionModel,
    LoanModel, LoanPaymentModel, FXForwardModel,
    CashFlowForecastModel, ForecastLineModel,
    TreasuryPositionModel, FXExposureModel, FXRateModel,
    IntercompanyLoanModel, IntercompanySweepModel,
    PaymentBatchModel, PaymentBatchItemModel,
    BankConnectorConfigModel, BankSyncLogModel,
    TreasuryPolicyModel, TreasuryAuditLogModel,
)
from infrastructure.models.cash_models import (
    CashReceiptModel, CashPaymentModel, PettyCashFundModel, BankAccountModel,
)
from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def uc(session):
    return TreasuryUseCases(session)


def _create_forecast(uc, name="FCST001", opening=Decimal("100000000"),
                     forecast_date=None, **kw):
    if forecast_date is None:
        forecast_date = date(2026, 7, 1)
    return uc.create_forecast(
        forecast_name=name,
        horizon=kw.get("horizon", ForecastHorizon.DAY_30),
        scenario=kw.get("scenario", ScenarioType.BASE),
        opening_balance=opening,
        forecast_date=forecast_date,
        min_balance_threshold=kw.get("min_balance_threshold"),
        surplus_threshold=kw.get("surplus_threshold"),
        currency=kw.get("currency", "VND"),
        period=kw.get("period", "2026-07"),
    )


def _create_investment(uc, code="INV001", name="Test Investment",
                       inv_type=InvestmentType.TERM_DEPOSIT,
                       cost=Decimal("500000000"), **kw):
    return uc.create_investment(
        investment_code=code,
        investment_name=name,
        investment_type=inv_type,
        cost_price=cost,
        total_cost=cost,
        purchase_date=kw.get("purchase_date", date(2026, 6, 1)),
        maturity_date=kw.get("maturity_date", date(2026, 12, 31)),
        quantity=kw.get("quantity"),
        market_price=kw.get("market_price"),
        counterparty_name=kw.get("counterparty_name", "BIDV"),
        counterparty_id=kw.get("counterparty_id", "BIDV001"),
        interest_rate=kw.get("interest_rate", Decimal("0.065")),
        coa_code=kw.get("coa_code", "121"),
        period=kw.get("period", "2026-07"),
    )


def _create_loan(uc, code="LN001", name="Test Loan",
                 principal=Decimal("1000000000"),
                 rate=Decimal("0.085"), **kw):
    return uc.create_loan(
        loan_code=code,
        loan_name=name,
        loan_type=kw.get("loan_type", LoanType.BANK_LOAN),
        principal=principal,
        interest_rate=rate,
        drawdown_date=kw.get("drawdown_date", date(2026, 6, 1)),
        maturity_date=kw.get("maturity_date", date(2028, 6, 1)),
        interest_basis=kw.get("interest_basis", ICInterestBasis.ACTUAL_365),
        repayment_frequency=kw.get("repayment_frequency", "monthly"),
        repayment_day=kw.get("repayment_day", 1),
        lender_name=kw.get("lender_name", "Vietcombank"),
        lender_id=kw.get("lender_id", "VCB001"),
        currency=kw.get("currency", "VND"),
        coa_code=kw.get("coa_code", "341"),
        covenant_dscr_min=kw.get("covenant_dscr_min"),
        covenant_icr_min=kw.get("covenant_icr_min"),
        covenant_ltv_max=kw.get("covenant_ltv_max"),
    )


# ── UC-TRS-01: Consolidated Cash Position ───────────────────────────

class TestConsolidatedCashPosition:
    def test_get_initial_position_empty(self, uc):
        """Returns a position even with no cash/bank data (zeros)."""
        result = uc.get_consolidated_cash_position()
        assert result.is_success()
        pos = result.get_data()
        assert pos.total_cash == Decimal("0.00")
        assert pos.total_bank == Decimal("0.00")
        assert pos.total_cash_in_transit == Decimal("0.00")
        assert pos.total_blocked == Decimal("0.00")
        assert pos.total_available == Decimal("0.00")
        assert pos.total_investments == Decimal("0.00")
        assert pos.total_loans == Decimal("0.00")
        assert pos.net_liquidity == Decimal("0.00")
        assert pos.snapshot_date == date.today()

    def test_get_position_after_setup(self, uc):
        """Position is saved and retrievable via history."""
        result = uc.get_consolidated_cash_position()
        assert result.is_success()
        pos = result.get_data()
        assert pos.id is not None
        hist = uc.get_position_history(days=1)
        assert hist.is_success()
        positions = hist.get_data()
        assert len(positions) >= 1


# ── UC-TRS-02: Cash Flow Forecasting ───────────────────────────────

class TestCashFlowForecasting:
    def test_create_forecast(self, uc):
        result = _create_forecast(uc)
        assert result.is_success()
        fc = result.get_data()
        assert fc.forecast_name == "FCST001"
        assert fc.horizon == ForecastHorizon.DAY_30
        assert fc.scenario == ScenarioType.BASE
        assert fc.opening_balance == Decimal("100000000.00")
        assert fc.closing_balance == Decimal("100000000.00")
        assert fc.min_balance_breach is False

    def test_create_forecast_with_thresholds(self, uc):
        result = _create_forecast(
            uc, name="FCST_THRESH",
            opening=Decimal("50000000"),
            min_balance_threshold=Decimal("10000000"),
            surplus_threshold=Decimal("100000000"),
        )
        assert result.is_success()
        fc = result.get_data()
        assert fc.min_balance_threshold == Decimal("10000000.00")
        assert fc.surplus_threshold == Decimal("100000000.00")

    def test_add_forecast_line(self, uc):
        fc = _create_forecast(uc, name="FCST_LINE")
        assert fc.is_success()
        fc_id = fc.get_data().id
        result = uc.add_forecast_line(
            forecast_id=fc_id,
            line_type="inflow",
            description="Customer payment",
            expected_amount=Decimal("20000000"),
            expected_date=date(2026, 7, 15),
        )
        assert result.is_success()
        line = result.get_data()
        assert line.forecast_id == fc_id
        assert line.expected_amount == Decimal("20000000.00")
        assert line.line_type == "inflow"

    def test_run_forecast_calculation_with_inflow(self, uc):
        fc = _create_forecast(uc, name="FCST_CALC", opening=Decimal("50000000"))
        fc_id = fc.get_data().id
        uc.add_forecast_line(fc_id, "inflow", "Payment received",
                             Decimal("30000000"), date(2026, 7, 10))
        result = uc.run_forecast_calculation(fc_id)
        assert result.is_success()
        data = result.get_data()
        assert data["opening_balance"] == Decimal("50000000.00")
        assert data["total_inflows"] == Decimal("30000000.00")
        assert data["total_outflows"] == Decimal("0.00")
        assert data["closing_balance"] == Decimal("80000000.00")
        assert data["min_balance_breach"] is False

    def test_run_forecast_calculation_with_outflow(self, uc):
        fc = _create_forecast(uc, name="FCST_OUT", opening=Decimal("50000000"))
        fc_id = fc.get_data().id
        uc.add_forecast_line(fc_id, "outflow", "Supplier payment",
                             Decimal("20000000"), date(2026, 7, 5))
        result = uc.run_forecast_calculation(fc_id)
        assert result.is_success()
        data = result.get_data()
        assert data["total_outflows"] == Decimal("20000000.00")
        assert data["closing_balance"] == Decimal("30000000.00")

    def test_run_forecast_calculation_min_balance_breach(self, uc):
        fc = _create_forecast(
            uc, name="FCST_BREACH", opening=Decimal("10000000"),
            min_balance_threshold=Decimal("5000000"),
        )
        fc_id = fc.get_data().id
        uc.add_forecast_line(fc_id, "outflow", "Large payment",
                             Decimal("8000000"), date(2026, 7, 3))
        result = uc.run_forecast_calculation(fc_id)
        assert result.is_success()
        data = result.get_data()
        assert data["closing_balance"] == Decimal("2000000.00")
        assert data["min_balance_breach"] is True

    def test_get_forecast(self, uc):
        fc = _create_forecast(uc, name="FCST_GET")
        fc_id = fc.get_data().id
        result = uc.get_forecast(fc_id)
        assert result.is_success()
        assert result.get_data().forecast_name == "FCST_GET"

    def test_list_forecasts(self, uc):
        _create_forecast(uc, name="FCST_A")
        _create_forecast(uc, name="FCST_B")
        result = uc.list_forecasts()
        assert result.is_success()
        forecasts = result.get_data()
        assert len(forecasts) >= 2

    def test_add_multiple_lines_and_calculate(self, uc):
        fc = _create_forecast(uc, name="FCST_MULTI", opening=Decimal("100000000"))
        fc_id = fc.get_data().id
        uc.add_forecast_line(fc_id, "inflow", "Receipt A",
                             Decimal("20000000"), date(2026, 7, 5))
        uc.add_forecast_line(fc_id, "inflow", "Receipt B",
                             Decimal("15000000"), date(2026, 7, 10))
        uc.add_forecast_line(fc_id, "outflow", "Payment A",
                             Decimal("25000000"), date(2026, 7, 8))
        result = uc.run_forecast_calculation(fc_id)
        assert result.is_success()
        data = result.get_data()
        assert data["total_inflows"] == Decimal("35000000.00")
        assert data["total_outflows"] == Decimal("25000000.00")
        assert data["closing_balance"] == Decimal("110000000.00")


# ── UC-TRS-03: Investment Management ───────────────────────────────

class TestInvestmentManagement:
    def test_create_investment_term_deposit(self, uc):
        result = _create_investment(uc, code="TD001", name="Term Deposit 6M",
                                    inv_type=InvestmentType.TERM_DEPOSIT)
        assert result.is_success()
        inv = result.get_data()
        assert inv.investment_code == "TD001"
        assert inv.investment_type == InvestmentType.TERM_DEPOSIT
        assert inv.status == InvestmentStatus.ACTIVE
        assert inv.total_cost == Decimal("500000000.00")

    def test_create_investment_trading_security(self, uc):
        result = uc.create_investment(
            investment_code="TS001",
            investment_name="Trading Security",
            investment_type=InvestmentType.TRADING_SECURITY,
            cost_price=Decimal("100000"),
            total_cost=Decimal("50000000"),
            purchase_date=date(2026, 6, 1),
            quantity=Decimal("500"),
            market_price=Decimal("105000"),
            counterparty_name="HOSE",
            coa_code="121",
        )
        assert result.is_success()
        inv = result.get_data()
        assert inv.investment_type == InvestmentType.TRADING_SECURITY
        assert inv.quantity == Decimal("500")
        assert inv.market_price == Decimal("105000.00")

    def test_create_investment_with_maturity_date(self, uc):
        result = _create_investment(uc, code="MAT001", name="Maturing Deposit",
                                    maturity_date=date(2027, 1, 1))
        assert result.is_success()
        inv = result.get_data()
        assert inv.maturity_date == date(2027, 1, 1)

    def test_get_investment(self, uc):
        created = _create_investment(uc, code="GET_INV")
        inv_id = created.get_data().id
        result = uc.get_investment(inv_id)
        assert result.is_success()
        assert result.get_data().investment_code == "GET_INV"

    def test_list_investments(self, uc):
        _create_investment(uc, code="LIST_A")
        _create_investment(uc, code="LIST_B")
        result = uc.list_investments()
        assert result.is_success()
        items = result.get_data()
        assert len(items) >= 2

    def test_record_investment_maturity(self, uc):
        created = _create_investment(uc, code="MATURE", name="To Mature",
                                     maturity_date=date(2026, 12, 31))
        inv_id = created.get_data().id
        result = uc.record_investment_maturity(
            investment_id=inv_id,
            maturity_date=date(2026, 12, 31),
            actual_amount=Decimal("525000000"),
            interest_income=Decimal("25000000"),
        )
        assert result.is_success()
        inv_result = uc.get_investment(inv_id)
        assert inv_result.get_data().status == InvestmentStatus.MATURED

    def test_record_investment_sale(self, uc):
        created = _create_investment(uc, code="SELL", name="To Sell",
                                     inv_type=InvestmentType.TRADING_SECURITY,
                                     quantity=Decimal("1000"))
        inv_id = created.get_data().id
        result = uc.record_investment_sale(
            investment_id=inv_id,
            sale_date=date(2026, 8, 1),
            quantity=Decimal("1000"),
            sale_price=Decimal("110000"),
            total_amount=Decimal("110000000"),
            gain_loss=Decimal("10000000"),
        )
        assert result.is_success()
        inv_result = uc.get_investment(inv_id)
        assert inv_result.get_data().status == InvestmentStatus.SOLD

    def test_get_maturing_investments(self, uc):
        _create_investment(uc, code="MAT30", name="Maturing Soon",
                           maturity_date=date.today() + timedelta(days=15))
        _create_investment(uc, code="NOT_MAT", name="Not Maturing",
                           maturity_date=date.today() + timedelta(days=90))
        result = uc.get_maturing_investments(days=30)
        assert result.is_success()
        items = result.get_data()
        codes = [i.investment_code for i in items]
        assert "MAT30" in codes
        assert "NOT_MAT" not in codes


# ── UC-TRS-04: Debt Management ─────────────────────────────────────

class TestDebtManagement:
    def test_create_loan(self, uc):
        result = _create_loan(uc)
        assert result.is_success()
        loan = result.get_data()
        assert loan.loan_code == "LN001"
        assert loan.principal == Decimal("1000000000.00")
        assert loan.outstanding_balance == Decimal("1000000000.00")
        assert loan.status == LoanStatus.ACTIVE

    def test_get_loan(self, uc):
        created = _create_loan(uc, code="GET_LN")
        loan_id = created.get_data().id
        result = uc.get_loan(loan_id)
        assert result.is_success()
        assert result.get_data().loan_code == "GET_LN"

    def test_list_loans(self, uc):
        _create_loan(uc, code="LN_A")
        _create_loan(uc, code="LN_B")
        result = uc.list_loans()
        assert result.is_success()
        items = result.get_data()
        assert len(items) >= 2

    def test_record_loan_payment(self, uc):
        created = _create_loan(uc, code="PAY_LN", principal=Decimal("500000000"))
        loan_id = created.get_data().id
        result = uc.record_loan_payment(
            loan_id=loan_id,
            payment_date=date(2026, 7, 1),
            principal_amount=Decimal("100000000"),
            interest_amount=Decimal("3500000"),
        )
        assert result.is_success()
        loan_result = uc.get_loan(loan_id)
        assert loan_result.get_data().outstanding_balance == Decimal("400000000.00")

    def test_loan_fully_paid(self, uc):
        created = _create_loan(uc, code="FULL_PAY", principal=Decimal("100000000"))
        loan_id = created.get_data().id
        result = uc.record_loan_payment(
            loan_id=loan_id,
            payment_date=date(2026, 7, 1),
            principal_amount=Decimal("100000000"),
            interest_amount=Decimal("700000"),
        )
        assert result.is_success()
        loan_result = uc.get_loan(loan_id)
        assert loan_result.get_data().outstanding_balance == Decimal("0.00")
        assert loan_result.get_data().status == LoanStatus.FULLY_PAID

    def test_check_loan_covenants_no_covenants(self, uc):
        created = _create_loan(uc, code="COVENANT_NONE")
        loan_id = created.get_data().id
        result = uc.check_loan_covenants(loan_id)
        assert result.is_success()
        data = result.get_data()
        assert data["compliant"] is True
        assert len(data["covenant_breaches"]) == 0

    def test_get_upcoming_payments(self, uc):
        result = uc.get_upcoming_payments(days=30)
        assert result.is_success()
        assert isinstance(result.get_data(), list)


# ── UC-TRS-06: FX Exposure Monitoring ──────────────────────────────

class TestFXExposure:
    def test_record_fx_rate(self, uc):
        result = uc.record_fx_rate(
            currency="USD",
            rate_date=date(2026, 7, 1),
            rate_avg=Decimal("25450"),
            rate_buying=Decimal("25300"),
            rate_selling=Decimal("25600"),
        )
        assert result.is_success()
        rate = result.get_data()
        assert rate.currency == "USD"
        assert rate.rate_avg == Decimal("25450")

    def test_get_fx_rate(self, uc):
        uc.record_fx_rate("USD", date(2026, 7, 1), Decimal("25450"))
        result = uc.get_fx_rate("USD", date(2026, 7, 1))
        assert result.is_success()
        assert result.get_data().rate_avg == Decimal("25450")

    def test_calculate_fx_exposure(self, uc):
        """No foreign currency loans/investments → empty exposures."""
        result = uc.calculate_fx_exposure()
        assert result.is_success()
        exposures = result.get_data()
        assert isinstance(exposures, list)

    def test_fx_forward_create(self, uc):
        result = uc.record_fx_forward(
            contract_number="FWD001",
            base_currency="VND",
            target_currency="USD",
            amount=Decimal("500000000"),
            forward_rate=Decimal("25500"),
            value_date=date(2026, 8, 1),
            maturity_date=date(2026, 10, 1),
            counterparty="Vietcombank",
        )
        assert result.is_success()
        fwd = result.get_data()
        assert fwd.contract_number == "FWD001"
        assert fwd.status.value == "open"

    def test_fx_forward_settle(self, uc):
        created = uc.record_fx_forward(
            contract_number="FWD_SETTLE",
            base_currency="VND",
            target_currency="USD",
            amount=Decimal("300000000"),
            forward_rate=Decimal("25400"),
            value_date=date(2026, 8, 1),
            maturity_date=date(2026, 10, 1),
            counterparty="Vietcombank",
        )
        assert created.is_success()
        fwd_id = created.get_data().id
        result = uc.settle_fx_forward(fwd_id, settlement_amount=Decimal("310000000"),
                                       settlement_date=date(2026, 10, 1))
        assert result.is_success()
        data = result.get_data()
        assert data["fx_id"] == fwd_id
        assert data["settlement_amount"] == Decimal("310000000.00")

    def test_fx_forward_settle_already_settled_fails(self, uc):
        created = uc.record_fx_forward(
            contract_number="FWD_2X",
            base_currency="VND", target_currency="USD",
            amount=Decimal("100000000"), forward_rate=Decimal("25000"),
            value_date=date(2026, 8, 1), maturity_date=date(2026, 10, 1),
            counterparty="Bank",
        )
        fwd_id = created.get_data().id
        uc.settle_fx_forward(fwd_id, Decimal("105000000"), date(2026, 10, 1))
        result = uc.settle_fx_forward(fwd_id, Decimal("105000000"), date(2026, 10, 1))
        assert result.is_failure()

    def test_fx_forward_not_found(self, uc):
        result = uc.settle_fx_forward(999, Decimal("0"), date.today())
        assert result.is_failure()


# ── UC-TRS-07: Intercompany Cash Management ────────────────────────

class TestIntercompany:
    def test_create_ic_loan(self, uc):
        result = uc.create_ic_loan(
            loan_code="ICL001",
            lender_entity_id="ENTITY_A",
            borrower_entity_id="ENTITY_B",
            principal=Decimal("500000000"),
            interest_rate=Decimal("0.05"),
            start_date=date(2026, 7, 1),
            maturity_date=date(2027, 7, 1),
        )
        assert result.is_success()
        loan = result.get_data()
        assert loan.loan_code == "ICL001"
        assert loan.outstanding_balance == Decimal("500000000.00")

    def test_get_ic_loan(self, uc):
        created = uc.create_ic_loan("ICL_GET", "ENT_A", "ENT_B",
                                     Decimal("100000000"), Decimal("0.05"),
                                     date(2026, 7, 1), date(2027, 7, 1))
        loan_id = created.get_data().id
        result = uc.get_ic_loan(loan_id)
        assert result.is_success()
        assert result.get_data().loan_code == "ICL_GET"

    def test_list_ic_loans(self, uc):
        uc.create_ic_loan("ICL_LST1", "ENT_A", "ENT_B",
                          Decimal("100000000"), Decimal("0.05"),
                          date(2026, 7, 1), date(2027, 7, 1))
        uc.create_ic_loan("ICL_LST2", "ENT_B", "ENT_C",
                          Decimal("200000000"), Decimal("0.06"),
                          date(2026, 8, 1), date(2027, 8, 1))
        result = uc.list_ic_loans()
        assert result.is_success()
        assert len(result.get_data()) >= 2

    def test_propose_ic_sweeps(self, uc):
        result = uc.propose_ic_sweeps(
            sweep_date=date(2026, 7, 1),
            entities_config={
                "ENTITY_A": {"current_balance": Decimal("200000000"),
                             "target_balance": Decimal("50000000")},
                "ENTITY_B": {"current_balance": Decimal("10000000"),
                             "target_balance": Decimal("50000000")},
            },
        )
        assert result.is_success()
        data = result.get_data()
        assert data["total_proposals"] >= 1
        proposal = data["proposals"][0]
        assert proposal["source_entity_id"] == "ENTITY_A"
        assert proposal["target_entity_id"] == "ENTITY_B"
        assert proposal["amount"] == Decimal("40000000.00")

    def test_execute_ic_sweep(self, uc):
        from domain.treasury import TreasuryPosition
        pos = TreasuryPosition(
            snapshot_date=date.today(), total_cash=Decimal("100000000"),
            total_bank=Decimal("0"), total_available=Decimal("100000000"),
            net_liquidity=Decimal("100000000"),
        )
        pos.entity_id = "ENTITY_A"
        uc.repo.create_treasury_position(pos)
        sweep = uc.repo.create_ic_sweep(IntercompanySweep(
            sweep_type=SweepType.ZERO_BALANCING,
            sweep_date=date(2026, 7, 1),
            source_entity_id="ENTITY_A",
            target_entity_id="ENTITY_B",
            amount=Decimal("50000000"),
            source_acct_type="bank",
            source_acct_id=1,
            target_acct_type="bank",
            target_acct_id=2,
        ))
        assert sweep.is_success()
        sweep_id = sweep.get_data().id
        result = uc.execute_ic_sweep(sweep_id)
        assert result.is_success()
        assert result.get_data()["status"] == "executed"

    def test_execute_ic_sweep_already_executed_fails(self, uc):
        sweep = uc.repo.create_ic_sweep(IntercompanySweep(
            sweep_type=SweepType.ZERO_BALANCING,
            sweep_date=date(2026, 7, 1),
            source_entity_id="ENT_X", target_entity_id="ENT_Y",
            amount=Decimal("10000000"),
            source_acct_type="bank", source_acct_id=1,
            target_acct_type="bank", target_acct_id=2,
        ))
        sweep_id = sweep.get_data().id
        uc.execute_ic_sweep(sweep_id)
        result = uc.execute_ic_sweep(sweep_id)
        assert result.is_failure()

    def test_ic_loan_same_entity_fails(self, uc):
        result = uc.create_ic_loan(
            loan_code="ICL_SAME",
            lender_entity_id="ENT_SAME",
            borrower_entity_id="ENT_SAME",
            principal=Decimal("100000000"),
            interest_rate=Decimal("0.05"),
            start_date=date(2026, 7, 1),
            maturity_date=date(2027, 7, 1),
        )
        assert result.is_failure()

    def test_ic_loan_non_compliant_fails(self, uc):
        result = uc.create_ic_loan(
            loan_code="ICL_TP",
            lender_entity_id="ENT_A",
            borrower_entity_id="ENT_B",
            principal=Decimal("100000000"),
            interest_rate=Decimal("0.05"),
            start_date=date(2026, 7, 1),
            maturity_date=date(2027, 7, 1),
            transfer_pricing_compliant=False,
        )
        assert result.is_failure()

    def test_ic_sweep_not_found(self, uc):
        result = uc.execute_ic_sweep(999)
        assert result.is_failure()


# ── UC-TRS-08: Treasury Dashboard & KPIs ───────────────────────────

class TestDashboard:
    def test_compute_dashboard_kpis(self, uc):
        result = uc.compute_dashboard_kpis()
        assert result.is_success()
        kpis = result.get_data()
        assert "days_cash_on_hand" in kpis
        assert "current_ratio" in kpis
        assert "quick_ratio" in kpis
        assert "liquidity_coverage" in kpis
        assert "total_available_cash" in kpis
        assert "total_loans_outstanding" in kpis
        assert "total_investments" in kpis
        assert kpis["total_available_cash"] == Decimal("0.00")

    def test_get_position_history(self, uc):
        uc.get_consolidated_cash_position()
        result = uc.get_position_history(days=30)
        assert result.is_success()
        positions = result.get_data()
        assert len(positions) >= 1

    def test_generate_daily_report(self, uc):
        result = uc.generate_treasury_report(report_type="daily")
        assert result.is_success()
        report = result.get_data()
        assert report["report_type"] == "daily"
        assert "position" in report
        assert "kpis" in report

    def test_generate_monthly_report(self, uc):
        result = uc.generate_treasury_report(report_type="monthly", period="2026-07")
        assert result.is_success()
        report = result.get_data()
        assert report["report_type"] == "monthly"
        assert report["period"] == "2026-07"

    def test_generate_unknown_report_fails(self, uc):
        result = uc.generate_treasury_report(report_type="weekly")
        assert result.is_failure()


# ── UC-TRS-09: Payment Factory ─────────────────────────────────────

class TestPaymentFactory:
    def test_create_payment_batch(self, uc):
        result = uc.create_payment_batch(
            batch_code="BATCH001",
            payment_date=date(2026, 7, 5),
        )
        assert result.is_success()
        batch = result.get_data()
        assert batch.batch_code == "BATCH001"
        assert batch.status == BatchStatus.DRAFT
        assert batch.total_amount == Decimal("0.00")

    def test_add_item_to_batch(self, uc):
        batch = uc.create_payment_batch("BATCH_ADD", date(2026, 7, 5))
        batch_id = batch.get_data().id
        result = uc.add_item_to_batch(
            batch_id=batch_id,
            source_module="ap",
            source_id=100,
            source_reference="INV-001",
            payee_name="Supplier A",
            amount=Decimal("50000000"),
            payee_account="123456789",
            payee_bank="Vietcombank",
        )
        assert result.is_success()
        item = result.get_data()
        assert item.payee_name == "Supplier A"
        assert item.amount == Decimal("50000000.00")

    def _create_cash_position(self, uc, available=Decimal("100000000")):
        from infrastructure.models.cash_models import CashReceiptModel, CashVoucherStatusDB
        receipt = CashReceiptModel(
            receipt_number="TST_RCPT",
            receipt_date=date.today(),
            amount=available,
            amount_in_words="One hundred million",
            currency="VND",
            status=CashVoucherStatusDB.APPROVED,
            receipt_type="cash_sale",
            payer_name="Test",
            account_code="1111",
            counter_account="5111",
            description="Test receipt",
            created_by="test",
        )
        uc.session.add(receipt)
        uc.session.flush()

    def test_approve_batch(self, uc):
        self._create_cash_position(uc)
        batch = uc.create_payment_batch("BATCH_APPROVE", date(2026, 7, 5))
        batch_id = batch.get_data().id
        uc.add_item_to_batch(batch_id, "ap", 1, "REF001",
                             "Supplier", Decimal("10000000"))
        uc.review_batch(batch_id)
        result = uc.approve_batch(batch_id, approved_by="NV001")
        assert result.is_success()
        assert result.get_data()["status"] == "approved"

    def test_submit_batch(self, uc):
        self._create_cash_position(uc)
        batch = uc.create_payment_batch("BATCH_SUBMIT", date(2026, 7, 5))
        batch_id = batch.get_data().id
        uc.add_item_to_batch(batch_id, "ap", 1, "REF001",
                             "Supplier", Decimal("10000000"))
        uc.review_batch(batch_id)
        uc.approve_batch(batch_id, "NV001")
        result = uc.submit_batch(batch_id)
        assert result.is_success()
        assert result.get_data()["status"] == "submitted"

    def test_get_batch(self, uc):
        batch = uc.create_payment_batch("BATCH_GET", date(2026, 7, 5))
        batch_id = batch.get_data().id
        uc.add_item_to_batch(batch_id, "ap", 1, "REF001",
                             "Supplier", Decimal("20000000"))
        result = uc.get_batch(batch_id)
        assert result.is_success()
        data = result.get_data()
        assert data["batch"].batch_code == "BATCH_GET"
        assert len(data["items"]) == 1

    def test_list_batches(self, uc):
        uc.create_payment_batch("BATCH_LST1", date(2026, 7, 5))
        uc.create_payment_batch("BATCH_LST2", date(2026, 7, 6))
        result = uc.list_batches()
        assert result.is_success()
        assert len(result.get_data()) >= 2

    def test_approve_without_review_fails(self, uc):
        """Batch can be approved from DRAFT status directly."""
        self._create_cash_position(uc)
        batch = uc.create_payment_batch("BATCH_NOREVIEW", date(2026, 7, 5))
        batch_id = batch.get_data().id
        uc.add_item_to_batch(batch_id, "ap", 1, "REF001",
                             "Supplier", Decimal("10000000"))
        result = uc.approve_batch(batch_id, "NV001")
        assert result.is_success()

    def test_submit_without_approve_fails(self, uc):
        batch = uc.create_payment_batch("BATCH_NOSUBMIT", date(2026, 7, 5))
        batch_id = batch.get_data().id
        result = uc.submit_batch(batch_id)
        assert result.is_failure()

    def test_add_item_to_nonexistent_batch(self, uc):
        result = uc.add_item_to_batch(
            batch_id=999, source_module="ap", source_id=1,
            source_reference="REF", payee_name="X", amount=Decimal("1000"),
        )
        assert result.is_failure()

    def test_get_nonexistent_batch(self, uc):
        result = uc.get_batch(999)
        assert result.is_failure()

    def test_batch_item_updates_total(self, uc):
        batch = uc.create_payment_batch("BATCH_TOTAL", date(2026, 7, 5))
        batch_id = batch.get_data().id
        uc.add_item_to_batch(batch_id, "ap", 1, "REF_A",
                             "Sup A", Decimal("30000000"))
        uc.add_item_to_batch(batch_id, "ap", 2, "REF_B",
                             "Sup B", Decimal("20000000"))
        result = uc.get_batch(batch_id)
        data = result.get_data()
        assert data["batch"].total_amount == Decimal("50000000.00")
        assert data["batch"].item_count == 2


# ── UC-TRS-10: Bank Connectivity ───────────────────────────────────

class TestBankConnectivity:
    def test_create_connector(self, uc):
        result = uc.create_bank_connector(
            bank_code="VCB",
            bank_name="Vietcombank",
            api_endpoint="https://api.vietcombank.vn",
            auth_type="api_key",
        )
        assert result.is_success()
        conn = result.get_data()
        assert conn.bank_code == "VCB"
        assert conn.is_active is True

    def test_list_connectors(self, uc):
        uc.create_bank_connector("VCB", "Vietcombank")
        uc.create_bank_connector("CTG", "Vietinbank")
        result = uc.list_connectors()
        assert result.is_success()
        assert len(result.get_data()) >= 2

    def test_sync_bank_data(self, uc):
        conn = uc.create_bank_connector("BIDV", "BIDV")
        conn_id = conn.get_data().id
        result = uc.sync_bank_data(connector_id=conn_id, sync_type="balance")
        assert result.is_success()
        log = result.get_data()
        assert log.sync_status == SyncStatus.SUCCESS
        assert log.transactions_fetched == 10

    def test_sync_logs(self, uc):
        conn = uc.create_bank_connector("TCB", "Techcombank")
        conn_id = conn.get_data().id
        uc.sync_bank_data(conn_id, "balance")
        result = uc.get_sync_logs(conn_id)
        assert result.is_success()
        logs = result.get_data()
        assert len(logs) >= 1

    def test_sync_inactive_connector_fails(self, uc):
        conn = uc.create_bank_connector("EIB", "Eximbank")
        conn_id = conn.get_data().id
        uc.repo.update_connector(conn_id, is_active=False)
        result = uc.sync_bank_data(conn_id)
        assert result.is_failure()

    def test_sync_nonexistent_connector(self, uc):
        result = uc.sync_bank_data(999)
        assert result.is_failure()

    def test_test_connector(self, uc):
        conn = uc.create_bank_connector("ACB", "ACB")
        conn_id = conn.get_data().id
        result = uc.test_connector(conn_id)
        assert result.is_success()
        assert result.get_data()["test_result"] == "success"

    def test_test_inactive_connector_fails(self, uc):
        conn = uc.create_bank_connector("MB", "MB Bank")
        conn_id = conn.get_data().id
        uc.repo.update_connector(conn_id, is_active=False)
        result = uc.test_connector(conn_id)
        assert result.is_failure()


# ── Treasury Policies ──────────────────────────────────────────────

class TestTreasuryPolicies:
    def test_create_policy(self, uc):
        result = uc.create_treasury_policy(
            policy_code="INV_LIMIT_001",
            policy_name="Investment Limit - Term Deposits",
            policy_type="investment_limit",
            max_value=Decimal("5000000000"),
            min_value=Decimal("100000000"),
        )
        assert result.is_success()
        policy = result.get_data()
        assert policy.policy_code == "INV_LIMIT_001"
        assert policy.max_value == Decimal("5000000000.00")
        assert policy.active is True

    def test_get_policy(self, uc):
        created = uc.create_treasury_policy("FX_LIMIT", "FX Exposure Limit",
                                             "fx_limit", max_value=Decimal("100000000"))
        policy_id = created.get_data().id
        result = uc.get_treasury_policy(policy_id)
        assert result.is_success()
        assert result.get_data().policy_code == "FX_LIMIT"

    def test_list_policies(self, uc):
        uc.create_treasury_policy("POL_A", "Policy A", "investment_limit")
        uc.create_treasury_policy("POL_B", "Policy B", "fx_limit")
        result = uc.list_treasury_policies()
        assert result.is_success()
        assert len(result.get_data()) >= 2

    def test_list_policies_by_type(self, uc):
        uc.create_treasury_policy("TYPE_A", "Type A", "investment_limit")
        uc.create_treasury_policy("TYPE_B", "Type B", "fx_limit")
        result = uc.list_treasury_policies(policy_type="investment_limit")
        assert result.is_success()
        codes = [p.policy_code for p in result.get_data()]
        assert "TYPE_A" in codes
        assert "TYPE_B" not in codes

    def test_list_policies_active_only(self, uc):
        uc.create_treasury_policy("ACT_A", "Active A", "investment_limit")
        pol = uc.create_treasury_policy("INACT_B", "Inactive B", "fx_limit")
        pol_id = pol.get_data().id
        uc.repo.update_policy(pol_id, active=False)
        result = uc.list_treasury_policies(active_only=True)
        codes = [p.policy_code for p in result.get_data()]
        assert "ACT_A" in codes
        assert "INACT_B" not in codes

    def test_get_nonexistent_policy(self, uc):
        result = uc.get_treasury_policy(999)
        assert result.is_failure()

    def test_duplicate_policy_code_fails(self, uc):
        uc.create_treasury_policy("DUP_CODE", "First", "investment_limit")
        result = uc.create_treasury_policy("DUP_CODE", "Second", "investment_limit")
        assert result.is_failure()

    def test_policy_with_counterparty_restriction(self, uc):
        result = uc.create_treasury_policy(
            policy_code="CP_RESTRICT",
            policy_name="Counterparty Restricted",
            policy_type="investment_limit",
            counterparty_restriction="['UNTRUSTED_BANK']",
            max_value=Decimal("1000000000"),
        )
        assert result.is_success()
        assert result.get_data().counterparty_restriction == "['UNTRUSTED_BANK']"
