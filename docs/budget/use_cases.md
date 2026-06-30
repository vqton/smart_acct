# Budget Module — Use Cases (UC-BUDGET-01 through UC-BUDGET-15)
## SmartACCT ERP — Vietnamese Accounting System

**Version:** 1.0
**Date:** 2026-06-30

---

## UC-BUDGET-01: Budget Master & Structure

### Description
Manage budget master data: budget types, categories, dimensions, and structural setup. Define what can be budgeted, how items are classified, and which dimensions (cost center, department, project) apply.

### Actors
- Accounting Manager (setup)
- CFO (approve structure)

### Preconditions
- COA module active (accounts reference)
- Organizational hierarchy defined (departments, cost centers)

### Postconditions
- Budget structure created with valid dimensions

### Happy Path
1. Actor navigates to Admin → Budget → Structure
2. System displays current budget structure (or empty if new)
3. Actor defines budget types: Revenue, Expense, CAPEX, Cash Flow, Balance Sheet
4. Actor configures dimensions: cost center (required), department (required), project (optional), product line (optional), region (optional), channel (optional)
5. Actor defines budget categories for each type
6. Actor sets period type: Monthly, Quarterly, Annual (with Monthly = default)
7. System validates: at least one dimension configured, COA accounts assigned to types
8. System saves structure as active

### Alternative Paths
- **A1**: Import structure from COA — auto-create categories from account groups
- **A2**: Clone from existing company (multi-company setup)
- **A3**: Mark structure as inactive (prevents new budget creation, existing budgets still queryable)

### Exception Paths
- **E1**: No COA accounts configured → system returns ErrorCodes.BUDGET_NO_COA_ACCOUNTS
- **E2**: Duplicate dimension name → system returns ErrorCodes.BUDGET_DIMENSION_DUPLICATE
- **E3**: Budget type without accounts → system returns ErrorCodes.BUDGET_TYPE_NO_ACCOUNTS

### Rules
- Budget structure can be changed only when no active budget version for current year
- At least Revenue and Expense types required
- Cost center or department dimension required
- Each budget type must map to ≥1 GL account
- Max 10 custom dimensions (predefined: cost center, department, project = 3)

### Domain Entities
- BudgetStructure, BudgetType, BudgetDimension, BudgetCategory

### Data Flow
```
Actor → [Create Structure] → System validates → Save to DB → Return structure_id
```

---

## UC-BUDGET-02: Budget Period & Calendar

### Description
Create and manage budget periods aligned to fiscal year. Define budget cycle phases with dates: planning start, department submission deadline, finance review period, approval deadline, monitoring start.

### Actors
- Finance Manager
- CFO

### Preconditions
- Fiscal year periods exist in GL (AccountingPeriod)
- Budget structure created (UC-BUDGET-01)

### Postconditions
- Budget calendar created for fiscal year

### Happy Path
1. Actor selects fiscal year (e.g., 2027)
2. System loads existing GL periods for that year
3. Actor confirms period alignment (monthly periods match GL periods)
4. Actor sets budget calendar dates:
   - Guidelines release date: 01-Sep-Y-1
   - Department submission deadline: 15-Oct-Y-1
   - Finance review: 01-Nov-Y-1 → 30-Nov-Y-1
   - Budget committee: 01-Dec-Y-1 → 15-Dec-Y-1
   - Board approval: 20-Dec-Y-1
   - Budget load into system: 01-Jan-Y
5. System creates budget calendar
6. System creates 12 monthly budget periods + 4 quarterly roll-ups + 1 annual total

### Alternative Paths
- **A1**: Quick setup — auto-generate from GL periods with default calendar
- **A2**: Copy calendar from prior year (adjust dates)

### Exception Paths
- **E1**: Budget calendar already exists for this year → return ErrorCodes.BUDGET_PERIOD_EXISTS
- **E2**: End date before start date → ErrorCodes.BUDGET_INVALID_DATE_RANGE

### Rules
- Budget periods must be subset of GL periods (no future period beyond GL)
- Budget calendar can be modified until first budget plan submitted
- Budget period = fiscal year (01-Jan to 31-Dec)
- Monthly periods within budget are always calendar months

### Domain Entities
- BudgetCalendar, BudgetCalendarPhase, BudgetPeriod

---

## UC-BUDGET-03: Budget Template

### Description
Create reusable budget templates for departments/cost centers. Templates define line items, formulas, and structure for consistent budget submission.

### Actors
- Accounting Manager
- Department Head

### Preconditions
- Budget structure exists (UC-BUDGET-01)
- COA accounts exist

