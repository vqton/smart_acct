# Budget Module — Implementation Plan

**Version**: 1.0
**Date**: 2026-06-30
**Total Tasks**: 18 (4 phases)
**Estimate**: 12 weeks (1 team)

---

## Phase 0: Foundation & Setup (Week 1-2)

### Task 0.1: Domain Entities (`domain/budget.py`)

**Files**: `domain/budget.py`, update `domain/__init__.py`

Enums:
- `BudgetType`: REVENUE, EXPENSE, CAPEX, CASH_FLOW, BALANCE_SHEET
- `BudgetVersionStatus`: DRAFT, PROPOSED, UNDER_REVIEW, APPROVED, REJECTED, REVISED, CONSOLIDATED, ARCHIVED
- `BudgetPeriodType`: MONTHLY, QUARTERLY, ANNUAL
- `BudgetControlLevel`: NONE, WARNING_ONLY, SOFT_BLOCK, HARD_BLOCK
- `BudgetControlScope`: ACCOUNT, COST_CENTER, DEPARTMENT, PROJECT, GLOBAL
- `BudgetDimensionType`: COST_CENTER, DEPARTMENT, PROJECT, PRODUCT_LINE, REGION, CHANNEL, FUND_SOURCE
- `BudgetCategoryType`: FIXED, VARIABLE, SEMI_VARIABLE, DRIVER_BASED
- `AdjustmentType`: VIREMENT, SUPPLEMENTARY, EMERGENCY, REDUCTION
- `ApprovalStatus`: PENDING, APPROVED, REJECTED, CONDITIONALLY_APPROVED
- `VarianceFlag`: FAVORABLE, UNFAVORABLE, NEUTRAL
- `KPIThreshold`: GREEN, YELLOW, RED

Pydantic Entities:
- `BudgetStructure` — budget types, dimensions, config
- `BudgetDimension` — dimension type, values
- `BudgetCategory` — category grouping
- `BudgetPeriod` — fiscal year period config
- `BudgetCalendar` — budget cycle timeline
- `BudgetCalendarPhase` — phase definitions
- `BudgetTemplate` — reusable budget template
- `BudgetTemplateLine` — line item in template
- `BudgetVersion` — version with status tracking
- `BudgetPlan` — actual budget data container
- `BudgetPlanLine` — line item amounts by period
- `BudgetPlanDriver` — driver-based calc (qty × rate)
- `BudgetActual` — budget vs actual comparison
- `BudgetCommitment` — PO/contract encumbrance
- `BudgetControlRule` — control level config
- `BudgetOverride` — override authorization
- `BudgetBlockLog` — block audit trail
- `BudgetAdjustment` — adjustment request
- `BudgetAdjustmentLine` — source/target lines
- `BudgetApprovalWorkflow` — approval routing
- `BudgetApprovalStep` — step in workflow
- `BudgetApprovalLog` — approval history
- `BudgetConsolidation` — consolidation run
- `BudgetConsolidationEntity` — entity in consolidation
- `BudgetICTransaction` — intercompany elimination
- `BudgetDashboard` — dashboard config
- `BudgetKPI` — KPI definition
- `BudgetKPIValue` — KPI actual value
- `CAPEXRequest` — CAPEX approval request
- `CashFlowBudgetLine` — cash flow line
- `CashFlowFinancing` — financing line
- `BudgetVarianceReport` — variance analysis
- `BudgetVarianceLine` — variance line
- `BudgetVarianceAnnotation` — commentary
- `BudgetAuditLog` — audit trail

### Task 0.2: SQLAlchemy Models (`infrastructure/models/budget_models.py`)

**Tables** (20):
- `budget_structures`, `budget_dimensions`, `budget_categories`
- `budget_calendars`, `budget_calendar_phases`, `budget_periods`
- `budget_templates`, `budget_template_lines`
- `budget_versions`
- `budget_plans`, `budget_plan_lines`, `budget_plan_drivers`
- `budget_actuals`, `budget_commitments`
- `budget_control_rules`, `budget_overrides`, `budget_block_logs`
- `budget_adjustments`, `budget_adjustment_lines`
- `budget_approval_workflows`, `budget_approval_steps`, `budget_approval_logs`
- `budget_consolidations`, `budget_consolidation_entities`
- `budget_ic_transactions`
- `budget_kpi_definitions`, `budget_kpi_values`
- `budget_audit_logs`
- `capex_requests`, `cash_flow_budget_lines`

