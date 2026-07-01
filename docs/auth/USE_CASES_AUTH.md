# Use Cases: Authentication & Authorization Module

## UC-AUTH-01 → UC-AUTH-12

---

## UC-AUTH-01: User Registration

**Goal**: Create user account in system.

**Actor**: Admin (or self via invitation).

**Preconditions**: Admin authenticated with `auth:user:create` permission.

### Happy Path

1. Admin submits `{username, email, password, full_name, position, department, role_ids}`
2. System validates: username format (3-50 alphanumeric), email format, password strength (8+ chars, upper+lower+digit+special)
3. System checks username/email uniqueness
4. System hashes password with bcrypt (cost=12)
5. System creates `User` record
6. System assigns roles via `user_roles` table
7. System creates default session policy in Casbin
8. System logs `AUTH_USER_CREATED` to audit log
9. Return `{user_id, username, email, created_at}`

### Alternative: Self-Registration via Invitation

1. Admin creates user with `must_change_password=True`, no password set
2. System generates 48h invitation token, emails registration link
3. User clicks link, sets password
4. System hashes, updates user, clears token
5. Redirect to login

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Username exists | `AUTH_USER_EXISTS` | 409 |
| Email exists | `AUTH_EMAIL_EXISTS` | 409 |
| Weak password | `AUTH_WEAK_PASSWORD` | 422 |
| Invalid email format | `AUTH_INVALID_EMAIL` | 422 |
| Role not found | `AUTH_ROLE_NOT_FOUND` | 404 |
| Permission denied | `AUTH_FORBIDDEN` | 403 |

### Process Flow

```
[Admin] → POST /auth/users → Validate input → Check uniqueness → Hash pw → 
Create User → Assign Roles → Sync Casbin → Log audit → Return 201
```

### Rules

- Username: 3-50 chars, `^[a-zA-Z0-9_]+$`
- Email: valid RFC 5322 format
- Password: min 8 chars, ≥1 upper, ≥1 lower, ≥1 digit, ≥1 special
- bcrypt cost factor: 12 (configurable)
- `must_change_password` if created without user-set password

---

## UC-AUTH-02: Login

**Goal**: Authenticate user, issue tokens.

**Actor**: Any user (unauthenticated).

**Preconditions**: User account exists and is active.

### Happy Path

1. User submits `{username, password}`
2. System looks up user by username or email
3. System checks `is_active=True` and `locked_until` is past or NULL
4. System verifies password with bcrypt
5. System generates:
   - access_token (JWT HS256, 1h): `{sub: user_id, role: role_names, iat, exp}`
   - refresh_token (opaque 32-byte random, 7d)
6. System stores `sha256(refresh_token)` in `user_sessions`
7. System resets `failed_login_attempts=0`, updates `last_login`
8. System logs `AUTH_LOGIN_SUCCESS`
9. Return `{access_token, refresh_token, expires_in, user}`

### Alternative: Force Password Change

- User has `must_change_password=True`
- Return token with `force_password_change: True` in JWT claims
- All API calls except `/auth/change-password` return `AUTH_MUST_CHANGE_PASSWORD` (428)

### Alternative: Remember Me

- Client sends `remember_me: true`
- Refresh token TTL extended from 7d to 30d

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Wrong password (≤4 attempts) | `AUTH_INVALID_CREDENTIALS` | 401 |
| 5th wrong attempt | `AUTH_ACCOUNT_LOCKED` | 423 |
| Account disabled | `AUTH_ACCOUNT_DISABLED` | 403 |
| Missing username/password | `AUTH_MISSING_FIELDS` | 422 |

### Process Flow

```
[User] → POST /auth/login → Lookup user → Check active/locked → 
Verify bcrypt → Generate tokens → Store session → Log audit → Return 200
```

### Rules

- Failed attempts: increment counter on each failure
- Lockout: 5 failures → lock 15 min (`locked_until = now + 15min`)
- Lockout duration: configurable via `AUTH_LOCKOUT_MINUTES`
- JWT includes `jti` (token ID) for revocation
- Refresh token: `secrets.token_urlsafe(32)`, stored as `sha256`

---

## UC-AUTH-03: Logout

**Goal**: Revoke refresh token, end session.

**Actor**: Authenticated user.

**Preconditions**: User has valid JWT + refresh_token.

### Happy Path

1. User sends `Authorization: Bearer {access_token}` + `{refresh_token}`
2. System verifies access_token signature
3. System looks up `user_sessions` by `sha256(refresh_token)`
4. System sets `revoked=True`
5. System logs `AUTH_LOGOUT`
6. Return `{message: "Đã đăng xuất"}`

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Refresh token not found | `AUTH_TOKEN_INVALID` | 401 |
| Already revoked | (silent success) | 200 |

---

## UC-AUTH-04: Token Refresh

**Goal**: Issue new access_token using refresh_token (rotation).

**Actor**: Authenticated user.

**Preconditions**: User has valid refresh_token.

### Happy Path

