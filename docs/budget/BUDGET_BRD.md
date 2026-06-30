# BRD: Budget Module (Dự toán ngân sách)
## SmartACCT ERP — Vietnamese Accounting System

**Version:** 1.0
**Date:** 2026-06-30
**Author:** Lead BA (20+ yrs) + Chief Accountant (20+ yrs)
**Status:** VERIFIED — Production-ready spec

---

## 1. Executive Summary

### 1.1 Purpose

Build **Budget (Dự toán ngân sách)** module for SmartACCT ERP. Provide enterprise budgeting (quản trị ngân sách doanh nghiệp): master budget lifecycle — plan, approve, execute, monitor, control, analyze, and roll forward. Cover revenue, expense, CAPEX, cash flow, and balance sheet budgeting per VAS best practices, TT 99/2025/TT-BTC (quản trị), and IFRS management reporting requirements.

### 1.2 Current State Assessment

**VERDICT: NOT PRODUCTION-READY. SCORE: 0/5**

Budget module = **zero code**. No domain entities, use cases, repository, models, routes, or tests.

**What exists (usable but NOT Budget):**

| Asset | Status | Budget Reuse |
|-------|--------|-------------|
| COA TK accounts | AccountType defined | Reuse for budget dimension mapping |
| GLUseCases (JournalEntry) | Full CRUD + period-gated posting | Reuse for actual vs budget comparison |
| GLUseCases (AccountingPeriod) | Period CRUD, close/reopen | Reuse for budget period alignment |
| GLUseCases (Financial Statements) | P&L, Balance Sheet, Cash Flow | Reuse for budget vs actual reporting |
| Cost Center (TK 642/641) | Defined in COA | Reuse for budget dimension |
| Department (implied in GL) | Not explicit | Need to define org hierarchy |
| APUseCases | Purchase invoice actuals | Reuse for expense budget control |
| ARUseCases | Sales invoice actuals | Reuse for revenue budget control |
| PayrollUseCases | Labor cost actuals | Reuse for labor budget control |
| FAUseCases | Depreciation actuals | Reuse for CAPEX budget control |
| FAPeriods module | Fiscal period management | Reuse for budget period alignment |
| COA usage check | Account validation | Reuse for budget account validation |

**Gap: EVERYTHING** — budget master, budget template, budget version, budget item (revenue/expense/CAPEX/cash), budget approval workflow, budget monitoring, budget control (warning/block on overspend), budget adjustment/additional, budget roll-up/consolidation, budget vs actual analysis, budget dashboard (KPI), what-if scenario, cash flow budget, balance sheet budget, budget carry-forward, multi-currency budget, multi-company consolidation, budget locking, budget period (monthly/quarterly/annual), budget dimension (cost center/project/department/product line).

### 1.3 Scope

**In scope (UC-BUDGET-01 through UC-BUDGET-15):**

