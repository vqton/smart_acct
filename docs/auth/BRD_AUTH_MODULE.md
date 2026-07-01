# BRD: Authentication & Authorization Module

## SmartACCT ERP — Vietnamese Accounting System

**Version**: 1.0 | **Status**: DRAFT | **Date**: 2026-07-01

---

## 1. VERDICT: PROD-READY ASSESSMENT

**CAN IT OPERATE IN PROD ENV? → NO.**

### Critical Gaps

| # | Category | Gap | Severity |
|---|----------|-----|----------|
| 1 | **User Domain** | No `User` Pydantic entity in `domain/` | BLOCKER |
| 2 | **User DB** | No `users` SQLAlchemy table or migration | BLOCKER |
| 3 | **Password Hashing** | No bcrypt/passlib/argon2 — `requirements.txt` lacks lib | BLOCKER |
| 4 | **Auth Endpoints** | No `POST /auth/login`, `/register`, `/logout` | BLOCKER |
| 5 | **Token Issuance** | No JWT/refresh token generation flow | BLOCKER |
| 6 | **Role/Permission** | No `Role`/`Permission` domain model or DB table | BLOCKER |
| 7 | **Casbin** | `Casbin==1.37.0` in `requirements.txt` but **zero usage** — no enforcer, no model.conf, no policy.csv | HIGH |
| 8 | **Middleware** | `JWTAuthenticationMiddleware` in `infrastructure/auth.py` exists but is **not wired** in `run.py.create_app()` | HIGH |
| 9 | **Password Mgmt** | No change-password, forgot-password, reset-password | HIGH |
| 10 | **User CRUD** | No admin user management (create/list/update/deactivate) | HIGH |
| 11 | **Audit** | No login/logout audit trail | MEDIUM |
| 12 | **Rate Limiting** | Uses `_get_user_from_jwt()` with `options={"verify_signature": False}` — security hole | HIGH |
| 13 | **CORS** | `CORS(app, resources={r"/api/*": {"origins": "*"}})` — wide open | HIGH |
| 14 | **Tests** | Zero auth-related tests | HIGH |
| 15 | **Refresh Token** | No refresh token rotation or expiry | MEDIUM |
| 16 | **Session Mgmt** | No concurrent session control, no device tracking | MEDIUM |
| 17 | **2FA/MFA** | No multi-factor authentication | MEDIUM |

### Regulatory Non-Compliance

| Regulation | Requirement | Status |
|-----------|-------------|--------|
| **Luật An ninh mạng 2018 (24/2018/QH14)** | Điều 26: Xác thực thông tin người dùng đăng ký tài khoản số | ❌ Missing |
| **Luật An ninh mạng 2018 (24/2018/QH14)** | Điều 26: Bảo mật thông tin, tài khoản người dùng | ❌ Missing |
| **Luật Giao dịch điện tử 2023 (20/2023/QH15)** | Điều 22: Chữ ký điện tử an toàn — xác thực chủ thể ký | ❌ Missing |
| **Nghị định 13/2023/NĐ-CP (Bảo vệ dữ liệu cá nhân)** | Điều 9-16: Quyền chủ thể dữ liệu — consent, access, deletion | ❌ Missing |
| **Nghị định 13/2023/NĐ-CP** | Điều 24-27: An toàn hệ thống — mã hóa, kiểm soát truy cập | ❌ Missing |
| **Nghị định 23/2025/NĐ-CP (Chữ ký điện tử — thay thế 130/2018)** | Điều 33: Yêu cầu phần mềm ký số, kiểm tra chữ ký số | ❌ Missing |
| **TT 99/2025/TT-BTC (Chế độ kế toán DN)** | Điều 3: Quản trị và kiểm soát nội bộ — phân định quyền, nghĩa vụ | ❌ Missing |
| **Nghị định 85/2021/NĐ-CP (TMĐT)** | Xác thực giao dịch điện tử | ❌ Missing |

### Verdict

