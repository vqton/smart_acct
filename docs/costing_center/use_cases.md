# Costing Center Module — Use Cases (UC-CC-01 through UC-CC-15)

**Version**: 1.0
**Date**: 2026-06-30
**Author**: BA Lead + Chief Accountant (20+ yrs)
**Regulatory Basis**: TT99/2025/TT-BTC (eff. 01/01/2026), VAS 01, VAS 16, IFRS 8

---

## UC-CC-01: Cost Center Hierarchy Management

**ID**: UC-CC-01
**Description**: Create, read, update, deactivate cost center nodes in a tree hierarchy. Each cost center is a responsibility unit with defined manager, type, and GL mapping.
**Priority**: P0

### Actors
- Chief Accountant (create/edit/delete)
- Cost Center Manager (read own)
- Finance Director (approve structural changes)

### Preconditions
- User authenticated with appropriate role
- At least one root cost center exists (company level)
- COA accounts exist for GL mapping

### Happy Path
1. Actor navigates to Cost Center Management
2. System displays tree of existing cost centers with expand/collapse
3. Actor selects parent node → clicks "Add Child"
4. System presents form: code, name, type (cost/profit/investment), manager, GL account, active dates
5. Actor fills required fields:
   - Code: auto-generated or manual (unique within parent)
   - Name: Vietnamese + English names
   - Type: Cost Center / Profit Center / Investment Center
   - Management: employee ID (validated against HR)
   - GL Account: default absorption account
   - Valid from → Valid to (default: from current period, no expiry)
   - Cost collector flag: YES = accumulates costs
6. Actor clicks "Save"
7. System validates:
   - Code uniqueness within parent branch
   - GL account exists in COA
   - Manager exists in employee database
   - Valid date range
8. System creates node → returns full path: "Công ty → Sản xuất → Phân xưởng A"
9. System logs audit: "CostCenter#123 created by user X"

### Alternative Paths
- **A1 — Bulk import**: Actor uploads Excel/CSV with columns [parent_code, code, name, type, manager_id, gl_account, valid_from, valid_to]. System validates each row; returns error file with row-level messages. Successful rows committed; failed rows skipped.
- **A2 — Move node**: Actor drags node to new parent. System validates: no circular reference (target not a descendant). If node has children, entire subtree moves. Audit logs the relocation.
- **A3 — Quick deactivate**: Actor sets `is_active = False`. System checks: no unposted allocations, no open commitments. Deactivated nodes excluded from allocation runs but preserved in historical reports.

### Exception Paths
- **E1 — Duplicate code**: Code "PROD_A" already exists under same parent → ErrorCodes.COST_CENTER_CODE_DUPLICATE
- **E2 — Circular reference**: Moving node under its own child → ErrorCodes.COST_CENTER_CIRCULAR_REF
- **E3 — Invalid GL account**: Account "9999" not in COA → ErrorCodes.COA_ACCOUNT_NOT_FOUND
- **E4 — Invalid manager**: Employee ID 99999 does not exist → ErrorCodes.EMPLOYEE_NOT_FOUND
- **E5 — Exceeds max depth**: Adding beyond level 10 → ErrorCodes.COST_CENTER_MAX_DEPTH
- **E6 — Has active transactions**: Cannot delete node with transactions → ErrorCodes.COST_CENTER_HAS_TRANSACTIONS

### Validation Rules
- Code: max 20 chars, alphanumeric + underscore, unique per parent
- Name: max 200 chars, required
- Level: auto-calculated (parent.level + 1), max 10
- Dates: valid_from ≤ valid_to; valid_from must be ≥ current period start (with override)
- GL account: must be a cost/expense type account (6xx/8xx)

---

## UC-CC-02: Cost Driver Management

**ID**: UC-CC-02
**Description**: Define cost drivers used as allocation bases. Drivers link cost pools to cost objects.
**Priority**: P0

### Actors
- Cost Accountant (CRUD)
- Chief Accountant (approve)

### Happy Path
1. Actor selects "Cost Drivers" → "New Driver"
2. System presents form: code, name, type, source module, source account, UoM
3. Actor fills:
   - Type: Quantity (headcount/sqm/kWh/machine hours) / Percentage / Fixed rate / Actual (from GL)
   - Source module: HR / Production / GL / Sales / Manual
   - Source account: GL account where driver value is posted
   - Unit of measure: người/m2/kWh/giờ máy/%
   - Formula (optional): e.g. `GL.6421 / HEADCOUNT`
4. Actor saves → System validates and creates driver
5. Driver available for allocation rules

