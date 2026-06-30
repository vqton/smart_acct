from flask import Blueprint, current_app, jsonify, request

fs_bp = Blueprint("fs", __name__)


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_line_item(l):
    return {
        "id": l.id,
        "ma_so": l.ma_so,
        "ten_chi_tieu": l.ten_chi_tieu,
        "so_thu_tu": l.so_thu_tu,
        "parent_ma_so": l.parent_ma_so,
        "current_year": str(l.current_year),
        "previous_year": str(l.previous_year) if l.previous_year is not None else None,
        "is_subtotal": l.is_subtotal,
        "is_calculated": l.is_calculated,
        "thuyet_minh": l.thuyet_minh,
    }


def _json_fs(fs):
    return {
        "id": fs.id,
        "entity_id": fs.entity_id,
        "period": fs.period,
        "statement_type": fs.statement_type.value,
        "status": fs.status.value,
        "version": fs.version,
        "cash_flow_method": fs.cash_flow_method.value if fs.cash_flow_method else None,
        "approved_by": fs.approved_by,
        "approval_date": fs.approval_date.isoformat() if fs.approval_date else None,
        "signed_by": fs.signed_by,
        "signed_date": fs.signed_date.isoformat() if fs.signed_date else None,
        "generated_by": fs.generated_by,
        "generated_at": fs.generated_at.isoformat() if fs.generated_at else None,
        "is_consolidated": fs.is_consolidated,
        "consolidation_group_id": fs.consolidation_group_id,
        "notes": fs.notes,
        "lines": [_json_line_item(l) for l in fs.lines],
        "created_at": fs.created_at.isoformat() if fs.created_at else None,
        "updated_at": fs.updated_at.isoformat() if fs.updated_at else None,
    }


def _json_mapping(m):
    return {
        "id": m.id,
        "fs_ma_so": m.fs_ma_so,
        "account_code": m.account_code,
        "weight": str(m.weight),
        "direction": m.direction,
        "statement_type": m.statement_type.value,
    }