> **➤ Current auth module is NOT production-ready.** It is a stub/scaffold. Deploying to PROD with current implementation exposes the system to: data breach liability under ND 13/2023, non-compliance with TT 99/2025 internal control requirements, and fails Luật An ninh mạng 2018 Điều 26 identity verification requirements. A full auth/authz module must be built from scratch.

---

## 2. REGULATORY FRAMEWORK (Updated 2026)

### Primary Legislation

| Document | Status | Key Provisions |
|----------|--------|----------------|
| **Luật An ninh mạng 24/2018/QH14** | Eff. 01/01/2019 | Điều 26: Identity verification, data protection, security |
| **Luật Giao dịch điện tử 20/2023/QH15** | Eff. 01/07/2024 | Replaces 2005 law. Digital signatures, trusted services |
| **Luật An toàn thông tin mạng 86/2015/QH13** | Eff. 01/07/2016 | Information security standards |
| **Nghị định 13/2023/NĐ-CP** | Eff. 01/07/2023 | Personal data protection — consent, processing, cross-border |
| **Nghị định 23/2025/NĐ-CP** | Eff. 10/04/2025 | **Replaces** ND 130/2018 + 48/2024. E-signatures + trusted services |
| **Nghị định 85/2021/NĐ-CP** | Eff. 25/10/2021 | E-commerce management |
| **TT 99/2025/TT-BTC** | Eff. 01/01/2026 | **Replaces** TT 200/2014. Internal control requirements (Điều 3) |

### Regulatory Hierarchy (Auth)

```
Luật An ninh mạng 2018       ← Primary law for identity & access
  └── ND 13/2023/NĐ-CP        ← Personal data protection (consent, encryption, breach notification)
  └── ND 85/2021/NĐ-CP        ← E-commerce identity
Luật Giao dịch điện tử 2023   ← Digital transactions
  └── ND 23/2025/NĐ-CP        ← E-signatures & trusted services (replaced 130/2018)
Luật Kế toán 2015
  └── TT 99/2025/TT-BTC       ← Accounting regime, internal control (Điều 3)
```

### Deprecated Documents (Do Not Reference)

| Old Document | Status | Replacement |
|-------------|--------|-------------|
| Nghị định 130/2018/NĐ-CP | **Hết hiệu lực** from 10/04/2025 | Nghị định 23/2025/NĐ-CP |
| Nghị định 48/2024/NĐ-CP | **Hết hiệu lực** from 10/04/2025 | Nghị định 23/2025/NĐ-CP |
| Nghị định 26/2007/NĐ-CP | Hết hiệu lực | Nghị định 130/2018 → 23/2025 |
| Thông tư 200/2014/TT-BTC | Hết hiệu lực from 01/01/2026 | TT 99/2025/TT-BTC |
| Thông tư 133/2016/TT-BTC | Hết hiệu lực from 01/01/2026 | TT 99/2025/TT-BTC |

---

## 3. OBJECTIVE

Build a production-grade Authentication & Authorization module for SmartACCT ERP that:

1. **Authenticates** users via JWT (access + refresh tokens) with bcrypt password hashing
2. **Authorizes** via Casbin RBAC (Role-Based Access Control) with fine-grained permissions
3. **Complies** with Vietnamese cybersecurity, data protection, and accounting regulations
4. **Audits** all auth events for regulatory compliance
5. **Secures** all API endpoints properly

---

## 4. DOMAIN MODELS

### 4.1 Proposed Entities (`domain/auth.py`)

```python
class User(BaseModel):
    id: Optional[int] = None
    username: str           # Login ID
    email: str
    password_hash: str      # bcrypt hash, never plaintext
    full_name: str
    position: Optional[str]     # Chức danh (Kế toán trưởng, Kế toán viên...)
    department: Optional[str]   # Phòng ban
    phone: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    must_change_password: bool = False
    locale: str = "vi"
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class Role(BaseModel):
    id: Optional[int] = None
    name: str               # e.g. "ke_toan_truong", "ke_toan_vien"
    display_name: str       # Vietnamese display name
    description: Optional[str]
    is_system: bool = False  # System roles cannot be deleted
    created_at: datetime

class Permission(BaseModel):
    id: Optional[int] = None
    resource: str           # e.g. "gl:journal:create", "coa:account:read"
    action: str             # create, read, update, delete, approve, export
    description: Optional[str]

class UserSession(BaseModel):
    id: Optional[int] = None
    user_id: int
    refresh_token_hash: str
    device_info: Optional[str]
    ip_address: Optional[str]
    expires_at: datetime
    revoked: bool = False
    created_at: datetime
```

