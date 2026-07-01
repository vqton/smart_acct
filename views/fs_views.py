from flask import render_template, request, session, redirect, url_for, flash
from . import views_bp
from use_cases.fs import FSUseCases
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from domain import FinancialStatementType, FSStatus


def _get_session():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager.get_session()


def _get_entity():
    return {"entity_name": "", "address": ""}


_TYPE_ROUTES = {
    "bs": (FinancialStatementType.BALANCE_SHEET_GC, "fs/b01_dn.html"),
    "is": (FinancialStatementType.INCOME_STATEMENT_GC, "fs/b02_dn.html"),
    "cf": (FinancialStatementType.CASH_FLOW_GC, "fs/b03_dn.html"),
    "notes": (FinancialStatementType.NOTES_GC, "fs/b09_dn.html"),
}


def _render_fs_view(kind: str):
    stype, template = _TYPE_ROUTES[kind]
    period = request.args.get("period") or session.get("period")
    if not period:
        flash("Vui lòng chọn kỳ kế toán.", "warning")
        return redirect(url_for("views.fs"))

    session_db = _get_session()
    try:
        uc = FSUseCases(session_db)
        statements = uc.list_statements(
            period=period, statement_type=stype,
            status=FSStatus.APPROVED, limit=1,
        )
        if not statements:
            statements = uc.list_statements(
                period=period, statement_type=stype, limit=1,
            )
        if not statements:
            flash(f"Chưa có báo cáo {stype.value} cho kỳ {period}. Vui lòng tạo báo cáo trước.", "warning")
            return redirect(url_for("views.fs", period=period))

        fs = statements[0]
        entity = _get_entity()
        return render_template(template, fs=fs, entity=entity)
    except Exception as e:
        flash(f"Lỗi tải báo cáo: {e}", "danger")
        return redirect(url_for("views.fs"))
    finally:
        session_db.close()


@views_bp.route("/fs/bs")
def fs_bs():
    return _render_fs_view("bs")


@views_bp.route("/fs/is")
def fs_is():
    return _render_fs_view("is")


@views_bp.route("/fs/cf")
def fs_cf():
    return _render_fs_view("cf")


@views_bp.route("/fs/notes")
def fs_notes():
    return _render_fs_view("notes")


@views_bp.route("/fs")
def fs():
    session_db = _get_session()
    try:
        uc = FSUseCases(session_db)
        page = request.args.get("page", 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page

        statements = uc.list_statements(
            period=request.args.get("period"),
            statement_type=None,
            status=None,
            entity_id=None,
            limit=per_page,
            offset=offset,
        )

        return render_template("fs/list.html",
            period=session.get("period"),
            statements=statements,
            statement_types=FinancialStatementType,
            page=page,
            per_page=per_page,
        )
    finally:
        session_db.close()
