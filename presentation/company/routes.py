from flask import g, jsonify, request, current_app

from domain.company import (
    CompanyCreate, CompanyUpdate, FiscalYearCreate,
    NumberingRuleUpdate, SetupSection, DocumentType,
)
from domain.common import VASValidationError, Result
from domain.i18n import ErrorCodes
from presentation import resolve_error
from presentation.company import company_bp


def _get_company_use_cases():
    from use_cases.company import CompanyUseCases
    return CompanyUseCases(
        session_factory=current_app.db_manager.get_session,
    )


# ── UC-COMP-01/03/04: Company ────────────────────────────────────────


@company_bp.route("/api/v1/company", methods=["GET"])
def get_active_company():
    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 404
    return jsonify(result.get_data()), 200


@company_bp.route("/api/v1/company", methods=["POST"])
def create_company():
    data = request.get_json(silent=True) or {}
    try:
        req = CompanyCreate(
            name=data.get("name", ""),
            tax_code=data.get("tax_code"),
            address=data.get("address"),
            phone=data.get("phone"),
            email=data.get("email"),
            website=data.get("website"),
            business_reg_number=data.get("business_reg_number"),
            date_format=data.get("date_format", "DD/MM/YYYY"),
            currency_code=data.get("currency_code", "VND"),
            fiscal_year_start_month=data.get("fiscal_year_start_month", 1),
            accounting_regime=data.get("accounting_regime", "TT99"),
            locale=data.get("locale", "vi"),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_company_use_cases()
    result = uc.create_company(req)
    if result.is_failure():
        err = result.get_error()
        code = 409 if err.msgid == ErrorCodes.COMPANY_ALREADY_EXISTS else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code

    return jsonify(result.get_data()), 201


@company_bp.route("/api/v1/company", methods=["PUT"])
def update_company():
    data = request.get_json(silent=True) or {}
    try:
        updates = CompanyUpdate(
            name=data.get("name"),
            tax_code=data.get("tax_code"),
            address=data.get("address"),
            phone=data.get("phone"),
            email=data.get("email"),
            website=data.get("website"),
            logo_url=data.get("logo_url"),
            business_reg_number=data.get("business_reg_number"),
            date_format=data.get("date_format"),
            currency_code=data.get("currency_code"),
            fiscal_year_start_month=data.get("fiscal_year_start_month"),
            accounting_regime=data.get("accounting_regime"),
            locale=data.get("locale"),
            is_active=data.get("is_active"),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404

    company = result.get_data()
    result = uc.update_company(company["id"], updates)
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400

    updated = result.get_data()
    return jsonify({
        "id": updated.id,
        "name": updated.name,
        "tax_code": updated.tax_code,
        "locale": updated.locale,
        "currency_code": updated.currency_code,
    }), 200


# ── UC-COMP-05/06/07: Fiscal Years ────────────────────────────────────


@company_bp.route("/api/v1/company/fiscal-years", methods=["GET"])
def list_fiscal_years():
    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    company = result.get_data()
    result = uc.list_fiscal_years(company["id"])
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@company_bp.route("/api/v1/company/fiscal-years", methods=["POST"])
def create_fiscal_year():
    data = request.get_json(silent=True) or {}
    try:
        req = FiscalYearCreate(
            fiscal_year=data.get("fiscal_year", 0),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            is_current=data.get("is_current", False),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    company = result.get_data()

    result = uc.create_fiscal_year(company["id"], req)
    if result.is_failure():
        err = result.get_error()
        code = 409 if err.msgid in (ErrorCodes.FISCAL_YEAR_EXISTS, ErrorCodes.FISCAL_YEAR_OVERLAP) else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify(result.get_data()), 201


@company_bp.route("/api/v1/company/fiscal-years/<int:fiscal_year>/close", methods=["POST"])
def close_fiscal_year(fiscal_year: int):
    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    company = result.get_data()

    result = uc.close_fiscal_year(company["id"], fiscal_year)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.FISCAL_YEAR_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Fiscal year closed"}), 200


# ── UC-COMP-08/09/10: Numbering Rules ────────────────────────────────


@company_bp.route("/api/v1/company/numbering-rules", methods=["GET"])
def list_numbering_rules():
    document_type_str = request.args.get("document_type")
    fiscal_year = request.args.get("fiscal_year", type=int)
    document_type = DocumentType(document_type_str) if document_type_str else None

    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    company = result.get_data()

    result = uc.list_numbering_rules(company["id"], document_type, fiscal_year)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@company_bp.route("/api/v1/company/numbering-rules/<int:rule_id>", methods=["PUT"])
def update_numbering_rule(rule_id: int):
    data = request.get_json(silent=True) or {}
    try:
        req = NumberingRuleUpdate(
            prefix=data.get("prefix"),
            suffix=data.get("suffix"),
            next_number=data.get("next_number"),
            pad_length=data.get("pad_length"),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    company = result.get_data()

    result = uc.update_numbering_rule(company["id"], rule_id, req)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.NUMBERING_RULE_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify(result.get_data()), 200


@company_bp.route("/api/v1/company/next-number", methods=["GET"])
def get_next_number():
    document_type_str = request.args.get("document_type", "")
    fiscal_year = request.args.get("fiscal_year", type=int)
    if not document_type_str or not fiscal_year:
        return jsonify({"error": resolve_error(ErrorCodes.QUERY_PARAM_REQUIRED)}), 400

    try:
        document_type = DocumentType(document_type_str)
    except ValueError:
        return jsonify({"error": resolve_error(ErrorCodes.INVALID_ACCOUNT_TYPE)}), 400

    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    company = result.get_data()

    result = uc.get_next_number(company["id"], document_type, fiscal_year)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.NUMBERING_RULE_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify(result.get_data()), 200


# ── UC-COMP-11: Setup Checklist ──────────────────────────────────────


@company_bp.route("/api/v1/company/setup-checklist", methods=["GET"])
def get_setup_checklist():
    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    company = result.get_data()

    result = uc.get_setup_checklist(company["id"])
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@company_bp.route("/api/v1/company/setup-checklist/<section>", methods=["PUT"])
def mark_setup_complete(section: str):
    try:
        setup_section = SetupSection(section)
    except ValueError:
        return jsonify({"error": resolve_error(ErrorCodes.SETUP_SECTION_NOT_FOUND)}), 400

    uc = _get_company_use_cases()
    result = uc.get_active_company()
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    company = result.get_data()

    result = uc.mark_setup_complete(company["id"], setup_section)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.SETUP_SECTION_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify(result.get_data()), 200
