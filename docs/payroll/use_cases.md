# Payroll Module — Use Cases (UC-PR-01 to UC-PR-15)

**Version**: 1.0  
**Date**: 2026-06-30  
**Regulatory Baseline**: TT 99/2025/TT-BTC, PIT Law 109/2025/QH15, SI Law 41/2024/QH15, Decree 158/2025/NĐ-CP, Decree 293/2025/NĐ-CP

---

## UC-PR-01: Employee Master Data Management

**Priority**: P0 | **Complexity**: Medium

### Description
Create, read, update, deactivate employee records. Central repository for all employee information required for payroll processing.

### Preconditions
- User has HR Manager or Payroll Admin role

### Happy Path
1. User navigates to Employee Management → Add Employee
2. System displays employee creation form with fields: code, name, DOB, gender, ID number, tax code, SI book number, bank account, department, position, region, start date, contract type
3. User fills mandatory fields and submits
4. System validates:
   - Employee code unique
   - Tax code format (10 or 13 digits)
   - ID number format (9 or 12 digits)
   - Region (1/2/3/4) valid
   - Start date not in future > 30 days
5. System creates employee record → Returns employee ID
6. User can edit, view history, deactivate (soft delete)

### Alternative Paths
- **Bulk import**: Upload Excel/CSV → validate all rows → report errors → confirm import
- **Update tax code**: Requires re-validation, log change in audit trail
- **Deactivate employee**: Check no active contract → warn if payroll exists for current period → confirm

### Exception Paths
- Duplicate employee code → reject with error `EMPLOYEE_CODE_DUPLICATE`
- Invalid tax code format → reject with error `TAX_CODE_INVALID_FORMAT`
- Missing mandatory fields → reject with error `MANDATORY_FIELD_MISSING`
- Employee with active payroll in current period → warn but allow deactivation

### Validation Rules
| Field | Rule | Error Code |
|-------|------|------------|
| employee_code | Required, unique, max 20 chars, alphanumeric | EMPLOYEE_CODE_EMPTY / DUPLICATE |
| full_name | Required, max 100 chars | NAME_EMPTY |
| id_number | Required if Vietnamese, 9 or 12 digits | ID_INVALID |
| tax_code | Required, 10 or 13 digits, valid checksum | TAX_CODE_INVALID |
| si_book_number | Optional, unique if provided | SI_BOOK_DUPLICATE |
| region | Required, 1-4 | REGION_INVALID |
| bank_account | Required if payment method = bank | BANK_ACCOUNT_EMPTY |

---

## UC-PR-02: Employee Contract Management

**Priority**: P0 | **Complexity**: Medium

### Description
Manage employment contracts lifecycle: create, amend, renew, terminate. Each employee has one active contract at any time.

### Happy Path
1. User navigates to Employee → Contracts → Add Contract
2. System displays form: contract type (indefinite/fixed-term/seasonal), start date, end date (if fixed), base salary, position allowance, other allowances, working days/month
3. User enters data and submits
4. System validates:
   - No overlapping active contract
   - End date > start date
   - Base salary ≥ regional minimum wage
5. System creates contract → Sets previous contract to "expired" status
6. Contract start date triggers SI registration update

### Alternative Paths
- **Contract amendment**: Create new version → previous version archived
- **Contract renewal**: Extend end date or create new contract
- **Termination**: Set end date, trigger SI de-registration, final pay calculation

### Exception Paths
- Overlapping active contract → error `ACTIVE_CONTRACT_EXISTS`
- End date before start date → error `END_DATE_BEFORE_START`
- Base salary below minimum wage → error `SALARY_BELOW_MINIMUM`
- Contract type = fixed-term but no end date → error `FIXED_TERM_NO_END_DATE`

### Key Data: Base Salary Components
| Component | Included in SI Base? | Notes |
|-----------|---------------------|-------|
| Base salary (lương chính) | Yes | Per Decree 158 |
| Position allowance (phụ cấp chức vụ) | Yes | Included |
| Seniority allowance (phụ cấp thâm niên) | Yes | Included |
| Responsibility allowance (phụ cấp trách nhiệm) | Yes | Included |
| Meal allowance (tiền ăn ca) | No | Unless specified in contract & regular |
| Phone allowance (tiền điện thoại) | No | Unless specified in contract & regular |
| Transport allowance (tiền xăng xe) | No | Unless specified in contract & regular |
| Performance bonus (thưởng) | No | Variable by nature |