| UC | Name | Description |
|----|------|-------------|
| UC-BUDGET-01 | Budget Master & Structure | Budget type (revenue/expense/CAPEX/cash/balance sheet), budget period (monthly/quarterly/annual), budget dimension (cost center/department/project), budget category |
| UC-BUDGET-02 | Budget Period & Calendar | Fiscal year budget calendar, budget cycle (planning → review → approval → monitor), budget period vs accounting period alignment |
| UC-BUDGET-03 | Budget Template | Reusable templates by department/cost center, template items with formulas, version management |
| UC-BUDGET-04 | Budget Plan (Draft) | Bottom-up/top-down/negotiated budget creation, data entry (manual/import from Excel/copy from prior year), driver-based planning (volume × rate) |
| UC-BUDGET-05 | Budget Approval Workflow | Multi-level approval (department head → finance → CFO → board), approval routing, reject with comments, approve with conditions, delegation |
| UC-BUDGET-06 | Budget Versioning | Draft/Proposed/Approved/Revised versions, version comparison, version lock/unlock, baseline vs revised vs forecast |
| UC-BUDGET-07 | Budget Adjustment & Additional | In-year budget adjustment (virement between items), supplementary budget, emergency budget, delegation of adjustment authority |
| UC-BUDGET-08 | Budget Execution Monitoring | Actual vs budget tracking, commitment tracking (PO/contract), encumbrance accounting, free balance calculation |
| UC-BUDGET-09 | Budget Control (Warning/Block) | Configurable control levels (warning/soft block/hard block), threshold rules, exemption (manager override), real-time check on AP/AR/GL posting |
| UC-BUDGET-10 | Budget Consolidation & Roll-up | Multi-department roll-up to division → company, multi-company consolidation (intercompany elimination), currency conversion |
| UC-BUDGET-11 | Budget vs Actual Analysis | Variance analysis (favorable/unfavorable), variance % and amount, drill-down (org → cost center → item), period comparison |
| UC-BUDGET-12 | Budget Dashboard & KPI | Dashboard: burn rate, remaining budget, variance %, forecast vs budget, KPI: expense ratio, revenue achievement, CAPEX utilization |
| UC-BUDGET-13 | Revenue Budget | Sales volume × price budget, product line/region/channel breakdown, seasonality, growth rate assumption |
| UC-BUDGET-14 | Expense Budget | Fixed/variable/semi-variable cost budget, headcount/labor budget, depreciation budget, procurement budget, SG&A budget |
| UC-BUDGET-15 | CAPEX & Cash Flow Budget | Capital expenditure budget (approval required), cash inflow/outflow forecast, financing plan, debt service coverage |

**Out of scope (v2.0+):**
- Driver-based rolling forecast (beyond annual budget)
- AI/ML predictive budget (machine learning forecast)
- Integrated business planning (IBP) — full S&OP
- Treasury/cash flow direct forecasting with bank integration
- Budget simulation (Monte Carlo / what-if optimizer)
- ESG/sustainability budget module
- Public sector state budget (NSNN) compliance — separate module for HCSN

### 1.4 Key Dependencies

| Dependency | Module | Purpose |
|------------|--------|---------|
| Chart of Accounts | COA | Budget accounts linked to GL accounts |
| Journal Entry | GL | Actual data for budget vs actual analysis |
| Accounting Period | GL | Budget period alignment |
| Cost Center | COA/GL | Budget dimension (TK 641/642) |
| AP Invoice | AP | Purchase commitment for budget control |
| AR Invoice | AR | Revenue actuals for budget tracking |
| Payroll | Payroll | Labor cost actuals |
| FA Depreciation | FA | Depreciation budget tracking |
| Tax | Tax | Tax expense budget tracking |
| Cash | Cash | Cash flow budget tracking |
| Inventory | Inventory | Inventory budget tracking |

---

## 2. Regulatory & Compliance Framework

### 2.1 Primary Legislation — DOUBLE-CHECKED ✅ (as of 30/06/2026)

