from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.costing_center import (
    ccost_bp, _get_session, _get_ccost_use_cases,
    _json_cost_center, _json_driver, _json_rule, _json_allocation_run,
    _json_cost_object, _json_accumulation,
    _json_budget, _json_variance,
)
from domain import VASValidationError


def _validate_json_fields(data, required: list) -> str | None:
    for field in required:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            return f"Missing required field: {field}"
    return None


# ── Cost Centers ───────────────────────────────────────────────────

@ccost_bp.route("/cost-centers", methods=["POST"])
def create_cost_center():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.create_cost_center(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cost_center(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/cost-centers", methods=["GET"])
def list_cost_centers():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        parent_id = request.args.get("parent_id", type=int)
        active_only = request.args.get("active_only", "true").lower() == "true"
        result = uc.list_cost_centers(parent_id=parent_id, active_only=active_only)
        ccs = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"cost_centers": [_json_cost_center(c) for c in ccs], "total": len(ccs)})
    finally:
        session.close()


@ccost_bp.route("/cost-centers/tree", methods=["GET"])
def get_cost_center_tree():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        root_id = request.args.get("root_id", type=int)
        result = uc.get_cost_center_tree(root_id=root_id)
        return jsonify({"tree": result.get_data() if hasattr(result, 'get_data') else result})
    finally:
        session.close()


@ccost_bp.route("/cost-centers/<int:cost_center_id>", methods=["GET"])
def get_cost_center(cost_center_id):
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.get_cost_center(cost_center_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_cost_center(result.get_data()))
    finally:
        session.close()