---

## UC-PR-03: Timesheet / Attendance Import

**Priority**: P0 | **Complexity**: High

### Description
Import and validate monthly attendance data from Excel/CSV or direct entry. Basis for calculating salary.

### Happy Path
1. User selects month/year → System shows import interface
2. User downloads template or uploads file
3. System parses file → Validates:
   - Employee codes exist in system
   - Working days ≤ standard days (unless overtime)
   - Data types correct (numeric for days, hours)
4. System shows validation summary: N records valid, M errors
5. User fixes errors → re-uploads
6. User confirms import → System saves timesheet data
7. System computes default working days if not provided (standard = 26 days for monthly salary)

### Data Structure
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| employee_code | str | Yes | Must exist in Employee master |
| working_days | Decimal | Yes | 0-31, ≤ standard_days |
| overtime_weekday_hours | Decimal | No | Max 4h/day per Labor Code |
| overtime_weekend_hours | Decimal | No | Max 8h/day |
| overtime_holiday_hours | Decimal | No | Max 8h/day |
| sick_leave_days | Decimal | No | Requires doctor note for >3 days |
| unpaid_leave_days | Decimal | No | 0-31 |
| paid_leave_days | Decimal | No | Annual leave, max carryover |

### Alternative Paths
- **Direct entry**: Manual input per employee via grid interface
- **HRMS integration**: API pull from timekeeping system

### Exception Paths
- Employee not found → error `EMPLOYEE_NOT_FOUND` with row reference
- Working days > standard + overtime cap → error `DAYS_EXCEED_MAX`
- Sick leave > 14 days → warning: triggers SI suspension rules

---

## UC-PR-04: Payroll Computation (Monthly)

**Priority**: P0 | **Complexity**: Critical

### Description
Core payroll engine. Computes gross salary, deductions, PIT, net pay, and employer costs for all employees in a period.

### Preconditions
- Timesheet data exists for the period
- Employee contracts are active
- No existing payroll run for the period in "computed" or later status (unless adjustment)

### Happy Path
1. User selects period (month/year) → Clicks "Run Payroll"
2. System checks for existing run → Creates new PayrollRun (draft)
3. For each active employee:
   a. **Gross salary**: Base salary × (working_days / standard_days) + overtime + allowances
   b. **SI base determination**:
      - Sum base salary + position allowance + regular supplements per contract
      - Clamp: min = regional minimum wage, max = 20× reference level
   c. **Employee deductions**:
      - SI = 8% × SI base
      - HI = 1.5% × SI base
      - UI = 1% × SI base
      - Advance repayments (from pending advances)
   d. **Taxable income**:
      - Gross + non-salary taxable benefits
      - − exempt income (overtime premium, innovation income)
      - − SI/HI/UI employee portion
      - − personal relief (15,500,000)
      - − dependent relief (6,200,000 × count)
      - − supplementary pension / life insurance (within limits)
   e. **PIT**: Apply 5-bracket progressive table
   f. **Net pay**: Gross − employee SI/HI/UI − PIT − advances − other deductions
   g. **Employer costs**:
      - SI = 17.5% × SI base
      - HI = 3% × SI base
      - UI = 1% × SI base
      - OCC = 0.5% × SI base
      - KPCĐ = 2% × SI base
4. System computes totals → Status = "computed"
5. User reviews summary → Clicks "Approve"
6. Status = "approved" → No further editing allowed without reversal

### PIT Engine Logic (5-Bracket, from 2026)
```
taxable = max(0, taxable_income)
tax = 0

if taxable > 100,000,000:
    tax += (taxable - 100,000,000) * 0.35
    taxable = 100,000,000
if taxable > 60,000,000:
    tax += (taxable - 60,000,000) * 0.30
    taxable = 60,000,000
if taxable > 30,000,000:
    tax += (taxable - 30,000,000) * 0.20
    taxable = 30,000,000
if taxable > 10,000,000:
    tax += (taxable - 10,000,000) * 0.10
    taxable = 10,000,000
tax += taxable * 0.05

# Simplified formula (equivalent):
# tax = taxable * rate - progressive_deduction
# Progressive deductions: 0 | 500k | 3,500k | 9,500k | 19,500k
```

