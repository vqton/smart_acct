import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from domain.auth import (
    User, UserCreate, UserUpdate, Role, Permission, UserSession,
    PasswordResetToken, AuthAuditLog, AuthEventType,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result
from infrastructure.models.auth_models import (
    UserModel, RoleModel, UserRoleModel, PermissionModel, RolePermissionModel,
    UserSessionModel, PasswordResetTokenModel, AuthAuditLogModel,
    AuthEventTypeDB,
)

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: UserCreate, password_hash: str) -> Result:
        existing = self.session.query(UserModel).filter(
            or_(UserModel.username == user.username, UserModel.email == user.email)
        ).first()
        if existing:
            if existing.username == user.username:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_USERNAME_EXISTS))
            return Result.failure(VASValidationError(ErrorCodes.AUTH_EMAIL_EXISTS))
        model = UserModel(
            username=user.username,
            email=user.email,
            password_hash=password_hash,
            full_name=user.full_name,
            position=user.position,
            department=user.department,
            phone=user.phone,
            locale=user.locale or "vi",
        )
        self.session.add(model)
        self.session.flush()
        if user.role_ids:
            roles = self.session.query(RoleModel).filter(RoleModel.id.in_(user.role_ids)).all()
            if len(roles) != len(user.role_ids):
                return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_NOT_FOUND))
            for role in roles:
                self.session.add(UserRoleModel(user_id=model.id, role_id=role.id))
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def get_by_id(self, user_id: int) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        return self._model_to_domain(model) if model else None

    def get_by_username(self, username: str) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.username == username).first()
        return self._model_to_domain(model) if model else None

    def get_by_email(self, email: str) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.email == email).first()
        return self._model_to_domain(model) if model else None

    def list(self, offset: int = 0, limit: int = 50, active_only: bool = False) -> List[User]:
        query = self.session.query(UserModel)
        if active_only:
            query = query.filter(UserModel.is_active.is_(True))
        models = query.order_by(UserModel.id).offset(offset).limit(limit).all()
        return [self._model_to_domain(m) for m in models]

    def count(self, active_only: bool = False) -> int:
        query = self.session.query(UserModel)
        if active_only:
            query = query.filter(UserModel.is_active.is_(True))
        return query.count()

    def update(self, user_id: int, updates: UserUpdate) -> Result:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_USER_NOT_FOUND))
        update_data = updates.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(model, key, value)
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def update_password(self, user_id: int, password_hash: str) -> None:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            model.password_hash = password_hash
            model.must_change_password = False
            model.updated_at = datetime.now(timezone.utc)
            self.session.flush()

    def record_login_success(self, user_id: int) -> None:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            model.failed_login_attempts = 0
            model.locked_until = None
            model.last_login = datetime.now(timezone.utc)
            model.updated_at = datetime.now(timezone.utc)
            self.session.flush()

    def record_login_failure(self, username: str) -> Optional[int]:
        model = self.session.query(UserModel).filter(UserModel.username == username).first()
        if not model:
            return None
        model.failed_login_attempts = (model.failed_login_attempts or 0) + 1
        model.updated_at = datetime.now(timezone.utc)
        if model.failed_login_attempts >= 5:
            from infrastructure.auth import ACCOUNT_LOCKOUT_MINUTES
            model.locked_until = datetime.now(timezone.utc) + timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES)
        self.session.flush()
        return model.id

    def lock_account(self, user_id: int, minutes: int = 30) -> None:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            from datetime import timedelta
            model.locked_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            model.updated_at = datetime.now(timezone.utc)
            self.session.flush()

    def unlock_account(self, user_id: int) -> None:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            model.failed_login_attempts = 0
            model.locked_until = None
            model.updated_at = datetime.now(timezone.utc)
            self.session.flush()

    def get_user_roles(self, user_id: int) -> List[Role]:
        models = (
            self.session.query(RoleModel)
            .join(UserRoleModel)
            .filter(UserRoleModel.user_id == user_id)
            .all()
        )
        return [Role(id=m.id, name=m.name, display_name=m.display_name,
                     description=m.description, is_system=m.is_system) for m in models]

    def set_user_roles(self, user_id: int, role_ids: List[int]) -> Result:
        user = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_USER_NOT_FOUND))
        roles = self.session.query(RoleModel).filter(RoleModel.id.in_(role_ids)).all()
        if len(roles) != len(set(role_ids)):
            return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_NOT_FOUND))
        self.session.query(UserRoleModel).filter(UserRoleModel.user_id == user_id).delete()
        for rid in role_ids:
            self.session.add(UserRoleModel(user_id=user_id, role_id=rid))
        self.session.flush()
        return Result.success(None)

    def delete(self, user_id: int) -> Result:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_USER_NOT_FOUND))
        if model.is_superuser:
            count = self.session.query(UserModel).filter(UserModel.is_superuser.is_(True)).count()
            if count <= 1:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_CANNOT_DELETE_LAST_SUPERUSER))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    def _model_to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            position=model.position,
            department=model.department,
            phone=model.phone,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            must_change_password=model.must_change_password,
            locale=model.locale,
            failed_login_attempts=model.failed_login_attempts,
            locked_until=model.locked_until,
            last_login=model.last_login,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class RoleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, role: Role) -> Result:
        existing = self.session.query(RoleModel).filter(RoleModel.name == role.name).first()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_EXISTS))
        model = RoleModel(
            name=role.name,
            display_name=role.display_name,
            description=role.description,
            is_system=role.is_system,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def get_by_id(self, role_id: int) -> Optional[Role]:
        model = self.session.query(RoleModel).filter(RoleModel.id == role_id).first()
        return self._model_to_domain(model) if model else None

    def get_by_name(self, name: str) -> Optional[Role]:
        model = self.session.query(RoleModel).filter(RoleModel.name == name).first()
        return self._model_to_domain(model) if model else None

    def list(self, offset: int = 0, limit: int = 50) -> List[Role]:
        models = self.session.query(RoleModel).order_by(RoleModel.id).offset(offset).limit(limit).all()
        return [self._model_to_domain(m) for m in models]

    def count(self) -> int:
        return self.session.query(RoleModel).count()

    def update(self, role_id: int, name: Optional[str] = None,
               display_name: Optional[str] = None,
               description: Optional[str] = None) -> Result:
        model = self.session.query(RoleModel).filter(RoleModel.id == role_id).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_NOT_FOUND))
        if model.is_system:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_CANNOT_MODIFY_SYSTEM_ROLE))
        if name is not None:
            model.name = name
        if display_name is not None:
            model.display_name = display_name
        if description is not None:
            model.description = description
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def delete(self, role_id: int) -> Result:
        model = self.session.query(RoleModel).filter(RoleModel.id == role_id).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_NOT_FOUND))
        if model.is_system:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_CANNOT_MODIFY_SYSTEM_ROLE))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    def get_role_permissions(self, role_id: int) -> List[Permission]:
        models = (
            self.session.query(PermissionModel)
            .join(RolePermissionModel)
            .filter(RolePermissionModel.role_id == role_id)
            .all()
        )
        return [Permission(id=m.id, resource=m.resource, action=m.action,
                          description=m.description) for m in models]

    def set_role_permissions(self, role_id: int, permission_ids: List[int]) -> Result:
        role = self.session.query(RoleModel).filter(RoleModel.id == role_id).first()
        if not role:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_NOT_FOUND))
        if role.is_system:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_CANNOT_MODIFY_SYSTEM_ROLE))
        perms = self.session.query(PermissionModel).filter(PermissionModel.id.in_(permission_ids)).all()
        if len(perms) != len(set(permission_ids)):
            return Result.failure(VASValidationError(ErrorCodes.AUTH_PERMISSION_NOT_FOUND))
        self.session.query(RolePermissionModel).filter(RolePermissionModel.role_id == role_id).delete()
        for pid in permission_ids:
            self.session.add(RolePermissionModel(role_id=role_id, permission_id=pid))
        self.session.flush()
        return Result.success(None)

    def _model_to_domain(self, model: RoleModel) -> Role:
        return Role(
            id=model.id,
            name=model.name,
            display_name=model.display_name,
            description=model.description,
            is_system=model.is_system,
            created_at=model.created_at,
        )


class PermissionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, permission: Permission) -> Result:
        existing = self.session.query(PermissionModel).filter(
            and_(PermissionModel.resource == permission.resource,
                 PermissionModel.action == permission.action)
        ).first()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_PERMISSION_EXISTS))
        model = PermissionModel(
            resource=permission.resource,
            action=permission.action,
            description=permission.description,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def get_by_id(self, perm_id: int) -> Optional[Permission]:
        model = self.session.query(PermissionModel).filter(PermissionModel.id == perm_id).first()
        return self._model_to_domain(model) if model else None

    def list(self, offset: int = 0, limit: int = 100) -> List[Permission]:
        models = self.session.query(PermissionModel).order_by(PermissionModel.resource, PermissionModel.action).offset(offset).limit(limit).all()
        return [self._model_to_domain(m) for m in models]

    def count(self) -> int:
        return self.session.query(PermissionModel).count()

    def delete(self, perm_id: int) -> Result:
        model = self.session.query(PermissionModel).filter(PermissionModel.id == perm_id).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.AUTH_PERMISSION_NOT_FOUND))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    def _model_to_domain(self, model: PermissionModel) -> Permission:
        return Permission(
            id=model.id,
            resource=model.resource,
            action=model.action,
            description=model.description,
        )


class SessionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, session_entry: UserSession) -> UserSession:
        model = UserSessionModel(
            user_id=session_entry.user_id,
            refresh_token_hash=session_entry.refresh_token_hash,
            device_info=session_entry.device_info,
            ip_address=session_entry.ip_address,
            expires_at=session_entry.expires_at,
        )
        self.session.add(model)
        self.session.flush()
        session_entry.id = model.id
        return session_entry

    def find_by_refresh_hash(self, token_hash: str) -> Optional[UserSessionModel]:
        return self.session.query(UserSessionModel).filter(
            UserSessionModel.refresh_token_hash == token_hash,
            UserSessionModel.revoked.is_(False),
        ).first()

    def find_active_by_user_id(self, user_id: int) -> List[UserSessionModel]:
        now = datetime.now(timezone.utc)
        return self.session.query(UserSessionModel).filter(
            UserSessionModel.user_id == user_id,
            UserSessionModel.revoked.is_(False),
            UserSessionModel.expires_at > now,
        ).all()

    def revoke(self, session_id: int) -> None:
        model = self.session.query(UserSessionModel).filter(UserSessionModel.id == session_id).first()
        if model:
            model.revoked = True
            self.session.flush()

    def revoke_all_for_user(self, user_id: int) -> None:
        self.session.query(UserSessionModel).filter(
            UserSessionModel.user_id == user_id,
            UserSessionModel.revoked.is_(False),
        ).update({"revoked": True})
        self.session.flush()

    def cleanup_expired(self) -> int:
        now = datetime.now(timezone.utc)
        count = self.session.query(UserSessionModel).filter(
            UserSessionModel.expires_at <= now
        ).delete()
        self.session.flush()
        return count


class PasswordResetTokenRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, token: PasswordResetToken) -> PasswordResetToken:
        model = PasswordResetTokenModel(
            user_id=token.user_id,
            token_hash=token.token_hash,
            expires_at=token.expires_at,
        )
        self.session.add(model)
        self.session.flush()
        token.id = model.id
        return token

    def find_valid(self, token_hash: str) -> Optional[PasswordResetTokenModel]:
        now = datetime.now(timezone.utc)
        return self.session.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.token_hash == token_hash,
            PasswordResetTokenModel.used.is_(False),
            PasswordResetTokenModel.expires_at > now,
        ).first()

    def mark_used(self, token_id: int) -> None:
        model = self.session.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.id == token_id
        ).first()
        if model:
            model.used = True
            self.session.flush()

    def invalidate_all_for_user(self, user_id: int) -> None:
        self.session.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.user_id == user_id,
            PasswordResetTokenModel.used.is_(False),
        ).update({"used": True})
        self.session.flush()


from datetime import timedelta
