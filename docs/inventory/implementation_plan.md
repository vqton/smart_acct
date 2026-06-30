# Inventory Module — Implementation Plan
## SmartACCT ERP — Vietnamese Accounting System

**Version:** 1.0
**Date:** 2026-06-30
**Estimate:** 75 team-days (3 developers × 5 weeks, or 2 developers × 7.5 weeks)
**Dependencies:** COA, GL module complete; AP module (for purchase linkage) preferred

---

## Phase 1: Foundation (Week 1-2 | ~20 team-days)

### Task 1.1 — Domain Entities + Enums
**Files:** `domain/inventory.py`
- Dev: All entities (InventoryItem, Warehouse, WarehouseBin, StockCard, InventoryTransaction, TransactionLine, CostLayer, InventoryCount, CountLine, InventoryProvision, ProductionBatch)
- Dev: Enums (ValuationMethod, InventoryType, TransactionType, WarehouseType, CountStatus, BatchStatus)
- Dev: Pydantic validators (positive qty, positive price, code format, balance check)
- Dev: i18n error codes (cf. `domain/i18n.py` pattern)
- Test: 20+ domain unit tests (validation rules, enum logic, default values)
- **Verify:** `pytest tests/test_inventory_domain.py -v — 20 tests pass`

### Task 1.2 — SQLAlchemy Models
**Files:** `infrastructure/models/inventory_models.py`, migration script
- Dev: All 10+ SQLAlchemy models matching domain entities
- Dev: Foreign keys, indexes, unique constraints
- Dev: Relationship definitions
- Dev: Alembic migration (`inventory_tables`)
- Test: Model creation, relationship loading
- **Verify:** `alembic upgrade head` — tables created in DB

### Task 1.3 — Repository Layer
**Files:** `infrastructure/repositories/inventory_repository.py`
- Dev: InventoryRepository class
- Dev: CRUD for InventoryItem, Warehouse, StockCard
- Dev: Transaction CRUD (create_transaction, get_transaction, post_transaction)
- Dev: CostLayer management (get_layers_for_item, consume_layer, create_layer, recalc_wac)
- Dev: InventoryCount CRUD + discrepancy calculation
- Dev: Provision CRUD + calculation
- Dev: ProductionBatch CRUD + WIP cost tracking
- Dev: StockCard get/update (period-based)
- Dev: GL reconciliation query
- Test: 30+ integration tests (all CRUD, FIFO layer consumption, WAC recalc, count discrepancy)
- **Verify:** `pytest tests/test_inventory_integration.py -v — 30 tests pass`

---

## Phase 2: Core Transactions (Week 2-3 | ~20 team-days)

### Task 2.1 — Inventory Master + Warehouse Use Cases
**Files:** `use_cases/inventory/__init__.py`
- Dev: UC-HTK-01 (Inventory Master) — CRUD, import, clone
- Dev: UC-HTK-02 (Warehouse) — CRUD, deactivate
- Test: 10+ integration tests (valid/invalid data, import, deactivate rules)
- **Verify:** `pytest tests/test_inventory_integration.py -v — new tests pass`

### Task 2.2 — Goods Receipt + Issue Use Cases
**Files:** `use_cases/inventory/__init__.py`
- Dev: UC-HTK-03 (Purchase Receipt) — PO-linked + direct, import, 3-way match support
- Dev: UC-HTK-04 (Production Receipt) — batch completion
- Dev: UC-HTK-05 (Production Issue) — cost layer consumption
- Dev: UC-HTK-06 (Sale Issue) — COGS at FIFO/WAC/Specific ID
- Test: 25+ integration tests (all transaction types, cost layer integrity)
- **Verify:** `pytest tests/test_inventory_integration.py -v — 35 total tests pass`