### Postconditions
- Reusable template saved

### Happy Path
1. Actor navigates to Budget → Templates → Create
2. Actor enters template name, description, applicable department type
3. Actor adds line items:
   - Revenue templates: sales lines with volume × unit price
   - Expense templates: cost items with fixed/variable classification
4. For each line: select GL account, set formula (if any), set required/optional
5. Actor adds notes/hints for each line item
6. Actor sets default distribution (e.g., equal monthly, seasonal, custom)
7. System validates: no circular formula, all accounts exist
8. System saves template as active

### Alternative Paths
- **A1**: Import template from Excel (predefined format)
- **A2**: Duplicate existing template → modify
- **A3**: Set template as default for specific cost centers

### Exception Paths
- **E1**: Circular formula chain → ErrorCodes.BUDGET_CIRCULAR_FORMULA
- **E2**: Template name duplicate → ErrorCodes.BUDGET_TEMPLATE_DUPLICATE
- **E3**: Formula references deleted line → ErrorCodes.BUDGET_FORMULA_INVALID_REF

### Rules
- Template can be updated only when no budget plan using it is in Approved status
- Template inheritance: child cost center inherits parent template unless overridden
- Formula syntax supports: +, -, *, /, SUM(), AVG(), PRIOR_YEAR(), GROWTH(%)

### Domain Entities
- BudgetTemplate, BudgetTemplateLine, BudgetTemplateFormula

---

## UC-BUDGET-04: Budget Plan (Draft)

### Description
Create budget plan entries. Supports bottom-up (department drafts), top-down (finance allocates), or negotiated (iterative). Data entry via UI, Excel import, or copy from prior year.

### Actors
- Department Head (enter)
- Accountant (enter)
- Finance Manager (review)

### Preconditions
- Budget structure, period, template exist
- User assigned to cost center(s)

### Postconditions
- Budget plan created in Draft status (editable)

### Happy Path
1. Actor selects: fiscal year, budget version (Draft), department/cost center
2. System loads template (if assigned) or blank form
3. For each line item, actor enters:
   - Amount (VND) per period (monthly/quarterly)
   - OR quantity × unit rate (driver-based)
   - Notes/assumptions (free text)
4. Actor enters growth %, inflation assumptions (optional, auto-calc)
5. System auto-calculates totals per period and annual
6. System runs validation rules:
   - Revenue ≥ 0
   - Expense ≥ 0
   - Budget total within organizational limits (if configured)
7. Actor saves as Draft
8. System creates BudgetPlan with status=Draft

### Alternative Paths
- **A1**: Import from Excel (upload xlsx → map columns → validate → import)
- **A2**: Copy from prior year approved budget → apply growth % → auto-populate
- **A3**: Copy from prior year actuals → apply growth % → auto-populate
- **A4**: Top-down allocation — finance enters total → system auto-distributes to departments

### Exception Paths
- **E1**: Excel file format invalid → ErrorCodes.BUDGET_IMPORT_INVALID_FORMAT
- **E2**: Amount exceeds maximum configured for this cost center → ErrorCodes.BUDGET_AMOUNT_EXCEEDS_LIMIT
- **E3**: Mandatory line item missing → ErrorCodes.BUDGET_MANDATORY_ITEM_MISSING
- **E4**: Negative revenue → ErrorCodes.BUDGET_REVENUE_NEGATIVE
- **E5**: Zero sales volume with price > 0 → ErrorCodes.BUDGET_PRICE_WO_VOLUME
- **E6**: Total budget > company cap → ErrorCodes.BUDGET_CAP_EXCEEDED

### Rules
- Department can only edit own budget
- Finance can edit all draft budgets
- Draft can be saved multiple times (overwrites)
- Driver-based calculation: Quantity × Rate = Amount (auto-computed)
- Growth rate applied: Prior year × (1 + growth%) = Budget
- Partial save allowed (not all lines required in Draft)
- Multi-currency: amount in VND + source currency + FX rate

### Domain Entities
- BudgetPlan, BudgetPlanLine, BudgetPlanDriver, BudgetPlanPeriod

### Data Flow
```
User input → Validate (structure rules + business rules) → Calculate totals → Save Draft
  ↓                                    ↓
  Exception → Reject                  Commit to DB → Confirm
```

---

## UC-BUDGET-05: Budget Approval Workflow

### Description
Multi-level approval routing for budget plans. Supports sequential (department → finance → CFO → board) or parallel (finance + HR review simultaneously).

### Actors
- Department Head (submit)
- Finance Manager (review)
- CFO (approve)
- Board (final approval)
- System (auto-route)

