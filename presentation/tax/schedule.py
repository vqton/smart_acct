from flask import request, jsonify
from presentation import resolve_error
from presentation.tax import tax_bp, _get_session, _json_schedule
from use_cases.tax import TaxUseCases
from domain import TaxType
from datetime import date


@tax_bp.route("/schedule", methods=["GET"])
def get_schedule():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        year = request.args.get("year", type=int)
        tax_type_str = request.args.get("tax_type")
        schedules = uc.get_tax_schedule(
            year=year or date.today().year,
            tax_type=TaxType(tax_type_str) if tax_type_str else None,
        )
        return jsonify({
            "schedules": [_json_schedule(s) for s in schedules],
            "total": len(schedules),
        })
    finally:
        session.close()


@tax_bp.route("/schedule/<int:schedule_id>", methods=["GET"])
def get_schedule_item(schedule_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_schedule(schedule_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_schedule(result.get_data()))
    finally:
        session.close()


@tax_bp.route("/schedule/<int:schedule_id>", methods=["PUT"])
def update_schedule(schedule_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.update_schedule(schedule_id, **data)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_schedule(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/schedule/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.delete_schedule(schedule_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": f"Schedule {schedule_id} deleted"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/schedule/generate", methods=["POST"])
def generate_schedule():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        year = data.get("year", date.today().year)
        result = uc.generate_schedule(year=year)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(result.get_data())
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@tax_bp.route("/reminders", methods=["GET"])
def get_reminders():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        days = request.args.get("days", 7, type=int)
        reminders = uc.get_due_reminders(days_ahead=days)
        return jsonify({
            "reminders": [_json_schedule(r) for r in reminders],
            "total": len(reminders),
        })
    finally:
        session.close()


@tax_bp.route("/summary", methods=["GET"])
def summary():
    session = _get_session()
    try:
        uc = TaxUseCases(session)
        result = uc.get_summary()
        return jsonify(result.get_data())
    finally:
        session.close()
