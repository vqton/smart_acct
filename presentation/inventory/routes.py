from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.inventory import (
    inv_bp, _get_session,
    _json_category, _json_warehouse, _json_item, _json_batch, _json_serial,
    _json_receipt, _json_issue, _json_transfer, _json_stock_card,
    _json_check, _json_adjustment,
)
from domain import VASValidationError


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


# ═══════════════════════════════════════════════════════════════════
# Categories
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_category(
            code=data["code"], name=data["name"],
            description=data.get("description"),
            inventory_type=data.get("inventory_type", "merchandise"),
            valuation_method=data.get("valuation_method", "weighted_average"),
            gl_inventory_account=data.get("gl_inventory_account", "152"),
            gl_receipt_account=data.get("gl_receipt_account", "331"),
            gl_issue_account=data.get("gl_issue_account", "621"),
            gl_sales_account=data.get("gl_sales_account", "632"),
            gl_cost_of_sales=data.get("gl_cost_of_sales", "632"),
            gl_return_account=data.get("gl_return_account", "521"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_category(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/categories", methods=["GET"])
def list_categories():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        inventory_type = request.args.get("inventory_type")
        is_active = request.args.get("is_active")
        if is_active is not None:
            is_active = is_active.lower() == "true"
        categories = uc.list_categories(inventory_type=inventory_type, is_active=is_active)
        return jsonify({"categories": [_json_category(c) for c in categories], "total": len(categories)})
    finally:
        session.close()


@inv_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_category(category_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_category(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
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


@inv_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.delete_category(category_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Warehouses
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/warehouses", methods=["POST"])
def create_warehouse():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_warehouse(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_warehouse(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/warehouses", methods=["GET"])
def list_warehouses():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        is_active = request.args.get("is_active")
        if is_active is not None:
            is_active = is_active.lower() == "true"
        warehouses = uc.list_warehouses(is_active=is_active)
        return jsonify({"warehouses": [_json_warehouse(w) for w in warehouses], "total": len(warehouses)})
    finally:
        session.close()


@inv_bp.route("/warehouses/<int:warehouse_id>", methods=["GET"])
def get_warehouse(warehouse_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_warehouse(warehouse_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_warehouse(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/warehouses/<int:warehouse_id>", methods=["PUT"])
def update_warehouse(warehouse_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.update_warehouse(warehouse_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_warehouse(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Items (Master Data)
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name", "category_id"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_item(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_item(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/items", methods=["GET"])
def list_items():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        category_id = request.args.get("category_id", type=int)
        inventory_type = request.args.get("inventory_type")
        status = request.args.get("status")
        search = request.args.get("search")
        low_stock = request.args.get("low_stock", "").lower() == "true"
        items = uc.list_items(category_id=category_id, inventory_type=inventory_type,
                              status=status, search=search, low_stock=low_stock)
        return jsonify({"items": [_json_item(i) for i in items], "total": len(items)})
    finally:
        session.close()


@inv_bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_item(item_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_item(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
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


# ═══════════════════════════════════════════════════════════════════
# Batches
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/batches", methods=["POST"])
def create_batch():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["item_id", "batch_code", "received_date"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_batch(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_batch(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/batches", methods=["GET"])
def list_batches():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        item_id = request.args.get("item_id", type=int)
        warehouse_id = request.args.get("warehouse_id", type=int)
        status = request.args.get("status")
        batches = uc.list_batches(item_id=item_id, warehouse_id=warehouse_id, status=status)
        return jsonify({"batches": [_json_batch(b) for b in batches], "total": len(batches)})
    finally:
        session.close()


@inv_bp.route("/batches/<int:batch_id>", methods=["GET"])
def get_batch(batch_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_batch(batch_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_batch(result.get_data()))
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Serials
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/serials", methods=["POST"])
def create_serial():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["item_id", "serial_code"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_serial(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_serial(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/serials", methods=["GET"])
def list_serials():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        item_id = request.args.get("item_id", type=int)
        warehouse_id = request.args.get("warehouse_id", type=int)
        status = request.args.get("status")
        serials = uc.list_serials(item_id=item_id, warehouse_id=warehouse_id, status=status)
        return jsonify({"serials": [_json_serial(s) for s in serials], "total": len(serials)})
    finally:
        session.close()


@inv_bp.route("/serials/<int:serial_id>", methods=["GET"])
def get_serial(serial_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_serial(serial_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_serial(result.get_data()))
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Receipts
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/receipts", methods=["POST"])
def create_receipt():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["receipt_code", "receipt_date", "warehouse_id", "lines"])
    if err:
        return jsonify({"error": err}), 400
    if not isinstance(data.get("lines"), list) or len(data["lines"]) == 0:
        return jsonify({"error": "At least one line required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_receipt(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_receipt(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/receipts", methods=["GET"])
def list_receipts():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        warehouse_id = request.args.get("warehouse_id", type=int)
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        is_posted = request.args.get("is_posted")
        skip = request.args.get("skip", 0, type=int)
        limit = request.args.get("limit", 50, type=int)
        if date_from:
            date_from = date.fromisoformat(date_from)
        if date_to:
            date_to = date.fromisoformat(date_to)
        if is_posted is not None:
            is_posted = is_posted.lower() == "true"
        receipts, total = uc.list_receipts(
            warehouse_id=warehouse_id, date_from=date_from, date_to=date_to,
            is_posted=is_posted, skip=skip, limit=limit,
        )
        return jsonify({"receipts": [_json_receipt(r) for r in receipts], "total": total})
    finally:
        session.close()


@inv_bp.route("/receipts/<int:receipt_id>", methods=["GET"])
def get_receipt(receipt_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_receipt(receipt_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_receipt(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/receipts/<int:receipt_id>/post", methods=["POST"])
def post_receipt(receipt_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.post_receipt(receipt_id, gl_ref=request.json.get("gl_ref") if request.json else None)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_receipt(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Issues
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/issues", methods=["POST"])
def create_issue():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["issue_code", "issue_date", "warehouse_id", "lines"])
    if err:
        return jsonify({"error": err}), 400
    if not isinstance(data.get("lines"), list) or len(data["lines"]) == 0:
        return jsonify({"error": "At least one line required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_issue(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_issue(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/issues", methods=["GET"])
def list_issues():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        warehouse_id = request.args.get("warehouse_id", type=int)
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        is_posted = request.args.get("is_posted")
        skip = request.args.get("skip", 0, type=int)
        limit = request.args.get("limit", 50, type=int)
        if date_from:
            date_from = date.fromisoformat(date_from)
        if date_to:
            date_to = date.fromisoformat(date_to)
        if is_posted is not None:
            is_posted = is_posted.lower() == "true"
        issues, total = uc.list_issues(
            warehouse_id=warehouse_id, date_from=date_from, date_to=date_to,
            is_posted=is_posted, skip=skip, limit=limit,
        )
        return jsonify({"issues": [_json_issue(r) for r in issues], "total": total})
    finally:
        session.close()


@inv_bp.route("/issues/<int:issue_id>", methods=["GET"])
def get_issue(issue_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_issue(issue_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_issue(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/issues/<int:issue_id>/post", methods=["POST"])
def post_issue(issue_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.post_issue(issue_id, gl_ref=request.json.get("gl_ref") if request.json else None)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_issue(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Transfers
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/transfers", methods=["POST"])
def create_transfer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["transfer_code", "transfer_date", "from_warehouse_id", "to_warehouse_id", "lines"])
    if err:
        return jsonify({"error": err}), 400
    if not isinstance(data.get("lines"), list) or len(data["lines"]) == 0:
        return jsonify({"error": "At least one line required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_transfer(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_transfer(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/transfers", methods=["GET"])
def list_transfers():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        from_wh = request.args.get("from_warehouse_id", type=int)
        to_wh = request.args.get("to_warehouse_id", type=int)
        status = request.args.get("status")
        skip = request.args.get("skip", 0, type=int)
        limit = request.args.get("limit", 50, type=int)
        transfers, total = uc.list_transfers(
            from_warehouse_id=from_wh, to_warehouse_id=to_wh,
            status=status, skip=skip, limit=limit,
        )
        return jsonify({"transfers": [_json_transfer(t) for t in transfers], "total": total})
    finally:
        session.close()


@inv_bp.route("/transfers/<int:transfer_id>", methods=["GET"])
def get_transfer(transfer_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_transfer(transfer_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_transfer(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/transfers/<int:transfer_id>/status", methods=["PUT"])
def update_transfer_status(transfer_id):
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "status field required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.update_transfer_status(transfer_id, data["status"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_transfer(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/transfers/<int:transfer_id>/post", methods=["POST"])
def post_transfer(transfer_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.post_transfer(transfer_id, gl_ref=request.json.get("gl_ref") if request.json else None)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_transfer(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Stock Cards / Balance
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/stock-cards", methods=["GET"])
def list_stock_cards():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        item_id = request.args.get("item_id", type=int)
        warehouse_id = request.args.get("warehouse_id", type=int)
        period_from = request.args.get("period_from")
        period_to = request.args.get("period_to")
        cards = uc.list_stock_cards(
            item_id=item_id, warehouse_id=warehouse_id,
            period_from=period_from, period_to=period_to,
        )
        return jsonify({"stock_cards": [_json_stock_card(c) for c in cards], "total": len(cards)})
    finally:
        session.close()


@inv_bp.route("/stock-cards/<int:item_id>/<int:warehouse_id>/<period>", methods=["GET"])
def get_stock_card(item_id, warehouse_id, period):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_stock_card(item_id, warehouse_id, period)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_stock_card(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/balance/<int:item_id>", methods=["GET"])
def get_inventory_balance(item_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_inventory_balance(item_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Inventory Checks (Stocktake)
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/checks", methods=["POST"])
def create_check():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["check_code", "check_date", "warehouse_id", "lines"])
    if err:
        return jsonify({"error": err}), 400
    if not isinstance(data.get("lines"), list) or len(data["lines"]) == 0:
        return jsonify({"error": "At least one line required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_check(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_check(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/checks", methods=["GET"])
def list_checks():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        warehouse_id = request.args.get("warehouse_id", type=int)
        status = request.args.get("status")
        skip = request.args.get("skip", 0, type=int)
        limit = request.args.get("limit", 50, type=int)
        checks, total = uc.list_checks(warehouse_id=warehouse_id, status=status, skip=skip, limit=limit)
        return jsonify({"checks": [_json_check(c) for c in checks], "total": total})
    finally:
        session.close()


@inv_bp.route("/checks/<int:check_id>", methods=["GET"])
def get_check(check_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_check(check_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_check(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/checks/<int:check_id>/status", methods=["PUT"])
def update_check_status(check_id):
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "status field required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.update_check_status(check_id, data["status"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_check(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/checks/<int:check_id>/approve", methods=["POST"])
def approve_check(check_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.approve_check(check_id, approved_by=data.get("approved_by"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_check(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Adjustments
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/adjustments", methods=["POST"])
def create_adjustment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["adjustment_code", "adjustment_date", "warehouse_id", "reason", "lines"])
    if err:
        return jsonify({"error": err}), 400
    if not isinstance(data.get("lines"), list) or len(data["lines"]) == 0:
        return jsonify({"error": "At least one line required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.create_adjustment(**data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_adjustment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/adjustments", methods=["GET"])
def list_adjustments():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        warehouse_id = request.args.get("warehouse_id", type=int)
        adj_type = request.args.get("adjustment_type")
        skip = request.args.get("skip", 0, type=int)
        limit = request.args.get("limit", 50, type=int)
        adjustments, total = uc.list_adjustments(
            warehouse_id=warehouse_id, adjustment_type=adj_type,
            skip=skip, limit=limit,
        )
        return jsonify({"adjustments": [_json_adjustment(a) for a in adjustments], "total": total})
    finally:
        session.close()


@inv_bp.route("/adjustments/<int:adjustment_id>", methods=["GET"])
def get_adjustment(adjustment_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_adjustment(adjustment_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_adjustment(result.get_data()))
    finally:
        session.close()


@inv_bp.route("/adjustments/<int:adjustment_id>/post", methods=["POST"])
def post_adjustment(adjustment_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.post_adjustment(adjustment_id, gl_ref=request.json.get("gl_ref") if request.json else None)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_adjustment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Valuation
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/valuation/moving-average/<int:item_id>", methods=["POST"])
def calculate_moving_average(item_id):
    data = request.get_json()
    if not data or "new_quantity" not in data or "new_unit_price" not in data:
        return jsonify({"error": "new_quantity and new_unit_price required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.calculate_moving_average(
            item_id,
            Decimal(str(data["new_quantity"])),
            Decimal(str(data["new_unit_price"])),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    finally:
        session.close()


@inv_bp.route("/valuation/revalue/<int:item_id>", methods=["POST"])
def revalue_item(item_id):
    data = request.get_json()
    if not data or "new_unit_price" not in data:
        return jsonify({"error": "new_unit_price required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.revalue_item(item_id, Decimal(str(data["new_unit_price"])))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_item(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# GL Posting
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/gl-accounts/<int:item_id>", methods=["GET"])
def get_gl_accounts(item_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_gl_accounts_for_item(item_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@inv_bp.route("/gl-entries/receipt/<int:receipt_id>", methods=["GET"])
def get_receipt_gl_entries(receipt_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.build_receipt_gl_entries(receipt_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify({"entries": result.get_data()})
    finally:
        session.close()


@inv_bp.route("/gl-entries/issue/<int:issue_id>", methods=["GET"])
def get_issue_gl_entries(issue_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.build_issue_gl_entries(issue_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify({"entries": result.get_data()})
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Reports
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/reports/inventory", methods=["GET"])
def inventory_report():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        warehouse_id = request.args.get("warehouse_id", type=int)
        category_id = request.args.get("category_id", type=int)
        result = uc.get_inventory_report(warehouse_id=warehouse_id, category_id=category_id)
        return jsonify(result.get_data())
    finally:
        session.close()


@inv_bp.route("/reports/low-stock", methods=["GET"])
def low_stock_report():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.get_low_stock_report()
        return jsonify(result.get_data())
    finally:
        session.close()


@inv_bp.route("/reports/movements/<int:item_id>", methods=["GET"])
def stock_movement_report(item_id):
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        if not date_from or not date_to:
            return jsonify({"error": "date_from and date_to required"}), 400
        result = uc.get_stock_movement_report(item_id, date.fromisoformat(date_from), date.fromisoformat(date_to))
        return jsonify(result.get_data())
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Import / Export
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/import/items", methods=["POST"])
def import_items():
    data = request.get_json()
    if not data or not isinstance(data.get("rows"), list):
        return jsonify({"error": "rows array required"}), 400
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        result = uc.import_items_from_csv(data["rows"])
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@inv_bp.route("/export/items", methods=["GET"])
def export_items():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        category_id = request.args.get("category_id", type=int)
        items = uc.export_items(category_id=category_id)
        return jsonify({"items": items, "total": len(items)})
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════════════════════

@inv_bp.route("/dashboard", methods=["GET"])
def dashboard():
    session = _get_session()
    try:
        from use_cases.inventory import InventoryUseCases
        uc = InventoryUseCases(session)
        return jsonify(uc.get_dashboard())
    finally:
        session.close()
