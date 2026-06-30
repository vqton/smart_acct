# CCDC Module — Implementation Plan
## SmartACCT ERP — Công cụ, Dụng cụ (Tools & Equipment)

**Version:** 1.0
**Date:** 2026-06-30
**Author:** Lead BA (20+ yrs) + Chief Accountant (20+ yrs)

---

## 1. Architecture & File Mapping

Using existing SmartACCT pattern (see AGENTS.md):

```
domain/
  cc.py                    # CCDC domain entities + enums (Pydantic v2)
  __init__.py              # Add CCDC exports

infrastructure/
  models/
    cc_models.py           # SQLAlchemy models (all CCDC tables)
  repositories/
    cc_repository.py       # CCDC Repository (CRUD + allocation engine + reports)

use_cases/
  cc/                      # CCDC use cases subpackage (like coa/, fa/, ap/)
    __init__.py            # CCDCUseCases class (all 12 UC methods)

presentation/
  cc_routes.py             # Flask blueprint for CCDC REST API

tests/
  test_cc_domain.py        # Domain unit tests
  test_cc_integration.py   # Repository + use case integration + DB

migrations/
  versions/
    xxxx_ccdc_tables.py    # Migration for all CCDC tables
```

### File Count: 8 new files (plus migration)
| File | Est. Lines | Purpose |
|------|-----------|---------|
| domain/cc.py | 300 | Enums + Pydantic entities |
| domain/__init__.py | +15 | Add CCDC exports |
| infrastructure/models/cc_models.py | 250 | SQLAlchemy models |
| infrastructure/repositories/cc_repository.py | 700 | Repository |
| use_cases/cc/__init__.py | 800 | CCDCUseCases |
| presentation/cc_routes.py | 500 | Flask routes |
| tests/test_cc_domain.py | 300 | Domain tests |
| tests/test_cc_integration.py | 500 | Integration tests |
| migrations/versions/xxxx_ccdc.py | 60 | Migration script |
| **TOTAL** | **~3,425** | |

---

## 2. Domain Entities (domain/cc.py)

### Enums
```python
class CCDCAllocationMethod(str, Enum):
    ONE_TIME = "one_time"
    TWO_TIME = "two_time"
    MULTI_PERIOD = "multi_period"

class CCDCReceiptType(str, Enum):
    PURCHASE = "purchase"
    SELF_MADE = "self_made"
    CONTRIBUTION = "contribution"
    DONOR = "donor"
    INVENTORY_SURPLUS = "inventory_surplus"
    RETURN = "return"

class CCDCStatus(str, Enum):
    IN_STOCK = "in_stock"
    ISSUED = "issued"
    DISPOSED = "disposed"

class AllocationStatus(str, Enum):
    ACTIVE = "active"
    FULLY_ALLOCATED = "fully_allocated"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"

class DisposalType(str, Enum):
    SALE = "sale"
    SCRAP = "scrap"
    DONATION = "donation"
    THEFT = "theft"
    DESTRUCTION = "destruction"
    RETURN_TO_SUPPLIER = "return_to_supplier"

class InventoryDiscrepancyType(str, Enum):
    SURPLUS = "surplus"
    SHORTAGE = "shortage"
    DAMAGE = "damage"

class IssueType(str, Enum):
    PRODUCTION = "production"
    ADMIN = "admin"
    SALES = "sales"
    RENTAL = "rental"
    TRANSFER = "transfer"
```

### Pydantic Entities
```python
class CCDCCategory(BaseModel)
class ToolEquipment(BaseModel)       # CCDC master
class CCDCReceipt(BaseModel)
class CCDCReceiptLine(BaseModel)
class CCDCReceiptLine_Create(BaseModel)
class CCDCReceipt_Create(BaseModel)
class CCDCReceipt_Update(BaseModel)
class CCDCReceiptLine_Update(BaseModel)
class CCDCReceiptResponse(BaseModel)
class CCDCIssue(BaseModel)
class CCDCIssueLine(BaseModel)
class CCDCAllocation(BaseModel)
class CCDCAllocationLine(BaseModel)
class CCDCTransfer(BaseModel)
class CCDCInventory(BaseModel)
class CCDCInventoryLine(BaseModel)
class CCDCDisposal(BaseModel)
class CCDCDisposalLine(BaseModel)
```

