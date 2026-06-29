# AR Module — Implementation Roadmap & Execution Plan

**Project:** SmartACCT ERP — Accounts Receivable  
**Prepared by:** Lead BA (20 yrs practice) + Chief Accountant (20k hrs)  
**Date:** 2026-06-29  
**Status:** APPROVED FOR EXECUTION  
**Estimated Duration:** 14 weeks (3.5 months)  
**Estimated Effort:** 77 story points (~11 dev-days × 2 devs)  
**Budget:** 1 senior dev (full-time) + 1 accountant (20% advisory)  

---

## 1. Roadmap Overview

```
WEEK 0    │ Setup
──────────┼─────────────────────────────────────────────────────
W1–3      │ Phase 1: Foundation (DB + Domain + Repository)
W4–7      │ Phase 2: Core AR (Customer + Invoice + Payment + GDT)
W8–10     │ Phase 3: Collections (Dunning + Provisions + Write-off)
W11–12    │ Phase 4: Polish (i18n + credit + IFRS 15)
W13–14    │ Phase 5: Reporting (Balance + CEI/DSO + Statements)  ← v1.0 GO-LIVE
──────────┼─────────────────────────────────────────────────────
W15–18+   │ Phase 6: Advanced (IFRS 9 ECL, Netting, Multi-currency) ← v2.0
```

**Go-Live Criteria (end of W14):**
- [ ] All P0 (UC-AR-01/02/03/04/05) + P1 (UC-AR-06/07/08/09/10/11) use cases live
- [ ] 379 existing tests green + 40+ new AR tests green
- [ ] GDT auto-submit verified on production credentials
- [ ] Regional accountant sign-off on TK 131/511/333/630 posting
- [ ] Vietnamese + English i18n complete

---

## 2. Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ARInvoice vs EInvoice | **Separate tables, linked by FK** | EInvoice = legal tax document (GDT format); ARInvoice = financial ledger (our posting logic). Linked via `ar_invoice.einvoice_id`. Allows AR logic without depending on GDT state. |
| Customer Master | **New table** `customers` | No existing customer entity. Critical for AR, credit, tax-code validation. Isolated for reuse by AP (future). |
| Aging calculation | **Computed on-read** for `GET /ar/aging`; **snapshot table** for month-end | Live query = accurate real-time. Snapshot = historical consistency + BCTC lock. Both needed. |
| Dunning | **Cron-driven state machine** (APScheduler) | Predictable; auditable; supports both automatic + manual advance. |
| Payment allocation | **FIFO default**, overrideable | Vietnamese practice: oldest debt first. Allows specific allocation if customer requests. |
| Provision timing | **Year-end + on-demand** (CFO trigger) | Not per-transaction. Matches VAS year-end close cycle. |
| GL posting | **Sync within same DB transaction** as AR action | Double-entry must be atomic with AR. If GL fails → AR fails. |
| GDT submit | **Async with retry** (3×, backoff) | NĐ70/2025 submission can be slow. Don't block user. Mark ERROR if all retries fail. |
| IFRS 9 | **Optional tier** (flag in config) | Only for IFRS-reporting enterprises. Default off. No overhead for VAS-only firms. |

---

## 3. Execution Plan — Phase by Phase

### Phase 1: Foundation (Weeks 1–3)

**Goal:** Database schema + domain entities + repository. No API yet.  
**Parallelizable:** Tasks marked (P) can run in parallel.

#### T1.1 — Domain Entities (W1) [P]
- **Scope:** M — 1 file
- **File:** `domain/ar.py`
- **Entities (8):** `Customer`, `ARInvoice`, `ARInvoiceLine`, `ARPayment`, `ARPaymentAllocation`, `ARDunningLog`, `BadDebtProvision`, `AR AgingSnapshot`
- **Behavior:** Pure Pydantic v2. No DB imports. Validators for tax_code, credit_limit, payment_terms, invoice_number uniqueness per customer. Computed fields: `days_past_due`, `balance_due`, `aging_bucket`.
- **Acceptance:**
  - [ ] `domain/ar.py` imports without errors
  - [ ] All 8 entities instantiate with valid data
  - [ ] Validators reject: invalid tax_code, negative credit_limit, past due_date
  - [ ] `ARInvoice.balance_due` computed correctly from lines + payments (manual compute test)
- **Verify:** `.venv/bin/python -c "from domain.ar import Customer, ARInvoice; print('OK')"` → passes
- **Tests:** `tests/test_ar_domain.py` — 15 tests (validator + computed fields)

#### T1.2 — SQLAlchemy Models (W1) [P]
- **Scope:** M — 1 file + 1 migration
- **File:** `infrastructure/models/ar_models.py`
- **Models (8):** `CustomerModel`, `ARInvoiceModel`, `ARInvoiceLineModel`, `ARPaymentModel`, `ARPaymentAllocationModel`, `ARDunningLogModel`, `BadDebtProvisionModel`, `AR AgingSnapshotModel`
- **Relationships:** Customer 1→N ARInvoice; ARInvoice 1→N ARInvoiceLine; ARInvoice 1→N ARPaymentAllocation; ARPayment 1→N ARPaymentAllocation; ARInvoice 1→N ARDunningLog; Customer/ARInvoice FK to BadDebtProvision.
- **Acceptance:**
  - [ ] All models importable
  - [ ] DB roundtrip: insert + query for each model
  - [ ] FK constraints verified (cannot insert ARInvoice without valid customer_id)
  - [ ] UNIQUE(Customer.tax_code) enforced at DB level
