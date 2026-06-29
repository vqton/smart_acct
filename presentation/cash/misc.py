from datetime import date
from decimal import Decimal
from flask import request, jsonify, render_template

from presentation import resolve_error
from presentation.cash import cash_bp, _get_session, _json_petty_cash, _json_advance, _json_transfer, _json_daily_cash_count, _json_cheque
from use_cases.cash_use_cases import CashUseCases
from domain import CashVoucherStatus


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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_petty_cash(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/petty-cash/<int:fund_id>", methods=["GET"])
def get_petty_cash(fund_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_petty_cash_fund(fund_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_advance(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/advances/<int:advance_id>", methods=["GET"])
def get_advance(advance_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_advance(advance_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_advance(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_transfer(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/transfers/<int:transfer_id>", methods=["GET"])
def get_transfer(transfer_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_transfer(transfer_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_daily_cash_count(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cheque(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/cheques/<int:cheque_id>", methods=["GET"])
def get_cheque(cheque_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_cheque(cheque_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 400
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
            return jsonify({"error": resolve_error(result.error)}), 400
        data = result.get_data()
        if fmt == "html":
            return render_template("cash_book_report.html", **data), 200, {"Content-Type": "text/html; charset=utf-8"}
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
            return jsonify({"error": resolve_error(result.error)}), 404
        data = result.get_data()
        if fmt == "html":
            return render_template("cash_count_report.html", **data["count"]), 200, {"Content-Type": "text/html; charset=utf-8"}
        return jsonify(data)
    finally:
        session.close()


# ── Cheque List + Lifecycle ────────────────────────────────────────────


@cash_bp.route("/cheques", methods=["GET"])
def list_cheques():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        cheques = uc.repo.list_cheques()
        return jsonify({"cheques": [_json_cheque(c) for c in cheques], "total": len(cheques)})
    finally:
        session.close()


@cash_bp.route("/cheques/stale", methods=["GET"])
def stale_cheques():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        days = request.args.get("days", 180, type=int)
        result = uc.get_stale_cheques(days=days)
        return jsonify(result.get_data())
    finally:
        session.close()


@cash_bp.route("/cheques/<int:cheque_id>/issue", methods=["POST"])
def issue_cheque(cheque_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.issue_cheque(
            cheque_id=cheque_id,
            payee=data.get("payee", ""),
            amount=Decimal(str(data["amount"])) if data.get("amount") else None,
            bank_account_id=data.get("bank_account_id"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cheque(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/cheques/<int:cheque_id>/clear", methods=["POST"])
def clear_cheque(cheque_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = CashUseCases(session)
        cleared_date = date.fromisoformat(data["cleared_date"]) if data.get("cleared_date") else date.today()
        result = uc.clear_cheque(cheque_id, cleared_date)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cheque(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/cheques/<int:cheque_id>/cancel", methods=["POST"])
def cancel_cheque(cheque_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = CashUseCases(session)
        reason = data.get("reason", "")
        result = uc.cancel_cheque(cheque_id, reason)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cheque(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/cheques/<int:cheque_id>/stop", methods=["POST"])
def stop_cheque(cheque_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = CashUseCases(session)
        reason = data.get("reason", "")
        result = uc.stop_cheque(cheque_id, reason)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cheque(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/cheques/<int:cheque_id>/bounce", methods=["POST"])
def bounce_cheque(cheque_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = CashUseCases(session)
        reason = data.get("reason", "")
        result = uc.bounce_cheque(cheque_id, reason)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cheque(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()
