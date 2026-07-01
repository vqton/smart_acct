from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.cash import cash_bp, _get_session, _json_payment
from use_cases.cash import CashUseCases
from domain import CashPaymentType


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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_payment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_payment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cash_bp.route("/payments/<int:payment_id>/cancel", methods=["POST"])
def cancel_payment(payment_id):
    session = _get_session()
    try:
        uc = CashUseCases(session)
        result = uc.cancel_payment(payment_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Payment cancelled"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()
