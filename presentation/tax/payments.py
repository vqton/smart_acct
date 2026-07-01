from flask import request, jsonify
from presentation import resolve_error
from presentation.tax import tax_bp, _get_session, _json_payment, _json_adjustment, _json_incentive
from use_cases.tax import TaxUseCases
from domain import TaxType, TaxPaymentStatus, TaxAdjustmentType, TaxIncentiveType
from datetime import date
from decimal import Decimal


@tax_bp.route("/payments", methods=["POST"])
def create_payment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.create_payment(
            declaration_id=data["declaration_id"],
            amount=Decimal(str(data["amount"])),
            due_date=date.fromisoformat(data["due_date"]),
            payment_date=date.fromisoformat(data["payment_date"]),
            tax_type=TaxType(data["tax_type"]),
            budget_account=data.get("budget_account", "1701"),
            payment_method=data.get("payment_method", "etax"),
            notes=data.get("notes"),
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


@tax_bp.route("/payments", methods=["GET"])
def list_payments():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        decl_id = request.args.get("declaration_id", type=int)
        payments = uc.list_payments(declaration_id=decl_id)
        return jsonify({"payments": [_json_payment(p) for p in payments], "total": len(payments)})
    finally:
        session.close()


@tax_bp.route("/payments/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_payment(payment_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_payment(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/payments/<int:payment_id>", methods=["PUT"])
def update_payment(payment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_payment(payment_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_payment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/payments/<int:payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_payment(payment_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Payment {payment_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/adjustments", methods=["POST"])
def create_adjustment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.create_adjustment(
            declaration_id=data["declaration_id"],
            adjustment_type=TaxAdjustmentType(data["adjustment_type"]),
            reason=data["reason"],
            original_amount=Decimal(str(data["original_amount"])),
            adjusted_amount=Decimal(str(data["adjusted_amount"])),
            supplemental_declaration_id=data.get("supplemental_declaration_id"),
            penalty_interest=Decimal(str(data.get("penalty_interest", 0))),
            penalty=Decimal(str(data.get("penalty", 0))),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_adjustment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/adjustments", methods=["GET"])
def list_adjustments():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        decl_id = request.args.get("declaration_id", type=int)
        adjustments = uc.list_adjustments(declaration_id=decl_id)
        return jsonify({
            "adjustments": [_json_adjustment(a) for a in adjustments],
            "total": len(adjustments),
        })
    finally:
        session.close()


@tax_bp.route("/adjustments/<int:adj_id>", methods=["GET"])
def get_adjustment(adj_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_adjustment(adj_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_adjustment(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/adjustments/<int:adj_id>", methods=["PUT"])
def update_adjustment(adj_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_adjustment(adj_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_adjustment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/adjustments/<int:adj_id>", methods=["DELETE"])
def delete_adjustment(adj_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_adjustment(adj_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Adjustment {adj_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/incentives", methods=["POST"])
def create_incentive():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.create_incentive(
            tax_type=TaxType(data["tax_type"]),
            incentive_type=TaxIncentiveType(data["incentive_type"]),
            code=data["code"],
            name=data["name"],
            legal_basis=data["legal_basis"],
            rate_value=Decimal(str(data.get("rate_value", 0))),
            is_percentage=data.get("is_percentage", True),
            valid_from=date.fromisoformat(data["valid_from"]),
            valid_to=date.fromisoformat(data["valid_to"]) if data.get("valid_to") else None,
            max_duration_months=data.get("max_duration_months"),
            eligibility_condition=data.get("eligibility_condition"),
            requires_approval=data.get("requires_approval", False),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_incentive(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/incentives", methods=["GET"])
def list_incentives():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        tax_type = request.args.get("tax_type")
        incentives = uc.list_incentives(
            tax_type=TaxType(tax_type) if tax_type else None,
        )
        return jsonify({
            "incentives": [_json_incentive(i) for i in incentives],
            "total": len(incentives),
        })
    finally:
        session.close()


@tax_bp.route("/incentives/<int:incentive_id>", methods=["GET"])
def get_incentive(incentive_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_incentive(incentive_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_incentive(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/incentives/<int:incentive_id>", methods=["PUT"])
def update_incentive(incentive_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_incentive(incentive_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_incentive(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/incentives/<int:incentive_id>", methods=["DELETE"])
def delete_incentive(incentive_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_incentive(incentive_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Incentive {incentive_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()