### Alternative Paths
- **A1 — Auto-create from GL**: System suggests drivers based on GL pattern analysis (recurring expenses by nature)
- **A2 — Driver with formula**: Actor defines computed driver using expression language. System validates formula syntax at save time

### Exception Paths
- **E1 — Duplicate code**: ErrorCodes.COST_DRIVER_CODE_DUPLICATE
- **E2 — Invalid formula**: Parse error → ErrorCodes.COST_DRIVER_INVALID_FORMULA
- **E3 — Driver in use**: Cannot delete driver used by active allocation rules → ErrorCodes.COST_DRIVER_IN_USE

---

## UC-CC-03: Allocation Rule Configuration

**ID**: UC-CC-03
**Description**: Define rules for allocating costs from source cost centers to target cost centers.
**Priority**: P0

### Actors
- Cost Accountant (create/edit)
- Finance Director (approve)

### Happy Path
1. Actor navigates to "Allocation Rules" → "New Rule"
2. System presents rule form:
   - Rule code, name
   - Source cost center (FROM)
   - Target cost center(s) (TO) — one or many
   - Driver (FK → CostDriver)
   - Allocation method: Direct (100% to one target) / Percentage (fixed %) / Proportional (based on driver value)
   - Effective period
   - Priority (for ordering)
3. Actor selects source = "IT Department", targets = ["Production", "Sales", "Admin"]
4. Actor selects driver = "Headcount", method = "Proportional"
5. System shows preview: headcount values + calculated percentages + allocated amounts (based on latest driver data)
6. Actor confirms → Rule saved as "Draft"
7. Rule must be approved by Finance Director before execution

### Alternative Paths
- **A1 — Step allocation**: Multi-level rule chain: Admin → IT → Production (requires sequential runs). Actor sets rule priority: Admin (prio 1), IT (prio 2), Production (prio 3)
- **A2 — Copy rule**: Duplicate existing rule for new period with adjusted percentages
- **A3 — Rule group**: Group rules for batch approval and execution

### Exception Paths
- **E1 — Circular allocation**: Rule chain A→B→C→A detected → ErrorCodes.COST_ALLOCATION_CIRCULAR
- **E2 — Total ≠ 100%**: For percentage method, sum of allocations ≠ 100% → ErrorCodes.COST_ALLOCATION_TOTAL_NOT_100
- **E3 — Same source and target**: ErrorCodes.COST_ALLOCATION_SAME_CC
- **E4 — Driver data unavailable**: No driver data for current period → ErrorCodes.COST_DRIVER_DATA_MISSING
- **E5 — Source already allocated**: Rules would double-allocate same source → ErrorCodes.COST_ALLOCATION_DUPLICATE_SOURCE

### Validation Rules
- Rule priority: unique per period; lower number executes first
- Source CC must be cost collector
- Targets must exclude source CC
- Driver must match assignment period
- Rule must be within cost center active date range

---

## UC-CC-04: Allocation Execution

**ID**: UC-CC-04
**Description**: Execute allocation rules for a period. Generates allocation lines and optionally posts to GL.
**Priority**: P0

### Actors
- Cost Accountant (execute)
- Chief Accountant (review & post)

### Happy Path
1. Actor selects period → "Run Allocation"
2. System checks: period is open, no previous posted run exists for this period (unless re-run policy)
3. System displays selected rules to execute (by priority order)
4. Actor clicks "Execute"
5. System processes rules sequentially:
   - For each rule: read driver data → calculate allocation per target → generate allocation lines
   - Accumulate amounts per target cost center
6. System saves allocation run as "Draft" with all lines
7. Actor reviews allocation summary:
   - Total allocated vs total source (must balance)
   - Per-target amounts
   - Material variances (if previous period data available)
8. Actor clicks "Post to GL"
9. System generates GL journal entries:
   - Debit: Target CC expense account
   - Credit: Source CC expense account (or contra-account)
   - Each line carries cost center dimension
10. System updates run status → "Posted"
11. System logs: "AllocationRun#456 posted for period 202606"

### Alternative Paths
- **A1 — Re-run**: Actor selects "Re-run" for period (only if no period close). System reversals previous posted run (creates reversing GL entries), then executes fresh
- **A2 — Partial allocation**: Actor selects subset of rules to execute (e.g., only overhead rules)
- **A3 — Dry run**: Actor runs in test mode → produces allocation lines without posting. Used for verification

