from io import BytesIO
from flask import Blueprint, request, jsonify, current_app

from use_cases.coa_use_cases import COAUseCases
from use_cases.coa_validate_use_case import COAValidateUseCase
from use_cases.coa_import_use_case import COAImportUseCase
from use_cases.coa_export_use_case import COAExportUseCase
from use_cases.coa_versioning_use_case import COAVersioningUseCase
from use_cases.coa_ifrs_use_case import COAIFRSUseCase
from use_cases.coa_usage_use_case import COAUsageUseCase
from use_cases.coa_template_use_case import COATemplateUseCase
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


@coa_bp.route("/import", methods=["POST"])
def import_accounts():
    session = _get_session()
    try:
        uc = COAImportUseCase(session)
        data = request.get_json()
        if data and "accounts" in data:
            result = uc.import_from_dicts(
                data["accounts"],
                regime=data.get("regime", "tt99_2025"),
            )
        elif request.files:
            f = request.files.get("file")
            if not f:
                return jsonify({"error": "No file uploaded"}), 400
            tmp = "/tmp/_coa_import.xlsx"
            f.save(tmp)
            result = uc.import_from_excel(
                tmp,
                regime=request.form.get("regime", "tt99_2025"),
            )
        else:
            return jsonify({"error": "Provide JSON body with 'accounts' array or upload Excel file"}), 400

        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@coa_bp.route("/export", methods=["GET"])
def export_accounts():
    session = _get_session()
    try:
        uc = COAExportUseCase(session)
        fmt = request.args.get("format", "xlsx")
        regime = request.args.get("regime")
        status = request.args.get("status")

        if fmt == "csv":
            buf = BytesIO()
            uc.export_to_csv(buf, regime=regime, status=status)
            buf.seek(0)
            from flask import Response as FlaskResponse
            return FlaskResponse(
                buf.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment; filename=chart_of_accounts.csv"},
            )
        elif fmt == "json":
            data = uc.export_to_json(regime=regime, status=status)
            return jsonify(data)
        else:
            buf = BytesIO()
            uc.export_to_excel(buf, regime=regime, status=status)
            buf.seek(0)
            from flask import Response as FlaskResponse
            return FlaskResponse(
                buf.getvalue(),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=chart_of_accounts.xlsx"},
            )
    finally:
        session.close()


@coa_bp.route("/versions", methods=["POST"])
def create_version():
    session = _get_session()
    try:
        uc = COAVersioningUseCase(session)
        data = request.get_json() or {}
        result = uc.create_snapshot(
            created_by=data.get("created_by"),
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@coa_bp.route("/versions", methods=["GET"])
def list_versions():
    session = _get_session()
    try:
        uc = COAVersioningUseCase(session)
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
        versions = uc.list_versions(limit=limit, offset=offset)
        return jsonify({"versions": versions, "total": len(versions)})
    finally:
        session.close()


@coa_bp.route("/versions/<int:version_id>", methods=["GET"])
def get_version(version_id):
    session = _get_session()
    try:
        uc = COAVersioningUseCase(session)
        result = uc.get_version(version_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/versions/diff", methods=["GET"])
def diff_versions():
    v1 = request.args.get("v1", type=int)
    v2 = request.args.get("v2", type=int)
    if not v1 or not v2:
        return jsonify({"error": "Query params 'v1' and 'v2' required"}), 400

    session = _get_session()
    try:
        uc = COAVersioningUseCase(session)
        result = uc.diff_versions(v1, v2)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/ifrs-mapping", methods=["POST"])
def create_ifrs_mapping():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = COAIFRSUseCase(session)
        result = uc.create_mapping(
            vas_account_code=data["vas_account_code"],
            ifrs_account_code=data["ifrs_account_code"],
            mapping_type=data.get("mapping_type", "1:1"),
            expression=data.get("expression"),
            description=data.get("description"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@coa_bp.route("/ifrs-mapping", methods=["GET"])
def list_ifrs_mappings():
    session = _get_session()
    try:
        uc = COAIFRSUseCase(session)
        vas_code = request.args.get("vas_account_code")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        mappings = uc.list_mappings(vas_account_code=vas_code, limit=limit, offset=offset)
        return jsonify({"mappings": mappings, "total": len(mappings)})
    finally:
        session.close()


@coa_bp.route("/ifrs-mapping/<int:mapping_id>", methods=["GET"])
def get_ifrs_mapping(mapping_id):
    session = _get_session()
    try:
        uc = COAIFRSUseCase(session)
        result = uc.get_mapping(mapping_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/ifrs-mapping/<int:mapping_id>", methods=["DELETE"])
def delete_ifrs_mapping(mapping_id):
    session = _get_session()
    try:
        uc = COAIFRSUseCase(session)
        result = uc.delete_mapping(mapping_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Mapping {mapping_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@coa_bp.route("/ifrs-mapping/coverage", methods=["GET"])
def ifrs_coverage():
    session = _get_session()
    try:
        uc = COAIFRSUseCase(session)
        return jsonify(uc.get_coverage())
    finally:
        session.close()


@coa_bp.route("/compliance/scan", methods=["GET"])
def compliance_scan():
    session = _get_session()
    try:
        uc = COAValidateUseCase(session)
        result = uc.run_compliance_scan()
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/compliance/<code>", methods=["GET"])
def check_compliance(code):
    session = _get_session()
    try:
        uc = COAValidateUseCase(session)
        result = uc.check_compliance(code)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/templates", methods=["GET"])
def list_templates():
    session = _get_session()
    try:
        uc = COATemplateUseCase(session)
        return jsonify({"templates": uc.list_templates()})
    finally:
        session.close()


@coa_bp.route("/templates/<template_id>", methods=["GET"])
def preview_template(template_id):
    session = _get_session()
    try:
        uc = COATemplateUseCase(session)
        result = uc.preview_template(template_id)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@coa_bp.route("/templates/<template_id>/apply", methods=["POST"])
def apply_template(template_id):
    session = _get_session()
    try:
        uc = COATemplateUseCase(session)
        data = request.get_json() or {}
        result = uc.apply_template(template_id, clear_existing=data.get("clear_existing", False))
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@coa_bp.route("/usage/<code>", methods=["GET"])
def check_account_usage(code):
    session = _get_session()
    try:
        uc = COAUsageUseCase(session)
        result = uc.check_usage(code)
        if result.is_failure():
            return jsonify({"error": str(result.error)}), 404
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
