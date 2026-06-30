# BRD: Costing Center Module (Trung tâm chi phí)

**Version**: 1.0
**Date**: 2026-06-30
**Author**: BA Lead + Chief Accountant (20+ yrs)
**Status**: Draft — NOT PRODUCTION-READY

---

## 0. Executive Summary: PROD-READY ASSESSMENT

### SCORE: 0/5 — NOT PRODUCTION-READY

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Domain entities | ❌ MISSING | Only `CostCenter` enum in `domain/payroll.py` (6 hardcoded values: 622, 627, 641, 642, 241, 623) |
| DB models/tables | ❌ MISSING | No costing_center table, no cost_allocation, no cost_driver, no hierarchy |
| Repository | ❌ MISSING | No `costing_center_repository.py` |
| Use cases | ❌ MISSING | No `use_cases/costing_center/` |
| Routes | ❌ MISSING | No endpoints |
| Tests | ❌ MISSING | No test files |
| Regulatory compliance | ⚠️ PARTIAL | TT99/2025 Art.11 allows enterprise COA autonomy; cost center as analytical segment required |
| Integration | ❌ MISSING | No GL/AP/AR/FA/Inventory/Payroll/Budget integration |

### Key Gaps vs PROD Requirements

1. **No cost center hierarchy** — tree structure with parent/child, levels, cost center managers
2. **No cost allocation engine** — no methods (direct/step-down/reciprocal/ABC), no allocation bases, no drivers
3. **No cost object tracking** — no product/project/order costing, no cost accumulation
4. **No budget integration** — budget module exists as domain entities but zero implementation
5. **No GL integration** — no automatic posting rules, no segment dimension in journal entries
6. **No reporting** — no cost center P&L, no variance analysis, no allocation reports
7. **No multi-currency** — no FX handling for cross-border cost centers
8. **No audit trail** — no costing_center_audit_log table

---

## 1. Objective

Build a **Costing Center (Trung tâm chi phí)** module enabling Vietnamese enterprises to:

- Define cost center hierarchy per organizational structure
- Track costs by responsibility center (cost center, profit center, investment center)
- Allocate indirect costs using multiple methods (direct, step-down, reciprocal, ABC)
- Analyze cost variances (budget vs actual, period-over-period)
- Generate management accounting reports (cost center P&L, allocation summary, driver analysis)
- Comply with TT99/2025/TT-BTC (effective 01/01/2026) analytical segment requirements

### Legal Basis

| Reference | Status | Relevance |
|-----------|--------|-----------|
| TT99/2025/TT-BTC | ACTIVE from 01/01/2026 | COA autonomy Art.11; segment structure (đơn vị, trung tâm chi phí, sản phẩm, dự án); cost tracking requirement |
| TT133/2016/TT-BTC | ACTIVE (SMEs) | Simplified COA; SMEs may optionally follow TT99 |
| TT200/2014/TT-BTC | REPLACED by TT99 (eff 01/01/2026) | Legacy; only equitization content remains |
| VAS 01 — Chuẩn mực chung | ACTIVE | Matching principle, cost recognition |
| VAS 16 — Chi phí đi vay | ACTIVE | Borrowing cost allocation |
| Luật Kế toán 2015 (amended 2024) | ACTIVE | Art.10: accounting principles; internal control requirements |
| Decree 20/2025/ND-CP | ACTIVE from 27/03/2025 | Transfer pricing; cost allocation, EBITDA 30% cap |
| Decree 132/2020/ND-CP | ACTIVE | TP documentation; cost allocation justification |
| IFRS 8 — Operating Segments | REFERENCE | Segment reporting; cost allocation principles |
| IFRS 15 — Revenue from Contracts | REFERENCE | Cost allocation to performance obligations |
| IFRS 9 — Financial Instruments | REFERENCE | Cost allocation for ECL provisioning |

### Key Regulatory Changes in TT99/2025 (effective 01/01/2026)

1. **COA Autonomy** (Art.11): Enterprises may amend COA from Level 2 onwards without MOF pre-approval, provided they issue an internal Accounting Policy Regulation
2. **Segment Structure**: COA must support analytical segments: unit (đơn vị), cost center (trung tâm chi phí), product (sản phẩm), project (dự án)
3. **Cost Tracking by Element**: Mandatory tracking by nature (labor, materials, outsourcing, depreciation)
4. **Expense Classification**: By nature (recommended) or by function — must be consistent
5. **Prepaid Expenses (TK 242)**: Renamed "Chi phí chờ phân bổ" — allocation period based on economic benefit
6. **Standard Cost Method**: Introduced for inventory valuation
7. **Internal Control Requirement**: Enterprise must issue internal accounting regulations
8. **Digital Auditability**: Full digital traceability required

