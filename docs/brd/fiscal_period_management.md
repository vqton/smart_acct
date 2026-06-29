# Fiscal Period Management — BRD

**Version**: 1.0  
**Date**: 2026-06-29  
**Author**: Agentic AI  
**Regulatory Basis**: Circular 133/2016/TT-BTC (SMEs), Circular 99/2025/TT-BTC (replacing 200/2014), Law on Accounting 88/2015/QH13, GDT requirements

---

## 1. Executive Summary

Fiscal Period Management controls the accounting period lifecycle: open, close, reopen, carry-forward, and audit trail. Period closure is the gateway to financial statement generation and tax declaration submission. Vietnamese law requires that once a period is closed, no further postings are permitted without a formal reopening with audit trail.

Current implementation has basic close/reopen/list/is_closed functionality but lacks period-gated posting (just fixed), period type metadata, audit trail, auto-creation, carry-forward, and closing process automation.

---

## 2. Use Cases

### UC-FP-01: Open / Create Period

| Field | Value |
|-------|-------|
| **Actor** | System (auto) / Admin (manual) |
| **Trigger** | First journal entry referencing a new YYYY-MM period; or admin explicitly opens a new fiscal year |
| **Preconditions** | Period does not already exist |
| **Postconditions** | Period record created with `is_closed = false`, `type = monthly`, date range computed |

**Happy Path**:
1. Actor issues POST `/periods` with `{period, type, start_date, end_date?}`
2. System validates format, uniqueness, no overlap with existing periods
3. System creates `AccountingPeriodModel` record, returns 201

**Alternatives**:
- **Auto-create on first entry**: If `create_entry` references a period that doesn't exist, auto-create it as open (default: monthly, YYYY-MM date range). This is how most Vietnamese ERPs work.

**Validation Rules**:
- Period format: `YYYY-MM` for monthly, `YYYY-Q1/Q2/Q3/Q4` for quarterly, `YYYY` for yearly
- First period in entity: min 3 months, max 15 months (Law on Accounting 88/2015 Art 12)
- Final period: from fiscal year start to dissolution date
- No date overlap between periods of same type

### UC-FP-02: Close Period

| Field | Value |
|-------|-------|
| **Actor** | Chief Accountant / Admin |
| **Trigger** | End of accounting period; all entries posted and verified |
| **Preconditions** | Period is open; all entries in period are posted (default) or all entries are at minimum balanced |
| **Postconditions** | Period marked `is_closed = true`; no new/posted entries permitted; audit record created |

**Happy Path**:
1. Actor calls `POST /periods/{period}/close` with `{closed_by, notes?}`
2. System validates: all entries in period are posted (configurable)
3. System verifies: no orphan/unbalanced entries in period
4. System marks period closed, records `closed_by`, `closed_at`, `notes`
5. Audit log entry created: `PERIOD_CLOSE {period} by {user} at {timestamp}`
6. Returns 200 with period status

**Alternatives**:
- **Force close**: Admin can force-close with `force: true` to skip validation checks (audit-logged separately)
- **Close with unposted entries**: Some Vietnamese ERPs allow closing with unposted drafts if they are flagged as `non-material`. Configurable via `allow_unposted_on_close: bool`

**Validation Rules**:
- Cannot close an already-closed period
- (Configurable) All entries must be posted before close
- Financial statements should be generated before close (soft warning)

### UC-FP-03: Reopen Period

| Field | Value |
|-------|-------|
| **Actor** | Chief Accountant / Admin |
| **Trigger** | Error discovered in closed period requiring correction |
| **Preconditions** | Period is closed; next period(s) may need adjustment |
| **Postconditions** | Period marked `is_closed = false`; audit record created; downstream periods flagged as `needs_reconciliation` |

**Happy Path**:
1. Actor calls `POST /periods/{period}/reopen` with `{reason}`
2. System validates period is closed
3. System checks: no tax declarations submitted for this period (if linked) — hard block
4. System marks period open, clears `closed_by`/`closed_at`
5. Audit log entry created: `PERIOD_REOPEN {period} by {user} at {timestamp} — {reason}`
6. Downstream periods marked `needs_reconciliation: true`
7. Returns 200

