"""Integration tests for Auth module — repositories + use cases + services."""
import os
import json
import tempfile
import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain.auth import (
    User, UserCreate, UserUpdate, Role, Permission, UserSession,
    LoginRequest, ChangePasswordRequest, AuthEventType,
)
from domain.common import VASValidationError, Result
from domain.i18n import ErrorCodes
from infrastructure.auth import (
    BcryptPasswordService, JWTService, AuditService,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
)
from infrastructure.repositories.auth_repository import (
    UserRepository, RoleRepository, PermissionRepository,
    SessionRepository, PasswordResetTokenRepository,
)
from infrastructure.models.coa_models import Base


# ── Mock Casbin Service ───────────────────────────────────────────────


class MockCasbinService:
    def __init__(self):
        self._roles = {}  # username -> set of roles
        self._policies = {}  # role -> list of (obj, act)

    def enforce(self, sub: str, obj: str, act: str) -> bool:
        roles = self._roles.get(sub, set())
        for role in roles:
            policies = self._policies.get(role, [])
            if any(p[0] == obj and p[1] == act for p in policies):
                return True
        return False

    def add_role_for_user(self, user: str, role: str) -> bool:
        if user not in self._roles:
            self._roles[user] = set()
        self._roles[user].add(role)
        return True

    def delete_role_for_user(self, user: str, role: str) -> bool:
        if user in self._roles and role in self._roles[user]:
            self._roles[user].discard(role)
            return True
        return False

    def delete_user(self, user: str) -> bool:
        self._roles.pop(user, None)
        return True

    def delete_role(self, role: str) -> bool:
        self._policies.pop(role, None)
        for user in self._roles:
            self._roles[user].discard(role)
        return True

    def add_policy(self, role: str, obj: str, act: str) -> bool:
        if role not in self._policies:
            self._policies[role] = []
        self._policies[role].append((obj, act))
        return True

    def remove_policy(self, role: str, obj: str, act: str) -> bool:
        if role in self._policies:
            self._policies[role] = [(o, a) for o, a in self._policies[role] if o != obj or a != act]
            return True
        return False

    def get_permissions_for_user(self, user: str):
        perms = []
        roles = self._roles.get(user, set())
        for role in roles:
            policies = self._policies.get(role, [])
            for obj, act in policies:
                perms.append([user, obj, act])
        return perms

    def get_all_roles(self) -> list:
        return list(self._policies.keys())

    def get_all_subjects(self) -> list:
        return list(self._roles.keys())


# ── Stateful Test Session Manager ──────────────────────────────────────


class FakeDBManager:
    def __init__(self, engine):
        self._engine = engine

    def get_session(self):
        return Session(self._engine)

    def close(self):
        pass


# ── Fixtures ───────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture(scope="function")
def db_manager(session):
    engine = session.get_bind()
    return FakeDBManager(engine)


@pytest.fixture(scope="function")
def jwt_service():
    return JWTService(secret_key="test-secret-key-for-jwt")


@pytest.fixture(scope="function")
def casbin():
    return MockCasbinService()


@pytest.fixture(scope="function")
def audit_service(session):
    return AuditService(session_factory=lambda: session)


@pytest.fixture(scope="function")
def user_repo(session):
    return UserRepository(session)


@pytest.fixture(scope="function")
def role_repo(session):
    return RoleRepository(session)


@pytest.fixture(scope="function")
def perm_repo(session):
    return PermissionRepository(session)


@pytest.fixture(scope="function")
def session_repo(session):
    return SessionRepository(session)


@pytest.fixture(scope="function")
def reset_token_repo(session):
    return PasswordResetTokenRepository(session)


@pytest.fixture(scope="function")
def use_cases(db_manager, jwt_service, casbin, audit_service):
    from use_cases.auth import AuthUseCases
    return AuthUseCases(
        session_factory=db_manager.get_session,
        jwt_service=jwt_service,
        casbin_service=casbin,
        audit_service=audit_service,
    )


# ── Helpers ────────────────────────────────────────────────────────────