### Exception Paths
- **E1 — Period closed**: Cannot execute allocation for closed period → ErrorCodes.PERIOD_CLOSED
- **E2 — No rules configured**: No active rules for this period → ErrorCodes.COST_NO_RULES_FOR_PERIOD
- **E3 — Driver data stale**: Driver data more than 2 periods old → ErrorCodes.COST_DRIVER_DATA_STALE
- **E4 — GL posting error**: Journal entry fails validation (unbalanced, missing account) → ErrorCodes.COST_GL_POSTING_ERROR
- **E5 — Source no balance**: Source cost center has zero expense balance for period → Warning (allocation produces zero amounts)

### GL Posting Template
```
For allocation FROM CC_A TO CC_B (driver: headcount, $10,000 × 60% = $6,000):
  Dr 627_(CC_B)  $6,000  (Production OH allocated to CC_B)
  Cr 627_(CC_A)  $6,000  (Production OH allocated FROM CC_A)
  -- each line carries cost_center_id + cost_object_id
```

---

## UC-CC-05: Cost Object Management

**ID**: UC-CC-05
**Description**: Define cost objects (products, projects, orders, customers) for cost accumulation.
**Priority**: P1

### Actors
- Cost Accountant
- Production Manager (view product costing)

### Happy Path
1. Actor selects "Cost Objects" → "New"
2. Actor defines: code, name, type (product/project/order/campaign/customer), GL account
3. Actor optionally links to existing master data (product from Inventory, project from Project module)
4. System creates cost object
5. Actor can view accumulated costs (direct + allocated) for the object

### Alternative Paths
- **A1 — Auto-create from sales order**: Cost object created automatically when a new sales order is entered
- **A2 — Product BOM costing**: Cost object linked to BOM → system accumulates material + labor + overhead cost

### Exception Paths
- **E1 — Duplicate code**: ErrorCodes.COST_OBJECT_CODE_DUPLICATE
- **E2 — Missing BOM**: Cannot cost product without BOM → ErrorCodes.COST_OBJECT_MISSING_BOM
- **E3 — No costs tracked**: Cost object has zero accumulated cost → Warning

---

## UC-CC-06: Cost Accumulation & Tracking

**ID**: UC-CC-06
**Description**: Accumulate direct and allocated costs against cost objects. Track by period, CC, and GL account.
**Priority**: P1

### Actors
- System (automated)
- Cost Accountant (manual override)

### Happy Path
1. System runs daily accumulation process:
   - Reads GL actuals where cost_center_id + cost_object_id are populated
   - Reads AP invoices with cost center/cost object tags
   - Reads payroll distribution by cost center
   - Reads inventory issues by cost center
2. System accumulates to CostAccumulation table:
   - direct_cost: costs directly traceable to object
   - allocated_cost: costs assigned via allocation rules
   - period_cost: period-based (time-matched)
3. System updates cost object totals
4. Cost Accountant can drill-down: Period → CC → GL Account → Source Document

### Alternative Paths
- **A1 — Manual cost entry**: Cost Accountant can manually add cost items (allocations, adjustments)
- **A2 — Re-accumulate**: Trigger full re-accumulation for a period (after corrections)

### Exception Paths
- **E1 — GL data unavailable**: GL not posted for period → ErrorCodes.COST_GL_DATA_UNAVAILABLE
- **E2 — Duplicate accumulation**: Source already accumulated → skip (idempotent)
- **E3 — Mismatch total**: Accumulated total ≠ GL total by CC → ErrorCodes.COST_ACCUMULATION_MISMATCH

---

## UC-CC-07: Cost Center Budget Integration

**ID**: UC-CC-07
**Description**: Read budget data from Budget module for variance analysis. Cost center budget = budget amounts by CC + GL account + period.
**Priority**: P1
**Dependency**: Budget module must exist (Score: 0/5 — see Budget BRD)

### Happy Path
1. System reads budget data from Budget module: budget amounts by (cost_center_id, gl_account_code, period_key)
2. System stores in CostCenterBudget table (local cache for performance)
3. System matches actuals (from GL) vs budget (from Budget)
4. Variance = Actual - Budget (unfavorable if actual > budget for expense)

### Exception Paths
- **E1 — No budget data**: Budget not configured for cost center → variance = N/A
- **E2 — Budget module unavailable**: System gracefully skips variance → "No budget data"

---

## UC-CC-08: Variance Analysis

**ID**: UC-CC-08
**Description**: Analyze cost variances: budget vs actual, period-over-period, actual vs prior year.
**Priority**: P1

### Happy Path
1. Actor selects period, cost center, optional GL account filter
2. System computes:
   - Budget variance: Budget Amount - Actual Amount
   - Period variance: This period - Last period
   - Year variance: YTD this year - YTD last year
   - Variance %: Variance / Budget × 100
   - Flag: Favorable (expense lower) / Unfavorable (expense higher) / Neutral
3. System displays variance table with drill-down
4. Actor can annotate variance (add explanation)

