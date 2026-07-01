from flask import Blueprint

auth_bp = Blueprint("auth", __name__, template_folder="../../templates/auth")

from presentation.auth import routes


def serialize_user(user_data: dict) -> dict:
    return {
        "id": user_data.get("id"),
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "full_name": user_data.get("full_name"),
        "position": user_data.get("position"),
        "department": user_data.get("department"),
        "phone": user_data.get("phone"),
        "is_active": user_data.get("is_active", True),
        "is_superuser": user_data.get("is_superuser", False),
        "must_change_password": user_data.get("must_change_password", False),
        "locale": user_data.get("locale", "vi"),
        "roles": user_data.get("roles", []),
        "last_login": user_data.get("last_login"),
        "created_at": user_data.get("created_at"),
    }


def serialize_role(role: dict) -> dict:
    return {
        "id": role.get("id"),
        "name": role.get("name"),
        "display_name": role.get("display_name"),
        "description": role.get("description"),
        "is_system": role.get("is_system", False),
        "permissions": role.get("permissions", []),
    }


def serialize_permission(perm: dict) -> dict:
    return {
        "id": perm.get("id"),
        "resource": perm.get("resource"),
        "action": perm.get("action"),
        "description": perm.get("description"),
    }