def _seed_role(session, name="admin", display_name="Administrator", is_system=False):
    from infrastructure.models.auth_models import RoleModel
    r = RoleModel(name=name, display_name=display_name, is_system=is_system)
    session.add(r)
    session.flush()
    return r


def _seed_user(session, username="testuser", email="test@example.com",
               full_name="Test User", password="Str0ng!Pass1",
               is_active=True, is_superuser=False):
    pw_hash = BcryptPasswordService.hash_password(password)
    from infrastructure.models.auth_models import UserModel
    u = UserModel(
        username=username, email=email, password_hash=pw_hash,
        full_name=full_name, is_active=is_active, is_superuser=is_superuser,
    )
    session.add(u)
    session.flush()
    return u


# ══════════════════════════════════════════════════════════════════════
# BcryptPasswordService Tests
# ══════════════════════════════════════════════════════════════════════


class TestBcryptPasswordService:
    def test_hash_and_verify(self):
        pw = "MyStr0ng!Pass"
        hashed = BcryptPasswordService.hash_password(pw)
        assert hashed != pw
        assert BcryptPasswordService.verify_password(pw, hashed) is True

    def test_wrong_password(self):
        hashed = BcryptPasswordService.hash_password("Correct1!")
        assert BcryptPasswordService.verify_password("Wrong1!", hashed) is False

    def test_empty_password(self):
        hashed = BcryptPasswordService.hash_password("a")
        assert BcryptPasswordService.verify_password("b", hashed) is False


# ══════════════════════════════════════════════════════════════════════
# JWTService Tests
# ══════════════════════════════════════════════════════════════════════


class TestJWTService:
    def test_create_access_token(self, jwt_service):
        token = jwt_service.create_access_token(1, "testuser")
        assert token.count(".") == 2

    def test_decode_valid_access(self, jwt_service):
        token = jwt_service.create_access_token(1, "testuser", {"role": "admin"})
        payload = jwt_service.decode_token(token, verify_type="access")
        assert payload["sub"] == "1"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
        assert payload["role"] == "admin"

    def test_create_and_decode_refresh(self, jwt_service):
        token = jwt_service.create_refresh_token(1, "testuser")
        payload = jwt_service.decode_token(token, verify_type="refresh")
        assert payload["type"] == "refresh"

    def test_reject_access_as_refresh(self, jwt_service):
        token = jwt_service.create_access_token(1, "testuser")
        with pytest.raises(Exception):
            jwt_service.decode_token(token, verify_type="refresh")

    def test_expired_token(self, jwt_service):
        import jwt as pyjwt
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "1", "username": "testuser",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
            "iss": "smartacct", "type": "access",
        }
        expired = pyjwt.encode(payload, "test-secret-key-for-jwt", algorithm="HS256")
        with pytest.raises(Exception):
            jwt_service.decode_token(expired)


# ══════════════════════════════════════════════════════════════════════
# UserRepository Tests
# ══════════════════════════════════════════════════════════════════════


