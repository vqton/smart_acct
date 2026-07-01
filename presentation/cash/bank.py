from datetime import date
from decimal import Decimal
from flask import request, jsonify, render_template

from presentation import resolve_error
from presentation.cash import cash_bp, _get_session, _json_bank_account, _json_statement
from use_cases.cash import CashUseCases
from domain import BankAccountStatus


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
            sub_account_type=data.get("sub_account_type"),
            swift_code=data.get("swift_code"),
            iban=data.get("iban"),
            opening_balance=Decimal(str(data.get("opening_balance", "0"))),
            signatories=data.get("signatories"),
            authorization_limit=Decimal(str(data.get("authorization_limit", "0"))),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_bank_account(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_bank_account(result.get_data()))
    finally:
        session.close()


# ── UC-CASH-05: Bank Statements ──────────────────────────────────────────


@cash_bp.route("/statements", methods=["POST"])
def import_statement():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.import_bank_statement(
            bank_account_id=data["bank_account_id"],
            statement_date=date.fromisoformat(data["statement_date"]),
            opening_balance=Decimal(str(data["opening_balance"])),
            closing_balance=Decimal(str(data["closing_balance"])),
            transactions=data.get("transactions", []),
            source=data.get("source", "csv"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_statement(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/statements", methods=["GET"])
def list_statements():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        bank_account_id = request.args.get("bank_account_id", type=int)
        stmts = uc.repo.list_statements(bank_account_id=bank_account_id)
        return jsonify({"statements": [_json_statement(s) for s in stmts], "total": len(stmts)})
    finally:
        session.close()


@cash_bp.route("/statements/<int:stmt_id>", methods=["GET"])
def get_statement(stmt_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        stmt = uc.repo.get_statement(stmt_id)
        if not stmt:
            return jsonify({"error": "Statement not found"}), 404
        return jsonify(_json_statement(stmt))
    finally:
        session.close()


# ── Bank Account Balance ──────────────────────────────────────────────


@cash_bp.route("/bank-accounts/<int:ba_id>/balance", methods=["GET"])
def get_bank_account_balance(ba_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_bank_balance(ba_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


# ── Bank Book Report (So tien gui NH) ────────────────────────────────


@cash_bp.route("/reports/bank-book", methods=["GET"])
def bank_book_report():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        bank_account_id = request.args.get("bank_account_id", type=int)
        fmt = request.args.get("format", "json")
        from_date = date.fromisoformat(request.args["from_date"]) if request.args.get("from_date") else None
        to_date = date.fromisoformat(request.args["to_date"]) if request.args.get("to_date") else None
        if not bank_account_id or not from_date or not to_date:
            return jsonify({"error": "bank_account_id, from_date, to_date required"}), 400
        result = uc.generate_bank_book_report(
            bank_account_id=bank_account_id,
            from_date=from_date,
            to_date=to_date,
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        data = result.get_data()
        if fmt == "html":
            return render_template("reconciliation_report.html", **data), 200, {"Content-Type": "text/html; charset=utf-8"}
        return jsonify(data)
    finally:
        session.close()