### Preconditions
- Budget plan in Draft status
- Approval routing rules configured

### Postconditions
- Budget plan transitions through approval chain
- Final status: Approved or Rejected

### Happy Path
1. Department Head submits draft budget (status → Proposed)
2. System routes to first approver (Finance Manager)
3. Finance Manager reviews: checks consistency, cross-department balance
4. Finance Manager can:
   - Approve → route to next level (CFO)
   - Reject → return to Department Head with comments (status → Draft)
   - Return with revision request
5. CFO reviews strategic alignment, total spending
6. CFO approves → route to Board (or final if Board not required)
7. Board reviews at scheduled meeting
8. Board approves → status → Approved (locked)
9. System notifies all participants
10. System creates baseline BudgetVersion in Approved status

### Alternative Paths
- **A1**: Delegation — approver delegates to deputy (with audit trail)
- **A2**: Parallel approval — finance + HR review simultaneously
- **A3**: Escalation — if approver does not act in N days, route to next level
- **A4**: CFO approves with conditions (conditional approval — items flagged for adjustment later)
- **A5**: Budget committee meeting approval via minutes upload (offline)

### Exception Paths
- **E1**: No approver configured for this cost center → ErrorCodes.BUDGET_NO_APPROVER
- **E2**: Approver is also submitter (self-approval) → ErrorCodes.BUDGET_SELF_APPROVAL_DENIED
- **E3**: Budget plan locked (another approval in progress) → ErrorCodes.BUDGET_IN_LOCKED_WORKFLOW

### Rules
- Approver cannot be same as submitter for any given step
- Approval chain configurable per cost center
- Notification at each step (email + in-app)
- Rejection includes required comment
- Approval timestamps recorded for SLA tracking
- Board-level approval requires min N of M participants to approve

### Domain Entities
- BudgetApprovalWorkflow, BudgetApprovalStep, BudgetApprovalLog

### Workflow Diagram
```
[Draft] → Submit → [Proposed] → Finance Review → [Under Review] → CFO Review → [Approved]
    ↑                 ↓                              ↓
    └── Rejected ← Return to Dept           Return to Finance
```

---

## UC-BUDGET-06: Budget Versioning

### Description
Manage budget versions: Draft → Proposed → Approved → Revised. Compare versions, lock/unlock, baseline management.

### Actors
- Finance Manager
- CFO
- System (auto-version)

### Preconditions
- At least one budget plan exists

### Postconditions
- Budget version created with appropriate status

### Happy Path
1. Actor opens budget version management
2. System displays current version list (Draft/Proposed/Approved/Revised)
3. Actor selects version to view details
4. Actor can:
   - Compare two versions (side-by-side, variance % and amount)
   - Lock a version (prevents further editing)
   - Unlock a version (CFO-only, with audit reason)
5. When budget is approved (UC-BUDGET-05), system auto-creates Approved baseline
6. When adjustment occurs (UC-BUDGET-07), system creates Revised version = Approved + adjustments
7. System maintains version history: every change logged

### Alternative Paths
- **A1**: Version rollback — revert to prior version (CFO approval required)
- **A2**: What-if version — create scratch version for simulation (not for control)
- **A3**: Archive old versions (no deletion, only archival)

### Exception Paths
- **E1**: Cannot unlock budget in execution phase without CFO override → ErrorCodes.BUDGET_LOCK_CANNOT_UNLOCK
- **E2**: Version comparison with mismatched dimensions → ErrorCodes.BUDGET_VERSION_MISMATCH

### Rules
- Only one active Approved version per fiscal year per entity
- Revised version increments: v1.0 (Approved), v1.1 (first revision), v1.2 (second revision)
- What-if versions: WIP-001, WIP-002 (not for control)
- Version comparison available only for versions of same fiscal year
- Audit log: who created version, when, from which version

### Domain Entities
- BudgetVersion, BudgetVersionComparison, BudgetVersionAudit

---

## UC-BUDGET-07: Budget Adjustment (Virement & Supplementary)

### Description
In-year budget adjustments: virement between items, supplementary budget, emergency budget. Track every change against original approved budget.

### Actors
- Department Head (request)
- Finance Manager (review)
- CFO (approve)
- Board (approve — material adjustments)

### Preconditions
- Budget version in Approved status
- Current fiscal year not yet closed

### Postconditions
- Revised budget version created (or adjustment registered)

