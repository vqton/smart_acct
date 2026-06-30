# Fixed Assets Module — Implementation Plan

**Version**: 1.0
**Date**: 2026-06-30
**Total Tasks**: 16 (4 phases)

---

## Phase 0: Foundation & Setup (Week 1-2)

### Task 0.1: Domain Entities (`domain/fa.py`)

**Files**: `domain/fa.py`, update `domain/__init__.py`

Enums:
- `AssetType`: TANGIBLE, INTANGIBLE, FINANCE_LEASE, BIOLOGICAL, INVESTMENT_PROPERTY
- `DepreciationMethod`: STRAIGHT_LINE, DECLINING_BALANCE, UNITS_OF_PRODUCTION
- `AssetStatus`: ACTIVE, SUSPENDED, FULLY_DEPRECIATED, DISPOSED, HELD_FOR_SALE
- `DisposalType`: SALE, LIQUIDATION, DONATION, THEFT, DESTRUCTION
- `AdjustmentType`: UPGRADE, PARTIAL_DISMANTLE, COST_CORRECTION, IMPAIRMENT, REVALUATION
- `BiologicalType`: PERIODIC_PRODUCER, ONE_TIME_PRODUCT, SEASONAL_CROP
- `GrowthStage`: IMMATURE, MATURE
- `AssetClassification` (Loại 1-7 per TT 147/2016)
- `FundSource`: OWNERS_EQUITY, LOAN, GOVERNMENT_GRANT, WELFARE_FUND, RD_FUND

Pydantic Entities:
- `FixedAssetCategory`
- `FixedAsset`
- `DepreciationRecord`
- `FAAdjustment`
- `FADisposal`
- `FAInventory`
- `FATransfer`
- `FASparePart`
- `FAComponent`
- `BiologicalAsset` (extends FixedAsset)
- `BiologicalProvision`
- `DepreciationMethodConfig`

### Task 0.2: SQLAlchemy Models (`infrastructure/models/fa_models.py`)

**Tables**: `fa_categories`, `fa_assets`, `fa_depreciation_records`, `fa_adjustments`, `fa_disposals`, `fa_inventories`, `fa_transfers`, `fa_spare_parts`, `fa_components`, `fa_biological_assets`, `fa_biological_provisions`, `fa_audit_log`

### Task 0.3: Alembic Migration

**Branch**: off `8e9f0a1b2c3d` (after AP tables)

### Task 0.4: Error Codes (`domain/i18n.py`)

Add `FA_` prefix error codes (40+ entries), Vietnamese translations

**Acceptance**: Domain entities pass type checks, migration creates tables, error codes registered.

---

## Phase 1: Core CRUD (Week 3-5)

### Task 1.1: FA Category CRUD

- Repository: `create_category`, `get_category`, `update_category`, `delete_category`, `list_categories`
- Use case: `create_category`, `update_category`, `list_categories`
- Route: `GET/POST/PUT /api/v1/fa/categories`
- Tests: 8 tests

### Task 1.2: FA Asset CRUD + Acquisition

- Repository: `create_asset`, `get_asset`, `update_asset`, `list_assets`, `search_assets`
- Use case: `register_asset` (UC-FA-02)
- Depreciation schedule generation on creation
- GL posting integration
- Route: `GET/POST /api/v1/fa/assets`, `GET/PUT/DELETE /api/v1/fa/assets/{id}`
- Tests: 15 tests (incl. acquisition types, validation, GL posting)

### Task 1.3: FA Depreciation Engine

- Depreciation calculator class with 3 methods
- `run_depreciation(period)` use case (UC-FA-03)
- `reverse_depreciation(period)` use case
- GL batch posting
- Route: `POST /api/v1/fa/depreciation/run`, `POST .../reverse`
- Tests: 12 tests (each method, mid-month acquisition, pro-rata, fully depreciated)

### Task 1.4: FA Disposal

- Repository + use case (UC-FA-07)
- GL posting for sale, liquidation, donation, theft
- Route: `POST /api/v1/fa/assets/{id}/dispose`
- Tests: 8 tests

**Checkpoint**: All core FA lifecycle operations functional via API.

---

## Phase 2: Advanced Operations (Week 6-8)

### Task 2.1: FA Adjustments

- Revaluation (UC-FA-04), upgrade, impairment, partial dismantle (UC-FA-06)
- Route: `POST/PUT /api/v1/fa/assets/{id}/adjust`, `POST .../revalue`
- Tests: 10 tests

### Task 2.2: FA Transfer

- Transfer between departments/cost centers (UC-FA-05)
- Route: `POST /api/v1/fa/assets/{id}/transfer`
- Tests: 6 tests

### Task 2.3: FA Inventory

- Physical count upload, automatic discrepancy detection (UC-FA-08)
- Route: `POST /api/v1/fa/inventories`, `GET /api/v1/fa/inventories/{id}`
- Tests: 8 tests

### Task 2.4: Biological Assets

- TK 215 management (UC-FA-09)
- Growth stage transitions, harvest, provision (TK 2295)
- Route: `POST/GET /api/v1/fa/biological-assets`
- Tests: 10 tests