### i18n Error Codes (add to domain/i18n.py)
~40 new codes: `CCDC_CATEGORY_CODE_EXISTS`, `CCDC_INSUFFICIENT_STOCK`, `CCDC_ALLOCATION_PERIOD_EXCEEDS_MAXIMUM`, etc.

---

## 3. DB Migration Plan

Create new migration `bf9c1d2e3f4a` (continuing chain after `9fa1b2c3d4e5`):

```sql
-- cc_categories
CREATE TABLE cc_categories (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name_vn VARCHAR(200) NOT NULL,
    description TEXT,
    parent_category_id INTEGER REFERENCES cc_categories(id),
    default_allocation_method VARCHAR(20) NOT NULL DEFAULT 'multi_period',
    default_useful_months INTEGER NOT NULL DEFAULT 12,
    account_sub_type VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- tool_equipment (CCDC master)
CREATE TABLE tool_equipment (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name_vn VARCHAR(500) NOT NULL,
    specification TEXT,
    category_id INTEGER REFERENCES cc_categories(id),
    unit_of_measure VARCHAR(50),
    quantity_in_stock DECIMAL(18,2) DEFAULT 0,
    unit_cost DECIMAL(18,2) DEFAULT 0,
    total_cost DECIMAL(18,2) GENERATED ALWAYS AS (quantity_in_stock * unit_cost) STORED,
    location VARCHAR(200),
    image_url TEXT,
    is_valuable_item BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'in_stock',
    custom_fields JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- cc_receipts
CREATE TABLE cc_receipts (
    id SERIAL PRIMARY KEY,
    receipt_date DATE NOT NULL,
    receipt_type VARCHAR(30) NOT NULL,
    document_ref VARCHAR(100),
    supplier_id INTEGER,         -- FK to ap_vendors
    warehouse_keeper_id INTEGER,
    total_amount DECIMAL(18,2) DEFAULT 0,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    gl_posting_id INTEGER,       -- FK to gl entries
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- cc_receipt_lines
CREATE TABLE cc_receipt_lines (
    id SERIAL PRIMARY KEY,
    receipt_id INTEGER REFERENCES cc_receipts(id),
    tool_equipment_id INTEGER REFERENCES tool_equipment(id),
    quantity DECIMAL(18,2) NOT NULL,
    unit_price DECIMAL(18,2) NOT NULL,
    vat_rate DECIMAL(5,2) DEFAULT 0,
    vat_amount DECIMAL(18,2) DEFAULT 0,
    total_line DECIMAL(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- cc_issues
CREATE TABLE cc_issues (
    id SERIAL PRIMARY KEY,
    issue_date DATE NOT NULL,
    issue_type VARCHAR(30) NOT NULL,
    department_id INTEGER,
    responsible_person_id INTEGER,
    allocation_method VARCHAR(20) NOT NULL,
    useful_months INTEGER DEFAULT 0,
    total_value DECIMAL(18,2) DEFAULT 0,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    gl_posting_id INTEGER,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- cc_issue_lines
CREATE TABLE cc_issue_lines (
    id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES cc_issues(id),
    tool_equipment_id INTEGER REFERENCES tool_equipment(id),
    quantity DECIMAL(18,2) NOT NULL,
    unit_price DECIMAL(18,2) NOT NULL,
    total_line DECIMAL(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    cost_account_id INTEGER   -- FK to COA (TK 6233/6273/6413/6423)
);

-- cc_allocations
CREATE TABLE cc_allocations (
    id SERIAL PRIMARY KEY,
    source_issue_id INTEGER REFERENCES cc_issues(id),
    tool_equipment_id INTEGER REFERENCES tool_equipment(id),
    total_value DECIMAL(18,2) NOT NULL,
    allocated_value DECIMAL(18,2) DEFAULT 0,
    remaining_value DECIMAL(18,2) GENERATED ALWAYS AS (total_value - allocated_value) STORED,
    method VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    useful_months INTEGER,
    monthly_amount DECIMAL(18,2),
    current_period_number INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active'
);

-- cc_allocation_lines (monthly detail)
CREATE TABLE cc_allocation_lines (
    id SERIAL PRIMARY KEY,
    allocation_id INTEGER REFERENCES cc_allocations(id),
    period_year INTEGER NOT NULL,
    period_month INTEGER NOT NULL,
    allocated_amount DECIMAL(18,2) NOT NULL,
    cost_account_id INTEGER,
    department_id INTEGER,
    gl_posting_id INTEGER,
    status VARCHAR(20) DEFAULT 'posted'
);

-- cc_transfers
CREATE TABLE cc_transfers (
    id SERIAL PRIMARY KEY,
    transfer_date DATE NOT NULL,
    from_department_id INTEGER,
    to_department_id INTEGER,
    from_warehouse VARCHAR(200),
    to_warehouse VARCHAR(200),
    responsible_person_from INTEGER,
    responsible_person_to INTEGER,
    status VARCHAR(20) DEFAULT 'draft',
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- cc_transfer_lines
CREATE TABLE cc_transfer_lines (
    id SERIAL PRIMARY KEY,
    transfer_id INTEGER REFERENCES cc_transfers(id),
    tool_equipment_id INTEGER REFERENCES tool_equipment(id),
    quantity DECIMAL(18,2) NOT NULL
);

-- cc_inventories
CREATE TABLE cc_inventories (
    id SERIAL PRIMARY KEY,
    count_date DATE NOT NULL,
    location VARCHAR(200),
    committee_members JSONB,
    status VARCHAR(20) DEFAULT 'in_progress',
    created_by INTEGER,
    approved_by INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- cc_inventory_lines
CREATE TABLE cc_inventory_lines (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER REFERENCES cc_inventories(id),
    tool_equipment_id INTEGER REFERENCES tool_equipment(id),
    book_quantity DECIMAL(18,2) NOT NULL,
    actual_quantity DECIMAL(18,2),
    damaged_quantity DECIMAL(18,2) DEFAULT 0,
    difference_type VARCHAR(20),
    difference_value DECIMAL(18,2) DEFAULT 0,
    handling_recommendation TEXT,
    gl_posting_id INTEGER
);

-- cc_disposals
CREATE TABLE cc_disposals (
    id SERIAL PRIMARY KEY,
    disposal_date DATE NOT NULL,
    disposal_type VARCHAR(30) NOT NULL,
    counterparty VARCHAR(500),
    proceeds_amount DECIMAL(18,2) DEFAULT 0,
    expense_amount DECIMAL(18,2) DEFAULT 0,
    approval_document_ref VARCHAR(100),
    approved_by INTEGER,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_by INTEGER,
    gl_posting_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- cc_disposal_lines
CREATE TABLE cc_disposal_lines (
    id SERIAL PRIMARY KEY,
    disposal_id INTEGER REFERENCES cc_disposals(id),
    tool_equipment_id INTEGER REFERENCES tool_equipment(id),
    quantity DECIMAL(18,2) NOT NULL,
    remaining_value DECIMAL(18,2) NOT NULL,
    proceeds DECIMAL(18,2) DEFAULT 0
);
```