| Citation | Title | Budget Impact | Status |
|----------|-------|---------------|--------|
| **Luật NSNN 89/2025/QH15** (25/06/2025, eff. FY 2026) | State Budget Law — replaces 83/2015/QH13 | Principles: budget discipline, transparency, public accountability; Art 8: budget management principles; Art 10: reserve 2-5%; Art 15: budget disclosure | **ACTIVE** from 01/01/2026 — replaces 83/2015/QH13 |
| **Luật NSNN 83/2015/QH13** (25/06/2015, eff. 01/01/2017) | State Budget Law (old) | Fully replaced by 89/2025/QH15 | **EXPIRED** 01/01/2026 |
| **NĐ 73/2026/NĐ-CP** (10/03/2026) | Guiding Law 89/2025/QH15 | Budget execution, allocation, adjustment procedures | **ACTIVE** |
| **NĐ 347/2025/NĐ-CP** (29/12/2025) | Budget implementation for FY 2026 | Budget execution organization, payment procedures via KBNN | **ACTIVE** |
| **TT 56/2025/TT-BTC** (25/06/2025, eff. 09/08/2025) | Budget construction guide FY 2026 + 3yr plan 2026-2028 | Budget format, timeline, submission requirements | **ACTIVE** |
| **TT 26/2026/TT-BTC** (25/03/2026) | Detail of NĐ 73/2026/NĐ-CP | Payment methods, lệnh chi tiền, KBNN procedures | **ACTIVE** |
| **TT 24/2024/TT-BTC** (17/04/2024, eff. 01/01/2025) | HCSN Accounting Regime | Budget accounting for state units (TK 0081/0082/0091/0092) | **ACTIVE** for HCSN |
| **TT 99/2025/TT-BTC** (27/10/2025, eff. 01/01/2026) | Enterprise Accounting Regime | Management accounting — Điều 6: budget preparation for internal management | **ACTIVE** |
| **IFRS Management Approach** | IFRS Framework | Segment reporting, management approach for budget vs actual | **REFERENCE** |
| **IAS 1/ASC 205** | Financial Statement Presentation | Going concern assumption requires budget assessment (12-month forward look) | **ACTIVE** |

**Note:** Enterprise budgeting (quản trị ngân sách) is governed by **TT 99/2025 — Điều 6 (Quản trị doanh nghiệp)** requiring enterprises to prepare periodic budgets for management decision-making, not by state budget law. State budget law applies to public sector units only.

### 2.2 Chart of Accounts (TK) Mapping for Budget

| TK Code | Acct Name | Budget Role |
|---------|-----------|-------------|
| TK 511 | Doanh thu bán hàng | Revenue budget — sales |
| TK 515 | Doanh thu tài chính | Revenue budget — financial |
| TK 711 | Thu nhập khác | Revenue budget — other |
| TK 632 | Giá vốn hàng bán | Expense budget — COGS |
| TK 641 | Chi phí bán hàng | Expense budget — SG&A |
| TK 642 | Chi phí QLDN | Expense budget — admin |
| TK 621-627 | Chi phí SX | Expense budget — production |
| TK 211-213 | Tài sản cố định | CAPEX budget |
| TK 241 | XDCB dở dang | CAPEX budget — construction |
| TK 353 | Quỹ khen thưởng | Budget — welfare fund |
| TK 331 | Phải trả NB | Cash budget — payment |
| TK 131 | Phải thu KH | Cash budget — collection |
| TK 111/112 | Tiền mặt/Tiền gửi | Cash budget — balance |

---

## 3. Business Process Overview

### 3.1 Budget Lifecycle (Annual Cycle)

```
[Planning] → [Drafting] → [Review] → [Approval] → [Execution] → [Monitoring] → [Analysis] → [Roll-forward]
     ↓            ↓            ↓            ↓             ↓              ↓              ↓              ↓
 Assumptions   Data entry   Department   Budget       PO/Contract   Actual vs      Variance      Carry-forward
 & targets     (bottom-up)  review       committee    spending      budget        analysis       to next year
 Market        Top-down     Finance      Board        Encumbrance   Dashboard     Root-cause    New cycle
 forecast      guidelines   review       approval     tracking      Alerts        Remediation   begins
```

### 3.2 Budget Calendar (Typical)

| Phase | Timeline | Owner |
|-------|----------|-------|
| Strategic plan & targets | Aug–Sep (Y-1) | Board/CFO |
| Budget guidelines released | Sep (Y-1) | Finance |
| Department budget submission | Oct (Y-1) | Department heads |
| Finance review | Nov (Y-1) | Finance team |
| Budget committee review | Dec (Y-1) | Budget committee |
| Board approval | Dec (Y-1) | Board |
| Budget loaded into system | Jan (Y) | Finance |
| Monitoring (monthly/quarterly) | Monthly (Y) | All |
| Budget adjustment (as needed) | Quarterly (Y) | Department heads |
| Year-end variance analysis | Jan (Y+1) | Finance |
| Carry-forward/roll-forward | Jan (Y+1) | Finance |

