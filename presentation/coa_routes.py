from flask import Blueprint, request, jsonify, current_app

from use_cases.coa_use_cases import COAUseCases
from use_cases.coa_validate_use_case import COAValidateUseCase
from domain import (
    AccountType, DCRDirection, AccountingRegime, AccountStatus,
)
from infrastructure.database import DatabaseError

coa_bp = Blueprint("coa", __name__)


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_account(acc) -> dict:
    return {
        "code": acc.code,
        "name": acc.name,
        "account_type": acc.account_type.value,
        "regime": acc.regime.value,
        "vas_compliant": acc.vas_compliant,
        "drcr_direction": acc.drcr_direction.value,
        "level": acc.level,
        "status": acc.status.value,
        "currency": acc.currency,
        "unit": acc.unit,
        "parent_code": acc.parent_code,
        "description": acc.description,
        "created_at": acc.created_at.isoformat() if acc.created_at else None,
        "updated_at": acc.updated_at.isoformat() if acc.updated_at else None,
    }


@coa_bp.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = COAUseCases(session)
        result = uc.create_account(
            code=data["code"],
            name=data["name"],
            account_type=AccountType(data["account_type"]),
            drcr_direction=DCRDirection(data.get("drcr_direction", data.get("direction", "debit"))),
            regime=AccountingRegime(data.get("regime", "tt99_2025")),
            parent_code=data.get("parent_code"),
            description=data.get("description"),
            currency=data.get("currency", "VND"),
            unit=data.get("unit", "VND"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_account(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@coa_bp.route("/accounts", methods=["GET"])
def list_accounts():
    session = _get_session()
    try:
        uc = COAUseCases(session)
        regime = request.args.get("regime")
        status = request.args.get("status")
        account_type = request.args.get("account_type")

        regime_enum = AccountingRegime(regime) if regime else None
        status_enum = AccountStatus(status) if status else None
        type_enum = AccountType(account_type) if account_type else None

        accounts = uc.list_accounts(
            regime=regime_enum,
            status=status_enum,
            account_type=type_enum,
        )
        return jsonify({"accounts": [_json_account(a) for a in accounts], "total": len(accounts)})
    finally:
        session.close()


@coa_bp.route("/accounts/<code>", methods=["GET"])
def get_account(code):
    session = _get_session()
    try:
        uc = COAUseCases(session)
        result = uc.get_account(code)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(_json_account(result.get_data()))
    finally:
        session.close()


@coa_bp.route("/accounts/<code>", methods=["PUT"])
def update_account(code):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = COAUseCases(session)
        allowed = {"name", "description", "status", "currency", "unit", "vas_compliant", "parent_code"}
        kwargs = {k: v for k, v in data.items() if k in allowed}
        result = uc.update_account(code, **kwargs)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(_json_account(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@coa_bp.route("/accounts/<code>", methods=["DELETE"])
def delete_account(code):
    session = _get_session()
    try:
        uc = COAUseCases(session)
        result = uc.delete_account(code)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Account '{code}' deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@coa_bp.route("/accounts/search", methods=["GET"])
def search_accounts():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400

    session = _get_session()
    try:
        uc = COAUseCases(session)
        accounts = uc.search_accounts(query)
        return jsonify({"accounts": [_json_account(a) for a in accounts], "total": len(accounts)})
    finally:
        session.close()


@coa_bp.route("/accounts/<code>/hierarchy", methods=["GET"])
def account_hierarchy(code):
    session = _get_session()
    try:
        uc = COAUseCases(session)
        result = uc.get_account_hierarchy(code)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/validate/<code>", methods=["GET"])
def validate_account(code):
    session = _get_session()
    try:
        uc = COAValidateUseCase(session)
        result = uc.validate_account(code)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/validate", methods=["GET"])
def validate_all():
    session = _get_session()
    try:
        uc = COAValidateUseCase(session)
        regime = request.args.get("regime")
        regime_enum = AccountingRegime(regime) if regime else None
        result = uc.validate_all(regime=regime_enum)
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/summary", methods=["GET"])
def summary():
    session = _get_session()
    try:
        uc = COAUseCases(session)
        result = uc.get_summary()
        return jsonify(result.get_data())
    finally:
        session.close()