- **Verify:** `.venv/bin/pytest tests/test_ar_models.py -v` → green
- **Tests:** `tests/test_ar_models.py` — 20 tests (CRUD + constraints)

#### T1.3 — Alembic Migration (W2)
- **Scope:** S — 1 file
- **File:** `migrations/versions/XXXX_ar_tables.py`
- **Content:** `CREATE TABLE customers (...)`, `CREATE TABLE ar_invoices (...)`, etc. 8 tables. Proper indexes: `customer_id`, `due_date`, `status`, `dunning_level`.
- **Acceptance:**
  - [ ] `alembic upgrade head` runs without error
  - [ ] All 8 tables exist in PostgreSQL
  - [ ] Indexes verified: `EXPLAIN ANALYZE` on aging query uses index
  - [ ] Downgrade (`alembic downgrade -1`) drops tables cleanly
- **Verify:** `psql -c "\dt"` → all 8 AR tables present
- **Dependency:** T1.2 must pass before migration written

#### T1.4 — AR Repository (W2–W3)
- **Scope:** L — 1 file, ~15 methods
- **File:** `infrastructure/repositories/ar_repository.py`
- **Methods:** CRUD for Customer, ARInvoice, ARPayment, ARDunningLog, BadDebtProvision, ARAgingSnapshot + specialized queries: `get_customer_balance()`, `get_aging_report(customer_id, period)`, `get_dunning_queue()`, `calculate_provisions(period)`.
- **Acceptance:**
  - [ ] All 15 repo methods unit-tested with in-memory SQLite or test Postgres
  - [ ] `get_aging_report` returns correct buckets for synthetic data
  - [ ] `calculate_provisions` applies Circular 200/2014 rates correctly
  - [ ] `get_dunning_queue` filters correctly by due_date and dunning_level
- **Verify:** `.venv/bin/pytest tests/test_ar_repository.py -v` → green
- **Tests:** `tests/test_ar_repository.py` — 25 tests

#### T1.5 — AR Use Cases (W3)
- **Scope:** M — 1 file (or subpackage if >1000 LOC)
- **File:** `use_cases/ar/__init__.py` (ARUseCases class)
- **Methods (15):** `create_customer`, `list_customers`, `get_customer`, `update_customer`, `deactivate_customer`, `create_invoice`, `send_invoice`, `get_invoice`, `list_invoices`, `allocate_payment`, `get_aging_report`, `generate_aging_snapshot`, `advance_dunning`, `create_provision`, `write_off_bad_debt`.
- **Acceptance:**
  - [ ] All 15 methods defined with correct signatures
  - [ ] Each returns `Result[T]` (Success/Failure pattern per existing codebase)
  - [ ] GL posting wired into `create_invoice` and `allocate_payment` (mock GL for now)
  - [ ] Period gating enforced (reject if AccountingPeriod is CLOSED)
- **Verify:** `.venv/bin/pytest tests/test_ar_use_cases.py -v` → green
- **Tests:** `tests/test_ar_use_cases.py` — 30 tests (1 per use case + edge cases)

**Phase 1 Checkpoint:**
- [ ] All 8 tables migrated
- [ ] 70+ tests pass (domain 15 + models 20 + repo 25 + use cases 30)
- [ ] `from use_cases.ar import ARUseCases` works
- [ ] Demo: create customer + invoice in Python REPL

---

### Phase 2: Core AR (Weeks 4–7)

**Goal:** Customer + Invoice + Payment API endpoints. End-to-end flow works. GDT integration.  
**Sequential:** Build in dependency order. T2.1 → T2.2 → T2.3 → T2.4 → T2.5 + T2.6 (parallel) → T2.7.

#### T2.1 — Customer Routes (W4)
- **Scope:** M — 2 files
- **Files:** `presentation/ar/__init__.py` (creates `ar_bp`, imports submodules), `presentation/ar/customers.py`
- **Endpoints (5):**
  - `POST /ar/customers` — create (tax_code validated, duplicate check)
  - `GET /ar/customers` — list/search (?q, ?tax_code, ?is_active)
  - `GET /ar/customers/{id}` — detail
  - `PUT /ar/customers/{id}` — update (credit_limit, terms, override_reason)
  - `DELETE /ar/customers/{id}` — deactivate (BLOCK if open AR: ALT-AR-11)
- **Acceptance:**
  - [ ] All 5 endpoints return correct HTTP status codes
  - [ ] POST /ar/customers validates tax_code (10-13 digits, no leading 0) → 400 if bad
  - [ ] POST with duplicate tax_code → 409
  - [ ] DELETE with open invoices → 409 + CUSTOMER_HAS_OPEN_AR
  - [ ] i18n error messages resolve (vi + en)
- **Verify:** `curl -X POST http://localhost:5000/api/v1/ar/customers -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"tax_code":"0123456789","name":"Test","credit_limit":100000000}'` → 201
- **Tests:** 10 route tests in `tests/test_ar_routes.py`

#### T2.2 — Invoice Routes (W4–W5)
- **Scope:** L — 2 files
- **Files:** `presentation/ar/invoices.py` (create, list, get, send, void), `presentation/ar/invoice_lines.py` (add line, remove line)
- **Endpoints (6):**
  - `POST /ar/invoices` — create DRAFT (validates customer, credit limit, period)
  - `GET /ar/invoices` — list (filters: customer_id, status, from_date, to_date, overdue)
  - `GET /ar/invoices/{id}` — detail
  - `PUT /ar/invoices/{id}` — update DRAFT only (items, customer_id — limited fields)
  - `POST /ar/invoices/{id}/send` — transition DRAFT→SENT + GDT submit + GL post
  - `POST /ar/invoices/{id}/void` — cancel DRAFT