### Task 2.3 — Transfer + Goods in Transit
**Files:** `use_cases/inventory/__init__.py`
- Dev: UC-HTK-07 (Transfer) — source→dest, cost carryover
- Dev: UC-HTK-08 (Goods in Transit) — TK 151 tracking, aging alert, receipt
- Test: 8+ integration tests
- **Verify:** `pytest — 43 total tests pass`

### Task 2.4 — Inventory Valuation Engine
**Files:** `use_cases/inventory/__init__.py` (UC-HTK-09)
- Dev: FIFO engine (layer creation + consumption, multi-layer issue)
- Dev: WAC perpetual engine (recalc on receipt, apply on issue)
- Dev: WAC periodic engine (period-end recalc)
- Dev: Specific ID engine (lot selection at issue)
- Test: 15+ tests (FIFO multi-layer, WAC drift, specific ID edge cases)
- **Verify:** `pytest — 58 total tests pass`

---

## Phase 3: Advanced Features (Week 3-4 | ~18 team-days)

### Task 3.1 — Inventory Counting
**Files:** `use_cases/inventory/__init__.py` (UC-HTK-10)
- Dev: Count creation, sheet generation
- Dev: Physical entry, discrepancy calculation
- Dev: Surplus/shortage/damage resolution
- Dev: Approval workflow (KTT → GĐ escalation)
- Dev: Adjustment posting → GL
- Test: 8+ integration tests
- **Verify:** `pytest — 66 tests pass`

### Task 3.2 — Provision Engine
**Files:** `use_cases/inventory/__init__.py` (UC-HTK-11)
- Dev: NRV test per item
- Dev: Provision calc → adjustment (provision vs reversal)
- Dev: Provision schedule report
- Dev: Post to GL
- Test: 6+ tests (provision calc, reversal, edge case: cost = NRV)
- **Verify:** `pytest — 72 tests pass`

### Task 3.3 — WIP / Manufacturing Cost
**Files:** `use_cases/inventory/__init__.py` (UC-HTK-12)
- Dev: Cost collection (621/622/627 → 154)
- Dev: Overhead allocation (labor hours, machine hours, qty)
- Dev: Batch completion → FG (154 → 155)
- Dev: By-product handling
- Test: 8+ tests (cost collection, allocation, joint products)
- **Verify:** `pytest — 80 tests pass`

### Task 3.4 — Auto-GL Posting
**Files:** `use_cases/inventory/__init__.py` (UC-HTK-13)
- Dev: Transaction → GL mapping engine
- Dev: Period validation (open/close check)
- Dev: Post validation (Dr=Cr, account type check)
- Dev: Rollback on failure
- Test: 10+ tests (all transaction types, GL validation)
- **Verify:** `pytest — 90 tests pass`

---

## Phase 4: Reports + Routes + Close (Week 4-5 | ~17 team-days)

### Task 4.1 — Inventory Reports
**Files:** `use_cases/inventory/__init__.py` (UC-HTK-14)
- Dev: R01 Stock Card
- Dev: R02 Form 01-VT/02-VT
- Dev: R03 Form 05-VT count report
- Dev: R04 Inventory Aging
- Dev: R05 Slow-moving report
- Dev: R06 Inventory Turnover
- Dev: R07 ABC Analysis
- Dev: R08 Provision Schedule
- Dev: R09 WIP Status
- Dev: R10 GL-Stock Reconciliation
- Test: 12+ report tests
- **Verify:** `pytest — 102 tests pass`

### Task 4.2 — Month-End Close
**Files:** `use_cases/inventory/__init__.py` (UC-HTK-15)
- Dev: Pre-close validation checks
- Dev: Cost revaluation (if periodic WAC)
- Dev: GL reconciliation
- Dev: Period close
- Dev: Auto-open next period
- Test: 4+ tests (close sequence, rollback on failure)
- **Verify:** `pytest — 106 tests pass`