### Happy Path (Virement within cost center)
1. Department Head identifies need to shift budget from Line A to Line B
2. Actor creates Adjustment Request: source line A (-50M), target line B (+50M)
3. Actor adds justification (free text)
4. System calculates: A new budget = A original - 50M, B new = B original + 50M
5. System checks:
   - Line A reduction not > 50% of original (configurable)
   - Line B increase not > 30% of original (configurable)
   - Net change = 0 (rebalancing within same cost center)
6. Route to approval (department head approves for ≤ 10%, CFO for > 10%)
7. Approved → System creates adjustment record
8. System creates Revised budget version (if cumulative adjustments exceed materiality threshold)

### Alternative Paths
- **A1**: Supplementary budget (new items, net increase in total) → Board approval required
- **A2**: Emergency budget (natural disaster, urgent) → CEO approves, Board ratifies in next meeting
- **A3**: Transfer between cost centers → reduce A cost center, increase B cost center; CFO approval req
- **A4**: In-year budget reduction (across-the-board cut) → CEO directive, auto-apply %

### Exception Paths
- **E1**: Source line already at zero → ErrorCodes.BUDGET_ADJUST_SOURCE_EXHAUSTED
- **E2**: Total increase > 20% of original (materiality) without Board approval → ErrorCodes.BUDGET_ADJUST_MATERIALITY_EXCEEDED
- **E3**: Period closed for adjustments → ErrorCodes.BUDGET_PERIOD_CLOSED
- **E4**: Source line committed amount > new budget → ErrorCodes.BUDGET_ADJUST_COMMITMENT_EXCEEDS

### Rules
- Virement (rebalancing): net change = 0 within same cost center
- Supplementary: net increase > 0
- Materiality threshold: 20% of original budget (configurable, requires Board)
- Adjustment cannot reduce budget below current commitments
- Maximum reductions: 50% of individual line item (configurable)
- All adjustments registered in audit trail
- Cumulative adjustments tracked against Approved baseline

### Domain Entities
- BudgetAdjustment, BudgetAdjustmentLine, BudgetAdjustmentApproval

---

## UC-BUDGET-08: Budget Execution Monitoring

### Description
Track actual performance against budgeted amounts. Monitor actual revenue/expense, commitments (PO/contract), encumbrances, and free balance.

### Actors
- Finance Manager
- Department Head
- CFO

### Preconditions
- Approved budget version exists
- GL/AP/AR modules posting actual transactions

### Postconditions
- Budget execution report generated

### Happy Path
1. Actor opens Budget → Execution Monitor
2. System loads budget data: Approved amounts by account + cost center + period
3. System fetches actual amounts from GL (via account + cost center + period query)
4. System fetches commitments from AP (PO not yet invoiced)
5. System fetches encumbrances from AP (goods receipt but not yet invoiced)
6. System calculates:
   - Free Balance = Budget - Actual - Commitment - Encumbrance
   - Utilization % = (Actual + Commitment) / Budget × 100
   - Remaining % = Free Balance / Budget × 100
7. System color-codes: Green (< 70%), Yellow (70-90%), Red (> 90%)
8. Actor can drill down: cost center → department → line item
9. Actor can export to Excel/PDF

### Alternative Paths
- **A1**: Period filter — view by month, quarter, YTD
- **A2**: Dimension filter — by cost center, department, project
- **A3**: Commitment-only view (encumbrance report)

### Exception Paths
- **E1**: GL actuals not available for current period (GL not posted) → system shows "Last posted: [date]"
- **E2**: Account mapping mismatch (budget account not linked to GL account) → ErrorCodes.BUDGET_ACCOUNT_MISMATCH
- **E3**: Budget version not specified → ErrorCodes.BUDGET_VERSION_REQUIRED

### Rules
- Actual data retrieved from GL in real-time (or near-real-time, max 15-min delay)
- Commitment data from AP PO module
- Actuals = posted GL journal entries (not draft)
- Intercompany transactions included/excluded based on consolidation setting
- FX impact: actuals at spot rate, budget at planning rate

### Domain Entities
- BudgetExecutionItem, BudgetCommitment, BudgetEncumbrance, BudgetFreeBalance

### Data Flow
```
GL Tables → Query by account+CC+period → Actual amount
AP Tables → Query by PO status → Commitment amount
    ↓
Budget Execution Engine → Free Balance = Budget - Actual - Commitment
    ↓
Dashboard / Report
```

---

## UC-BUDGET-09: Budget Control (Warning/Block)

### Description
Real-time budget control integrated with transaction posting. When user posts AP invoice, AR credit note, GL journal, or PO, system checks available budget and applies configured control level.

### Actors
- All users (posting transactions)
- System (auto-enforce control)
- Manager (override)
- CFO (block override)