class TestUserRepository:
    def test_create_user(self, user_repo, session):
        uc = UserCreate(
            username="newuser", email="new@example.com",
            password="Str0ng!Pass", full_name="New User",
        )
        pw_hash = BcryptPasswordService.hash_password("Str0ng!Pass")
        result = user_repo.create(uc, pw_hash)
        assert result.is_success()
        user = result.get_data()
        assert user.id is not None
        assert user.username == "newuser"

    def test_create_duplicate_username(self, user_repo, session):
        uc1 = UserCreate(username="dup", email="a@b.com", password="Str0ng!Pass", full_name="A")
        pw_hash = BcryptPasswordService.hash_password("Str0ng!Pass")
        user_repo.create(uc1, pw_hash)
        session.flush()
        uc2 = UserCreate(username="dup", email="c@d.com", password="Str0ng!Pass", full_name="B")
        result = user_repo.create(uc2, pw_hash)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_USERNAME_EXISTS

    def test_get_by_id(self, user_repo, session):
        model = _seed_user(session)
        session.commit()
        user = user_repo.get_by_id(model.id)
        assert user is not None
        assert user.username == "testuser"

    def test_get_by_username(self, user_repo, session):
        model = _seed_user(session)
        session.commit()
        user = user_repo.get_by_username("testuser")
        assert user is not None
        assert user.email == "test@example.com"

    def test_get_by_username_not_found(self, user_repo, session):
        user = user_repo.get_by_username("nonexistent")
        assert user is None

    def test_get_by_email(self, user_repo, session):
        _seed_user(session)
        session.commit()
        user = user_repo.get_by_email("test@example.com")
        assert user is not None

    def test_list_users(self, user_repo, session):
        _seed_user(session, username="user1", email="u1@b.com")
        _seed_user(session, username="user2", email="u2@b.com")
        session.commit()
        users = user_repo.list(offset=0, limit=10)
        assert len(users) >= 2

    def test_count(self, user_repo, session):
        _seed_user(session, username="c1", email="c1@b.com")
        _seed_user(session, username="c2", email="c2@b.com")
        session.commit()
        assert user_repo.count() >= 2

    def test_update_user(self, user_repo, session):
        model = _seed_user(session)
        session.commit()
        updates = UserUpdate(full_name="Updated Name", locale="en")
        result = user_repo.update(model.id, updates)
        assert result.is_success()
        updated = result.get_data()
        assert updated.full_name == "Updated Name"
        assert updated.locale == "en"

    def test_update_nonexistent(self, user_repo, session):
        updates = UserUpdate(full_name="No one")
        result = user_repo.update(99999, updates)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_USER_NOT_FOUND

    def test_delete_user(self, user_repo, session):
        model = _seed_user(session, username="deluser", email="del@b.com")
        session.commit()
        result = user_repo.delete(model.id)
        assert result.is_success()
        assert user_repo.get_by_id(model.id) is None

    def test_delete_last_superuser_blocked(self, user_repo, session):
        model = _seed_user(session, username="su", email="su@b.com", is_superuser=True)
        session.commit()
        result = user_repo.delete(model.id)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_CANNOT_DELETE_LAST_SUPERUSER

    def test_record_login_success(self, user_repo, session):
        model = _seed_user(session)
        session.commit()
        user_repo.record_login_success(model.id)
        session.flush()
        user = user_repo.get_by_id(model.id)
        assert user.failed_login_attempts == 0
        assert user.last_login is not None

    def test_record_login_failure(self, user_repo, session):
        model = _seed_user(session, username="failuser", email="fail@b.com")
        session.commit()
        for _ in range(3):
            user_repo.record_login_failure("failuser")
        session.flush()
        user = user_repo.get_by_id(model.id)
        assert user.failed_login_attempts == 3

    def test_lock_account(self, user_repo, session):
        model = _seed_user(session, username="lockuser", email="lock@b.com")
        session.commit()
        user_repo.lock_account(model.id)
        session.flush()
        user = user_repo.get_by_id(model.id)
        assert user.locked_until is not None

    def test_unlock_account(self, user_repo, session):
        model = _seed_user(session, username="ulusr", email="ul@b.com")
        session.commit()
        user_repo.lock_account(model.id)
        user_repo.unlock_account(model.id)
        session.flush()
        user = user_repo.get_by_id(model.id)
        assert user.locked_until is None
        assert user.failed_login_attempts == 0

    def test_set_user_roles(self, user_repo, session):
        user = _seed_user(session, username="roleuser", email="ru@b.com")
        role = _seed_role(session, name="viewer", display_name="Viewer")
        session.commit()
        result = user_repo.set_user_roles(user.id, [role.id])
        assert result.is_success()
        roles = user_repo.get_user_roles(user.id)
        assert len(roles) == 1
        assert roles[0].name == "viewer"


# ══════════════════════════════════════════════════════════════════════
# RoleRepository Tests
# ══════════════════════════════════════════════════════════════════════