### Alternative Paths
- **Adjustment run**: For retroactive changes → computed separately, flags as adjustment
- **Partial month**: Prorate base salary, prorate personal relief
- **Zero payroll**: No active employees → create empty run

### Exception Paths
- No timesheet data → error `TIMESHEET_MISSING`
- Employee has no active contract → error `NO_ACTIVE_CONTRACT`
- Employee SI base < minimum wage → error `SI_BELOW_MINIMUM` (require override)
- Net pay negative → error `NET_PAY_NEGATIVE` (require manager override)
- Calculation mismatch > 1,000 VND in parallel check → error `CALCULATION_MISMATCH`

---

## UC-PR-05: PIT Withholding & Declaration

**Priority**: P0 | **Complexity**: Critical

### Description
Monthly/quarterly PIT declaration and payment. Withhold PIT from salary, declare to tax authority, issue withholding certificates.

### Happy Path (Monthly)
1. After payroll run approved, system generates PIT declaration
2. Declaration includes: total income, exempt income, deductions, tax for all employees
3. User reviews declaration → Submits via HTKK export (XML) or API
4. System records submission date and reference
5. On payment day: user records PIT payment → System updates status

### Happy Path (Quarterly)
- Similar to monthly but aggregated quarterly
- Deadline: last day of month following quarter

### PIT Withholding Certificate (Decree 70/2025/NĐ-CP)
- Electronic format required from 01/06/2025
- Issued when: employee requests, upon termination, annual finalization
- Content: employer info, employee info, total income, tax withheld per month

### Alternative Paths
- **Non-resident employee**: Flat 20% rate (no progressive table)
- **Seasonal contract <3 months**: Withhold 10% (no progressive, unless income only source → Form 23/CK-TNCN)
- **Multiple employers**: Employee must choose one for personal relief; others withhold at 10% (transition rules)

### Exception Paths
- Tax authority portal unavailable → generate XML for later upload
- PIT law change mid-year → dual-bracket support for transition
- Employee requests immediate certificate → generate ad-hoc

---

## UC-PR-06: SI/HI/UI Contribution Calculation & Declaration

**Priority**: P0 | **Complexity**: High

### Description
Calculate and declare social, health, unemployment insurance contributions. Submit to BHXH e-portal.

### Happy Path
1. After payroll run, system computes SI declaration by employee:
   - SI base salary (from payroll)
   - Employee contributions: SI 8% + HI 1.5% + UI 1%
   - Employer contributions: SI 17.5% + HI 3% + UI 1% + OCC 0.5% + KPCĐ 2%
2. System generates TK1-TS declaration data
3. User exports → Submits via eBHXH / VssID / DVC portal
4. Record C12-TS confirmation reference
5. On payment: record payment date, amount, bank transaction ref

### Alternative Paths
- **Voluntary SI**: separate tracking (not in payroll module)
- **New employees mid-month**: partial month contributions
- **Sick leave >14 days**: SI suspension → back payment later

### Exception Paths
- SI portal rejects → parse error XML → fix and resubmit
- Late payment → system calculates 0.03%/day interest
- Employee SI base change → trigger adjustment declaration

---

## UC-PR-07: Salary Payment

**Priority**: P0 | **Complexity**: Medium

### Description
Process salary disbursement via bank transfer (preferred) or cash. Generate bank file, record payment.

### Happy Path (Bank Transfer)
1. User selects approved payroll run → Clicks "Pay Salary"
2. Selects payment method: "Bank Transfer"
3. System generates bank file (required format: VietinBank, BIDV, Vietcombank, Techcombank, etc.)
4. User downloads bank file → Uploads to internet banking
5. After bank confirmation, user uploads payment confirmation → System marks PayrollLine as "paid"
6. Cash integration: SmartACCT Cash module records outgoing payment

### Alternative Paths
- **Cash payment**: Generate cash payment order → Cash module creates CashPayment record
- **Partial payment**: Select specific employees to pay
- **Combined**: Some employees bank, some cash

### Exception Paths
- Bank transfer rejected (wrong account) → mark employee as "payment failed", notify HR
- Bank system down → switch to cash or reschedule
- Employee account closed → notify payroll clerk for manual handling

---

## UC-PR-08: GL Posting (Payroll Cost Allocation)

**Priority**: P0 | **Complexity**: High

