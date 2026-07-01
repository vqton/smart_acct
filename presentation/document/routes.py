import os
from flask import jsonify, request, send_file

from domain.document import DocumentCategory
from domain.common import VASValidationError
from domain.i18n import ErrorCodes
from presentation import resolve_error
from presentation.document import document_bp, _get_doc_use_cases, _get_session


@document_bp.route("/api/v1/documents/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": resolve_error(ErrorCodes.DOCUMENT_FILE_REQUIRED)}), 400
    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": resolve_error(ErrorCodes.DOCUMENT_FILE_REQUIRED)}), 400

    title = request.form.get("title", "")
    document_type = request.form.get("document_type", "other")
    company_id = request.form.get("company_id", type=int, default=1)
    reference_type = request.form.get("reference_type")
    reference_id = request.form.get("reference_id", type=int)
    uploaded_by = request.form.get("uploaded_by", type=int)
    tags = request.form.get("tags")
    category_id = request.form.get("category_id", type=int)
    description = request.form.get("description")
    notes = request.form.get("notes")

    uc = _get_doc_use_cases()
    result = uc.upload_document(
        company_id=company_id,
        file=file,
        title=title,
        document_type=document_type,
        reference_type=reference_type,
        reference_id=reference_id,
        uploaded_by=uploaded_by,
        tags=tags,
        category_id=category_id,
        description=description,
        notes=notes,
    )
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400
    return jsonify(result.get_data()), 201


@document_bp.route("/api/v1/documents/<int:id>/upload-version", methods=["POST"])
def upload_document_version(id: int):
    if "file" not in request.files:
        return jsonify({"error": resolve_error(ErrorCodes.DOCUMENT_FILE_REQUIRED)}), 400
    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": resolve_error(ErrorCodes.DOCUMENT_FILE_REQUIRED)}), 400

    change_notes = request.form.get("change_notes")
    uploaded_by = request.form.get("uploaded_by", type=int)

    uc = _get_doc_use_cases()
    result = uc.upload_new_version(
        document_id=id,
        file=file,
        change_notes=change_notes,
        uploaded_by=uploaded_by,
    )
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400
    return jsonify(result.get_data()), 201


@document_bp.route("/api/v1/documents/<int:id>", methods=["GET"])
def get_document(id: int):
    uc = _get_doc_use_cases()
    result = uc.get_document(id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify(result.get_data()), 200


@document_bp.route("/api/v1/documents/<int:id>/download", methods=["GET"])
def download_document(id: int):
    uc = _get_doc_use_cases()
    result = uc.get_document_file_path(id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    info = result.get_data()
    if not os.path.exists(info["file_path"]):
        return jsonify({"error": resolve_error(ErrorCodes.FILE_NOT_FOUND)}), 404
    return send_file(
        info["file_path"],
        mimetype=info["mime_type"],
        as_attachment=True,
        download_name=info["file_name"],
    )


@document_bp.route("/api/v1/documents", methods=["GET"])
def list_documents():
    company_id = request.args.get("company_id", type=int, default=1)
    document_type = request.args.get("document_type")
    status = request.args.get("status")
    reference_type = request.args.get("reference_type")
    reference_id = request.args.get("reference_id", type=int)
    search = request.args.get("search")
    page = request.args.get("page", type=int, default=1)
    per_page = min(request.args.get("per_page", type=int, default=20), 100)

    uc = _get_doc_use_cases()
    result = uc.list_documents(
        company_id=company_id,
        document_type=document_type,
        status=status,
        reference_type=reference_type,
        reference_id=reference_id,
        search=search,
        page=page,
        per_page=per_page,
    )
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@document_bp.route("/api/v1/documents/<int:id>", methods=["PUT"])
def update_document(id: int):
    data = request.get_json(silent=True) or {}
    uc = _get_doc_use_cases()
    result = uc.update_document(id, data)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.DOCUMENT_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Document updated"}), 200


@document_bp.route("/api/v1/documents/<int:id>", methods=["DELETE"])
def delete_document(id: int):
    uc = _get_doc_use_cases()
    result = uc.delete_document(id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify({"message": "Document deleted"}), 200


@document_bp.route("/api/v1/documents/<int:id>/archive", methods=["POST"])
def archive_document(id: int):
    uc = _get_doc_use_cases()
    result = uc.archive_document(id)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.DOCUMENT_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Document archived"}), 200


@document_bp.route("/api/v1/documents/entity/<entity_type>/<int:entity_id>", methods=["GET"])
def get_documents_for_entity(entity_type: str, entity_id: int):
    uc = _get_doc_use_cases()
    result = uc.get_documents_for_entity(entity_type, entity_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify({"documents": result.get_data()}), 200


@document_bp.route("/api/v1/documents/<int:id>/versions", methods=["GET"])
def get_document_versions(id: int):
    uc = _get_doc_use_cases()
    result = uc.get_document_versions(id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify({"versions": result.get_data()}), 200


# ── Categories ─────────────────────────────────────────────────────────

@document_bp.route("/api/v1/document-categories", methods=["GET"])
def list_categories():
    active_only = request.args.get("active_only", "false").lower() == "true"
    uc = _get_doc_use_cases()
    result = uc.list_categories(active_only)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify({"categories": result.get_data()}), 200


@document_bp.route("/api/v1/document-categories/<int:id>", methods=["GET"])
def get_category(id: int):
    uc = _get_doc_use_cases()
    result = uc.get_category(id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify(result.get_data()), 200


@document_bp.route("/api/v1/document-categories", methods=["POST"])
def create_category():
    data = request.get_json(silent=True) or {}
    try:
        cat = DocumentCategory(
            name=data.get("name", ""),
            code=data.get("code", ""),
            description=data.get("description"),
            parent_id=data.get("parent_id"),
            is_active=data.get("is_active", True),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_doc_use_cases()
    result = uc.create_category(cat)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 409
    return jsonify(result.get_data()), 201


@document_bp.route("/api/v1/document-categories/<int:id>", methods=["PUT"])
def update_category(id: int):
    data = request.get_json(silent=True) or {}
    uc = _get_doc_use_cases()
    result = uc.update_category(id, data)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Category updated"}), 200


@document_bp.route("/api/v1/document-categories/<int:id>", methods=["DELETE"])
def delete_category(id: int):
    uc = _get_doc_use_cases()
    result = uc.delete_category(id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify({"message": "Category deleted"}), 200