---

## 2. Scope

### In Scope (Phase 1 — MVP)

| ID | Feature | Priority |
|----|---------|----------|
| CC-01 | Cost center hierarchy CRUD (tree structure, parent/child, levels) | P0 |
| CC-02 | Cost center types (cost/profit/investment) | P0 |
| CC-03 | Cost center manager assignment | P0 |
| CC-04 | Cost allocation rules (direct method) | P0 |
| CC-05 | Cost allocation execution engine | P0 |
| CC-06 | Cost driver management (quantity, rate) | P0 |
| CC-07 | Cost object registration (product/project/order) | P1 |
| CC-08 | Cost accumulation by cost object | P1 |
| CC-09 | GL integration — journal entry segmentation | P1 |
| CC-10 | Cost center P&L report | P1 |
| CC-11 | Allocation summary report | P1 |
| CC-12 | Variance analysis (budget vs actual) | P1 |
| CC-13 | Budget integration (read budget data) | P1 |
| CC-14 | Audit trail for all costing operations | P1 |
| CC-15 | Import/export cost center data (Excel/CSV) | P2 |

### Out of Scope (Phase 2+)

| Feature | Rationale |
|---------|-----------|
| ABC (Activity-Based Costing) | Complex; requires process mapping |
| Step-down / Reciprocal allocation | Sequential requires iteration solver |
| Multi-currency cost centers | FX volatility adds complexity |
| Transfer pricing module | Covered by separate TP compliance |
| IFRS segment reporting | Covered by separate IFRS convergence |
| Machine learning cost prediction | Advanced analytics |

---

## 3. Users & Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| Chief Accountant (Kế toán trưởng) | Full access — cost center design, allocation rules, approvals | ALL |
| Cost Accountant (Kế toán chi phí) | Execute allocations, maintain drivers, generate reports | CC-04 to CC-15 |
| Cost Center Manager (Trưởng bộ phận) | View own cost center data, input actuals, submit budget input | Read own + input actuals |
| Finance Director (Giám đốc tài chính) | Approve allocation rules, view all reports | Read ALL + approve rules |
| Auditor (Kiểm toán) | Read-only audit trail | Read audit logs |

---

## 4. Data Model (Conceptual)

### Core Entities

```
CostCenter
├── id, code, name, type (cost/profit/investment)
├── parent_id (self-referencing hierarchy)
├── level (1-based depth)
├── manager_employee_id
├── department_id (FK→department)
├── gl_account_code (default cost account)
├── budget_control_level (none/warning/soft/hard)
├── is_active, is_cost_collector
├── valid_from, valid_to (effective dating)
└── accounting_policy_ref (Link to TT99 policy document)

CostDriver
├── id, code, name
├── driver_type (quantity/percentage/rate/actual)
├── source_module (GL/HR/Production/Sales)
├── source_account_code
├── is_active
└── unit_of_measure

CostAllocationRule
├── id, rule_code, rule_name
├── source_cost_center_id (allocating FROM)
├── target_cost_center_ids (allocating TO)
├── driver_id (FK→CostDriver)
├── allocation_method (direct/percentage/proportional)
├── percentage_value (for fixed %)
├── effective_from, effective_to
├── priority_order
├── approval_status (draft/approved/active/archived)
├── created_by, approved_by
└── notes

CostAllocationRun
├── id, run_code
├── period_key (YYYYMM)
├── fiscal_year, period_month
├── run_date, run_by
├── status (draft/posted/reversed)
├── total_allocated_amount
└── notes

CostAllocationLine
├── id, run_id
├── source_cost_center_id
├── target_cost_center_id
├── rule_id
├── driver_id
├── gl_account_code
├── original_amount
├── allocated_amount
├── driver_quantity, driver_rate
└── allocation_basis_description

CostObject
├── id, code, name
├── object_type (product/project/order/campaign/customer)
├── parent_object_id
├── gl_account_code
├── is_active
└── custom_attributes (JSON)

CostAccumulation
├── id
├── cost_object_id
├── source_cost_center_id
├── gl_account_code
├── period_key
├── direct_cost_amount
├── allocated_cost_amount
├── total_cost_amount
└── cost_type (direct/indirect)

CostCenterBudget
├── id, cost_center_id
├── fiscal_year, period_key
├── gl_account_code
├── budget_amount
├── budget_version_id
├── revised_amount
└── notes

CostCenterActual
├── id, cost_center_id
├── period_key, gl_account_code
├── actual_amount (from GL)
├── commitment_amount (from PO/AP)
├── allocated_amount (from CC module)
└── source_reference (JE ID, PO ID, AP ID)

CostCenterVariance
├── id, cost_center_id
├── period_key, gl_account_code
├── budget_amount, actual_amount
├── variance_amount, variance_pct
├── variance_type (favorable/unfavorable)
└── annotation

CostingAuditLog
├── id
├── entity_type (cost_center/rule/driver/run)
├── entity_id
├── action (create/update/delete/approve/post/reverse)
├── changes (JSON diff)
├── actor
└── created_at
```