### Preconditions
- Approved budget version active
- Budget control rules configured
- Transaction posting integrated with budget check

### Postconditions
- Transaction either posted, warned, or blocked based on budget availability

### Happy Path (Within Budget)
1. User creates AP invoice (or PO, GL journal, AR credit)
2. User enters GL account + cost center + amount
3. System calls BudgetControlService:
4. Budget check: Actual + Commitment + New Transaction ≤ Budget × Control Threshold
5. If utilization < 80%: Transaction posts with no warning (Green)
6. If utilization ≥ 80% but < 90%: Transaction posts with Yellow warning banner ("Over 80% of budget used")
7. If utilization ≥ 90% but < 100%: Transaction posts with Red warning ("Over 90% — approve to proceed")
   - Soft block: user can proceed with cost center manager approval code
8. If utilization ≥ 100%: Hard block — transaction cannot post
   - Error message: "Budget exhausted for account [X] / cost center [Y]"
   - Override: CFO-level authorization code required

### Alternative Paths
- **A1**: Override workflow — hard block triggers auto-email to CFO with details
- **A2**: Grace period — user can exceed budget in current month by max 10M if below annual YTD
- **A3**: Soft block with justification — user enters reason, auto-routed to manager for post-facto approval

### Exception Paths
- **E1**: No budget control config for this cost center → transaction proceeds (default: no control)
- **E2**: Budget control service unavailable (timeout) → transaction proceeds with warning log
- **E3**: Invalid override code → transaction still blocked

### Rules
- Control rules configurable per account group + cost center
- Levels: None, Warning only, Soft block (manager), Hard block (CFO)
- Budget check: Annual budget YTD (cumulative), not period budget (configurable)
- Override codes: 6-digit numeric, one-time use, expire in 24 hours
- All blocks and overrides logged in audit table
- CAPEX always requires hard block (no spending without approved CAPEX budget)
- Revenue tracking: if actual < 80% of budget, warning (not block)

### Domain Entities
- BudgetControlRule, BudgetOverride, BudgetBlockLog

### Data Flow
```
Transaction Entry → Extract (Account, CC, Amount, Period)
    ↓
Lookup BudgetVersion (Approved, current FY)
    ↓
Lookup BudgetControlRule (Account + CC)
    ↓
Calculate: Utilization = (Actual + Commitment + NewTx) / Budget × 100
    ↓
Compare vs Control Levels:
    ├── < 80%  → Allow (no warning)
    ├── 80-90% → Allow (warning)
    ├── 90-100% → Allow (soft block — manager override)
    └── ≥ 100%  → Block (hard block — CFO override)
    ↓
Return: Status (Allow/Warning/Block) + Message
    ↓
Transaction Processor: Apply response
```

---

## UC-BUDGET-10: Budget Consolidation & Roll-up

### Description
Consolidate budgets from departments → division → company. Support multi-entity consolidation with intercompany elimination and currency conversion.

### Actors
- Consolidation Accountant
- CFO

### Preconditions
- Budget plans for all entities/ departments exist in Approved status
- Consolidation mapping set up (entity → parent, IC accounts)

### Postconditions
- Consolidated budget created at parent level

### Happy Path
1. Actor selects consolidation scope: entities to include, fiscal year, budget version
2. System aggregates budget lines from all included entities
3. For multi-currency: system converts to reporting currency (VND) using budget FX rate
4. System identifies intercompany (IC) transactions for elimination:
   - IC revenue/expense (e.g., entity A sells to entity B)
   - IC receivable/payable budget
   - IC dividend
5. System nets IC items to zero in consolidation
6. System generates consolidated budget P&L, Balance Sheet, Cash Flow
7. Actor reviews consolidated budget
8. Actor approves consolidated version → status = Consolidated

### Alternative Paths
- **A1**: Partial consolidation — exclude certain entities (e.g., discontinued operations)
- **A2**: Roll-up without IC elimination (for internal management view)
- **A3**: Compare consolidated vs sum-of-individual (see IC impact directly)

### Exception Paths
- **E1**: Entity not yet submitted budget → ErrorCodes.BUDGET_CONSOLIDATION_INCOMPLETE
- **E2**: IC elimination incomplete (unmatched counterpart) → ErrorCodes.BUDGET_IC_MISMATCH
- **E3**: FX rate not available for budget period → ErrorCodes.BUDGET_FX_RATE_MISSING