- **Acceptance:**
  - [ ] POST with credit_limit exceeded → 422 + CREDIT_LIMIT_EXCEEDED
  - [ ] POST in CLOSED period → 403 + PERIOD_CLOSED
  - [ ] POST /send → creates EInvoice, signs, submits to GDT stub, posts GL, status → SENT
  - [ ] POST /send with GDT rejection → status → ERROR, retry logged, notification queued
  - [ ] PUT on SENT invoice → 400 (cannot modify sent invoice)
  - [ ] Void on SENT invoice → 400 (must use write-off flow)
- **Verify:** End-to-end: POST customer → POST invoice → POST /send → GL entry exists in DB → EInvoice.status = SENT
- **Tests:** 15 route tests

#### T2.3 — Payment Routes (W5)
- **Scope:** M — 1 file
- **File:** `presentation/ar/payments.py`
- **Endpoints (3):**
  - `POST /ar/payments` — record + FIFO allocate
  - `GET /ar/payments` — list (filter: customer_id, date_from, date_to)
  - `GET /ar/payments/{id}` — detail
- **Acceptance:**
  - [ ] Payment auto-allocates to oldest open invoice (FIFO)
  - [ ] Partial payment → status PARTIALLY_PAID, balance_due reduced
  - [ ] Full payment → status PAID, balance_due = 0
  - [ ] Overpayment → amount_unapplied > 0, refund notice generated
  - [ ] GL posted: Dr TK111 / Cr TK131 per allocation
  - [ ] Payment in CLOSED period → 403 + PERIOD_CLOSED
- **Verify:** Create 2 invoices (100m + 50m), pay 120m → first invoice PAID (100m), second PARTIALLY_PAID (20m allocated, 30m remaining), unapplied = 0
- **Tests:** 8 route tests

#### T2.4 — Wire GDT Auto-Submit (W5) [P with T2.2]
- **Scope:** S — modify `use_cases/ar/__init__.py` + `services/gdt_client.py`
- **Behavior:** In `send_invoice()`:
  1. Call `SigningService.sign(einvoice)` — actual RSA sign (already stubbed)
  2. Call `GDTClient.submit_invoice(signed)` — 3 retries with backoff
  3. On success: persist `verification_code`, `gdt_transaction_id`
  4. On failure: mark EInvoice.status = ERROR, notify Sales Accountant
- **Acceptance:**
  - [ ] Success path: EInvoice.status = SENT, verification_code stored
  - [ ] Failure path: after 3 retries, status = ERROR
  - [ ] Idempotency: re-calling send on already-SENT is no-op (return current state)
- **Verify:** Integration test with mocked GDTClient (no real API call)

#### T2.5 — Aging Engine (Live) (W6)
- **Scope:** M — 1 endpoint + 1 repo method
- **File:** add `get_aging_report()` to repo + route in `presentation/ar/aging.py`
- **Endpoint:** `GET /ar/aging?customer_id=&period=`
- **Acceptance:**
  - [ ] Returns 6 buckets per customer (0/1-30/31-60/61-90/91-180/181-365/365+)
  - [ ] Buckets match BR-AR-03 rules
  - [ ] Totals sum exactly to total_outstanding
  - [ ] Without period → use current GL period
  - [ ] Performance: 10k invoices → < 2s
- **Verify:** Load test with 10k synthetic invoices → query < 2s
- **Tests:** 5 tests

#### T2.6 — Aging Snapshot (Period-Locked) (W6) [Parallel with T2.5]
- **Scope:** M — 2 endpoints + 1 repo method
- **File:** add to `presentation/ar/aging.py`
- **Endpoints:**
  - `POST /ar/aging/snapshot?period=YYYY-MM` — generate (requires CLOSED period)
  - `GET /ar/aging/snapshots` — list
  - `GET /ar/aging/snapshots/{id}` — detail
- **Acceptance:**
  - [ ] POST with OPEN period → 409 + PERIOD_NOT_CLOSED
  - [ ] POST with closed period → creates snapshot, locks it
  - [ ] Second POST for same period → 409 + SNAPSHOT_ALREADY_EXISTS
  - [ ] Snapshot totals match GL TK 131 balance
- **Verify:** Create 10 invoices, close period, snapshot → totals match GL query
- **Tests:** 5 tests

#### T2.7 — GL Auto-Posting Verification (W7)
- **Scope:** S — verification + test
- **Behavior:** Audit all GL postings from T2.2, T2.3, T2.5
  - ARInvoice.create → Dr 131 / Cr 511 / Cr 3331
  - ARPayment.allocate → Dr 111 / Cr 131
- **Acceptance:**
  - [ ] Journal entries balanced (sum(Dr) = sum(Cr) within 0.001 tolerance)
  - [ ] Entries reference `source_module = "AR"`, `created_by` = user_id
  - [ ] Rollback on GL failure → AR transaction rolled back (atomic)
  - [ ] All GL postings have period check (reject if CLOSED)
- **Verify:** Manual test: create invoice + payment → verify GL entries in DB
- **Tests:** 5 integration tests

