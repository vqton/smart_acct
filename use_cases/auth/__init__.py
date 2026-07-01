import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from domain.auth import (
    User, UserCreate, UserUpdate, Role, Permission, UserSession,
    PasswordResetToken, LoginRequest, ChangePasswordRequest, TokenResponse,
    AuthEventType,
)
from domain.common import VASValidationError, Result
from domain.i18n import ErrorCodes
from infrastructure.auth import (
    BcryptPasswordService, JWTService, CasbinEnforcerService, AuditService,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
    MAX_FAILED_LOGIN_ATTEMPTS,
)
from infrastructure.repositories.auth_repository import (
    UserRepository, RoleRepository, PermissionRepository,
    SessionRepository, PasswordResetTokenRepository,
)

logger = logging.getLogger(__name__)


class AuthUseCases:
    def __init__(self, session_factory, jwt_service: JWTService,
                 casbin_service: CasbinEnforcerService,
                 audit_service: AuditService):
        self._session_factory = session_factory
        self._jwt = jwt_service
        self._casbin = casbin_service
        self._audit = audit_service

    # ── Helpers ────────────────────────────────────────────────────────

    def _get_repos(self, session):
        return (
            UserRepository(session),
            RoleRepository(session),
            PermissionRepository(session),
            SessionRepository(session),
            PasswordResetTokenRepository(session),
        )

    def _hash_refresh_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _audit_log(self, user_id: Optional[int], username: Optional[str],
                   event_type: AuthEventType, ip: Optional[str] = None,
                   ua: Optional[str] = None, details: Optional[dict] = None):
        try:
            self._audit.log_event(
                user_id=user_id, username=username,
                event_type=event_type.value, ip_address=ip,
                user_agent=ua, details=details,
            )
        except Exception as e:
            logger.warning(f"Audit log failed (non-fatal): {e}")

    # ── UC-AUTH-01: Login ──────────────────────────────────────────────

    def login(self, req: LoginRequest, ip: Optional[str] = None,
              user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            user_repo = UserRepository(session)
            user = user_repo.get_by_username(req.username)
            if not user:
                self._audit_log(None, req.username, AuthEventType.LOGIN_FAILED, ip, user_agent)
                return Result.failure(VASValidationError(ErrorCodes.AUTH_INVALID_CREDENTIALS))

            if not user.is_active:
                self._audit_log(user.id, user.username, AuthEventType.LOGIN_FAILED, ip, user_agent,
                                {"reason": "account_disabled"})
                return Result.failure(VASValidationError(ErrorCodes.AUTH_ACCOUNT_DISABLED))

            locked_until = user.locked_until
            if locked_until is not None:
                if locked_until.tzinfo is None:
                    locked_until = locked_until.replace(tzinfo=timezone.utc)
                if locked_until > datetime.now(timezone.utc):
                    self._audit_log(user.id, user.username, AuthEventType.LOGIN_FAILED, ip, user_agent,
                                    {"reason": "account_locked"})
                    return Result.failure(VASValidationError(ErrorCodes.AUTH_ACCOUNT_LOCKED))

            if not BcryptPasswordService.verify_password(req.password, user.password_hash):
                user_repo.record_login_failure(req.username)
                self._audit_log(user.id, user.username, AuthEventType.LOGIN_FAILED, ip, user_agent)
                return Result.failure(VASValidationError(ErrorCodes.AUTH_INVALID_CREDENTIALS))

            user_repo.record_login_success(user.id)
            session_repo = SessionRepository(session)

            role_names = [r.name for r in user_repo.get_user_roles(user.id)]
            extra_claims = {"roles": role_names, "locale": user.locale}
            if user.must_change_password:
                extra_claims["must_change_password"] = True

            access_token = self._jwt.create_access_token(user.id, user.username, extra_claims)
            refresh_token = self._jwt.create_refresh_token(user.id, user.username)
            token_hash = self._hash_refresh_token(refresh_token)

            expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            session_entry = UserSession(
                user_id=user.id, refresh_token_hash=token_hash,
                device_info=user_agent, ip_address=ip, expires_at=expires_at,
            )
            session_repo.create(session_entry)

            self._audit_log(user.id, user.username, AuthEventType.LOGIN_SUCCESS, ip, user_agent)

            session.commit()
            return Result.success({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "roles": role_names,
                    "locale": user.locale,
                    "must_change_password": user.must_change_password,
                },
            })
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Login error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-02: Logout ─────────────────────────────────────────────

    def logout(self, user_id: int, refresh_token: Optional[str] = None,
               ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            session_repo = SessionRepository(session)
            if refresh_token:
                token_hash = self._hash_refresh_token(refresh_token)
                stored = session_repo.find_by_refresh_hash(token_hash)
                if stored:
                    session_repo.revoke(stored.id)
            else:
                session_repo.revoke_all_for_user(user_id)
            self._audit_log(user_id, None, AuthEventType.LOGOUT, ip, user_agent)
            session.commit()
            return Result.success(None)
        except Exception as e:
            session.rollback()
            logger.exception(f"Logout error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-03: Token Refresh ──────────────────────────────────────

    def refresh_token(self, refresh_token: str, ip: Optional[str] = None,
                      user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            try:
                payload = self._jwt.decode_token(refresh_token, verify_type="refresh")
            except Exception:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_REFRESH_TOKEN_INVALID))

            user_id = int(payload["sub"])
            username = payload["username"]
            token_hash = self._hash_refresh_token(refresh_token)

            session_repo = SessionRepository(session)
            stored = session_repo.find_by_refresh_hash(token_hash)
            if not stored:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_REFRESH_TOKEN_INVALID))

            session_repo.revoke(stored.id)

            user_repo = UserRepository(session)
            user = user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_ACCOUNT_DISABLED))

            role_names = [r.name for r in user_repo.get_user_roles(user.id)]
            extra_claims = {"roles": role_names, "locale": user.locale}

            new_access = self._jwt.create_access_token(user.id, user.username, extra_claims)
            new_refresh = self._jwt.create_refresh_token(user.id, user.username)
            new_hash = self._hash_refresh_token(new_refresh)
            expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

            new_session = UserSession(
                user_id=user.id, refresh_token_hash=new_hash,
                device_info=user_agent, ip_address=ip, expires_at=expires_at,
            )
            session_repo.create(new_session)

            self._audit_log(user.id, user.username, AuthEventType.TOKEN_REFRESH, ip, user_agent)

            session.commit()
            return Result.success({
                "access_token": new_access,
                "refresh_token": new_refresh,
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            })
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Token refresh error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-04: Change Password ────────────────────────────────────

    def change_password(self, user_id: int, req: ChangePasswordRequest,
                        ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            user_repo = UserRepository(session)
            user = user_repo.get_by_id(user_id)
            if not user:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_USER_NOT_FOUND))

            if not BcryptPasswordService.verify_password(req.current_password, user.password_hash):
                return Result.failure(VASValidationError(ErrorCodes.AUTH_PASSWORD_MISMATCH))

            if BcryptPasswordService.verify_password(req.new_password, user.password_hash):
                return Result.failure(VASValidationError(ErrorCodes.AUTH_PASSWORD_SAME_AS_OLD))

            new_hash = BcryptPasswordService.hash_password(req.new_password)
            user_repo.update_password(user_id, new_hash)

            session_repo = SessionRepository(session)
            session_repo.revoke_all_for_user(user_id)

            self._audit_log(user_id, user.username, AuthEventType.PASSWORD_CHANGE, ip, user_agent)
            session.commit()
            return Result.success(None)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Change password error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-05: User CRUD ──────────────────────────────────────────

    def create_user(self, user_data: UserCreate,
                    ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            password_hash = BcryptPasswordService.hash_password(user_data.password)
            user_repo = UserRepository(session)
            result = user_repo.create(user_data, password_hash)
            if result.is_failure():
                session.rollback()
                return result

            user = result.get_data()
            # Sync roles to Casbin
            for rid in user_data.role_ids:
                role_repo = RoleRepository(session)
                role = role_repo.get_by_id(rid)
                if role:
                    self._casbin.add_role_for_user(user.username, role.name)

            self._audit_log(user.id, user.username, AuthEventType.USER_CREATE, ip, user_agent)
            session.commit()
            return Result.success(user)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Create user error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def get_user(self, user_id: int) -> Result:
        session = self._session_factory()
        try:
            user_repo = UserRepository(session)
            user = user_repo.get_by_id(user_id)
            if not user:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_USER_NOT_FOUND))
            role_names = [r.name for r in user_repo.get_user_roles(user_id)]
            session.close()
            return Result.success({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "position": user.position,
                "department": user.department,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "must_change_password": user.must_change_password,
                "locale": user.locale,
                "roles": role_names,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "created_at": user.created_at.isoformat(),
            })
        except Exception as e:
            logger.exception(f"Get user error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def list_users(self, offset: int = 0, limit: int = 50,
                   active_only: bool = False) -> Result:
        session = self._session_factory()
        try:
            user_repo = UserRepository(session)
            users = user_repo.list(offset, limit, active_only)
            total = user_repo.count(active_only)
            session.close()
            return Result.success({
                "items": [{
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "full_name": u.full_name,
                    "is_active": u.is_active,
                    "is_superuser": u.is_superuser,
                    "locale": u.locale,
                    "last_login": u.last_login.isoformat() if u.last_login else None,
                    "created_at": u.created_at.isoformat(),
                } for u in users],
                "total": total,
                "offset": offset,
                "limit": limit,
            })
        except Exception as e:
            logger.exception(f"List users error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def update_user(self, user_id: int, updates: UserUpdate,
                    ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            user_repo = UserRepository(session)
            result = user_repo.update(user_id, updates)
            if result.is_success():
                self._audit_log(user_id, None, AuthEventType.USER_UPDATE, ip, user_agent)
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Update user error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def delete_user(self, user_id: int,
                    ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            user_repo = UserRepository(session)
            user = user_repo.get_by_id(user_id)
            if not user:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_USER_NOT_FOUND))
            username = user.username

            result = user_repo.delete(user_id)
            if result.is_failure():
                session.rollback()
                return result

            self._casbin.delete_user(username)
            self._audit_log(None, username, AuthEventType.USER_DELETE, ip, user_agent)
            session.commit()
            return Result.success(None)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Delete user error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-06: Role CRUD ──────────────────────────────────────────

    def create_role(self, role: Role,
                    ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            role_repo = RoleRepository(session)
            result = role_repo.create(role)
            if result.is_success():
                self._audit_log(None, None, AuthEventType.USER_UPDATE, ip, user_agent,
                                {"role": role.name, "action": "create"})
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Create role error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def get_role(self, role_id: int) -> Result:
        session = self._session_factory()
        try:
            role_repo = RoleRepository(session)
            role = role_repo.get_by_id(role_id)
            if not role:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_NOT_FOUND))
            perms = role_repo.get_role_permissions(role_id)
            session.close()
            return Result.success({
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "is_system": role.is_system,
                "permissions": [{"id": p.id, "resource": p.resource, "action": p.action}
                                for p in perms],
            })
        except Exception as e:
            logger.exception(f"Get role error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def list_roles(self, offset: int = 0, limit: int = 50) -> Result:
        session = self._session_factory()
        try:
            role_repo = RoleRepository(session)
            roles = role_repo.list(offset, limit)
            total = role_repo.count()
            session.close()
            return Result.success({
                "items": [{
                    "id": r.id, "name": r.name, "display_name": r.display_name,
                    "description": r.description, "is_system": r.is_system,
                } for r in roles],
                "total": total,
            })
        except Exception as e:
            logger.exception(f"List roles error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def update_role(self, role_id: int, name: Optional[str] = None,
                    display_name: Optional[str] = None,
                    description: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            role_repo = RoleRepository(session)
            result = role_repo.update(role_id, name, display_name, description)
            session.commit()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Update role error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def delete_role(self, role_id: int,
                    ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            role_repo = RoleRepository(session)
            role = role_repo.get_by_id(role_id)
            if not role:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_NOT_FOUND))
            result = role_repo.delete(role_id)
            if result.is_success():
                self._casbin.delete_role(role.name)
                self._audit_log(None, None, AuthEventType.ROLE_CHANGE, ip, user_agent,
                                {"role": role.name, "action": "delete"})
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Delete role error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-07: User Role Assignment ───────────────────────────────

    def set_user_roles(self, user_id: int, role_ids: List[int],
                       ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            user_repo = UserRepository(session)
            user = user_repo.get_by_id(user_id)
            if not user:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_USER_NOT_FOUND))

            old_roles = user_repo.get_user_roles(user_id)
            result = user_repo.set_user_roles(user_id, role_ids)
            if result.is_failure():
                session.rollback()
                return result

            for r in old_roles:
                self._casbin.delete_role_for_user(user.username, r.name)
            role_repo = RoleRepository(session)
            for rid in role_ids:
                role = role_repo.get_by_id(rid)
                if role:
                    self._casbin.add_role_for_user(user.username, role.name)

            self._audit_log(user_id, user.username, AuthEventType.ROLE_CHANGE, ip, user_agent,
                            {"role_ids": role_ids})
            session.commit()
            return Result.success(None)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Set user roles error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-08: Permission Management ──────────────────────────────

    def create_permission(self, permission: Permission) -> Result:
        session = self._session_factory()
        try:
            perm_repo = PermissionRepository(session)
            result = perm_repo.create(permission)
            session.commit()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Create permission error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def list_permissions(self, offset: int = 0, limit: int = 100) -> Result:
        session = self._session_factory()
        try:
            perm_repo = PermissionRepository(session)
            perms = perm_repo.list(offset, limit)
            total = perm_repo.count()
            session.close()
            return Result.success({
                "items": [{
                    "id": p.id, "resource": p.resource,
                    "action": p.action, "description": p.description,
                } for p in perms],
                "total": total,
            })
        except Exception as e:
            logger.exception(f"List permissions error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def delete_permission(self, perm_id: int) -> Result:
        session = self._session_factory()
        try:
            perm_repo = PermissionRepository(session)
            result = perm_repo.delete(perm_id)
            session.commit()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Delete permission error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-09: Role-Permission Assignment ─────────────────────────

    def set_role_permissions(self, role_id: int, permission_ids: List[int],
                             ip: Optional[str] = None, user_agent: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            role_repo = RoleRepository(session)
            role = role_repo.get_by_id(role_id)
            if not role:
                return Result.failure(VASValidationError(ErrorCodes.AUTH_ROLE_NOT_FOUND))

            old_perms = role_repo.get_role_permissions(role_id)
            result = role_repo.set_role_permissions(role_id, permission_ids)
            if result.is_failure():
                session.rollback()
                return result

            for p in old_perms:
                self._casbin.remove_policy(role.name, p.resource, p.action)
            perm_repo = PermissionRepository(session)
            for pid in permission_ids:
                perm = perm_repo.get_by_id(pid)
                if perm:
                    self._casbin.add_policy(role.name, perm.resource, perm.action)

            self._audit_log(None, None, AuthEventType.ROLE_CHANGE, ip, user_agent,
                            {"role_id": role_id, "action": "set_permissions"})
            session.commit()
            return Result.success(None)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Set role permissions error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-10: RBAC Enforcement ───────────────────────────────────

    def check_permission(self, username: str, resource: str, action: str) -> bool:
        return self._casbin.enforce(username, resource, action)

    def get_user_permissions(self, username: str) -> List[str]:
        perms = self._casbin.get_permissions_for_user(username)
        return [f"{p[1]}:{p[2]}" for p in perms]

    # ── UC-AUTH-11: Session Management ─────────────────────────────────

    def get_active_sessions(self, user_id: int) -> Result:
        session = self._session_factory()
        try:
            session_repo = SessionRepository(session)
            models = session_repo.find_active_by_user_id(user_id)
            session.close()
            return Result.success([{
                "id": m.id,
                "device_info": m.device_info,
                "ip_address": m.ip_address,
                "created_at": m.created_at.isoformat(),
                "expires_at": m.expires_at.isoformat(),
            } for m in models])
        except Exception as e:
            logger.exception(f"Get sessions error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def revoke_session(self, session_id: int, user_id: int) -> Result:
        session = self._session_factory()
        try:
            session_repo = SessionRepository(session)
            models = session_repo.find_active_by_user_id(user_id)
            if not any(m.id == session_id for m in models):
                return Result.failure(VASValidationError(ErrorCodes.AUTH_SESSION_EXPIRED))
            session_repo.revoke(session_id)
            self._audit_log(user_id, None, AuthEventType.SESSION_REVOKE)
            session.commit()
            return Result.success(None)
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Revoke session error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    def revoke_all_sessions(self, user_id: int, exclude_session_id: Optional[int] = None) -> Result:
        session = self._session_factory()
        try:
            session_repo = SessionRepository(session)
            if exclude_session_id:
                models = session_repo.find_active_by_user_id(user_id)
                for m in models:
                    if m.id != exclude_session_id:
                        session_repo.revoke(m.id)
            else:
                session_repo.revoke_all_for_user(user_id)
            self._audit_log(user_id, None, AuthEventType.SESSION_REVOKE,
                            details={"action": "revoke_all"})
            session.commit()
            return Result.success(None)
        except Exception as e:
            session.rollback()
            logger.exception(f"Revoke all sessions error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()

    # ── UC-AUTH-12: Audit Log ──────────────────────────────────────────

    def get_audit_logs(self, offset: int = 0, limit: int = 50,
                       event_type: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            from infrastructure.models.auth_models import AuthAuditLogModel
            query = session.query(AuthAuditLogModel)
            if event_type:
                query = query.filter(AuthAuditLogModel.event_type == event_type)
            total = query.count()
            models = query.order_by(AuthAuditLogModel.created_at.desc()).offset(offset).limit(limit).all()
            session.close()
            return Result.success({
                "items": [{
                    "id": m.id,
                    "user_id": m.user_id,
                    "username": m.username,
                    "event_type": m.event_type.value if hasattr(m.event_type, 'value') else m.event_type,
                    "ip_address": m.ip_address,
                    "user_agent": m.user_agent,
                    "details": json.loads(m.details) if m.details else None,
                    "created_at": m.created_at.isoformat(),
                } for m in models],
                "total": total,
            })
        except Exception as e:
            logger.exception(f"Get audit logs error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.AUTH_INTERNAL_ERROR))
        finally:
            session.close()


import json
