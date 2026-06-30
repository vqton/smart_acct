# SmartACCT | AGENTS.md

Vietnamese ERP (Flask + SQLAlchemy + PostgreSQL 16). Flattened structure — no `/app/` directory.

---

## 1. Project Overview

```
/home/projects/smart_acct/
├── config.py              # Pydantic config, env vars, connection pooling
├── run.py                 # Flask entry point
├── alembic.ini            # Alembic config (reads DATABASE_URL from .env)
├── CHANGELOG.md           # Release notes
├── domain/                # Pure domain models (Pydantic v2, no framework deps)
│   └── __init__.py        # All domain entities + enums (TT99/2025, TT133/2016)
├── infrastructure/
│   ├── database.py        # DB manager, JWT auth, formatters
│   ├── models/
│   │   ├── __init__.py
│   │   ├── coa_models.py         # SQLAlchemy models for COA
│   │   └── tax_models.py         # SQLAlchemy models for tax (8 tables)
│   └── repositories/
│       ├── __init__.py
│       ├── coa_repository.py     # COA CRUD repo (domain↔DB mapping)
│       └── tax_repository.py     # Tax CRUD repo (7 entity types)
├── use_cases/
│   ├── __init__.py               # Re-exports all use case classes
│   ├── coa/                      # 8 modules: use_cases, validate, import, export, versioning, ifrs, usage, template
│   │   └── __init__.py
│   ├── gl/                       # GLUseCases (gl_use_cases.py shim for backward compat)
│   │   └── __init__.py
│   ├── tax/                      # TaxUseCases (tax_use_cases.py shim for backward compat)
│   │   └── __init__.py
│   ├── cash/                     # CashUseCases (cash_use_cases.py shim for backward compat)
│   │   └── __init__.py
│   ├── coa_use_cases.py          # → shim: imported from use_cases.coa.use_cases
│   ├── gl_use_cases.py           # → shim: from use_cases.gl import GLUseCases
│   ├── tax_use_cases.py          # → shim: from use_cases.tax import TaxUseCases
│   └── cash_use_cases.py         # → shim: from use_cases.cash import CashUseCases
├── presentation/
│   ├── __init__.py
│   ├── coa_routes.py     # Flask blueprint (/api/v1/coa/*)
│   ├── gl_routes.py      # Flask blueprint (/api/v1/gl/*, periods)
│   ├── tax_routes.py     # Flask blueprint (/api/v1/tax/*, 40 endpoints)
│   └── cash_routes.py    # Flask blueprint (/api/v1/cash/*, 23 endpoints)
├── services/
│   ├── gdt_client.py     # GDT eTax API client stub
│   └── signing_service.py# RSA-SHA256 e-invoice signing stub
├── migrations/
│   └── versions/          # Alembic migration scripts (COA + tax + GL + cash)
├── tests/
│   ├── __init__.py
│   ├── test_coa_domain.py        # COA domain unit tests
│   ├── test_tax_domain.py        # Tax domain unit tests
│   ├── test_tax_integration.py   # Tax repository + use case integration
│   ├── test_gl_integration.py    # GL/period integration tests
│   └── test_cash_integration.py  # Cash (64 tests) + bank integration
└── requirements.txt
```

**Tech Stack**: Flask 3.0, SQLAlchemy 2.0, PostgreSQL 16, PyJWT, Casbin, openpyxl, WeasyPrint, pytest.

---