### Task 0.3: Alembic Migration

**Branch**: off `2fa3b4c5d6e7` (after Payroll tables)

### Task 0.4: Error Codes (`domain/i18n.py`)

Add `BUDGET_` prefix error codes (80+ entries):
- `BUDGET_NO_COA_ACCOUNTS`, `BUDGET_DIMENSION_DUPLICATE`, `BUDGET_TYPE_NO_ACCOUNTS`
- `BUDGET_PERIOD_EXISTS`, `BUDGET_INVALID_DATE_RANGE`
- `BUDGET_CIRCULAR_FORMULA`, `BUDGET_TEMPLATE_DUPLICATE`, `BUDGET_FORMULA_INVALID_REF`
- `BUDGET_IMPORT_INVALID_FORMAT`, `BUDGET_AMOUNT_EXCEEDS_LIMIT`, `BUDGET_MANDATORY_ITEM_MISSING`
- `BUDGET_REVENUE_NEGATIVE`, `BUDGET_PRICE_WO_VOLUME`, `BUDGET_CAP_EXCEEDED`
- `BUDGET_NO_APPROVER`, `BUDGET_SELF_APPROVAL_DENIED`, `BUDGET_IN_LOCKED_WORKFLOW`
- `BUDGET_LOCK_CANNOT_UNLOCK`, `BUDGET_VERSION_MISMATCH`
- `BUDGET_ADJUST_SOURCE_EXHAUSTED`, `BUDGET_ADJUST_MATERIALITY_EXCEEDED`
- `BUDGET_ADJUST_PERIOD_CLOSED`, `BUDGET_ADJUST_COMMITMENT_EXCEEDS`
- `BUDGET_ACCOUNT_MISMATCH`, `BUDGET_VERSION_REQUIRED`
- `BUDGET_CONSOLIDATION_INCOMPLETE`, `BUDGET_IC_MISMATCH`, `BUDGET_FX_RATE_MISSING`
- `BUDGET_NO_ACTUAL_DATA`, `BUDGET_VERSION_PERIOD_MISMATCH`
- `BUDGET_PRODUCT_INACTIVE`, `BUDGET_FTE_EXCEEDS_LIMIT`, `BUDGET_DEPR_MISMATCH`
- `BUDGET_SI_BELOW_MINIMUM`, `BUDGET_CASH_DEFICIT`, `BUDGET_USEFUL_LIFE_INVALID`
- `BUDGET_CAPEX_FUNDING_REQUIRED`, `BUDGET_CASH_NEGATIVE_CLOSING`, `BUDGET_DSC_INSUFFICIENT`

Add Vietnamese translations in `translations/vi/LC_MESSAGES/messages.po`

**Acceptance**: Domain entities pass type checks, migration creates tables, error codes registered.

---

## Phase 1: Core CRUD + Master Data (Week 3-5)

### Task 1.1: Budget Structure CRUD (UC-BUDGET-01)

- Repository: `create_structure`, `get_structure`, `update_structure`, `delete_structure`, `list_structures`
- Use case: `create_budget_structure`, `update_budget_structure`
- Route: `GET/POST/PUT/DELETE /api/v1/budget/structures`
- Tests: 8 tests

### Task 1.2: Budget Period & Calendar (UC-BUDGET-02)

- Repository: `create_calendar`, `get_calendar`, `update_calendar`, `list_calendars`, `get_periods`
- Use case: `create_budget_calendar`, `get_budget_calendar`
- Route: `GET/POST/PUT /api/v1/budget/calendars`
- Tests: 6 tests

### Task 1.3: Budget Template CRUD (UC-BUDGET-03)

