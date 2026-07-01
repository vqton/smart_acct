from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from infrastructure.models.coa_models import Base


class AuthEventTypeDB(str, enum.Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCK = "account_lock"
    ACCOUNT_UNLOCK = "account_unlock"
    SESSION_REVOKE = "session_revoke"
    ROLE_CHANGE = "role_change"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"


class UserModel(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False, default="")
    full_name = Column(String(200), nullable=False)
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    must_change_password = Column(Boolean, default=False, nullable=False)
    locale = Column(String(10), default="vi", nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    roles = relationship("UserRoleModel", back_populates="user", lazy="selectin",
                         cascade="all, delete-orphan")
    sessions = relationship("UserSessionModel", back_populates="user", lazy="selectin",
                            cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, username='{self.username}')>"


class RoleModel(Base):
    __tablename__ = "auth_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    users = relationship("UserRoleModel", back_populates="role", lazy="selectin",
                         cascade="all, delete-orphan")
    permissions = relationship("RolePermissionModel", back_populates="role", lazy="selectin",
                               cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RoleModel(id={self.id}, name='{self.name}')>"


class UserRoleModel(Base):
    __tablename__ = "auth_user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("auth_roles.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("UserModel", back_populates="roles")
    role = relationship("RoleModel", back_populates="users")

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    def __repr__(self) -> str:
        return f"<UserRoleModel(user_id={self.user_id}, role_id={self.role_id})>"


class PermissionModel(Base):
    __tablename__ = "auth_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint("resource", "action", name="uq_permission"),
        Index("ix_permission_resource_action", "resource", "action"),
    )

    roles = relationship("RolePermissionModel", back_populates="permission", lazy="selectin",
                         cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<PermissionModel(id={self.id}, resource='{self.resource}', action='{self.action}')>"


class RolePermissionModel(Base):
    __tablename__ = "auth_role_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("auth_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("auth_permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    role = relationship("RoleModel", back_populates="permissions")
    permission = relationship("PermissionModel", back_populates="roles")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    def __repr__(self) -> str:
        return f"<RolePermissionModel(role_id={self.role_id}, permission_id={self.permission_id})>"


class UserSessionModel(Base):
    __tablename__ = "auth_user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token_hash = Column(String(255), nullable=False)
    device_info = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("UserModel", back_populates="sessions")

    __table_args__ = (
        Index("ix_session_user_revoked", "user_id", "revoked"),
    )

    def __repr__(self) -> str:
        return f"<UserSessionModel(id={self.id}, user_id={self.user_id})>"


class PasswordResetTokenModel(Base):
    __tablename__ = "auth_password_reset_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<PasswordResetTokenModel(id={self.id}, user_id={self.user_id})>"


class AuthAuditLogModel(Base):
    __tablename__ = "auth_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("auth_users.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String(50), nullable=True)
    event_type = Column(SAEnum(AuthEventTypeDB), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_audit_event_created", "event_type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuthAuditLogModel(id={self.id}, event='{self.event_type}', user='{self.username}')>"
