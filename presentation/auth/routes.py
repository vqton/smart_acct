import functools
import os
from datetime import datetime, timezone
from typing import Optional

from flask import g, jsonify, request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from domain.auth import (
    UserCreate, UserUpdate, Role, Permission, LoginRequest, ChangePasswordRequest,
)
from domain.common import VASValidationError, Result
from domain.i18n import ErrorCodes
from infrastructure.auth import (
    BcryptPasswordService, JWTService, CasbinEnforcerService, AuditService,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from presentation import resolve_error
from presentation.auth import auth_bp

# ── Helpers ────────────────────────────────────────────────────────────


def _get_jwt_service() -> JWTService:
    return current_app.auth_jwt_service


def _get_casbin() -> CasbinEnforcerService:
    return current_app.auth_casbin_service


def _get_audit() -> AuditService:
    return current_app.auth_audit_service


def _get_auth_use_cases():
    from use_cases.auth import AuthUseCases
    return AuthUseCases(
        session_factory=current_app.db_manager.get_session,
        jwt_service=_get_jwt_service(),
        casbin_service=_get_casbin(),
        audit_service=_get_audit(),
    )


def _get_current_user() -> Optional[dict]:
    """Extract current user from JWT in Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        import jwt
        token = auth[7:]
        secret = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret"))
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except Exception:
        return None


def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        user = _get_current_user()
        if not user:
            return jsonify({"error": resolve_error(ErrorCodes.AUTH_UNAUTHORIZED)}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def permission_required(resource: str, action: str):
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            username = g.current_user.get("username")
            if g.current_user.get("is_superuser"):
                return f(*args, **kwargs)
            if not _get_casbin().enforce(username, resource, action):
                return jsonify({
                    "error": resolve_error(ErrorCodes.AUTH_INSUFFICIENT_PERMISSIONS)
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── UC-AUTH-01: Login ─────────────────────────────────────────────────


@auth_bp.route("/api/v1/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    try:
        req = LoginRequest(
            username=data.get("username", ""),
            password=data.get("password", ""),
            remember_me=data.get("remember_me", False),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_auth_use_cases()
    result = uc.login(req, ip=request.remote_addr, user_agent=request.user_agent.string if request.user_agent else None)
    if result.is_failure():
        err = result.get_error()
        code = 403 if err.msgid in (ErrorCodes.AUTH_ACCOUNT_DISABLED, ErrorCodes.AUTH_ACCOUNT_LOCKED) else 401
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code

    return jsonify(result.get_data()), 200


# ── UC-AUTH-02: Logout ────────────────────────────────────────────────


@auth_bp.route("/api/v1/auth/logout", methods=["POST"])
@login_required
def logout():
    data = request.get_json(silent=True) or {}
    user_id = int(g.current_user["sub"])
    uc = _get_auth_use_cases()
    result = uc.logout(
        user_id,
        refresh_token=data.get("refresh_token"),
        ip=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify({"message": "Logged out"}), 200


# ── UC-AUTH-03: Token Refresh ─────────────────────────────────────────


@auth_bp.route("/api/v1/auth/refresh", methods=["POST"])
def refresh_token():
    data = request.get_json(silent=True) or {}
    refresh_token_str = data.get("refresh_token", "")
    if not refresh_token_str:
        return jsonify({"error": resolve_error(ErrorCodes.AUTH_REFRESH_TOKEN_INVALID)}), 401

    uc = _get_auth_use_cases()
    result = uc.refresh_token(
        refresh_token_str,
        ip=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 401
    return jsonify(result.get_data()), 200


# ── UC-AUTH-04: Change Password ───────────────────────────────────────


@auth_bp.route("/api/v1/auth/change-password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    try:
        req = ChangePasswordRequest(
            current_password=data.get("current_password", ""),
            new_password=data.get("new_password", ""),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    user_id = int(g.current_user["sub"])
    uc = _get_auth_use_cases()
    result = uc.change_password(
        user_id, req,
        ip=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 400
    return jsonify({"message": "Password changed"}), 200


# ── UC-AUTH-05: User CRUD ─────────────────────────────────────────────


@auth_bp.route("/api/v1/auth/users", methods=["GET"])
@permission_required("users", "list")
def list_users():
    offset = request.args.get("offset", 0, type=int)
    limit = min(request.args.get("limit", 50, type=int), 200)
    active_only = request.args.get("active_only", "false").lower() == "true"
    uc = _get_auth_use_cases()
    result = uc.list_users(offset, limit, active_only)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@auth_bp.route("/api/v1/auth/users/<int:user_id>", methods=["GET"])
@permission_required("users", "read")
def get_user(user_id: int):
    uc = _get_auth_use_cases()
    result = uc.get_user(user_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify(result.get_data()), 200


@auth_bp.route("/api/v1/auth/users", methods=["POST"])
@permission_required("users", "create")
def create_user():
    data = request.get_json(silent=True) or {}
    try:
        user_data = UserCreate(
            username=data.get("username", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            full_name=data.get("full_name", ""),
            position=data.get("position"),
            department=data.get("department"),
            phone=data.get("phone"),
            role_ids=data.get("role_ids", []),
            locale=data.get("locale", "vi"),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_auth_use_cases()
    result = uc.create_user(
        user_data,
        ip=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )
    if result.is_failure():
        err = result.get_error()
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), 409
    user = result.get_data()
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }), 201


@auth_bp.route("/api/v1/auth/users/<int:user_id>", methods=["PUT"])
@permission_required("users", "update")
def update_user(user_id: int):
    data = request.get_json(silent=True) or {}
    try:
        updates = UserUpdate(
            full_name=data.get("full_name"),
            position=data.get("position"),
            department=data.get("department"),
            phone=data.get("phone"),
            locale=data.get("locale"),
            is_active=data.get("is_active"),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_auth_use_cases()
    result = uc.update_user(
        user_id, updates,
        ip=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.AUTH_USER_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code

    updated = result.get_data()
    return jsonify({
        "id": updated.id,
        "username": updated.username,
        "email": updated.email,
        "full_name": updated.full_name,
        "is_active": updated.is_active,
    }), 200


@auth_bp.route("/api/v1/auth/users/<int:user_id>", methods=["DELETE"])
@permission_required("users", "delete")
def delete_user(user_id: int):
    # Prevent self-deletion
    g_user_id = int(g.current_user["sub"])
    if g_user_id == user_id:
        return jsonify({"error": "Cannot delete yourself"}), 400

    uc = _get_auth_use_cases()
    result = uc.delete_user(
        user_id,
        ip=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.AUTH_USER_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "User deleted"}), 200


# ── UC-AUTH-06: Role CRUD ─────────────────────────────────────────────


@auth_bp.route("/api/v1/auth/roles", methods=["GET"])
@permission_required("roles", "list")
def list_roles():
    offset = request.args.get("offset", 0, type=int)
    limit = min(request.args.get("limit", 50, type=int), 200)
    uc = _get_auth_use_cases()
    result = uc.list_roles(offset, limit)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@auth_bp.route("/api/v1/auth/roles/<int:role_id>", methods=["GET"])
@permission_required("roles", "read")
def get_role(role_id: int):
    uc = _get_auth_use_cases()
    result = uc.get_role(role_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify(result.get_data()), 200


@auth_bp.route("/api/v1/auth/roles", methods=["POST"])
@permission_required("roles", "create")
def create_role():
    data = request.get_json(silent=True) or {}
    try:
        role = Role(
            name=data.get("name", ""),
            display_name=data.get("display_name", ""),
            description=data.get("description"),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_auth_use_cases()
    result = uc.create_role(role)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 409
    r = result.get_data()
    return jsonify({"id": r.id, "name": r.name, "display_name": r.display_name}), 201


@auth_bp.route("/api/v1/auth/roles/<int:role_id>", methods=["PUT"])
@permission_required("roles", "update")
def update_role(role_id: int):
    data = request.get_json(silent=True) or {}
    uc = _get_auth_use_cases()
    result = uc.update_role(
        role_id,
        name=data.get("name"),
        display_name=data.get("display_name"),
        description=data.get("description"),
    )
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.AUTH_ROLE_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Role updated"}), 200


@auth_bp.route("/api/v1/auth/roles/<int:role_id>", methods=["DELETE"])
@permission_required("roles", "delete")
def delete_role(role_id: int):
    uc = _get_auth_use_cases()
    result = uc.delete_role(role_id)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.AUTH_ROLE_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Role deleted"}), 200


# ── UC-AUTH-07: User Role Assignment ──────────────────────────────────


@auth_bp.route("/api/v1/auth/users/<int:user_id>/roles", methods=["PUT"])
@permission_required("users", "update")
def set_user_roles(user_id: int):
    data = request.get_json(silent=True) or {}
    role_ids = data.get("role_ids", [])
    uc = _get_auth_use_cases()
    result = uc.set_user_roles(user_id, role_ids)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid in (ErrorCodes.AUTH_USER_NOT_FOUND, ErrorCodes.AUTH_ROLE_NOT_FOUND) else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Roles updated"}), 200


@auth_bp.route("/api/v1/auth/users/<int:user_id>/roles", methods=["GET"])
@permission_required("users", "read")
def get_user_roles(user_id: int):
    from infrastructure.repositories.auth_repository import UserRepository
    from domain.auth import AuthEventType
    session = current_app.db_manager.get_session()
    try:
        repo = UserRepository(session)
        roles = repo.get_user_roles(user_id)
        return jsonify([{"id": r.id, "name": r.name, "display_name": r.display_name}
                        for r in roles]), 200
    finally:
        session.close()


# ── UC-AUTH-08: Permission CRUD ───────────────────────────────────────


@auth_bp.route("/api/v1/auth/permissions", methods=["GET"])
@permission_required("permissions", "list")
def list_permissions():
    offset = request.args.get("offset", 0, type=int)
    limit = min(request.args.get("limit", 100, type=int), 500)
    uc = _get_auth_use_cases()
    result = uc.list_permissions(offset, limit)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


@auth_bp.route("/api/v1/auth/permissions", methods=["POST"])
@permission_required("permissions", "create")
def create_permission():
    data = request.get_json(silent=True) or {}
    try:
        permission = Permission(
            resource=data.get("resource", ""),
            action=data.get("action", ""),
            description=data.get("description"),
        )
    except VASValidationError as e:
        return jsonify({"error": resolve_error(e.msgid, **e.params)}), 400

    uc = _get_auth_use_cases()
    result = uc.create_permission(permission)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 409
    p = result.get_data()
    return jsonify({"id": p.id, "resource": p.resource, "action": p.action}), 201


@auth_bp.route("/api/v1/auth/permissions/<int:perm_id>", methods=["DELETE"])
@permission_required("permissions", "delete")
def delete_permission(perm_id: int):
    uc = _get_auth_use_cases()
    result = uc.delete_permission(perm_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify({"message": "Permission deleted"}), 200


# ── UC-AUTH-09: Role-Permission Assignment ────────────────────────────


@auth_bp.route("/api/v1/auth/roles/<int:role_id>/permissions", methods=["PUT"])
@permission_required("roles", "update")
def set_role_permissions(role_id: int):
    data = request.get_json(silent=True) or {}
    permission_ids = data.get("permission_ids", [])
    uc = _get_auth_use_cases()
    result = uc.set_role_permissions(role_id, permission_ids)
    if result.is_failure():
        err = result.get_error()
        code = 404 if err.msgid == ErrorCodes.AUTH_ROLE_NOT_FOUND else 400
        return jsonify({"error": resolve_error(err.msgid, **err.params)}), code
    return jsonify({"message": "Permissions updated"}), 200


@auth_bp.route("/api/v1/auth/roles/<int:role_id>/permissions", methods=["GET"])
@permission_required("roles", "read")
def get_role_permissions(role_id: int):
    from infrastructure.repositories.auth_repository import RoleRepository
    session = current_app.db_manager.get_session()
    try:
        repo = RoleRepository(session)
        perms = repo.get_role_permissions(role_id)
        return jsonify([{"id": p.id, "resource": p.resource, "action": p.action,
                         "description": p.description} for p in perms]), 200
    finally:
        session.close()


# ── UC-AUTH-10: Check Permission ──────────────────────────────────────


@auth_bp.route("/api/v1/auth/check-permission", methods=["POST"])
@login_required
def check_permission():
    data = request.get_json(silent=True) or {}
    resource = data.get("resource", "")
    action = data.get("action", "")
    username = g.current_user.get("username")
    allowed = _get_casbin().enforce(username, resource, action)
    return jsonify({"allowed": allowed}), 200


@auth_bp.route("/api/v1/auth/my-permissions", methods=["GET"])
@login_required
def my_permissions():
    username = g.current_user.get("username")
    perms = _get_casbin().get_permissions_for_user(username)
    return jsonify({
        "permissions": [{"resource": p[1], "action": p[2]} for p in perms]
    }), 200


# ── UC-AUTH-11: Session Management ────────────────────────────────────


@auth_bp.route("/api/v1/auth/sessions", methods=["GET"])
@login_required
def get_my_sessions():
    user_id = int(g.current_user["sub"])
    uc = _get_auth_use_cases()
    result = uc.get_active_sessions(user_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify({"sessions": result.get_data()}), 200


@auth_bp.route("/api/v1/auth/sessions/<int:session_id>", methods=["DELETE"])
@login_required
def revoke_session(session_id: int):
    user_id = int(g.current_user["sub"])
    uc = _get_auth_use_cases()
    result = uc.revoke_session(session_id, user_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify({"message": "Session revoked"}), 200


@auth_bp.route("/api/v1/auth/sessions", methods=["DELETE"])
@login_required
def revoke_all_sessions():
    user_id = int(g.current_user["sub"])
    uc = _get_auth_use_cases()
    result = uc.revoke_all_sessions(user_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify({"message": "All other sessions revoked"}), 200


# ── UC-AUTH-12: Audit Log ─────────────────────────────────────────────


@auth_bp.route("/api/v1/auth/audit-log", methods=["GET"])
@permission_required("audit", "read")
def get_audit_logs():
    offset = request.args.get("offset", 0, type=int)
    limit = min(request.args.get("limit", 50, type=int), 200)
    event_type = request.args.get("event_type")
    uc = _get_auth_use_cases()
    result = uc.get_audit_logs(offset, limit, event_type)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 500
    return jsonify(result.get_data()), 200


# ── Me Endpoint ───────────────────────────────────────────────────────


@auth_bp.route("/api/v1/auth/me", methods=["GET"])
@login_required
def me():
    user_id = int(g.current_user["sub"])
    uc = _get_auth_use_cases()
    result = uc.get_user(user_id)
    if result.is_failure():
        return jsonify({"error": resolve_error(result.get_error().msgid)}), 404
    return jsonify(result.get_data()), 200
