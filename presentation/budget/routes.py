from decimal import Decimal
from datetime import date
from flask import request, jsonify

from presentation import resolve_error
from presentation.budget import budget_bp, _get_session, _json_structure, _json_dimension, _json_calendar, _json_template, _json_version, _json_plan, _json_workflow, _json_adjustment
from use_cases.budget import BudgetUseCases
from domain import (
    BudgetType, BudgetDimensionType, BudgetPeriodType,
    BudgetControlLevel, BudgetCategoryType,
)
from domain.budget import AdjustmentType as BudgetAdjustmentType
from domain.i18n import ErrorCodes


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-01: Budget Master & Structure
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/structures", methods=["POST"])
def create_structure():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        bts = None
        if data.get("budget_types"):
            bts = [BudgetType(t) for t in data["budget_types"]]
        dims = None
        if data.get("dimensions"):
            dims = [BudgetDimensionType(d) for d in data["dimensions"]]
        pt = BudgetPeriodType(data.get("period_type", "monthly")) if data.get("period_type") else BudgetPeriodType.MONTHLY
        result = uc.create_budget_structure(
            fiscal_year=int(data["fiscal_year"]),
            name=data["name"],
            budget_types=bts,
            dimensions=dims,
            period_type=pt,
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_structure(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/structures", methods=["GET"])
def list_structures():
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        structures = uc.list_budget_structures()
        return jsonify({"structures": [_json_structure(s) for s in structures], "total": len(structures)})
    finally:
        session.close()


@budget_bp.route("/structures/<int:structure_id>", methods=["GET"])
def get_structure(structure_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        s = uc.get_budget_structure(structure_id)
        if not s:
            return jsonify({"error": "Budget structure not found"}), 404
        return jsonify(_json_structure(s))
    finally:
        session.close()


@budget_bp.route("/structures/by-year/<int:fiscal_year>", methods=["GET"])
def get_structure_by_year(fiscal_year):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        s = uc.get_budget_structure_by_year(fiscal_year)
        if not s:
            return jsonify({"error": "No structure found for fiscal year"}), 404
        return jsonify(_json_structure(s))
    finally:
        session.close()


@budget_bp.route("/structures/<int:structure_id>", methods=["PUT"])
def update_structure(structure_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.update_budget_structure(structure_id, **data)
        if not result:
            return jsonify({"error": "Budget structure not found"}), 404
        session.commit()
        return jsonify(_json_structure(result))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/structures/<int:structure_id>/categories", methods=["POST"])
def create_category(structure_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        bt = BudgetType(data["budget_type"])
        ct = BudgetCategoryType(data.get("category_type", "variable"))
        result = uc.create_budget_category(structure_id, bt, data["name"], ct, data.get("gl_account_codes"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_category(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/structures/<int:structure_id>/categories", methods=["GET"])
def list_categories(structure_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        categories = uc.list_budget_categories(structure_id)
        return jsonify({"categories": [_json_category(c) for c in categories]})
    finally:
        session.close()


@budget_bp.route("/structures/<int:structure_id>/dimensions", methods=["POST"])
def create_dimension(structure_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        dt = BudgetDimensionType(data["dimension_type"])
        result = uc.create_budget_dimension(structure_id, dt, data["code"], data["name"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_dimension(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/structures/<int:structure_id>/dimensions", methods=["GET"])
def list_dimensions(structure_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        dim_type_raw = request.args.get("dimension_type")
        dim_type = BudgetDimensionType(dim_type_raw) if dim_type_raw else None
        dims = uc.list_budget_dimensions(structure_id, dim_type)
        return jsonify({"dimensions": [_json_dimension(d) for d in dims], "total": len(dims)})
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-02: Budget Period & Calendar
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/calendars", methods=["POST"])
def create_calendar():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.create_budget_calendar(
            fiscal_year=int(data["fiscal_year"]),
            name=data["name"],
            phases=data.get("phases"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_calendar(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/calendars/by-year/<int:fiscal_year>", methods=["GET"])
def get_calendar(fiscal_year):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        cal = uc.get_budget_calendar(fiscal_year)
        if not cal:
            return jsonify({"error": "Calendar not found for fiscal year"}), 404
        return jsonify(_json_calendar(cal))
    finally:
        session.close()


@budget_bp.route("/calendars/<int:calendar_id>/periods", methods=["GET"])
def list_periods(calendar_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        periods = uc.list_budget_periods(calendar_id)
        return jsonify({"periods": [{
            "id": p.id, "period_key": p.period_key,
            "period_type": p.period_type.value if hasattr(p.period_type, 'value') else p.period_type,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "is_closed": p.is_closed,
        } for p in periods], "total": len(periods)})
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-03: Budget Template
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/templates", methods=["POST"])
def create_template():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        bt = BudgetType(data["budget_type"])
        result = uc.create_budget_template(
            name=data["name"], budget_type=bt,
            lines=data.get("lines"), description=data.get("description"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_template(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/templates", methods=["GET"])
def list_templates():
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        bt_raw = request.args.get("budget_type")
        bt = BudgetType(bt_raw) if bt_raw else None
        templates = uc.list_budget_templates(bt)
        return jsonify({"templates": [_json_template(t) for t in templates], "total": len(templates)})
    finally:
        session.close()


@budget_bp.route("/templates/<int:template_id>", methods=["GET"])
def get_template(template_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        t = uc.get_budget_template(template_id)
        if not t:
            return jsonify({"error": "Template not found"}), 404
        return jsonify(_json_template(t))
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-04: Budget Plan (Draft)
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/versions", methods=["POST"])
def create_version():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.create_budget_version(
            fiscal_year=int(data["fiscal_year"]),
            label=data["label"],
            version_number=data.get("version_number"),
            parent_version_id=data.get("parent_version_id"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_version(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/versions", methods=["GET"])
def list_versions():
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        fy = int(request.args.get("fiscal_year", 0)) if request.args.get("fiscal_year") else 0
        if not fy:
            return jsonify({"error": "fiscal_year query parameter required"}), 400
        versions = uc.list_budget_versions(fy)
        return jsonify({"versions": [_json_version(v) for v in versions], "total": len(versions)})
    finally:
        session.close()


@budget_bp.route("/versions/active/<int:fiscal_year>", methods=["GET"])
def get_active_version(fiscal_year):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        v = uc.get_active_budget_version(fiscal_year)
        if not v:
            return jsonify({"error": "No active budget version"}), 404
        return jsonify(_json_version(v))
    finally:
        session.close()


@budget_bp.route("/versions/<int:version_id>/lock", methods=["POST"])
def lock_version(version_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.lock_budget_version(version_id)
        if not result:
            return jsonify({"error": "Version not found"}), 404
        session.commit()
        return jsonify(_json_version(result))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/versions/<int:version_id>/unlock", methods=["POST"])
def unlock_version(version_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.unlock_budget_version(version_id, data.get("reason", ""))
        if not result:
            return jsonify({"error": "Version not found"}), 404
        session.commit()
        return jsonify(_json_version(result))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/versions/<int:version_id>/revise", methods=["POST"])
def revise_version(version_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.create_revised_version(version_id, data.get("label", "Revised"), data.get("created_by"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_version(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/plans", methods=["POST"])
def create_plan():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        dt = BudgetDimensionType(data["dimension_type"])
        result = uc.create_budget_plan(
            version_id=int(data["version_id"]),
            structure_id=int(data["structure_id"]),
            dimension_type=dt,
            dimension_code=data["dimension_code"],
            lines=data.get("lines"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_plan(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/plans/<int:plan_id>", methods=["GET"])
def get_plan(plan_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        p = uc.get_budget_plan(plan_id)
        if not p:
            return jsonify({"error": "Plan not found"}), 404
        return jsonify(_json_plan(p))
    finally:
        session.close()


@budget_bp.route("/plans/dimension/<int:version_id>", methods=["GET"])
def get_plan_by_dimension(version_id):
    dim_type_raw = request.args.get("dimension_type")
    dim_code = request.args.get("dimension_code")
    if not dim_type_raw or not dim_code:
        return jsonify({"error": "dimension_type and dimension_code required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        dt = BudgetDimensionType(dim_type_raw)
        p = uc.get_budget_plan_by_dimension(version_id, dt, dim_code)
        if not p:
            return jsonify({"error": "Plan not found"}), 404
        return jsonify(_json_plan(p))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/plans/version/<int:version_id>", methods=["GET"])
def list_plans(version_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        plans = uc.list_budget_plans(version_id)
        return jsonify({"plans": [_json_plan(p) for p in plans], "total": len(plans)})
    finally:
        session.close()


@budget_bp.route("/plans/<int:plan_id>/lines", methods=["PUT"])
def update_plan_lines(plan_id):
    data = request.get_json()
    if not data or "lines" not in data:
        return jsonify({"error": "lines required in request body"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.update_budget_plan(plan_id, data["lines"])
        if not result:
            return jsonify({"error": "Plan not found"}), 404
        session.commit()
        return jsonify(_json_plan(result))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-05: Budget Approval Workflow
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/plans/<int:plan_id>/submit", methods=["POST"])
def submit_for_approval(plan_id):
    data = request.get_json()
    if not data or "steps" not in data:
        return jsonify({"error": "steps required in request body"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.submit_budget_for_approval(plan_id, data["steps"], data.get("submitted_by", "system"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"workflow_id": result.get_data().id, "status": "submitted"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/workflows/<int:workflow_id>/finalize", methods=["POST"])
def finalize_approval(workflow_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.finalize_approval(workflow_id, int(data.get("plan_id", 0)), data.get("actor", "system"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/workflows/<int:workflow_id>/approve", methods=["POST"])
def approve_step(workflow_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.approve_budget(
            step_id=int(data.get("step_id", workflow_id)),
            actor=data.get("actor", "system"),
            comments=data.get("comments"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"status": "approved"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/workflows/<int:workflow_id>/reject", methods=["POST"])
def reject_step(workflow_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.reject_budget(
            step_id=int(data.get("step_id", workflow_id)),
            actor=data.get("actor", "system"),
            comments=data.get("comments", ""),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"status": "rejected"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/plans/<int:plan_id>/workflow", methods=["GET"])
def get_workflow(plan_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        w = uc.get_approval_workflow(plan_id)
        if not w:
            return jsonify({"error": "No workflow for this plan"}), 404
        return jsonify(_json_workflow(w))
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-07: Budget Adjustment
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/adjustments", methods=["POST"])
def create_adjustment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        at = BudgetAdjustmentType(data["adjustment_type"])
        result = uc.request_budget_adjustment(
            version_id=int(data["version_id"]),
            adjustment_type=at,
            reference=data.get("reference", ""),
            reason=data["reason"],
            lines=data.get("lines", []),
            created_by=data.get("created_by", "system"),
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


@budget_bp.route("/adjustments/<int:adjustment_id>/approve", methods=["POST"])
def approve_adjustment(adjustment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.approve_adjustment(adjustment_id, data.get("approved_by", "system"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"status": "approved"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/adjustments/version/<int:version_id>", methods=["GET"])
def list_adjustments(version_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        adjustments = uc.list_adjustments(version_id)
        return jsonify({"adjustments": [_json_adjustment(a) for a in adjustments], "total": len(adjustments)})
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-08: Budget Execution Monitoring
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/execution/<int:version_id>", methods=["GET"])
def get_execution(version_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        dim_type_raw = request.args.get("dimension_type")
        dim_code = request.args.get("dimension_code")
        dim_type = BudgetDimensionType(dim_type_raw) if dim_type_raw else None
        items = uc.get_budget_execution(version_id, dim_type, dim_code)
        return jsonify({"items": [{
            "plan_line_id": i.plan_line_id,
            "budget_amount": str(i.budget_amount),
            "actual_amount": str(i.actual_amount),
            "commitment_amount": str(i.commitment_amount),
            "free_balance": str(i.free_balance),
            "utilization_pct": str(i.utilization_pct),
        } for i in items], "total": len(items)})
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-09: Budget Control
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/control-rules", methods=["POST"])
def create_control_rule():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        cl = BudgetControlLevel(data["control_level"])
        dim_type = BudgetDimensionType(data["dimension_type"]) if data.get("dimension_type") else None
        result = uc.configure_budget_control(
            structure_id=int(data["structure_id"]),
            gl_account_code=data["gl_account_code"],
            control_level=cl,
            dimension_type=dim_type,
            dimension_code=data.get("dimension_code"),
            warning_pct=Decimal(str(data.get("warning_pct", "80"))),
            soft_block_pct=Decimal(str(data.get("soft_block_pct", "90"))),
            hard_block_pct=Decimal(str(data.get("hard_block_pct", "100"))),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data().id), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/control-rules/structure/<int:structure_id>", methods=["GET"])
def list_control_rules(structure_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        rules = uc.list_control_rules(structure_id)
        return jsonify({"rules": [{
            "id": r.id, "structure_id": r.structure_id,
            "gl_account_code": r.gl_account_code,
            "dimension_type": r.dimension_type.value if hasattr(r.dimension_type, 'value') else r.dimension_type,
            "dimension_code": r.dimension_code,
            "control_level": r.control_level.value if hasattr(r.control_level, 'value') else r.control_level,
            "warning_threshold_pct": str(r.warning_threshold_pct),
            "soft_block_threshold_pct": str(r.soft_block_threshold_pct),
            "hard_block_threshold_pct": str(r.hard_block_threshold_pct),
        } for r in rules], "total": len(rules)})
    finally:
        session.close()


@budget_bp.route("/control-rules/<int:rule_id>/override", methods=["POST"])
def generate_override(rule_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.generate_override_code(rule_id, data.get("requested_by", "system"),
                                           data.get("reason", ""),
                                           int(data.get("expires_in_hours", 24)))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"override_code": result.get_data().override_code,
                        "expires_at": result.get_data().expires_at.isoformat()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-10: Budget Consolidation
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/consolidations", methods=["POST"])
def create_consolidation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        result = uc.consolidate_budget(
            fiscal_year=int(data["fiscal_year"]),
            parent_entity_code=data["parent_entity_code"],
            entities=data.get("entities", []),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"id": result.get_data().id, "status": "created"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@budget_bp.route("/consolidations/<int:consolidation_id>", methods=["GET"])
def get_consolidation(consolidation_id):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        c = uc.get_consolidation(consolidation_id)
        if not c:
            return jsonify({"error": "Consolidation not found"}), 404
        return jsonify({
            "id": c.id, "fiscal_year": c.fiscal_year,
            "parent_entity_code": c.parent_entity_code,
            "entities": [{
                "entity_code": e.entity_code, "entity_name": e.entity_name,
                "version_id": e.version_id, "fx_rate": str(e.fx_rate),
            } for e in (c.entities or [])],
        })
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-11: Budget vs Actual Analysis
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/variance/<int:version_id>/<period_key>", methods=["GET"])
def run_variance(version_id, period_key):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        report = uc.run_variance_analysis(version_id, period_key)
        if not report:
            return jsonify({"error": "No data for variance analysis"}), 404
        return jsonify({
            "period_key": report.period_key,
            "lines": [{
                "gl_account_code": l.gl_account_code, "name": l.name,
                "budget_amount": str(l.budget_amount),
                "actual_amount": str(l.actual_amount),
                "variance_amount": str(l.variance_amount),
                "variance_pct": str(l.variance_pct),
                "flag": l.flag.value if hasattr(l.flag, 'value') else l.flag,
            } for l in report.lines],
            "total": len(report.lines),
        })
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# UC-BUDGET-12: Budget Dashboard
# ═══════════════════════════════════════════════════════════════

@budget_bp.route("/dashboard/<int:fiscal_year>", methods=["GET"])
def get_dashboard(fiscal_year):
    session = _get_session()
    try:
        uc = BudgetUseCases(session)
        dash = uc.get_budget_dashboard(fiscal_year)
        if not dash:
            return jsonify({"error": "No dashboard data"}), 404
        return jsonify({
            "fiscal_year": dash.fiscal_year,
            "total_budget_amount": str(dash.total_budget_amount) if dash.total_budget_amount else "0",
            "revenue_achievement": str(dash.revenue_achievement) if dash.revenue_achievement else "0",
            "opex_utilization": str(dash.opex_utilization) if dash.opex_utilization else "0",
            "capex_utilization": str(dash.capex_utilization) if dash.capex_utilization else "0",
            "ytd_variance": str(dash.ytd_variance) if dash.ytd_variance else "0",
        })
    finally:
        session.close()