### Alternative Paths
- **A1 — Export**: Export variance report to Excel/PDF
- **A2 — Drill-down**: Click on variance → see underlying transactions
- **A3 — Threshold alert**: If variance > configurable % (default 20%), flag for review

### Exception Paths
- **E1 — No prior period data**: Period-over-period comparison unavailable → N/A

---

## UC-CC-09: GL Integration — Cost Center on Journal Entries

**ID**: UC-CC-09
**Description**: Every journal entry line can carry a cost center dimension. This enables cost tracking at source.
**Priority**: P1

### Design
```python
class JournalEntryLine(BaseModel):
    # ... existing fields ...
    cost_center_id: Optional[int] = Field(None, description="FK → CostCenter")
    cost_object_id: Optional[int] = Field(None, description="FK → CostObject")
    # segment_string populated as "entity.cost_center.product.project"
    segment_string: Optional[str] = Field(None, max_length=100)
```

### Rules
- Cost center required when GL account is cost/expense type (6xx, 8xx)
- Cost center optional for revenue/asset/liability accounts
- When no cost center specified, defaults to "unallocated" cost center
- Cost center on JE line must be active at transaction date
- Allocation rules post to cost centers automatically

---

## UC-CC-10: Cost Center P&L Report

**ID**: UC-CC-10
**Description**: Generate Profit & Loss statement by cost center — shows revenue (if profit center), direct costs, allocated costs, net contribution.
**Priority**: P1

### Report Structure
```
COST CENTER P&L — June 2026
Công ty → Sản xuất → Phân xưởng A
Type: Profit Center
Manager: Nguyễn Văn A

Line Item                 | Budget  | Actual  | Variance | %
--------------------------|---------|---------|----------|------
Revenue (if profit ctr)   | 5,000   | 5,200   | 200 F    | +4%
Direct Materials (621)    | (1,000) | (1,100) | (100) U  | -10%
Direct Labor (622)        | (800)   | (750)   | 50 F     | +6.3%
Machine OH (623)          | (300)   | (320)   | (20) U   | -6.7%
Production OH Allocated   | (400)   | (420)   | (20) U   | -5%
Total Cost                | (2,500) | (2,590) | (90) U   | -3.6%
Contribution              | 2,500   | 2,610   | 110 F    | +4.4%
```

### Happy Path
1. Actor selects period(s), cost center(s), report type (summary/detail)
2. System computes revenue (if profit center), direct costs from GL, allocated costs from allocation engine
3. System renders report in HTML/PDF/Excel
4. Actor can drill into any line to see underlying transactions

---

## UC-CC-11: Allocation Summary Report

**ID**: UC-CC-11
**Description**: Show all allocations for a period: source CC → target CC → amount → driver.
**Priority**: P1

### Happy Path
1. Actor selects period
2. System shows allocation matrix (source CC rows × target CC columns)
3. Each cell shows allocated amount with breakdown by rule
4. Total row shows sum per target; total column shows sum per source
5. System also shows allocation tree: Source → Rule → Driver → Target → Amount

---

## UC-CC-12: Import/Export Cost Center Data

**ID**: UC-CC-12
**Description**: Import/export cost center master data, drivers, and rules via Excel/CSV.
**Priority**: P2

### Happy Path
1. Actor selects "Export" → downloads Excel template with current data
2. Actor modifies data in Excel offline
3. Actor selects "Import" → uploads Excel
4. System validates:
   - Column headers match template
   - Data types correct
   - Referential integrity (parent CC exists, GL account exists)
5. System shows validation summary: N rows OK, M errors
6. Actor confirms → import executes
7. Failed rows written to error file for download

### Exception Paths
- **E1 — Template mismatch**: Column headers don't match → ErrorCodes.COST_IMPORT_TEMPLATE_MISMATCH
- **E2 — Referential error**: Parent CC not found on row 5 → Error file with row details
- **E3 — Partial import**: Some rows succeed, some fail → System rolls back entire import or commits successful batch (configurable)

---

## UC-CC-13: Audit Trail

**ID**: UC-CC-13
**Description**: Every operation leaves an audit trail for compliance (TT99/2025 digital auditability).
**Priority**: P1

### Captured Events
| Entity | Events |
|--------|--------|
| CostCenter | CREATE, UPDATE, DEACTIVATE, REACTIVATE, MOVE |
| CostDriver | CREATE, UPDATE, DELETE |
| AllocationRule | CREATE, UPDATE, APPROVE, REJECT, ACTIVATE, ARCHIVE |
| AllocationRun | EXECUTE, POST, REVERSE, RE_RUN |
| CostObject | CREATE, UPDATE, DELETE |
| Import/Export | IMPORT, EXPORT |
| Budget | SYNC |