## 2. Setup & Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
FLASK_DEBUG=false
HOST=0.0.0.0
PORT=5000
```

### Quick Start
```bash
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py          # http://0.0.0.0:5000
```

### Database Pooling
- Pool size: 20, max overflow: 30, recycle: 3600s
- PostgreSQL 16 required (Docker recommended)
- Never create separate `SQLAlchemy` instances — use `infrastructure/database.py` manager
- Dispose connections in teardown

### Production
- TLS/HTTPS required
- Regular PostgreSQL backups
- Connection pool monitoring (nest 80/tcp)

---

## 3. Architecture

### Layer Rules
| Layer | Depends On | Responsibility |
|-------|-----------|----------------|
| `domain/` | Nothing | Pure Pydantic entities, no framework/DB imports |
| `use_cases/` | domain | Application logic (journal posting, VAT, month-end close) |
| `infrastructure/` | domain | DB, auth, formatting, repositories |
| `presentation/` | use_cases | Flask blueprints, Jinja2 templates |
| `services/` | domain, infrastructure | Report generation |

### Vietnam (VAS) Conventions
- **Account codes**: Circular 133/2016 format (`1.1.1`, `2.1.1`, `4.1.1`). Valid: `1`, `1.1`, `1.1.1`, `12345`. Invalid: `0`, `A1`, `>4 levels`.
- **DCR Direction**: Debit normal = ASSET, CASH, INVENTORY, EXPENSE. Credit normal = LIABILITY, EQUITY, REVENUE.
- **Double-entry**: Must balance within 0.001 VND tolerance
- **Currency**: VND preferred. Locale: `1.500.000,50 đ`. Also USD, EUR, JPY, GBP.
- **Dates**: Vietnamese month names (`15 tháng 1 năm 2024`)
- **Account types**: 33+ from Circular 133/2016
- **Monthly balances**: Table for fast financial statements

### Code Conventions
- **Imports**: `from use_cases.coa import COAUseCases`, `from use_cases.gl import GLUseCases`
- **Type hints**: Required everywhere
- **Errors**: Raise `VASValidationError` or `ValidationError`
- **No hardcoded currency symbols**

### Internationalization (i18n) — Completed
- **Stack**: Flask-Babel 4.0 for presentation layer; error-code keys for domain/use case messages
- **Two-tier architecture**:
  - **Domain + Use Cases**: Raise/return **error code strings** (e.g. `"ACCOUNT_CODE_EMPTY"`) — no framework imports. `VASValidationError` carries `msgid` + `**params` for `gettext("%(name)s")` resolution. Resolution to locale happens at the presentation boundary.
  - **Presentation**: `resolve_error()` helper in `presentation/__init__.py` calls `gettext(msgid, **params)` on all error returns; falls back to raw string when Flask context unavailable.
- **`domain/i18n.py`**: `ErrorCodes` class with 200+ canonical error code constants; `resolve()` helper
- **`translations/` directory**: `.po`/`.mo` files for `vi` (primary) and `en` (secondary) — full Vietnamese translations for all error codes
- **Locale negotiation**: `?lang=` → Accept-Language header → `vi` default (JWT locale claim wired but depends on token presence)
- **Scope**: 450+ hardcoded strings converted across 21 files (domain/__init__.py, 10 use case files, 4 repositories, 4 route files)
- **Format**: `.po` `msgstr` uses `%(name)s` format for Flask-Babel `gettext()` compatibility
- **Authoritative vocabulary sources** (use for accurate Vietnamese accounting/tax terminology):
  - MOF: `mof.gov.vn`
  - GDT eTax: `thuedientu.gdt.gov.vn`
  - Customs e-declaration: `customs.gov.vn`
  - Social Insurance e-portal: `baohiemxahoi.gov.vn`
  - National Public Service Portal: `dichvucong.gov.vn`
  - General Dept of Taxation: `gdt.gov.vn`
  - VACPA (Auditing practitioners): `vacpa.org.vn`
  - VAA (Vietnam Accounting & Auditing Association): `vaa.net.vn`
  - Big 4 Vietnam tax/accounting glossaries: EY, PwC, Deloitte, KPMG
- **Remaining**: (none — all i18n work complete)

---

## 4. Development Workflow (TDD)

### Feature Flow
```
interview-me → spec-driven-development → planning-and-task-breakdown
→ incremental-implementation + test-driven-development
→ code-review-and-quality → code-simplification
→ shipping-and-launch
```

### Implementation Steps
1. Write failing test in `tests/` (Red)
2. Implement minimal code in `use_cases/` (Green)
3. Refactor while tests stay green
4. Add repository in `infrastructure/repositories/` (if needed)
5. Update domain in `domain/` (if needed)
6. Add route in `presentation/routes.py`

### Testing
```bash
.venv/bin/pytest tests/                    # All
.venv/bin/pytest tests/test_domain.py      # Domain
.venv/bin/pytest tests/test_integration.py  # Integration
.venv/bin/pytest tests/ -v                 # Verbose
```

**Test categories**: Unit (domain validation), Integration (use cases + DB), Edge cases (invalid codes, amounts, dates).

### Security
- JWT Bearer tokens for API auth
- bcrypt password hashing
- Flask-JWT session management
- Rate limiting on endpoints

---

## 5. Tooling & Navigation

### CodeGraph (Primary Navigation)
**Always use CodeGraph first** — pre-built knowledge graph, faster than grep/read.

| Intent | Tool |
|--------|------|
| "How does X work?" / Architecture / Bug / "Where is X?" | `codegraph_explore` **(PRIMARY)** |
| "What calls X?" / "What does X call?" / Blast radius | `codegraph_callers` / `codegraph_callees` / `codegraph_impact` |
| Symbol location only | `codegraph_search` |
| One symbol full source (overloaded names) | `codegraph_node` with `includeCode=true` |
| Directory tree | `codegraph_files` |
| Index health | `codegraph_status` |

**Anti-patterns**: Don't grep first. Don't chain search+node — one `explore` does it. Don't loop `node` over many symbols. Don't re-verify CodeGraph results.

**Staleness**: If banner says "edited since last sync", read those files. Others are fresh.

### Skills Reference
**Always check skills before non-trivial work.** Load with: `skill <name>`

| When | Skill |
|------|-------|
| Vague request ("build X") | `interview-me` |
| Rough idea, need options | `idea-refine` |
| New project, no spec | `spec-driven-development` |
| Have spec, need tasks | `planning-and-task-breakdown` |
| Implementing | `incremental-implementation` |
| API design | `api-and-interface-design` |
| UI work | `frontend-ui-engineering` |
| Writing tests | `test-driven-development` |
| Bug | `debugging-and-error-recovery` |
| Code quality | `karpathy-guidelines` |
| Code review | `code-review-and-quality` |
| Too complex | `code-simplification` |
| Security | `security-and-hardening` |
| Performance | `performance-optimization` |
| Deploy | `shipping-and-launch` |
| Docs/ADRs | `documentation-and-adrs` |
| Git | `git-workflow-and-versioning` |
| CI/CD | `ci-cd-and-automation` |

### Karpathy Principles (Load at session start: `skill karpathy-guidelines`)

1. **Think before coding** — State assumptions, name confusion, ask.
2. **Simplicity first** — "Is this the minimum that solves the problem?"
3. **Surgical changes** — Match existing style. Touch only what's requested. Every line traces to the request.
4. **Goal-driven execution** — Transform tasks into verifiable goals. Tests pass before AND after.

### Session Initialization
```bash
skill caveman              # 75% token reduction (auto-active, off with "normal mode")
codegraph status           # Verify index is fresh
skill <skill-name>         # Load task-appropriate skill
```

---

## 6. Validation & Verification

### Health Checks
```bash
curl http://localhost:5000/api/v1/health
.venv/bin/python -c "from infrastructure.database import SmartACCTDatabase; print('DB OK')"
.venv/bin/pytest tests/test_vietnamese_formatting.py -v
```

### Architecture Validation
```bash
# Domain layer isolation
.venv/bin/python -c "
from domain.entities import Account, JournalEntry
assert 'app' not in str(Account.__module__)
assert 'app' not in str(JournalEntry.__module__)
print('Domain layer clean')
"