1. User sends `{refresh_token}`
2. System computes `sha256(refresh_token)`, looks up session
3. System checks: not revoked, not expired
4. System generates new access_token + new refresh_token
5. System revokes old session, creates new session with new hash
6. Return `{access_token, refresh_token, expires_in}`

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Token expired | `AUTH_TOKEN_EXPIRED` | 401 |
| Token revoked | `AUTH_TOKEN_REVOKED` | 401 |
| Token not found | `AUTH_TOKEN_INVALID` | 401 |

### Security: Token Rotation

> On refresh: old refresh_token is revoked. If a stolen refresh_token is used after the legitimate owner refreshed → the legitimate session is already gone. This signals theft. The system should revoke ALL sessions for the user when a revoked token is used (token reuse detection).

---

## UC-AUTH-05: Authorization Check

**Goal**: Enforce access control on protected endpoints.

**Actor**: Middleware (automatic).

**Preconditions**: Request arrives with `Authorization: Bearer {token}`.

### Happy Path (Authorized)

1. Middleware extracts JWT from `Authorization` header
2. Verifies signature using `JWT_SECRET_KEY` (HS256) or public key (RS256)
3. Checks `exp` claim (reject if expired)
4. Extracts `sub` (user_id) and `role` claim
5. Casbin enforcer loads policy for that role
6. Enforce: `e.enforce(user_id, request.path, request.method)`
7. If `True` → forward to route handler

### Alternative: Superuser Bypass

- If JWT contains `is_superuser: True` → skip Casbin check, always allow
- Logged as `AUTH_SUPERUSER_ACCESS`

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| No Authorization header | `AUTH_MISSING_TOKEN` | 401 |
| Invalid signature | `AUTH_TOKEN_INVALID` | 401 |
| Expired token | `AUTH_TOKEN_EXPIRED` | 401 |
| Permission denied | `AUTH_FORBIDDEN` | 403 |

### Casbin Matcher

```
m = g(r.sub, p.sub) && keyMatch(r.obj, p.obj) && regexMatch(r.act, p.act)
```

Where:
- `r.sub` = user_id (mapped through g to role)
- `r.obj` = request path (e.g. `/api/v1/gl/entries`)
- `r.act` = HTTP method mapped to action (GET→read, POST→create, PUT→update, DELETE→delete)

### Action Mapping

| HTTP Method | Permission Action |
|-------------|-------------------|
| GET | read |
| POST | create |
| PUT | update |
| PATCH | update |
| DELETE | delete |

Special actions (from query param or route suffix):
- `/approve` → approve
- `/export` → export
- `/import` → import
- `/post` → post
- `/close` → close
- `/submit` → submit

---

## UC-AUTH-06: Role Management

**Goal**: CRUD for roles.

**Actor**: Admin.

**Preconditions**: Authenticated with `auth:role:*` permission.

### Happy Path (Create)

1. Admin submits `{name, display_name, description, permission_ids}`
2. System validates: name is unique, display_name not empty
3. System creates Role record
4. System assigns permissions via `role_permissions`
5. Casbin policy updated: `p, {role_name}, ...` entries added
6. Log `AUTH_ROLE_CREATED`
7. Return 201

### Alternative: System Roles Read-Only

- Attempting to update/delete roles with `is_system=True`
- Return `AUTH_SYSTEM_ROLE` (422)

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Duplicate role name | `AUTH_ROLE_EXISTS` | 409 |
| Delete role with assigned users | `AUTH_ROLE_IN_USE` | 409 |
| Permission not found | `AUTH_PERMISSION_NOT_FOUND` | 404 |

---

## UC-AUTH-07: Permission Management

**Goal**: View available permissions.

**Actor**: Admin.

**Preconditions**: Authenticated with `auth:permission:read`.

### Happy Path

1. Admin requests `GET /auth/permissions`
2. System returns all permissions grouped by resource
3. Each permission: `{id, resource, action, description}`

### Note

Permissions are **system-defined and seeded** — not user-creatable. New permissions require code changes (seed migration).

### Default Permission Resources

| Resource Pattern | Description |
|-----------------|-------------|
| `auth:user:*` | User management |
| `auth:role:*` | Role management |
| `auth:permission:*` | Permission read |
| `auth:audit:*` | Audit log read |
| `coa:account:*` | COA accounts |
| `coa:mapping:*` | IFRS mappings |
| `gl:entry:*` | Journal entries |
| `gl:period:*` | Fiscal periods |
| `tax:declaration:*` | Tax declarations |
| `tax:payment:*` | Tax payments |
| `cash:receipt:*` | Cash receipts |
| `cash:payment:*` | Cash payments |
| `ar:invoice:*` | AR invoices |
| `ap:invoice:*` | AP invoices |
| `inv:item:*` | Inventory items |
| `fa:asset:*` | Fixed assets |
| `payroll:run:*` | Payroll runs |
| `fs:statement:*` | Financial statements |
| `budget:plan:*` | Budget plans |
| `trs:investment:*` | Treasury investments |
| `report:*` | Reports |

---

## UC-AUTH-08: Password Change

