# Payroll Module — Implementation Plan

**Version**: 1.0  
**Date**: 2026-06-30  
**Phases**: 4 | **Duration**: ~16 weeks | **Total Tests Planned**: ~200

---

## Phase 1: Foundation (Weeks 1-4)

### Task 1.1: Domain Entities (Week 1)
**Files to create**: `domain/payroll.py`

Create Pydantic v2 entities with validators and i18n error codes:
- `Employee`, `EmployeeContract`, `EmployeeDependent`
- `Timesheet`, `PayrollRun`, `PayrollLine`
- `PITDeclaration`, `SIInsuranceRecord`
- `SalaryPayment`, `SalaryPaymentLine`
- `PayrollAdjustment`, `PayrollCostAllocation`
- Enums: `ContractType`, `PayrollRunStatus`, `PaymentMethod`, `Region`, `EmployeeStatus`

**Est**: 350 lines | **Tests**: 40 domain tests

### Task 1.2: DB Schema + Migration (Week 2)
**Files to create**: `infrastructure/models/payroll_models.py`
**Migration**: `2fa3b4c5d6e7` (payroll tables)

Create 12 SQLAlchemy tables:
1. `payroll_employees`
2. `payroll_employee_contracts`
3. `payroll_employee_dependents`
4. `payroll_timesheets`
5. `payroll_runs`
6. `payroll_run_lines`
7. `payroll_pit_declarations`
8. `payroll_si_records`
9. `payroll_salary_payments`
10. `payroll_salary_payment_lines`
11. `payroll_adjustments`
12. `payroll_audit_logs`

**Est**: 400 lines | **Migration**: 200 lines

### Task 1.3: Repository Layer (Week 3-4)
**Files to create**: `infrastructure/repositories/payroll_repository.py`

Implement CRUD + business queries:
- Employee CRUD (create/get/update/deactivate/search/bulk_import)
- Contract CRUD (create/amend/terminate/get_active)
- PayrollRun CRUD (create/get/compute/approve/cancel)
- PayrollLine queries (by_run/by_employee)
- PIT & SI declaration CRUD
- Utility queries (get_by_department, get_by_period, total_by_account)

**Est**: 700 lines | **Tests**: 30 integration tests (DB)

---

## Phase 2: Core Payroll Engine (Weeks 5-8)

### Task 2.1: Timesheet Import (Week 5)
**File to create**: `use_cases/payroll/__init__.py` (timesheet section)

Implement:
- Excel/CSV import with validation
- Direct entry API
- Auto-calculation of standard days

**Est**: 150 lines | **Tests**: 15 integration tests

### Task 2.2: Payroll Computation Engine (Weeks 6-7)
**File**: `use_cases/payroll/__init__.py` (computation section)

Critical path — implement with TDD:
1. Gross salary computation (base × attendance ratio + overtime)
2. SI base determination (per Decree 158/2025)
3. Employee SI/HI/UI deduction calculation
4. Taxable income formula
5. PIT engine (5-bracket progressive)
6. Employer cost calculation
7. Net pay computation
8. Rounding rules (VND rounding to whole number)
9. Validation: balance check (gross = net + deductions)
10. Parallel test against Excel-calculated values

**Est**: 500 lines | **Tests**: 50 tests (unit + integration)

### Task 2.3: PIT & SI Declaration (Week 8)
**File**: `use_cases/payroll/__init__.py` (declaration section)

Implement:
- Monthly PIT declaration generation (05/KK-TNCN format)
- Quarterly PIT declaration aggregation
- SI declaration generation (TK1-TS format)
- XML/CSV export for HTKK and eBHXH
- Dual-bracket support for 2026 transition

**Est**: 300 lines | **Tests**: 25 tests

---

## Phase 3: Payment, GL & Reports (Weeks 9-12)

### Task 3.1: Salary Payment (Week 9)
**File**: `use_cases/payroll/__init__.py` (payment section)

Implement:
- Bank file generation (multi-format support)
- Cash payment integration with Cash module
- Payment status tracking
- Failed payment retry logic

**Est**: 200 lines | **Tests**: 15 tests