### 4.2 Auth Enums

```python
class PermissionAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    EXPORT = "export"
    IMPORT = "import"
    POST = "post"
    REVERSE = "reverse"
    CLOSE = "close"
    ADMIN = "admin"

class AuthEventType(str, enum.Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCK = "account_lock"
    ACCOUNT_UNLOCK = "account_unlock"
    ROLE_CHANGE = "role_change"
    PERMISSION_CHANGE = "permission_change"
    SESSION_REVOKE = "session_revoke"
    MFA_ENABLE = "mfa_enable"
    MFA_DISABLE = "mfa_disable"
```

---

## 5. USE CASES

### UC-AUTH-01: User Registration

| Path | Description |
|------|-------------|
| **Happy** | Admin creates user with username, email, temp password. System hashes password, creates User record, assigns default role. Returns user ID. |
| **Alternative** | Self-registration via invitation token (email link). User sets own password on first login. |
| **Exception** | Username/email already exists → `USERNAME_EXISTS` / `EMAIL_EXISTS`. Weak password → `WEAK_PASSWORD`. Invalid email → `INVALID_EMAIL`. |

### UC-AUTH-02: Login

| Path | Description |
|------|-------------|
| **Happy** | User submits username + password. System verifies bcrypt hash, checks account not locked. Issues access_token (1h) + refresh_token (7d). Returns tokens + user profile. Updates last_login, resets failed attempts. |
| **Alternative 1** | First login + `must_change_password=True` → returns token with `force_password_change` flag. |
| **Alternative 2** | Remember-me → refresh_token validity extended to 30d. |
| **Exception** | Wrong password → increment `failed_login_attempts`. After 5 failures → lock account 15 min (`ACCOUNT_LOCKED`). Account disabled → `ACCOUNT_DISABLED`. |

### UC-AUTH-03: Logout

| Path | Description |
|------|-------------|
| **Happy** | User sends logout with refresh_token. System revokes session. Access token remains valid until expiry (typically short-lived). |
| **Exception** | Invalid/expired refresh token → `INVALID_TOKEN`. Already revoked → silently succeed. |

### UC-AUTH-04: Token Refresh

| Path | Description |
|------|-------------|
| **Happy** | User sends valid refresh_token. System verifies hash, checks not expired/revoked. Issues new access_token + new refresh_token (rotation). Revokes old refresh_token. |
| **Exception** | Refresh token expired → `TOKEN_EXPIRED`. Token revoked → `TOKEN_REVOKED` (possible theft — revoke all user sessions). Invalid signature → `INVALID_TOKEN`. |

### UC-AUTH-05: Authorization Check

| Path | Description |
|------|-------------|
| **Happy** | Request hits protected endpoint. Middleware decodes JWT, extracts user_id + roles. Casbin enforcer checks `(user, resource, action)`. Allow or deny. |
| **Alternative** | Superuser bypasses all permission checks. |
| **Exception** | No token → 401 `UNAUTHORIZED`. Invalid token → 401 `INVALID_TOKEN`. Insufficient permissions → 403 `FORBIDDEN`. |

### UC-AUTH-06: Role Management

| Path | Description |
|------|-------------|
| **Happy** | Admin creates/updates/deletes roles. Assigns permissions to role. Assigns role to users. |
| **Alternative** | System roles (admin, accountant) are read-only. |
| **Exception** | Deleting role assigned to users → `ROLE_IN_USE`. Duplicate role name → `ROLE_EXISTS`. |

### UC-AUTH-07: Permission Management

