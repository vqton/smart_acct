from io import BytesIO
from flask import request, jsonify, Response as FlaskResponse

from domain import AccountingRegime
from infrastructure.database import DatabaseError
from presentation import resolve_error
from presentation.coa import coa_bp, _get_session
from use_cases.coa_validate_use_case import COAValidateUseCase
from use_cases.coa_import_use_case import COAImportUseCase
from use_cases.coa_export_use_case import COAExportUseCase
from use_cases.coa_versioning_use_case import COAVersioningUseCase
from use_cases.coa_ifrs_use_case import COAIFRSUseCase
from use_cases.coa_usage_use_case import COAUsageUseCase
from use_cases.coa_template_use_case import COATemplateUseCase


# ── Validation ────────────────────────────────────────────────────────

@coa_bp.route("/validate/<code>", methods=["GET"])
def validate_account(code):
    session = _get_session()
    try:
        uc = COAValidateUseCase(session)
        result = uc.validate_account(code)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
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


# ── Import / Export ───────────────────────────────────────────────────

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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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
            return FlaskResponse(
                buf.getvalue(),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=chart_of_accounts.xlsx"},
            )
    finally:
        session.close()


# ── Versioning ────────────────────────────────────────────────────────

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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


# ── IFRS Mapping ──────────────────────────────────────────────────────

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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Mapping {mapping_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
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


# ── Compliance ────────────────────────────────────────────────────────

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
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


# ── Templates ─────────────────────────────────────────────────────────

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
            return jsonify({"error": resolve_error(result.error)}), 404
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
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Usage ─────────────────────────────────────────────────────────────

@coa_bp.route("/usage/<code>", methods=["GET"])
def check_account_usage(code):
    session = _get_session()
    try:
        uc = COAUsageUseCase(session)
        result = uc.check_usage(code)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()