---

## 4. Data Flow Diagrams

### CCDC Purchase → Receipt → Issue → Allocation

```
[Supplier] → Purchase Invoice → [CCDC Receipt] → Dr 153 / Cr 331
                                                → Stock Qty +
                                  ↓
[Department Request] → [CCDC Issue]
  ├── Allocation: One-Time   → Dr 6233/6273/6413/6423 / Cr 153 (full)
  ├── Allocation: Two-Time   → Dr 242 / Cr 153 (full)
  │                           → Dr cost / Cr 242 (50%)
  │                           → At return: Dr cost / Cr 242 (50%)
  └── Allocation: Multi-Period → Dr 242 / Cr 153 (full)
                                → Monthly: Dr cost / Cr 242 (value/n months)
                                  ↓
[CCDC Allocation Engine] → Monthly batch → Dr cost / Cr 242
                                  ↓
[Fully Allocated] → Status = fully_allocated
                                  ↓
[Physical Retirement / Write-off] → History archive
```

### Inventory Count → Discrepancy → GL Posting

```
[Physical Count] → Enter actual qty
       ↓
[Compare with Book] → Difference?
       ├── No diff → Close inventory (no GL)
       ├── Surplus → Dr 153 / Cr 711 (at fair value)
       ├── Shortage (identified) → Dr 138/334 / Cr 153
       └── Shortage (unidentified) → Dr 632 / Cr 153
              ↓
[Approve by Committee Chair] → [GL Posting] → Stock adjusted
```

---

## 5. Workflow Summary