**Validation Rules**:
- Cannot reopen a period that has tax declarations in `submitted`/`accepted` state
- Reopen reason is mandatory (audit requirement)
- Downstream periods (all periods with start_date > reopened period's end_date) get flagged

### UC-FP-04: List / Query Periods

| Field | Value |
|-------|-------|
| **Actor** | Any authenticated user |
| **Trigger** | User views period calendar or financial statement selector |
| **Preconditions** | None |

**Happy Path**:
1. `GET /periods` returns all periods ordered by period desc
2. `GET /periods?status=open|closed` filters
3. `GET /periods/{period}` returns single period detail
4. Returns: `{id, period, type, start_date, end_date, is_closed, closed_by, closed_at, notes, is_current, has_entries}`

### UC-FP-05: Get Current Period

| Field | Value |
|-------|-------|
| **Actor** | Any authenticated user |
| **Trigger** | UI needs to set default period for new entries |
| **Preconditions** | None |

**Happy Path**:
1. `GET /periods/current` returns the current open period
2. If current month period is closed, returns the most recent open period
3. If all periods closed, returns 404

### UC-FP-06: Block Entry in Closed Period (Enforcement)

| Field | Value |
|-------|-------|
| **Actor** | System (automatic) |
| **Trigger** | Any `create_entry`, `post_entry`, `update_entry`, `delete_entry` targeting a closed period |
| **Preconditions** | Period exists and `is_closed = true` |
| **Postconditions** | Operation rejected with 400 error: "Period {period} is closed"

**VIP Coverage**: Already implemented in current codebase.  
Tested in: `test_create_entry_in_closed_period_fails`, `test_post_entry_in_closed_period_fails`, `test_update_entry_in_closed_period_fails`.

### UC-FP-07: Year-End Close Process

| Field | Value |
|-------|-------|
| **Actor** | Chief Accountant |
| **Trigger** | End of fiscal year (period = YYYY-12) |
| **Preconditions** | All 12 months are closed; all revenue/expense accounts are balanced |
| **Postconditions** | Revenue/expense accounts closed to retained earnings; balance sheet accounts carry forward; new fiscal year opened |

**Steps**:
1. Run closing entries:
   - Close revenue accounts (511, 512, 515, 521) → 911 (P/L summary)
   - Close expense accounts (632, 635, 641, 642) → 911
   - Close 911 → 421 (retained earnings)
2. Generate final financial statements
3. Lock period
4. Open next fiscal year period(s)
5. Carry forward balance sheet account balances

### UC-FP-08: Period Audit Trail

| Field | Value |
|-------|-------|
| **Actor** | Auditor / Admin |
| **Trigger** | Query period history |
| **Preconditions** | None |

**Happy Path**:
1. `GET /periods/{period}/audit-log` returns ordered list of events
2. Each event: `{event_type, timestamp, user, details}`
3. Event types: `PERIOD_CREATE`, `PERIOD_CLOSE`, `PERIOD_REOPEN`, `PERIOD_FORCE_CLOSE`, `PERIOD_CARRY_FORWARD`

---

## 3. Data Model

### AccountingPeriodModel (Current)

```python
class AccountingPeriodModel(Base):
    __tablename__ = "accounting_periods"
    id = Column(Integer, primary_key=True)
    period = Column(String(7), unique=True, nullable=False)  # YYYY-MM
    is_closed = Column(Boolean, default=False)
    closed_by = Column(String(100), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, onupdate=now)
```

### AccountingPeriodModel (Proposed)

```python
class PeriodType(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class AccountingPeriodModel(Base):
    __tablename__ = "accounting_periods"
    id = Column(Integer, primary_key=True)
    period = Column(String(10), unique=True, nullable=False)  # YYYY-MM, YYYY-Q1, or YYYY
    type = Column(SAEnum(PeriodType), default=PeriodType.MONTHLY, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_closed = Column(Boolean, default=False, nullable=False)
    closed_by = Column(String(100), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)
    is_current = Column(Boolean, default=False)
    needs_reconciliation = Column(Boolean, default=False)
    parent_period = Column(String(10), nullable=True)  # e.g., "2024" for "2024-01"
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, onupdate=now)
```

### PeriodAuditLogModel (New)

```python
class PeriodAuditLogModel(Base):
    __tablename__ = "period_audit_log"
    id = Column(Integer, primary_key=True)
    period = Column(String(10), nullable=False, index=True)
    event_type = Column(String(30), nullable=False)  # CREATE, CLOSE, REOPEN, FORCE_CLOSE
    user = Column(String(100), nullable=False)
    details = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=now)
```

---

## 4. API Endpoints

| Method | Endpoint | UC | Status |
|--------|----------|----|--------|
| `POST` | `/api/v1/periods` | UC-FP-01 | Missing |
| `GET` | `/api/v1/periods` | UC-FP-04 | Done |
| `GET` | `/api/v1/periods/current` | UC-FP-05 | Missing |
| `GET` | `/api/v1/periods/{period}` | UC-FP-04 | Done |
| `POST` | `/api/v1/periods/{period}/close` | UC-FP-02 | Done |
| `POST` | `/api/v1/periods/{period}/reopen` | UC-FP-03 | Done |
| `GET` | `/api/v1/periods/{period}/audit-log` | UC-FP-08 | Missing |
| `POST` | `/api/v1/periods/{period}/carry-forward` | UC-FP-07 | Missing |

---

## 5. Gap Analysis (Current vs PROD)

| # | Feature | Status | Priority |
|---|---------|--------|----------|
| 1 | Period-gated posting (create/post/update blocked in closed period) | **IMPLEMENTED** | P0 |
| 2 | Period type field (monthly/quarterly/yearly) | Missing | P1 |
| 3 | Date range (start_date/end_date) | Missing | P1 |
| 4 | Period auto-creation on first reference | Missing | P1 |
| 5 | Period audit trail table + API | Missing | P1 |
| 6 | GET /periods/current endpoint | Missing | P1 |
| 7 | POST /periods create endpoint | Missing | P2 |
| 8 | Year-end close process (carry-forward) | Missing | P2 |
| 9 | Hierarchy (parent_period for quarter/year rollup) | Missing | P2 |
| 10 | Tax declaration linkage (block close if tax submitted) | Missing | P2 |
| 11 | Closing checklist (depreciation, accruals, etc.) | Missing | P3 |
| 12 | Graceful first/last period handling (min 3mo, max 15mo) | Missing | P3 |

---

## 6. Implementation Plan

### Slice 1 (Current — DONE)
- ✅ Period-gated posting: block create/post/update entries in closed periods
- ✅ Tests: 3 new integration tests in `TestPeriodClose`

### Slice 2 (Next)
- Add `PeriodType` enum, `start_date`, `end_date`, `is_current`, `needs_reconciliation`, `parent_period` to `AccountingPeriodModel`
- Migration: add columns to `accounting_periods`
- Auto-compute date range from period string on create

### Slice 3 (Next)
- `/periods/current` endpoint — returns current open period
- Auto-create period on first entry reference (in `create_entry`)
- `PeriodAuditLogModel` + audit trail on close/reopen

### Slice 4 (Next)
- `POST /periods` explicit create
- `GET /periods/{period}/audit-log`
- `POST /periods/{period}/carry-forward`
- Year-end closing entries automation

---

## 7. References

- Circular 133/2016/TT-BTC: SMEs accounting regime
- Circular 99/2025/TT-BTC: replaces Circular 200/2014/TT-BTC, effective Jan 1 2026
- Law on Accounting 88/2015/QH13 Art 12: Fiscal period definition
- GDT requirements: single accounting system, no dual books
- Big4 Vietnam close process: EY FAAS, Deloitte Vietnam, KPMG Vietnam, PwC Vietnam