# Infrastructure import check
.venv/bin/python -c "
from infrastructure.database import SmartACCTDatabase
print('Infrastructure imports domain correctly')
"
```

---

## 7. Gotchas & Anti-Patterns

### Gotchas
- **Currency formatting**: `1000000.50` → `1.000.000,50 đ` (VND), `1,000,000.50 ¥` (JPY)
- **DCR Direction**: Commit to memory — wrong direction = invalid entries
- **Connection pooling**: Single manager instance only. No raw `SQLAlchemy()` calls.
- **CodeGraph stale?**: Check the sync banner. Read listed files, trust others.

### What NOT to Do
❌ Create `app/` subdirectory
❌ Bypass domain validation in use_cases
❌ Mix presentation logic with domain logic
❌ Hardcode currency symbols
❌ Skip TDD red-green cycle
❌ Implement without checking applicable skill first
❌ Guess when confused — surface the confusion

---

## 8. Persistent Memory (obsidian-mind)

An [obsidian-mind](https://github.com/breferrari/obsidian-mind) vault is installed at `.obsidian-mind/` for cross-session agent memory. Open it in Obsidian to browse/ edit memories, or use the built-in MCP (`Obsidian Bridge`) for agent-driven reads/writes.

Key vault directories:
- `brain/` — decisions, incidents, patterns, glossary
- `bases/` — domain knowledge bases (VAS, tax law)
- `org/` — North Star goals, team docs, roadmaps
- `perf/` — performance tracking, benchmarks
- `work/` — active tasks, context captures
- `reference/` — external reference materials
- `thinking/` — structured thinking (MOC, debate, first principles)
- `templates/` — note templates

The vault is `.gitignore`d — keep it local to each developer's machine.

---

## 9. Clarifying Questions

When requirements are unclear, ask about:
- Team conventions (contribution process)
- Performance requirements (concurrent users, transaction volume)
- Compliance scope (GST, CIT, PIT, VAT modules)
- Deployment infrastructure (Docker, k8s, AWS/GCP)
- Reporting requirements (Excel vs PDF, SLA deadlines)

---

## 10. Anchored Summary

### COA Module — Completed (UC-01 through UC-08, 87 tests)
- Account CRUD, Excel import/export, CSV/JSON export, versioning & audit, VAS↔IFRS mapping (5 mapping types), account usage check, full VAS compliance scan (incl. DCR direction), TT99/2025 + TT133/2016 templates, API integration tests
- `code` regex fix: `^[1-9](?:\.[0-9]+)*$|^[1-9][0-9]{3,5}$`
- 8 use case classes consolidated in `use_cases/coa/` subpackage

### Fiscal Period Management — Completed (UC-FP-01 through UC-FP-08)
- BRD: `docs/brd/fiscal_period_management.md`
- **Period-gated posting**: `create_entry`/`update_entry`/`post_entry` reject closed periods
- **Period model upgrade**: `PeriodType` enum (monthly/quarterly/yearly), `start_date`, `end_date`, `is_current`, `needs_reconciliation`, `parent_period`; migration `5e6f7a8b9c0d`
- **Period auto-creation + CRUD**: `_auto_create_period()` computes date range from period string; `POST /periods`; `GET /periods/current`
- **Period audit trail**: `PeriodAuditLogModel` + migration `6c8d9f0a1b2d`; audit logging on create/close/reopen; `GET /periods/{period}/audit-log`
- **Close validation**: `_count_unposted_entries()` + `_has_unbalanced_entries()` checks; `force` param to skip; `PERIOD_FORCE_CLOSE` audit event
- **Reopen validation**: mandatory `reason` param; downstream period `needs_reconciliation` flagging; tax declaration lock checks `TaxDeclarationModel` for submitted/accepted statuses
- **List enhancements**: `?status=open|closed` filter; `has_entries` flag in response
- **Period overlap validation**: blocks create if date ranges overlap
- **Year-end carry-forward (UC-FP-07)**: revenue/expense → 911 → 421 closing entries; auto-creates next year period; `POST /periods/{period}/carry-forward`

### Tax Module — Completed
- 8 entities (declaration, line, payment, adjustment, incentive, e-invoice, e-invoice line, schedule)
- VAT calculation (deduction/direct), schedule generation, due reminders
- Domain edge cases, state transitions, multi-entity interactions (139 tests total incl. integration)

### Cash Module — Completed (UC-CASH-01 through UC-CASH-11, 64 tests)
- 11 domain entities (Advance, CashReceipt, CashPayment, PettyCashFund, PettyCashTransaction, CashTransfer, ChequeBook, Cheque, CashForecast, CashForecastLine, DailyCashCount) + 5 bank entities (BankAccount, BankTransaction, BankStatement, BankReconciliation, CashTransfer) — all with `id: Optional[int] = None` fix
- 14 SQLAlchemy models (`infrastructure/models/cash_models.py`), migration `7d8e9f0a1b2c`
- Full repository CRUD + `get_cash_balance()`, `get_cash_book_entries()`, `get_gl_entries_for_bank()`, `update_cheque_status()` (lifecycle-aware)
- Cash balance endpoint, cash book report (Sổ quỹ tiền mặt, HTML+JSON), cash count report (Biên bản kiểm kê quỹ, HTML+JSON with denomination + surplus/shortage)
- 23 route endpoints in `presentation/cash_routes.py`
- Bank features written in use cases (import_bank_statement, auto-matching, bank book report, reconciliation report, cheque lifecycle) — routes + tests deferred to Phase 2
- HTML report strings extracted to Jinja2 templates (`templates/cash_book_report.html`, `templates/cash_count_report.html`, `templates/reconciliation_report.html`) with `{% trans %}` blocks for i18n

### Internationalization (i18n) — Completed
- `VASValidationError` enhanced with `msgid` + `**params` for `gettext("%(name)s")` resolution
- `domain/i18n.py`: 200+ error code constants, `ERROR_CODE_MAP`, `resolve()` helper
- 450+ strings converted across 21 files (domain, use cases, repositories, routes)
- All `Result.failure()` and route `str(error)` → `ErrorCodes.CODE` + `resolve_error()`
- `presentation/__init__.py`: `resolve_error()` helper + Flask-Babel 4.x wiring
- `translations/vi` + `translations/en`: full `.po`/`.mo` for all error codes
- Format: `%(name)s` style for Flask-Babel `gettext()` compatibility
- Fallback to raw msgid when Flask app context unavailable (safe in tests)
- Cash report HTML extracted to Jinja2 templates with `{% trans %}` blocks: `templates/cash_book_report.html`, `templates/cash_count_report.html`, `templates/reconciliation_report.html`
- JWT locale claim verified with HS256 signature when `JWT_SECRET_KEY` configured

### AP Module — Completed (UC-AP-01 through UC-AP-15, 64 tests)
- **BRD**: `docs/brd/ap.md` (1526 lines) — full spec: 15 use cases, GL posting matrix, regulatory framework (TT99/2025, TT200/2014, Circular 103/2014 FCT)
- **Domain**: 10 entities (Vendor, APInvoice, APInvoiceLine, APPayment, APPaymentAllocation, VendorPrepayment, APProvision, APAgingSnapshot, FCTDeclaration, IntercompanyInvoice) + 15+ enums in `domain/ap.py` (333 lines)
- **DB**: 12 SQLAlchemy tables in `infrastructure/models/ap_models.py` (410 lines)
- **Repository**: `infrastructure/repositories/ap_repository.py` (890 lines) — 40+ CRUD + query methods
- **Use cases**: `use_cases/ap/__init__.py` (1272 lines) — all 15 UC-AP methods: vendor lifecycle, invoice CRUD (3-way match), credit/debit notes, payment + allocation, prepayments, aging report + snapshots (TT48/2019), provisions, FCT (Circular 103/2014), GL auto-posting, FX revaluation, intercompany
- **Routes**: `presentation/ap/__init__.py` (119 lines, blueprint + 7 JSON serializers) + `presentation/ap/routes.py` (733 lines, 35 endpoints)
- **Tests**: 64 tests (26 domain + 38 integration) covering all 15 use cases; all passing

### FA Module (Fixed Assets) — Completed (UC-FA-01 through UC-FA-12, 173 tests)
- **BRD**: `docs/brd/fixed_assets.md` (376 lines) — full spec: 12 use cases, regulatory regime analysis (TT 99/2025, TT 45/2013 as amended by 147/2016 + 28/2017 + 30/2025, VAS 03/04, IFRS convergence QĐ 345/2020), GL posting matrix, 7 FA classifications, chart of accounts, depreciation rules, 8 reports
- **Use Cases**: `docs/fa/use_cases.md` (676 lines) — UC-FA-01 through UC-FA-12: categories, registration, depreciation (3 methods), revaluation, transfer, adjustment, disposal, inventory, biological assets (TK 215), reports, IFRS conversion, TT 99 migration
- **Implementation Plan**: `docs/fa/implementation_plan.md` (275 lines) — 4 phases, 16 tasks, 143 tests planned, 12-week MVP estimate
- **Domain**: 12 enums + 13 Pydantic entities in `domain/fa.py` (375 lines) — FACategory, FixedAsset, DepreciationRecord, FAAdjustment, FADisposal, FAInventory, FAInventoryLine, FATransfer, FASparePart, FAComponent, BiologicalAsset, BiologicalProvision, DepreciationConfig; all with validators, i18n error codes
- **DB**: 12 SQLAlchemy tables in `infrastructure/models/fa_models.py` (383 lines) — migration `9fa1b2c3d4e5`
- **Repository**: `infrastructure/repositories/fa_repository.py` — 44 CRUD + query methods across all entities + GL posting + audit logging
- **Use cases**: `use_cases/fa/__init__.py` (852 lines) — all 12 UC-FA methods: category CRUD, asset registration, depreciation engine (SL/DB/units-of-production), adjustments, transfers, disposals, inventory, spare parts/components, biological assets (TK 215), 4 reports, TT 99/2025 migration, TT 30/2025 suspension/resume
- **Routes**: `presentation/fa/__init__.py` (blueprint `/api/v1/fa` + 13 serializers) + `presentation/fa/routes.py` (36 endpoints)
- **Tests**: 173 tests (122 domain + 51 integration) — all 12 use cases covered
- **Status**: ✅ Production-ready. All 12 use cases, 36 routes, 173 tests passing.

### CCDC Module (Tools & Equipment) — Completed (UC-CC-01 through UC-CC-12, 69 tests)
- **BRD**: `docs/brd/tools_equipment.md`, `docs/brd/tools_equipment_use_cases.md`, `docs/brd/tools_equipment_implementation.md`
- **Domain**: 7 enums + 11 Pydantic entities in `domain/cc.py` (365 lines): CCategory, CCDCItem, CCDCAllocation, CCDCAllocationLine, CCDCTransaction, CCDCTransfer, CCDCInventory, CCDCInventoryLine, CCDCWriteOff, CCDCSparePart, CCDCImportLog — all with validators, i18n error codes
- **DB**: 14 SQLAlchemy tables in `infrastructure/models/cc_models.py` (365 lines) — migration `0fa1b2c3d4e6`
- **Repository**: `infrastructure/repositories/cc_repository.py` (470 lines) — CRUD + business queries (by department, by employee, unallocated, total value)
- **Use cases**: `use_cases/cc/__init__.py` (500 lines) — all 12 UC-CC methods: category CRUD, item registration, allocation processing (1-time/2-time/multi-period w/ auto line generation), transaction recording, transfers, inventory/stocktake, disposal/write-off, spare parts, reports (by dept/employee/allocation schedule/value summary/inventory status), import/export, GL auto-posting, dashboard/KPI
- **Routes**: `presentation/cc/__init__.py` (blueprint `/api/v1/cc` + 11 serializers) + `presentation/cc/routes.py` (45 endpoints)
- **Tests**: 69 tests (31 domain + 38 integration) covering all 12 use cases + edge cases; all passing
- **Status**: ✅ Production-ready per TT 99/2025 (eff. 01/01/2026). TK 242 for multi-period allocation, max 36 months per TT 80/2021.

### Inventory Module — Completed (UC-INV-01 through UC-INV-15, 139 tests)
- **Domain**: 10 enums + 16 Pydantic entities in `domain/inventory.py` (~600 lines): InventoryCategory, Warehouse, InventoryItem, InventoryBatch, SerialNumber, InventoryReceipt, InventoryReceiptLine, InventoryIssue, InventoryIssueLine, InventoryTransfer, InventoryTransferLine, StockCard, InventoryCheck, InventoryCheckLine, InventoryAdjustment, InventoryAdjustmentLine, InventoryConfig, InventoryDashboard — all with validators, i18n error codes
- **DB**: 14 SQLAlchemy tables in `infrastructure/models/inventory_models.py` (~360 lines) — migration `1fa2b3c4d5e6`
- **Repository**: `infrastructure/repositories/inventory_repository.py` (~1220 lines) — full CRUD + stock adjustment, batch/serial tracking, stock card upsert, GL account resolution, dashboard metrics, 40+ methods
- **Use cases**: `use_cases/inventory/__init__.py` (~600 lines) — all 15 UC-INV methods: categories, item master data, warehouse management, goods receipt (post + stock update), goods issue (post + stock deduction), transfers (multi-warehouse), batch/serial tracking, stock card/balance enquiry, physical stocktake, adjustments, valuation (moving average), GL auto-posting (receipt/issue entries), reports (inventory/low-stock/movements), import/export, dashboard/KPI
- **Routes**: `presentation/inventory/__init__.py` (blueprint `/api/v1/inv` + 12 serializers) + `presentation/inventory/routes.py` (40+ endpoints)
- **Tests**: 139 tests (49 domain + 90 integration) covering all 15 use cases + edge cases; all passing
- **Status**: ✅ Production-ready per TT 133/2016 + TT 200/2014. TK 152/155/156/157 for inventory, TK 632 for COGS, TK 331/111/112 for payables.

### Test count: 845 passing (all tests)
- COA: 87 (domain 21, import 14, export 6, versioning 8, IFRS 10, usage 6, compliance 7, template 7, integration 8)
- GL: 47 (repository 6, posting 4, use cases 6, balances 1, period close 14, audit log 5, financial statements 3, carry forward 4, miscellaneous 4)
- Tax: 134 (domain 33, integration 46, edge cases 55)
- Cash: 111 (receipt 7, payment 7, bank account 5, bank reconciliation 7, petty cash 6, cash transfer 4, daily count 4, cheque 4, edge cases 6, balance 5, cash book report 3, cash count report 5, bank statements 8, cheque lifecycle 13, bank balance 4, bank book 4, reconciliation report 4, Flask routes 19)
- AP: 64 (domain 26, integration 38)
- FA: 173 (domain 122, integration 51)
- CCDC: 69 (domain 31, integration 38)
- Inventory: 139 (domain 49, integration 90)

### Migration chain
`9bd655dd20b4` (COA) → `6e53c00a09f4` (tax) → `3c4e5f6a7b8c` (GL) → `4d5e6f7a8b9c` (acct periods) → `5e6f7a8b9c0d` (period metadata) → `6c8d9f0a1b2d` (audit log) → `7d8e9f0a1b2c` (cash tables) → `8e9f0a1b2c3d` (ap tables) → `9fa1b2c3d4e5` (fa tables) → `0fa1b2c3d4e6` (cc tables) → `1fa2b3c4d5e6` (inv tables: inv_categories, inv_warehouses, inv_items, inv_batches, inv_serials, inv_receipts, inv_receipt_lines, inv_issues, inv_issue_lines, inv_transfers, inv_transfer_lines, inv_stock_cards, inv_checks, inv_check_lines, inv_adjustments, inv_adjustment_lines)

### Key files
- `use_cases/gl/__init__.py` — GLUseCases (period close/reopen/create/get_current/get_audit_log/carry_forward, financial statements)
- `infrastructure/repositories/gl_repository.py` — `_count_unposted_entries`, `_has_unbalanced_entries`, `_has_tax_declarations_blocking_reopen`, `_log_audit`, `_auto_create_period`, `carry_forward`, `_period_to_dict`
- `infrastructure/models/gl_models.py` — `AccountingPeriodModel` (upgraded), `PeriodAuditLogModel`
- `presentation/gl_routes.py` — `POST/GET /periods`, `POST .../close`, `POST .../reopen`, `GET .../audit-log`, `POST .../carry-forward`
- `tests/test_gl_integration.py` — 47 tests covering all period operations
- `domain/__init__.py` — All domain entities (COA, GL, Tax, Cash, Bank)
- `infrastructure/repositories/cash_repository.py` — Cash CRUD + balance + book + cheque lifecycle
- `use_cases/cash/__init__.py` — CashUseCases (UC-CASH-01 through UC-CASH-11)
- `presentation/cash_routes.py` — 23 endpoints: cash receipts/payments/bank/cheque/balance/reports
- `tests/test_cash_integration.py` — 64 tests covering all cash + edge cases
- `domain/i18n.py` — Central error code registry (200+ constants), `ERROR_CODE_MAP`, `resolve()` helper
- `presentation/__init__.py` — Flask-Babel 4.x wiring, locale selector, `resolve_error()` helper
- `translations/vi/LC_MESSAGES/messages.po` — Vietnamese translations for all error codes
- `translations/en/LC_MESSAGES/messages.po` — English translations for all error codes
- `templates/cash_book_report.html` — Cash book report template with `{% trans %}`
- `templates/cash_count_report.html` — Cash count report template with `{% trans %}`
- `templates/reconciliation_report.html` — Bank reconciliation report template with `{% trans %}`
- `domain/fa.py` — FA domain: 12 enums + 13 Pydantic entities with validators, i18n error codes
- `infrastructure/models/fa_models.py` — 12 SQLAlchemy models for all FA tables
- `infrastructure/repositories/fa_repository.py` — FARepository: 44 CRUD/query methods across all FA entities
- `use_cases/fa/__init__.py` — FAUseCases: UC-FA-01 through UC-FA-12 (36 methods)
- `presentation/fa/__init__.py` — FA blueprint + 13 JSON serializers
- `presentation/fa/routes.py` — 36 REST endpoints for FA module
- `tests/test_fa_domain.py` — 122 domain unit tests
- `tests/test_fa_integration.py` — 51 integration tests (DB + use cases)
- `domain/cc.py` — CC domain: 7 enums + 11 Pydantic entities with validators, i18n error codes
- `infrastructure/models/cc_models.py` — 14 SQLAlchemy models for all CC tables
- `infrastructure/repositories/cc_repository.py` — CCRepository: full CRUD + business queries
- `use_cases/cc/__init__.py` — CCUseCases: UC-CC-01 through UC-CC-12 (36 methods)
- `presentation/cc/__init__.py` — CC blueprint + 11 JSON serializers
- `presentation/cc/routes.py` — 45 REST endpoints for CCDC module
- `tests/test_cc_domain.py` — 31 domain unit tests
- `tests/test_cc_integration.py` — 38 integration tests (DB + use cases)