class TestRoleRepository:
    def test_create_role(self, role_repo, session):
        role = Role(name="editor", display_name="Editor", description="Can edit")
        result = role_repo.create(role)
        assert result.is_success()
        assert result.get_data().id is not None

    def test_create_duplicate(self, role_repo, session):
        role_repo.create(Role(name="dup", display_name="Dup"))
        session.flush()
        result = role_repo.create(Role(name="dup", display_name="Dup2"))
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_ROLE_EXISTS

    def test_get_by_id(self, role_repo, session):
        model = _seed_role(session)
        session.commit()
        role = role_repo.get_by_id(model.id)
        assert role is not None
        assert role.name == "admin"

    def test_list_roles(self, role_repo, session):
        _seed_role(session, name="r1", display_name="R1")
        _seed_role(session, name="r2", display_name="R2")
        session.commit()
        roles = role_repo.list()
        assert len(roles) >= 2

    def test_update_role(self, role_repo, session):
        model = _seed_role(session)
        session.commit()
        result = role_repo.update(model.id, display_name="Super Admin")
        assert result.is_success()
        assert result.get_data().display_name == "Super Admin"

    def test_update_system_role_blocked(self, role_repo, session):
        model = _seed_role(session, name="sys", display_name="System", is_system=True)
        session.commit()
        result = role_repo.update(model.id, display_name="Not Allowed")
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_CANNOT_MODIFY_SYSTEM_ROLE

    def test_delete_role(self, role_repo, session):
        model = _seed_role(session, name="delrole", display_name="Dell")
        session.commit()
        result = role_repo.delete(model.id)
        assert result.is_success()
        assert role_repo.get_by_id(model.id) is None

    def test_delete_system_role_blocked(self, role_repo, session):
        model = _seed_role(session, name="sysdel", display_name="Sys", is_system=True)
        session.commit()
        result = role_repo.delete(model.id)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_CANNOT_MODIFY_SYSTEM_ROLE

    def test_set_role_permissions(self, role_repo, perm_repo, session):
        model = _seed_role(session, name="seer", display_name="Seer")
        perm = perm_repo.create(Permission(resource="docs", action="read"))
        session.flush()
        assert perm.is_success()
        result = role_repo.set_role_permissions(model.id, [perm.get_data().id])
        assert result.is_success()
        perms = role_repo.get_role_permissions(model.id)
        assert len(perms) == 1
        assert perms[0].resource == "docs"


# ══════════════════════════════════════════════════════════════════════
# PermissionRepository Tests
# ══════════════════════════════════════════════════════════════════════


class TestPermissionRepository:
    def test_create(self, perm_repo, session):
        p = Permission(resource="reports", action="export")
        result = perm_repo.create(p)
        assert result.is_success()
        assert result.get_data().id is not None

    def test_create_duplicate(self, perm_repo, session):
        perm_repo.create(Permission(resource="x", action="y"))
        session.flush()
        result = perm_repo.create(Permission(resource="x", action="y"))
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_PERMISSION_EXISTS

    def test_list(self, perm_repo, session):
        perm_repo.create(Permission(resource="a", action="r"))
        perm_repo.create(Permission(resource="a", action="w"))
        session.flush()
        perms = perm_repo.list()
        assert len(perms) >= 2

    def test_delete(self, perm_repo, session):
        result = perm_repo.create(Permission(resource="tmp", action="x"))
        pid = result.get_data().id
        session.flush()
        result = perm_repo.delete(pid)
        assert result.is_success()
        assert perm_repo.get_by_id(pid) is None


# ══════════════════════════════════════════════════════════════════════
# SessionRepository Tests
# ══════════════════════════════════════════════════════════════════════