**Phase 2 Checkpoint:**
- [ ] End-to-end happy path works: create customer → create invoice → send to GDT → receive payment → verify GL
- [ ] 30+ new tests pass (customers 10 + invoices 15 + payments 8 + GL posting 5)
- [ ] Aging report live + snapshot for sample period
- [ ] GDT mocked integration verified

---

### Phase 3: Collections & Provisions (Weeks 8–10)

**Goal:** Dunning engine, daily cron, bad debt provisions, write-off approvals.

#### T3.1 — Dunning State Machine (W8)
- **Scope:** M — 1 repo method + 1 use case + 2 endpoints
- **File:** add to repo: `get_dunning_queue()`, `advance_dunning_level()`; add to use_cases; add `presentation/ar/dunning.py`
- **Endpoints:**
  - `POST /ar/invoices/{id}/dunning` — advance one level (manual)
  - `GET /ar/dunning` — list all overdue with dunning status
  - `GET /ar/dunning/queue` — priority queue (days_past_due DESC)
- **Acceptance:**
  - [ ] Invoice 5 days overdue → L1; 12 days → L2; 35 days → L3; 65 days → L4; 95 days → L5
  - [ ] Cannot advance past L5 (max)
  - [ ] Each advance creates ARDunningLog record
  - [ ] Notification method field set per level (email/SMS/letter/legal/external)
- **Verify:** Create invoice with due_date = today - 12 → manual advance → L2 logged
- **Tests:** 8 tests

#### T3.2 — Dunning Scheduler Job (W8)
- **Scope:** S — cron registration
- **File:** modify `run.py` (already has APScheduler wired)
- **Behavior:** Register `daily_dunning_job` — runs 08:00 VN time:
  1. Query open overdue invoices
  2. Advance dunning_level if threshold crossed
  3. Execute notification stub per level
  4. Log each action
  5. Alert CFO if any invoice enters L5
- **Acceptance:**
  - [ ] Job registered on app startup
  - [ ] Manual trigger works (`POST /admin/scheduler/dunning/trigger`)
  - [ ] Idempotent: re-running same day does not double-advance
  - [ ] CFO email alert queued for L5 invoices
- **Verify:** Manually trigger in dev → check ARDunningLog + logs
- **Tests:** 3 tests (mock scheduler)

#### T3.3 — TK 630 Provisions (W9)
- **Scope:** M — 1 use case + 2 endpoints
- **File:** add `create_provisions(period)` to use_cases + routes
- **Endpoints:**
  - `POST /ar/bad-debt/provisions?period=` — batch calculate
  - `GET /ar/bad-debt/provisions?period=&customer_id=` — list
- **Acceptance:**
  - [ ] Invoice 100 days overdue → 5% provision
  - [ ] Invoice 200 days overdue → 20% provision
  - [ ] Invoice 400 days overdue → 50% provision
  - [ ] Provisions sum per customer; BadDebtProvision rows created
  - [ ] Idempotent: re-run for same period does not duplicate
- **Verify:** Create 10 invoices across buckets, run provision → verify rates
- **Tests:** 8 tests

#### T3.4 — Write-Off Approval (W9)
- **Scope:** M — 1 use case + 1 endpoint
- **File:** add `approve_write_off()` to use_cases + route
- **Endpoint:** `POST /ar/bad-debt/write-off` (requires CFO role via JWT)
- **Acceptance:**
  - [ ] Invoice > 6mo overdue + dunning L5 + provision exists → success
  - [ ] Invoice < 6mo overdue → 422 + WRITE_OFF_PERIOD_NOT_MET
  - [ ] Non-CFO JWT → 403 + INSUFFICIENT_PERMISSIONS
  - [ ] Success: GL Dr TK630 / Cr TK131 + status → WRITTEN_OFF + audit log
  - [ ] Recovery path (ALT-AR-10): Dr 131 / Cr 631 (NOT reverse provision)
- **Verify:** CFO approves write-off → check GL entries + status + log
- **Tests:** 7 tests

#### T3.5 — ECL Calculator (IFRS 9) (W10) [Optional tier]
- **Scope:** M — 1 use case + 1 endpoint
- **Endpoint:** `GET /ar/reports/ecl?period=&customer_id=`
- **Acceptance:**
  - [ ] Stage 1 (current, no SICR) → 12-month ECL
  - [ ] Stage 2 (31-90 days OR SICR flag) → lifetime ECL
  - [ ] Stage 3 (>90 days) → lifetime ECL, net of interest
  - [ ] Returns total ECL + per-customer breakdown + stage count
  - [ ] Only active when config `IFRS_ENABLED = true`
- **Verify:** Synthetic data across 3 stages → ECL numbers match hand calculation
- **Tests:** 6 tests

**Phase 3 Checkpoint:**
- [ ] Dunning cron runs daily in dev
- [ ] All 5 dunning levels work end-to-end
- [ ] Provision calculator matches Circular 200/2014 rates
- [ ] Write-off creates correct GL entries (Dr 630 / Cr 131)
- [ ] 25+ new tests pass

---

### Phase 4: Polish & Compliance (Weeks 11–12)

**Goal:** i18n, credit limit enforcement, IFRS 15, edge cases, documentation.

