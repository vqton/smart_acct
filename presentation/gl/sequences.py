from flask import request, jsonify

from presentation import resolve_error
from presentation.gl import gl_bp, _get_session
from use_cases.gl_use_cases import GLUseCases


@gl_bp.route("/journal-sequences", methods=["GET"])
def list_journal_sequences():
    session = _get_session()
    try:
        uc = GLUseCases(session)
        fiscal_year = request.args.get("fiscal_year", type=int)
        sequences = uc.list_journal_sequences(fiscal_year)
        return jsonify({"sequences": sequences, "total": len(sequences)})
    finally:
        session.close()


@gl_bp.route("/journal-sequences/next-number", methods=["GET"])
def get_next_journal_number():
    session = _get_session()
    try:
        uc = GLUseCases(session)
        journal_type = request.args.get("journal_type", "general")
        period = request.args.get("period")
        result = uc.get_next_journal_number(journal_type, period)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    finally:
        session.close()


@gl_bp.route("/journal-sequences/<journal_type>/<int:fiscal_year>", methods=["GET"])
def get_journal_sequence(journal_type, fiscal_year):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.get_journal_sequence(journal_type, fiscal_year)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(result.get_data())
    finally:
        session.close()
