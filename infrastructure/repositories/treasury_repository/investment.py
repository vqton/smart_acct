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


class InvestmentMixin:
    """Mixin for Investment-related repository methods."""
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
        return _quantize_vnd(result)

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

