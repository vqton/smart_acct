from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.cash import cash_bp, _get_session, _json_receipt
from use_cases.cash import CashUseCases
from domain import CashReceiptType


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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_receipt(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_receipt(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/receipts/<int:receipt_id>/cancel", methods=["POST"])
def cancel_receipt(receipt_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.cancel_receipt(receipt_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Receipt cancelled"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()