```
┌─────────────────────────────────────────────────────┐
│  CCDC Lifecycle                                       │
│                                                       │
│  ┌─────────┐    ┌─────────┐    ┌──────────┐        │
│  │ RECEIPT │───→│  ISSUE  │───→│ALLOCATION│───→     │
│  │ (Nhập)  │    │ (Xuất)  │    │ (Phân bổ)│         │
│  └─────────┘    └─────────┘    └──────────┘         │
│       │              │               │               │
│       ▼              ▼               ▼               │
│  ┌─────────┐    ┌─────────┐    ┌──────────┐        │
│  │ Stock + │    │TK 242 +│    │Monthly   │        │
│  │ GL Post │    │GL Post │    │expense   │        │
│  └─────────┘    └─────────┘    └──────────┘        │
│                                                       │
│  ┌──────────┐    ┌───────────┐    ┌───────────┐    │
│  │TRANSFER  │    │ INVENTORY │    │ DISPOSAL  │    │
│  │(Điều ch.)│    │ (Kiểm kê) │    │ (Thanh lý)│    │
│  └──────────┘    └───────────┘    └───────────┘    │
│       │              │               │               │
│       ▼              ▼               ▼               │
│  ┌──────────┐    ┌───────────┐    ┌───────────┐    │
│  │ No GL    │    │ Gain/Loss │    │ Flush 242 │    │
│  │ Physical │    │ GL Post   │    │ GL Post   │    │
│  └──────────┘    └───────────┘    └───────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 6. Route API Design

All routes under `/api/v1/cc/`:

| Method | Path | UC | Description |
|--------|------|----|-------------|
| GET | /categories | 01 | List all categories |
| POST | /categories | 01 | Create category |
| GET | /categories/{id} | 01 | Get category detail |
| PUT | /categories/{id} | 01 | Update category |
| DELETE | /categories/{id} | 01 | Soft-delete category |
| GET | /items | 01 | List CCDC items |
| POST | /items | 01 | Create CCDC item |
| GET | /items/{id} | 01 | Get item detail |
| PUT | /items/{id} | 01 | Update item |
| DELETE | /items/{id} | 01 | Soft-delete item |
| GET | /receipts | 02 | List receipts |
| POST | /receipts | 02 | Create receipt |
| GET | /receipts/{id} | 02 | Get receipt detail |
| PUT | /receipts/{id} | 02 | Update receipt |
| POST | /receipts/{id}/post | 02 | Post receipt to GL |
| POST | /receipts/{id}/cancel | 02 | Cancel receipt |
| GET | /issues | 03 | List issues |
| POST | /issues | 03 | Create issue |
| GET | /issues/{id} | 03 | Get issue detail |
| PUT | /issues/{id} | 03 | Update issue |
| POST | /issues/{id}/post | 03 | Post issue to GL |
| POST | /issues/{id}/cancel | 03 | Cancel issue |
| POST | /allocations/run | 04 | Run monthly allocation batch |
| GET | /allocations | 04 | List allocations |
| GET | /allocations/{id} | 04 | Get allocation detail |
| POST | /returns | 05 | Return CCDC to warehouse |
| GET | /returns | 05 | List returns |
| POST | /transfers | 06 | Transfer CCDC |
| GET | /transfers | 06 | List transfers |
| GET | /transfers/{id} | 06 | Get transfer detail |
| POST | /inventories | 07 | Create inventory count |
| GET | /inventories | 07 | List inventory counts |
| GET | /inventories/{id} | 07 | Get inventory detail |
| PUT | /inventories/{id} | 07 | Update inventory results |
| POST | /inventories/{id}/approve | 07 | Approve inventory + post GL |
| POST | /disposals | 08 | Create disposal |
| GET | /disposals | 08 | List disposals |
| GET | /disposals/{id} | 08 | Get disposal detail |
| PUT | /disposals/{id} | 08 | Update disposal |
| POST | /disposals/{id}/approve | 08 | Approve disposal + post GL |
| GET | /reports/form-07-vt | 10 | Get Form 07-VT report |
| GET | /reports/ledger | 10 | Get CCDC ledger |
| GET | /reports/usage | 10 | Get CCDC usage by cost center |
| GET | /reports/allocation-schedule | 10 | Get future allocation schedule |
| GET | /reports/inventory-summary | 10 | Get inventory summary |
| GET | /responsibility/{person_id} | 11 | Get CCDC by responsible person |
| POST | /write-off | 12 | Write off fully-allocated CCDC |

**~45 endpoints total** — comparable to other modules (AP: 35, FA: 36, Cash: 23)

---

## 7. Testing Strategy

### Domain Tests (test_cc_domain.py) — ~80 tests
- Category code validation
- CCDC allocation method validation
- Receipt/issue line calculations
- Allocation engine math (1-time, 2-time, multi-period)
- Edge: useful_months = 0, negative qty, max 36 months
- Rounding errors in monthly allocation (last period adjusts)
- Inventory discrepancy calculation
- Disposal remaining value flush

### Integration Tests (test_cc_integration.py) — ~60 tests
- Full CCDC lifecycle: create category → receipt → issue → allocation → inventory → disposal
- GL posting for each transaction type
- Multi-period allocation over N months
- Return to warehouse + allocation reversal
- Transfer between departments (no GL)
- Inventory surplus/shortage → GL
- Disposal with gain/loss
- Cancellation with GL reversal
- Batch allocation engine (run for month, verify lines)
- Edge cases: mid-month issue allocation, early termination

**Total: ~140 tests** — comparable to FA module (173 tests)

---

## 8. Migration & Go-Live

### Data Migration from Legacy
1. Export CCDC opening balances from legacy system:
   - In-stock items: qty × unit_cost = value
   - Issued but unallocated: transfer to TK 242 with remaining schedule
   - Fully allocated but in use: optional — register in physical tracking
2. Bulk import via POST /cc/items + POST /cc/receipts (opening balance type)

### Go-Live Checklist
- [ ] All 12 use cases implemented
- [ ] All 45 routes operational
- [ ] 140 tests passing (domain + integration)
- [ ] i18n error codes registered in domain/i18n.py
- [ ] Vietnamese + English translations in .po files
- [ ] TT 99/2025 compliance verified
- [ ] GL posting matrix verified (every transaction type)
- [ ] Allocation engine tested for 36-month edge case
- [ ] Form 07-VT matches TT 99 template
- [ ] API documentation completed
- [ ] Legacy data migration executed

### Production Readiness Gate Check
| Gate | Criteria | Status |
|------|----------|--------|
| P1 | All domain tests pass | ❌ |
| P2 | All integration tests pass | ❌ |
| P3 | GL posting verified for all transaction types | ❌ |
| P4 | TT 99 compliance verified by Chief Accountant | ❌ |
| P5 | Allocation engine mathematically verified | ❌ |
| P6 | Reports match TT 99 templates | ❌ |
| P7 | i18n complete (VI + EN) | ❌ |
| P8 | Performance: 10K CCDC items, 100K allocation lines | ❌ |
| P9 | Security: role-based access enforced | ❌ |
| P10 | Audit trail: all transactions logged | ❌ |

**CURRENT: FAIL — Not Production Ready**

---

## 9. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| TT 99 sub-account flexibility causes inconsistent implementation across clients | Medium | Medium | Provide default sub-accounts, document customization process |
| Allocation engine rounding errors over 36 months | Low | Medium | Use DECIMAL(18,2), last period adjusts rounding difference |
| Legacy data migration clean (opening balances) | Medium | High | Build validation script, trial run before go-live |
| Confusion between CCDC (this module) and FA spare parts | Medium | Low | Clear boundary in UI: CCDC for <30M, FA spare parts for ≥30M |
| Performance: monthly allocation batch with 10K+ active allocations | Low | Medium | Batch processing with chunking, index on cc_allocations(start_date, end_date, status) |
| User resistance to physical tracking (responsibility) | Medium | Low | Start with departments, phase in individual tracking |

---

## 10. Dependencies

| Dependency | Module | Status | Required For |
|-----------|--------|--------|-------------|
| Chart of Accounts | COA | ✅ Complete | Get TK 153, 242, cost accounts |
| GL posting | GL | ✅ Complete | All CCDC→GL entries |
| Period management | GL | ✅ Complete | Period-gated posting |
| Vendor master | AP | ✅ Complete | Supplier reference for purchase receipt |
| Fixed Assets | FA | ✅ Complete | TSCĐ/CCDC boundary determination |
| User/Employee | HR (future) | ❌ Future | Responsible person tracking (use simple ID for now) |
| Department | GL | ✅ Complete | Cost center/department tracking |