### Task 4.3 — API Routes
**Files:** `presentation/inventory_routes.py`, `presentation/inventory/__init__.py`
- Dev: All inventory endpoints (30-40 endpoints)
- Dev: JSON serializers for all entities
- Dev: Error handling + i18n resolution
- Dev: Blueprint registration (`/api/v1/inventory`)
- Dev: Route tests (Flask test client)
- Test: 40+ route tests
- **Verify:** `pytest — 146 tests pass`

### Task 4.4 — Edge Cases + Hardening
**Files:** Various
- Dev: Negative stock prevention (block vs override)
- Dev: Decimal precision handling (18,6)
- Dev: Foreign currency inventory purchase (landed cost)
- Dev: Concurrent transaction safety (locking)
- Dev: Performance optimization (cost layer query index)
- Test: 20+ edge case tests
- **Verify:** `pytest — 166+ tests pass`

---

## Test Suite Summary

| Phase | Tests | New | Cumulative |
|-------|-------|-----|------------|
| 1.1 Domain | 20 | 20 | 20 |
| 1.2 Models | 5 | 5 | 25 |
| 1.3 Repository | 30 | 30 | 55 |
| 2.1 Master | 10 | 10 | 65 |
| 2.2 Receipt/Issue | 25 | 25 | 90 |
| 2.3 Transfer/GIT | 8 | 8 | 98 |
| 2.4 Valuation Engine | 15 | 15 | 113 |
| 3.1 Counting | 8 | 8 | 121 |
| 3.2 Provision | 6 | 6 | 127 |
| 3.3 WIP | 8 | 8 | 135 |
| 3.4 GL Posting | 10 | 10 | 145 |
| 4.1 Reports | 12 | 12 | 157 |
| 4.2 Close | 4 | 4 | 161 |
| 4.3 Routes | 40 | 40 | 201 |
| 4.4 Edge Cases | 20 | 20 | 221 |

**Target: 221 tests** (comparable to FA module 173 and CCDC 69 — inventory is more complex)

---

## Risk Register

| Task | Risk | Mitigation |
|------|------|------------|
| 2.4 FIFO engine | Incorrect layer consumption order | Unit test: 15 multi-layer scenarios; SQl query: `ORDER BY receipt_date ASC, id ASC` |
| 2.4 WAC engine | Floating point drift over many transactions | Decimal(18,6); period-end reconciliation check against total cost |
| 3.1 Counting | Concurrent transaction during count | Lock warehouse during count; reject transactions through period-end |
| 3.3 WIP | Overhead allocation complexity | Start with simple labor-hour basis; add machine-hour later |
| 3.4 GL Posting | Dr≠Cr or wrong account type | Validation before posting; rollback on failure |
| 4.3 Routes | 40 endpoints = large surface | Standardized error handler; consistent JSON shape |
| All | Changing TT 99/2025 interpretation | Reference official MOF guidance; design configurable |

---

## Migration Strategy

1. Create new tables: `alembic upgrade head` (migration `inventory_tables`)
2. Seed: Default warehouse, standard inventory categories
3. Data import (optional): Excel-based SKU import
4. Go-live: Start with new transactions. No legacy data migration needed for v1.0.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Cost layer storage | Separate `cost_layers` table | FIFO requires tracking per-layer quantity; WAC uses same table with single layer |
| Valuation method per item | At inventory master level | Different items may need different methods (VAS 02 allows this) |
| GL posting | Real-time per transaction | Avoids period-end bottleneck; supports real-time inventory GL view |
| Inventory vs warehouse account | Account at item level, not warehouse | Simplifies GL mapping; warehouse sub-ledger tracks per-warehouse value |
| Negative stock | Configurable: block or override with warning | Some enterprises need override capability (with audit trail) |
| Transaction numbering | Separate sequence per type (PNK/PXK/CPK/BBKK) | Clear identification; matches Vietnamese convention |
| Multi-currency | Cost recorded in VND; foreign currency noted | VAS 02 requires VND valuation; exchange rate at receipt date |
