from datetime import date, datetime
from decimal import Decimal
from flask import Blueprint, request, jsonify, current_app

from use_cases.cash_use_cases import CashUseCases
from domain import (
    CashReceiptType, CashPaymentType, CashVoucherStatus, BankAccountStatus,
    ChequeStatus, PettyCashFundStatus, ReconciliationDiscrepancyType,
    ValidationError, AccountError,
)

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


# ── UC-CASH-01: Cash Receipts ─────────────────────────────────────────


@cash_bp.route("/receipts", methods=["POST"])
def create_receipt():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_receipt(
            receipt_date=date.fromisoformat(data["receipt_date"]),
            receipt_type=CashReceiptType(data["receipt_type"]),
            payer_name=data["payer_name"],
            amount=Decimal(str(data["amount"])),
            amount_in_words=data["amount_in_words"],
            account_code=data["account_code"],
            counter_account=data["counter_account"],
            description=data["description"],
            created_by=data["created_by"],
            currency=data.get("currency", "VND"),
            fx_rate=Decimal(str(data["fx_rate"])) if data.get("fx_rate") else None,
            reference_number=data.get("reference_number"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_receipt(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/receipts", methods=["GET"])
def list_receipts():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        status = request.args.get("status")
        receipts = uc.list_receipts(status=status)
        return jsonify({"receipts": [_json_receipt(r) for r in receipts], "total": len(receipts)})
    finally:
        session.close()


@cash_bp.route("/receipts/<int:receipt_id>", methods=["GET"])
def get_receipt(receipt_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_receipt(receipt_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_receipt(result.get_data()))
    finally:
        session.close()


@cash_bp.route("/receipts/<int:receipt_id>/approve", methods=["POST"])
def approve_receipt(receipt_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.approve_receipt(receipt_id, data.get("approved_by", "system"))
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_receipt(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/receipts/<int:receipt_id>/cancel", methods=["POST"])
def cancel_receipt(receipt_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.cancel_receipt(receipt_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify({"message": "Receipt cancelled"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── UC-CASH-02: Cash Payments ─────────────────────────────────────────


@cash_bp.route("/payments", methods=["POST"])
def create_payment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_payment(
            payment_date=date.fromisoformat(data["payment_date"]),
            payment_type=CashPaymentType(data["payment_type"]),
            receiver_name=data["receiver_name"],
            amount=Decimal(str(data["amount"])),
            amount_in_words=data["amount_in_words"],
            account_code=data["account_code"],
            counter_account=data["counter_account"],
            description=data["description"],
            created_by=data["created_by"],
            currency=data.get("currency", "VND"),
            fx_rate=Decimal(str(data["fx_rate"])) if data.get("fx_rate") else None,
            reference_number=data.get("reference_number"),
            supporting_doc_ref=data.get("supporting_doc_ref"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_payment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/payments", methods=["GET"])
def list_payments():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        status = request.args.get("status")
        payments = uc.list_payments(status=status)
        return jsonify({"payments": [_json_payment(p) for p in payments], "total": len(payments)})
    finally:
        session.close()


@cash_bp.route("/payments/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_payment(payment_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_payment(result.get_data()))
    finally:
        session.close()


@cash_bp.route("/payments/<int:payment_id>/approve", methods=["POST"])
def approve_payment(payment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.approve_payment(payment_id, data.get("approved_by", "system"))
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_payment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/payments/<int:payment_id>/cancel", methods=["POST"])
def cancel_payment(payment_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.cancel_payment(payment_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify({"message": "Payment cancelled"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── UC-CASH-04: Bank Accounts ─────────────────────────────────────────


@cash_bp.route("/bank-accounts", methods=["POST"])
def create_bank_account():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_bank_account(
            bank_name=data["bank_name"],
            branch=data["branch"],
            account_number=data["account_number"],
            account_holder=data["account_holder"],
            coa_code=data["coa_code"],
            currency=data.get("currency", "VND"),
            swift_code=data.get("swift_code"),
            iban=data.get("iban"),
            opening_balance=Decimal(str(data.get("opening_balance", "0"))),
            signatories=data.get("signatories"),
            authorization_limit=Decimal(str(data.get("authorization_limit", "0"))),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_bank_account(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/bank-accounts", methods=["GET"])
def list_bank_accounts():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        status = request.args.get("status")
        result = uc.list_bank_accounts(status=status)
        return jsonify({"bank_accounts": [_json_bank_account(ba) for ba in result.get_data()]})
    finally:
        session.close()


@cash_bp.route("/bank-accounts/<int:ba_id>", methods=["GET"])
def get_bank_account(ba_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_bank_account(ba_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_bank_account(result.get_data()))
    finally:
        session.close()


# ── UC-CASH-06: Bank Reconciliations ──────────────────────────────────


@cash_bp.route("/reconciliations", methods=["POST"])
def create_reconciliation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_reconciliation(
            bank_account_id=data["bank_account_id"],
            period=data["period"],
            book_balance=Decimal(str(data["book_balance"])),
            bank_balance=Decimal(str(data["bank_balance"])),
            deposits_in_transit=Decimal(str(data.get("deposits_in_transit", "0"))),
            outstanding_checks=Decimal(str(data.get("outstanding_checks", "0"))),
            unrecorded_credits=Decimal(str(data.get("unrecorded_credits", "0"))),
            unrecorded_debits=Decimal(str(data.get("unrecorded_debits", "0"))),
            discrepancies=data.get("discrepancies"),
            reconciled_by=data.get("reconciled_by"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_reconciliation(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/reconciliations/<int:recon_id>", methods=["GET"])
def get_reconciliation(recon_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_reconciliation(recon_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_reconciliation(result.get_data()))
    finally:
        session.close()


# ── UC-CASH-03b: Petty Cash ───────────────────────────────────────────


@cash_bp.route("/petty-cash", methods=["POST"])
def create_petty_cash():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_petty_cash_fund(
            fund_code=data["fund_code"],
            custodian=data["custodian"],
            limit_amount=Decimal(str(data["limit_amount"])),
            currency=data.get("currency", "VND"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_petty_cash(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/petty-cash/<int:fund_id>", methods=["GET"])
def get_petty_cash(fund_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_petty_cash_fund(fund_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_petty_cash(result.get_data()))
    finally:
        session.close()


@cash_bp.route("/petty-cash", methods=["GET"])
def list_petty_cash():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.list_petty_cash_funds()
        return jsonify({"funds": [_json_petty_cash(f) for f in result.get_data()]})
    finally:
        session.close()


# ── UC-CASH-03a: Advances (TK 141) ────────────────────────────────────


@cash_bp.route("/advances", methods=["POST"])
def create_advance():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_advance(
            employee_name=data["employee_name"],
            employee_id=data["employee_id"],
            amount=Decimal(str(data["amount"])),
            purpose=data["purpose"],
            settlement_deadline=date.fromisoformat(data["settlement_deadline"]) if data.get("settlement_deadline") else None,
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_advance(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/advances/<int:advance_id>", methods=["GET"])
def get_advance(advance_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_advance(advance_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_advance(result.get_data()))
    finally:
        session.close()


@cash_bp.route("/advances/<int:advance_id>/settle", methods=["POST"])
def settle_advance(advance_id):
    data = request.get_json() or {}
    if "settlement_amount" not in data:
        return jsonify({"error": "settlement_amount required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.settle_advance(advance_id, Decimal(str(data["settlement_amount"])))
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_advance(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── UC-CASH-07: Cash Transfers ────────────────────────────────────────


@cash_bp.route("/transfers", methods=["POST"])
def create_transfer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_transfer(
            source_account=data["source_account"],
            destination_account=data["destination_account"],
            amount=Decimal(str(data["amount"])),
            reference=data["reference"],
            fx_rate=Decimal(str(data["fx_rate"])) if data.get("fx_rate") else None,
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_transfer(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/transfers/<int:transfer_id>", methods=["GET"])
def get_transfer(transfer_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_transfer(transfer_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_transfer(result.get_data()))
    finally:
        session.close()


# ── UC-CASH-08: Daily Cash Count ──────────────────────────────────────


@cash_bp.route("/daily-count", methods=["POST"])
def create_daily_count():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_daily_cash_count(
            account_code=data["account_code"],
            expected_balance=Decimal(str(data["expected_balance"])),
            actual_balance=Decimal(str(data["actual_balance"])),
            counted_by=data["counted_by"],
            denomination_breakdown=data.get("denomination_breakdown"),
            notes=data.get("notes"),
            witnessed_by=data.get("witnessed_by"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_daily_cash_count(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/daily-count", methods=["GET"])
def list_daily_counts():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        account_code = request.args.get("account_code")
        result = uc.list_daily_cash_counts(account_code=account_code)
        return jsonify({"counts": [_json_daily_cash_count(dcc) for dcc in result.get_data()]})
    finally:
        session.close()


# ── UC-CASH-10: Cheques ───────────────────────────────────────────────


@cash_bp.route("/cheques", methods=["POST"])
def create_cheque():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.create_cheque(
            cheque_number=data["cheque_number"],
            cheque_book_id=data["cheque_book_id"],
            payee=data["payee"],
            amount=Decimal(str(data["amount"])),
            bank_account_id=data["bank_account_id"],
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_cheque(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@cash_bp.route("/cheques/<int:cheque_id>", methods=["GET"])
def get_cheque(cheque_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_cheque(cheque_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_cheque(result.get_data()))
    finally:
        session.close()


# ── Cash Balance ─────────────────────────────────────────────────────


@cash_bp.route("/balance", methods=["GET"])
def get_cash_balance():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        account_code = request.args.get("account_code", "1111")
        result = uc.get_cash_balance(account_code=account_code)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        return jsonify(result.get_data())
    finally:
        session.close()


# ── UC-CASH-11: Cash Book Report (So quy tien mat) ──────────────────


@cash_bp.route("/reports/cash-book", methods=["GET"])
def get_cash_book_report():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        account_code = request.args.get("account_code", "1111")
        fmt = request.args.get("format", "json")
        from_date = date.fromisoformat(request.args["from_date"]) if request.args.get("from_date") else None
        to_date = date.fromisoformat(request.args["to_date"]) if request.args.get("to_date") else None
        result = uc.generate_cash_book_report(
            account_code=account_code,
            from_date=from_date,
            to_date=to_date,
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        data = result.get_data()
        if fmt == "html":
            return data["html"], 200, {"Content-Type": "text/html; charset=utf-8"}
        return jsonify(data)
    finally:
        session.close()


# ── Cash Count Report (Bien ban kiem ke quy) ────────────────────────


@cash_bp.route("/daily-count/<int:count_id>/report", methods=["GET"])
def get_cash_count_report(count_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        fmt = request.args.get("format", "json")
        result = uc.generate_cash_count_report(count_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        data = result.get_data()
        if fmt == "html":
            return data["html"], 200, {"Content-Type": "text/html; charset=utf-8"}
        return jsonify(data)
    finally:
        session.close()
