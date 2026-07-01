import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import bcrypt
import jwt
from casbin import Enforcer
from casbin_sqlalchemy_adapter import Adapter

logger = logging.getLogger(__name__)


ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_FAILED_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 30


class BcryptPasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class JWTService:
    def __init__(self, secret_key: str, issuer: str = "smartacct"):
        self.secret_key = secret_key
        self.issuer = issuer

    def create_access_token(self, user_id: int, username: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "username": username,
            "iat": now,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iss": self.issuer,
            "type": "access",
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def create_refresh_token(self, user_id: int, username: str) -> str:
        import secrets
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "username": username,
            "iat": now,
            "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "iss": self.issuer,
            "type": "refresh",
            "jti": secrets.token_urlsafe(16),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def decode_token(self, token: str, verify_type: Optional[str] = None) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"], issuer=self.issuer)
            if verify_type and payload.get("type") != verify_type:
                raise jwt.InvalidTokenError(f"Expected token type '{verify_type}', got '{payload.get('type')}'")
            return payload
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError:
            raise


class CasbinEnforcerService:
    def __init__(self, model_path: str, db_url: str):
        self.model_path = model_path
        self.db_url = db_url
        self._enforcer = None

    def initialize(self) -> None:
        adapter = Adapter(self.db_url)
        self._enforcer = Enforcer(self.model_path, adapter)
        self._enforcer.enable_auto_save(True)
        logger.info("Casbin enforcer initialized")

    @property
    def enforcer(self) -> Enforcer:
        if self._enforcer is None:
            raise RuntimeError("Casbin enforcer not initialized — call initialize() first")
        return self._enforcer

    def enforce(self, sub: str, obj: str, act: str) -> bool:
        return self.enforcer.enforce(sub, obj, act)

    def get_roles_for_user(self, user: str) -> List[str]:
        return self.enforcer.get_roles_for_user(user)

    def get_permissions_for_user(self, user: str) -> List[List[str]]:
        return self.enforcer.get_permissions_for_user(user)

    def get_permissions_for_role(self, role: str) -> List[List[str]]:
        return self.enforcer.get_permissions_for_role(role)

    def add_role_for_user(self, user: str, role: str) -> bool:
        return self.enforcer.add_role_for_user(user, role)

    def delete_role_for_user(self, user: str, role: str) -> bool:
        return self.enforcer.delete_role_for_user(user, role)

    def get_all_roles(self) -> List[str]:
        return self.enforcer.get_all_roles()

    def get_all_subjects(self) -> List[str]:
        return self.enforcer.get_all_subjects()

    def delete_user(self, user: str) -> bool:
        return self.enforcer.delete_user(user)

    def delete_role(self, role: str) -> bool:
        self.enforcer.delete_permissions_for_user(role)
        return self.enforcer.delete_role(role)

    def add_policy(self, role: str, obj: str, act: str) -> bool:
        return self.enforcer.add_policy(role, obj, act)

    def remove_policy(self, role: str, obj: str, act: str) -> bool:
        return self.enforcer.remove_policy(role, obj, act)

    def remove_filtered_policy(self, role: str, field_index: int, *field_values: str) -> bool:
        return self.enforcer.remove_filtered_policy(field_index, role, *field_values)


class AuditService:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def log_event(self, user_id: Optional[int], username: Optional[str],
                  event_type: str, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None) -> None:
        from infrastructure.models.auth_models import AuthAuditLogModel
        session = self._session_factory()
        try:
            log = AuthAuditLogModel(
                user_id=user_id,
                username=username,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                details=json.dumps(details, ensure_ascii=False) if details else None,
            )
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log auth event: {e}")
        finally:
            session.close()


import json
