from flask import Blueprint, request, jsonify, current_app
from datetime import date
from decimal import Decimal, InvalidOperation

from presentation import resolve_error
from use_cases.gl_use_cases import GLUseCases
from domain import ValidationError, DoubleEntryError

gl_bp = Blueprint("gl", __name__)


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_entry(entry) -> dict:
    return {
        "id": entry.id,
        "journal_number": entry.journal_number,
        "transaction_date": entry.transaction_date.isoformat(),
        "description": entry.description,
        "period": entry.period,
        "is_posted": entry.is_posted,
        "posted_date": entry.posted_date.isoformat() if entry.posted_date else None,
        "source_module": entry.source_module,
        "created_by": entry.created_by,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
        "lines": [_json_line(l) for l in entry.lines],
    }


def _json_line(line) -> dict:
    return {
        "id": line.id,
        "account_id": line.account_id,
        "debit": str(line.debit),
        "credit": str(line.credit),
        "description": line.description,
        "vat_rate": str(line.vat_rate) if line.vat_rate else None,
        "line_type": line.line_type,
        "is_taxable": line.is_taxable,
        "tax_code": line.tax_code,
    }


@gl_bp.route("/entries", methods=["POST"])
def create_entry():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    if "lines" not in data or not data["lines"]:
        return jsonify({"error": "At least one journal line required"}), 400

    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.create_entry(
            journal_number=data["journal_number"],
            transaction_date=date.fromisoformat(data["transaction_date"]),
            description=data["description"],
            lines=data["lines"],
            period=data.get("period"),
            source_module=data.get("source_module"),
            created_by=data.get("created_by"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_entry(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/entries", methods=["GET"])
def list_entries():
    session = _get_session()
    try:
        uc = GLUseCases(session)
        period = request.args.get("period")
        is_posted = request.args.get("is_posted")
        account_id = request.args.get("account_id")
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))

        is_posted_parsed = None
        if is_posted is not None:
            is_posted_parsed = is_posted.lower() == "true"

        from_date_parsed = date.fromisoformat(from_date) if from_date else None
        to_date_parsed = date.fromisoformat(to_date) if to_date else None

        entries = uc.list_entries(
            period=period,
            is_posted=is_posted_parsed,
            account_id=account_id,
            from_date=from_date_parsed,
            to_date=to_date_parsed,
            limit=limit,
            offset=offset,
        )
        return jsonify({"entries": [_json_entry(e) for e in entries], "total": len(entries)})
    except ValueError as e:
        return jsonify({"error": f"Invalid parameter: {e}"}), 400
    finally:
        session.close()


@gl_bp.route("/entries/<int:entry_id>", methods=["GET"])
def get_entry(entry_id):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.get_entry(entry_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_entry(result.get_data()))
    finally:
        session.close()


@gl_bp.route("/entries/<int:entry_id>", methods=["PUT"])
def update_entry(entry_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    session = _get_session()
    try:
        uc = GLUseCases(session)
        allowed = {"description", "period", "source_module"}
        kwargs = {k: v for k, v in data.items() if k in allowed}
        result = uc.update_entry(entry_id, **kwargs)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_entry(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/entries/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.delete_entry(entry_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Journal entry {entry_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/entries/<int:entry_id>/post", methods=["POST"])
def post_entry(entry_id):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.post_entry(entry_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_entry(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/balances/<account_id>", methods=["GET"])
def get_account_balance(account_id):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        period = request.args.get("period")
        balance = uc.get_account_balance(account_id, period)
        return jsonify(balance)
    finally:
        session.close()


# ── Period close ────────────────────────────────────────────────────────

@gl_bp.route("/periods", methods=["POST"])
def create_period():
    data = request.get_json()
    if not data or "period" not in data:
        return jsonify({"error": "period field required"}), 400
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.create_period(
            period=data["period"],
            type_=data.get("type", "monthly"),
            start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
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


@gl_bp.route("/periods/current", methods=["GET"])
def current_period():
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.get_current_period()
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@gl_bp.route("/periods/<period>", methods=["GET"])
def get_period(period):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.get_period(period)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()


@gl_bp.route("/periods", methods=["GET"])
def list_periods():
    status = request.args.get("status")
    if status and status not in ("open", "closed"):
        return jsonify({"error": "status must be 'open' or 'closed'"}), 400
    session = _get_session()
    try:
        uc = GLUseCases(session)
        periods = uc.list_periods(status)
        return jsonify({"periods": periods, "total": len(periods)})
    finally:
        session.close()


@gl_bp.route("/periods/<period>/close", methods=["POST"])
def close_period(period):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.close_period(
            period,
            closed_by=data.get("closed_by", "system"),
            notes=data.get("notes"),
            force=data.get("force", False),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/periods/<period>/reopen", methods=["POST"])
def reopen_period(period):
    data = request.get_json() or {}
    reason = data.get("reason", "")
    if not reason:
        return jsonify({"error": "reason is required for reopening a period"}), 400
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.reopen_period(
            period,
            reopened_by=data.get("reopened_by", "system"),
            reason=reason,
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/periods/<period>/carry-forward", methods=["POST"])
def carry_forward(period):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.carry_forward(
            period,
            closed_by=data.get("closed_by", "system"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/periods/<period>/audit-log", methods=["GET"])
def period_audit_log(period):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        logs = uc.get_period_audit_log(period)
        return jsonify({"logs": logs, "total": len(logs)})
    finally:
        session.close()


# ── Financial statements ────────────────────────────────────────────────

@gl_bp.route("/statements/balance-sheet/<period>", methods=["GET"])
def balance_sheet(period):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.generate_balance_sheet(period)
        return jsonify(result)
    finally:
        session.close()


@gl_bp.route("/statements/income-statement/<period>", methods=["GET"])
def income_statement(period):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.generate_income_statement(period)
        return jsonify(result)
    finally:
        session.close()
