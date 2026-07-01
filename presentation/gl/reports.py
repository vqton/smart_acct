from datetime import date
from flask import request, jsonify, render_template, send_file
from decimal import Decimal
from io import BytesIO

from presentation import resolve_error
from presentation.gl import gl_bp, _get_session
from use_cases.gl_use_cases import GLUseCases
from use_cases.gl.templates import (
    generate_journal_template, generate_s01_ledger, generate_subsidiary_template,
    JOURNAL_TYPE_TEMPLATE_MAP, TEMPLATE_NAMES,
)
from domain import ValidationError, JournalType


@gl_bp.route("/reports/journal/<period>", methods=["GET"])
def generate_journal_report(period):
    journal_type = request.args.get("journal_type", "general")
    format = request.args.get("format", "json")
    company_name = request.args.get("company_name", "")
    address = request.args.get("address", "")

    session = _get_session()
    try:
        uc = GLUseCases(session)
        entries = uc.list_entries(period=period, is_posted=True)
        entries_filtered = [e for e in entries if hasattr(e, 'journal_type') and e.journal_type.value == journal_type]

        jt = JournalType(journal_type)
    except (ValueError, ValidationError) as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

    template_code = JOURNAL_TYPE_TEMPLATE_MAP.get(jt, "S03c-DN")
    data = generate_journal_template(template_code, entries_filtered, period, company_name, address)

    if format == "html":
        return render_template("s03_dn_journal.html", **data)
    return jsonify(data)


@gl_bp.route("/reports/general-ledger/<account_code>/<period>", methods=["GET"])
def generate_general_ledger(account_code, period):
    company_name = request.args.get("company_name", "")
    address = request.args.get("address", "")
    format = request.args.get("format", "json")

    session = _get_session()
    try:
        uc = GLUseCases(session)
        entries = uc.list_entries(period=period, is_posted=True, account_id=account_code)
        account_name = account_code
        try:
            from infrastructure.repositories.gl_repository import GLRepository
            from infrastructure.models.coa_models import COAModel
            from sqlalchemy import select
            model = session.execute(
                select(COAModel).where(COAModel.code == account_code)
            ).scalar_one_or_none()
            if model:
                account_name = model.name
        except Exception:
            pass

        opening_balance = uc.get_account_balance(account_code).get("balance", 0)

        data = generate_s01_ledger(
            account_code=account_code, account_name=account_name,
            entries=entries, period=period,
            opening_balance=opening_balance,
            company_name=company_name, address=address,
        )
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

    if format == "html":
        return render_template("s01_dn_general_ledger.html", **data)
    return jsonify(data)


@gl_bp.route("/reports/subsidiary/<subsidiary_type>/<period>", methods=["GET"])
def generate_subsidiary_report(subsidiary_type, period):
    company_name = request.args.get("company_name", "")
    address = request.args.get("address", "")
    entity_id = request.args.get("entity_id", type=int)
    format = request.args.get("format", "json")

    template_code = "S06-DN" if subsidiary_type == "ar" else "S05-DN" if subsidiary_type == "ap" else f"S{subsidiary_type.upper()}-DN"

    session = _get_session()
    try:
        uc = GLUseCases(session)
        entries = uc.get_subsidiary_ledger(
            subsidiary_type=subsidiary_type, period=period, entity_id=entity_id,
        )

        data = generate_subsidiary_template(
            template_code=template_code,
            subsidiary_type=subsidiary_type,
            entries=entries,
            period=period,
            company_name=company_name,
            address=address,
        )
    except ValidationError as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()

    if format == "html":
        return render_template("s05_s06_dn_subsidiary.html", **data)
    return jsonify(data)


@gl_bp.route("/reports/balance-sheet/<period>", methods=["GET"])
def balance_sheet_report(period):
    format = request.args.get("format", "json")
    session = _get_session()
    try:
        uc = GLUseCases(session)
        data = uc.generate_balance_sheet(period)
    finally:
        session.close()
    if format == "html":
        return render_template("trial_balance.html", **data)
    return jsonify(data)


@gl_bp.route("/reports/income-statement/<period>", methods=["GET"])
def income_statement_report(period):
    format = request.args.get("format", "json")
    session = _get_session()
    try:
        uc = GLUseCases(session)
        data = uc.generate_income_statement(period)
    finally:
        session.close()
    return jsonify(data)


@gl_bp.route("/reports/trial-balance/<period>", methods=["GET"])
def trial_balance_report(period):
    format = request.args.get("format", "json")
    session = _get_session()
    try:
        uc = GLUseCases(session)
        data = uc.generate_trial_balance(period)
    finally:
        session.close()
    if format == "html":
        return render_template("trial_balance.html", **data)
    return jsonify(data)


@gl_bp.route("/reports/cash-flow/<period>", methods=["GET"])
def cash_flow_report(period):
    method = request.args.get("method", "direct")
    format = request.args.get("format", "json")
    session = _get_session()
    try:
        uc = GLUseCases(session)
        data = uc.generate_cash_flow(period, method)
    finally:
        session.close()
    if format == "html":
        return render_template("cash_flow.html", **data)
    return jsonify(data)


@gl_bp.route("/reports/export/<report_type>/<period>", methods=["GET"])
def export_report(report_type, period):
    export_format = request.args.get("format", "pdf")
    session = _get_session()
    try:
        uc = GLUseCases(session)
        if report_type == "trial-balance":
            data = uc.generate_trial_balance(period)
            html = render_template("trial_balance.html", **data)
        elif report_type == "cash-flow":
            method = request.args.get("method", "direct")
            data = uc.generate_cash_flow(period, method)
            html = render_template("cash_flow.html", **data)
        elif report_type == "balance-sheet":
            data = uc.generate_balance_sheet(period)
            html = render_template("trial_balance.html", **data)
        else:
            return jsonify({"error": f"Unknown report type: {report_type}"}), 400

        if export_format == "pdf":
            from weasyprint import HTML
            pdf_bytes = HTML(string=html).write_pdf()
            return send_file(
                BytesIO(pdf_bytes),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"{report_type}_{period}.pdf",
            )
        return html
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@gl_bp.route("/reports/templates", methods=["GET"])
def list_report_templates():
    templates = []
    for code, name in TEMPLATE_NAMES.items():
        templates.append({
            "code": code,
            "name": name,
            "endpoint": f"/api/v1/gl/reports/journal/<period>?journal_type=<type>&format=json",
        })
    return jsonify({"templates": templates, "total": len(templates)})