#### T4.1 — i18n AR Error Codes (W11)
- **Scope:** M — update domain + templates + translations
- **Files:** `domain/i18n.py` (add 50+ AR error codes), `translations/vi/LC_MESSAGES/messages.po`, `translations/en/LC_MESSAGES/messages.po`
- **Error codes to add (30 minimum):** `CUSTOMER_TAX_CODE_INVALID`, `CUSTOMER_CODE_DUPLICATE`, `CREDIT_LIMIT_EXCEEDED`, `CUSTOMER_HAS_OPEN_AR`, `AR_INVOICE_NOT_FOUND`, `AR_PAYMENT_NOT_FOUND`, `PERIOD_CLOSED`, `PERIOD_NOT_CLOSED`, `DUNNING_MAX_LEVEL_REACHED`, `PROVISION_PERIOD_NOT_MET`, `WRITE_OFF_PERIOD_NOT_MET`, `INSUFFICIENT_PERMISSIONS`, `EINVOICE_ALREADY_SUBMITTED`, `GDT_SUBMISSION_FAILED`, `OVERPAYMENT_DETECTED`, `ALLOCATION_INVALID`, etc.
- **Acceptance:**
  - [ ] All error codes resolve via `resolve_error()` in vi + en
  - [ ] Jinja2 templates (`reconciliation_report.html`, new AR templates) use `{% trans %}`
  - [ ] API returns localized error: `{"error": "Mã số thuế không hợp lệ"}` for Vietnamese locale
- **Verify:** Set `?lang=en` → English errors; `?lang=vi` → Vietnamese errors; no `?lang=` → Vietnamese default
- **Tests:** 5 i18n tests

#### T4.2 — Credit Limit Enforcement (W11)
- **Scope:** S — add to invoice creation flow
- **Behavior:** In `create_invoice()`:
  - Compute `total_exposure = customer.outstanding_balance + new_total`
  - If > 80%: log WARN, add response header `X-AR-Credit-Utilization: 85%`
  - If >= 100%: REJECT 422
  - CFO override: `customer.credit_limit_override = true` + `override_reason` + auto-expire 30 days
- **Acceptance:**
  - [ ] Credit limit at 80% → warning, invoice created
  - [ ] Credit limit at 100% → 422 rejection
  - [ ] CFO override → bypasses check for 30 days
  - [ ] Override auto-expires
- **Tests:** 5 tests

#### T4.3 — IFRS 15 Contract Asset Distinction (W12)
- **Scope:** S — computed field on ARInvoice
- **Behavior:**
  - If EInvoice.status = SENT but ARInvoice.status = DRAFT → this is Contract Asset (performance done, not yet invoiced)
  - Add computed field `ARInvoice.is_contract_asset`
  - Expose in API response
- **Acceptance:**
  - [ ] Contract asset invoices appear in separate report view
  - [ ] Once sent → transferred from contract asset to AR
  - [ ] IFRS disclosure note generated: "Contract assets at period end: X VND"
- **Tests:** 3 tests

#### T4.4 — QA Sprint + Bug Fix (W12)
- **Scope:** M — testing + fixes
- **Actions:**
  - [ ] Run all 379 existing tests → confirm green
  - [ ] Run all 40+ new AR tests → green
  - [ ] Load test: 10k invoices → aging < 2s
  - [ ] Load test: 1k dunning → cron < 1 min
  - [ ] End-to-end scenario: create 5 customers → 50 invoices → 30 payments → aging → dunning → provision → write-off
  - [ ] Vietnamese accountant review: posting logic matches TT99/2025 textbook (ketoanleanh.edu.vn standard)
  - [ ] Fix all bugs found; no critical bugs at end of W12

**Phase 4 Checkpoint:**
- [ ] 40+ AR tests green + 379 existing tests green
- [ ] i18n complete (vi/en)
- [ ] Credit limit enforcement tested
- [ ] Accountant sign-off on TK posting patterns
- [ ] Go/No-Go decision for Phase 5 (Reporting)

---

### Phase 5: Reporting (Weeks 13–14) — v1.0 Go-Live

**Goal:** AR-specific reports, KPI dashboards, customer statements, final polish.

#### T5.1 — AR Balance Report (W13)
- **Scope:** M — 1 endpoint
- **File:** `presentation/ar/reports.py`
- **Endpoint:** `GET /ar/reports/balance?customer_id=&period=`
- **Acceptance:**
  - [ ] Returns each customer's opening balance, invoices, payments, closing balance
  - [ ] Period-filtered; defaults to current period
  - [ ] Matches GL TK 131 balance (verified by accountant)
- **Tests:** 3 tests

#### T5.2 — Collection Effectiveness + DSO (W13)
- **Scope:** M — 1 endpoint
- **Endpoint:** `GET /ar/reports/collection-effectiveness?periods=`
- **Acceptance:**
  - [ ] CEI formula: (Beg_AR + Sales - End_AR - Bad_Debt) / (Beg_AR + Sales) × 100
  - [ ] DSO formula: (Average_AR / Total_Credit_Sales) × days_in_period
  - [ ] Returns time series per customer + portfolio totals
  - [ ] Flags if CEI < 90% or DSO > 45 days
- **Tests:** 4 tests

#### T5.3 — Customer AR Statement (W14)
- **Scope:** M — 1 endpoint + Jinja2 template
- **File:** `templates/ar_statement.html`
- **Endpoint:** `GET /ar/reports/statement/{customer_id}?format=json|html&period=`
- **Acceptance:**
  - [ ] JSON: structured statement data
  - [ ] HTML: Jinja2 template with `{% trans %}` i18n blocks
  - [ ] Shows: opening balance, invoice detail (date, number, due, amount, paid, balance), aging buckets, closing balance
  - [ ] Vietnamese locale: "Báo cáo công nợ khách hàng"
  - [ ] English locale: "Customer AR Statement"
- **Tests:** 3 tests