---

## 4. Budget Dimension Model

```
BudgetVersion
  ├── id, name (Draft/Approved/Revised), fiscal_year, status
  │
  ├── BudgetItem
  │   ├── id, account_id (FK→COA), cost_center_id, department_id
  │   ├── project_id (optional), product_line_id (optional)
  │   ├── period: month/quarter/annual
  │   ├── amount (VND + foreign currency)
  │   ├── quantity × unit_rate (driver-based)
  │   └── budget_category (revenue/expense/CAPEX/cash/balance_sheet)
  │
  ├── BudgetControl
  │   ├── control_level (warning/soft_block/hard_block)
  │   ├── threshold % or amount
  │   ├── exemption_role
  │   └── active flag
  │
  └── BudgetActual
      ├── budget_item_id
      ├── period
      ├── budget_amount
      ├── actual_amount (from GL)
      ├── commitment_amount (PO/contract)
      ├── encumbered_amount
      ├── free_balance
      └── variance (amount + %)
```

### 4.1 Dimensions

| Dimension | Source | Example Values |
|-----------|--------|---------------|
| Account (TK) | COA | TK 5111, TK 6421 |
| Cost Center | COA/GL | PX001 (Production), BH001 (Sales), QL001 (Admin) |
| Department | HR/Org | Sales, Marketing, R&D, Finance, HR |
| Project | Project | PRJ2025-001 |
| Product Line | Inventory | A-Series, B-Series |
| Region | Master | North, Central, South |
| Channel | Sales | Direct, Distributor, Online |
| Fund Source | State Budget | NSTW, NSDP, ODA |

---

## 5. Budget Control Matrix

| Control Type | Trigger | Action | Override |
|-------------|---------|--------|----------|
| Warning | Spending ≥ 80% of budget | Yellow flag, email alert | None needed |
| Soft Block | Spending ≥ 90% of budget | Warning + require cost center manager approval | Manager override code |
| Hard Block | Spending ≥ 100% of budget | Prevent posting, error message | CFO-level override |
| Hard Block | CAPEX without approved budget | Prevent PO creation | Board resolution required |
| Warning | Revenue < 80% of target | Dashboard alert, email to sales head | None needed |
| Soft Block | No budget allocated for cost center | Flag at transaction entry | Finance director override |

---

## 6. Budget Posting Rules to GL

Budget entries do NOT post to GL as journal entries. Budget is a **separate tracking layer** that references GL accounts for actual comparison.

- Budget item linked to GL account via `account_id`
- Actual amounts flow from GL via automated query (filter: account + cost center + period)
- Commitment amounts flow from AP via PO encumbrance
- No double-entry posting for budget itself
- Budget version is always for a fiscal year, broken into periods

---

## 7. Budget Templates & Forms

| Template | Purpose | Frequency |
|----------|---------|-----------|
| F-BUDGET-01 | Revenue Budget Template | Annual |
| F-BUDGET-02 | Expense Budget (SG&A) Template | Annual |
| F-BUDGET-03 | Labor/Headcount Budget Template | Annual |
| F-BUDGET-04 | CAPEX Budget Template | Annual |
| F-BUDGET-05 | Cash Flow Budget Template | Annual (monthly detail) |
| F-BUDGET-06 | P&L Budget Template | Annual (monthly detail) |
| F-BUDGET-07 | Balance Sheet Budget Template | Annual |
| F-BUDGET-08 | Budget vs Actual Report | Monthly |
| F-BUDGET-09 | Budget Variance Analysis | Monthly/Quarterly |
| F-BUDGET-10 | Budget Adjustment Request | Ad-hoc |
| F-BUDGET-11 | Budget Dashboard (KPI) | Real-time |

---

## 8. Master Budget Structure (Enterprise)

