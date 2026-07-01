from decimal import Decimal
from datetime import date

from flask import g, jsonify, request, current_app

from domain.common import VASValidationError
from domain.i18n import ErrorCodes
from presentation import resolve_error
from presentation.approval import approval_bp


def _get_approval_use_cases():
    from use_cases.approval import ApprovalUseCases
    return ApprovalUseCases(
        session_factory=current_app.db_manager.get_session,
    )


def _get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        import jwt
        import os
        token = auth[7:]
        secret = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret"))
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except Exception:
        return None


def login_required(f):
    import functools
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        user = _get_current_user()
        if not user:
            return jsonify({"error": resolve_error(ErrorCodes.AUTH_UNAUTHORIZED)}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


# ── Workflow CRUD ────────────────────────────────────────────────


@approval_bp.route("/api/v1/approval/workflows", methods=["POST"])
@login_required
def create_workflow():
    data = request.get_json(silent=True) or {}
    try:
        name = data.get("name", "")
        if not name.strip():
            return jsonify({"error": resolve_error(ErrorCodes.APPROVAL_NAME_EMPTY)}), 400
        uc = _get_approval_use_cases()
        result = uc.create_workflow(
            name=name,
            object_type=data.get("object_type", ""),
            strategy=data.get("strategy", "sequential"),
            description=data.get("description"),
            quorum_percentage=Decimal(str(data["quorum_percentage"])) if data.get("quorum_percentage") is not None else None,
            steps=data.get("steps", []),
        )
        if result.is_failure():
            err = result.get_error()
            return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400
        return jsonify(result.get_data()), 201
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400


@approval_bp.route("/api/v1/approval/workflows", methods=["GET"])
@login_required
def list_workflows():
    object_type = request.args.get("object_type")
    uc = _get_approval_use_cases()
    result = uc.list_workflows(object_type)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@approval_bp.route("/api/v1/approval/workflows/<int:workflow_id>", methods=["GET"])
@login_required
def get_workflow(workflow_id: int):
    uc = _get_approval_use_cases()
    result = uc.get_workflow(workflow_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify(result.get_data()), 200


@approval_bp.route("/api/v1/approval/workflows/<int:workflow_id>", methods=["PUT"])
@login_required
def update_workflow(workflow_id: int):
    data = request.get_json(silent=True) or {}
    if "quorum_percentage" in data and data["quorum_percentage"] is not None:
        data["quorum_percentage"] = Decimal(str(data["quorum_percentage"]))
    uc = _get_approval_use_cases()
    result = uc.update_workflow(workflow_id, data)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify(result.get_data()), 200


@approval_bp.route("/api/v1/approval/workflows/<int:workflow_id>", methods=["DELETE"])
@login_required
def delete_workflow(workflow_id: int):
    uc = _get_approval_use_cases()
    result = uc.delete_workflow(workflow_id)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.APPROVAL_WORKFLOW_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Workflow deactivated"}), 200


# ── Requests ──────────────────────────────────────────────────────


@approval_bp.route("/api/v1/approval/requests", methods=["POST"])
@login_required
def submit_request():
    data = request.get_json(silent=True) or {}
    user_id = int(g.current_user["sub"])
    amount = None
    if data.get("amount") is not None:
        amount = Decimal(str(data["amount"]))
    uc = _get_approval_use_cases()
    result = uc.submit_request(
        user_id=user_id,
        object_type=data.get("object_type", ""),
        object_id=data.get("object_id", 0),
        object_reference=data.get("object_reference"),
        amount=amount,
    )
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400
    return jsonify(result.get_data()), 201


@approval_bp.route("/api/v1/approval/requests/pending", methods=["GET"])
@login_required
def get_pending_approvals():
    user_id = int(g.current_user["sub"])
    object_type = request.args.get("object_type")
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    uc = _get_approval_use_cases()
    result = uc.get_pending_approvals(user_id, object_type, page, per_page)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@approval_bp.route("/api/v1/approval/requests/my", methods=["GET"])
@login_required
def get_my_submissions():
    user_id = int(g.current_user["sub"])
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    uc = _get_approval_use_cases()
    result = uc.get_my_submissions(user_id, status, page, per_page)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@approval_bp.route("/api/v1/approval/requests/<int:request_id>", methods=["GET"])
@login_required
def get_request(request_id: int):
    uc = _get_approval_use_cases()
    result = uc.get_request_detail(request_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify(result.get_data()), 200


@approval_bp.route("/api/v1/approval/requests/<int:request_id>/approve", methods=["POST"])
@login_required
def approve_request(request_id: int):
    data = request.get_json(silent=True) or {}
    user_id = int(g.current_user["sub"])
    uc = _get_approval_use_cases()
    result = uc.approve_step(
        request_id=request_id,
        approver_id=user_id,
        comments=data.get("comments"),
    )
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400
    return jsonify(result.get_data()), 200


@approval_bp.route("/api/v1/approval/requests/<int:request_id>/reject", methods=["POST"])
@login_required
def reject_request(request_id: int):
    data = request.get_json(silent=True) or {}
    user_id = int(g.current_user["sub"])
    uc = _get_approval_use_cases()
    result = uc.reject_step(
        request_id=request_id,
        approver_id=user_id,
        comments=data.get("comments"),
    )
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400
    return jsonify(result.get_data()), 200


@approval_bp.route("/api/v1/approval/requests/<int:request_id>/cancel", methods=["POST"])
@login_required
def cancel_request(request_id: int):
    user_id = int(g.current_user["sub"])
    uc = _get_approval_use_cases()
    result = uc.cancel_request(request_id, user_id)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid in (ErrorCodes.APPROVAL_REQUEST_NOT_FOUND,) else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Request cancelled"}), 200


# ── Status ─────────────────────────────────────────────────────────


@approval_bp.route("/api/v1/approval/status", methods=["GET"])
@login_required
def get_approval_status():
    object_type = request.args.get("object_type", "")
    object_id = request.args.get("object_id", 0, type=int)
    if not object_type or not object_id:
        return jsonify({"error": resolve_error(ErrorCodes.QUERY_PARAM_REQUIRED)}), 400
    uc = _get_approval_use_cases()
    result = uc.get_object_approval_status(object_type, object_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


# ── Delegations ─────────────────────────────────────────────────────


@approval_bp.route("/api/v1/approval/delegations", methods=["POST"])
@login_required
def set_delegation():
    data = request.get_json(silent=True) or {}
    user_id = int(g.current_user["sub"])
    start = None
    if data.get("start_date"):
        start = date.fromisoformat(data["start_date"])
    end = None
    if data.get("end_date"):
        end = date.fromisoformat(data["end_date"])
    uc = _get_approval_use_cases()
    result = uc.set_delegation(
        user_id=user_id,
        delegate_to=data.get("delegate_to", 0),
        object_type=data.get("object_type"),
        start_date=start,
        end_date=end,
    )
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400
    return jsonify(result.get_data()), 201


@approval_bp.route("/api/v1/approval/delegations", methods=["GET"])
@login_required
def get_delegations():
    user_id = int(g.current_user["sub"])
    uc = _get_approval_use_cases()
    result = uc.get_delegations(user_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200