### Rules
- All entities must have Approved budget before consolidation can run
- IC elimination: matching IC account pairs (e.g., TK 136/336) net to zero
- Currency conversion: use budget exchange rate table (planning rate, not spot)
- Minority interest calculated if applicable (ownership < 100%)
- Consolidation version linked to subsidiary versions (audit trail)
- Re-run consolidation if any subsidiary budget is adjusted

### Domain Entities
- BudgetConsolidation, BudgetConsolidationEntity, BudgetICTransaction

---

## UC-BUDGET-11: Budget vs Actual (Variance Analysis)

### Description
Comprehensive variance analysis comparing budget (planned) vs actual (executed). Support flexible drill-down, period comparisons, and root-cause annotation.

### Actors
- Finance Manager
- Department Head
- CFO

### Preconditions
- Approved budget version exists
- Actual data posted in GL for current period

### Postconditions
- Variance analysis report generated (viewable, exportable)

### Happy Path
1. Actor navigates to Budget → Variance Analysis
2. Actor selects: period (month/quarter/YTD/annual), budget version, dimension (entity/department/cost center)
3. System generates report:

| Account | Budget | Actual | Variance (VND) | Variance (%) | F/U | Note |
|---------|--------|--------|----------------|--------------|-----|------|
| Revenue | 1,000M | 1,050M | 50M | 5% | F | Volume increase |
| COGS | -600M | -630M | -30M | 5% | U | Raw material price |
| Gross Margin | 400M | 420M | 20M | 5% | F | |
| SG&A | -200M | -190M | 10M | 5% | F | Cost savings |

4. Actor can:
   - Drill down: click Revenue → see by product line → by region → by channel
   - Toggle between: amount variance, % variance (default: both)
   - Add commentary (notes attached to variance rows)
   - Set flags: investigate, ok, concern
5. Actor exports report (PDF/Excel/CSV)
6. System saves variance annotations for next period review

### Alternative Paths
- **A1**: Budget vs Forecast (revised) instead of budget vs actual
- **A2**: Year-over-year comparison (this year actual vs last year actual)
- **A3**: Period comparison (current month vs prior month vs same month last year)
- **A4**: Flexible budget variance (adjust for volume difference)

### Exception Paths
- **E1**: No actual data for period → ErrorCodes.BUDGET_NO_ACTUAL_DATA
- **E2**: Budget version does not match reporting period → ErrorCodes.BUDGET_VERSION_PERIOD_MISMATCH

### Rules
- Variance = Actual - Budget (positive = favorable for revenue, unfavorable for expense)
- Variance % = Variance / |Budget| × 100 (protect against division by zero)
- Favorable (F) = revenue higher than budget OR expense lower than budget
- Unfavorable (U) = revenue lower than budget OR expense higher than budget
- Variance significance: > 10% or > 100M VND flagged as significant (configurable)
- Flexible budget variance removed volume impact: budget recalculated at actual volume × budget rate

### Domain Entities
- BudgetVarianceReport, BudgetVarianceLine, BudgetVarianceAnnotation

---

## UC-BUDGET-12: Budget Dashboard & KPI

### Description
Real-time executive dashboard showing budget health: burn rate, remaining budget, revenue achievement, CAPEX utilization, forecast completion.

### Actors
- CFO
- CEO
- Finance Manager

### Preconditions
- Approved budget version active
- Actual data being posted

### Postconditions
- Dashboard rendered with real-time data

### Happy Path
1. User opens Budget → Dashboard
2. System loads current fiscal year budget data
3. Dashboard cards display:

   | KPI | Value | Trend |
   |-----|-------|-------|
   | Revenue Achievement | 78% of target | ↑ |
   | OPEX Utilization | 65% of budget | ↑ |
   | CAPEX Utilization | 42% of budget | → |
   | Gross Margin | 38.5% vs 40% budget | ↓ |
   | Net Profit Achievement | 82% of target | ↑ |
   | Budget Burn Rate | 8.3% / month | → |
   | Days of Budget Left | 45 days (at current rate) | ↓ |
   | YTD Variance | +125M Favorable | ↑ |

4. Charts:
   - Monthly trend: Budget vs Actual (line chart)
   - Department comparison (bar chart)
   - Revenue composition (pie chart by product line)
   - Spending by category (treemap)
5. User can filter: department, period, version
6. Dashboard auto-refresh (every 5 minutes, configurable)

### Alternative Paths
- **A1**: Dashboard export as PDF (executive summary)
- **A2**: Dashboard full-screen mode (presentation)
- **A3**: Email scheduled dashboard report (daily/weekly)

### Exception Paths
- **E1**: No budget data for current year → Empty state with "Create budget" CTA
- **E2**: GL data not posted for current period → show "(last updated: [date])" indicator