### Task 3.2: GL Posting (Week 10)
**File**: `use_cases/payroll/__init__.py` (gl section)

Implement:
- GL entry generation from PayrollRun
- Cost allocation by department type
- Integration with GLUseCases.create_entry()
- Validation: balanced entry check
- Accrual/reversal for cross-period allocation

**Est**: 200 lines | **Tests**: 15 tests

### Task 3.3: Reports (Week 11)
**Files to create**: `templates/payroll/` (Jinja2 templates)

Implement reports:
- Payroll Summary (HTML + PDF via WeasyPrint)
- Payroll Detail (HTML + PDF)
- SI Declaration Detail (Excel)
- PIT Declaration Detail (Excel)
- Cost Allocation Report
- Payroll Register
- Dashboard KPIs

**Est**: 400 lines (templates) + 200 lines (routes) | **Tests**: 10 tests

### Task 3.4: Routes & API (Week 12)
**Files to create**: `presentation/payroll/__init__.py`, `presentation/payroll/routes.py`

Implement REST endpoints (30+ endpoints):
```
POST/GET /api/v1/payroll/employees
GET/PUT/DELETE /api/v1/payroll/employees/{id}
POST /api/v1/payroll/employees/import
POST/GET /api/v1/payroll/contracts
GET /api/v1/payroll/contracts/active
POST /api/v1/payroll/timesheet/import
POST /api/v1/payroll/runs
GET /api/v1/payroll/runs/{period}
POST /api/v1/payroll/runs/{id}/compute
POST /api/v1/payroll/runs/{id}/approve
POST /api/v1/payroll/runs/{id}/pay
POST /api/v1/payroll/runs/{id}/gl-post
GET /api/v1/payroll/runs/{id}/reports/{type}
GET /api/v1/payroll/pit/{period}
POST /api/v1/payroll/pit/{period}/submit
GET /api/v1/payroll/si/{period}
POST /api/v1/payroll/si/{period}/submit
GET /api/v1/payroll/reports/summary
GET /api/v1/payroll/reports/cost-allocation
GET /api/v1/payroll/dashboard
```

**Est**: 500 lines (routes) + 100 lines (blueprint + serializers) | **Tests**: 20 route tests

---

## Phase 4: Advanced Features (Weeks 13-16)

### Task 4.1: Annual PIT Finalization (Week 13)
- Annual data aggregation
- Over/under withholding computation
- 05/QTT-TNCN form generation
- Appendices 05-1, 05-2, 05-3 generation

**Est**: 250 lines | **Tests**: 15 tests

### Task 4.2: Employee Self-Service (Week 14)
- Payslip view/download
- PIT/SI history
- Withholding certificate download
- Dependent registration
- Salary advance request

**Est**: 300 lines | **Tests**: 10 tests

### Task 4.3: Adjustments & Retroactive (Week 15)
- Adjustment run creation
- Delta computation
- Retroactive SI/PIT recalculation
- GL adjustment posting

**Est**: 200 lines | **Tests**: 15 tests

### Task 4.4: Audit Trail & Compliance (Week 16)
- Audit event logging across all payroll actions
- Compliance check reports
- Data retention enforcement
- Final integration testing

**Est**: 150 lines | **Tests**: 10 tests

---

## Summary: Size & Effort

| Component | Files | Lines (est) | Tests | Weeks |
|-----------|-------|-------------|-------|-------|
| Domain (`domain/payroll.py`) | 1 | 350 | 40 | 1 |
| DB Models + Migration | 2 | 600 | — | 1 |
| Repository | 1 | 700 | 30 | 2 |
| Use Cases (`use_cases/payroll.py`) | 1 | 1,500 | 120 | 4 |
| Routes + Blueprint | 2 | 600 | 20 | 1 |
| Jinja2 Templates | 5 | 400 | 10 | 1 |
| **Total** | **12** | **4,150** | **~200** | **16** |

---

## Architecture & File Layout

Following existing SmartACCT conventions:

```
domain/
  payroll.py              ← Pydantic entities + enums

infrastructure/
  models/
    payroll_models.py     ← SQLAlchemy models (12 tables)
  repositories/
    payroll_repository.py ← CRUD + business queries

use_cases/
  payroll.py              ← PayrollUseCases class (all methods)

presentation/
  payroll/
    __init__.py           ← Blueprint (blueprint = 'payroll', /api/v1/payroll)
    routes.py             ← 30+ REST endpoints

templates/
  payroll/
    payroll_summary.html
    payroll_detail.html
    payslip.html
    cost_allocation.html
    si_declaration.html
    pit_declaration.html

tests/
  test_payroll_domain.py    ← 40 domain unit tests
  test_payroll_integration.py  ← ~160 integration tests
```

---

## Key Dependencies

- **GL Module**: `use_cases/gl/__init__.py` — GLUseCases.create_entry() for payroll GL posting
- **Cash Module**: `use_cases/cash/__init__.py` — CashUseCases for salary payment recording
- **COA Module**: Account validation for TK 334, 338, 333, 622, 627, 641, 642
- **Period Module**: Period validation for payroll period and GL period
- **i18n**: `domain/i18n.py` for all error codes; `translations/` for locale support

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| PIT Law 109 implementing decree delayed | Config-driven bracket table; use current law + placeholders for undefined details |
| SI rates change | Store rates in DB (config table), not hardcoded |
| eBHXH API not available | Generate XML for manual upload; async integration |
| Payroll calc bugs | Comprehensive test suite + parallel Excel comparison |
| Employee data volume | Pagination for list endpoints; batch processing for computations |
| Dual-regime transition | Support two bracket tables with effective dates |

---

## Testing Strategy

### Domain Tests (40)
- Test all entity validators (employee code, tax code, region, etc.)
- Test PIT engine with known values
- Test SI calculation for all rate combinations
- Test edge cases: zero salary, max SI base, negative net pay handler

### Integration Tests (160)
- Repository CRUD for all 12 tables
- Payroll computation flow (full cycle)
- PIT declaration generation
- SI declaration generation
- GL posting flow
- Payment processing
- Adjustment flows
- Error handling: missing data, validation failures, duplicate runs

### TDD Approach
Red → Green → Refactor per established SmartACCT pattern:
1. Write failing test
2. Implement minimal code
3. Refactor while tests stay green
4. Document edge cases discovered during testing

---

## Regulatory Config (to be DB-stored)

```python
# Default config values (configurable via admin UI)
PAYROLL_CONFIG = {
    "standard_working_days": 26,
    "regional_minimum_wage": {
        "region_1": 5310000,
        "region_2": 4730000,
        "region_3": 4140000,
        "region_4": 3700000
    },
    "si_max_base_multiplier": 20,
    "reference_level": 2530000,  # From 01/07/2026
    "si_rates": {
        "employer_retirement": 0.14,
        "employer_sickness": 0.03,
        "employer_occupational": 0.005,
        "employer_health": 0.03,
        "employer_unemployment": 0.01,
        "employer_union": 0.02,
        "employee_retirement": 0.08,
        "employee_health": 0.015,
        "employee_unemployment": 0.01
    },
    "pit_personal_relief": 15500000,  # Resolution 110
    "pit_dependent_relief": 6200000,   # Resolution 110
    "pit_brackets": [
        {"max": 10000000, "rate": 0.05},
        {"max": 30000000, "rate": 0.10},
        {"max": 60000000, "rate": 0.20},
        {"max": 100000000, "rate": 0.30},
        {"max": None, "rate": 0.35}  # Above 100M
    ],
    "pit_non_resident_rate": 0.20,
    "pit_seasonal_rate": 0.10,  # <3 month contracts > 500K
    "payment_deadline_si": "last_day_of_following_month",
    "payment_deadline_pit_monthly": 20,  # 20th of following month
    "payment_deadline_pit_quarterly": 30,  # last day of following quarter
    "late_payment_interest_daily": 0.0003  # 0.03%/day
}
```

---

## References

- BRD: `docs/payroll/PAYROLL_BRD.md`
- Use Cases: `docs/payroll/use_cases.md`
- AGENTS.md project architecture guide
- Existing module patterns: AR (`domain/ar.py`, `presentation/ar/`), FA (`domain/fa.py`, `presentation/fa/`)

---

*End of Implementation Plan*
