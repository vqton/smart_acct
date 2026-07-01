from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.cash import cash_bp, _get_session, _json_reconciliation
from use_cases.cash import CashUseCases


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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_reconciliation(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/reconciliations/<int:recon_id>", methods=["GET"])
def get_reconciliation(recon_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.get_reconciliation(recon_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_reconciliation(result.get_data()))
    finally:
        session.close()


@cash_bp.route("/reconciliations", methods=["GET"])
def list_reconciliations():
    session = _get_session()
    try:
        uc = CashUseCases(session)
        bank_account_id = request.args.get("bank_account_id", type=int)
        recons = uc.repo.list_reconciliations(bank_account_id=bank_account_id)
        return jsonify({"reconciliations": [_json_reconciliation(r) for r in recons], "total": len(recons)})
    finally:
        session.close()


@cash_bp.route("/reconciliations/suggest-matches", methods=["POST"])
def suggest_matches():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.suggest_matches(
            bank_account_id=data["bank_account_id"],
            period=data.get("period"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    finally:
        session.close()


@cash_bp.route("/reconciliations/<int:recon_id>/report", methods=["GET"])
def reconciliation_report(recon_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        fmt = request.args.get("format", "json")
        result = uc.generate_reconciliation_report(recon_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        data = result.get_data()
        if fmt == "html":
            html = uc._render_reconciliation_html(data["data"])
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return jsonify(data)
    finally:
        session.close()