### GL Integration Design

```sql
-- Journal entries carry cost center dimension
CREATE TABLE journal_entry_lines (
    ...
    cost_center_id INTEGER REFERENCES cost_centers(id),
    cost_object_id INTEGER REFERENCES cost_objects(id),
    segment_string VARCHAR(100), -- "entity.cc.project.product"
    ...
);
```

---

## 5. Business Rules

### R1 — Hierarchy Rules
- Max 10 levels deep
- Code must be unique within parent
- Cannot delete cost center with children or active transactions
- Deactivation = soft delete; data preserved for historical reporting
- Effective dating: changes apply from next period + approval

### R2 — Allocation Rules
- No circular allocation (source → target → source) without explicit reciprocal method
- Total allocated = total source amount (no leakage)
- Allocation precision: 0 VND remainder handled by rounding to largest target
- Rule must be approved by Finance Director before execution
- Rule change requires re-allocation of current period

### R3 — Execution Rules
- One allocation run per period per rule group
- Execution order: by rule priority (lower number = earlier)
- Run status: Draft → Posted → (Reversed if error)
- Posted run locks the period for re-allocation
- Reversal creates reversing entries in GL

### R4 — Cost Object Rules
- Cost object can belong to multiple cost centers
- Direct cost = traced directly to object
- Indirect cost = allocated via rules
- Cost accumulation = sum of direct + allocated COGS + OPEX

### R5 — Period Rules
- Allocation runs must complete before period close
- Period close blocks allocation modification
- Prior-period allocation requires supplementary run
- Year-end: all allocations must balance → TK 911/421 carry

### R6 — Data Retention
- Cost center master: indefinite
- Allocation runs: 10 years (per Luật Kế toán Art.13)
- Drivers: 5 years
- Audit logs: 10 years

---

## 6. Integration Points

| Module | Integration Type | Description |
|--------|-----------------|-------------|
| GL | READ + WRITE | Read actuals by account+CC; write allocation journal entries |
| COA | READ | Validate GL accounts for cost centers |
| Budget | READ | Read budget amounts by CC+account for variance analysis |
| AP | READ | Cost center on PO/invoice lines for commitment tracking |
| AR | READ | Cost center on sales orders for revenue attribution |
| FA | READ | Depreciation by cost center for allocation |
| Inventory | READ | Cost center on receipt/issue for inventory cost tracking |
| Payroll | READ | Labor cost by cost center |
| CCDC | READ | Tools cost by cost center |
| Treasury | READ | Interest cost by cost center |

---

## 7. Report Matrix

| Report | Output | Frequency | Users |
|--------|--------|-----------|-------|
| Cost Center P&L (Báo cáo KQHĐKD theo TTCP) | HTML/PDF/Excel | Monthly | All |
| Allocation Summary (Bảng phân bổ chi phí) | HTML/PDF/Excel | Monthly | Cost Accountant |
| Cost Driver Analysis (Phân tích chi phí theo yếu tố) | HTML/PDF/Excel | Monthly | CFO |
| Variance Report (Phân tích chênh lệch) | HTML/PDF/Excel | Monthly | Cost Center Manager |
| Cost Object Costing (Tính giá thành) | HTML/PDF/Excel | Per batch | Cost Accountant |
| Cost Center Hierarchy (Sơ đồ TTCP) | HTML/PDF | Ad-hoc | Chief Accountant |
| Zero-Base Review (Rà soát chi phí gốc 0) | HTML/PDF/Excel | Annual | CFO |
| Inter-CC Recharge Summary | HTML/PDF/Excel | Monthly | Cost Accountant |

