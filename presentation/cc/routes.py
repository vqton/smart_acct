from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.cc import (
    cc_bp, _get_session, _get_cc_use_cases,
    _json_category, _json_item, _json_allocation, _json_allocation_line,
    _json_transaction, _json_transfer, _json_inventory, _json_inventory_line,
    _json_write_off, _json_spare_part,
)


def _validate_json_fields(data, required: list) -> str | None:
    for field in required:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            return f"Missing required field: {field}"
    return None


def _validate_date_format(date_str: str, field_name: str) -> str | None:
    try:
        if date_str:
            date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return f"Invalid date format for {field_name}: expected YYYY-MM-DD"
    return None


# ── Categories ────────────────────────────────────────────────────

@cc_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.create_category(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_category(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/categories", methods=["GET"])
def list_categories():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.list_categories()
        categories = result.get_data() if result.is_success() else []
        return jsonify({"categories": [_json_category(c) for c in categories], "total": len(categories)})
    finally:
        session.close()


@cc_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_category(category_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_category(result.get_data()))
    finally:
        session.close()


@cc_bp.route("/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.update_category(category_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_category(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.delete_category(category_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Category deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Items ─────────────────────────────────────────────────────────

@cc_bp.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name", "category_id"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.create_item(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_item(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/items", methods=["GET"])
def list_items():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        category_id = request.args.get("category_id", type=int)
        status = request.args.get("status")
        department_id = request.args.get("department_id", type=int)
        cc_type = request.args.get("cc_type")
        result = uc.list_items(category_id=category_id, status=status,
                                department_id=department_id, cc_type=cc_type)
        items = result.get_data() if result.is_success() else []
        return jsonify({"items": [_json_item(i) for i in items], "total": len(items)})
    finally:
        session.close()


@cc_bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_item(item_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_item(result.get_data()))
    finally:
        session.close()


@cc_bp.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.update_item(item_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_item(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.delete_item(item_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Item deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Allocations ───────────────────────────────────────────────────

@cc_bp.route("/allocations", methods=["POST"])
def create_allocation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["item_id", "allocation_method", "total_amount", "start_period"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.create_allocation(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        payload = result.get_data()
        payload["allocation"] = _json_allocation(payload["allocation"])
        payload["lines"] = [_json_allocation_line(l) for l in payload["lines"]]
        return jsonify(payload), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/allocations/<int:alloc_id>", methods=["GET"])
def get_allocation(alloc_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_allocation(alloc_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        payload = result.get_data()
        payload["allocation"] = _json_allocation(payload["allocation"])
        payload["lines"] = [_json_allocation_line(l) for l in payload["lines"]]
        return jsonify(payload)
    finally:
        session.close()


@cc_bp.route("/allocations", methods=["GET"])
def list_allocations():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        item_id = request.args.get("item_id", type=int)
        result = uc.list_allocations(item_id=item_id)
        allocs = result.get_data() if result.is_success() else []
        return jsonify({"allocations": [_json_allocation(a) for a in allocs], "total": len(allocs)})
    finally:
        session.close()


@cc_bp.route("/allocation-lines/<int:line_id>/post", methods=["POST"])
def post_allocation_line(line_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.post_allocation_line(line_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/allocation-lines", methods=["GET"])
def list_allocation_lines():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        allocation_id = request.args.get("allocation_id", type=int)
        item_id = request.args.get("item_id", type=int)
        period = request.args.get("period")
        lines = uc.repo.list_allocation_lines(allocation_id=allocation_id, item_id=item_id, period=period)
        return jsonify({"lines": [_json_allocation_line(l) for l in lines], "total": len(lines)})
    finally:
        session.close()


# ── Transactions ──────────────────────────────────────────────────

@cc_bp.route("/transactions", methods=["POST"])
def create_transaction():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["item_id", "transaction_type", "transaction_date", "period"])
    if err:
        return jsonify({"error": err}), 400
    if "transaction_date" in data:
        err = _validate_date_format(data["transaction_date"], "transaction_date")
        if err:
            return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.create_transaction(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_transaction(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/transactions/<int:txn_id>", methods=["GET"])
def get_transaction(txn_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_transaction(txn_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_transaction(result.get_data()))
    finally:
        session.close()


@cc_bp.route("/transactions", methods=["GET"])
def list_transactions():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        item_id = request.args.get("item_id", type=int)
        period = request.args.get("period")
        transaction_type = request.args.get("transaction_type")
        result = uc.list_transactions(item_id=item_id, period=period, transaction_type=transaction_type)
        txns = result.get_data() if result.is_success() else []
        return jsonify({"transactions": [_json_transaction(t) for t in txns], "total": len(txns)})
    finally:
        session.close()


# ── Transfers ─────────────────────────────────────────────────────

@cc_bp.route("/transfers", methods=["POST"])
def create_transfer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["item_id", "transfer_date"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.create_transfer(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_transfer(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/transfers/<int:transfer_id>", methods=["GET"])
def get_transfer(transfer_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_transfer(transfer_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_transfer(result.get_data()))
    finally:
        session.close()


@cc_bp.route("/transfers", methods=["GET"])
def list_transfers():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        item_id = request.args.get("item_id", type=int)
        result = uc.list_transfers(item_id=item_id)
        transfers = result.get_data() if result.is_success() else []
        return jsonify({"transfers": [_json_transfer(t) for t in transfers], "total": len(transfers)})
    finally:
        session.close()


# ── Inventories ───────────────────────────────────────────────────

@cc_bp.route("/inventories", methods=["POST"])
def create_inventory():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["inventory_date", "lines"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        lines = data.pop("lines", [])
        result = uc.create_inventory(data, lines)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_inventory(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/inventories/<int:inv_id>", methods=["GET"])
def get_inventory(inv_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_inventory(inv_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_inventory(result.get_data()))
    finally:
        session.close()


@cc_bp.route("/inventories", methods=["GET"])
def list_inventories():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        status = request.args.get("status")
        result = uc.list_inventories(status=status)
        invs = result.get_data() if result.is_success() else []
        return jsonify({"inventories": [_json_inventory(i) for i in invs], "total": len(invs)})
    finally:
        session.close()


@cc_bp.route("/inventories/<int:inv_id>/resolve", methods=["POST"])
def resolve_inventory(inv_id):
    data = request.get_json() or {}
    resolution = data.get("resolution", "")
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.resolve_inventory(inv_id, resolution)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_inventory(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Write-Offs ────────────────────────────────────────────────────

@cc_bp.route("/write-offs", methods=["POST"])
def create_write_off():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["item_id", "write_off_date", "reason"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.create_write_off(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_write_off(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/write-offs/<int:wo_id>", methods=["GET"])
def get_write_off(wo_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_write_off(wo_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_write_off(result.get_data()))
    finally:
        session.close()


@cc_bp.route("/write-offs", methods=["GET"])
def list_write_offs():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        item_id = request.args.get("item_id", type=int)
        result = uc.list_write_offs(item_id=item_id)
        wos = result.get_data() if result.is_success() else []
        return jsonify({"write_offs": [_json_write_off(wo) for wo in wos], "total": len(wos)})
    finally:
        session.close()


# ── Spare Parts ───────────────────────────────────────────────────

@cc_bp.route("/spare-parts", methods=["POST"])
def create_spare_part():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["item_id", "code", "name"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.create_spare_part(data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_spare_part(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/spare-parts/<int:sp_id>", methods=["GET"])
def get_spare_part(sp_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_spare_part(sp_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_spare_part(result.get_data()))
    finally:
        session.close()


@cc_bp.route("/spare-parts/<int:sp_id>", methods=["PUT"])
def update_spare_part(sp_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.update_spare_part(sp_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_spare_part(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/spare-parts/<int:sp_id>", methods=["DELETE"])
def delete_spare_part(sp_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.delete_spare_part(sp_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Spare part deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/spare-parts", methods=["GET"])
def list_spare_parts():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        item_id = request.args.get("item_id", type=int)
        result = uc.list_spare_parts(item_id=item_id)
        parts = result.get_data() if result.is_success() else []
        return jsonify({"spare_parts": [_json_spare_part(sp) for sp in parts], "total": len(parts)})
    finally:
        session.close()


# ── Reports ───────────────────────────────────────────────────────

@cc_bp.route("/reports/by-department/<int:department_id>", methods=["GET"])
def report_by_department(department_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.report_by_department(department_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        payload = result.get_data()
        payload["items"] = [_json_item(i) for i in payload["items"]]
        return jsonify(payload)
    finally:
        session.close()


@cc_bp.route("/reports/by-employee/<int:employee_id>", methods=["GET"])
def report_by_employee(employee_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.report_by_employee(employee_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        payload = result.get_data()
        payload["items"] = [_json_item(i) for i in payload["items"]]
        return jsonify(payload)
    finally:
        session.close()


@cc_bp.route("/reports/allocation-schedule/<int:item_id>", methods=["GET"])
def report_allocation_schedule(item_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.report_allocation_schedule(item_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        payload = result.get_data()
        payload["lines"] = [_json_allocation_line(l) for l in payload["lines"]]
        return jsonify(payload)
    finally:
        session.close()


@cc_bp.route("/reports/value-summary", methods=["GET"])
def report_value_summary():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.report_value_summary()
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    finally:
        session.close()


@cc_bp.route("/reports/inventory-status/<int:inv_id>", methods=["GET"])
def report_inventory_status(inv_id):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.report_inventory_status(inv_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        payload = result.get_data()
        payload["inventory"] = _json_inventory(payload["inventory"])
        return jsonify(payload)
    finally:
        session.close()


# ── Import/Export ─────────────────────────────────────────────────

@cc_bp.route("/import", methods=["POST"])
def import_items():
    data = request.get_json()
    if not data or "rows" not in data:
        return jsonify({"error": "Request body must contain 'rows' array"}), 400
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        filename = data.get("filename", "import.json")
        created_by = data.get("created_by")
        result = uc.import_items(data["rows"], filename, created_by=created_by)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@cc_bp.route("/export", methods=["GET"])
def export_items():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        status = request.args.get("status")
        result = uc.export_items(status=status)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"items": result.get_data(), "total": len(result.get_data())})
    finally:
        session.close()


@cc_bp.route("/import-logs", methods=["GET"])
def list_import_logs():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.get_import_logs()
        logs = result.get_data() if result.is_success() else []
        return jsonify({"import_logs": logs, "total": len(logs)})
    finally:
        session.close()


# ── GL Posting ────────────────────────────────────────────────────

@cc_bp.route("/post-period/<period>", methods=["POST"])
def post_period_allocations(period):
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.post_period_allocations(period)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Dashboard ─────────────────────────────────────────────────────

@cc_bp.route("/dashboard", methods=["GET"])
def dashboard():
    session = _get_session()
    try:
        uc = _get_cc_use_cases()
        result = uc.dashboard_summary()
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    finally:
        session.close()