### Description
Post payroll costs to General Ledger: salary expense, insurance payable, PIT payable. Allocate costs to correct cost centers.

### Happy Path
1. After payroll approved and paid, user clicks "Post to GL"
2. System generates GL entries per employee's department/cost center:
   - Debit: 622/627/641/642/241 (gross salary + employer contributions)
   - Credit: 3341 (gross salary)
   - Credit: 3383 (total SI), 3384 (HI), 3385 (UI), 3386 (OCC), 3382 (KPCĐ)
   - Credit: 3335 (PIT)
3. System validates: total debits = total credits (balance constraint)
4. GLUseCases.create_entry() called with source_module='payroll'
5. User reviews summary → Confirms

### Cost Allocation Logic
| Department Type | Debit Account | Example |
|----------------|---------------|---------|
| Manufacturing / Production | 622 | Factory workers |
| Production support | 627 | QC, warehouse, factory management |
| Sales | 641 | Sales team |
| Administration | 642 | HR, accounting, IT, management |
| Construction | 241 | Capital projects |

### Exception Paths
- GL period closed → error `PERIOD_CLOSED` → cannot post
- Debits ≠ Credits → error `UNBALANCED_ENTRY` → system must recompute
- Account 3341/338x/3335 not configured → error `ACCOUNT_NOT_CONFIGURED`

---

## UC-PR-09: Payroll Reports & Dashboards

**Priority**: P1 | **Complexity**: Medium

### Report List
| Report | Description | Format |
|--------|-------------|--------|
| Payroll Summary | By department: total gross, deductions, net | HTML, PDF, Excel |
| Payroll Detail | Per employee breakdown | HTML, PDF, Excel |
| SI Declaration Detail | Per employee: SI base, contributions | Excel, XML |
| PIT Declaration Detail | Per employee: income, exempt, taxable, PIT | Excel, XML (HTKK format) |
| Cost Allocation | By GL account: total debit per cost center | HTML, PDF, Excel |
| Payroll Register | Monthly run log | HTML, PDF |
| Annual PIT Summary | Year-to-date per employee | PDF, Excel |
| SI Payment History | Monthly contributions paid | HTML, PDF |
| Bank Transfer File | Machine-readable for internet banking | CSV/TXT (bank-specific format) |

### Dashboard KPIs
- Current month total payroll cost
- Month-over-month change
- Average salary by department
- SI cost as % of total payroll
- PIT as % of total payroll
- Headcount by department

---

## UC-PR-10: Annual PIT Finalization

**Priority**: P1 | **Complexity**: High

### Description
Annual reconciliation of monthly/quarterly PIT withholding vs actual annual liability. Prepare and submit quyết toán thuế TNCN.

### Happy Path
1. After year-end, user initiates annual finalization
2. System aggregates 12-month data per employee:
   - Total income (from all payroll runs)
   - Total exempt income (overtime, innovation)
   - Total deductions (SI/HI/UI)
   - Personal relief (15.5M × months worked)
   - Dependent relief (6.2M × dependents × months)
   - Total tax withheld
3. System computes actual annual liability (5-bracket table, annualized)
4. For each employee: compare withheld vs actual liability
   - Over-withholding → refund due
   - Under-withholding → additional tax due
5. System generates 05/QTT-TNCN form + appendices 05-1/BK, 05-2/BK, 05-3/BK
6. User exports → Submits via HTKK
7. Deadline: 31/03 of following year (for employer submission)

### Exceptions
- Employee with multiple employers → must self-finalize (not employer responsibility)
- Employee departing Vietnam permanently → early finalization
- Employee on maternity leave most of year → adjust personal relief calculation

---

## UC-PR-11: Employee Self-Service

**Priority**: P1 | **Complexity**: Medium

### Features
- View current & historical payslips (PDF download)
- View PIT withholding history
- View SI contribution history
- Download PIT withholding certificate (for tax finalization)
- Submit/update dependent registration
- Request salary advance
- View annual PIT finalization result

### Integration
- Employee portal: separate Flask blueprint or integration with presentation layer
- Authentication: JWT token (same as SmartACCT auth)
- Authorization: Employee can only view own data

---

## UC-PR-12: Payroll Adjustment & Retroactive Changes

**Priority**: P1 | **Complexity**: Medium

### Description
Handle retroactive salary changes, corrections, one-off adjustments after payroll is approved or paid.

