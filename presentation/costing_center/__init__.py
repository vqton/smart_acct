from typing import Optional
from decimal import Decimal
from flask import Blueprint, current_app

ccost_bp = Blueprint("ccost", __name__, url_prefix="/api/v1/costing")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


_ccost_use_cases: Optional[object] = None


def _get_ccost_use_cases():
    global _ccost_use_cases
    if _ccost_use_cases is None:
        from use_cases.costing_center import CostingCenterUseCases
        _ccost_use_cases = CostingCenterUseCases(_get_session())
    return _ccost_use_cases


def _json_cost_center(c) -> dict:
    return {
        "id": c.id, "code": c.code, "name": c.name, "name_en": c.name_en,
        "cost_center_type": c.cost_center_type.value if hasattr(c.cost_center_type, 'value') else c.cost_center_type,
        "parent_id": c.parent_id, "level": c.level, "path": c.path,
        "manager_employee_id": c.manager_employee_id,
        "gl_account_code": c.gl_account_code, "department_code": c.department_code,
        "is_cost_collector": c.is_cost_collector, "is_active": c.is_active,
        "valid_from": c.valid_from.isoformat() if c.valid_from else None,
        "valid_to": c.valid_to.isoformat() if c.valid_to else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _json_driver(d) -> dict:
    return {
        "id": d.id, "code": d.code, "name": d.name,
        "driver_type": d.driver_type.value if hasattr(d.driver_type, 'value') else d.driver_type,
        "source_module": d.source_module, "source_account_code": d.source_account_code,
        "unit_of_measure": d.unit_of_measure, "formula": d.formula,
        "is_active": d.is_active, "created_at": d.created_at.isoformat() if d.created_at else None,
    }


def _json_rule_target(t) -> dict:
    return {
        "id": t.id, "rule_id": t.rule_id,
        "target_cost_center_id": t.target_cost_center_id,
        "percentage": str(t.percentage) if t.percentage else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def _json_rule(r) -> dict:
    return {
        "id": r.id, "rule_code": r.rule_code, "rule_name": r.rule_name,
        "source_cost_center_id": r.source_cost_center_id,
        "driver_id": r.driver_id,
        "allocation_method": r.allocation_method.value if hasattr(r.allocation_method, 'value') else r.allocation_method,
        "targets": [_json_rule_target(t) for t in r.targets],
        "gl_debit_account_code": r.gl_debit_account_code,
        "gl_credit_account_code": r.gl_credit_account_code,
        "priority_order": r.priority_order,
        "effective_from": r.effective_from.isoformat() if r.effective_from else None,
        "effective_to": r.effective_to.isoformat() if r.effective_to else None,
        "approval_status": r.approval_status.value if hasattr(r.approval_status, 'value') else r.approval_status,
        "approved_by": r.approved_by, "approved_at": r.approved_at.isoformat() if r.approved_at else None,
        "notes": r.notes, "created_by": r.created_by,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }


def _json_allocation_line(l) -> dict:
    return {
        "id": l.id, "run_id": l.run_id,
        "source_cost_center_id": l.source_cost_center_id,
        "target_cost_center_id": l.target_cost_center_id,
        "rule_id": l.rule_id, "driver_id": l.driver_id,
        "gl_account_code": l.gl_account_code,
        "original_amount": str(l.original_amount),
        "allocated_amount": str(l.allocated_amount),
        "driver_quantity": str(l.driver_quantity) if l.driver_quantity else None,
        "driver_rate": str(l.driver_rate) if l.driver_rate else None,
        "allocation_basis_description": l.allocation_basis_description,
    }


def _json_allocation_run(r) -> dict:
    return {
        "id": r.id, "run_code": r.run_code,
        "period_key": r.period_key, "fiscal_year": r.fiscal_year,
        "period_month": r.period_month,
        "run_date": r.run_date.isoformat() if r.run_date else None,
        "run_by": r.run_by,
        "status": r.status.value if hasattr(r.status, 'value') else r.status,
        "total_allocated_amount": str(r.total_allocated_amount),
        "lines": [_json_allocation_line(l) for l in r.lines],
        "notes": r.notes,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def _json_cost_object(o) -> dict:
    return {
        "id": o.id, "code": o.code, "name": o.name,
        "object_type": o.object_type.value if hasattr(o.object_type, 'value') else o.object_type,
        "parent_object_id": o.parent_object_id,
        "gl_account_code": o.gl_account_code,
        "external_ref_id": o.external_ref_id,
        "external_ref_type": o.external_ref_type,
        "is_active": o.is_active,
        "custom_attributes": o.custom_attributes,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _json_accumulation(a) -> dict:
    return {
        "id": a.id, "cost_object_id": a.cost_object_id,
        "cost_center_id": a.cost_center_id,
        "gl_account_code": a.gl_account_code, "period_key": a.period_key,
        "direct_cost_amount": str(a.direct_cost_amount),
        "allocated_cost_amount": str(a.allocated_cost_amount),
        "total_cost_amount": str(a.total_cost_amount),
        "source_type": a.source_type, "source_reference": a.source_reference,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _json_budget(b) -> dict:
    return {
        "id": b.id, "cost_center_id": b.cost_center_id,
        "fiscal_year": b.fiscal_year, "period_key": b.period_key,
        "gl_account_code": b.gl_account_code,
        "budget_amount": str(b.budget_amount),
        "revised_amount": str(b.revised_amount),
        "notes": b.notes,
    }


def _json_variance(v) -> dict:
    return {
        "cost_center_id": v.cost_center_id,
        "period_key": v.period_key,
        "gl_account_code": v.gl_account_code,
        "budget_amount": str(v.budget_amount),
        "actual_amount": str(v.actual_amount),
        "variance_amount": str(v.variance_amount),
        "variance_pct": str(v.variance_pct) if v.variance_pct else None,
        "variance_type": v.variance_type.value if v.variance_type and hasattr(v.variance_type, 'value') else (v.variance_type if v.variance_type else None),
        "annotation": v.annotation,
    }


from . import routes  # noqa: E402