@ccost_bp.route("/cost-centers/<int:cost_center_id>", methods=["PUT"])
def update_cost_center(cost_center_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.update_cost_center(cost_center_id, data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cost_center(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/cost-centers/<int:cost_center_id>/deactivate", methods=["POST"])
def deactivate_cost_center(cost_center_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.deactivate_cost_center(cost_center_id, actor=data.get("actor", "api"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/cost-centers/<int:cost_center_id>/move", methods=["POST"])
def move_cost_center(cost_center_id):
    data = request.get_json() or {}
    err = _validate_json_fields(data, ["new_parent_id"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.move_cost_center(cost_center_id, int(data["new_parent_id"]), actor=data.get("actor", "api"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cost_center(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/cost-centers/import", methods=["POST"])
def bulk_import_cost_centers():
    data = request.get_json() or {}
    rows = data.get("rows", [])
    if not rows:
        return jsonify({"error": "rows required"}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.bulk_import_cost_centers(rows, actor=data.get("actor", "api"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"result": result.get_data().model_dump() if hasattr(result.get_data(), 'model_dump') else result.get_data()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/cost-centers/export", methods=["GET"])
def export_cost_centers():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        active_only = request.args.get("active_only", "true").lower() == "true"
        result = uc.export_cost_centers(active_only=active_only)
        return jsonify({"rows": result.get_data() if hasattr(result, 'get_data') else result})
    finally:
        session.close()


# ── Drivers ────────────────────────────────────────────────────────

@ccost_bp.route("/drivers", methods=["POST"])
def create_driver():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name", "driver_type"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.create_driver(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_driver(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/drivers", methods=["GET"])
def list_drivers():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        active_only = request.args.get("active_only", "true").lower() == "true"
        result = uc.list_drivers(active_only=active_only)
        drivers = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"drivers": [_json_driver(d) for d in drivers], "total": len(drivers)})
    finally:
        session.close()


@ccost_bp.route("/drivers/<int:driver_id>", methods=["GET"])
def get_driver(driver_id):
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.get_driver(driver_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_driver(result.get_data()))
    finally:
        session.close()


@ccost_bp.route("/drivers/<int:driver_id>", methods=["PUT"])
def update_driver(driver_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.update_driver(driver_id, data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_driver(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/drivers/<int:driver_id>", methods=["DELETE"])
def delete_driver(driver_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.delete_driver(driver_id, actor=data.get("actor", "api"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Allocation Rules ───────────────────────────────────────────────

@ccost_bp.route("/rules", methods=["POST"])
def create_rule():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["rule_code", "rule_name", "source_cost_center_id",
                                         "driver_id", "allocation_method", "created_by"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.create_rule(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_rule(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/rules", methods=["GET"])
def list_rules():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        source_cc_id = request.args.get("source_cost_center_id", type=int)
        status = request.args.get("status")
        period_key = request.args.get("period_key")
        result = uc.list_rules(source_cc_id=source_cc_id, status=status, period_key=period_key)
        rules = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"rules": [_json_rule(r) for r in rules], "total": len(rules)})
    finally:
        session.close()


@ccost_bp.route("/rules/<int:rule_id>", methods=["GET"])
def get_rule(rule_id):
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.get_rule(rule_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_rule(result.get_data()))
    finally:
        session.close()


@ccost_bp.route("/rules/<int:rule_id>", methods=["PUT"])
def update_rule(rule_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.update_rule(rule_id, data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_rule(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/rules/<int:rule_id>/approve", methods=["POST"])
def approve_rule(rule_id):
    data = request.get_json() or {}
    err = _validate_json_fields(data, ["approved_by"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.approve_rule(rule_id, data["approved_by"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_rule(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/rules/<int:rule_id>/archive", methods=["POST"])
def archive_rule(rule_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.archive_rule(rule_id, actor=data.get("actor", "api"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/rules/<int:rule_id>/preview", methods=["POST"])
def preview_rule(rule_id):
    data = request.get_json() or {}
    err = _validate_json_fields(data, ["period_key"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.get_allocation_preview(rule_id, data["period_key"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        preview = result.get_data()
        return jsonify({
            "rule_id": preview.rule_id, "rule_code": preview.rule_code,
            "source_cost_center_id": preview.source_cost_center_id,
            "source_amount": str(preview.source_amount),
            "total_allocated": str(preview.total_allocated),
            "lines": [{"source_cost_center_id": l.source_cost_center_id,
                        "target_cost_center_id": l.target_cost_center_id,
                        "allocated_amount": str(l.allocated_amount),
                        "gl_account_code": l.gl_account_code,
                        "driver_quantity": str(l.driver_quantity) if l.driver_quantity else None,
                        "driver_rate": str(l.driver_rate) if l.driver_rate else None} for l in preview.lines],
        })
    finally:
        session.close()


# ── Allocation Runs ────────────────────────────────────────────────

@ccost_bp.route("/allocations/execute", methods=["POST"])
def execute_allocation():
    data = request.get_json() or {}
    err = _validate_json_fields(data, ["period_key", "run_by"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        dry_run = data.get("dry_run", False)
        result = uc.execute_allocation(data["period_key"], data["run_by"], dry_run=dry_run)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        run = result.get_data()
        return jsonify(_json_allocation_run(run) if not dry_run else run), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/allocations/runs", methods=["GET"])
def list_allocation_runs():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        period_key = request.args.get("period_key")
        result = uc.list_allocation_runs(period_key=period_key)
        runs = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"runs": [_json_allocation_run(r) for r in runs], "total": len(runs)})
    finally:
        session.close()


@ccost_bp.route("/allocations/runs/<int:run_id>", methods=["GET"])
def get_allocation_run(run_id):
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.get_allocation_run(run_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_allocation_run(result.get_data()))
    finally:
        session.close()


@ccost_bp.route("/allocations/runs/<int:run_id>/post", methods=["POST"])
def post_allocation_run(run_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.post_allocation_run(run_id, posted_by=data.get("posted_by", "api"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_allocation_run(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/allocations/runs/<int:run_id>/reverse", methods=["POST"])
def reverse_allocation_run(run_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.reverse_allocation_run(run_id, reversed_by=data.get("reversed_by", "api"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_allocation_run(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/allocations/matrix", methods=["GET"])
def get_allocation_matrix():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        period_key = request.args.get("period_key", "")
        if not period_key:
            return jsonify({"error": "period_key required"}), 400
        result = uc.get_allocation_matrix(period_key)
        return jsonify({"matrix": result.get_data() if hasattr(result, 'get_data') else result})
    finally:
        session.close()


# ── Cost Objects ───────────────────────────────────────────────────

@ccost_bp.route("/cost-objects", methods=["POST"])
def create_cost_object():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name", "object_type"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.create_cost_object(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cost_object(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/cost-objects", methods=["GET"])
def list_cost_objects():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        object_type = request.args.get("object_type")
        result = uc.list_cost_objects(object_type=object_type)
        objs = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"cost_objects": [_json_cost_object(o) for o in objs], "total": len(objs)})
    finally:
        session.close()


@ccost_bp.route("/cost-objects/<int:cost_object_id>", methods=["GET"])
def get_cost_object(cost_object_id):
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.get_cost_object(cost_object_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_cost_object(result.get_data()))
    finally:
        session.close()


@ccost_bp.route("/cost-objects/<int:cost_object_id>", methods=["PUT"])
def update_cost_object(cost_object_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.update_cost_object(cost_object_id, data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_cost_object(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/cost-objects/<int:cost_object_id>", methods=["DELETE"])
def delete_cost_object(cost_object_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.delete_cost_object(cost_object_id, actor=data.get("actor", "api"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/cost-objects/export", methods=["GET"])
def export_cost_objects():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        object_type = request.args.get("object_type")
        result = uc.export_cost_objects(object_type=object_type)
        return jsonify({"rows": result.get_data() if hasattr(result, 'get_data') else result})
    finally:
        session.close()


# ── Accumulation ───────────────────────────────────────────────────

@ccost_bp.route("/accumulate", methods=["POST"])
def accumulate_costs():
    data = request.get_json() or {}
    err = _validate_json_fields(data, ["period_key"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.accumulate_costs(data["period_key"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        acc = result.get_data()
        return jsonify({"period_key": acc.period_key, "total_lines": acc.total_lines,
                         "total_direct": str(acc.total_direct),
                         "total_allocated": str(acc.total_allocated)}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/accumulated-costs", methods=["GET"])
def get_accumulated_costs():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        cost_object_id = request.args.get("cost_object_id", type=int)
        period_key = request.args.get("period_key", "")
        if not cost_object_id or not period_key:
            return jsonify({"error": "cost_object_id and period_key required"}), 400
        result = uc.get_accumulated_costs(cost_object_id, period_key)
        rows = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"accumulations": [_json_accumulation(a) for a in rows], "total": len(rows)})
    finally:
        session.close()


# ── Budget & Variance ──────────────────────────────────────────────

@ccost_bp.route("/budget/sync", methods=["POST"])
def sync_budget():
    data = request.get_json() or {}
    err = _validate_json_fields(data, ["period_key"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.sync_budget(data["period_key"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@ccost_bp.route("/budget", methods=["GET"])
def get_budget():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        cost_center_id = request.args.get("cost_center_id", type=int)
        period_key = request.args.get("period_key", "")
        if not cost_center_id or not period_key:
            return jsonify({"error": "cost_center_id and period_key required"}), 400
        result = uc.get_budget(cost_center_id, period_key)
        budgets = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"budgets": [_json_budget(b) for b in budgets], "total": len(budgets)})
    finally:
        session.close()


@ccost_bp.route("/variance", methods=["GET"])
def compute_variance():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        cost_center_id = request.args.get("cost_center_id", type=int)
        period_key = request.args.get("period_key", "")
        if not cost_center_id or not period_key:
            return jsonify({"error": "cost_center_id and period_key required"}), 400
        result = uc.compute_variance(cost_center_id, period_key)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        variances = result.get_data()
        return jsonify({"variances": [_json_variance(v) for v in variances], "total": len(variances)})
    finally:
        session.close()


@ccost_bp.route("/pl", methods=["GET"])
def get_cc_pl():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        cost_center_id = request.args.get("cost_center_id", type=int)
        period_key = request.args.get("period_key", "")
        include_children = request.args.get("include_children", "false").lower() == "true"
        if not cost_center_id or not period_key:
            return jsonify({"error": "cost_center_id and period_key required"}), 400
        result = uc.report_cc_pl(cost_center_id, period_key, include_children=include_children)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    finally:
        session.close()


# ── Allocation Report ──────────────────────────────────────────────

@ccost_bp.route("/reports/allocation-summary", methods=["GET"])
def allocation_summary():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        period_key = request.args.get("period_key", "")
        if not period_key:
            return jsonify({"error": "period_key required"}), 400
        result = uc.report_allocation_summary(period_key)
        return jsonify(result.get_data() if hasattr(result, 'get_data') else result)
    finally:
        session.close()


# ── Audit ──────────────────────────────────────────────────────────

@ccost_bp.route("/audit-logs", methods=["GET"])
def get_audit_logs():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        entity_type = request.args.get("entity_type")
        entity_id = request.args.get("entity_id", type=int)
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        result = uc.get_audit_logs(entity_type=entity_type, entity_id=entity_id,
                                     limit=limit, offset=offset)
        logs = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"audit_logs": logs, "total": len(logs)})
    finally:
        session.close()


# ── Dashboard ──────────────────────────────────────────────────────

@ccost_bp.route("/dashboard", methods=["GET"])
def dashboard_summary():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.dashboard_summary()
        return jsonify(result.get_data() if hasattr(result, 'get_data') else result)
    finally:
        session.close()


# ── Self-Service ───────────────────────────────────────────────────

@ccost_bp.route("/manager/cost-centers", methods=["GET"])
def get_manager_cost_centers():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        employee_id = request.args.get("employee_id", type=int)
        if not employee_id:
            return jsonify({"error": "employee_id required"}), 400
        result = uc.get_manager_cost_centers(employee_id)
        ccs = result.get_data() if hasattr(result, 'get_data') else result
        return jsonify({"cost_centers": [_json_cost_center(c) for c in ccs], "total": len(ccs)})
    finally:
        session.close()


@ccost_bp.route("/manager/dashboard", methods=["GET"])
def get_manager_dashboard():
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        employee_id = request.args.get("employee_id", type=int)
        period_key = request.args.get("period_key", "")
        if not employee_id or not period_key:
            return jsonify({"error": "employee_id and period_key required"}), 400
        result = uc.get_manager_dashboard(employee_id, period_key)
        return jsonify(result.get_data() if hasattr(result, 'get_data') else result)
    finally:
        session.close()


# ── Health / Validation ────────────────────────────────────────────

@ccost_bp.route("/validate-cost-center", methods=["POST"])
def validate_cost_center_for_je():
    data = request.get_json() or {}
    err = _validate_json_fields(data, ["cost_center_id", "gl_account_code"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_ccost_use_cases()
        result = uc.validate_cost_center_for_je(int(data["cost_center_id"]), data["gl_account_code"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"valid": True})
    finally:
        session.close()
