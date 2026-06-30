from datetime import date
from decimal import InvalidOperation
from flask import request, jsonify

from presentation import resolve_error
from presentation.gl import gl_bp, _get_session, _json_entry
from use_cases.gl_use_cases import GLUseCases
from domain import ValidationError, DoubleEntryError


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
            journal_number=data.get("journal_number", ""),
            transaction_date=date.fromisoformat(data["transaction_date"]),
            description=data["description"],
            lines=data["lines"],
            period=data.get("period"),
            journal_type=data.get("journal_type"),
            source_module=data.get("source_module"),
            created_by=data.get("created_by"),
            auto_number=data.get("auto_number", False),
            approved_by=data.get("approved_by"),
            ref_journal_number=data.get("ref_journal_number"),
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
