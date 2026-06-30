from typing import Optional, List, Any, Dict
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, desc

from domain.treasury import (
    CashInTransit, SecurityInvestment, InvestmentTransaction,
    Loan, LoanPayment, FXForward, CashFlowForecast, ForecastLine,
    TreasuryPosition, FXExposure, FXRate,
    IntercompanyLoan, IntercompanySweep,
    PaymentBatch, PaymentBatchItem,
    BankConnectorConfig, BankSyncLog,
    TreasuryPolicy, TreasuryAuditLog,
    InvestmentType, InvestmentStatus, LoanType, LoanStatus,
    FXForwardStatus, SweepType,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd
from infrastructure.models.treasury_models import (
    CashInTransitModel, SecurityInvestmentModel, InvestmentTransactionModel,
    LoanModel, LoanPaymentModel, FXForwardModel,
    CashFlowForecastModel, ForecastLineModel,
    TreasuryPositionModel, FXExposureModel, FXRateModel,
    IntercompanyLoanModel, IntercompanySweepModel,
    PaymentBatchModel, PaymentBatchItemModel,
    BankConnectorConfigModel, BankSyncLogModel,
    TreasuryPolicyModel, TreasuryAuditLogModel,
    InvestmentTypeDB, InvestmentStatusDB, LoanTypeDB, LoanStatusDB,
    SweepTypeDB, ICSweepStatusDB, BatchStatusDB, BatchItemStatusDB,
    SyncStatusDB, FXForwardStatusDB,
)


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class TreasuryRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── CashInTransit ─────────────────────────────────────────────────

    def _cit_to_domain(self, m: CashInTransitModel) -> CashInTransit:
        d = CashInTransit(
            reference=m.reference,
            amount=m.amount,
            currency=m.currency,
            source_account_type=m.source_account_type,
            source_account_id=m.source_account_id,
            dest_account_type=m.dest_account_type,
            dest_account_id=m.dest_account_id,
            transfer_date=m.transfer_date,
            expected_clear_date=m.expected_clear_date,
            cleared=m.cleared,
            cleared_at=m.cleared_at,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _cit_to_model(self, d: CashInTransit) -> CashInTransitModel:
        return CashInTransitModel(
            reference=d.reference,
            amount=d.amount,
            currency=d.currency,
            source_account_type=d.source_account_type,
            source_account_id=d.source_account_id,
            dest_account_type=d.dest_account_type,
            dest_account_id=d.dest_account_id,
            transfer_date=d.transfer_date,
            expected_clear_date=d.expected_clear_date,
            cleared=d.cleared,
            cleared_at=d.cleared_at,
            notes=d.notes,
        )

    def create_cash_in_transit(self, cit: CashInTransit) -> Result:
        existing = self.session.execute(
            select(CashInTransitModel).where(CashInTransitModel.reference == cit.reference)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="CashInTransit", id=cit.reference))
        model = self._cit_to_model(cit)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._cit_to_domain(model))

    def get_cash_in_transit(self, cit_id: int) -> Optional[CashInTransit]:
        m = self.session.get(CashInTransitModel, cit_id)
        return self._cit_to_domain(m) if m else None

    def list_cash_in_transit(
        self, cleared: Optional[bool] = None, limit: int = 50, offset: int = 0,
    ) -> List[CashInTransit]:
        stmt = select(CashInTransitModel)
        if cleared is not None:
            stmt = stmt.where(CashInTransitModel.cleared == cleared)
        stmt = stmt.order_by(CashInTransitModel.transfer_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._cit_to_domain(m) for m in models]

    def update_cash_in_transit(self, cit_id: int, **updates) -> Optional[CashInTransit]:
        model = self.session.get(CashInTransitModel, cit_id)
        if not model:
            return None
        allowed = ("amount", "currency", "source_account_type", "source_account_id",
                   "dest_account_type", "dest_account_id", "transfer_date",
                   "expected_clear_date", "cleared", "cleared_at", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._cit_to_domain(model)

    def mark_cit_cleared(self, cit_id: int, cleared_at: datetime) -> Optional[CashInTransit]:
        return self.update_cash_in_transit(cit_id, cleared=True, cleared_at=cleared_at)

    # ── SecurityInvestment ────────────────────────────────────────────

    def _inv_to_domain(self, m: SecurityInvestmentModel) -> SecurityInvestment:
        d = SecurityInvestment(
            investment_code=m.investment_code,
            investment_name=m.investment_name,
            investment_type=InvestmentType(m.investment_type),
            status=InvestmentStatus(m.status),
            quantity=m.quantity,
            cost_price=m.cost_price,
            market_price=m.market_price,
            total_cost=m.total_cost,
            fair_value=m.fair_value,
            counterparty_name=m.counterparty_name,
            counterparty_id=m.counterparty_id,
            purchase_date=m.purchase_date,
            maturity_date=m.maturity_date,
            interest_rate=m.interest_rate,
            interest_basis=m.interest_basis,
            coa_code=m.coa_code,
            coa_income_code=m.coa_income_code,
            coa_expense_code=m.coa_expense_code,
            period=m.period,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _inv_to_model(self, d: SecurityInvestment) -> SecurityInvestmentModel:
        return SecurityInvestmentModel(
            investment_code=d.investment_code,
            investment_name=d.investment_name,
            investment_type=d.investment_type.value,
            status=d.status.value,
            quantity=d.quantity,
            cost_price=d.cost_price,
            market_price=d.market_price,
            total_cost=d.total_cost,
            fair_value=d.fair_value,
            counterparty_name=d.counterparty_name,
            counterparty_id=d.counterparty_id,
            purchase_date=d.purchase_date,
            maturity_date=d.maturity_date,
            interest_rate=d.interest_rate,
            interest_basis=d.interest_basis,
            coa_code=d.coa_code,
            coa_income_code=d.coa_income_code,
            coa_expense_code=d.coa_expense_code,
            period=d.period,
            notes=d.notes,
        )

    def create_investment(self, inv: SecurityInvestment) -> Result:
        existing = self.session.execute(
            select(SecurityInvestmentModel).where(
                SecurityInvestmentModel.investment_code == inv.investment_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="SecurityInvestment", id=inv.investment_code))
        model = self._inv_to_model(inv)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._inv_to_domain(model))

    def get_investment(self, inv_id: int) -> Optional[SecurityInvestment]:
        m = self.session.get(SecurityInvestmentModel, inv_id)
        return self._inv_to_domain(m) if m else None

    def get_investment_by_code(self, code: str) -> Optional[SecurityInvestment]:
        m = self.session.execute(
            select(SecurityInvestmentModel).where(SecurityInvestmentModel.investment_code == code)
        ).scalar_one_or_none()
        return self._inv_to_domain(m) if m else None

    def list_investments(
        self,
        investment_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SecurityInvestment]:
        stmt = select(SecurityInvestmentModel)
        if investment_type:
            stmt = stmt.where(SecurityInvestmentModel.investment_type == investment_type)
        if status:
            stmt = stmt.where(SecurityInvestmentModel.status == status)
        stmt = stmt.order_by(SecurityInvestmentModel.purchase_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._inv_to_domain(m) for m in models]

    def update_investment(self, inv_id: int, **updates) -> Optional[SecurityInvestment]:
        model = self.session.get(SecurityInvestmentModel, inv_id)
        if not model:
            return None
        allowed = ("investment_name", "investment_type", "status", "quantity",
                   "cost_price", "market_price", "total_cost", "fair_value",
                   "counterparty_name", "counterparty_id", "purchase_date",
                   "maturity_date", "interest_rate", "interest_basis",
                   "coa_code", "coa_income_code", "coa_expense_code", "period", "notes")
        for k, v in updates.items():
            if k in allowed:
                if isinstance(v, (InvestmentType, InvestmentStatus)):
                    setattr(model, k, v.value)
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._inv_to_domain(model)

    def get_active_investments_total(self) -> Decimal:
        result = self.session.execute(
            select(func.coalesce(func.sum(SecurityInvestmentModel.total_cost), Decimal("0")))
            .where(SecurityInvestmentModel.status == "active")
        ).scalar_one()
        return _vnd(result)

    def get_maturing_investments(self, as_of: date, days: int = 30) -> List[SecurityInvestment]:
        cutoff = as_of.__class__(as_of.year, as_of.month, as_of.day)
        from datetime import timedelta
        end = cutoff + timedelta(days=days)
        models = self.session.execute(
            select(SecurityInvestmentModel)
            .where(SecurityInvestmentModel.status == "active")
            .where(SecurityInvestmentModel.maturity_date.isnot(None))
            .where(SecurityInvestmentModel.maturity_date.between(cutoff, end))
            .order_by(SecurityInvestmentModel.maturity_date)
        ).scalars().all()
        return [self._inv_to_domain(m) for m in models]

    # ── InvestmentTransaction ─────────────────────────────────────────

    def _inv_txn_to_domain(self, m: InvestmentTransactionModel) -> InvestmentTransaction:
        d = InvestmentTransaction(
            investment_id=m.investment_id,
            transaction_type=m.transaction_type,
            transaction_date=m.transaction_date,
            quantity=m.quantity,
            price=m.price,
            total_amount=m.total_amount,
            fee=m.fee,
            gain_loss=m.gain_loss,
            counterparty_ref=m.counterparty_ref,
            notes=m.notes,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _inv_txn_to_model(self, d: InvestmentTransaction) -> InvestmentTransactionModel:
        return InvestmentTransactionModel(
            investment_id=d.investment_id,
            transaction_type=d.transaction_type,
            transaction_date=d.transaction_date,
            quantity=d.quantity,
            price=d.price,
            total_amount=d.total_amount,
            fee=d.fee,
            gain_loss=d.gain_loss,
            counterparty_ref=d.counterparty_ref,
            notes=d.notes,
        )

    def create_investment_txn(self, txn: InvestmentTransaction) -> Result:
        model = self._inv_txn_to_model(txn)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._inv_txn_to_domain(model))

    def get_transactions_for_investment(self, investment_id: int) -> List[InvestmentTransaction]:
        models = self.session.execute(
            select(InvestmentTransactionModel)
            .where(InvestmentTransactionModel.investment_id == investment_id)
            .order_by(InvestmentTransactionModel.transaction_date)
        ).scalars().all()
        return [self._inv_txn_to_domain(m) for m in models]

    # ── Loan ──────────────────────────────────────────────────────────

    def _loan_to_domain(self, m: LoanModel) -> Loan:
        d = Loan(
            loan_code=m.loan_code,
            loan_name=m.loan_name,
            loan_type=LoanType(m.loan_type),
            status=LoanStatus(m.status),
            principal=m.principal,
            outstanding_balance=m.outstanding_balance,
            interest_rate=m.interest_rate,
            interest_basis=m.interest_basis,
            drawdown_date=m.drawdown_date,
            maturity_date=m.maturity_date,
            repayment_frequency=m.repayment_frequency,
            repayment_day=m.repayment_day,
            lender_name=m.lender_name,
            lender_id=m.lender_id,
            currency=m.currency,
            coa_code=m.coa_code,
            coa_interest_code=m.coa_interest_code,
            covenant_dscr_min=m.covenant_dscr_min,
            covenant_icr_min=m.covenant_icr_min,
            covenant_ltv_max=m.covenant_ltv_max,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _loan_to_model(self, d: Loan) -> LoanModel:
        return LoanModel(
            loan_code=d.loan_code,
            loan_name=d.loan_name,
            loan_type=d.loan_type.value,
            status=d.status.value,
            principal=d.principal,
            outstanding_balance=d.outstanding_balance,
            interest_rate=d.interest_rate,
            interest_basis=d.interest_basis,
            drawdown_date=d.drawdown_date,
            maturity_date=d.maturity_date,
            repayment_frequency=d.repayment_frequency,
            repayment_day=d.repayment_day,
            lender_name=d.lender_name,
            lender_id=d.lender_id,
            currency=d.currency,
            coa_code=d.coa_code,
            coa_interest_code=d.coa_interest_code,
            covenant_dscr_min=d.covenant_dscr_min,
            covenant_icr_min=d.covenant_icr_min,
            covenant_ltv_max=d.covenant_ltv_max,
            notes=d.notes,
        )

    def create_loan(self, loan: Loan) -> Result:
        existing = self.session.execute(
            select(LoanModel).where(LoanModel.loan_code == loan.loan_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="Loan", id=loan.loan_code))
        model = self._loan_to_model(loan)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._loan_to_domain(model))

    def get_loan(self, loan_id: int) -> Optional[Loan]:
        m = self.session.get(LoanModel, loan_id)
        return self._loan_to_domain(m) if m else None

    def get_loan_by_code(self, code: str) -> Optional[Loan]:
        m = self.session.execute(
            select(LoanModel).where(LoanModel.loan_code == code)
        ).scalar_one_or_none()
        return self._loan_to_domain(m) if m else None

    def list_loans(
        self,
        loan_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Loan]:
        stmt = select(LoanModel)
        if loan_type:
            stmt = stmt.where(LoanModel.loan_type == loan_type)
        if status:
            stmt = stmt.where(LoanModel.status == status)
        stmt = stmt.order_by(LoanModel.drawdown_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._loan_to_domain(m) for m in models]

    def update_loan(self, loan_id: int, **updates) -> Optional[Loan]:
        model = self.session.get(LoanModel, loan_id)
        if not model:
            return None
        allowed = ("loan_name", "loan_type", "status", "principal",
                   "outstanding_balance", "interest_rate", "interest_basis",
                   "drawdown_date", "maturity_date", "repayment_frequency",
                   "repayment_day", "lender_name", "lender_id", "currency",
                   "coa_code", "coa_interest_code",
                   "covenant_dscr_min", "covenant_icr_min", "covenant_ltv_max", "notes")
        for k, v in updates.items():
            if k in allowed:
                if isinstance(v, (LoanType, LoanStatus)):
                    setattr(model, k, v.value)
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._loan_to_domain(model)

    def get_total_outstanding_loans(self) -> Decimal:
        result = self.session.execute(
            select(func.coalesce(func.sum(LoanModel.outstanding_balance), Decimal("0")))
            .where(LoanModel.status.in_(["active", "refinanced"]))
        ).scalar_one()
        return _vnd(result)

    # ── LoanPayment ───────────────────────────────────────────────────

    def _loan_pmt_to_domain(self, m: LoanPaymentModel) -> LoanPayment:
        d = LoanPayment(
            loan_id=m.loan_id,
            payment_date=m.payment_date,
            principal_amount=m.principal_amount,
            interest_amount=m.interest_amount,
            total_amount=m.total_amount,
            is_scheduled=m.is_scheduled,
            is_early_repayment=m.is_early_repayment,
            early_repayment_penalty=m.early_repayment_penalty,
            status=m.status,
            reference=m.reference,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _loan_pmt_to_model(self, d: LoanPayment) -> LoanPaymentModel:
        return LoanPaymentModel(
            loan_id=d.loan_id,
            payment_date=d.payment_date,
            principal_amount=d.principal_amount,
            interest_amount=d.interest_amount,
            total_amount=d.total_amount,
            is_scheduled=d.is_scheduled,
            is_early_repayment=d.is_early_repayment,
            early_repayment_penalty=d.early_repayment_penalty,
            status=d.status,
            reference=d.reference,
        )

    def create_loan_payment(self, payment: LoanPayment) -> Result:
        model = self._loan_pmt_to_model(payment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._loan_pmt_to_domain(model))

    def get_loan_payments(self, loan_id: int) -> List[LoanPayment]:
        models = self.session.execute(
            select(LoanPaymentModel).where(LoanPaymentModel.loan_id == loan_id)
            .order_by(LoanPaymentModel.payment_date)
        ).scalars().all()
        return [self._loan_pmt_to_domain(m) for m in models]

    def get_upcoming_loan_payments(self, days: int = 30) -> List[LoanPayment]:
        from datetime import timedelta
        today = date.today()
        end = today + timedelta(days=days)
        models = self.session.execute(
            select(LoanPaymentModel)
            .where(LoanPaymentModel.payment_date.between(today, end))
            .where(LoanPaymentModel.status == "pending")
            .order_by(LoanPaymentModel.payment_date)
        ).scalars().all()
        return [self._loan_pmt_to_domain(m) for m in models]

    def update_loan_payment(self, payment_id: int, **updates) -> Optional[LoanPayment]:
        model = self.session.get(LoanPaymentModel, payment_id)
        if not model:
            return None
        allowed = ("principal_amount", "interest_amount", "total_amount",
                   "is_scheduled", "is_early_repayment", "early_repayment_penalty",
                   "status", "reference")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._loan_pmt_to_domain(model)

    # ── FXForward ─────────────────────────────────────────────────────

    def _fxfwd_to_domain(self, m: FXForwardModel) -> FXForward:
        d = FXForward(
            contract_number=m.contract_number,
            base_currency=m.base_currency,
            target_currency=m.target_currency,
            amount=m.amount,
            forward_rate=m.forward_rate,
            value_date=m.value_date,
            maturity_date=m.maturity_date,
            counterparty=m.counterparty,
            status=FXForwardStatus(m.status),
            settlement_amount=m.settlement_amount,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _fxfwd_to_model(self, d: FXForward) -> FXForwardModel:
        return FXForwardModel(
            contract_number=d.contract_number,
            base_currency=d.base_currency,
            target_currency=d.target_currency,
            amount=d.amount,
            forward_rate=d.forward_rate,
            value_date=d.value_date,
            maturity_date=d.maturity_date,
            counterparty=d.counterparty,
            status=d.status.value,
            settlement_amount=d.settlement_amount,
            notes=d.notes,
        )

    def create_fx_forward(self, ff: FXForward) -> Result:
        existing = self.session.execute(
            select(FXForwardModel).where(FXForwardModel.contract_number == ff.contract_number)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="FXForward", id=ff.contract_number))
        model = self._fxfwd_to_model(ff)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fxfwd_to_domain(model))

    def get_fx_forward(self, fx_id: int) -> Optional[FXForward]:
        m = self.session.get(FXForwardModel, fx_id)
        return self._fxfwd_to_domain(m) if m else None

    def list_fx_forwards(
        self, status: Optional[str] = None, limit: int = 50, offset: int = 0,
    ) -> List[FXForward]:
        stmt = select(FXForwardModel)
        if status:
            stmt = stmt.where(FXForwardModel.status == status)
        stmt = stmt.order_by(FXForwardModel.value_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._fxfwd_to_domain(m) for m in models]

    def update_fx_forward(self, fx_id: int, **updates) -> Optional[FXForward]:
        model = self.session.get(FXForwardModel, fx_id)
        if not model:
            return None
        allowed = ("base_currency", "target_currency", "amount", "forward_rate",
                   "value_date", "maturity_date", "counterparty", "status",
                   "settlement_amount", "notes")
        for k, v in updates.items():
            if k in allowed:
                if isinstance(v, FXForwardStatus):
                    setattr(model, k, v.value)
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._fxfwd_to_domain(model)

    # ── CashFlowForecast ──────────────────────────────────────────────

    def _forecast_to_domain(self, m: CashFlowForecastModel) -> CashFlowForecast:
        d = CashFlowForecast(
            forecast_name=m.forecast_name,
            horizon=m.horizon,
            scenario=m.scenario,
            currency=m.currency,
            opening_balance=m.opening_balance,
            total_inflows=m.total_inflows,
            total_outflows=m.total_outflows,
            closing_balance=m.closing_balance,
            min_balance_threshold=m.min_balance_threshold,
            min_balance_breach=m.min_balance_breach,
            surplus_threshold=m.surplus_threshold,
            surplus_identified=m.surplus_identified,
            forecast_date=m.forecast_date,
            period=m.period,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _forecast_to_model(self, d: CashFlowForecast) -> CashFlowForecastModel:
        return CashFlowForecastModel(
            forecast_name=d.forecast_name,
            horizon=d.horizon,
            scenario=d.scenario,
            currency=d.currency,
            opening_balance=d.opening_balance,
            total_inflows=d.total_inflows,
            total_outflows=d.total_outflows,
            closing_balance=d.closing_balance,
            min_balance_threshold=d.min_balance_threshold,
            min_balance_breach=d.min_balance_breach,
            surplus_threshold=d.surplus_threshold,
            surplus_identified=d.surplus_identified,
            forecast_date=d.forecast_date,
            period=d.period,
            notes=d.notes,
        )

    def create_forecast(self, forecast: CashFlowForecast) -> Result:
        model = self._forecast_to_model(forecast)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._forecast_to_domain(model))

    def get_forecast(self, forecast_id: int) -> Optional[CashFlowForecast]:
        m = self.session.get(CashFlowForecastModel, forecast_id)
        return self._forecast_to_domain(m) if m else None

    def list_forecasts(
        self,
        period: Optional[str] = None,
        horizon: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[CashFlowForecast]:
        stmt = select(CashFlowForecastModel)
        if period:
            stmt = stmt.where(CashFlowForecastModel.period == period)
        if horizon:
            stmt = stmt.where(CashFlowForecastModel.horizon == horizon)
        stmt = stmt.order_by(CashFlowForecastModel.forecast_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._forecast_to_domain(m) for m in models]

    def update_forecast(self, forecast_id: int, **updates) -> Optional[CashFlowForecast]:
        model = self.session.get(CashFlowForecastModel, forecast_id)
        if not model:
            return None
        allowed = ("forecast_name", "horizon", "scenario", "currency",
                   "opening_balance", "total_inflows", "total_outflows",
                   "closing_balance", "min_balance_threshold", "min_balance_breach",
                   "surplus_threshold", "surplus_identified", "forecast_date",
                   "period", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._forecast_to_domain(model)

    # ── ForecastLine ──────────────────────────────────────────────────

    def _fcl_to_domain(self, m: ForecastLineModel) -> ForecastLine:
        d = ForecastLine(
            forecast_id=m.forecast_id,
            line_type=m.line_type,
            description=m.description,
            expected_amount=m.expected_amount,
            expected_date=m.expected_date,
            confidence_pct=m.confidence_pct,
            source_module=m.source_module,
            source_reference=m.source_reference,
            is_manual=m.is_manual,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _fcl_to_model(self, d: ForecastLine) -> ForecastLineModel:
        return ForecastLineModel(
            forecast_id=d.forecast_id,
            line_type=d.line_type,
            description=d.description,
            expected_amount=d.expected_amount,
            expected_date=d.expected_date,
            confidence_pct=d.confidence_pct,
            source_module=d.source_module,
            source_reference=d.source_reference,
            is_manual=d.is_manual,
        )

    def add_forecast_line(self, line: ForecastLine) -> Result:
        model = self._fcl_to_model(line)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fcl_to_domain(model))

    def get_forecast_lines(self, forecast_id: int) -> List[ForecastLine]:
        models = self.session.execute(
            select(ForecastLineModel).where(ForecastLineModel.forecast_id == forecast_id)
            .order_by(ForecastLineModel.expected_date)
        ).scalars().all()
        return [self._fcl_to_domain(m) for m in models]

    def update_forecast_line(self, line_id: int, **updates) -> Optional[ForecastLine]:
        model = self.session.get(ForecastLineModel, line_id)
        if not model:
            return None
        allowed = ("line_type", "description", "expected_amount", "expected_date",
                   "confidence_pct", "source_module", "source_reference", "is_manual")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._fcl_to_domain(model)

    def remove_forecast_line(self, line_id: int) -> bool:
        model = self.session.get(ForecastLineModel, line_id)
        if not model:
            return False
        self.session.delete(model)
        return True

    # ── TreasuryPosition ──────────────────────────────────────────────

    def _pos_to_domain(self, m: TreasuryPositionModel) -> TreasuryPosition:
        d = TreasuryPosition(
            snapshot_date=m.snapshot_date,
            currency=m.currency,
            total_cash=m.total_cash,
            total_bank=m.total_bank,
            total_cash_in_transit=m.total_cash_in_transit,
            total_blocked=m.total_blocked,
            total_available=m.total_available,
            total_investments=m.total_investments,
            total_loans=m.total_loans,
            net_liquidity=m.net_liquidity,
            entity_id=m.entity_id,
            generated_at=m.generated_at,
        )
        d.id = m.id
        return d

    def _pos_to_model(self, d: TreasuryPosition) -> TreasuryPositionModel:
        return TreasuryPositionModel(
            snapshot_date=d.snapshot_date,
            currency=d.currency,
            total_cash=d.total_cash,
            total_bank=d.total_bank,
            total_cash_in_transit=d.total_cash_in_transit,
            total_blocked=d.total_blocked,
            total_available=d.total_available,
            total_investments=d.total_investments,
            total_loans=d.total_loans,
            net_liquidity=d.net_liquidity,
            entity_id=d.entity_id,
        )

    def create_treasury_position(self, pos: TreasuryPosition) -> Result:
        model = self._pos_to_model(pos)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._pos_to_domain(model))

    def get_treasury_position(self, pos_id: int) -> Optional[TreasuryPosition]:
        m = self.session.get(TreasuryPositionModel, pos_id)
        return self._pos_to_domain(m) if m else None

    def get_latest_position(self, entity_id: Optional[str] = None) -> Optional[TreasuryPosition]:
        stmt = select(TreasuryPositionModel).order_by(TreasuryPositionModel.snapshot_date.desc())
        if entity_id:
            stmt = stmt.where(TreasuryPositionModel.entity_id == entity_id)
        stmt = stmt.limit(1)
        m = self.session.execute(stmt).scalars().first()
        return self._pos_to_domain(m) if m else None

    def list_positions(
        self,
        snapshot_date: Optional[date] = None,
        entity_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TreasuryPosition]:
        stmt = select(TreasuryPositionModel)
        if snapshot_date:
            stmt = stmt.where(TreasuryPositionModel.snapshot_date == snapshot_date)
        if entity_id:
            stmt = stmt.where(TreasuryPositionModel.entity_id == entity_id)
        stmt = stmt.order_by(TreasuryPositionModel.snapshot_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._pos_to_domain(m) for m in models]

    # ── FXExposure ────────────────────────────────────────────────────

    def _fx_exp_to_domain(self, m: FXExposureModel) -> FXExposure:
        d = FXExposure(
            snapshot_date=m.snapshot_date,
            currency=m.currency,
            total_long=m.total_long,
            total_short=m.total_short,
            net_exposure=m.net_exposure,
            vnd_equivalent=m.vnd_equivalent,
            exchange_rate=m.exchange_rate,
            rate_source=m.rate_source,
            unrealized_gain_loss=m.unrealized_gain_loss,
            policy_limit=m.policy_limit,
            threshold_breached=m.threshold_breached,
            entity_id=m.entity_id,
            generated_at=m.generated_at,
        )
        d.id = m.id
        return d

    def _fx_exp_to_model(self, d: FXExposure) -> FXExposureModel:
        return FXExposureModel(
            snapshot_date=d.snapshot_date,
            currency=d.currency,
            total_long=d.total_long,
            total_short=d.total_short,
            net_exposure=d.net_exposure,
            vnd_equivalent=d.vnd_equivalent,
            exchange_rate=d.exchange_rate,
            rate_source=d.rate_source,
            unrealized_gain_loss=d.unrealized_gain_loss,
            policy_limit=d.policy_limit,
            threshold_breached=d.threshold_breached,
            entity_id=d.entity_id,
        )

    def create_fx_exposure(self, fx: FXExposure) -> Result:
        model = self._fx_exp_to_model(fx)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fx_exp_to_domain(model))

    def get_latest_fx_exposure(
        self, currency: str, entity_id: Optional[str] = None,
    ) -> Optional[FXExposure]:
        stmt = select(FXExposureModel).where(
            FXExposureModel.currency == currency
        ).order_by(FXExposureModel.snapshot_date.desc())
        if entity_id:
            stmt = stmt.where(FXExposureModel.entity_id == entity_id)
        stmt = stmt.limit(1)
        m = self.session.execute(stmt).scalars().first()
        return self._fx_exp_to_domain(m) if m else None

    def list_fx_exposures(
        self, snapshot_date: Optional[date] = None,
    ) -> List[FXExposure]:
        stmt = select(FXExposureModel)
        if snapshot_date:
            stmt = stmt.where(FXExposureModel.snapshot_date == snapshot_date)
        stmt = stmt.order_by(FXExposureModel.currency)
        models = self.session.execute(stmt).scalars().all()
        return [self._fx_exp_to_domain(m) for m in models]

    # ── FXRate ────────────────────────────────────────────────────────

    def _fx_rate_to_domain(self, m: FXRateModel) -> FXRate:
        d = FXRate(
            currency=m.currency,
            rate_date=m.rate_date,
            rate_buying=m.rate_buying,
            rate_selling=m.rate_selling,
            rate_avg=m.rate_avg,
            rate_source=m.rate_source,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _fx_rate_to_model(self, d: FXRate) -> FXRateModel:
        return FXRateModel(
            currency=d.currency,
            rate_date=d.rate_date,
            rate_buying=d.rate_buying,
            rate_selling=d.rate_selling,
            rate_avg=d.rate_avg,
            rate_source=d.rate_source,
        )

    def upsert_fx_rate(self, rate: FXRate) -> Result:
        existing = self.session.execute(
            select(FXRateModel).where(
                FXRateModel.currency == rate.currency,
                FXRateModel.rate_date == rate.rate_date,
                FXRateModel.rate_source == rate.rate_source,
            )
        ).scalar_one_or_none()
        if existing:
            existing.rate_buying = rate.rate_buying
            existing.rate_selling = rate.rate_selling
            existing.rate_avg = rate.rate_avg
            self.session.flush()
            return Result.success(self._fx_rate_to_domain(existing))
        model = self._fx_rate_to_model(rate)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fx_rate_to_domain(model))

    def get_fx_rate(
        self, currency: str, rate_date: date, source: str = "bank_avg",
    ) -> Optional[FXRate]:
        m = self.session.execute(
            select(FXRateModel).where(
                FXRateModel.currency == currency,
                FXRateModel.rate_date == rate_date,
                FXRateModel.rate_source == source,
            )
        ).scalar_one_or_none()
        return self._fx_rate_to_domain(m) if m else None

    # ── IntercompanyLoan ──────────────────────────────────────────────

    def _ic_loan_to_domain(self, m: IntercompanyLoanModel) -> IntercompanyLoan:
        d = IntercompanyLoan(
            loan_code=m.loan_code,
            lender_entity_id=m.lender_entity_id,
            borrower_entity_id=m.borrower_entity_id,
            principal=m.principal,
            outstanding_balance=m.outstanding_balance,
            interest_rate=m.interest_rate,
            interest_basis=m.interest_basis,
            currency=m.currency,
            start_date=m.start_date,
            maturity_date=m.maturity_date,
            status=m.status,
            coa_receivable_code=m.coa_receivable_code,
            coa_payable_code=m.coa_payable_code,
            agreement_ref=m.agreement_ref,
            transfer_pricing_compliant=m.transfer_pricing_compliant,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _ic_loan_to_model(self, d: IntercompanyLoan) -> IntercompanyLoanModel:
        return IntercompanyLoanModel(
            loan_code=d.loan_code,
            lender_entity_id=d.lender_entity_id,
            borrower_entity_id=d.borrower_entity_id,
            principal=d.principal,
            outstanding_balance=d.outstanding_balance,
            interest_rate=d.interest_rate,
            interest_basis=d.interest_basis,
            currency=d.currency,
            start_date=d.start_date,
            maturity_date=d.maturity_date,
            status=d.status,
            coa_receivable_code=d.coa_receivable_code,
            coa_payable_code=d.coa_payable_code,
            agreement_ref=d.agreement_ref,
            transfer_pricing_compliant=d.transfer_pricing_compliant,
            notes=d.notes,
        )

    def create_ic_loan(self, loan: IntercompanyLoan) -> Result:
        existing = self.session.execute(
            select(IntercompanyLoanModel).where(IntercompanyLoanModel.loan_code == loan.loan_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="IntercompanyLoan", id=loan.loan_code))
        model = self._ic_loan_to_model(loan)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._ic_loan_to_domain(model))

    def get_ic_loan(self, loan_id: int) -> Optional[IntercompanyLoan]:
        m = self.session.get(IntercompanyLoanModel, loan_id)
        return self._ic_loan_to_domain(m) if m else None

    def get_ic_loan_by_code(self, code: str) -> Optional[IntercompanyLoan]:
        m = self.session.execute(
            select(IntercompanyLoanModel).where(IntercompanyLoanModel.loan_code == code)
        ).scalar_one_or_none()
        return self._ic_loan_to_domain(m) if m else None

    def list_ic_loans(
        self,
        lender: Optional[str] = None,
        borrower: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[IntercompanyLoan]:
        stmt = select(IntercompanyLoanModel)
        if lender:
            stmt = stmt.where(IntercompanyLoanModel.lender_entity_id == lender)
        if borrower:
            stmt = stmt.where(IntercompanyLoanModel.borrower_entity_id == borrower)
        if status:
            stmt = stmt.where(IntercompanyLoanModel.status == status)
        stmt = stmt.order_by(IntercompanyLoanModel.start_date.desc())
        models = self.session.execute(stmt).scalars().all()
        return [self._ic_loan_to_domain(m) for m in models]

    def update_ic_loan(self, loan_id: int, **updates) -> Optional[IntercompanyLoan]:
        model = self.session.get(IntercompanyLoanModel, loan_id)
        if not model:
            return None
        allowed = ("principal", "outstanding_balance", "interest_rate",
                   "interest_basis", "currency", "start_date", "maturity_date",
                   "status", "coa_receivable_code", "coa_payable_code",
                   "agreement_ref", "transfer_pricing_compliant", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._ic_loan_to_domain(model)

    # ── IntercompanySweep ─────────────────────────────────────────────

    def _ic_sweep_to_domain(self, m: IntercompanySweepModel) -> IntercompanySweep:
        d = IntercompanySweep(
            sweep_type=SweepType(m.sweep_type),
            status=m.status,
            sweep_date=m.sweep_date,
            source_entity_id=m.source_entity_id,
            target_entity_id=m.target_entity_id,
            amount=m.amount,
            source_acct_type=m.source_acct_type,
            source_acct_id=m.source_acct_id,
            target_acct_type=m.target_acct_type,
            target_acct_id=m.target_acct_id,
            target_balance_after=m.target_balance_after,
            ic_loan_id=m.ic_loan_id,
            approved_by=m.approved_by,
            executed_at=m.executed_at,
            notes=m.notes,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _ic_sweep_to_model(self, d: IntercompanySweep) -> IntercompanySweepModel:
        return IntercompanySweepModel(
            sweep_type=d.sweep_type.value,
            status=d.status.value if hasattr(d.status, 'value') else d.status,
            sweep_date=d.sweep_date,
            source_entity_id=d.source_entity_id,
            target_entity_id=d.target_entity_id,
            amount=d.amount,
            source_acct_type=d.source_acct_type,
            source_acct_id=d.source_acct_id,
            target_acct_type=d.target_acct_type,
            target_acct_id=d.target_acct_id,
            target_balance_after=d.target_balance_after,
            ic_loan_id=d.ic_loan_id,
            approved_by=d.approved_by,
            executed_at=d.executed_at,
            notes=d.notes,
        )

    def create_ic_sweep(self, sweep: IntercompanySweep) -> Result:
        model = self._ic_sweep_to_model(sweep)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._ic_sweep_to_domain(model))

    def get_ic_sweep(self, sweep_id: int) -> Optional[IntercompanySweep]:
        m = self.session.get(IntercompanySweepModel, sweep_id)
        return self._ic_sweep_to_domain(m) if m else None

    def list_ic_sweeps(
        self,
        entity_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[IntercompanySweep]:
        stmt = select(IntercompanySweepModel)
        if entity_id:
            stmt = stmt.where(
                (IntercompanySweepModel.source_entity_id == entity_id) |
                (IntercompanySweepModel.target_entity_id == entity_id)
            )
        if status:
            stmt = stmt.where(IntercompanySweepModel.status == status)
        stmt = stmt.order_by(IntercompanySweepModel.sweep_date.desc()).limit(limit)
        models = self.session.execute(stmt).scalars().all()
        return [self._ic_sweep_to_domain(m) for m in models]

    def update_ic_sweep(self, sweep_id: int, **updates) -> Optional[IntercompanySweep]:
        model = self.session.get(IntercompanySweepModel, sweep_id)
        if not model:
            return None
        allowed = ("sweep_type", "status", "sweep_date", "source_entity_id",
                   "target_entity_id", "amount", "source_acct_type", "source_acct_id",
                   "target_acct_type", "target_acct_id", "target_balance_after",
                   "ic_loan_id", "approved_by", "executed_at", "notes")
        for k, v in updates.items():
            if k in allowed:
                if isinstance(v, SweepType):
                    setattr(model, k, v.value)
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._ic_sweep_to_domain(model)

    # ── PaymentBatch ──────────────────────────────────────────────────

    def _batch_to_domain(self, m: PaymentBatchModel) -> PaymentBatch:
        d = PaymentBatch(
            batch_code=m.batch_code,
            status=m.status,
            payment_date=m.payment_date,
            currency=m.currency,
            total_amount=m.total_amount,
            item_count=m.item_count,
            approved_by=m.approved_by,
            approved_at=m.approved_at,
            submitted_at=m.submitted_at,
            bank_ref=m.bank_ref,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _batch_to_model(self, d: PaymentBatch) -> PaymentBatchModel:
        return PaymentBatchModel(
            batch_code=d.batch_code,
            status=d.status.value if hasattr(d.status, 'value') else d.status,
            payment_date=d.payment_date,
            currency=d.currency,
            total_amount=d.total_amount,
            item_count=d.item_count,
            approved_by=d.approved_by,
            approved_at=d.approved_at,
            submitted_at=d.submitted_at,
            bank_ref=d.bank_ref,
            notes=d.notes,
        )

    def create_payment_batch(self, batch: PaymentBatch) -> Result:
        existing = self.session.execute(
            select(PaymentBatchModel).where(PaymentBatchModel.batch_code == batch.batch_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="PaymentBatch", id=batch.batch_code))
        model = self._batch_to_model(batch)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._batch_to_domain(model))

    def get_payment_batch(self, batch_id: int) -> Optional[PaymentBatch]:
        m = self.session.get(PaymentBatchModel, batch_id)
        return self._batch_to_domain(m) if m else None

    def get_payment_batch_by_code(self, code: str) -> Optional[PaymentBatch]:
        m = self.session.execute(
            select(PaymentBatchModel).where(PaymentBatchModel.batch_code == code)
        ).scalar_one_or_none()
        return self._batch_to_domain(m) if m else None

    def list_payment_batches(
        self, status: Optional[str] = None, limit: int = 50, offset: int = 0,
    ) -> List[PaymentBatch]:
        stmt = select(PaymentBatchModel)
        if status:
            stmt = stmt.where(PaymentBatchModel.status == status)
        stmt = stmt.order_by(PaymentBatchModel.payment_date.desc()).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._batch_to_domain(m) for m in models]

    def update_payment_batch(self, batch_id: int, **updates) -> Optional[PaymentBatch]:
        model = self.session.get(PaymentBatchModel, batch_id)
        if not model:
            return None
        allowed = ("status", "payment_date", "currency", "total_amount",
                   "item_count", "approved_by", "approved_at", "submitted_at",
                   "bank_ref", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._batch_to_domain(model)

    # ── PaymentBatchItem ──────────────────────────────────────────────

    def _batch_item_to_domain(self, m: PaymentBatchItemModel) -> PaymentBatchItem:
        d = PaymentBatchItem(
            batch_id=m.batch_id,
            source_module=m.source_module,
            source_id=m.source_id,
            source_reference=m.source_reference,
            payee_name=m.payee_name,
            payee_account=m.payee_account,
            payee_bank=m.payee_bank,
            amount=m.amount,
            currency=m.currency,
            status=m.status,
            bank_txn_ref=m.bank_txn_ref,
            rejection_reason=m.rejection_reason,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _batch_item_to_model(self, d: PaymentBatchItem) -> PaymentBatchItemModel:
        return PaymentBatchItemModel(
            batch_id=d.batch_id,
            source_module=d.source_module,
            source_id=d.source_id,
            source_reference=d.source_reference,
            payee_name=d.payee_name,
            payee_account=d.payee_account,
            payee_bank=d.payee_bank,
            amount=d.amount,
            currency=d.currency,
            status=d.status.value if hasattr(d.status, 'value') else d.status,
            bank_txn_ref=d.bank_txn_ref,
            rejection_reason=d.rejection_reason,
        )

    def add_batch_item(self, item: PaymentBatchItem) -> Result:
        model = self._batch_item_to_model(item)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._batch_item_to_domain(model))

    def get_batch_items(self, batch_id: int) -> List[PaymentBatchItem]:
        models = self.session.execute(
            select(PaymentBatchItemModel).where(PaymentBatchItemModel.batch_id == batch_id)
            .order_by(PaymentBatchItemModel.created_at)
        ).scalars().all()
        return [self._batch_item_to_domain(m) for m in models]

    def update_batch_item(self, item_id: int, **updates) -> Optional[PaymentBatchItem]:
        model = self.session.get(PaymentBatchItemModel, item_id)
        if not model:
            return None
        allowed = ("status", "bank_txn_ref", "rejection_reason", "payee_name",
                   "payee_account", "payee_bank", "amount", "currency")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._batch_item_to_domain(model)

    # ── BankConnectorConfig ───────────────────────────────────────────

    def _connector_to_domain(self, m: BankConnectorConfigModel) -> BankConnectorConfig:
        d = BankConnectorConfig(
            bank_code=m.bank_code,
            bank_name=m.bank_name,
            api_endpoint=m.api_endpoint,
            api_version=m.api_version,
            auth_type=m.auth_type,
            credentials_encrypted=m.credentials_encrypted,
            sync_frequency_minutes=m.sync_frequency_minutes,
            last_sync_at=m.last_sync_at,
            is_active=m.is_active,
            supports_balance=m.supports_balance,
            supports_transactions=m.supports_transactions,
            supports_statements=m.supports_statements,
            ip_whitelist=m.ip_whitelist,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _connector_to_model(self, d: BankConnectorConfig) -> BankConnectorConfigModel:
        return BankConnectorConfigModel(
            bank_code=d.bank_code,
            bank_name=d.bank_name,
            api_endpoint=d.api_endpoint,
            api_version=d.api_version,
            auth_type=d.auth_type,
            credentials_encrypted=d.credentials_encrypted,
            sync_frequency_minutes=d.sync_frequency_minutes,
            last_sync_at=d.last_sync_at,
            is_active=d.is_active,
            supports_balance=d.supports_balance,
            supports_transactions=d.supports_transactions,
            supports_statements=d.supports_statements,
            ip_whitelist=d.ip_whitelist,
        )

    def create_connector(self, config: BankConnectorConfig) -> Result:
        existing = self.session.execute(
            select(BankConnectorConfigModel).where(BankConnectorConfigModel.bank_code == config.bank_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="BankConnectorConfig", id=config.bank_code))
        model = self._connector_to_model(config)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._connector_to_domain(model))

    def get_connector(self, connector_id: int) -> Optional[BankConnectorConfig]:
        m = self.session.get(BankConnectorConfigModel, connector_id)
        return self._connector_to_domain(m) if m else None

    def get_connector_by_code(self, code: str) -> Optional[BankConnectorConfig]:
        m = self.session.execute(
            select(BankConnectorConfigModel).where(BankConnectorConfigModel.bank_code == code)
        ).scalar_one_or_none()
        return self._connector_to_domain(m) if m else None

    def list_connectors(self, active_only: bool = False) -> List[BankConnectorConfig]:
        stmt = select(BankConnectorConfigModel)
        if active_only:
            stmt = stmt.where(BankConnectorConfigModel.is_active.is_(True))
        stmt = stmt.order_by(BankConnectorConfigModel.bank_code)
        models = self.session.execute(stmt).scalars().all()
        return [self._connector_to_domain(m) for m in models]

    def update_connector(self, connector_id: int, **updates) -> Optional[BankConnectorConfig]:
        model = self.session.get(BankConnectorConfigModel, connector_id)
        if not model:
            return None
        allowed = ("bank_name", "api_endpoint", "api_version", "auth_type",
                   "credentials_encrypted", "sync_frequency_minutes", "last_sync_at",
                   "is_active", "supports_balance", "supports_transactions",
                   "supports_statements", "ip_whitelist")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._connector_to_domain(model)

    # ── BankSyncLog ───────────────────────────────────────────────────

    def _sync_log_to_domain(self, m: BankSyncLogModel) -> BankSyncLog:
        d = BankSyncLog(
            connector_id=m.connector_id,
            sync_type=m.sync_type,
            sync_status=m.sync_status,
            started_at=m.started_at,
            completed_at=m.completed_at,
            transactions_fetched=m.transactions_fetched,
            transactions_matched=m.transactions_matched,
            transactions_unmatched=m.transactions_unmatched,
            error_message=m.error_message,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _sync_log_to_model(self, d: BankSyncLog) -> BankSyncLogModel:
        return BankSyncLogModel(
            connector_id=d.connector_id,
            sync_type=d.sync_type,
            sync_status=d.sync_status.value if hasattr(d.sync_status, 'value') else d.sync_status,
            started_at=d.started_at,
            completed_at=d.completed_at,
            transactions_fetched=d.transactions_fetched,
            transactions_matched=d.transactions_matched,
            transactions_unmatched=d.transactions_unmatched,
            error_message=d.error_message,
        )

    def create_sync_log(self, log: BankSyncLog) -> Result:
        model = self._sync_log_to_model(log)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._sync_log_to_domain(model))

    def get_sync_logs(self, connector_id: int, limit: int = 50) -> List[BankSyncLog]:
        models = self.session.execute(
            select(BankSyncLogModel).where(BankSyncLogModel.connector_id == connector_id)
            .order_by(BankSyncLogModel.started_at.desc()).limit(limit)
        ).scalars().all()
        return [self._sync_log_to_domain(m) for m in models]

    # ── TreasuryPolicy ────────────────────────────────────────────────

    def _policy_to_domain(self, m: TreasuryPolicyModel) -> TreasuryPolicy:
        d = TreasuryPolicy(
            policy_code=m.policy_code,
            policy_name=m.policy_name,
            policy_type=m.policy_type,
            threshold_value=m.threshold_value,
            threshold_pct=m.threshold_pct,
            min_value=m.min_value,
            max_value=m.max_value,
            counterparty_restriction=m.counterparty_restriction,
            active=m.active,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _policy_to_model(self, d: TreasuryPolicy) -> TreasuryPolicyModel:
        return TreasuryPolicyModel(
            policy_code=d.policy_code,
            policy_name=d.policy_name,
            policy_type=d.policy_type,
            threshold_value=d.threshold_value,
            threshold_pct=d.threshold_pct,
            min_value=d.min_value,
            max_value=d.max_value,
            counterparty_restriction=d.counterparty_restriction,
            active=d.active,
            notes=d.notes,
        )

    def create_policy(self, policy: TreasuryPolicy) -> Result:
        existing = self.session.execute(
            select(TreasuryPolicyModel).where(TreasuryPolicyModel.policy_code == policy.policy_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.ALREADY_EXISTS, type="TreasuryPolicy", id=policy.policy_code))
        model = self._policy_to_model(policy)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._policy_to_domain(model))

    def get_policy(self, policy_id: int) -> Optional[TreasuryPolicy]:
        m = self.session.get(TreasuryPolicyModel, policy_id)
        return self._policy_to_domain(m) if m else None

    def get_policy_by_code(self, code: str) -> Optional[TreasuryPolicy]:
        m = self.session.execute(
            select(TreasuryPolicyModel).where(TreasuryPolicyModel.policy_code == code)
        ).scalar_one_or_none()
        return self._policy_to_domain(m) if m else None

    def list_policies(
        self,
        policy_type: Optional[str] = None,
        active_only: bool = False,
    ) -> List[TreasuryPolicy]:
        stmt = select(TreasuryPolicyModel)
        if policy_type:
            stmt = stmt.where(TreasuryPolicyModel.policy_type == policy_type)
        if active_only:
            stmt = stmt.where(TreasuryPolicyModel.active.is_(True))
        stmt = stmt.order_by(TreasuryPolicyModel.policy_code)
        models = self.session.execute(stmt).scalars().all()
        return [self._policy_to_domain(m) for m in models]

    def update_policy(self, policy_id: int, **updates) -> Optional[TreasuryPolicy]:
        model = self.session.get(TreasuryPolicyModel, policy_id)
        if not model:
            return None
        allowed = ("policy_name", "policy_type", "threshold_value", "threshold_pct",
                   "min_value", "max_value", "counterparty_restriction", "active", "notes")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._policy_to_domain(model)

    # ── TreasuryAuditLog ──────────────────────────────────────────────

    def _audit_to_domain(self, m: TreasuryAuditLogModel) -> TreasuryAuditLog:
        d = TreasuryAuditLog(
            entity_type=m.entity_type,
            entity_id=m.entity_id,
            action=m.action,
            old_value=m.old_value,
            new_value=m.new_value,
            performed_by=m.performed_by,
            notes=m.notes,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def log_audit(self, audit: TreasuryAuditLog) -> Result:
        model = TreasuryAuditLogModel(
            entity_type=audit.entity_type,
            entity_id=audit.entity_id,
            action=audit.action,
            old_value=audit.old_value,
            new_value=audit.new_value,
            performed_by=audit.performed_by,
            notes=audit.notes,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._audit_to_domain(model))

    def get_audit_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[TreasuryAuditLog]:
        stmt = select(TreasuryAuditLogModel)
        if entity_type:
            stmt = stmt.where(TreasuryAuditLogModel.entity_type == entity_type)
        if entity_id is not None:
            stmt = stmt.where(TreasuryAuditLogModel.entity_id == entity_id)
        stmt = stmt.order_by(TreasuryAuditLogModel.created_at.desc()).limit(limit)
        models = self.session.execute(stmt).scalars().all()
        return [self._audit_to_domain(m) for m in models]

    # ── Aggregation queries ──────────────────────────────────────────

    def get_total_cash_balance(self) -> Decimal:
        from infrastructure.models.cash_models import CashReceiptModel
        from infrastructure.models.cash_models import CashPaymentModel
        total_in = self.session.execute(
            select(func.coalesce(func.sum(CashReceiptModel.total_amount), Decimal("0")))
            .where(CashReceiptModel.status == "posted")
        ).scalar_one()
        total_out = self.session.execute(
            select(func.coalesce(func.sum(CashPaymentModel.total_amount), Decimal("0")))
            .where(CashPaymentModel.status == "posted")
        ).scalar_one()
        return _vnd(total_in - total_out)

    def get_total_bank_balance(self) -> Decimal:
        from infrastructure.models.cash_models import BankAccountModel
        result = self.session.execute(
            select(func.coalesce(func.sum(BankAccountModel.balance), Decimal("0")))
        ).scalar_one()
        return _vnd(result)

    def get_blocked_amount(self) -> Decimal:
        from infrastructure.models.cash_models import BankAccountModel
        result = self.session.execute(
            select(func.coalesce(func.sum(BankAccountModel.blocked_amount), Decimal("0")))
        ).scalar_one()
        return _vnd(result)