### Rules
- Burn rate = Total spent / Number of days in period × 30 (monthly run-rate)
- Revenue achievement = Actual Revenue / Budget Revenue × 100
- Budget utilization = (Actual + Commitment) / Budget × 100
- Forecast completion = Actual + (Remaining based on plan)
- Dashboard data cached (max 5-min stale) for performance
- KPI thresholds: Green (≥ 90%), Yellow (70-90%), Red (< 70%)

### Domain Entities
- BudgetDashboard, BudgetKPI, BudgetKPIDefinition

---

## UC-BUDGET-13: Revenue Budget

### Description
Detailed revenue budgeting: sales volume × unit price by product line, region, channel, customer segment. Support seasonality patterns, growth rate assumptions, and multi-currency pricing.

### Actors
- Sales Manager (enter)
- Finance Manager (review)
- CFO (approve)

### Preconditions
- Product master (Inventory) or service catalog exists
- Customer/region master exists
- Budget structure (UC-BUDGET-01) configured

### Postconditions
- Revenue budget created and submitted for approval

### Happy Path
1. Actor selects Revenue Budget for fiscal year
2. System loads product lines, regions, channels from master data
3. For each product line:
   - Enter sales volume (units) per period
   - Enter unit price (VND) per period
   - System auto-calculates: Revenue = Volume × Price
4. Actor enters growth assumptions:
   - Volume growth % (vs prior year)
   - Price increase % (vs prior year)
5. Actor sets seasonality pattern (e.g., TET = 15% of annual in Jan-Feb)
6. For export revenue: enter in foreign currency + FX rate assumption
7. System calculates: Total Revenue = Σ (Volume_p × Price_p) across all products/periods
8. System validates:
   - Revenue total consistent with corporate target (if set)
   - Volume × Price > 0 for all active products
9. Actor submits for approval

### Alternative Paths
- **A1**: Driver-based revenue budget: enter total market size × market share × ASP
- **A2**: Import sales forecast from CRM (opportunity pipeline → revenue budget)
- **A3**: Contract-based revenue: sum of signed contracts × expected fulfillment %

### Exception Paths
- **E1**: Product not active in catalog → ErrorCodes.BUDGET_PRODUCT_INACTIVE
- **E2**: Revenue below minimum corporate target → Warning (not block) → CFO review
- **E3**: Export revenue FX rate missing → ErrorCodes.BUDGET_FX_RATE_MISSING
- **E4**: No seasonality defined → defaults to equal distribution

### Rules
- Volume: integer, ≥ 0
- Price: ≥ 0 (0 = free/donation — requires annotation)
- Growth % applied to prior year actuals if available
- Seasonality: weights for 12 months sum to 100%
- Multi-currency: converted at planning FX rate (set by Finance)
- Trade discounts and rebates tracked separately (contra-revenue)

### Domain Entities
- RevenueBudgetLine, RevenueBudgetDriver, RevenueSeasonality

---

## UC-BUDGET-14: Expense Budget

### Description
Comprehensive expense budgeting: fixed costs (rent, salary), variable costs (materials, commission), semi-variable costs (utilities). Support headcount planning, depreciation schedule, and procurement plan.

### Actors
- Department Head (enter)
- HR Manager (headcount)
- Finance Manager (review)

### Preconditions
- Cost centers created
- Employee/headcount data available
- FA depreciation schedule available

### Postconditions
- Expense budget created per cost center

### Happy Path
1. Actor selects Expense Budget for department/cost center
2. System loads prior year actuals for reference
3. Actor creates expense lines by category:
   - **Personnel (TK 6421)**: salary, bonus, social insurance (SI 23.5%), health insurance, unemployment insurance, union fees
   - **Office (TK 6423)**: rent, utilities, supplies, communication
   - **Travel (TK 6425)**: domestic/international travel, per diem
   - **Depreciation (TK 6424/6427)**: auto-populated from FA schedule
   - **Professional services**: audit, legal, consulting
   - **Marketing**: advertising, promotion, PR
   - **IT**: software, hardware, cloud services
4. For headcount: enter FTE count × average cost per FTE
5. System auto-calculates SI contributions (employer portion)
6. Actor sets fixed/variable classification
7. System validates: total expense ≤ available budget (if corporate ceiling configured)
8. Actor submits for approval

### Alternative Paths
- **A1**: Zero-based budgeting — each line justified from zero (no reference to prior year)
- **A2**: Incremental budgeting — prior year actual + inflation % (fast approach)
- **A3**: Activity-based budgeting — cost per driver unit × activity volume