### Types
| Type | Description | Example |
|------|-------------|---------|
| Retroactive increase | Salary increase applied from earlier month | Promotion effective 2 months ago |
| Correction | Error in previous computation | Wrong attendance data |
| One-off bonus | Ad-hoc payment | Annual bonus, project bonus |
| Penalty | Deduction for violation | Late arrival penalty |
| Back-pay | Legal settlement | Court-ordered back wages |

### Process
1. User selects "Create Adjustment" → specifies type, employee, period, amount, reason
2. System validates adjustment against original payroll run
3. Adjustment creates delta PayrollLine:
   - Positive adjustment: increase gross → recalculate SI/PIT/net
   - Negative adjustment: decrease → recalculate
4. System recomputes PIT on delta (marginal rate)
5. Adjustment run status = "computed"
6. On next regular payroll: include adjustment net amount
7. GL: post adjustment entry with explanation

---

## UC-PR-13: Multi-Period Allocation (Accruals)

**Priority**: P2 | **Complexity**: High

### Description
Handle month-end salary accruals when payroll is computed in the following month. Accrue estimated salary cost to correct period.

### Process
1. Month M ends, but payroll will be computed in month M+1
2. System creates accrual journal entry on last day of month M:
   - Debit 622/627/641/642 (estimated salary + employer contributions)
   - Credit 335 (accrued expenses)
3. When actual payroll is computed in M+1:
   - System generates reversing entry on first day of M+1
   - Posts actual payroll entries in M+1
4. If actual differs from estimate → adjustment posted in M+1

### Estimation Methods
- Previous month actual (default)
- User-entered estimated amounts
- Budget-based estimation

---

## UC-PR-14: Integration with HRMS/Timekeeping

**Priority**: P2 | **Complexity**: Medium

### Integration Points
| System | Integration Type | Data Flow |
|--------|-----------------|-----------|
| HRMS | REST API / Import | Employee data, contracts, org structure |
| Timekeeping | REST API / Import | Attendance, overtime, leave |
| Bank | File export | Salary transfer file |
| eBHXH | API / XML export | SI declaration (TK1-TS) |
| iTax / HTKK | XML export | PIT declaration (05/KK-TNCN) |
| DVCQG | API integration | Submit government declarations |

### API Design (Proposed)
```
POST /api/v1/payroll/employees/import     # Bulk employee import
POST /api/v1/payroll/timesheet/import     # Timesheet import
GET  /api/v1/payroll/runs/{period}        # Get payroll run
POST /api/v1/payroll/runs                 # Create payroll run
POST /api/v1/payroll/runs/{id}/compute   # Execute computation
POST /api/v1/payroll/runs/{id}/approve   # Approve
POST /api/v1/payroll/runs/{id}/pay       # Process payment
POST /api/v1/payroll/runs/{id}/gl-post   # Post to GL
GET  /api/v1/payroll/runs/{id}/reports   # Generate reports
GET  /api/v1/payroll/pit/{period}        # PIT declaration
GET  /api/v1/payroll/si/{period}         # SI declaration
```

---

## UC-PR-15: Compliance & Audit Trail

**Priority**: P1 | **Complexity**: Medium

### Description
Full audit trail for all payroll actions. Regulatory compliance checks. Reports for inspection.

### Audit Log Events
| Event | Data Captured |
|-------|---------------|
| Employee create/update | Who, when, what fields changed |
| Contract create/amend | Previous vs new values |
| Payroll run create | Who triggered, parameters |
| Payroll approval | Approver, timestamp |
| Payroll manual override | Who overrode, reason, original values |
| PIT declaration submit | Submission ref, total amounts, timestamp |
| SI declaration submit | Submission ref, total amounts |
| GL posting | Journal entry reference, vs expected |
| Report generation | Report type, parameters, timestamp |

### Regulatory Compliance Checks
- Monthly: SI contribution adequacy check
- Monthly: PIT withholding accuracy check
- Quarterly: Minimum wage compliance
- Annual: PIT finalization vs monthly totals
- Annual: Social insurance contribution reconciliation

### Retention
- Payroll data: 5 years minimum (per accounting law)
- Employee contracts: 3 years after termination
- PIT records: 10 years (per tax law)
- SI records: lifetime (per SI law)

---

*End of Use Cases — Next document: Implementation Plan (implementation_plan.md)*
