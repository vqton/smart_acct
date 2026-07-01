"""Domain unit tests for Auth module."""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError as PydanticValidationError

from domain.auth import (
    User, UserCreate, UserUpdate, Role, Permission, UserSession,
    PasswordResetToken, AuthAuditLog, LoginRequest, ChangePasswordRequest,
    AuthEventType,
)
from domain.common import VASValidationError
from domain.i18n import ErrorCodes


class TestUser:
    def test_create_valid(self):
        u = User(username="testuser", email="test@example.com", full_name="Test User")
        assert u.username == "testuser"
        assert u.email == "test@example.com"
        assert u.full_name == "Test User"
        assert u.is_active is True
        assert u.is_superuser is False
        assert u.locale == "vi"

    def test_username_empty(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            User(username="", email="a@b.com", full_name="Test")
        if isinstance(exc.value, VASValidationError):
            assert exc.value.msgid == ErrorCodes.AUTH_USERNAME_EMPTY

    def test_username_too_short(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            User(username="ab", email="a@b.com", full_name="Test")
        if isinstance(exc.value, VASValidationError):
            assert exc.value.msgid == ErrorCodes.AUTH_USERNAME_TOO_SHORT

    def test_username_too_long(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            User(username="a" * 51, email="a@b.com", full_name="Test")
        if isinstance(exc.value, VASValidationError):
            assert exc.value.msgid == ErrorCodes.AUTH_USERNAME_TOO_LONG

    def test_email_empty(self):
        with pytest.raises(VASValidationError) as exc:
            User(username="testuser", email="", full_name="Test")
        assert exc.value.msgid == ErrorCodes.AUTH_EMAIL_EMPTY

    def test_email_invalid(self):
        with pytest.raises(VASValidationError) as exc:
            User(username="testuser", email="not-an-email", full_name="Test")
        assert exc.value.msgid == ErrorCodes.AUTH_EMAIL_INVALID

    def test_full_name_empty(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            User(username="testuser", email="a@b.com", full_name="")
        if isinstance(exc.value, VASValidationError):
            assert exc.value.msgid == ErrorCodes.AUTH_FULL_NAME_EMPTY

    def test_invalid_locale(self):
        with pytest.raises(VASValidationError) as exc:
            User(username="testuser", email="a@b.com", full_name="Test", locale="de")
        assert exc.value.msgid == ErrorCodes.AUTH_INVALID_LOCALE

    def test_valid_locales(self):
        for loc in ("vi", "en"):
            u = User(username="testuser", email="a@b.com", full_name="Test", locale=loc)
            assert u.locale == loc

    def test_email_lowercased(self):
        u = User(username="testuser", email="Test@Example.COM", full_name="Test")
        assert u.email == "test@example.com"

    def test_default_timestamps(self):
        u = User(username="testuser", email="a@b.com", full_name="Test")
        assert u.created_at is not None
        assert u.failed_login_attempts == 0
        assert u.must_change_password is False


class TestUserCreate:
    def test_valid(self):
        uc = UserCreate(
            username="newuser", email="new@example.com",
            password="Str0ng!Pass", full_name="New User",
        )
        assert uc.username == "newuser"
        assert uc.role_ids == []

    def test_weak_password_no_upper(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            UserCreate(
                username="newuser", email="a@b.com",
                password="weak!pass1", full_name="Test",
            )

    def test_weak_password_no_lower(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            UserCreate(
                username="newuser", email="a@b.com",
                password="WEAK!PASS1", full_name="Test",
            )

    def test_weak_password_no_digit(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            UserCreate(
                username="newuser", email="a@b.com",
                password="Weak!Pass", full_name="Test",
            )

    def test_weak_password_no_special(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            UserCreate(
                username="newuser", email="a@b.com",
                password="WeakPass1", full_name="Test",
            )

    def test_weak_password_too_short(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            UserCreate(
                username="newuser", email="a@b.com",
                password="Sh0rt!x", full_name="Test",
            )

    def test_strong_password_accepted(self):
        uc = UserCreate(
            username="newuser", email="a@b.com",
            password="Str0ng!Pass#2024", full_name="Test",
        )
        assert uc.password == "Str0ng!Pass#2024"


class TestLoginRequest:
    def test_valid(self):
        req = LoginRequest(username="testuser", password="secret")
        assert req.username == "testuser"
        assert req.remember_me is False

    def test_remember_me(self):
        req = LoginRequest(username="testuser", password="secret", remember_me=True)
        assert req.remember_me is True

    def test_empty_username(self):
        with pytest.raises(PydanticValidationError):
            LoginRequest(username="", password="secret")

    def test_empty_password(self):
        with pytest.raises(PydanticValidationError):
            LoginRequest(username="testuser", password="")


class TestChangePasswordRequest:
    def test_valid(self):
        req = ChangePasswordRequest(
            current_password="OldPass1!",
            new_password="NewStr0ng!Pass",
        )
        assert req.current_password == "OldPass1!"
        assert req.new_password == "NewStr0ng!Pass"

    def test_weak_new_password(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            ChangePasswordRequest(
                current_password="OldPass1!",
                new_password="weak",
            )


class TestRole:
    def test_valid(self):
        r = Role(name="admin", display_name="Administrator")
        assert r.name == "admin"
        assert r.display_name == "Administrator"
        assert r.is_system is False

    def test_name_empty(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            Role(name="", display_name="Test")

    def test_display_name_empty(self):
        with pytest.raises((VASValidationError, PydanticValidationError)) as exc:
            Role(name="test", display_name="")

    def test_system_role(self):
        r = Role(name="superadmin", display_name="Super Admin", is_system=True)
        assert r.is_system is True


class TestPermission:
    def test_valid(self):
        p = Permission(resource="journal_entries", action="create")
        assert p.resource == "journal_entries"
        assert p.action == "create"

    def test_with_description(self):
        p = Permission(
            resource="users", action="delete",
            description="Can delete users",
        )
        assert p.description == "Can delete users"


class TestUserSession:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        s = UserSession(
            user_id=1,
            refresh_token_hash="abc123",
            expires_at=now,
        )
        assert s.user_id == 1
        assert s.revoked is False
        assert s.created_at is not None


class TestPasswordResetToken:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        t = PasswordResetToken(
            user_id=1,
            token_hash="def456",
            expires_at=now,
        )
        assert t.user_id == 1
        assert t.used is False


class TestAuthAuditLog:
    def test_valid(self):
        log = AuthAuditLog(event_type=AuthEventType.LOGIN_SUCCESS)
        assert log.event_type == AuthEventType.LOGIN_SUCCESS
        assert log.created_at is not None

    def test_with_all_fields(self):
        log = AuthAuditLog(
            user_id=1,
            username="testuser",
            event_type=AuthEventType.PASSWORD_CHANGE,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"reason": "expired"},
        )
        assert log.details == {"reason": "expired"}

    def test_all_event_types(self):
        for event in AuthEventType:
            log = AuthAuditLog(event_type=event)
            assert log.event_type == event


class TestUserUpdate:
    def test_all_optional(self):
        uu = UserUpdate()
        assert uu.full_name is None

    def test_partial_update(self):
        uu = UserUpdate(full_name="New Name", locale="en")
        assert uu.full_name == "New Name"
        assert uu.locale == "en"
        assert uu.position is None

    def test_activate(self):
        uu = UserUpdate(is_active=False)
        assert uu.is_active is False