---

## 8. Compliance Matrix

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| TT99/2025 Art.11 COA Autonomy | Segment structure in COA | Cost center as analytical dimension on every JE line |
| TT99/2025 — Expense by nature | Track cost by nature element | Driver types mapped to GL accounts |
| TT99/2025 — Prepaid allocation | Systematic allocation method | Allocation rules engine |
| TT99/2025 — Internal control | Documented accounting policy | Rule approval workflow |
| TT99/2025 — Digital auditability | Full digital trace | CostingAuditLog table |
| Decree 20/2025 — EBITDA cap | 30% EBITDA interest cap | Cost allocation to EBITDA calculation |
| Luật Kế toán Art.13 | 10-year data retention | Archive strategy |
| VAS 01 — Matching | Cost matching revenue | Period-based allocation |
| IFRS 8 — Segments | Segment reporting | Cost center → operating segment mapping |

---

## 9. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Circular allocation infinite loop | HIGH | MEDIUM | Cycle detection in rule validation |
| Data integrity with GL out-of-sync | HIGH | MEDIUM | Re-allocation trigger; reconciliation report |
| Performance with large cost centers (1000+) | MEDIUM | LOW | Batch processing; indexed queries |
| User error in allocation % (over/under allocation) | MEDIUM | MEDIUM | Validation sum = 100%; remainder handling |
| Regulatory change (TT99 amendments) | MEDIUM | LOW | Configurable rule engine; versioned policies |
| Budget data unavailable | MEDIUM | LOW | Graceful fallback; variance = N/A marker |
| Multi-entity consolidation complexity | HIGH | LOW | Deferred to Phase 2 |

---

## 10. Success Criteria

1. Cost center hierarchy supports 10+ levels with 5000+ nodes
2. Allocation run completes under 5 minutes for 200 cost centers × 500 rules
3. Any allocation can be traced from source GL entry → driver → rule → target
4. Reports render in < 3 seconds for 1000+ cost centers
5. All TT99/2025 segment disclosure requirements met
6. No circular allocation possible (detection prevents creation)
7. Audit trail captures every CRUD + approve + post + reverse action
8. Zero data loss on reversal (full reversing journal entries)

---

## 11. Open Questions

1. ABC implementation — Phase 1 or Phase 2? (Recommend Phase 2)
2. Multi-currency cost centers — required for FDI clients? (PM input needed)
3. Transfer pricing cost allocation — separate module or within CC? (Recommend separate)
4. Budget integration — read-only from budget module or bidirectional? (Read-only Phase 1)
5. Standard cost variance — integrate with inventory module? (Phase 2)

---

## 12. References

- [TT99/2025/TT-BTC full text (800 pages)](https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Thong-tu-99-2025-TT-BTC-huong-dan-Che-do-ke-toan-doanh-nghiep-565484.aspx)
- [TT99 vs TT200 comparison](https://kiemtoanas.com.vn/vi/so-sanh-he-thong-tai-khoan-ke-toan-thong-tu-992025-va-thong-tu-2002014)
- [KPMG — Key changes in Vietnamese Accounting System](https://kpmg.com/vn/en/insights/2025/11/key-changes-in-vietnamese-accounting-system-for-enterprises.html)
- [EY — Cost allocation strategic elevation](https://www.ey.com/en_vn/insights/assurance/why-cost-allocation-strategically-elevates-the-finance-function)
- [PwC — Cost and Performance Management](https://www.pwc.com/vn/en/services/consulting/cost-performance-management.html)
- [Grant Thornton — TT99 slides](https://www.grantthornton.com.vn/contentassets/af9027513fcd4f7bb7c9e9aa395c3390/slide-key-updates-in-circular-no.-992025tt-btc-on-the-vietnamese-corporate-accounting-framework.pdf)
- [Acclime — Circular 99 key changes](https://vietnam.acclime.com/news-insights/circular-99-2025-key-changes-in-vietnams-accounting-rules-every-business-must-know/)
- [VNLawFirm — Circular 99 full text analysis](https://vnlawfirm.vn/van-ban/circular-no-99-2025-tt-btc-on-corporate-accounting-guidelines/)
