from flask import Blueprint, current_app

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


from . import accounts, misc  # noqa: E402