### Audit Log Schema
```
entity_type, entity_id, action, changes (JSON diff), actor, ip_address, created_at
```

---

## UC-CC-14: Dashboard & KPIs

**ID**: UC-CC-14
**Description**: Real-time cost center dashboard with key metrics.
**Priority**: P2

### KPIs
| KPI | Formula | Target |
|-----|---------|--------|
| Total cost by CC | Sum of actuals | Per budget |
| Cost per unit | Total cost / output quantity | < Standard |
| Allocation accuracy | (Allocated - Target) / Target | ±5% |
| CC budget utilization | Actual / Budget × 100 | < 100% |
| Unallocated % | Unallocated / Total × 100 | < 2% |
| Cost center count | Active CC nodes | As designed |
| Rule coverage | CC with rules / Total CC × 100 | 100% |
| Period close time | Last allocation → Close | < 5 days |

---

## UC-CC-15: Cost Center Manager Self-Service

**ID**: UC-CC-15
**Description**: Cost center managers can view their cost centers, review variances, and annotate.
**Priority**: P2

### Happy Path
1. Cost center manager logs in → sees dashboard for assigned cost centers
2. Manager views:
   - Current period actuals vs budget
   - Allocations received
   - Allocations sent (if service CC)
3. Manager can annotate variances (explain reasons)
4. Manager can download reports (PDF/Excel)
5. Manager can submit budget adjustment requests (redirects to Budget module)

---

## Use Case Dependency Map

```
UC-CC-01 (Hierarchy) ──→ UC-CC-03 (Rules) ──→ UC-CC-04 (Execution)
       │                       │                      │
       ▼                       ▼                      ▼
UC-CC-02 (Drivers) ────→ UC-CC-05 (Cost Obj) ──→ UC-CC-06 (Accumulation)
       │                       │                      │
       ▼                       ▼                      ▼
UC-CC-07 (Budget) ─────→ UC-CC-08 (Variance) ──→ UC-CC-09 (GL Integration)
       │                       │                      │
       ▼                       ▼                      ▼
UC-CC-10 (P&L Report) ──→ UC-CC-11 (Alloc Report) ── UC-CC-12 (Import/Export)
       │                       │                      │
       ▼                       ▼                      ▼
UC-CC-13 (Audit Trail)   UC-CC-14 (Dashboard)   UC-CC-15 (Self-Service)
```

---

## Reference: Cost Center Types (Vietnamese Accounting)

| Type | VAS Classification | Description | GL Accounts |
|------|-------------------|-------------|-------------|
| Cost Center (Trung tâm chi phí) | TK 621-627, 641, 642, 635, 811 | Responsibility for cost only | 621, 622, 623, 627, 641, 642, 635 |
| Production Cost Center | TK 621, 622, 623, 627 | Manufacturing cost center | 621, 622, 623, 627 |
| Service Cost Center | TK 627, 641, 642 | Support service (IT, HR, Admin) | 627, 641, 642 |
| Profit Center (Trung tâm lợi nhuận) | TK 511 + 621-642 | Revenue + cost responsibility | 511, 515, 621, 622, 623, 627, 632, 635, 641, 642 |
| Investment Center (Trung tâm đầu tư) | Full P&L + Balance Sheet | ROI responsibility | All accounts |
| Administrative Center | TK 642 | Management overhead | 642 |
| Selling Center | TK 641 | Sales & marketing | 641 |
| R&D Center | TK 642 (sub-account) | Research & development | 642 (R&D sub-account) |
| Project Center | By project | Project-based costing | By project accounts |
| Virtual Center | N/A | Cost pooling before re-allocation | Temporary accounts |

---

## Reference: Allocation Methods Mapping

| Method | VAS Name | When to Use | Precision |
|--------|----------|-------------|-----------|
| Direct (trực tiếp) | Phân bổ trực tiếp | Costs traceable to single CC | Exact |
| Percentage (tỷ lệ %) | Phân bổ theo tỷ lệ | Fixed allocation (e.g., rent 50:50) | Configurable |
| Proportional (tỷ lệ theo yếu tố) | Phân bổ theo yếu tố | Costs vary with driver (e.g., electricity by kWh) | High |
| Step-down (tuần tự) | Phân bổ tuần tự | Service CCs → Production CCs | Medium |
| Reciprocal (tương hỗ) | Phân bổ tương hỗ | Mutual services between CCs (Phase 2) | Very High |
| ABC | Phân bổ theo hoạt động | Activity-based costing (Phase 2) | Highest |
