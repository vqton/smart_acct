from flask import Blueprint, current_app, request

budget_bp = Blueprint("budget", __name__, url_prefix="/api/v1/budget")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_structure(s):
    return {
        "id": s.id, "fiscal_year": s.fiscal_year, "name": s.name,
        "budget_types": [t.value if hasattr(t, 'value') else t for t in (s.budget_types or [])],
        "dimensions": [d.value if hasattr(d, 'value') else d for d in (s.dimensions or [])],
        "period_type": s.period_type.value if hasattr(s.period_type, 'value') else s.period_type,
        "is_active": s.is_active, "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def _json_dimension(d):
    return {
        "id": d.id, "structure_id": d.structure_id,
        "dimension_type": d.dimension_type.value if hasattr(d.dimension_type, 'value') else d.dimension_type,
        "code": d.code, "name": d.name, "is_active": d.is_active,
    }


def _json_calendar(c):
    return {
        "id": c.id, "fiscal_year": c.fiscal_year, "name": c.name,
        "phases": [_json_cal_phase(p) for p in (c.phases or [])],
    }


def _json_cal_phase(p):
    return {
        "id": p.id, "phase_name": p.phase_name,
        "start_date": p.start_date.isoformat() if p.start_date else None,
        "end_date": p.end_date.isoformat() if p.end_date else None,
        "phase_order": p.phase_order,
    }


def _json_template(t):
    return {
        "id": t.id, "name": t.name, "description": t.description,
        "budget_type": t.budget_type.value if hasattr(t.budget_type, 'value') else t.budget_type,
        "lines": [_json_template_line(l) for l in (t.lines or [])],
    }


def _json_template_line(l):
    return {
        "id": l.id, "line_order": l.line_order, "gl_account_code": l.gl_account_code,
        "name": l.name, "category_type": l.category_type.value if hasattr(l.category_type, 'value') else l.category_type,
        "formula": l.formula, "is_required": l.is_required,
        "default_amount": str(l.default_amount), "notes": l.notes,
    }


def _json_version(v):
    return {
        "id": v.id, "fiscal_year": v.fiscal_year, "version_number": v.version_number,
        "label": v.label, "status": v.status.value if hasattr(v.status, 'value') else v.status,
        "is_locked": v.is_locked, "parent_version_id": v.parent_version_id,
        "created_by": v.created_by,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


def _json_plan(p):
    return {
        "id": p.id, "version_id": p.version_id, "structure_id": p.structure_id,
        "dimension_type": p.dimension_type.value if hasattr(p.dimension_type, 'value') else p.dimension_type,
        "dimension_code": p.dimension_code, "notes": p.notes,
        "created_by": p.created_by,
        "lines": [_json_plan_line(l) for l in (p.lines or [])],
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def _json_plan_line(l):
    return {
        "id": l.id, "gl_account_code": l.gl_account_code, "name": l.name,
        "category_type": l.category_type.value if hasattr(l.category_type, 'value') else l.category_type,
        "amounts": l.amounts, "notes": l.notes,
        "driver": _json_plan_driver(l.driver) if l.driver else None,
    }


def _json_plan_driver(d):
    return {
        "id": d.id, "quantity": str(d.quantity), "unit_rate": str(d.unit_rate),
        "driver_name": d.driver_name,
    }


def _json_workflow(w):
    return {
        "id": w.id, "plan_id": w.plan_id,
        "status": w.status.value if hasattr(w.status, 'value') else w.status,
        "steps": [_json_workflow_step(s) for s in (w.steps or [])],
    }


def _json_workflow_step(s):
    return {
        "id": s.id, "step_order": s.step_order, "approver_role": s.approver_role,
        "approver_name": s.approver_name, "min_approvers": s.min_approvers,
        "status": s.status.value if hasattr(s.status, 'value') else s.status,
        "comments": s.comments,
        "acted_at": s.acted_at.isoformat() if s.acted_at else None,
    }


def _json_adjustment(a):
    return {
        "id": a.id, "version_id": a.version_id,
        "adjustment_type": a.adjustment_type.value if hasattr(a.adjustment_type, 'value') else a.adjustment_type,
        "reference": a.reference, "reason": a.reason,
        "status": a.status.value if hasattr(a.status, 'value') else a.status,
        "lines": [_json_adjustment_line(l) for l in (a.lines or [])],
        "created_by": a.created_by,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _json_adjustment_line(l):
    return {
        "id": l.id, "source_plan_line_id": l.source_plan_line_id,
        "target_plan_line_id": l.target_plan_line_id,
        "amount": str(l.amount), "period_key": l.period_key,
    }


from . import routes  # noqa: E402
