from datetime import date
from flask import request, jsonify

from presentation import resolve_error
from presentation.gl import gl_bp, _get_session
from use_cases.gl_use_cases import GLUseCases


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
