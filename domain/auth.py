from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum

from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result, _quantize_vnd


class AuthEventType(str, Enum):
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


class User(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., max_length=255)
    password_hash: str = Field(default="", max_length=255)
    full_name: str = Field(..., min_length=1, max_length=200)
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: bool = True
    is_superuser: bool = False
    must_change_password: bool = False
    locale: str = "vi"
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.AUTH_USERNAME_EMPTY)
        if len(v) < 3:
            raise VASValidationError(ErrorCodes.AUTH_USERNAME_TOO_SHORT)
        if len(v) > 50:
            raise VASValidationError(ErrorCodes.AUTH_USERNAME_TOO_LONG)
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.AUTH_EMAIL_EMPTY)
        if "@" not in v or "." not in v.split("@")[-1]:
            raise VASValidationError(ErrorCodes.AUTH_EMAIL_INVALID)
        return v.strip().lower()

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.AUTH_FULL_NAME_EMPTY)
        return v.strip()

    @field_validator("password_hash")
    @classmethod
    def validate_password_hash(cls, v: str) -> str:
        if v and len(v) > 255:
            raise VASValidationError(ErrorCodes.AUTH_INVALID_FIELD)
        return v

    @model_validator(mode="after")
    def validate_locale(self):
        if self.locale not in ("vi", "en"):
            raise VASValidationError(ErrorCodes.AUTH_INVALID_LOCALE)
        return self


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=200)
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role_ids: List[int] = Field(default_factory=list)
    locale: str = "vi"

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        if not any(c.isupper() for c in v):
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        if not any(c.islower() for c in v):
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        if not any(c.isdigit() for c in v):
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" for c in v):
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    locale: Optional[str] = None
    is_active: Optional[bool] = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: dict


class Role(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    display_name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    is_system: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.AUTH_ROLE_NAME_EMPTY)
        return v.strip()

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.AUTH_ROLE_DISPLAY_NAME_EMPTY)
        return v.strip()


class Permission(BaseModel):
    id: Optional[int] = None
    resource: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class UserSession(BaseModel):
    id: Optional[int] = None
    user_id: int
    refresh_token_hash: str = Field(..., max_length=255)
    device_info: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    expires_at: datetime
    revoked: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PasswordResetToken(BaseModel):
    id: Optional[int] = None
    user_id: int
    token_hash: str = Field(..., max_length=255)
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthAuditLog(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    event_type: AuthEventType
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        if not any(c.isupper() for c in v):
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        if not any(c.islower() for c in v):
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        if not any(c.isdigit() for c in v):
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" for c in v):
            raise VASValidationError(ErrorCodes.AUTH_WEAK_PASSWORD)
        return v
