from flask import request, jsonify

from presentation import resolve_error
from presentation.gl import gl_bp, _get_session
from use_cases.gl import GLUseCases
from domain import ValidationError


@gl_bp.route("/subsidiary/<subsidiary_type>", methods=["GET"])
def get_subsidiary_ledger(subsidiary_type):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        entity_id = request.args.get("entity_id", type=int)
        period = request.args.get("period")
        account_code = request.args.get("account_code")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        entries = uc.get_subsidiary_ledger(
            subsidiary_type=subsidiary_type,
            entity_id=entity_id,
            period=period,
            account_code=account_code,
            limit=limit,
            offset=offset,
        )
        result = []
        for e in entries:
            result.append({
                "id": e.id,
                "subsidiary_type": e.subsidiary_type.value if hasattr(e.subsidiary_type, 'value') else str(e.subsidiary_type),
                "account_code": e.account_code,
                "entity_id": e.entity_id,
                "entity_name": e.entity_name,
                "transaction_date": e.transaction_date.isoformat(),
                "doc_ref": e.doc_ref,
                "doc_type": e.doc_type,
                "description": e.description,
                "debit": str(e.debit),
                "credit": str(e.credit),
                "balance": str(e.balance),
                "period": e.period,
                "journal_entry_id": e.journal_entry_id,
            })
        return jsonify({"entries": result, "total": len(result)})
    except ValidationError as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/subsidiary/<subsidiary_type>/summary/<period>", methods=["GET"])
def get_subsidiary_summary(subsidiary_type, period):
    session = _get_session()
    try:
        uc = GLUseCases(session)
        summary = uc.get_subsidiary_summary(subsidiary_type, period)
        return jsonify({"summary": summary, "total": len(summary)})
    except ValidationError as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@gl_bp.route("/subsidiary/<subsidiary_type>/post", methods=["POST"])
def post_to_subsidiary(subsidiary_type):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    journal_entry_id = data.get("journal_entry_id")
    entity_id = data.get("entity_id")
    entity_name = data.get("entity_name")
    doc_ref = data.get("doc_ref")
    doc_type = data.get("doc_type")

    if not all([journal_entry_id, entity_id, entity_name, doc_ref, doc_type]):
        return jsonify({"error": "journal_entry_id, entity_id, entity_name, doc_ref, doc_type required"}), 400

    session = _get_session()
    try:
        uc = GLUseCases(session)
        result = uc.post_to_subsidiary(
            journal_entry_id=journal_entry_id,
            subsidiary_type=subsidiary_type,
            entity_id=entity_id,
            entity_name=entity_name,
            doc_ref=doc_ref,
            doc_type=doc_type,
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Subsidiary ledger updated"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()