**Goal**: User changes own password.

**Actor**: Authenticated user.

**Preconditions**: User is logged in.

### Happy Path

1. User sends `{current_password, new_password}`
2. System verifies `current_password` against stored hash
3. System checks `new_password` meets strength requirements
4. System checks `new_password` not in last 5 passwords history
5. System hashes `new_password`
6. System updates `password_hash`, sets `must_change_password=False`
7. System revokes all sessions except current
8. System logs `AUTH_PASSWORD_CHANGE`
9. Return success

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Wrong current password | `AUTH_INVALID_CREDENTIALS` | 401 |
| Weak new password | `AUTH_WEAK_PASSWORD` | 422 |
| Same as current | `AUTH_PASSWORD_SAME` | 422 |
| Used recently (history) | `AUTH_PASSWORD_USED` | 422 |

---

## UC-AUTH-09: Forgot / Reset Password

**Goal**: Allow user to reset forgotten password via email.

**Actor**: Unauthenticated user.

### Happy Path (Forgot)

1. User submits `{email}`
2. System checks email exists (always return 200 to prevent enumeration)
3. System generates reset_token: `secrets.token_urlsafe(48)`
4. System stores `sha256(reset_token)` in `password_reset_tokens` with 15 min expiry
5. System sends email with link: `https://.../reset-password?token={reset_token}`
6. Return `{message: "If email exists, reset link sent"}`

### Happy Path (Reset)

1. User submits `{token, new_password}`
2. System computes `sha256(token)`, looks up in `password_reset_tokens`
3. System checks: not expired, not used
4. System verifies `new_password` strength
5. System updates password_hash
6. System marks token as used, revokes all user sessions
7. Log `AUTH_PASSWORD_RESET`
8. Return success

### Exception Paths (Forgot)

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Email not found | (always return 200) | 200 |

### Exception Paths (Reset)

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Token expired | `AUTH_RESET_TOKEN_EXPIRED` | 401 |
| Token used | `AUTH_RESET_TOKEN_USED` | 401 |
| Token invalid | `AUTH_TOKEN_INVALID` | 401 |
| Weak password | `AUTH_WEAK_PASSWORD` | 422 |

---

## UC-AUTH-10: Account Lock/Unlock

**Goal**: Manually lock or unlock user account.

**Actor**: Admin.

**Preconditions**: Authenticated with `auth:user:lock` or `auth:user:unlock`.

### Happy Path (Lock)

1. Admin sends `PUT /auth/users/{id}/lock {reason}`
2. System sets `is_active=False`
3. System revokes all user sessions
4. Log `AUTH_ACCOUNT_LOCK` with reason
5. Return success

### Happy Path (Unlock)

1. Admin sends `PUT /auth/users/{id}/unlock`
2. System sets `is_active=True`, `failed_login_attempts=0`, `locked_until=NULL`
3. Log `AUTH_ACCOUNT_UNLOCK`
4. Return success

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| User not found | `AUTH_USER_NOT_FOUND` | 404 |
| Cannot lock self | `AUTH_CANNOT_LOCK_SELF` | 422 |

---

## UC-AUTH-11: Session Management

**Goal**: View and manage active sessions.

**Actor**: Admin or user (own sessions).

### Happy Path (List)

1. User requests `GET /auth/sessions`
2. System returns active sessions: `{id, device_info, ip_address, created_at, is_current}`
3. Admin can query any user: `GET /auth/sessions?user_id={id}`

### Happy Path (Revoke)

1. User/admin sends `DELETE /auth/sessions/{id}`
2. System sets `revoked=True`
3. Log `AUTH_SESSION_REVOKE`
4. Return success

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Session not found | `AUTH_SESSION_NOT_FOUND` | 404 |
| Revoke non-own session (non-admin) | `AUTH_FORBIDDEN` | 403 |

---

## UC-AUTH-12: Audit Log

**Goal**: Query authentication audit trail.

**Actor**: Admin.

**Preconditions**: Authenticated with `auth:audit:read`.

### Happy Path

1. Admin requests `GET /auth/audit-log?user_id=&event_type=&from=&to=&limit=&offset=`
2. System filters, paginates, returns audit log entries
3. Each entry: `{id, user_id, username, event_type, ip_address, user_agent, details, created_at}`
4. Ordered by `created_at DESC`

### Exception Paths

| Condition | Error Code | HTTP |
|-----------|-----------|------|
| Invalid date range | `AUTH_INVALID_DATE_RANGE` | 422 |

### Audit Event Types

| Event | Trigger |
|-------|---------|
| `login_success` | Successful login |
| `login_failed` | Failed login attempt |
| `logout` | User logout |
| `token_refresh` | Token refreshed |
| `password_change` | Password changed |
| `password_reset` | Password reset via email |
| `account_lock` | Account locked (auto or manual) |
| `account_unlock` | Account unlocked |
| `session_revoke` | Session revoked |
| `role_change` | Role assigned/removed |
| `user_create` | User created |
| `user_update` | User updated |
| `user_delete` | User deleted |