- Repository: `create_template`, `get_template`, `update_template`, `delete_template`, `list_templates`
- Use case: `create_budget_template`, `update_budget_template`, `apply_template_to_cost_center`
- Route: `GET/POST/PUT/DELETE /api/v1/budget/templates`
- Tests: 8 tests

### Task 1.4: Budget Plan Draft (UC-BUDGET-04)

- Repository: `create_plan`, `get_plan`, `update_plan`, `delete_plan`, `list_plans`, `copy_from_prior_year`, `import_from_excel`
- Use case: `create_budget_plan`, `update_budget_plan`, `submit_budget_plan`
- Route: `GET/POST/PUT /api/v1/budget/plans`
- Excel import: `POST /api/v1/budget/plans/import`
- Tests: 15 tests (incl. validation, import, copy from prior)

---

## Phase 2: Workflow & Control (Week 6-8)

### Task 2.1: Approval Workflow (UC-BUDGET-05)

- Repository: `create_workflow`, `get_workflow`, `submit_for_approval`, `approve_step`, `reject_step`, `recall`
- Use case: `submit_budget_for_approval`, `approve_budget`, `reject_budget`
- Route: `POST /api/v1/budget/plans/{id}/submit`, `POST /api/v1/budget/plans/{id}/approve`, `POST /api/v1/budget/plans/{id}/reject`
- Notification integration (email/in-app)
- Tests: 12 tests (incl. delegation, escalation, parallel approval)

### Task 2.2: Budget Versioning (UC-BUDGET-06)

- Repository: `create_version`, `get_version`, `lock_version`, `unlock_version`, `compare_versions`, `list_versions`
- Use case: `create_budget_version`, `lock_budget_version`, `compare_versions`
- Route: `GET/POST /api/v1/budget/versions`, `GET /api/v1/budget/versions/{id}/compare?other_id=X`
- Tests: 8 tests

### Task 2.3: Budget Adjustment (UC-BUDGET-07)

- Repository: `create_adjustment`, `get_adjustment`, `approve_adjustment`, `reject_adjustment`, `list_adjustments`
- Use case: `request_budget_adjustment`, `approve_adjustment`, `execute_virement`
- Route: `POST /api/v1/budget/adjustments`, `POST /api/v1/budget/adjustments/{id}/approve`
- Tests: 10 tests (incl. virement, supplementary, emergency)

### Task 2.4: Budget Control (UC-BUDGET-09)

- Repository: `create_control_rule`, `get_control_rule`, `check_budget_availability`, `create_override`, `log_block`
- Use case: `configure_budget_control`, `check_budget_available`, `override_budget_block`
- Service: `BudgetControlService` — real-time check called by AP/AR/GL/PO transaction posting
- Route: `GET/POST/PUT /api/v1/budget/control-rules`, `POST /api/v1/budget/override`
- Integration hooks: AP invoice, PO, GL journal, AR credit/debit note
- Tests: 15 tests (incl. all control levels, override, edge cases)

---

## Phase 3: Monitoring & Reporting (Week 9-10)

### Task 3.1: Budget Execution Monitor (UC-BUDGET-08)

- Repository: `get_execution_data`, `get_actual_by_period`, `get_commitment_by_period`, `get_free_balance`
- Use case: `get_budget_execution`, `get_free_balance_report`
- GL actuals integration (queries posted JE by account + CC + period)
- AP commitment integration (PO open amounts)
- Route: `GET /api/v1/budget/execution`, `GET /api/v1/budget/execution/{cost_center_id}`
- Tests: 8 tests

### Task 3.2: Budget vs Actual Analysis (UC-BUDGET-11)

- Repository: `get_variance_report`, `get_variance_detail`, `save_annotation`, `get_annotations`
- Use case: `run_variance_analysis`, `annotate_variance`
- Route: `GET /api/v1/budget/variance`, `POST /api/v1/budget/variance/{line_id}/annotate`
- Export: PDF/Excel/CSV
- Tests: 8 tests

### Task 3.3: Budget Dashboard & KPI (UC-BUDGET-12)

