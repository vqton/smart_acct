from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.fa import (
    fa_bp, _get_session, _get_fa_use_cases,
    _json_category, _json_asset, _json_depreciation, _json_adjustment,
    _json_transfer, _json_disposal, _json_inventory, _json_inventory_line,
    _json_spare_part, _json_component, _json_biological, _json_biological_provision,
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


# ── Categories ────────────────────────────────────────────────────

@fa_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.create_category(
            code=data["code"],
            name=data["name"],
            asset_type=data.get("asset_type", "tangible"),
            asset_classification=data.get("asset_classification", "other"),
            default_depreciation_method=data.get("default_depreciation_method", "straight_line"),
            default_useful_life_min=data.get("default_useful_life_min"),
            default_useful_life_max=data.get("default_useful_life_max"),
            description=data.get("description"),
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


@fa_bp.route("/categories", methods=["GET"])
def list_categories():
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        asset_type = request.args.get("asset_type")
        categories = uc.list_categories(asset_type=asset_type)
        return jsonify({"categories": [_json_category(c) for c in categories], "total": len(categories)})
    finally:
        session.close()


@fa_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        category = uc.get_category(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404
        return jsonify(_json_category(category))
    finally:
        session.close()


@fa_bp.route("/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
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


@fa_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
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


# ── Assets ────────────────────────────────────────────────────────

@fa_bp.route("/assets", methods=["POST"])
def register_asset():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name", "category_id", "original_cost",
                                        "acquisition_date", "in_use_date",
                                        "useful_life_months", "depreciation_method"])
    if err:
        return jsonify({"error": err}), 400
    err = _validate_date_format(data["acquisition_date"], "acquisition_date")
    if err:
        return jsonify({"error": err}), 400
    err = _validate_date_format(data["in_use_date"], "in_use_date")
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.register_asset(
            code=data["code"],
            name=data["name"],
            category_id=data["category_id"],
            asset_type=data.get("asset_type", "tangible"),
            asset_classification=data.get("asset_classification", "other"),
            original_cost=Decimal(str(data["original_cost"])),
            acquisition_date=date.fromisoformat(data["acquisition_date"]),
            in_use_date=date.fromisoformat(data["in_use_date"]),
            useful_life_months=data["useful_life_months"],
            depreciation_method=data["depreciation_method"],
            residual_value=Decimal(str(data.get("residual_value", "0"))),
            department_id=data.get("department_id"),
            location=data.get("location"),
            fund_source=data.get("fund_source", "owners_equity"),
            use_type=data.get("use_type", "production"),
            supplier=data.get("supplier"),
            invoice_ref=data.get("invoice_ref"),
            description=data.get("description"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_asset(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/assets", methods=["GET"])
def list_assets():
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        category_id = request.args.get("category_id", type=int)
        status = request.args.get("status")
        department_id = request.args.get("department_id", type=int)
        asset_type = request.args.get("asset_type")
        assets = uc.list_assets(
            category_id=category_id,
            status=status,
            department_id=department_id,
            asset_type=asset_type,
        )
        return jsonify({"assets": [_json_asset(a) for a in assets], "total": len(assets)})
    finally:
        session.close()


@fa_bp.route("/assets/search", methods=["GET"])
def search_assets():
    q = request.args.get("q", "")
    if not q.strip():
        return jsonify({"error": "Search query required"}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        assets = uc.search_assets(q)
        return jsonify({"assets": [_json_asset(a) for a in assets], "total": len(assets)})
    finally:
        session.close()


@fa_bp.route("/assets/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        asset = uc.get_asset(asset_id)
        if not asset:
            return jsonify({"error": "Asset not found"}), 404
        return jsonify(_json_asset(asset))
    finally:
        session.close()


@fa_bp.route("/assets/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.update_asset(asset_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_asset(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Depreciation ──────────────────────────────────────────────────

@fa_bp.route("/depreciation/run", methods=["POST"])
def run_depreciation():
    data = request.get_json() or {}
    period = data.get("period")
    if not period:
        return jsonify({"error": "period required"}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.run_depreciation(period=period)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/depreciation", methods=["GET"])
def get_depreciation_for_period():
    period = request.args.get("period")
    if not period:
        return jsonify({"error": "period query parameter required"}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        records = uc.get_depreciation_for_period(period)
        return jsonify({"records": [_json_depreciation(r) for r in records], "total": len(records)})
    finally:
        session.close()


@fa_bp.route("/assets/<int:asset_id>/depreciation", methods=["GET"])
def get_asset_depreciation(asset_id):
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        records = uc.get_asset_depreciation(asset_id)
        return jsonify({"records": [_json_depreciation(r) for r in records], "total": len(records)})
    finally:
        session.close()


# ── Adjustments ───────────────────────────────────────────────────

@fa_bp.route("/assets/<int:asset_id>/adjustments", methods=["POST"])
def adjust_asset(asset_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["adjustment_type", "amount", "reason", "effective_date"])
    if err:
        return jsonify({"error": err}), 400
    err = _validate_date_format(data["effective_date"], "effective_date")
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.adjust_asset(
            asset_id=asset_id,
            adjustment_type=data["adjustment_type"],
            amount=Decimal(str(data["amount"])),
            reason=data["reason"],
            effective_date=date.fromisoformat(data["effective_date"]),
            document_ref=data.get("document_ref"),
            appraised_by=data.get("appraised_by"),
            appraisal_date=date.fromisoformat(data["appraisal_date"]) if data.get("appraisal_date") else None,
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


# ── Transfers ─────────────────────────────────────────────────────

@fa_bp.route("/assets/<int:asset_id>/transfers", methods=["POST"])
def transfer_asset(asset_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["from_department_id", "to_department_id", "effective_date", "reason"])
    if err:
        return jsonify({"error": err}), 400
    err = _validate_date_format(data["effective_date"], "effective_date")
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.transfer_asset(
            asset_id=asset_id,
            from_department_id=data["from_department_id"],
            to_department_id=data["to_department_id"],
            effective_date=date.fromisoformat(data["effective_date"]),
            reason=data["reason"],
            from_location=data.get("from_location"),
            to_location=data.get("to_location"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_transfer(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Disposals ─────────────────────────────────────────────────────

@fa_bp.route("/assets/<int:asset_id>/disposals", methods=["POST"])
def dispose_asset(asset_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["disposal_type", "disposal_date", "reason"])
    if err:
        return jsonify({"error": err}), 400
    err = _validate_date_format(data["disposal_date"], "disposal_date")
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.dispose_asset(
            asset_id=asset_id,
            disposal_type=data["disposal_type"],
            disposal_date=date.fromisoformat(data["disposal_date"]),
            proceeds=Decimal(str(data.get("proceeds", "0"))),
            costs=Decimal(str(data.get("costs", "0"))),
            reason=data["reason"],
            buyer_info=data.get("buyer_info"),
            approved_by=data.get("approved_by"),
            document_ref=data.get("document_ref"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_disposal(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Inventories ───────────────────────────────────────────────────

@fa_bp.route("/inventories", methods=["POST"])
def create_inventory():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["inventory_date", "department_id"])
    if err:
        return jsonify({"error": err}), 400
    err = _validate_date_format(data["inventory_date"], "inventory_date")
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.create_inventory(
            inventory_date=date.fromisoformat(data["inventory_date"]),
            department_id=data["department_id"],
            notes=data.get("notes"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_inventory(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/inventories", methods=["GET"])
def list_inventories():
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        status = request.args.get("status")
        inventories = uc.list_inventories(status=status)
        return jsonify({"inventories": [_json_inventory(i) for i in inventories], "total": len(inventories)})
    finally:
        session.close()


@fa_bp.route("/inventories/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        inv = uc.get_inventory(inventory_id)
        if not inv:
            return jsonify({"error": "Inventory not found"}), 404
        return jsonify(_json_inventory(inv))
    finally:
        session.close()


@fa_bp.route("/inventories/<int:inventory_id>/lines", methods=["POST"])
def add_inventory_line(inventory_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["asset_id", "physical_quantity"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.add_inventory_line(
            inventory_id=inventory_id,
            asset_id=data["asset_id"],
            physical_quantity=data["physical_quantity"],
            book_quantity=data.get("book_quantity", 1),
            reason=data.get("reason"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_inventory_line(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/inventories/<int:inventory_id>/resolve", methods=["POST"])
def resolve_inventory(inventory_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.resolve_inventory(
            inventory_id=inventory_id,
            resolution=data.get("resolution"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_inventory(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Spare Parts & Components ──────────────────────────────────────

@fa_bp.route("/assets/<int:asset_id>/spare-parts", methods=["POST"])
def add_spare_part(asset_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["code", "name"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.add_spare_part(
            asset_id=asset_id,
            code=data["code"],
            name=data["name"],
            quantity=data.get("quantity", 1),
            unit=data.get("unit", "pcs"),
            value=Decimal(str(data.get("value", "0"))),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_spare_part(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/assets/<int:asset_id>/spare-parts", methods=["GET"])
def get_spare_parts(asset_id):
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        parts = uc.get_spare_parts(asset_id)
        return jsonify({"spare_parts": [_json_spare_part(p) for p in parts], "total": len(parts)})
    finally:
        session.close()


@fa_bp.route("/assets/<int:asset_id>/components", methods=["POST"])
def add_component(asset_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["name"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.add_component(
            asset_id=asset_id,
            name=data["name"],
            original_cost=Decimal(str(data.get("original_cost", "0"))),
            useful_life_months=data.get("useful_life_months"),
            depreciation_method=data.get("depreciation_method"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_component(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/assets/<int:asset_id>/components", methods=["GET"])
def get_components(asset_id):
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        components = uc.get_components(asset_id)
        return jsonify({"components": [_json_component(c) for c in components], "total": len(components)})
    finally:
        session.close()


# ── Biological Assets ─────────────────────────────────────────────

@fa_bp.route("/assets/<int:asset_id>/biological", methods=["POST"])
def register_biological_asset(asset_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["biological_type", "unit"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.register_biological_asset(
            asset_id=asset_id,
            biological_type=data["biological_type"],
            growth_stage=data.get("growth_stage", "immature"),
            quantity=Decimal(str(data.get("quantity", "1"))),
            unit=data["unit"],
            planting_date=date.fromisoformat(data["planting_date"]) if data.get("planting_date") else None,
            expected_harvest_date=date.fromisoformat(data["expected_harvest_date"]) if data.get("expected_harvest_date") else None,
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_biological(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/biological/<int:bio_id>", methods=["PUT"])
def update_biological_asset(bio_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.update_biological_asset(bio_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_biological(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/biological-list", methods=["GET"])
def list_biological_assets():
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        biological_type = request.args.get("biological_type")
        growth_stage = request.args.get("growth_stage")
        assets = uc.list_biological_assets(
            biological_type=biological_type,
            growth_stage=growth_stage,
        )
        return jsonify({"biological_assets": [_json_biological(b) for b in assets], "total": len(assets)})
    finally:
        session.close()


@fa_bp.route("/biological/<int:bio_id>/provisions", methods=["POST"])
def create_biological_provision(bio_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    err = _validate_json_fields(data, ["period", "provision_amount", "reason"])
    if err:
        return jsonify({"error": err}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.create_biological_provision(
            biological_asset_id=bio_id,
            period=data["period"],
            provision_amount=Decimal(str(data["provision_amount"])),
            reason=data["reason"],
            provision_type=data.get("provision_type", "new"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_biological_provision(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Reports ───────────────────────────────────────────────────────

@fa_bp.route("/reports/asset-register", methods=["GET"])
def get_asset_register_report():
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        asset_type = request.args.get("asset_type")
        department_id = request.args.get("department_id")
        report = uc.get_asset_register_report(
            asset_type=asset_type,
            department_id=department_id,
        )
        return jsonify(report)
    finally:
        session.close()


@fa_bp.route("/reports/depreciation-schedule", methods=["GET"])
def get_depreciation_schedule_report():
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        asset_id = request.args.get("asset_id", type=int)
        period = request.args.get("period")
        report = uc.get_depreciation_schedule_report(
            asset_id=asset_id,
            period=period,
        )
        return jsonify(report)
    finally:
        session.close()


@fa_bp.route("/reports/asset-increase-decrease", methods=["GET"])
def get_asset_increase_decrease_report():
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    if not from_date or not to_date:
        return jsonify({"error": "from_date and to_date query parameters required"}), 400
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        report = uc.get_asset_increase_decrease_report(
            from_date=date.fromisoformat(from_date),
            to_date=date.fromisoformat(to_date),
        )
        return jsonify(report)
    finally:
        session.close()


@fa_bp.route("/reports/asset-status-summary", methods=["GET"])
def get_asset_status_summary():
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        asset_type = request.args.get("asset_type")
        report = uc.get_asset_status_summary(asset_type=asset_type)
        return jsonify(report)
    finally:
        session.close()


# ── TT 99/2025 Migration ─────────────────────────────────────────

@fa_bp.route("/migration/tt99", methods=["POST"])
def run_tt99_migration():
    data = request.get_json() or {}
    dry_run = data.get("dry_run", True)
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.run_tt99_migration(dry_run=dry_run)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Suspension (TT 30/2025) ──────────────────────────────────────

@fa_bp.route("/assets/<int:asset_id>/suspend-depreciation", methods=["POST"])
def suspend_depreciation(asset_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.suspend_depreciation(
            asset_id=asset_id,
            reason=data.get("reason"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_asset(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@fa_bp.route("/assets/<int:asset_id>/resume-depreciation", methods=["POST"])
def resume_depreciation(asset_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = _get_fa_use_cases()
        result = uc.resume_depreciation(
            asset_id=asset_id,
            reason=data.get("reason"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_asset(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()
