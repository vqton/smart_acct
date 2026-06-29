from flask import Blueprint, current_app, render_template

cash_bp = Blueprint("cash", __name__)


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_receipt(r) -> dict:
    return {
        "id": r.id,
        "receipt_number": r.receipt_number,
        "receipt_date": r.receipt_date.isoformat(),
        "receipt_type": r.receipt_type.value,
        "payer_name": r.payer_name,
        "amount": str(r.amount),
        "amount_in_words": r.amount_in_words,
        "currency": r.currency,
        "fx_rate": str(r.fx_rate) if r.fx_rate else None,
        "account_code": r.account_code,
        "counter_account": r.counter_account,
        "reference_number": r.reference_number,
        "description": r.description,
        "status": r.status.value,
        "created_by": r.created_by,
        "approved_by": r.approved_by,
        "approved_at": r.approved_at.isoformat() if r.approved_at else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }


def _json_payment(p) -> dict:
    return {
        "id": p.id,
        "payment_number": p.payment_number,
        "payment_date": p.payment_date.isoformat(),
        "payment_type": p.payment_type.value,
        "receiver_name": p.receiver_name,
        "amount": str(p.amount),
        "amount_in_words": p.amount_in_words,
        "currency": p.currency,
        "fx_rate": str(p.fx_rate) if p.fx_rate else None,
        "account_code": p.account_code,
        "counter_account": p.counter_account,
        "reference_number": p.reference_number,
        "supporting_doc_ref": p.supporting_doc_ref,
        "description": p.description,
        "status": p.status.value,
        "created_by": p.created_by,
        "approved_by": p.approved_by,
        "approved_at": p.approved_at.isoformat() if p.approved_at else None,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def _json_bank_account(ba) -> dict:
    return {
        "id": ba.id,
        "bank_name": ba.bank_name,
        "branch": ba.branch,
        "account_number": ba.account_number,
        "account_holder": ba.account_holder,
        "currency": ba.currency,
        "coa_code": ba.coa_code,
        "swift_code": ba.swift_code,
        "iban": ba.iban,
        "opening_balance": str(ba.opening_balance),
        "status": ba.status.value,
        "signatories": ba.signatories,
        "authorization_limit": str(ba.authorization_limit),
        "created_at": ba.created_at.isoformat() if ba.created_at else None,
        "updated_at": ba.updated_at.isoformat() if ba.updated_at else None,
    }


def _json_bank_transaction(t) -> dict:
    return {
        "id": t.id,
        "bank_account_id": t.bank_account_id,
        "statement_id": t.statement_id,
        "transaction_date": t.transaction_date.isoformat(),
        "value_date": t.value_date.isoformat() if t.value_date else None,
        "amount": str(t.amount),
        "is_debit": t.is_debit,
        "reference": t.reference,
        "description": t.description,
        "matched_entry_id": t.matched_entry_id,
    }


def _json_statement(s) -> dict:
    return {
        "id": s.id,
        "bank_account_id": s.bank_account_id,
        "statement_date": s.statement_date.isoformat(),
        "opening_balance": str(s.opening_balance),
        "closing_balance": str(s.closing_balance),
        "source": s.source,
        "imported_at": s.imported_at.isoformat() if s.imported_at else None,
        "transactions": [_json_bank_transaction(t) for t in s.transactions],
    }


def _json_reconciliation(r) -> dict:
    return {
        "id": r.id,
        "bank_account_id": r.bank_account_id,
        "period": r.period,
        "book_balance": str(r.book_balance),
        "bank_balance": str(r.bank_balance),
        "deposits_in_transit": str(r.deposits_in_transit),
        "outstanding_checks": str(r.outstanding_checks),
        "unrecorded_credits": str(r.unrecorded_credits),
        "unrecorded_debits": str(r.unrecorded_debits),
        "adjusted_book_balance": str(r.adjusted_book_balance),
        "adjusted_bank_balance": str(r.adjusted_bank_balance),
        "is_balanced": r.is_balanced,
        "reconciled_at": r.reconciled_at.isoformat() if r.reconciled_at else None,
        "reconciled_by": r.reconciled_by,
        "discrepancies": [_json_discrepancy(d) for d in r.discrepancies],
    }


def _json_discrepancy(d) -> dict:
    return {
        "id": d.id,
        "discrepancy_type": d.discrepancy_type.value,
        "amount": str(d.amount),
        "entry_side": d.entry_side,
        "reference": d.reference,
        "description": d.description,
        "status": d.status,
        "resolution_entry_id": d.resolution_entry_id,
    }


def _json_petty_cash(f) -> dict:
    return {
        "id": f.id,
        "fund_code": f.fund_code,
        "custodian": f.custodian,
        "limit_amount": str(f.limit_amount),
        "current_balance": str(f.current_balance),
        "currency": f.currency,
        "established_date": f.established_date.isoformat(),
        "status": f.status.value,
    }


def _json_advance(a) -> dict:
    return {
        "id": a.id,
        "employee_name": a.employee_name,
        "employee_id": a.employee_id,
        "amount": str(a.amount),
        "advance_date": a.advance_date.isoformat(),
        "purpose": a.purpose,
        "settlement_deadline": a.settlement_deadline.isoformat(),
        "settlement_amount": str(a.settlement_amount),
        "remaining_balance": str(a.remaining_balance),
        "status": a.status,
    }


def _json_transfer(t) -> dict:
    return {
        "id": t.id,
        "source_account": t.source_account,
        "destination_account": t.destination_account,
        "amount": str(t.amount),
        "transfer_date": t.transfer_date.isoformat(),
        "fx_rate": str(t.fx_rate) if t.fx_rate else None,
        "reference": t.reference,
        "status": t.status.value,
        "created_by": t.created_by,
    }


def _json_cheque(c) -> dict:
    return {
        "id": c.id,
        "cheque_number": c.cheque_number,
        "cheque_book_id": c.cheque_book_id,
        "payee": c.payee,
        "amount": str(c.amount),
        "issue_date": c.issue_date.isoformat(),
        "status": c.status.value,
        "bank_account_id": c.bank_account_id,
        "cleared_date": c.cleared_date.isoformat() if c.cleared_date else None,
        "cancelled_reason": c.cancelled_reason,
    }


def _json_daily_cash_count(dcc) -> dict:
    return {
        "id": dcc.id,
        "count_date": dcc.count_date.isoformat(),
        "account_code": dcc.account_code,
        "expected_balance": str(dcc.expected_balance),
        "actual_balance": str(dcc.actual_balance),
        "difference": str(dcc.difference),
        "denomination_breakdown": dcc.denomination_breakdown,
        "notes": dcc.notes,
        "counted_by": dcc.counted_by,
        "witnessed_by": dcc.witnessed_by,
    }


from . import receipts, payments, bank, reconciliations, misc  # noqa: E402