#### T5.4 — Year-End BCTC Disclosure (W14)
- **Scope:** M — 1 endpoint
- **Endpoint:** `GET /ar/reports/bctc-disclosure?period=`
- **Acceptance:**
  - [ ] Returns IFRS 7 disclosure blocks: AR aging, ECL, credit risk, maturity analysis
  - [ ] Returns VAS disclosure: TK 131 breakdown, TK 630 provision movement
  - [ ] JSON + PDF (via WeasyPrint)
  - [ ] Cross-references GL period close date
- **Tests:** 4 tests

**Phase 5 Checkpoint (v1.0 GO-LIVE):**
- [ ] All P0 + P1 use cases live + tested
- [ ] All 5 reports accurate (verified against manual calculations)
- [ ] 40+ AR tests green
- [ ] Accountant UAT sign-off
- [ ] Documentation: Vietnamese user guide (ketoanleanh.edu.vn standard)
- [ ] Deployment to production (staged: 1 dev → staging → prod)

---

## 4. Dependency Graph

```
T1.1 (domain/ar.py)
    ↓
T1.2 (models) ──────────┐
    ↓                    │
T1.3 (migration) ────────┤
    ↓                    │
T1.4 (repository) ───────┤
    ↓                    ↓
T1.5 (use cases) ────────┴──────→ T2.x (API routes)
                                         ↓
                                   T4.1 (i18n)
                                   T4.2 (credit limit)
                                         ↓
                                   T5.x (reports)
```

**Sequential (must wait):** T1.1 → T1.2 → T1.3 → T1.4 → T1.5 → T2.1+2.2 → T2.3+2.4 → T3.x → T5.x  
**Parallel windows:** T1.1 + nothing (only one domain file); T1.2 + T1.1 (models can start while domain finalizes); T2.5 + T2.6 (both use same data but independent endpoints); T4.1 + T4.2 (i18n + credit are independent).

---

## 5. Resource Plan

| Role | Allocated | Commitment | Activities |
|------|-----------|------------|------------|
| **Senior Backend Dev** | 1 FTE | W0–W14 (all phases) | Domain + models + repo + use cases + routes + GDT integration + i18n + reports |
| **Full-Stack Dev** | 1 FTE | W4–W14 (Phase 2 onward) | Routes + tests + templates + frontend API docs |
| **Chief Accountant** | 0.2 FTE | W1–W14 (advisory) | Validate TK posting, review BRD, UAT, BCTC sign-off |
| **DevOps** | 0.1 FTE | W1, W13 (migration deploy, prod deploy) | Run Alembic, deploy to staging, prod cutover |

**Capacity check:** 2 FTE devs × 14 weeks = 28 dev-weeks. Estimated at ~14 dev-weeks (77 SP / 5 SP per dev-week). **Buffer: 2 weeks** for unknowns (GDT sandbox delays, accountant review cycles, Big4 compliance questions).

---

## 6. Risk Register

| # | Risk | Prob | Impact | Mitigation | Owner |
|---|------|------|--------|------------|-------|
| R1 | GDT sandbox API unstable or different from prod | Med | High | Use contract tests + mock layer; only integrate against sandbox in W5; parse GDT docs for breaking changes | Dev |
| R2 | Accountant disputes TK posting logic | Med | High | Weekly sync with chief accountant; validate every posting rule against ketoanleanh.edu.vn + TT99/2025 wording | CFO + Dev |
| R3 | EInvoice entity split causes data inconsistency | Low | High | Strict FK: ARInvoice.einvoice_id nullable but immutable once set; reconciliation job daily | Dev |
| R4 | IFRS 9 ECL formula disagreement with auditor | Low | Med | Defer IFRS 9 to W10 (after core VAS stable); build as optional flag; get VACPA auditor sign-off | CFO + Auditor |
| R5 | Large dataset aging performance (>100k invoices) | Med | Med | Index on due_date + status + customer_id; materialized view option if needed | Dev |
| R6 | NĐ70 regulatory update mid-project | Low | High | Weekly check of gdt.gov.vn + mof.gov.vn; design GDTClient with versioned API path | Dev |
| R7 | SmartACCT existing tests break due to GDT/AR wiring | Low | Med | TDD: add integration test for each T2.x slice immediately; run full suite after each task | Dev |
| R8 | i18n translation quality (Vietnamese accounting terminology) | Med | Low | Chief accountant reviews all vi translations; reference ketoanthienung.net + ketoanleanh.edu.vn terminology | Accountant |

---

## 7. Checkpoints & Go/No-Go Gates

| Checkpoint | Gate | Criteria |
|-----------|------|----------|
| **CP1 (W3 end)** | Foundation complete | 70 tests green; all tables migrated; ARUseCases class defined |
| **CP2 (W7 end)** | Core AR live | End-to-end create→send→pay works; GDT integration tested; 30 tests green |
| **CP3 (W10 end)** | Collections live | Dunning cron works; provisions calculated correctly; write-off GL correct |
| **CP4 (W12 end)** | Polish complete | i18n done; credit limit enforced; 40+ tests green; accountant UAT |
| **CP5 (W14 end)** | **v1.0 GO-LIVE** | All P0+P1 use cases live; 5 reports accurate; prod deploy; BCTC disclosure ready |

**Go/No-Go format:** Each checkpoint requires sign-off from:
1. Lead Dev (tests green, code reviewed)
2. Chief Accountant (TK posting verified)
3. BA Lead (BRD compliance verified)