```
MASTER BUDGET (Dự toán tổng thể)
├── Operating Budget (Dự toán hoạt động)
│   ├── 1. Revenue/Sales Budget (Dự toán tiêu thụ)
│   │   └── Quantity × Price by product/region/channel
│   ├── 2. Production Budget (Dự toán sản xuất)
│   │   └── Units to produce = Sales + Closing - Opening inventory
│   ├── 3. Direct Materials Budget (Dự toán NVL trực tiếp)
│   │   └── Materials needed = Production × BOM rate
│   ├── 4. Direct Labor Budget (Dự toán NC trực tiếp)
│   │   └── Labor hours = Production × hours/unit × rate/hour
│   ├── 5. Manufacturing Overhead Budget (Dự toán SXC)
│   │   └── Variable + Fixed overhead allocation
│   ├── 6. Ending Inventory Budget (Dự toán tồn kho cuối kỳ)
│   │   └── FG inventory valuation
│   ├── 7. COGS Budget (Dự toán giá vốn)
│   │   └── = DM + DL + MOH allocated
│   └── 8. SG&A Budget (Dự toán BH & QL)
│       └── Selling + Administrative expenses
│
├── Financial Budget (Dự toán tài chính)
│   ├── 9. Cash Budget (Dự toán tiền)
│   │   └── Inflow (collections) - Outflow (payments) ± Financing
│   ├── 10. Capital Expenditure Budget (Dự toán đầu tư)
│   │   └── Asset purchases, construction, disposals
│   └── 11. Budgeted Financial Statements
│       ├── Budgeted P&L (Dự toán KQKD)
│       ├── Budgeted Balance Sheet (Dự toán Bảng CĐKT)
│       └── Budgeted Cash Flow (Dự toán LCTT)
│
└── Supporting Schedules
    ├── 12. Depreciation Schedule (Khấu hao)
    ├── 13. Debt Service Schedule (Nợ vay)
    ├── 14. Tax Provision Schedule (Thuế)
    └── 15. Intercompany Schedule (Nội bộ)
```

---

## 9. Key Business Rules

### 9.1 Budget Calculation Rules

| Rule | Formula | Description |
|------|---------|-------------|
| Revenue Budget | Σ (Sales Volume × Unit Price) | By product, region, channel, period |
| Production Budget | Sales + Closing FG - Opening FG | Units to manufacture |
| Direct Materials | Production × Qty per Unit × Price | Material procurement budget |
| Direct Labor | Production × Hours per Unit × Hourly Rate | Labor cost budget |
| MOH Budget | Variable: driver-based; Fixed: annual allocation | Overhead cost budget |
| COGS | DM + DL + MOH absorbed | Cost of goods sold |
| Gross Margin | Revenue - COGS | Margin analysis |
| SG&A Budget | Department-level expense submission | Fixed + variable allocation |
| Cash Collection | % of current + prior period sales | AR collection pattern |
| Cash Payment | % of current + prior period purchases | AP payment pattern |
| Variance % | (Actual - Budget) / Budget × 100 | Performance measure |
| Free Balance | Budget - Actual - Commitment | Available spending |
| Burn Rate | Total Spent / Total Period Days × 30 | Run-rate analysis |

### 9.2 Budget Version Rules

1. **Draft**: Editable, not visible in control checks. Created by department.
2. **Proposed**: Submitted for review. Finance can edit. Department cannot edit without recall.
3. **Approved**: Locked. Used for budget control (warning/block). Amendment requires adjustment request.
4. **Revised**: Created from Approved + adjustments. New baseline for comparison.
5. **Forecast**: Rolling forecast (management view, not for control). Updated quarterly.

### 9.3 Budget Adjustment Rules

1. Virement (between items within same cost center): ≤ 10% of original item — manager approval
2. Virement between cost centers: Requires finance director approval
3. Supplementary budget (new items): Board approval required
4. Emergency budget (unforeseen): CEO approval + board ratification at next meeting
5. Adjustment must reference original budget item and approval document number
6. All adjustments tracked in audit log