| Path | Description |
|------|-------------|
| **Happy** | Admin defines resources + actions. Casbin policy updated dynamically. |
| **Exception** | Invalid resource pattern → `INVALID_RESOURCE`. Policy conflict detected → `POLICY_CONFLICT`. |

### UC-AUTH-08: Password Change

| Path | Description |
|------|-------------|
| **Happy** | User sends current_password + new_password. Verifies current hash. Updates password_hash. Revokes all sessions except current. Logs event. |
| **Exception** | Wrong current password → `INVALID_PASSWORD`. New password same as current → `SAME_PASSWORD`. Weak new password → `WEAK_PASSWORD`. |

### UC-AUTH-09: Forgot / Reset Password

| Path | Description |
|------|-------------|
| **Happy** | User requests reset. System generates signed reset_token (15 min), emails link. User submits new password with token. System verifies token, updates hash. |
| **Exception** | Email not found → `EMAIL_NOT_FOUND` (return generic msg to prevent enumeration). Token expired → `RESET_TOKEN_EXPIRED`. Token already used → `RESET_TOKEN_USED`. |

### UC-AUTH-10: Account Lock/Unlock

| Path | Description |
|------|-------------|
| **Happy** | Admin manually locks/unlocks user account. Audit-logged. |
| **Alternative** | Auto-lock after N failed attempts (configurable, default 5). Auto-unlock after lockout period (configurable, default 15 min). |
| **Exception** | Locking already locked user → idempotent. Unlocking non-locked user → idempotent. |

### UC-AUTH-11: Session Management

| Path | Description |
|------|-------------|
| **Happy** | User views active sessions (list). User revokes specific session. Admin revokes all sessions for a user. |
| **Exception** | Cannot revoke current session without re-login → handle gracefully. |

### UC-AUTH-12: Audit Log

| Path | Description |
|------|-------------|
| **Happy** | All auth events logged to `auth_audit_log` table. Queriable by user, date range, event type. |
| **Exception** | Log storage failure → non-blocking (log error, continue). |

---

## 6. SYSTEM ARCHITECTURE

### 6.1 Layer Mapping

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION                              │
│  auth_routes.py  │  auth_middleware.py  │  login_required() │
├─────────────────────────────────────────────────────────────┤
│                      USE CASES                               │
│  AuthUseCases (login, register, authorize, etc.)             │
├─────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE                             │
│  auth.py        │  auth_repository.py  │  auth_models.py    │
│  jwt_service.py │  password_service.py │  casbin_enforcer   │
├─────────────────────────────────────────────────────────────┤
│                       DOMAIN                                 │
│  User │ Role │ Permission │ enums │ interfaces              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Token Lifecycle

```
Registration
     │
     ▼
  Login ──► { access_token (1h) + refresh_token (7d) }
     │
     ├── Access Resource ──► Decode JWT ──► Check Casbin ──► Allow/Deny
     │
     ├── Token Expired ──► Refresh ──► New access_token + rotated refresh_token
     │
     ├── Logout ──► Revoke refresh_token
     │
     └── Password Change ──► Revoke all sessions except current
```

### 6.3 Data Model (Tables)