### Exception Paths
- **E1**: Headcount cost exceeds HR-approved FTE total → ErrorCodes.BUDGET_FTE_EXCEEDS_LIMIT
- **E2**: Depreciation budget does not match FA schedule → ErrorCodes.BUDGET_DEPR_MISMATCH
- **E3**: SI contribution % below legal rate → ErrorCodes.BUDGET_SI_BELOW_MINIMUM

### Rules
- SI rates (employer): Retirement 14%, Sickness 3%, Occupational 0.5%, Health 3%, Unemployment 1%, Union 2% = total 23.5%
- SI rates (employee): Retirement 8%, Health 1.5%, Unemployment 1% = total 10.5%
- Fixed costs: budget same each month (rent, depreciation)
- Variable costs: budget proportional to driver (sales volume, production volume)
- Semi-variable: base + variable component
- Headcount cost = (Base salary + Allowances + Bonus) × (1 + SI%) × 12 months
- Zero-based: require justification for every line > threshold

### Domain Entities
- ExpenseBudgetLine, HeadcountBudget, ExpenseDriver

---

## UC-BUDGET-15: CAPEX & Cash Flow Budget

### Description
Capital expenditure budget with approval workflow and cash flow budget (inflow/outflow/financing) with monthly detail.

### Actors
- Department Head (request)
- Finance Manager (analyze)
- CFO/Board (approve CAPEX)
- Treasurer (review cash flow)

### Preconditions
- FA asset categories defined
- Debt schedule available (loan repayments)
- Prior year cash balance known

### Postconditions
- CAPEX budget approved
- Cash flow budget balanced

### CAPEX Budget Path
1. Actor creates CAPEX request: asset type (TK 211/213/217), description, estimated cost, useful life, expected ROI
2. Actor selects funding source: internal cash, loan, lease
3. System routes CAPEX request through approval (department → finance → board if > threshold)
4. Board approves → CAPEX added to budget
5. System schedules cash outflow per expected payment milestones

### Cash Flow Budget Path
1. Actor opens Cash Flow Budget
2. System loads:
   - **Inflows**: Revenue collections (from UC-BUDGET-13 × AR collection pattern)
   - **Other inflows**: loan disbursements, asset sales, capital contributions, interest income
3. System loads:
   - **Outflows**: expense payments (from UC-BUDGET-14 × AP payment pattern)
   - **CAPEX outflow** (from CAPEX budget above)
   - **Debt service**: principal + interest (from debt schedule)
   - **Tax payments**: CIT quarterly installments, VAT payments, PIT
   - **Dividends**: proposed dividend schedule
4. System calculates:
   - Net Cash Flow = Total Inflow - Total Outflow
   - Opening Balance (from prior month actual or budgeted)
   - Closing Balance = Opening + Net Cash Flow
5. If Closing Balance < minimum required (e.g., 3 months operating expenses):
   - System flags cash deficit
   - Actor can add financing line: drawdown credit line, delay CAPEX, accelerate AR
6. Actor balances until Closing ≥ minimum (or CFO approves deficit plan)

### Alternative Paths
- **A1**: Direct method cash flow (actual receipts and payments)
- **A2**: Indirect method (P&L + balance sheet changes)
- **A3**: 13-week rolling cash forecast (short-term focus)

### Exception Paths
- **E1**: CAPEX + OPEX > total available cash → ErrorCodes.BUDGET_CASH_DEFICIT
- **E2**: Asset useful life inconsistent with FA policy → ErrorCodes.BUDGET_USEFUL_LIFE_INVALID
- **E3**: CAPEX funding source not specified → ErrorCodes.BUDGET_CAPEX_FUNDING_REQUIRED
- **E4**: Cash closing balance negative → ErrorCodes.BUDGET_CASH_NEGATIVE_CLOSING
- **E5**: Debt service coverage < 1.25x → ErrorCodes.BUDGET_DSC_INSUFFICIENT

### Rules
- CAPEX > 500M VND requires Board approval (configurable)
- CAPEX < 50M VND can be expensed (not capitalized) per FA policy
- Cash minimum balance: 3 months OPEX (configurable)
- Debt Service Coverage = (EBITDA) / (Principal + Interest) ≥ 1.25x (VAS covenant)
- Financing decisions need CFO sign-off
- VAT on CAPEX: input VAT recoverable shown separately in cash flow
- Exchange rate impact on foreign currency debt shown as separate line

### Domain Entities
- CAPEXRequest, CAPEXApproval, CashFlowBudgetLine, CashFlowFinancing