### 9.4 Budget Lock Rules

1. Current month: locked after month-end close
2. Current quarter: locked after quarter-end review
3. Current year: locked after year-end — only year-end adjustments allowed
4. Budget version can be unlocked temporarily by CFO with audit trail

### 9.5 Budget Consistency Rules

1. Budget sum of periods = Annual total (no orphan periods)
2. Revenue budget ≥ 0 (negative revenue not allowed — will use negative variance)
3. Expense budget ≥ 0 (negative expense = revenue in some cases — handled as other income)
4. CAPEX budget detail must match asset category
5. Cash budget must balance: Beginning Cash + Inflow - Outflow = Ending Cash
6. Inter-department cross-charges must net to zero in consolidation

---

## 10. Integration Points

| Integration | Direction | Data |
|-------------|-----------|------|
| COA → Budget | One-way | Account list for budget items |
| GL → Budget (Actuals) | One-way | Actual revenue/expense by account + cost center + period |
| AP → Budget (Commitment) | One-way | PO/contract amounts for encumbrance tracking |
| AP → Budget (Actuals) | One-way | Actual AP invoice amounts |
| AR → Budget (Actuals) | One-way | Actual AR invoice amounts |
| Payroll → Budget (Actuals) | One-way | Actual labor costs |
| FA → Budget (Actuals) | One-way | Actual depreciation/CAPEX |
| Tax → Budget (Actuals) | One-way | Actual tax payments/provisions |
| Budget → GL (Control) | One-way | Budget control flag (warning/block) |
| Budget → Dashboard | One-way | Budget KPI data |
| Period → Budget | One-way | Period open/close status for budget locking |

---

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Budget data quality (manual entry errors) | High | Medium | Import from Excel with validation; driver-based auto-calc |
| Budget control slows operations | Medium | Medium | Configurable control levels + manager override |
| Multi-currency budget complexity | High | Low | Budget in functional currency (VND) with FX rate assumption table |
| User adoption (Excel to system) | Medium | High | Excel import/export; user training; parallel run |
| Budget vs actual reconciliation errors | High | Medium | Automated GL actuals fetch; period-end reconciliation |
| Regulatory changes (new laws) | Medium | Medium | Modular design, parameterized rules, configurable |

---

## 12. Implementation Phases

### Phase 1 — Foundation (UC-BUDGET-01 to UC-BUDGET-04)
- Budget master, structure, period, template
- Basic budget plan entry (manual + Excel import)
- Cost center/department dimension

### Phase 2 — Workflow & Control (UC-BUDGET-05 to UC-BUDGET-09)
- Approval workflow (multi-level)
- Version management
- Adjustment/virement process
- Budget control (warning/block) integrated with AP/AR/GL

### Phase 3 — Analysis & Reporting (UC-BUDGET-10 to UC-BUDGET-12)
- Consolidation roll-up
- Budget vs actual variance analysis
- Dashboard with KPI

### Phase 4 — Full Coverage (UC-BUDGET-13 to UC-BUDGET-15)
- Revenue/driver-based budget
- Expense budget with headcount planning
- CAPEX approval workflow
- Cash flow budget

---

## 13. Appendix: Integration with State Budget (NSNN)

For HCSN units using SmartACCT, the Budget module can optionally support:

| Feature | Enterprise | HCSN (State Budget) |
|---------|-----------|---------------------|
| Budget source | Internal plan | NSNN allocation + own revenue |
| Budget accounts | Management COA | TK 0081/0082 (off-BS), TK 0091/0092 |
| Budget format | Internal format | TT 56/2025/TT-BTC templates |
| Approval | Internal workflow | State budget authority hierarchy |
| Reporting | Management reports | Báo cáo quyết toán NSNN (TT 90/2018/TT-BTC) |
| Control | Internal thresholds | KBNN control per NĐ 347/2025/NĐ-CP |

**HCSN budget implementation is scope for v2.0.**