- Repository: `get_dashboard_data`, `get_kpi_values`, `calculate_burn_rate`
- Use case: `get_budget_dashboard`, `get_kpi_summary`
- Route: `GET /api/v1/budget/dashboard`, `GET /api/v1/budget/kpi`
- Tests: 6 tests

---

## Phase 4: Full Coverage (Week 11-12)

### Task 4.1: Revenue Budget (UC-BUDGET-13)

- Repository: `create_revenue_lines`, `get_revenue_by_product`, `get_seasonality`
- Use case: `create_revenue_budget`, `import_sales_forecast`
- Route: `POST /api/v1/budget/revenue`, `GET /api/v1/budget/revenue`
- Tests: 8 tests

### Task 4.2: Expense Budget (UC-BUDGET-14)

- Repository: `create_expense_lines`, `get_expense_by_department`, `get_headcount_budget`
- Use case: `create_expense_budget`, `create_headcount_budget`, `zero_based_budget`
- Route: `POST /api/v1/budget/expense`, `GET /api/v1/budget/expense`
- Tests: 10 tests (incl. SI calc, headcount limits)

### Task 4.3: CAPEX & Cash Flow Budget (UC-BUDGET-15)

- Repository: `create_capex_request`, `approve_capex`, `get_capex_budget`
- Use case: `create_capex_request`, `approve_capex_request`, `create_cash_flow_budget`
- Route: `POST /api/v1/budget/capex`, `POST /api/v1/budget/capex/{id}/approve`, `POST /api/v1/budget/cash-flow`
- Tests: 12 tests (incl. CAPEX approval limits, cash balance rules, DSCR)

### Task 4.4: Budget Consolidation (UC-BUDGET-10)

- Repository: `run_consolidation`, `get_consolidation_result`, `identify_ic_transactions`
- Use case: `consolidate_budget`, `eliminate_intercompany`
- Route: `POST /api/v1/budget/consolidation`, `GET /api/v1/budget/consolidation/{id}`
- Tests: 8 tests

---

## Summary Test Plan

| Phase | Tasks | Tests | Cumulative |
|-------|-------|-------|------------|
| Phase 0 | 4 (setup) | 0 | 0 |
| Phase 1 | 4 (CRUD) | 37 | 37 |
| Phase 2 | 4 (workflow) | 45 | 82 |
| Phase 3 | 3 (reporting) | 22 | 104 |
| Phase 4 | 4 (full) | 38 | 142 |
| **Total** | **19** | **142** | **142** |

## Presentation Routes

| Blueprint | Path | Endpoints |
|-----------|------|-----------|
| **budget** | `/api/v1/budget` | |
| | `GET/POST/PUT/DELETE /structures` | 4 |
| | `GET/POST/PUT /calendars` | 3 |
| | `GET/POST/PUT/DELETE /templates` | 4 |
| | `GET/POST/PUT /plans` | 3 |
| | `POST /plans/{id}/submit` | 1 |
| | `POST /plans/{id}/approve` | 1 |
| | `POST /plans/{id}/reject` | 1 |
| | `POST /plans/{id}/recall` | 1 |
| | `GET/POST /versions` | 2 |
| | `GET /versions/{id}/compare` | 1 |
| | `POST /versions/{id}/lock` | 1 |
| | `POST /versions/{id}/unlock` | 1 |
| | `POST /adjustments` | 1 |
| | `POST /adjustments/{id}/approve` | 1 |
| | `POST /adjustments/{id}/reject` | 1 |
| | `GET /execution` | 1 |
| | `GET /execution/{cost_center_id}` | 1 |
| | `GET/POST/PUT /control-rules` | 3 |
| | `POST /override` | 1 |
| | `GET /variance` | 1 |
| | `POST /variance/{line_id}/annotate` | 1 |
| | `GET /dashboard` | 1 |
| | `GET /kpi` | 1 |
| | `POST /revenue` | 1 |
| | `POST /expense` | 1 |
| | `POST /capex` | 1 |
| | `POST /capex/{id}/approve` | 1 |
| | `POST /cash-flow` | 1 |
| | `POST /consolidation` | 1 |
| | `GET /consolidation/{id}` | 1 |
| | **Total endpoints** | **~40** |