**Checkpoint**: All 12 use cases implemented and tested.

---

## Phase 3: Reporting & Integration (Week 9-10)

### Task 3.1: FA Reports (UC-FA-10)

- 6 reports: fa_ledger, depreciation_schedule, fa_movement, asset_card, inventory_report, depreciation_allocation
- HTML/JSON/PDF/XLSX formats
- Jinja2 templates with i18n `{% trans %}`
- Tests: 12 tests

### Task 3.2: Period Gating Integration

- Depreciation blocked for closed periods
- FA acquisition blocked for closed periods
- Integration with `AccountingPeriodModel`
- Tests: 4 tests

### Task 3.3: AP/GL Integration

- FA acquisition from AP invoice (auto-create asset on AP posting)
- GL reconciliation: FA subsidiary vs GL account balances
- Tests: 6 tests

### Task 3.4: TT 99/2025 COA Migration (UC-FA-12)

- Migration script: 441/466 → 4118, 211 biological → 215, 2413 rename
- Route: `POST /api/v1/fa/migrate-to-tt99`
- Tests: 4 tests

**Checkpoint**: All reports render in 3 formats, integration tests pass.

---

## Phase 4: Polish & Hardening (Week 11-12)

### Task 4.1: IFRS Conversion (UC-FA-11)

- Basic IFRS parallel tracking
- Revaluation model support
- Route: `POST /api/v1/fa/ifrs-conversion`
- Tests: 4 tests

### Task 4.2: Audit Trail Enhancement

- Full lifecycle audit: every state change with before/after JSON snapshot
- Route: `GET /api/v1/fa/assets/{id}/audit-log`
- Tests: 4 tests

### Task 4.3: Performance & Edge Cases

- Bulk import/export optimization
- 100+ concurrent depreciation runs
- Edge case tests (zero residual value, max useful life, mid-month transfers, partial-period depreciation)
- Tests: 12 edge case tests

### Task 4.4: Final Hardening

- Security review (permission assertions on every endpoint)
- i18n completeness check (all error codes translated)
- Full regression test suite

**Checkpoint**: All tests pass, security review clean, i18n complete.

---

## Summary: Test Plan

| Component | Tests |
|-----------|-------|
| Domain entities + validation | 20 |
| Category CRUD | 8 |
| Asset CRUD + acquisition | 15 |
| Depreciation (3 methods) | 12 |
| Disposal | 8 |
| Adjustments (revalue/upgrade/impair) | 10 |
| Transfer | 6 |
| Inventory | 8 |
| Biological assets | 10 |
| Reports | 12 |
| Period gating | 4 |
| AP/GL integration | 6 |
| TT 99 migration | 4 |
| IFRS conversion | 4 |
| Audit trail | 4 |
| Edge cases | 12 |
| **TOTAL** | **143** |

---

## File Creation Order

```
Week 1-2:
  domain/fa.py
  domain/__init__.py (update)
  domain/i18n.py (update)
  infrastructure/models/fa_models.py
  migrations/versions/9fa1b2c3d4e5_fa_tables.py

Week 3-5:
  infrastructure/repositories/fa_repository.py
  use_cases/fa/__init__.py
  presentation/fa_routes.py

Week 6-8:
  (additions to existing files above)

Week 9-10:
  templates/fa_reports/*.html
  (report generation additions)

Week 11-12:
  (hardening, integration tests, edge cases)
  tests/test_fa_domain.py
  tests/test_fa_integration.py
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| TT 99/2025 interpretation ambiguity | Medium | High | MOF official guidance, VACPA consultation |
| Depreciation calculation inaccuracies | Low | Critical | Double-check with independent calculator per method |
| Biological asset scope confusion (211 vs 215) | Medium | Medium | MOF Q&A ruling available (portal.mof.gov.vn) |
| IFRS convergence scope creep | High | Medium | Phase-lock: cost model only for Phase 1 |
| Performance with 10K+ assets | Low | Medium | Indexed queries, batch processing for depreciation |
| Legacy TT 200 data migration | Medium | High | Migration script with dry-run mode |

---

## Production Readiness Assessment

**Verdict**: NOT ready for production.

| Criterion | Status | Gap |
|-----------|--------|-----|
| FA lifecycle (acquire → depreciate → dispose) | ❌ | Zero code exists |
| TT 99/2025 COA compliance (215, 2295, 2414) | ❌ | Not implemented |
| Depreciation engine (3 methods) | ❌ | Not implemented |
| GL integration | ❌ | Not implemented |
| Period gating | ❌ | Not implemented |
| Audit trail | ❌ | Not implemented |
| Reports | ❌ | Not implemented |
| i18n (vi + en) | ❌ | Not implemented |
| Tests | ❌ | Not implemented |
| API endpoints | ❌ | Not implemented |

**Estimated MVP timeline**: 12-16 weeks with 1 senior developer + 1 QA.

**Blocking dependencies**: None. FA module is self-contained except for existing GL/AP/Period modules (all complete).