If any gate fails: freeze feature work, fix blocker, re-verify before advancing.

---

## 8. Task Execution Order (Detailed)

```
Week 1 (Parallel):
├─ T1.1: domain/ar.py [P]
└─ T1.2: infrastructure/models/ar_models.py [P]

Week 2:
├─ T1.3: migrations/versions/XXXX_ar_tables.py (after T1.2)
└─ T1.4: infrastructure/repositories/ar_repository.py (after T1.3)

Week 3:
└─ T1.5: use_cases/ar/__init__.py (after T1.4)
   └─ CP1

Week 4:
├─ T2.1: presentation/ar/customers.py (after T1.5) [parallel with partial T2.2]
└─ T2.2 start: presentation/ar/invoices.py (customer validation + create)

Week 5:
├─ T2.2 finish: presentation/ar/invoices.py (send + void endpoints)
├─ T2.3: presentation/ar/payments.py (3 endpoints + FIFO allocation)
└─ T2.4: Wire GDTClient.submit_invoice() into send flow (parallel)

Week 6:
├─ T2.5: GET /ar/aging (live computed, 6 buckets)
└─ T2.6: POST /ar/aging/snapshot + GET /ar/aging/snapshots (parallel)

Week 7:
├─ T2.7: GL posting audit (verify Dr 131 / Cr 511 / Cr 3331 + Dr 111 / Cr 131)
└─ CP2 (Core AR live)

Week 8:
├─ T3.1: presentation/ar/dunning.py (POST /dunning, GET /dunning, GET /dunning/queue)
└─ T3.2: APScheduler daily dunning cron at 08:00 (parallel)

Week 9:
├─ T3.3: POST /ar/bad-debt/provisions (TK 630 per Circular 200/2014)
└─ T3.4: POST /ar/bad-debt/write-off (CFO approval + GL Dr 630 / Cr 131)

Week 10:
├─ T3.5 (optional): GET /ar/reports/ecl (IFRS 9 3-stage, feature-flagged)
└─ CP3 (Collections live)

Week 11:
├─ T4.1: i18n — add 50+ AR error codes to vi/en .po files
└─ T4.2: Credit limit enforcement (80/100 rule + CFO override)

Week 12:
├─ T4.3: IFRS 15 contract asset distinction
├─ T4.4: QA sprint — load test, accountant UAT, bug bash
└─ CP4 (Polish complete — Go/No-Go for Phase 5)

Week 13:
├─ T5.1: GET /ar/reports/balance (customer AR balance summary)
└─ T5.2: GET /ar/reports/collection-effectiveness (CEI + DSO)

Week 14:
├─ T5.3: GET /ar/reports/statement/{customer_id} (aged statement PDF via Jinja2)
├─ T5.4: GET /ar/reports/bctc-disclosure (IFRS 7 + VAS disclosure blocks)
└─ CP5 (v1.0 GO-LIVE)
```

---

## 9. Test Strategy

### Test Pyramid

```
        ┌─────────────┐
        │  E2E (5)    │  ← Full happy path: create customer → invoice → GDT → payment → aging → dunning
        ├─────────────┤
        │ Integration │  ← 40 tests: route → use case → repo → DB (test_postgres)
        │   (40)      │
        ├─────────────┤
        │   Unit      │  ← 60 tests: domain validators, repo queries, use case logic
        │   (60)      │
        └─────────────┘
```

### Test Coverage Targets

| Module | Unit | Integration | E2E | Total Target |
|--------|------|-------------|-----|---------------|
| `domain/ar.py` | 15 | — | — | 15 |
| `infrastructure/models/ar_models.py` | 20 | — | — | 20 |
| `infrastructure/repositories/ar_repository.py` | 25 | 10 | — | 35 |
| `use_cases/ar/` | 30 | 15 | — | 45 |
| `presentation/ar/` | — | 15 | 5 | 20 |
| **TOTAL** | **90** | **40** | **5** | **135** |

### Critical Test Scenarios

| ID | Scenario | Type | Why Critical |
|----|----------|------|--------------|
| TC-AR-01 | Tax code 10–13 digit validation | Unit | Regulatory (Mã số thuế format) |
| TC-AR-02 | Credit limit check at 80%, 100% | Integration | Financial control |
| TC-AR-03 | GDT submission retry (3× backoff) | Integration | NĐ70/2025 compliance |
| TC-AR-04 | GL entry balances (Dr = Cr ± 0.001) | Integration | Double-entry integrity |
| TC-AR-05 | FIFO payment allocation | Unit | Standard AR practice |
| TC-AR-06 | Aging snapshot locked to CLOSED period | Integration | Audit trail |
| TC-AR-07 | Provision rates match Circular 200/2014 | Unit | VAS compliance |
| TC-AR-08 | Write-off blocked if < 6 months overdue | Integration | Regulated condition |
| TC-AR-09 | Dunning levels auto-advance cron | Integration | Collection workflow |
| TC-AR-10 | End-to-end with GDT sandbox | E2E | Full happy path |

### Regression Commitment

```
BEFORE COMMIT:
  .venv/bin/pytest tests/ --tb=short -q        ← 379 existing + new AR tests
  .venv/bin/pytest tests/test_ar_*.py -v       ← AR-only tests
  .venv/bin/python -c "from presentation.ar import ar_bp; print('OK')"
```

**Hard rule:** No commit that breaks existing 379 tests. If breakage found → fix immediately or revert.

---

## 10. Definition of Done (DoD)

A task is **done** when ALL of:

- [ ] **Code:** Implements the acceptance criteria exactly (no gold-plating)
- [ ] **Tests:** Unit/integration tests pass; new test(s) written for new behavior
- [ ] **i18n:** All user-facing strings use error codes or `gettext()`; vi/en translations exist
- [ ] **Docs:** Docstring on public methods; BRD/plan updated if behavior deviates
- [ ] **Git:** Atomic commit with message following repo convention
- [ ] **Review:** Chief accountant verified TK posting logic (for GL-affecting tasks)
- [ ] **Performance:** No query > 2s on 10k-row dataset without index justification
- [ ] **Security:** No raw SQL, no hardcoded secrets, JWT auth on all endpoints

---

## 11. Budget & Timeline Summary

| Phase | Weeks | Dev-Weeks | Key Deliverable |
|-------|-------|-----------|------------------|
| 1 — Foundation | W1–3 | 3 | 8 DB tables + domain + repo + use cases |
| 2 — Core AR | W4–7 | 5 | Customer CRUD + Invoice flow + Payment + GDT |
| 3 — Collections | W8–10 | 3 | Dunning + Provisions + Write-off |
| 4 — Polish | W11–12 | 2 | i18n + Credit + IFRS 15 + QA |
| 5 — Reporting | W13–14 | 2 | Balance + CEI/DSO + Statements + BCTC |
| Buffer | 2 | 2 | Unknowns, GDT delays, review cycles |
| **TOTAL** | **~16** | **~17** | **v1.0 production-ready AR module** |

**Start date:** Week 0 (setup) — first task T1.1 begins immediately  
**Target production date:** End of Week 14 (or Week 16 with buffer)  
**Go/No-Go review:** Every Friday standup + formal CP gates at W3/W7/W10/W12/W14

---

## 12. Out-of-Scope (Deferred to v2.0)

| Feature | Reason Deferred | v2.0 Target |
|---------|----------------|-------------|
| Multi-currency AR | Requires hedge accounting logic + FX rate service | W20–24 |
| Customer self-service portal | Requires separate auth flow + UI investment | W24–28 |
| External credit scoring | Integration with CIC/PCI Vietnam bureau | W18–22 |
| Automated legal escalation | Requires legal template library + e-signature | W22–26 |
| AR factoring / invoice discounting | Financial product, legal framework, bank integration | Post-v2.0 |
| ePayment gateway (MoMo, ZaloPay, VNPay) | Separate integration per gateway; payment module first | W18–20 |

---

## 13. Appendices

### A. Story Point Breakdown

| UC | Story Points | Rationale |
|----|-------------|-----------|
| UC-AR-01 (Customer CRUD) | 5 | Straightforward CRUD; tax_code validation adds 1 SP |
| UC-AR-02 (Create AR Invoice) | 8 | Complex: customer validate, credit check, EInvoice gen, GL post, GDT submit |
| UC-AR-03 (Aging Report) | 5 | Computed query; performance tuning |
| UC-AR-04 (Aging Snapshot) | 3 | Write snapshot; period lock check |
| UC-AR-05 (Dunning) | 8 | State machine + cron + notifications + logs |
| UC-AR-06 (Payment Allocation) | 8 | FIFO logic + GL posting + overpayment handling |
| UC-AR-07 (Provisions) | 5 | TK 630 rate table + batch calc |
| UC-AR-08 (Credit Limit) | 3 | Simple gate + override |
| UC-AR-09 (GL Posting) | 8 | Atomic posting + rollback + multi-posting scenarios |
| UC-AR-10 (GDT Submit) | 5 | Retry + sign + idempotency |
| UC-AR-11 (Write-Off) | 5 | Approval flow + CFO gate + audit |
| UC-AR-12 (CEI + DSO) | 5 | Formula impl + time-series aggregation |
| UC-AR-13 (ECL IFRS 9) | 8 | 3-stage classification + probability models |
| UC-AR-14 (Netting) | 5 | Cross-module (AR + AP) offset logic |
| **TOTAL** | **77 SP** | **~11 dev-days @ 7 SP/day × 2 devs** |

### B. Team RACI

| Activity | Lead BA | Chief Acct | Senior Dev | Full-Stack Dev | DevOps |
|----------|---------|-----------|-----------|----------------|--------|
| BRD + Use Cases | **R/A** | C | I | I | I |
| TK posting validation | C | **R/A** | C | I | I |
| Domain model design | C | C | **R/A** | C | I |
| DB schema + migration | I | I | **R/A** | C | C |
| Repository + use cases | I | I | **R/A** | C | I |
| API routes | I | I | C | **R/A** | I |
| GDT integration | I | I | **R/A** | C | I |
| i18n | C | C | C | **R/A** | I |
| Reports (PDF) | C | C | C | **R/A** | I |
| Deployment | I | I | C | C | **R/A** |
| UAT + Sign-off | **R/A** | **R/A** | C | C | I |

*R = Responsible, A = Accountable, C = Consulted, I = Informed*

### C. Reference Links

| Document | Location |
|----------|----------|
| BRD | `docs/brd/accounts_receivable.md` |
| Use Cases | `docs/ar/use_cases.md` |
| Workflows | `docs/ar/workflows.md` |
| This Plan | `docs/ar/implementation-plan.md` |
| Existing i18n guide | `domain/i18n.py` + `translations/` |
| SmartACCT architecture | `AGENTS.md` |

---

*Document prepared by Lead BA + Chief Accountant. Approved for execution pending CP1 start.*