class TestSessionRepository:
    def test_create_and_find(self, session_repo, session):
        user = _seed_user(session)
        session.commit()
        s = UserSession(
            user_id=user.id,
            refresh_token_hash="abc123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        created = session_repo.create(s)
        assert created.id is not None

        found = session_repo.find_by_refresh_hash("abc123")
        assert found is not None
        assert found.user_id == user.id

    def test_revoke(self, session_repo, session):
        user = _seed_user(session)
        session.commit()
        s = UserSession(
            user_id=user.id,
            refresh_token_hash="torevoke",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        created = session_repo.create(s)
        session_repo.revoke(created.id)
        session.flush()
        found = session_repo.find_by_refresh_hash("torevoke")
        assert found is None

    def test_revoke_all_for_user(self, session_repo, session):
        user = _seed_user(session)
        session.commit()
        for i in range(3):
            session_repo.create(UserSession(
                user_id=user.id,
                refresh_token_hash=f"tok{i}",
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            ))
        session_repo.revoke_all_for_user(user.id)
        session.flush()
        active = session_repo.find_active_by_user_id(user.id)
        assert len(active) == 0


# ══════════════════════════════════════════════════════════════════════
# AuthUseCases Integration Tests
# ══════════════════════════════════════════════════════════════════════


class TestAuthUseCasesLogin:
    def test_login_success(self, use_cases, session):
        _seed_user(session)
        session.commit()
        req = LoginRequest(username="testuser", password="Str0ng!Pass1")
        result = use_cases.login(req)
        assert result.is_success()
        data = result.get_data()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, use_cases, session):
        _seed_user(session)
        session.commit()
        req = LoginRequest(username="testuser", password="Wrong1!")
        result = use_cases.login(req)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_INVALID_CREDENTIALS

    def test_login_disabled_account(self, use_cases, session):
        _seed_user(session, username="disabled", email="dis@b.com", is_active=False)
        session.commit()
        req = LoginRequest(username="disabled", password="Str0ng!Pass1")
        result = use_cases.login(req)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_ACCOUNT_DISABLED

    def test_login_locked_account(self, use_cases, session):
        from infrastructure.models.auth_models import UserModel
        pw = BcryptPasswordService.hash_password("Str0ng!Pass1")
        u = UserModel(
            username="locked", email="lock@b.com", password_hash=pw,
            full_name="Locked", failed_login_attempts=5,
            locked_until=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        session.add(u)
        session.commit()
        req = LoginRequest(username="locked", password="Str0ng!Pass1")
        result = use_cases.login(req)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_ACCOUNT_LOCKED

    def test_login_nonexistent_user(self, use_cases, session):
        req = LoginRequest(username="nobody", password="Str0ng!Pass1")
        result = use_cases.login(req)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_INVALID_CREDENTIALS


class TestAuthUseCasesLogout:
    def test_logout(self, use_cases, session):
        model = _seed_user(session)
        session.commit()
        result = use_cases.logout(model.id)
        assert result.is_success()


class TestAuthUseCasesRefreshToken:
    def test_refresh_token(self, use_cases, jwt_service, session):
        model = _seed_user(session)
        session.commit()
        # Login first to get tokens
        req = LoginRequest(username="testuser", password="Str0ng!Pass1")
        login_result = use_cases.login(req)
        assert login_result.is_success()
        refresh_token = login_result.get_data()["refresh_token"]

        # Now refresh
        result = use_cases.refresh_token(refresh_token)
        assert result.is_success()
        new_data = result.get_data()
        assert "access_token" in new_data
        assert "refresh_token" in new_data
        assert new_data["refresh_token"] != refresh_token  # rotation


class TestAuthUseCasesChangePassword:
    def test_change_password(self, use_cases, session):
        model = _seed_user(session)
        session.commit()
        req = ChangePasswordRequest(
            current_password="Str0ng!Pass1",
            new_password="NewStr0ng!Pass1",
        )
        result = use_cases.change_password(model.id, req)
        assert result.is_success()

        # Login with new password
        login = use_cases.login(LoginRequest(
            username="testuser", password="NewStr0ng!Pass1",
        ))
        assert login.is_success()

    def test_wrong_current_password(self, use_cases, session):
        model = _seed_user(session)
        session.commit()
        req = ChangePasswordRequest(
            current_password="Wrong1!",
            new_password="NewStr0ng!Pass1",
        )
        result = use_cases.change_password(model.id, req)
        assert result.is_failure()
        assert result.get_error().msgid == ErrorCodes.AUTH_PASSWORD_MISMATCH


class TestAuthUseCasesUserCRUD:
    def test_create_user(self, use_cases, session):
        uc = UserCreate(
            username="createuser", email="cu@b.com",
            password="Str0ng!Pass", full_name="Created User",
        )
        result = use_cases.create_user(uc)
        assert result.is_success()
        user = result.get_data()
        assert user.username == "createuser"

    def test_get_user(self, use_cases, session):
        model = _seed_user(session)
        session.commit()
        result = use_cases.get_user(model.id)
        assert result.is_success()
        data = result.get_data()
        assert data["username"] == "testuser"

    def test_list_users(self, use_cases, session):
        _seed_user(session, username="lu1", email="lu1@b.com")
        _seed_user(session, username="lu2", email="lu2@b.com")
        session.commit()
        result = use_cases.list_users()
        assert result.is_success()
        data = result.get_data()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

    def test_update_user(self, use_cases, session):
        model = _seed_user(session)
        session.commit()
        updates = UserUpdate(full_name="Updated Name")
        result = use_cases.update_user(model.id, updates)
        assert result.is_success()

    def test_delete_user(self, use_cases, session):
        model = _seed_user(session, username="delus", email="dus@b.com")
        session.commit()
        result = use_cases.delete_user(model.id)
        assert result.is_success()


class TestAuthUseCasesRoleCRUD:
    def test_create_role(self, use_cases, session):
        role = Role(name="testrole", display_name="Test Role")
        result = use_cases.create_role(role)
        assert result.is_success()
        data = result.get_data()
        assert data.name == "testrole"

    def test_get_role(self, use_cases, session):
        from infrastructure.models.auth_models import RoleModel
        r = RoleModel(name="getrole", display_name="Get Role")
        session.add(r)
        session.commit()
        result = use_cases.get_role(r.id)
        assert result.is_success()
        assert result.get_data()["name"] == "getrole"

    def test_list_roles(self, use_cases, session):
        from infrastructure.models.auth_models import RoleModel
        session.add(RoleModel(name="lr1", display_name="LR1"))
        session.add(RoleModel(name="lr2", display_name="LR2"))
        session.commit()
        result = use_cases.list_roles()
        assert result.is_success()
        assert result.get_data()["total"] >= 2


class TestAuthUseCasesPermission:
    def test_create_permission(self, use_cases, session):
        p = Permission(resource="invoices", action="approve")
        result = use_cases.create_permission(p)
        assert result.is_success()
        data = result.get_data()
        assert data.resource == "invoices"

    def test_list_permissions(self, use_cases, session):
        from infrastructure.repositories.auth_repository import PermissionRepository
        perm_repo = PermissionRepository(session)
        perm_repo.create(Permission(resource="x", action="r"))
        perm_repo.create(Permission(resource="x", action="w"))
        session.commit()
        result = use_cases.list_permissions()
        assert result.is_success()
        assert result.get_data()["total"] >= 2


class TestAuthUseCasesCasbinEnforcement:
    def test_check_permission(self, use_cases, casbin, session):
        casbin.add_role_for_user("cbdemo", "viewer")
        casbin.add_policy("viewer", "docs", "read")

        allowed = use_cases.check_permission("cbdemo", "docs", "read")
        assert allowed is True

        not_allowed = use_cases.check_permission("cbdemo", "docs", "delete")
        assert not_allowed is False

    def test_no_permission_by_default(self, use_cases, session):
        allowed = use_cases.check_permission("someuser", "any", "any")
        assert allowed is False


class TestAuthUseCasesSessions:
    def test_get_active_sessions(self, use_cases, session):
        model = _seed_user(session)
        session.commit()
        result = use_cases.get_active_sessions(model.id)
        assert result.is_success()
        assert result.get_data() == []  # no sessions initially

    def test_revoke_all_sessions(self, use_cases, session):
        model = _seed_user(session)
        session.commit()
        result = use_cases.revoke_all_sessions(model.id)
        assert result.is_success()


class TestAuthUseCasesAuditLog:
    def test_get_audit_logs(self, use_cases, session):
        # Perform a login to generate audit logs
        _seed_user(session)
        session.commit()
        req = LoginRequest(username="testuser", password="Str0ng!Pass1")
        use_cases.login(req)

        result = use_cases.get_audit_logs()
        assert result.is_success()
        data = result.get_data()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
