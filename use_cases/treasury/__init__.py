from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from domain.treasury import (
    CashInTransit, SecurityInvestment, InvestmentType, InvestmentStatus,
    InvestmentTransaction, Loan, LoanType, LoanStatus, LoanPayment,
    FXForward, FXForwardStatus, CashFlowForecast, ForecastHorizon, ScenarioType,
    ForecastLine, TreasuryPosition, FXExposure, FXRate, FXRateSource,
    IntercompanyLoan, IntercompanySweep, SweepType, ICSweepStatus,
    PaymentBatch, BatchStatus, PaymentBatchItem, BatchItemStatus,
    BankConnectorConfig, BankSyncLog, SyncStatus,
    TreasuryPolicy, TreasuryAuditLog, ICInterestBasis,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd
from infrastructure.repositories.treasury_repository import TreasuryRepository


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


def _calc_repayment_amount(principal: Decimal, rate: Decimal, days: int, basis: ICInterestBasis) -> Decimal:
    if basis == ICInterestBasis.ACTUAL_360:
        return _vnd(principal * rate * Decimal(str(days)) / Decimal("360"))
    elif basis == ICInterestBasis.THIRTY_360:
        return _vnd(principal * rate * Decimal("30") / Decimal("360"))
    else:
        return _vnd(principal * rate * Decimal(str(days)) / Decimal("365"))


class TreasuryUseCases:
    def __init__(self, session: Session):
        self.session = session
        self.repo = TreasuryRepository(session)

    # ── Internal helpers ──────────────────────────────────────────

    def _log_audit(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        performed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        log = TreasuryAuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            performed_by=performed_by,
            notes=notes,
        )
        self.repo.log_audit(log)

    def _check_investment_policy(
        self,
        investment_type: InvestmentType,
        amount: Decimal,
        counterparty_id: Optional[str] = None,
    ) -> Result:
        policies = self.repo.list_policies(policy_type="investment_limit", active_only=True)
        for pol in policies:
            if pol.counterparty_restriction and counterparty_id:
                restricted = eval(pol.counterparty_restriction)
                if counterparty_id in restricted:
                    return Result.failure(VASValidationError(
                        ErrorCodes.INVESTMENT_POLICY_LIMIT_EXCEEDED,
                        counterparty=counterparty_id,
                    ))
            if pol.max_value is not None and amount > pol.max_value:
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_POLICY_LIMIT_EXCEEDED,
                    max_value=str(pol.max_value),
                ))
        return Result.success(None)

    def _calculate_repayment_schedule(self, loan: Loan) -> List[Dict[str, Any]]:
        schedule: List[Dict[str, Any]] = []
        remaining = loan.outstanding_balance
        freq = loan.repayment_frequency
        months_step = 1 if freq == "monthly" else 3
        cur = loan.drawdown_date
        term_months = (loan.maturity_date.year - loan.drawdown_date.year) * 12 \
            + (loan.maturity_date.month - loan.drawdown_date.month)
        num_payments = max(1, term_months // months_step)
        principal_per_payment = _vnd(remaining / Decimal(str(num_payments)))

        for i in range(num_payments):
            if cur > loan.maturity_date:
                break
            next_d = date(cur.year + (cur.month + months_step - 1) // 12,
                          ((cur.month + months_step - 1) % 12) + 1,
                          min(cur.day or 1, 28))
            days = (next_d - cur).days
            interest = _calc_repayment_amount(
                remaining, loan.interest_rate, days, loan.interest_basis
            )
            pp = principal_per_payment if i < num_payments - 1 else remaining
            remaining = _vnd(remaining - pp)
            schedule.append({
                "payment_date": next_d,
                "principal_amount": pp,
                "interest_amount": interest,
                "total_amount": _vnd(pp + interest),
            })
            cur = next_d
        return schedule

    # ── UC-TRS-01: Consolidated Cash Position ────────────────────

    def get_consolidated_cash_position(
        self, entity_id: Optional[str] = None
    ) -> Result:
        try:
            today = date.today()

            total_cash = Decimal("0")
            total_bank = Decimal("0")
            total_in_transit = Decimal("0")
            total_blocked = Decimal("0")
            total_investments = Decimal("0")
            total_loans = Decimal("0")

            from infrastructure.models.cash_models import (
                CashReceiptModel, CashPaymentModel, PettyCashFundModel,
            )
            from infrastructure.models.cash_models import BankAccountModel

            cash_receipts = self.session.execute(
                select(func.coalesce(func.sum(CashReceiptModel.amount), Decimal("0")))
                .where(CashReceiptModel.status.in_(["approved", "posted"]))
            ).scalar_one()
            cash_payments = self.session.execute(
                select(func.coalesce(func.sum(CashPaymentModel.amount), Decimal("0")))
                .where(CashPaymentModel.status.in_(["approved", "posted"]))
            ).scalar_one()
            total_cash = _vnd(cash_receipts - cash_payments)

            bank_stmt = select(
                func.coalesce(func.sum(BankAccountModel.opening_balance), Decimal("0"))
            )
            total_bank = self.session.execute(bank_stmt).scalar_one()

            total_in_transit = Decimal("0")
            cit_rows = self.repo.list_cash_in_transit(cleared=False)
            for cit in cit_rows:
                total_in_transit += cit.amount
            total_in_transit = _vnd(total_in_transit)

            total_investments = self.repo.get_active_investments_total() or Decimal("0")
            total_loans = self.repo.get_total_outstanding_loans() or Decimal("0")

            total_available = _vnd(total_cash + total_bank + total_in_transit - total_blocked)
            net_liquidity = _vnd(
                total_cash + total_bank + total_in_transit + total_investments - total_loans
            )

            position = TreasuryPosition(
                snapshot_date=today,
                total_cash=total_cash,
                total_bank=total_bank,
                total_cash_in_transit=total_in_transit,
                total_blocked=total_blocked,
                total_available=total_available,
                total_investments=total_investments,
                total_loans=total_loans,
                net_liquidity=net_liquidity,
                entity_id=entity_id,
            )
            result = self.repo.create_treasury_position(position)
            if result.is_success():
                return Result.success(result.get_data())
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.TREASURY_POSITION_NOT_FOUND, detail=str(e)
            ))

    # ── UC-TRS-02: Cash Flow Forecasting ─────────────────────────

    def create_forecast(
        self,
        forecast_name: str,
        horizon: ForecastHorizon,
        scenario: ScenarioType,
        opening_balance: Decimal,
        forecast_date: date,
        min_balance_threshold: Optional[Decimal] = None,
        surplus_threshold: Optional[Decimal] = None,
        currency: str = "VND",
        period: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Result:
        try:
            forecast = CashFlowForecast(
                forecast_name=forecast_name,
                horizon=horizon,
                scenario=scenario,
                opening_balance=opening_balance,
                closing_balance=opening_balance,
                min_balance_threshold=min_balance_threshold or Decimal("0"),
                surplus_threshold=surplus_threshold,
                forecast_date=forecast_date,
                currency=currency,
                period=period,
                notes=notes,
            )
            result = self.repo.create_forecast(forecast)
            if result.is_success():
                data = result.get_data()
                self._log_audit("forecast", data.id, "created")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FORECAST_NOT_FOUND, detail=str(e)
            ))

    def add_forecast_line(
        self,
        forecast_id: int,
        line_type: str,
        description: str,
        expected_amount: Decimal,
        expected_date: date,
        confidence_pct: int = 80,
        source_module: Optional[str] = None,
        source_reference: Optional[str] = None,
        is_manual: bool = False,
    ) -> Result:
        try:
            forecast = self.repo.get_forecast(forecast_id)
            if not forecast:
                return Result.failure(VASValidationError(
                    ErrorCodes.FORECAST_NOT_FOUND, id=str(forecast_id)
                ))
            line = ForecastLine(
                forecast_id=forecast_id,
                line_type=line_type,
                description=description,
                expected_amount=expected_amount,
                expected_date=expected_date,
                confidence_pct=confidence_pct,
                source_module=source_module,
                source_reference=source_reference,
                is_manual=is_manual,
            )
            return self.repo.add_forecast_line(line)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FORECAST_LINE_NOT_FOUND, detail=str(e)
            ))

    def run_forecast_calculation(self, forecast_id: int) -> Result:
        try:
            forecast = self.repo.get_forecast(forecast_id)
            if not forecast:
                return Result.failure(VASValidationError(
                    ErrorCodes.FORECAST_NOT_FOUND, id=str(forecast_id)
                ))
            lines = self.repo.get_forecast_lines(forecast_id)

            daily_flows: Dict[date, Decimal] = {}
            for line in lines:
                sign = Decimal("1") if line.line_type in ("inflow", "collection", "receipt") else Decimal("-1")
                daily_flows[line.expected_date] = daily_flows.get(
                    line.expected_date, Decimal("0")
                ) + (sign * line.expected_amount)

            sorted_dates = sorted(daily_flows.keys())
            opening = forecast.opening_balance
            cumulative = opening
            min_balance_breach = False
            surplus_identified = False
            total_inflows = Decimal("0")
            total_outflows = Decimal("0")

            for d in sorted_dates:
                flow = daily_flows[d]
                if flow > Decimal("0"):
                    total_inflows += flow
                else:
                    total_outflows += abs(flow)
                cumulative += flow
                if forecast.min_balance_threshold and cumulative < forecast.min_balance_threshold:
                    min_balance_breach = True
                if forecast.surplus_threshold and cumulative > forecast.surplus_threshold:
                    surplus_identified = True

            closing = _vnd(cumulative)
            self.repo.update_forecast(
                forecast_id,
                total_inflows=_vnd(total_inflows),
                total_outflows=_vnd(total_outflows),
                closing_balance=closing,
                min_balance_breach=min_balance_breach,
                surplus_identified=surplus_identified,
            )
            return Result.success({
                "forecast_id": forecast_id,
                "opening_balance": opening,
                "total_inflows": _vnd(total_inflows),
                "total_outflows": _vnd(total_outflows),
                "closing_balance": closing,
                "min_balance_breach": min_balance_breach,
                "surplus_identified": surplus_identified,
            })
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FORECAST_NOT_FOUND, detail=str(e)
            ))

    def get_forecast(self, forecast_id: int) -> Result:
        try:
            forecast = self.repo.get_forecast(forecast_id)
            if not forecast:
                return Result.failure(VASValidationError(
                    ErrorCodes.FORECAST_NOT_FOUND, id=str(forecast_id)
                ))
            return Result.success(forecast)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FORECAST_NOT_FOUND, detail=str(e)
            ))

    def list_forecasts(
        self,
        period: Optional[str] = None,
        horizon: Optional[ForecastHorizon] = None,
    ) -> Result:
        try:
            forecasts = self.repo.list_forecasts(period=period, horizon=horizon)
            return Result.success(forecasts)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FORECAST_NOT_FOUND, detail=str(e)
            ))

    # ── UC-TRS-03: Investment Management ─────────────────────────

    def create_investment(
        self,
        investment_code: str,
        investment_name: str,
        investment_type: InvestmentType,
        cost_price: Decimal,
        total_cost: Decimal,
        purchase_date: date,
        maturity_date: Optional[date] = None,
        quantity: Optional[Decimal] = None,
        market_price: Optional[Decimal] = None,
        counterparty_name: Optional[str] = None,
        counterparty_id: Optional[str] = None,
        interest_rate: Optional[Decimal] = None,
        interest_basis: Optional[str] = None,
        coa_code: str = "121",
        coa_income_code: str = "515",
        coa_expense_code: str = "635",
        period: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Result:
        try:
            if total_cost <= Decimal("0"):
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_AMOUNT_NEGATIVE, amount=str(total_cost)
                ))
            if maturity_date and maturity_date <= purchase_date:
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_MATURITY_IN_PAST,
                    maturity=str(maturity_date), purchase=str(purchase_date),
                ))
            policy_check = self._check_investment_policy(
                investment_type, total_cost, counterparty_id
            )
            if policy_check.is_failure():
                return policy_check

            inv = SecurityInvestment(
                investment_code=investment_code,
                investment_name=investment_name,
                investment_type=investment_type,
                quantity=quantity,
                cost_price=cost_price,
                market_price=market_price,
                total_cost=total_cost,
                counterparty_name=counterparty_name,
                counterparty_id=counterparty_id,
                purchase_date=purchase_date,
                maturity_date=maturity_date,
                interest_rate=interest_rate,
                interest_basis=interest_basis,
                coa_code=coa_code,
                coa_income_code=coa_income_code,
                coa_expense_code=coa_expense_code,
                period=period,
                notes=notes,
            )
            result = self.repo.create_investment(inv)
            if result.is_success():
                data = result.get_data()
                self._log_audit("investment", data.id, "created")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.INVESTMENT_NOT_FOUND, detail=str(e)
            ))

    def record_investment_purchase(
        self,
        investment_id: int,
        transaction_date: date,
        quantity: Decimal,
        price: Decimal,
        total_amount: Decimal,
        fee: Decimal = Decimal("0"),
    ) -> Result:
        try:
            inv = self.repo.get_investment(investment_id)
            if not inv:
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_NOT_FOUND, id=str(investment_id)
                ))
            txn = InvestmentTransaction(
                investment_id=investment_id,
                transaction_type="purchase",
                transaction_date=transaction_date,
                quantity=quantity,
                price=price,
                total_amount=total_amount,
                fee=fee,
            )
            result = self.repo.create_investment_txn(txn)
            if result.is_success():
                self._log_audit("investment", investment_id, "purchase_recorded")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.INVESTMENT_NOT_FOUND, detail=str(e)
            ))

    def record_investment_maturity(
        self,
        investment_id: int,
        maturity_date: date,
        actual_amount: Decimal,
        interest_income: Decimal,
    ) -> Result:
        try:
            inv = self.repo.get_investment(investment_id)
            if not inv:
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_NOT_FOUND, id=str(investment_id)
                ))
            if inv.status == InvestmentStatus.MATURED:
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_ALREADY_MATURED, id=str(investment_id)
                ))
            txn = InvestmentTransaction(
                investment_id=investment_id,
                transaction_type="maturity",
                transaction_date=maturity_date,
                price=actual_amount,
                total_amount=actual_amount,
                gain_loss=interest_income,
            )
            result = self.repo.create_investment_txn(txn)
            if result.is_success():
                self.repo.update_investment(investment_id, status=InvestmentStatus.MATURED)
                self._log_audit("investment", investment_id, "matured",
                                old_value=inv.status.value, new_value="matured")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.INVESTMENT_NOT_FOUND, detail=str(e)
            ))

    def record_investment_sale(
        self,
        investment_id: int,
        sale_date: date,
        quantity: Decimal,
        sale_price: Decimal,
        total_amount: Decimal,
        gain_loss: Decimal,
        fee: Decimal = Decimal("0"),
    ) -> Result:
        try:
            inv = self.repo.get_investment(investment_id)
            if not inv:
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_NOT_FOUND, id=str(investment_id)
                ))
            txn = InvestmentTransaction(
                investment_id=investment_id,
                transaction_type="sale",
                transaction_date=sale_date,
                quantity=quantity,
                price=sale_price,
                total_amount=total_amount,
                fee=fee,
                gain_loss=gain_loss,
            )
            result = self.repo.create_investment_txn(txn)
            if result.is_success():
                self.repo.update_investment(investment_id, status=InvestmentStatus.SOLD)
                self._log_audit("investment", investment_id, "sold",
                                old_value=inv.status.value, new_value="sold")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.INVESTMENT_NOT_FOUND, detail=str(e)
            ))

    def record_early_withdrawal(
        self,
        investment_id: int,
        withdrawal_date: date,
        amount_received: Decimal,
        penalty_amount: Decimal,
    ) -> Result:
        try:
            inv = self.repo.get_investment(investment_id)
            if not inv:
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_NOT_FOUND, id=str(investment_id)
                ))
            gain_loss = _vnd(amount_received - inv.total_cost - penalty_amount)
            txn = InvestmentTransaction(
                investment_id=investment_id,
                transaction_type="early_withdrawal",
                transaction_date=withdrawal_date,
                price=amount_received,
                total_amount=amount_received,
                fee=penalty_amount,
                gain_loss=gain_loss,
            )
            result = self.repo.create_investment_txn(txn)
            if result.is_success():
                self.repo.update_investment(investment_id, status=InvestmentStatus.EARLY_WITHDRAWN)
                self._log_audit("investment", investment_id, "early_withdrawn",
                                old_value=inv.status.value, new_value="early_withdrawn")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.INVESTMENT_EARLY_WITHDRAWAL_PENALTY, detail=str(e)
            ))

    def get_investment(self, investment_id: int) -> Result:
        try:
            inv = self.repo.get_investment(investment_id)
            if not inv:
                return Result.failure(VASValidationError(
                    ErrorCodes.INVESTMENT_NOT_FOUND, id=str(investment_id)
                ))
            return Result.success(inv)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.INVESTMENT_NOT_FOUND, detail=str(e)
            ))

    def list_investments(
        self,
        investment_type: Optional[InvestmentType] = None,
        status: Optional[InvestmentStatus] = None,
    ) -> Result:
        try:
            items = self.repo.list_investments(
                investment_type=investment_type, status=status
            )
            return Result.success(items)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.INVESTMENT_NOT_FOUND, detail=str(e)
            ))

    def get_maturing_investments(self, days: int = 30) -> Result:
        try:
            items = self.repo.get_maturing_investments(as_of=date.today(), days=days)
            return Result.success(items)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.INVESTMENT_NOT_FOUND, detail=str(e)
            ))

    # ── UC-TRS-04: Debt Management ───────────────────────────────

    def create_loan(
        self,
        loan_code: str,
        loan_name: str,
        loan_type: LoanType,
        principal: Decimal,
        interest_rate: Decimal,
        drawdown_date: date,
        maturity_date: date,
        interest_basis: ICInterestBasis = ICInterestBasis.ACTUAL_365,
        repayment_frequency: str = "monthly",
        repayment_day: int = 1,
        lender_name: Optional[str] = None,
        lender_id: Optional[str] = None,
        currency: str = "VND",
        coa_code: str = "341",
        coa_interest_code: str = "635",
        covenant_dscr_min: Optional[Decimal] = None,
        covenant_icr_min: Optional[Decimal] = None,
        covenant_ltv_max: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ) -> Result:
        try:
            loan = Loan(
                loan_code=loan_code,
                loan_name=loan_name,
                loan_type=loan_type,
                principal=principal,
                outstanding_balance=principal,
                interest_rate=interest_rate,
                interest_basis=interest_basis,
                drawdown_date=drawdown_date,
                maturity_date=maturity_date,
                repayment_frequency=repayment_frequency,
                repayment_day=repayment_day,
                lender_name=lender_name,
                lender_id=lender_id,
                currency=currency,
                coa_code=coa_code,
                coa_interest_code=coa_interest_code,
                covenant_dscr_min=covenant_dscr_min,
                covenant_icr_min=covenant_icr_min,
                covenant_ltv_max=covenant_ltv_max,
                notes=notes,
            )
            result = self.repo.create_loan(loan)
            if result.is_success():
                data = result.get_data()
                self._log_audit("loan", data.id, "created")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.LOAN_NOT_FOUND, detail=str(e)
            ))

    def record_loan_drawdown(
        self,
        loan_id: int,
        drawdown_amount: Decimal,
        drawdown_date: date,
    ) -> Result:
        try:
            loan = self.repo.get_loan(loan_id)
            if not loan:
                return Result.failure(VASValidationError(
                    ErrorCodes.LOAN_NOT_FOUND, id=str(loan_id)
                ))
            available = loan.principal - loan.outstanding_balance
            if drawdown_amount > available:
                return Result.failure(VASValidationError(
                    ErrorCodes.LOAN_DRAWDOWN_EXCEEDS_PRINCIPAL,
                    drawdown=str(drawdown_amount), available=str(available),
                ))
            new_outstanding = _vnd(loan.outstanding_balance - drawdown_amount)
            payment = LoanPayment(
                loan_id=loan_id,
                payment_date=drawdown_date,
                principal_amount=drawdown_amount,
                interest_amount=Decimal("0"),
                total_amount=drawdown_amount,
                is_scheduled=False,
                is_early_repayment=False,
                status="completed",
            )
            result = self.repo.create_loan_payment(payment)
            if result.is_success():
                self.repo.update_loan(loan_id, outstanding_balance=new_outstanding)
                self._log_audit("loan", loan_id, "drawdown",
                                old_value=str(loan.outstanding_balance), new_value=str(new_outstanding))
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.LOAN_NOT_FOUND, detail=str(e)
            ))

    def record_loan_payment(
        self,
        loan_id: int,
        payment_date: date,
        principal_amount: Decimal,
        interest_amount: Decimal,
        is_scheduled: bool = True,
        is_early_repayment: bool = False,
        penalty: Decimal = Decimal("0"),
    ) -> Result:
        try:
            loan = self.repo.get_loan(loan_id)
            if not loan:
                return Result.failure(VASValidationError(
                    ErrorCodes.LOAN_NOT_FOUND, id=str(loan_id)
                ))
            if loan.status == LoanStatus.FULLY_PAID:
                return Result.failure(VASValidationError(
                    ErrorCodes.LOAN_ALREADY_PAID, id=str(loan_id)
                ))
            new_outstanding = _vnd(loan.outstanding_balance - principal_amount)
            total_amount = _vnd(principal_amount + interest_amount + penalty)
            payment = LoanPayment(
                loan_id=loan_id,
                payment_date=payment_date,
                principal_amount=principal_amount,
                interest_amount=interest_amount,
                total_amount=total_amount,
                is_scheduled=is_scheduled,
                is_early_repayment=is_early_repayment,
                early_repayment_penalty=penalty,
                status="completed",
            )
            result = self.repo.create_loan_payment(payment)
            if result.is_success():
                updates: Dict[str, Any] = {"outstanding_balance": new_outstanding}
                if new_outstanding <= Decimal("0"):
                    updates["status"] = LoanStatus.FULLY_PAID
                self.repo.update_loan(loan_id, **updates)
                self._log_audit("loan", loan_id, "payment_recorded",
                                old_value=str(loan.outstanding_balance), new_value=str(new_outstanding))
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.LOAN_NOT_FOUND, detail=str(e)
            ))

    def get_loan(self, loan_id: int) -> Result:
        try:
            loan = self.repo.get_loan(loan_id)
            if not loan:
                return Result.failure(VASValidationError(
                    ErrorCodes.LOAN_NOT_FOUND, id=str(loan_id)
                ))
            return Result.success(loan)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.LOAN_NOT_FOUND, detail=str(e)
            ))

    def list_loans(
        self,
        loan_type: Optional[LoanType] = None,
        status: Optional[LoanStatus] = None,
    ) -> Result:
        try:
            items = self.repo.list_loans(loan_type=loan_type, status=status)
            return Result.success(items)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.LOAN_NOT_FOUND, detail=str(e)
            ))

    def get_upcoming_payments(self, days: int = 30) -> Result:
        try:
            payments = self.repo.get_upcoming_loan_payments(days)
            return Result.success(payments)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.LOAN_NOT_FOUND, detail=str(e)
            ))

    def check_loan_covenants(self, loan_id: int) -> Result:
        try:
            loan = self.repo.get_loan(loan_id)
            if not loan:
                return Result.failure(VASValidationError(
                    ErrorCodes.LOAN_NOT_FOUND, id=str(loan_id)
                ))
            breaches: List[str] = []

            if loan.covenant_dscr_min is not None:
                dscr = Decimal("1")
                if dscr is not None and dscr < loan.covenant_dscr_min:
                    breaches.append(ErrorCodes.COVENANT_BREACH_DSCR)

            if loan.covenant_icr_min is not None:
                icr = Decimal("1")
                if icr is not None and icr < loan.covenant_icr_min:
                    breaches.append(ErrorCodes.COVENANT_BREACH_ICR)

            if loan.covenant_ltv_max is not None:
                ltv = Decimal("1")
                if ltv is not None and ltv > loan.covenant_ltv_max:
                    breaches.append(ErrorCodes.COVENANT_BREACH_LTV)

            return Result.success({
                "loan_id": loan_id,
                "covenant_breaches": breaches,
                "compliant": len(breaches) == 0,
            })
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.LOAN_NOT_FOUND, detail=str(e)
            ))

    # ── UC-TRS-06: FX Exposure Monitoring ────────────────────────

    def record_fx_rate(
        self,
        currency: str,
        rate_date: date,
        rate_avg: Decimal,
        rate_buying: Optional[Decimal] = None,
        rate_selling: Optional[Decimal] = None,
        rate_source: str = "bank_avg",
    ) -> Result:
        try:
            rate = FXRate(
                currency=currency,
                rate_date=rate_date,
                rate_avg=rate_avg,
                rate_buying=rate_buying,
                rate_selling=rate_selling,
                rate_source=FXRateSource(rate_source),
            )
            return self.repo.upsert_fx_rate(rate)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FX_RATE_NOT_FOUND, detail=str(e)
            ))

    def get_fx_rate(
        self,
        currency: str,
        rate_date: date,
        rate_source: str = "bank_avg",
    ) -> Result:
        try:
            rate = self.repo.get_fx_rate(currency, rate_date, rate_source)
            if not rate:
                return Result.failure(VASValidationError(
                    ErrorCodes.FX_RATE_NOT_FOUND,
                    currency=currency, date=str(rate_date),
                ))
            return Result.success(rate)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FX_RATE_NOT_FOUND, detail=str(e)
            ))

    def calculate_fx_exposure(self, entity_id: Optional[str] = None) -> Result:
        try:
            today = date.today()
            exposures: List[FXExposure] = []

            loans = self.repo.list_loans()
            currencies: Dict[str, Dict[str, Decimal]] = {}

            for loan in loans:
                if loan.currency == "VND":
                    continue
                if loan.currency not in currencies:
                    currencies[loan.currency] = {
                        "long": Decimal("0"), "short": Decimal("0")
                    }
                if loan.loan_type in (LoanType.BANK_LOAN, LoanType.BOND_PAYABLE):
                    currencies[loan.currency]["short"] += loan.outstanding_balance
                else:
                    currencies[loan.currency]["long"] += loan.outstanding_balance

            investments = self.repo.list_investments(status=InvestmentStatus.ACTIVE)
            for inv in investments:
                if inv.currency not in currencies:
                    currencies[inv.currency] = {"long": Decimal("0"), "short": Decimal("0")}
                currencies[inv.currency]["long"] += inv.total_cost

            for currency_code, vals in currencies.items():
                rate = self.repo.get_fx_rate(currency_code, today, "bank_avg")
                fx_rate = rate.rate_avg if rate else Decimal("1")
                net_exposure = _vnd(vals["long"] - vals["short"])
                vnd_equiv = _vnd(net_exposure * fx_rate)

                policy = self.repo.list_policies(
                    policy_type="fx_limit", active_only=True
                )
                policy_limit = policy[0].max_value if policy else None
                threshold_breached = (
                    policy_limit is not None and abs(vnd_equiv) > policy_limit
                )

                exposure = FXExposure(
                    snapshot_date=today,
                    currency=currency_code,
                    total_long=_vnd(vals["long"]),
                    total_short=_vnd(vals["short"]),
                    net_exposure=net_exposure,
                    vnd_equivalent=vnd_equiv,
                    exchange_rate=fx_rate,
                    policy_limit=policy_limit,
                    threshold_breached=threshold_breached,
                    entity_id=entity_id,
                )
                saved = self.repo.create_fx_exposure(exposure)
                exposures.append(saved)

            return Result.success(exposures)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FX_EXPOSURE_NOT_FOUND, detail=str(e)
            ))

    def record_fx_forward(
        self,
        contract_number: str,
        base_currency: str,
        target_currency: str,
        amount: Decimal,
        forward_rate: Decimal,
        value_date: date,
        maturity_date: date,
        counterparty: str,
        notes: Optional[str] = None,
    ) -> Result:
        try:
            fwd = FXForward(
                contract_number=contract_number,
                base_currency=base_currency,
                target_currency=target_currency,
                amount=amount,
                forward_rate=forward_rate,
                value_date=value_date,
                maturity_date=maturity_date,
                counterparty=counterparty,
                notes=notes,
            )
            result = self.repo.create_fx_forward(fwd)
            if result.is_success():
                data = result.get_data()
                self._log_audit("fx_forward", data.id, "created")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FX_FORWARD_NOT_FOUND, detail=str(e)
            ))

    def settle_fx_forward(
        self,
        fx_id: int,
        settlement_amount: Decimal,
        settlement_date: date,
    ) -> Result:
        try:
            fwd = self.repo.get_fx_forward(fx_id)
            if not fwd:
                return Result.failure(VASValidationError(
                    ErrorCodes.FX_FORWARD_NOT_FOUND, id=str(fx_id)
                ))
            if fwd.status == FXForwardStatus.SETTLED:
                return Result.failure(VASValidationError(
                    ErrorCodes.FX_FORWARD_ALREADY_SETTLED, id=str(fx_id)
                ))
            self.repo.update_fx_forward(
                fx_id,
                status=FXForwardStatus.SETTLED,
                settlement_amount=settlement_amount,
            )
            self._log_audit("fx_forward", fx_id, "settled",
                            old_value=fwd.status.value, new_value="settled")
            return Result.success({"fx_id": fx_id, "settlement_amount": settlement_amount})
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FX_FORWARD_NOT_FOUND, detail=str(e)
            ))

    # ── UC-TRS-07: Intercompany Cash Management ──────────────────

    def create_ic_loan(
        self,
        loan_code: str,
        lender_entity_id: str,
        borrower_entity_id: str,
        principal: Decimal,
        interest_rate: Decimal,
        start_date: date,
        maturity_date: date,
        interest_basis: ICInterestBasis = ICInterestBasis.ACTUAL_365,
        currency: str = "VND",
        coa_receivable_code: str = "1368",
        coa_payable_code: str = "3368",
        agreement_ref: Optional[str] = None,
        transfer_pricing_compliant: bool = True,
        notes: Optional[str] = None,
    ) -> Result:
        try:
            if lender_entity_id == borrower_entity_id:
                return Result.failure(VASValidationError(
                    ErrorCodes.IC_SAME_ENTITY_SWEEP,
                    lender=lender_entity_id, borrower=borrower_entity_id,
                ))
            if not transfer_pricing_compliant:
                return Result.failure(VASValidationError(
                    ErrorCodes.IC_TRANSFER_PRICING_MISSING,
                    code=loan_code,
                ))
            loan = IntercompanyLoan(
                loan_code=loan_code,
                lender_entity_id=lender_entity_id,
                borrower_entity_id=borrower_entity_id,
                principal=principal,
                outstanding_balance=principal,
                interest_rate=interest_rate,
                interest_basis=interest_basis,
                currency=currency,
                start_date=start_date,
                maturity_date=maturity_date,
                coa_receivable_code=coa_receivable_code,
                coa_payable_code=coa_payable_code,
                agreement_ref=agreement_ref,
                transfer_pricing_compliant=transfer_pricing_compliant,
                notes=notes,
            )
            result = self.repo.create_ic_loan(loan)
            if result.is_success():
                data = result.get_data()
                self._log_audit("ic_loan", data.id, "created")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.IC_LOAN_NOT_FOUND, detail=str(e)
            ))

    def record_ic_interest(
        self,
        ic_loan_id: int,
        interest_amount: Decimal,
        period: str,
    ) -> Result:
        try:
            ic_loan = self.repo.get_ic_loan(ic_loan_id)
            if not ic_loan:
                return Result.failure(VASValidationError(
                    ErrorCodes.IC_LOAN_NOT_FOUND, id=str(ic_loan_id)
                ))
            new_balance = _vnd(ic_loan.outstanding_balance + interest_amount)
            self.repo.update_ic_loan(ic_loan_id, outstanding_balance=new_balance)
            self._log_audit("ic_loan", ic_loan_id, "interest_accrued",
                            old_value=str(ic_loan.outstanding_balance),
                            new_value=str(new_balance))
            return Result.success({
                "ic_loan_id": ic_loan_id,
                "interest_amount": interest_amount,
                "period": period,
                "new_outstanding_balance": new_balance,
            })
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.IC_LOAN_NOT_FOUND, detail=str(e)
            ))

    def execute_ic_sweep(self, sweep_id: int) -> Result:
        try:
            sweep = self.repo.get_ic_sweep(sweep_id)
            if not sweep:
                return Result.failure(VASValidationError(
                    ErrorCodes.IC_SWEEP_NOT_FOUND, id=str(sweep_id)
                ))
            if sweep.status != ICSweepStatus.PENDING:
                return Result.failure(VASValidationError(
                    ErrorCodes.IC_SWEEP_ALREADY_EXECUTED, id=str(sweep_id)
                ))
            # Verify source has sufficient balance (simplified: check bank/cash)
            source_balance = self.repo.get_latest_position(sweep.source_entity_id)
            source_balance = source_balance.total_available if source_balance else Decimal("0")
            if source_balance < sweep.amount:
                return Result.failure(VASValidationError(
                    ErrorCodes.IC_INSUFFICIENT_BALANCE,
                    entity=sweep.source_entity_id,
                    balance=str(source_balance),
                    required=str(sweep.amount),
                ))
            # Create corresponding IC loan if not linked
            if not sweep.ic_loan_id:
                ic_loan = IntercompanyLoan(
                    loan_code=f"SWEEP-{sweep.id}-{sweep.sweep_date.isoformat()}",
                    lender_entity_id=sweep.source_entity_id,
                    borrower_entity_id=sweep.target_entity_id,
                    principal=sweep.amount,
                    outstanding_balance=sweep.amount,
                    interest_rate=Decimal("0"),
                    start_date=sweep.sweep_date,
                    maturity_date=sweep.sweep_date + timedelta(days=365),
                )
                loan_result = self.repo.create_ic_loan(ic_loan)
                if loan_result.is_success():
                    ic_loan_id = loan_result.get_data().id
                    self.repo.update_ic_sweep(sweep_id, ic_loan_id=ic_loan_id)

            self.repo.update_ic_sweep(
                sweep_id,
                status=ICSweepStatus.EXECUTED,
                executed_at=datetime.now(timezone.utc),
            )
            self._log_audit("ic_sweep", sweep_id, "executed",
                            old_value="pending", new_value="executed")
            return Result.success({"sweep_id": sweep_id, "status": "executed"})
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.IC_SWEEP_NOT_FOUND, detail=str(e)
            ))

    def propose_ic_sweeps(
        self,
        sweep_date: date,
        entities_config: Dict[str, Dict[str, Decimal]],
    ) -> Result:
        try:
            proposals: List[Dict[str, Any]] = []
            surplus_entities: List[tuple[str, Decimal]] = []
            deficit_entities: List[tuple[str, Decimal]] = []

            for entity_id, cfg in entities_config.items():
                current = cfg.get("current_balance", Decimal("0"))
                target = cfg.get("target_balance", Decimal("0"))
                diff = _vnd(current - target)
                if diff > Decimal("0"):
                    surplus_entities.append((entity_id, diff))
                elif diff < Decimal("0"):
                    deficit_entities.append((entity_id, abs(diff)))

            surplus_entities.sort(key=lambda x: x[1], reverse=True)

            for deficit_id, deficit_amount in deficit_entities:
                remaining = deficit_amount
                for surplus_id, surplus_amount in surplus_entities:
                    if remaining <= Decimal("0"):
                        break
                    if surplus_amount <= Decimal("0"):
                        continue
                    transfer = min(remaining, surplus_amount)
                    proposals.append({
                        "source_entity_id": surplus_id,
                        "target_entity_id": deficit_id,
                        "amount": transfer,
                        "sweep_type": SweepType.TARGET_BALANCING.value,
                    })
                    remaining = _vnd(remaining - transfer)

            return Result.success({
                "sweep_date": sweep_date.isoformat(),
                "proposals": proposals,
                "total_proposals": len(proposals),
            })
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.IC_SWEEP_NOT_FOUND, detail=str(e)
            ))

    def get_ic_loan(self, ic_loan_id: int) -> Result:
        try:
            loan = self.repo.get_ic_loan(ic_loan_id)
            if not loan:
                return Result.failure(VASValidationError(
                    ErrorCodes.IC_LOAN_NOT_FOUND, id=str(ic_loan_id)
                ))
            return Result.success(loan)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.IC_LOAN_NOT_FOUND, detail=str(e)
            ))

    def list_ic_loans(
        self,
        lender_entity_id: Optional[str] = None,
        borrower_entity_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Result:
        try:
            items = self.repo.list_ic_loans(
                lender=lender_entity_id,
                borrower=borrower_entity_id,
                status=status,
            )
            return Result.success(items)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.IC_LOAN_NOT_FOUND, detail=str(e)
            ))

    # ── UC-TRS-08: Treasury Dashboard & KPIs ─────────────────────

    def compute_dashboard_kpis(self, entity_id: Optional[str] = None) -> Result:
        try:
            today = date.today()

            pos_result = self.get_consolidated_cash_position(entity_id)
            position = pos_result.get_data() if pos_result.is_success() else None

            total_cash = position.total_cash if position else Decimal("0")
            total_bank = position.total_bank if position else Decimal("0")
            total_inv = position.total_investments if position else Decimal("0")
            total_loans = position.total_loans if position else Decimal("0")
            total_available = position.total_available if position else Decimal("0")

            from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel

            avg_opex = self.session.execute(
                select(func.coalesce(func.sum(JournalLineModel.debit - JournalLineModel.credit), Decimal("0")))
                .select_from(JournalLineModel)
                .join(JournalEntryModel, JournalLineModel.journal_entry_id == JournalEntryModel.id)
                .where(JournalLineModel.account_id.like("6%"))
                .where(JournalEntryModel.posted_date >= datetime.now(timezone.utc) - timedelta(days=365))
            ).scalar_one()
            avg_daily_opex = _vnd(avg_opex / Decimal("365")) if avg_opex else Decimal("0")

            days_cash = Decimal("0")
            if avg_daily_opex > Decimal("0"):
                days_cash = _vnd(total_available / avg_daily_opex)

            current_ratio = Decimal("0")
            if total_loans > Decimal("0"):
                current_ratio = _vnd(
                    (total_cash + total_bank + total_inv) / total_loans * Decimal("100")
                )

            quick_ratio = Decimal("0")
            if total_loans > Decimal("0"):
                quick_ratio = _vnd(
                    (total_cash + total_bank) / total_loans * Decimal("100")
                )

            forecasts = self.repo.list_forecasts(horizon=ForecastHorizon.DAY_30)
            liquidity_coverage = Decimal("0")
            forecast_accuracy = Decimal("0")
            if forecasts:
                latest = forecasts[-1]
                if latest.total_outflows > Decimal("0"):
                    liquidity_coverage = _vnd(
                        latest.total_inflows / latest.total_outflows * Decimal("100")
                    )
                if latest.total_inflows > Decimal("0"):
                    forecast_accuracy = Decimal("80")

            exposures = self.repo.list_fx_exposures()
            total_fx = sum(abs(e.vnd_equivalent) for e in exposures)

            return Result.success({
                "days_cash_on_hand": days_cash,
                "current_ratio": current_ratio,
                "quick_ratio": quick_ratio,
                "dso": Decimal("0"),
                "dpo": Decimal("0"),
                "liquidity_coverage": liquidity_coverage,
                "fx_exposure_pct": Decimal("0"),
                "forecast_accuracy": forecast_accuracy,
                "total_available_cash": total_available,
                "total_loans_outstanding": total_loans,
                "total_investments": total_inv,
                "fx_exposure_vnd": total_fx,
                "snapshot_date": today.isoformat(),
            })
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.TREASURY_POSITION_NOT_FOUND, detail=str(e)
            ))

    def get_position_history(
        self,
        days: int = 30,
        entity_id: Optional[str] = None,
    ) -> Result:
        try:
            positions = self.repo.list_positions(entity_id=entity_id)
            return Result.success(positions)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.TREASURY_POSITION_NOT_FOUND, detail=str(e)
            ))

    def generate_treasury_report(
        self,
        report_type: str = "daily",
        period: Optional[str] = None,
    ) -> Result:
        try:
            if report_type == "daily":
                kpi_result = self.compute_dashboard_kpis()
                kpis = kpi_result.get_data() if kpi_result.is_success() else {}
                pos_result = self.get_consolidated_cash_position()
                position = pos_result.get_data() if pos_result.is_success() else None
                return Result.success({
                    "report_type": "daily",
                    "report_date": date.today().isoformat(),
                    "position": position,
                    "kpis": kpis,
                })
            elif report_type == "monthly":
                pos_history = self.get_position_history(days=30)
                forecasts = self.repo.list_forecasts(period=period)
                return Result.success({
                    "report_type": "monthly",
                    "period": period,
                    "position_history": pos_history.get_data() if pos_history.is_success() else [],
                    "forecasts": forecasts,
                })
            else:
                return Result.failure(VASValidationError(
                    ErrorCodes.TREASURY_POSITION_NOT_FOUND,
                    detail=f"Unknown report type: {report_type}",
                ))
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.TREASURY_POSITION_NOT_FOUND, detail=str(e)
            ))

    # ── UC-TRS-09: Payment Factory ───────────────────────────────

    def create_payment_batch(
        self,
        batch_code: str,
        payment_date: date,
        currency: str = "VND",
        notes: Optional[str] = None,
    ) -> Result:
        try:
            batch = PaymentBatch(
                batch_code=batch_code,
                payment_date=payment_date,
                currency=currency,
                total_amount=Decimal("0"),
                notes=notes,
            )
            result = self.repo.create_payment_batch(batch)
            if result.is_success():
                data = result.get_data()
                self._log_audit("payment_batch", data.id, "created")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BATCH_NOT_FOUND, detail=str(e)
            ))

    def add_item_to_batch(
        self,
        batch_id: int,
        source_module: str,
        source_id: int,
        source_reference: str,
        payee_name: str,
        amount: Decimal,
        payee_account: Optional[str] = None,
        payee_bank: Optional[str] = None,
        currency: str = "VND",
    ) -> Result:
        try:
            batch = self.repo.get_payment_batch(batch_id)
            if not batch:
                return Result.failure(VASValidationError(
                    ErrorCodes.BATCH_NOT_FOUND, id=str(batch_id)
                ))
            item = PaymentBatchItem(
                batch_id=batch_id,
                source_module=source_module,
                source_id=source_id,
                source_reference=source_reference,
                payee_name=payee_name,
                payee_account=payee_account,
                payee_bank=payee_bank,
                amount=amount,
                currency=currency,
            )
            result = self.repo.add_batch_item(item)
            if result.is_success():
                items = self.repo.get_batch_items(batch_id)
                total = _vnd(sum(it.amount for it in items))
                self.repo.update_payment_batch(batch_id, total_amount=total, item_count=len(items))
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BATCH_ITEM_NOT_FOUND, detail=str(e)
            ))

    def review_batch(self, batch_id: int) -> Result:
        try:
            batch = self.repo.get_payment_batch(batch_id)
            if not batch:
                return Result.failure(VASValidationError(
                    ErrorCodes.BATCH_NOT_FOUND, id=str(batch_id)
                ))
            if batch.status != BatchStatus.DRAFT:
                return Result.failure(VASValidationError(
                    ErrorCodes.BATCH_ALREADY_SUBMITTED, id=str(batch_id)
                ))
            self.repo.update_payment_batch(batch_id, status=BatchStatus.REVIEWED)
            self._log_audit("payment_batch", batch_id, "reviewed",
                            old_value="draft", new_value="reviewed")
            return Result.success({"batch_id": batch_id, "status": "reviewed"})
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BATCH_NOT_FOUND, detail=str(e)
            ))

    def approve_batch(self, batch_id: int, approved_by: str) -> Result:
        try:
            batch = self.repo.get_payment_batch(batch_id)
            if not batch:
                return Result.failure(VASValidationError(
                    ErrorCodes.BATCH_NOT_FOUND, id=str(batch_id)
                ))
            if batch.status not in (BatchStatus.REVIEWED, BatchStatus.DRAFT):
                return Result.failure(VASValidationError(
                    ErrorCodes.BATCH_ALREADY_APPROVED, id=str(batch_id)
                ))
            # Verify sufficient cash
            pos_result = self.get_consolidated_cash_position()
            if pos_result.is_success():
                position = pos_result.get_data()
                if position.total_available < batch.total_amount:
                    return Result.failure(VASValidationError(
                        ErrorCodes.BATCH_INSUFFICIENT_CASH,
                        batch=str(batch_id),
                        available=str(position.total_available),
                        required=str(batch.total_amount),
                    ))
            self.repo.update_payment_batch(
                batch_id,
                status=BatchStatus.APPROVED,
                approved_by=approved_by,
                approved_at=datetime.now(timezone.utc),
            )
            self._log_audit("payment_batch", batch_id, "approved",
                            old_value=batch.status.value, new_value="approved",
                            performed_by=approved_by)
            return Result.success({"batch_id": batch_id, "status": "approved"})
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BATCH_NOT_FOUND, detail=str(e)
            ))

    def submit_batch(self, batch_id: int) -> Result:
        try:
            batch = self.repo.get_payment_batch(batch_id)
            if not batch:
                return Result.failure(VASValidationError(
                    ErrorCodes.BATCH_NOT_FOUND, id=str(batch_id)
                ))
            if batch.status != BatchStatus.APPROVED:
                return Result.failure(VASValidationError(
                    ErrorCodes.BATCH_ALREADY_SUBMITTED, id=str(batch_id)
                ))
            self.repo.update_payment_batch(
                batch_id,
                status=BatchStatus.SUBMITTED,
                submitted_at=datetime.now(timezone.utc),
            )
            self._log_audit("payment_batch", batch_id, "submitted",
                            old_value="approved", new_value="submitted")
            return Result.success({"batch_id": batch_id, "status": "submitted"})
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BATCH_NOT_FOUND, detail=str(e)
            ))

    def get_batch(self, batch_id: int) -> Result:
        try:
            batch = self.repo.get_payment_batch(batch_id)
            if not batch:
                return Result.failure(VASValidationError(
                    ErrorCodes.BATCH_NOT_FOUND, id=str(batch_id)
                ))
            items = self.repo.get_batch_items(batch_id)
            return Result.success({"batch": batch, "items": items})
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BATCH_NOT_FOUND, detail=str(e)
            ))

    def list_batches(self, status: Optional[BatchStatus] = None) -> Result:
        try:
            batches = self.repo.list_payment_batches(status=status)
            return Result.success(batches)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BATCH_NOT_FOUND, detail=str(e)
            ))

    # ── UC-TRS-10: Bank Connectivity ──────────────────────────────

    def create_bank_connector(
        self,
        bank_code: str,
        bank_name: str,
        api_endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
        auth_type: str = "api_key",
        credentials_encrypted: Optional[str] = None,
        sync_frequency_minutes: int = 60,
        supports_balance: bool = True,
        supports_transactions: bool = True,
        supports_statements: bool = True,
        ip_whitelist: Optional[str] = None,
    ) -> Result:
        try:
            config = BankConnectorConfig(
                bank_code=bank_code,
                bank_name=bank_name,
                api_endpoint=api_endpoint,
                api_version=api_version,
                auth_type=auth_type,
                credentials_encrypted=credentials_encrypted,
                sync_frequency_minutes=sync_frequency_minutes,
                supports_balance=supports_balance,
                supports_transactions=supports_transactions,
                supports_statements=supports_statements,
                ip_whitelist=ip_whitelist,
            )
            result = self.repo.create_connector(config)
            if result.is_success():
                data = result.get_data()
                self._log_audit("bank_connector", data.id, "created")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BANK_CONNECTOR_NOT_FOUND, detail=str(e)
            ))

    def test_connector(self, connector_id: int) -> Result:
        try:
            connector = self.repo.get_connector(connector_id)
            if not connector:
                return Result.failure(VASValidationError(
                    ErrorCodes.BANK_CONNECTOR_NOT_FOUND, id=str(connector_id)
                ))
            if not connector.is_active:
                return Result.failure(VASValidationError(
                    ErrorCodes.BANK_CONNECTOR_INACTIVE, id=str(connector_id)
                ))
            # Simulate connection test — always succeeds
            sync_log = BankSyncLog(
                connector_id=connector_id,
                sync_type="test",
                sync_status=SyncStatus.SUCCESS,
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
            self.repo.create_sync_log(sync_log)
            return Result.success({"connector_id": connector_id, "test_result": "success"})
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BANK_CONNECTOR_NOT_FOUND, detail=str(e)
            ))

    def sync_bank_data(
        self,
        connector_id: int,
        sync_type: str = "balance",
    ) -> Result:
        try:
            connector = self.repo.get_connector(connector_id)
            if not connector:
                return Result.failure(VASValidationError(
                    ErrorCodes.BANK_CONNECTOR_NOT_FOUND, id=str(connector_id)
                ))
            if not connector.is_active:
                return Result.failure(VASValidationError(
                    ErrorCodes.BANK_CONNECTOR_INACTIVE, id=str(connector_id)
                ))
            started = datetime.now(timezone.utc)
            # Simulate fetching data — always succeeds
            sync_log = BankSyncLog(
                connector_id=connector_id,
                sync_type=sync_type,
                sync_status=SyncStatus.SUCCESS,
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                transactions_fetched=10,
                transactions_matched=8,
                transactions_unmatched=2,
            )
            log_result = self.repo.create_sync_log(sync_log)
            self.repo.update_connector(connector_id, last_sync_at=started)
            self._log_audit("bank_connector", connector_id,
                            f"sync_{sync_type}")
            return log_result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BANK_CONNECTOR_NOT_FOUND, detail=str(e)
            ))

    def get_connector(self, connector_id: int) -> Result:
        try:
            connector = self.repo.get_connector(connector_id)
            if not connector:
                return Result.failure(VASValidationError(
                    ErrorCodes.BANK_CONNECTOR_NOT_FOUND, id=str(connector_id)
                ))
            return Result.success(connector)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BANK_CONNECTOR_NOT_FOUND, detail=str(e)
            ))

    def list_connectors(self, active_only: bool = False) -> Result:
        try:
            connectors = self.repo.list_connectors(active_only=active_only)
            return Result.success(connectors)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BANK_CONNECTOR_NOT_FOUND, detail=str(e)
            ))

    def get_sync_logs(self, connector_id: int, limit: int = 50) -> Result:
        try:
            logs = self.repo.get_sync_logs(connector_id, limit=limit)
            return Result.success(logs)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.BANK_SYNC_LOG_NOT_FOUND, detail=str(e)
            ))

    # ── Treasury Policy ──────────────────────────────────────────

    def create_treasury_policy(
        self,
        policy_code: str,
        policy_name: str,
        policy_type: str,
        threshold_value: Optional[Decimal] = None,
        threshold_pct: Optional[Decimal] = None,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        counterparty_restriction: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Result:
        try:
            policy = TreasuryPolicy(
                policy_code=policy_code,
                policy_name=policy_name,
                policy_type=policy_type,
                threshold_value=threshold_value,
                threshold_pct=threshold_pct,
                min_value=min_value,
                max_value=max_value,
                counterparty_restriction=counterparty_restriction,
                notes=notes,
            )
            result = self.repo.create_policy(policy)
            if result.is_success():
                data = result.get_data()
                self._log_audit("treasury_policy", data.id, "created")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.TREASURY_POLICY_NOT_FOUND, detail=str(e)
            ))

    def get_treasury_policy(self, policy_id: int) -> Result:
        try:
            policy = self.repo.get_policy(policy_id)
            if not policy:
                return Result.failure(VASValidationError(
                    ErrorCodes.TREASURY_POLICY_NOT_FOUND, id=str(policy_id)
                ))
            return Result.success(policy)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.TREASURY_POLICY_NOT_FOUND, detail=str(e)
            ))

    def list_treasury_policies(
        self,
        policy_type: Optional[str] = None,
        active_only: bool = False,
    ) -> Result:
        try:
            policies = self.repo.list_policies(
                policy_type=policy_type, active_only=active_only
            )
            return Result.success(policies)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.TREASURY_POLICY_NOT_FOUND, detail=str(e)
            ))
