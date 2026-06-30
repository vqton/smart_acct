from flask import Blueprint, current_app

trs_bp = Blueprint("treasury", __name__, url_prefix="/api/v1/treasury")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_cash_in_transit(c):
    return {
        "id": c.id, "reference": c.reference, "amount": str(c.amount),
        "currency": c.currency, "source_account_type": c.source_account_type,
        "source_account_id": c.source_account_id,
        "dest_account_type": c.dest_account_type,
        "dest_account_id": c.dest_account_id,
        "transfer_date": c.transfer_date.isoformat(),
        "expected_clear_date": c.expected_clear_date.isoformat(),
        "cleared": c.cleared, "cleared_at": c.cleared_at.isoformat() if c.cleared_at else None,
        "notes": c.notes, "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _json_investment(inv):
    return {
        "id": inv.id, "investment_code": inv.investment_code,
        "investment_name": inv.investment_name,
        "investment_type": inv.investment_type.value if hasattr(inv.investment_type, 'value') else inv.investment_type,
        "status": inv.status.value if hasattr(inv.status, 'value') else inv.status,
        "cost_price": str(inv.cost_price), "total_cost": str(inv.total_cost),
        "market_price": str(inv.market_price) if inv.market_price else None,
        "fair_value": str(inv.fair_value) if inv.fair_value else None,
        "counterparty_name": inv.counterparty_name,
        "purchase_date": inv.purchase_date.isoformat(),
        "maturity_date": inv.maturity_date.isoformat() if inv.maturity_date else None,
        "interest_rate": str(inv.interest_rate) if inv.interest_rate else None,
        "coa_code": inv.coa_code, "period": inv.period,
        "notes": inv.notes, "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }


def _json_loan(loan):
    return {
        "id": loan.id, "loan_code": loan.loan_code, "loan_name": loan.loan_name,
        "loan_type": loan.loan_type.value if hasattr(loan.loan_type, 'value') else loan.loan_type,
        "status": loan.status.value if hasattr(loan.status, 'value') else loan.status,
        "principal": str(loan.principal),
        "outstanding_balance": str(loan.outstanding_balance),
        "interest_rate": str(loan.interest_rate),
        "drawdown_date": loan.drawdown_date.isoformat(),
        "maturity_date": loan.maturity_date.isoformat(),
        "lender_name": loan.lender_name, "currency": loan.currency,
        "notes": loan.notes, "created_at": loan.created_at.isoformat() if loan.created_at else None,
        "updated_at": loan.updated_at.isoformat() if loan.updated_at else None,
    }


def _json_forecast(f):
    return {
        "id": f.id, "forecast_name": f.forecast_name,
        "horizon": f.horizon.value if hasattr(f.horizon, 'value') else f.horizon,
        "scenario": f.scenario.value if hasattr(f.scenario, 'value') else f.scenario,
        "currency": f.currency, "opening_balance": str(f.opening_balance),
        "total_inflows": str(f.total_inflows), "total_outflows": str(f.total_outflows),
        "closing_balance": str(f.closing_balance),
        "min_balance_breach": f.min_balance_breach,
        "surplus_identified": f.surplus_identified,
        "forecast_date": f.forecast_date.isoformat(), "period": f.period,
        "notes": f.notes, "created_at": f.created_at.isoformat() if f.created_at else None,
    }


def _json_position(pos):
    return {
        "id": pos.id, "snapshot_date": pos.snapshot_date.isoformat(),
        "currency": pos.currency, "total_cash": str(pos.total_cash),
        "total_bank": str(pos.total_bank),
        "total_cash_in_transit": str(pos.total_cash_in_transit),
        "total_blocked": str(pos.total_blocked),
        "total_available": str(pos.total_available),
        "total_investments": str(pos.total_investments),
        "total_loans": str(pos.total_loans),
        "net_liquidity": str(pos.net_liquidity),
        "entity_id": pos.entity_id,
        "generated_at": pos.generated_at.isoformat() if pos.generated_at else None,
    }


def _json_fx_exposure(fx):
    return {
        "id": fx.id, "snapshot_date": fx.snapshot_date.isoformat(),
        "currency": fx.currency, "net_exposure": str(fx.net_exposure),
        "vnd_equivalent": str(fx.vnd_equivalent),
        "exchange_rate": str(fx.exchange_rate),
        "unrealized_gain_loss": str(fx.unrealized_gain_loss),
        "threshold_breached": fx.threshold_breached,
        "entity_id": fx.entity_id,
    }


def _json_ic_loan(loan):
    return {
        "id": loan.id, "loan_code": loan.loan_code,
        "lender_entity_id": loan.lender_entity_id,
        "borrower_entity_id": loan.borrower_entity_id,
        "principal": str(loan.principal),
        "outstanding_balance": str(loan.outstanding_balance),
        "interest_rate": str(loan.interest_rate),
        "currency": loan.currency,
        "start_date": loan.start_date.isoformat(),
        "maturity_date": loan.maturity_date.isoformat(),
        "status": loan.status,
        "notes": loan.notes,
        "created_at": loan.created_at.isoformat() if loan.created_at else None,
    }


def _json_ic_sweep(s):
    return {
        "id": s.id, "sweep_type": s.sweep_type.value if hasattr(s.sweep_type, 'value') else s.sweep_type,
        "status": s.status.value if hasattr(s.status, 'value') else s.status,
        "sweep_date": s.sweep_date.isoformat(),
        "source_entity_id": s.source_entity_id,
        "target_entity_id": s.target_entity_id,
        "amount": str(s.amount),
        "approved_by": s.approved_by,
        "executed_at": s.executed_at.isoformat() if s.executed_at else None,
        "notes": s.notes,
    }


def _json_batch(b):
    return {
        "id": b.id, "batch_code": b.batch_code,
        "status": b.status.value if hasattr(b.status, 'value') else b.status,
        "payment_date": b.payment_date.isoformat(),
        "currency": b.currency, "total_amount": str(b.total_amount),
        "item_count": b.item_count,
        "approved_by": b.approved_by,
        "approved_at": b.approved_at.isoformat() if b.approved_at else None,
        "submitted_at": b.submitted_at.isoformat() if b.submitted_at else None,
        "bank_ref": b.bank_ref, "notes": b.notes,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


def _json_connector(c):
    return {
        "id": c.id, "bank_code": c.bank_code, "bank_name": c.bank_name,
        "api_endpoint": c.api_endpoint, "api_version": c.api_version,
        "auth_type": c.auth_type, "is_active": c.is_active,
        "sync_frequency_minutes": c.sync_frequency_minutes,
        "last_sync_at": c.last_sync_at.isoformat() if c.last_sync_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def _json_policy(p):
    return {
        "id": p.id, "policy_code": p.policy_code, "policy_name": p.policy_name,
        "policy_type": p.policy_type,
        "threshold_value": str(p.threshold_value) if p.threshold_value else None,
        "threshold_pct": str(p.threshold_pct) if p.threshold_pct else None,
        "min_value": str(p.min_value) if p.min_value else None,
        "max_value": str(p.max_value) if p.max_value else None,
        "active": p.active, "notes": p.notes,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def _json_kpi(d):
    return {k: str(v) if isinstance(v, Decimal) else v for k, v in d.items()}


from . import routes  # noqa: E402