```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    position VARCHAR(100),
    department VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    must_change_password BOOLEAN DEFAULT FALSE,
    locale VARCHAR(10) DEFAULT 'vi',
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- User ↔ Role (many-to-many)
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Permissions
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    UNIQUE(resource, action)
);

-- Role ↔ Permission (many-to-many)
CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Sessions (refresh token tracking)
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info VARCHAR(500),
    ip_address VARCHAR(45),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Auth Audit Log
CREATE TABLE auth_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Password Reset Tokens
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## 7. CASBIN CONFIGURATION

### Model (`infrastructure/auth_model.conf`)

```
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && keyMatch(r.obj, p.obj) && regexMatch(r.act, p.act)
```

### Sample Policy (built-in seed data)

```csv
p, admin, /*, .*
p, ke_toan_truong, /api/v1/coa/*, (create|read|update|delete|import|export)
p, ke_toan_truong, /api/v1/gl/*, (create|read|update|delete|post|reverse)
p, ke_toan_truong, /api/v1/tax/*, (create|read|update|delete|submit)
p, ke_toan_truong, /api/v1/fs/*, (create|read|update|delete|approve|export)
p, ke_toan_truong, /api/v1/payroll/*, (create|read|update|delete|approve)
p, ke_toan_vien, /api/v1/coa/*, read
p, ke_toan_vien, /api/v1/gl/*, (read|create)
p, ke_toan_vien, /api/v1/tax/*, (read|create)
p, ke_toan_vien, /api/v1/cash/*, (read|create)
p, thu_quy, /api/v1/cash/*, (create|read)
p, thu_quy, /api/v1/bank/*, (create|read)
g, admin, admin
g, ke_toan_truong, ke_toan_truong
g, ke_toan_vien, ke_toan_vien
g, thu_quy, thu_quy
```

---

## 8. ROUTE LAYOUT

| Method | Endpoint | Auth | Permission |
|--------|----------|------|------------|
| POST | `/api/v1/auth/login` | Public | — |
| POST | `/api/v1/auth/logout` | JWT | — |
| POST | `/api/v1/auth/refresh` | Refresh | — |
| POST | `/api/v1/auth/change-password` | JWT | — |
| POST | `/api/v1/auth/forgot-password` | Public | — |
| POST | `/api/v1/auth/reset-password` | ResetToken | — |
| GET | `/api/v1/auth/sessions` | JWT | — |
| DELETE | `/api/v1/auth/sessions/{id}` | JWT | — |
| GET | `/api/v1/auth/me` | JWT | — |
| PUT | `/api/v1/auth/me` | JWT | — |
| GET | `/api/v1/auth/users` | JWT | `auth:user:read` |
| POST | `/api/v1/auth/users` | JWT | `auth:user:create` |
| GET | `/api/v1/auth/users/{id}` | JWT | `auth:user:read` |
| PUT | `/api/v1/auth/users/{id}` | JWT | `auth:user:update` |
| DELETE | `/api/v1/auth/users/{id}` | JWT | `auth:user:delete` |
| PUT | `/api/v1/auth/users/{id}/lock` | JWT | `auth:user:lock` |
| PUT | `/api/v1/auth/users/{id}/unlock` | JWT | `auth:user:unlock` |
| GET | `/api/v1/auth/roles` | JWT | `auth:role:read` |
| POST | `/api/v1/auth/roles` | JWT | `auth:role:create` |
| PUT | `/api/v1/auth/roles/{id}` | JWT | `auth:role:update` |
| DELETE | `/api/v1/auth/roles/{id}` | JWT | `auth:role:delete` |
| GET | `/api/v1/auth/permissions` | JWT | `auth:permission:read` |
| GET | `/api/v1/auth/audit-log` | JWT | `auth:audit:read` |

---

## 9. ERROR CODES (i18n)

| Code | vi | en |
|------|----|----|
| `AUTH_USER_EXISTS` | Tên đăng nhập đã tồn tại | Username already exists |
| `AUTH_EMAIL_EXISTS` | Email đã được đăng ký | Email already registered |
| `AUTH_WEAK_PASSWORD` | Mật khẩu không đủ mạnh (tối thiểu 8 ký tự, có chữ hoa, số, ký tự đặc biệt) | Password too weak |
| `AUTH_INVALID_CREDENTIALS` | Tên đăng nhập hoặc mật khẩu không đúng | Invalid username or password |
| `AUTH_ACCOUNT_LOCKED` | Tài khoản bị khóa do đăng nhập sai nhiều lần. Vui lòng thử lại sau | Account locked due to multiple failed attempts |
| `AUTH_ACCOUNT_DISABLED` | Tài khoản đã bị vô hiệu hóa | Account disabled |
| `AUTH_TOKEN_EXPIRED` | Phiên đăng nhập đã hết hạn | Session expired |
| `AUTH_TOKEN_INVALID` | Token không hợp lệ | Invalid token |
| `AUTH_TOKEN_REVOKED` | Phiên đăng nhập đã bị thu hồi | Session revoked |
| `AUTH_FORBIDDEN` | Bạn không có quyền thực hiện thao tác này | You do not have permission |
| `AUTH_PASSWORD_SAME` | Mật khẩu mới không được trùng với mật khẩu cũ | New password must differ from current |
| `AUTH_RESET_TOKEN_EXPIRED` | Link đặt lại mật khẩu đã hết hạn | Password reset link expired |
| `AUTH_RESET_TOKEN_USED` | Link đặt lại mật khẩu đã được sử dụng | Password reset link already used |
| `AUTH_ROLE_IN_USE` | Không thể xóa vai trò đang được gán cho người dùng | Cannot delete role assigned to users |
| `AUTH_ROLE_EXISTS` | Vai trò đã tồn tại | Role already exists |
| `AUTH_SYSTEM_ROLE` | Không thể sửa đổi vai trò hệ thống | Cannot modify system role |

---

## 10. SECURITY REQUIREMENTS

### 10.1 Password Policy (ND 13/2023 + TT 99/2025 internal control)

| Rule | Value |
|------|-------|
| Min length | 8 characters |
| Require uppercase | Yes |
| Require lowercase | Yes |
| Require digit | Yes |
| Require special char | Yes |
| Max age | 90 days |
| History | Last 5 passwords |
| Lockout threshold | 5 failed attempts |
| Lockout duration | 15 minutes (configurable) |
| Session idle timeout | 30 minutes (admin: 15 min) |

### 10.2 JWT Configuration

| Parameter | Value |
|-----------|-------|
| Algorithm | HS256 (RS256 for production) |
| Access token TTL | 1 hour |
| Refresh token TTL | 7 days (remember-me: 30 days) |
| Token rotation | Yes — refresh invalidates previous |
| Clock skew tolerance | 30 seconds |
| Issuer | `smart-acct` |
| Key rotation | Annually |

### 10.3 API Security

| Measure | Implementation |
|---------|----------------|
| Rate limiting | 10 req/min per IP for login, 100/hr for API |
| CORS | Whitelist specific origins |
| CSP | Flask-Talisman with strict CSP |
| HSTS | Enabled (1 year) |
| Content-Type | `nosniff` |
| XSS Protection | `X-XSS-Protection: 1; mode=block` |
| Brute force | Account lockout + IP-based throttling |
| Audit trail | All auth events logged immutably |

---

## 11. DATA FLOWS

### 11.1 Login Flow

```
Client                    Server
  │                         │
  │  POST /auth/login       │
  │  {username, password}   │
  │────────────────────────►│
  │                         ├── Lookup user by username/email
  │                         ├── Check is_active, locked_until
  │                         ├── Verify bcrypt(password_hash)
  │                         ├── Generate access_token (JWT)
  │                         ├── Generate refresh_token (opaque)
  │                         ├── Store refresh_token_hash in user_sessions
  │                         ├── Log AUTH_LOGIN_SUCCESS
  │                         ├── Reset failed_login_attempts
  │                         ├── Update last_login
  │                         │
  │  {access_token,         │
  │   refresh_token,        │
  │   user}                 │
  │◄────────────────────────│
```

### 11.2 Authorization Flow (per-request)

```
Client                    Server (Middleware)
  │                         │
  │  Request + Bearer JWT   │
  │────────────────────────►│
  │                         ├── Verify JWT signature + expiry
  │                         ├── Extract user_id, role
  │                         ├── Load Casbin enforcer
  │                         ├── Enforce(user, resource, action)
  │                         │
  │  ├── ALLOW ────────────►│── Forward to route handler
  │  ├── DENY  ────────────►│── Return 403 FORBIDDEN
```

---

## 12. SEED ROLES (System Defaults)

| Role | Display Name | Description |
|------|-------------|-------------|
| `admin` | Quản trị hệ thống | Full access to all features |
| `ke_toan_truong` | Kế toán trưởng | Full accounting ops, approvals, reporting |
| `ke_toan_vien` | Kế toán viên | Data entry, read access to COA/GL |
| `ke_toan_tong_hop` | Kế toán tổng hợp | GL posting, financial statements |
| `ke_toan_cong_no` | Kế toán công nợ | AR/AP management |
| `ke_toan_kho` | Kế toán kho | Inventory operations |
| `ke_toan_thue` | Kế toán thuế | Tax declarations, payments |
| `ke_toan_tien_mat` | Kế toán tiền mặt | Cash/bank transactions |
| `ke_toan_tien_luong` | Kế toán tiền lương | Payroll processing |
| `thu_quy` | Thủ quỹ | Cash receipt/payment |
| `kiem_soat_vien` | Kiểm soát viên | Review, cannot create/modify |
| `giam_doc` | Giám đốc | View all reports, approve |

---

## 13. FILE MANIFEST

| File | Purpose |
|------|---------|
| `domain/auth.py` | User, Role, Permission, UserSession entities + enums |
| `domain/i18n.py` | Add AUTH_ error codes |
| `infrastructure/models/auth_models.py` | SQLAlchemy models for 7 tables |
| `migrations/versions/` | Alembic migration for auth tables |
| `infrastructure/repositories/auth_repository.py` | UserRepository, RoleRepository, SessionRepository |
| `infrastructure/auth.py` | Rewrite: JWT service, Casbin enforcer, password service |
| `infrastructure/auth_model.conf` | Casbin RBAC model definition |
| `infrastructure/policy.csv` | Casbin default policies |
| `use_cases/auth/__init__.py` | AuthUseCases (all UC-AUTH methods) |
| `presentation/auth/__init__.py` | Flask blueprint + serializers |
| `presentation/auth/routes.py` | All auth endpoints |
| `tests/test_auth_domain.py` | Domain unit tests |
| `tests/test_auth_integration.py` | Integration tests |

---

## 14. VERIFICATION CRITERIA

| Criterion | Test |
|-----------|------|
| All 12 UC-AUTH use cases implemented | Test each happy/alt/exception path |
| Password stored as bcrypt hash | Verify no plaintext in DB |
| JWT verification includes signature + expiry | Decode and verify |
| Casbin enforce works at middleware level | Call protected endpoint with/without permissions |
| Login rate limiting blocks brute force | Send 11 requests in 1 min → 429 |
| Account locks after 5 failures | 6th attempt → 423 LOCKED |
| Refresh token rotation invalidates old token | Use old token after refresh → error |
| Password reset token expires after 15 min | Wait 16 min → TOKEN_EXPIRED |
| All auth events logged to audit table | Query auth_audit_log for each event type |
| i18n error codes return Vietnamese | Set `Accept-Language: vi` → Vietnamese message |
| CORS blocks unauthorized origins | Request from non-whitelisted origin → blocked |
| Only superuser can manage roles/permissions | Non-admin gets 403 |
| Session revocation works | Revoke → subsequent refresh fails |
| Password history enforced | Try last 5 passwords → `PASSWORD_USED` |

---

## 15. OUTDATED REFERENCES REMOVED

The following documents from previous project state are AUTHENTICATED AS DEPRECATED and must NOT be used:

| Removed Doc | Reason | Replacement |
|-------------|--------|-------------|
| `Nghị định 130/2018/NĐ-CP` | Replaced by ND 23/2025 from 10/04/2025 | `Nghị định 23/2025/NĐ-CP` |
| `Nghị định 48/2024/NĐ-CP` | Amended 130/2018, now also expired | `Nghị định 23/2025/NĐ-CP` |
| `Thông tư 200/2014/TT-BTC` | Replaced by TT 99/2025 from 01/01/2026 | `Thông tư 99/2025/TT-BTC` |
| `Thông tư 133/2016/TT-BTC` | Replaced by TT 99/2025 from 01/01/2026 | `Thông tư 99/2025/TT-BTC` |
| `Luật Giao dịch điện tử 2005` | Replaced by 2023 law | `Luật Giao dịch điện tử 2023` |
