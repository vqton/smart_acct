# Payroll Module — Business Requirements Document (BRD)

**Version**: 1.0  
**Date**: 2026-06-30  
**Author**: BA Lead / Chief Accountant (20+ years)  
**Status**: Draft for Review  
**Regulatory Baseline**: TT 99/2025/TT-BTC, TT 133/2016/TT-BTC, PIT Law 109/2025/QH15, SI Law 41/2024/QH15, Employment Law 2025, Decree 293/2025/NĐ-CP, Decree 158/2025/NĐ-CP, Decree 161/2026/NĐ-CP, Resolution 110/2025/UBTVQH15

---

## 1. Executive Summary

### 1.1 Current Status
**No Payroll module exists** in SmartACCT. The cash module has a `SALARY` enum; the AP module references insurance payable (TK 338). Zero payroll-specific domain entities, DB tables, or routes.

### 1.2 Can Operate in PROD? **NO.**

| Check | Status | Reason |
|-------|--------|--------|
| Domain entities | ❌ Missing | 0/15 planned entities |
| DB tables | ❌ Missing | 0/12 planned tables |
| Repository layer | ❌ Missing | 0 CRUD methods |
| Use cases | ❌ Missing | 0/15 UC-PR methods |
| Routes | ❌ Missing | 0 endpoints |
| Tests | ❌ Missing | 0 tests |
| Regulatory compliance | ❌ Not applicable | No code to audit |

**Verdict**: Greenfield module. Must build from zero. Estimated 12-16 weeks for MVP.

### 1.3 Why Now
- TT 99/2025/TT-BTC effective 01/01/2026 — new chart of accounts (TK 334, 338, 3335), new forms
- PIT Law 109/2025/QH15 — 5-bracket system from tax year 2026, personal relief 15.5M, dependent 6.2M
- SI Law 41/2024/QH15 effective 01/07/2025 — expanded coverage, new contribution basis, 0.03%/day late interest
- Employment Law 2025 effective 01/01/2026 — national labor registration database
- Decree 293/2025/NĐ-CP — new regional minimum wages from 01/01/2026
- Base salary 2,530,000 VND/month from 01/07/2026 (Decree 161/2026/NĐ-CP)

---

## 2. Regulatory Framework (Applicable as of 30/06/2026)

### 2.1 Primary Laws

| Law | Reference | Effective | Scope |
|-----|-----------|-----------|-------|
| Labor Code | 45/2019/QH14 | 01/01/2021 | Employment contracts, wages, working hours |
| PIT Law (new) | 109/2025/QH15 | 01/07/2026 (± employment income from 2026 tax year) | Personal income tax on salaries |
| SI Law | 41/2024/QH15 | 01/07/2025 | Social insurance compulsory/voluntary |
| Health Insurance Law | 46/2014/QH13 (amended 2024) | Amended sections from 01/07/2025 | Health insurance |
| Employment Law | 2025 | 01/01/2026 | Unemployment insurance, labor database |
| Trade Union Law | 2012 | Current | Trade union fees (KPCĐ) |

### 2.2 Key Decrees

| Decree | Content | Effective |
|--------|---------|-----------|
| 293/2025/NĐ-CP | Regional minimum wage (Vùng 1: 5,310,000; Vùng 2: 4,730,000; Vùng 3: 4,140,000; Vùng 4: 3,700,000) | 01/01/2026 |
| 158/2025/NĐ-CP | SI compulsory: contribution basis, salary composition | 01/07/2025 |
| 161/2026/NĐ-CP | Base salary 2,530,000 VND/month | 01/07/2026 |
| 70/2025/NĐ-CP | Electronic PIT withholding certificates | 01/06/2025 |
| 134/2015/NĐ-CP | Voluntary SI (amended by SI Law 2024) | As amended |

### 2.3 Key Circulars

| Circular | Content | Effective |
|----------|---------|-----------|
| TT 99/2025/TT-BTC | New accounting regime (replaces TT 200/2014 for enterprises) | 01/01/2026 |
| TT 133/2016/TT-BTC | Accounting regime for SMEs (still valid alongside TT 99) | Current |
| TT 111/2013/TT-BTC | PIT guidance (to be replaced by new implementing circular for Law 109) | Current (until replaced) |
| TT 32/2025/TT-BTC | Tax management, e-invoices, PIT withholding certificates | 01/06/2025 |

### 2.4 Key Resolutions

| Resolution | Content | Effective |
|------------|---------|-----------|
| 110/2025/UBTVQH15 | PIT relief: personal 15.5M, dependent 6.2M | 01/01/2026 |

### 2.5 Social Insurance Contribution Rates (2026)

**Compulsory SI** (based on salary per Decree 158/2025/NĐ-CP):

| Fund | Employer | Employee | Total |
|------|----------|----------|-------|
| Retirement & Survivors (HT-TT) | 14% | 8% | 22% |
| Sickness & Maternity (OD-TS) | 3% | — | 3% |
| Occupational Accident & Disease (TNLĐ-BNN) | 0.5% | — | 0.5% |
| **Subtotal SI** | **17.5%** | **8%** | **25.5%** |
| Health Insurance (BHYT) | 3% | 1.5% | 4.5% |
| Unemployment Insurance (BHTN) | 1% | 1% | 2% |
| **Total** | **21.5%** | **10.5%** | **32%** |
| Trade Union Fee (KPCĐ) | 2% | — | 2% |

**Maximum contribution base**: 20× reference level (20 × 2,530,000 = 50,600,000 VND/month from 01/07/2026)  
**Late payment interest**: 0.03%/day on overdue amount  
**Payment deadline**: Last day of following month (monthly); last day of following month after cycle end (quarterly/6-month)

### 2.6 PIT Rates (From 2026 Tax Year, Law 109/2025/QH15)

**New 5-bracket progressive tax table** (replacing 7 brackets):

| Bracket | Monthly Taxable Income (VND) | Rate |
|---------|------------------------------|------|
| 1 | 0 – 10,000,000 | 5% |
| 2 | 10,000,001 – 30,000,000 | 10% |
| 3 | 30,000,001 – 60,000,000 | 20% |
| 4 | 60,000,001 – 100,000,000 | 30% |
| 5 | Over 100,000,000 | 35% |

**Relief** (Resolution 110/2025/UBTVQH15):
- Personal: 15,500,000 VND/month
- Dependent: 6,200,000 VND/month/dependent

**New exemptions**:
- Overtime/night shift pay (fully exempt)
- Income from innovation/tech activities
- Unused leave cash-out (fully exempt)

**New deductions**:
- Supplementary pension insurance contributions
- Life insurance premiums (within Gov't limits)
- Healthcare, education, training expenses (qualifying)

### 2.7 New PIT Brackets vs Old (Transition Reference)

| New Brackets 2026+ | Monthly Income | Rate | Old Brackets (pre-2026) | Old Rate |
|--------------------|----------------|------|------------------------|----------|
| 1 | 0–10M | 5% | 0–5M | 5% |
| 1 (cont.) | — | — | 5–10M | 10% |
| 2 | 10–30M | 10% | 10–18M | 15% |
| 3 | 30–60M | 20% | 18–32M | 20% |
| 4 | 60–100M | 30% | 32–52M | 25% |
| 5 | >100M | 35% | 52–80M | 30% |
| — | — | — | >80M | 35% |

---

## 3. Chart of Accounts Impact (TT 99/2025/TT-BTC + TT 133/2016)

### 3.1 Primary Payroll Accounts

| TK | Name | Type | Normal Balance | Notes |
|----|------|------|---------------|-------|
| 3341 | Payable to employees — salary | Liability | Credit | Main salary account |
| 3348 | Payable to employees — other | Liability | Credit | Bonuses, allowances not via salary |
| 3382 | Trade union fee (KPCĐ) | Liability | Credit | 2% employer contribution |
| 3383 | Social insurance payable | Liability | Credit | SI contributions (BHXH) |
| 3384 | Health insurance payable | Liability | Credit | HI contributions (BHYT) |
| 3385 | Unemployment insurance payable | Liability | Credit | UI contributions (BHTN) |
| 3386 | OCC insurance payable | Liability | Credit | TNLĐ-BNN |
| 3335 | PIT payable | Liability | Credit | Personal income tax withheld |

### 3.2 Salary Cost Allocation Accounts

| TK | Cost Center | Description |
|----|-------------|-------------|
| 622 | Direct labor | Production workers |
| 623 | Machine operators | Construction machinery operators |
| 627 | Production overhead | Factory management, QC, warehouse |
| 641 | Selling expenses | Sales staff, marketing |
| 642 | Admin expenses | Management, HR, accounting, office |
| 241 | Construction in progress | Capitalized labor costs |
| 154 | Work in progress | Indirect production labor |

### 3.3 GL Posting Matrix

| Transaction | Debit | Credit | Amount |
|-------------|-------|--------|--------|
| Accrue salary cost | 622/623/627/641/642/241 | 3341 | Gross salary |
| Employee SI portion | 3341 | 3383 | 8% |
| Employee HI portion | 3341 | 3384 | 1.5% |
| Employee UI portion | 3341 | 3385 | 1% |
| Employee total deduction | 3341 | — | 10.5% |
| Employer SI portion | 622/623/627/641/642 | 3383 | 17.5% |
| Employer HI portion | 622/623/627/641/642 | 3384 | 3% |
| Employer UI portion | 622/623/627/641/642 | 3385 | 1% |
| Employer OCC portion | 622/623/627/641/642 | 3386 | 0.5% |
| Employer KPCĐ | 622/623/627/641/642 | 3382 | 2% |
| Employer total charge | — | — | 24% |
| PIT withholding | 3341 | 3335 | Computed |
| Salary advance | 3341 | 111/112 | Advance amount |
| Net salary payment | 3341 | 111/112 | Net pay |
| SI/HI/UI payment | 3383/3384/3385/3386 | 112 | Total due |
| PIT payment | 3335 | 112 | Amount remitted |
| Bonus from welfare fund | 353 (Bonus Fund) | 3348 | Bonus amount |
| Bonus payment | 3348 | 111/112 | Paid |

---

## 4. Domain Entities (Planned)

### 4.1 Employee-Related

1. **Employee** — Master data: code, name, DOB, gender, ID/CCCD, tax code, SI book number, bank account, department, position, start date, contract type, region, dependent count
2. **EmployeeContract** — Contract history: type (indefinite/fixed-term/seasonal), start/end date, base salary, allowances, position
3. **EmployeeDependent** — Dependents for PIT relief: name, relationship, DOB, tax code, from/to date
4. **Timesheet** — Monthly attendance: employee, working days, overtime hours, leave days (sick/paid/unpaid), holidays

### 4.2 Payroll Calculation

5. **SalaryStructure** — Salary components: base salary, position allowance, seniority, meal allowance, phone, transport, housing, responsibility, other
6. **PayrollRun** — Monthly run: period (month/year), status (draft/computed/approved/paid/cancelled), total gross, total deductions, total net
7. **PayrollLine** — Per-employee calc: gross, SI base, employee SI/HI/UI deductions, employer SI/HI/UI/OCC/KPCĐ, PIT, advances, other deductions, net pay
8. **PayrollAdjustment** — One-off adjustments: bonus, penalty, retroactive increase, correction

### 4.3 Insurance & Tax

9. **SIInsuranceRecord** — Monthly SI declaration: salary base, employee/employer amounts, status (pending/submitted/confirmed)
10. **PITDeclaration** — Monthly/quarterly PIT: total income, exempt income, deductions, tax payable, status
11. **PITFinalization** — Annual PIT finalization: reconciliation of monthly withholding vs annual liability

### 4.4 Payment

12. **SalaryPayment** — Payment record: period, payment date, method (cash/bank transfer), total amount
13. **SalaryPaymentLine** — Per-employee payment: net amount, bank account, transaction reference

### 4.5 Reporting

14. **PayrollReport** — Generated reports: payroll summary by department, PIT report, SI report, cost allocation
15. **PayrollCostAllocation** — Breakdown of salary + employer contributions by cost account (622/627/641/642)

---

## 5. Processes & Workflows

### 5.1 Monthly Payroll Cycle

```
┌─────────────────────────────────────────────────────────────────────┐
│ MONTHLY PAYROLL CYCLE                                               │
├─────────────────────────────────────────────────────────────────────┤
│  Day 1-5:   Timesheet submission & approval                         │
│  Day 3-7:   Import attendance data, validate                       │
│  Day 5-10:  Compute payroll (gross → deductions → net)             │
│  Day 8-12:  Manager approval                                       │
│  Day 10-15: PIT declaration submission (monthly/quarterly)          │
│  Day 10-15: SI declaration submission (monthly)                    │
│  Day 15-20: Pay salary (bank transfer / cash)                      │
│  Day 20-25: Remit SI/HI/UI contributions to SI fund               │
│  Day 20-25: Remit PIT to tax authority                             │
│  Day 25-30: GL posting (salary cost + insurance accrual)           │
│  Day 30+:   Generate reports (payroll summary, cost alloc)         │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Payroll Calculation Flow

```
Employee Master Data
    ↓
Timesheet / Attendance Data
    ↓
Gross Salary Calculation:
  Base Salary × (Working Days / Standard Days)
  + Overtime Pay (150%/200%/300% per Labor Code)
  + Allowances (meal, phone, transport, housing, position, etc.)
  + Bonuses
  = Gross Salary (Tổng thu nhập)
    ↓
SI Base Salary Determination (per Decree 158/2025/NĐ-CP):
  Base salary + position allowance + regular supplements
  (Excludes: performance bonus, meal allowance, one-off payments)
  Clamped to: ≥ Regional Minimum Wage, ≤ 20× Reference Level
    ↓
Employee Deductions:
  - SI (8% × SI Base)
  - HI (1.5% × SI Base)
  - UI (1% × SI Base)
  - Advance repayments
  - Other deductions
    ↓
Taxable Income (Thu nhập tính thuế):
  Gross Income
  - Exempt Income (overtime, innovation, etc.)
  - SI/HI/UI Employee Portion
  - Personal Relief (15,500,000)
  - Dependent Relief (6,200,000 × N)
  - Supplementary Pension / Life Insurance
  - Charity Donations
  = Taxable Income
    ↓
PIT Calculation (5-bracket progressive):
  Bracket 1: 0-10M × 5%
  Bracket 2: 10-30M × 10%
  Bracket 3: 30-60M × 20%
  Bracket 4: 60-100M × 30%
  Bracket 5: >100M × 35%
    ↓
Net Pay (Thực lĩnh):
  Gross Salary
  - Employee SI/HI/UI (10.5%)
  - PIT
  - Advance repayments
  - Other deductions
  = Net Pay
    ↓
Employer Cost (Tính vào chi phí DN):
  + Gross Salary
  + Employer SI (17.5% × SI Base)
  + Employer HI (3% × SI Base)
  + Employer UI (1% × SI Base)
  + Employer OCC (0.5% × SI Base)
  + KPCĐ (2% × SI Base)
  = Total Employer Cost
```

### 5.3 PIT Withholding & Finalization Cycle

```
Monthly/Quarterly Withholding:
  Compute PIT per employee → Withhold from salary
  → Issue PIT withholding certificate (electronic per Decree 70/2025)
  → Declare via 05/KK-TNCN (monthly) or 05/QTT-TNCN (quarterly)
  → Pay by 20th of following month (monthly) or last day of following quarter (quarterly)

Annual Finalization:
  Aggregate 12-month income & deductions per employee
  → Reconcile monthly withholding vs actual annual liability
  → Prepare 05/QTT-TNCN + appendices 05-1/BK, 05-2/BK, 05-3/BK
  → Deadline: last day of 3rd month (employer) or 4th month (individual)
  → Refund overpayment / pay shortfall
```

### 5.4 SI Declaration & Payment Workflow

```
Per Employee:
  Determine SI base salary (per Decree 158/2025/NĐ-CP)
  → Calculate contributions (employer 21.5% + employee 10.5% = 32%)
  → Generate TK1-TS declaration
  → Submit via eBHXH / VssID / DVCQG portal
  → Pay by last day of following month
  → Receive C12-TS confirmation

Lifecycle Events Triggering Adjustment:
  New hire → Increase declaration (TK1-TS)
  Resignation → Decrease declaration (TK1-TS)
  Salary change → Adjustment declaration
  Maternity leave → Temporary suspension / BHXH benefit claim
  Sick leave >14 days → Temporary SI suspension
```

---

## 6. Use Cases Summary

| ID | Name | Priority | Complexity |
|----|------|----------|------------|
| UC-PR-01 | Employee Master Data Management | P0 | Medium |
| UC-PR-02 | Employee Contract Management | P0 | Medium |
| UC-PR-03 | Timesheet / Attendance Import | P0 | High |
| UC-PR-04 | Payroll Computation (Monthly) | P0 | Critical |
| UC-PR-05 | PIT Withholding & Declaration | P0 | Critical |
| UC-PR-06 | SI/HI/UI Contribution Calculation & Declaration | P0 | High |
| UC-PR-07 | Salary Payment (Bank Transfer/Cash) | P0 | Medium |
| UC-PR-08 | GL Posting (Payroll Cost Allocation) | P0 | High |
| UC-PR-09 | Payroll Reports & Dashboards | P1 | Medium |
| UC-PR-10 | Annual PIT Finalization | P1 | High |
| UC-PR-11 | Employee Self-Service (Payslip, Leave) | P1 | Medium |
| UC-PR-12 | Payroll Adjustment & Retroactive Changes | P1 | Medium |
| UC-PR-13 | Multi-Period Allocation (Accruals) | P2 | High |
| UC-PR-14 | Integration with HRMS/Timekeeping | P2 | Medium |
| UC-PR-15 | Compliance & Audit Trail | P1 | Medium |

---

## 7. Data Model (Conceptual)

### 7.1 Employee
```
Employee
├── id: int PK
├── employee_code: str (unique)
├── full_name: str
├── date_of_birth: date
├── gender: enum (male/female/other)
├── id_number: str (CCCD/CMND)
├── id_issue_date: date
├── id_issue_place: str
├── tax_code: str (MST)
├── si_book_number: str (Số sổ BHXH)
├── bank_account: str
├── bank_name: str
├── department_id: int FK → departments
├── position: str
├── region: enum (1/2/3/4)
├── dependent_count: int
├── status: enum (active/terminated/suspended)
├── start_date: date
├── termination_date: date (nullable)
├── created_at, updated_at
└── created_by, updated_by
```

### 7.2 PayrollRun
```
PayrollRun
├── id: int PK
├── period_month: int (1-12)
├── period_year: int
├── status: enum (draft/computed/approved/paid/cancelled)
├── total_gross: Decimal
├── total_employee_si: Decimal
├── total_employee_hi: Decimal
├── total_employee_ui: Decimal
├── total_pit: Decimal
├── total_advances: Decimal
├── total_other_deductions: Decimal
├── total_net: Decimal
├── total_employer_si: Decimal
├── total_employer_hi: Decimal
├── total_employer_ui: Decimal
├── total_employer_occ: Decimal
├── total_kpcd: Decimal
├── computed_at: datetime
├── approved_at: datetime
├── approved_by: str
├── paid_at: datetime
├── notes: text
├── created_at, updated_at
└── created_by
```

### 7.3 PayrollLine
```
PayrollLine
├── id: int PK
├── payroll_run_id: int FK → PayrollRun
├── employee_id: int FK → Employee
├── base_salary: Decimal
├── working_days: Decimal (actual days worked)
├── standard_days: Decimal (standard working days in month)
├── overtime_hours: Decimal
├── overtime_amount: Decimal
├── allowances: JSON (meal, phone, transport, housing, position, etc.)
├── bonus_amount: Decimal
├── gross_salary: Decimal
├── si_base_salary: Decimal
├── employee_si: Decimal (8% × si_base)
├── employee_hi: Decimal (1.5% × si_base)
├── employee_ui: Decimal (1% × si_base)
├── advance_deduction: Decimal
├── other_deductions: Decimal
├── taxable_income: Decimal
├── pit_amount: Decimal
├── net_pay: Decimal
├── employer_si: Decimal (17.5% × si_base)
├── employer_hi: Decimal (3% × si_base)
├── employer_ui: Decimal (1% × si_base)
├── employer_occ: Decimal (0.5% × si_base)
├── kpcd: Decimal (2% × si_base)
├── payment_method: enum (cash/bank)
├── payment_status: enum (pending/paid/failed)
├── payment_date: date (nullable)
├── bank_transaction_ref: str (nullable)
└── notes: text
```

### 7.4 PITDeclaration
```
PITDeclaration
├── id: int PK
├── declaration_type: enum (monthly/quarterly/annual)
├── period_month: int (nullable)
├── period_quarter: int (nullable)
├── period_year: int
├── submission_type: enum (initial/adjustment)
├── status: enum (draft/submitted/accepted/rejected)
├── total_income: Decimal
├── total_exempt_income: Decimal
├── total_deductions: Decimal
├── total_personal_relief: Decimal
├── total_dependent_relief: Decimal
├── total_taxable_income: Decimal
├── total_pit: Decimal
├── total_pit_withheld: Decimal
├── total_pit_paid: Decimal
├── submission_date: datetime
├── tax_authority_response: JSON
├── created_at, updated_at
└── created_by
```

### 7.5 SIInsuranceRecord
```
SIInsuranceRecord
├── id: int PK
├── payroll_run_id: int FK → PayrollRun
├── period_month: int
├── period_year: int
├── status: enum (pending/submitted/confirmed/adjusted)
├── total_si_base: Decimal (sum of all employee SI bases)
├── total_employee_si: Decimal
├── total_employee_hi: Decimal
├── total_employee_ui: Decimal
├── total_employer_si: Decimal
├── total_employer_hi: Decimal
├── total_employer_ui: Decimal
├── total_employer_occ: Decimal
├── total_kpcd: Decimal
├── total_payable: Decimal
├── submission_date: datetime
├── confirmation_ref: str (from BHXH system)
├── payment_date: date
├── created_at, updated_at
└── created_by
```

---

## 8. Key Validation Rules

### 8.1 Employee Rules
- Employee code must be unique
- Tax code must follow MST format (10 or 13 digits)
- SI book number must be unique if provided
- Dependent relief requires valid dependent tax code
- Cannot have two active contracts simultaneously

### 8.2 Payroll Computation Rules
- Gross salary ≥ Regional minimum wage (by region)
- SI base: must include base salary + position allowance + regular supplements; exclude performance bonus, meal allowance, one-off payments
- SI base: min = regional minimum wage; max = 20× reference level
- Employee total deduction cap: cannot exceed gross salary (net pay cannot be negative, except with employer approval)
- Overtime rate: 150% (weekday), 200% (weekend), 300% (holiday) per Labor Code
- PIT: use 5-bracket progressive table from 2026 tax year
- Must balance: gross = net + employee SI/HI/UI + PIT + advances + other deductions

### 8.3 Period Rules
- Cannot compute payroll twice for same period (must use adjustment run)
- Cannot pay payroll for closed GL period
- Must have valid accounting period open before posting GL entries
- SI declaration must be submitted before payment deadline (last day of following month)

### 8.4 PIT Rules (Law 109/2025)
- Personal relief: 15,500,000/month (applied once per individual, even with multiple jobs)
- Dependent relief: 6,200,000/month/dependent
- Overtime/night shift income: fully exempt
- Innovation/tech income: exempt (qualified activities)
- Annual finalization: reconcile monthly withholding vs annual liability
- Deadline: 31/03 (employer) / 30/04 (individual) of following year

---

## 9. Happy Path (Full Monthly Cycle)

**Scenario**: Standard monthly payroll for 50 employees.

1. **HR imports timesheet** → System validates attendance data (working days ≤ standard days, overtime hours reasonable)
2. **Payroll clerk initiates payroll run** → System locks previous runs for the period, creates draft PayrollRun
3. **System computes per employee**:
   - Gross salary from base × attendance + overtime + allowances + bonuses
   - SI base determination per Decree 158
   - Employee SI/HI/UI deductions
   - Taxable income = gross - exempt - SI/HI/UI - personal relief - dependent relief - other deductions
   - PIT per 5-bracket table
   - Net pay = gross - deductions - PIT
   - Employer costs (SI/HI/UI/OCC/KPCĐ)
4. **Manager reviews & approves** → Status changes to "approved"
5. **System auto-generates SI declaration** → Payroll clerk submits to eBHXH portal
6. **System auto-generates PIT declaration** → Payroll clerk submits via HTKK/iTax
7. **Salary payment** → Bank file export (or cash payment order) → Mark as paid
8. **System posts GL entries** → Debit cost accounts (622/627/641/642), Credit 3341/3382-3386/3335
9. **System generates payslips** → Employee self-service portal updated
10. **Month-end reports** → Payroll summary, cost allocation, SI/PIT reconciliation

---

## 10. Alternative Paths

### 10.1 Retroactive Salary Increase
- HR enters retroactive adjustment for month M-1
- System creates PayrollAdjustment with delta values
- Adjustment run computes additional pay + SI/PIT delta
- GL posts adjustment entry (debit cost account, credit 3341)
- Employee receives back-pay in current month payroll

### 10.2 New Hire Mid-Month
- Employee start date determines partial month calculation
- Prorate base salary: (Base × Working Days / Standard Days)
- Full SI base applies from start date
- PIT relief prorated: personal relief × (remaining days / 30)
- Dependent registration can be submitted within 30 days

### 10.3 Resignation / Termination
- Final payroll run for resigning employee
- Calculate final pay including accrued leave payout
- SI book handover process
- PIT finalization for the partial year
- Issue PIT withholding certificate for full year-to-date

### 10.4 Maternity Leave
- Employee on maternity leave: SI suspension
- Company may top-up salary difference (per policy)
- BHXH pays maternity benefits directly to employee
- System tracks return-to-work date and SI resumption

### 10.5 Sick Leave >14 Days
- Temporary SI suspension (both employer + employee portions)
- Doctor note validation
- Back payment required when employee returns (per Decree 158)
- Deadline: last day of month following suspension end

---

## 11. Exception Paths

### 11.1 Computation Error
- If SI base < regional minimum wage → flag error, require override
- If net pay < 0 → flag error, require manager approval
- If overtime hours > 100/month → flag for compliance review
- If PIT discrepancy > 1% between computed and expected → warn

### 11.2 Payment Failure
- Bank transfer rejected → retry logic (3 attempts)
- After 3 failures → mark as pending manual, notify payroll clerk
- Cash payment alternative for failed bank transfers

### 11.3 SI Submission Rejection
- eBHXH rejects declaration → parse error code, suggest fix
- Common causes: employee info mismatch, SI base out of range
- Re-submit after correction

### 11.4 PIT Finalization Discrepancy
- Annual finalization reveals over/under withholding
- Over-withholding → apply refund in next period or process refund
- Under-withholding → deduct from employee's next salary (within limit)
- Significant discrepancy → trigger compliance report

### 11.5 Regulatory Change Mid-Year
- PIT law change (e.g., new Law 109 effective mid-2026)
- System must support dual-regime processing for transition year
- Old brackets for Jan-Jun, new brackets for Jul-Dec
- Annual finalization uses blended calculation

---

## 12. Data Flows

### 12.1 External Integrations

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  HRMS /      │────▶│   SmartACCT      │────▶│  Bank Portal │
│  Timekeeping │     │   Payroll Module │     │  (Salary     │
│  System      │     │                  │     │   Transfer)  │
└──────────────┘     │                  │     └──────────────┘
                     │                  │     ┌──────────────┐
┌──────────────┐     │                  │────▶│  eBHXH       │
│  Employee    │◀───▶│                  │     │  (SI Portal) │
│  Self-Service│     │                  │     └──────────────┘
│  Portal      │     │                  │     ┌──────────────┐
└──────────────┘     │                  │────▶│  iTax/HTKK   │
                     │                  │     │  (PIT Portal)│
                     │                  │     └──────────────┘
                     └──────────────────┘
```

### 12.2 GL Integration
```
Payroll Module → GL Module:
  For each PayrollLine, generate:
    Journal Entry "PR-{period}-{run_id}":
      Debit  622/623/627/641/642/241 = Gross + Employer contributions
      Credit 3341 = Gross salary
      Credit 3383 = Total SI (employee + employer)
      Credit 3384 = Total HI (employee + employer)
      Credit 3385 = Total UI (employee + employer)
      Credit 3386 = Employer OCC
      Credit 3382 = KPCĐ (employer)
      Credit 3335 = PIT withheld

  Payment Journal Entry "PMT-{period}-{run_id}":
      Debit  3341 = Net pay
      Credit 1121 = Bank transfer amount
```

### 12.3 Cash Integration
```
Payroll Module → Cash Module:
  Salary payment → CashReceipt (negative) or CashPayment record
  SI payment → CashPayment to SI fund
  PIT payment → CashPayment to tax authority
```

---

## 13. User Journeys

### 13.1 Payroll Clerk (Monthly)
1. Login → Dashboard shows pending payroll tasks
2. Click "Import Timesheet" → Upload Excel/CSV → Validate → Confirm
3. Click "Run Payroll" → System computes → Review summary
4. Click "View Detail" → Check per-employee breakdown
5. Click "Generate SI Declaration" → Export XML → Submit to eBHXH
6. Click "Generate PIT Declaration" → Export XML → Submit via HTKK
7. Click "Pay Salary" → Select payment method → Confirm
8. Click "Post to GL" → Review GL entries → Confirm posting
9. Click "Generate Reports" → Select report type → Export PDF/Excel

### 13.2 Employee
1. Login to self-service portal → View payslip for current/previous months
2. View PIT withholding history
3. View SI contribution history
4. Download PIT withholding certificate
5. Submit time-off request (integrated with timesheet)

### 13.3 Chief Accountant
1. Review monthly payroll summary vs budget
2. Approve or reject payroll run
3. Review GL posting entries
4. Sign SI and PIT declarations
5. Annual PIT finalization review and sign-off

---

## 14. Regulatory Timeline & Implementation Priorities

### 14.1 Critical Dates
| Date | Event | Impact |
|------|-------|--------|
| 01/07/2025 | SI Law 41/2024 effective | SI base determination rules |
| 01/01/2026 | TT 99/2025 effective | New chart of accounts |
| 01/01/2026 | Employment Law 2025 effective | UI rules, labor database |
| 01/01/2026 | Decree 293/2025 effective | New regional minimum wages |
| 01/01/2026 | Resolution 110/2025 effective | New PIT relief amounts |
| 01/01/2026 | PIT Law 109 (employment income) | 5-bracket table for 2026 tax year |
| 01/07/2026 | PIT Law 109 (full effective) | Full law implementation |
| 01/07/2026 | Base salary 2,530,000 (Decree 161) | SI max base updated |

### 14.2 Implementation Phasing
```
Phase 1 (Weeks 1-4): Foundation
  - Employee master data (UC-PR-01)
  - Employee contracts (UC-PR-02)
  - Domain entities & DB schema
  - Repository layer

Phase 2 (Weeks 5-8): Core Payroll
  - Timesheet import (UC-PR-03)
  - Payroll computation engine (UC-PR-04)
  - PIT engine with 5-bracket table (UC-PR-05)
  - SI contribution engine (UC-PR-06)

Phase 3 (Weeks 9-12): Payment & GL
  - Salary payment (UC-PR-07)
  - GL posting (UC-PR-08)
  - Reports (UC-PR-09)
  - Audit trail (UC-PR-15)

Phase 4 (Weeks 13-16): Advanced
  - Annual PIT finalization (UC-PR-10)
  - Employee self-service (UC-PR-11)
  - Adjustments (UC-PR-12)
  - Multi-period accruals (UC-PR-13)
```

---

## 15. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PIT Law 109 implementing decree delayed | Medium | High | Build flexible engine supporting both old/new brackets; config-driven rates |
| SI contribution rate change mid-development | Low | Medium | Store rates in DB not code; admin-configurable |
| Employee data migration from Excel | High | Medium | Provide import templates with validation |
| Integration with eBHXH API unavailable | Medium | High | Generate export files for manual upload; async API integration |
| Payroll calculation errors | Medium | Critical | Comprehensive unit tests; parallel run vs Excel comparison tool |
| Dual-regime transition (2026-2027) | High | High | Support dual bracket tables; configurable effective dates |

---

## 16. Appendix: Key Vietnamese Terminology

| Vietnamese | English | Context |
|------------|---------|---------|
| Tiền lương | Salary/Wages | Gross pay |
| Lương cơ bản | Base salary | Contractual base |
| Lương đóng BHXH | SI contribution salary | Base for insurance calc |
| Phụ cấp | Allowance | Position, meal, phone, etc. |
| Bảo hiểm xã hội (BHXH) | Social Insurance | SI |
| Bảo hiểm y tế (BHYT) | Health Insurance | HI |
| Bảo hiểm thất nghiệp (BHTN) | Unemployment Insurance | UI |
| Kinh phí công đoàn (KPCĐ) | Trade Union Fee | 2% employer |
| Thuế TNCN | Personal Income Tax | PIT |
| Giảm trừ gia cảnh | Family relief | Personal + dependent deduction |
| Người phụ thuộc | Dependent | For PIT relief |
| Quyết toán thuế TNCN | PIT finalization | Annual tax settlement |
| Tạm ứng lương | Salary advance | Pre-payment |
| Thực lĩnh | Net pay | Take-home pay |
| Bảng chấm công | Timesheet | Attendance record |
| Hợp đồng lao động | Labor contract | Employment agreement |
| Thang bảng lương | Salary scale | Company pay structure |
| Tờ khai thuế | Tax declaration | PIT form |
| Hóa đơn điện tử | E-invoice | Electronic invoice |
| Chứng từ khấu trừ thuế | Tax withholding certificate | PIT certificate |

---

## 17. References

### Laws & Regulations
- PIT Law 109/2025/QH15 (effective 01/07/2026)
- SI Law 41/2024/QH15 (effective 01/07/2025)
- Employment Law 2025 (effective 01/01/2026)
- Labor Code 45/2019/QH14
- Decree 293/2025/NĐ-CP — Regional minimum wage 2026
- Decree 158/2025/NĐ-CP — SI compulsory guidance
- Decree 161/2026/NĐ-CP — Base salary 2,530,000
- Decree 70/2025/NĐ-CP — E-withholding certificate
- Resolution 110/2025/UBTVQH15 — PIT relief amounts
- TT 99/2025/TT-BTC — New accounting regime
- TT 133/2016/TT-BTC — SME accounting regime
- TT 111/2013/TT-BTC — PIT guidance (current)
- TT 32/2025/TT-BTC — Tax management, e-invoices

### Websites Referenced
- ketoanthienung.net — Payroll calculation practice
- ketoanleanh.edu.vn — Salary, BHXH, TNCN education
- webketoan.com — Accounting community forums
- vbpl.vn — Legal document database
- mof.gov.vn — Ministry of Finance Q&A
- thuedientu.gdt.gov.vn — e-Tax portal
- baohiemxahoi.gov.vn — Social Insurance portal
- dichvucong.gov.vn — National public service portal
- ey.com — EY Vietnam tax alerts
- pwc.com/vn — PwC Vietnam tax summaries
- deloitte.com/vn — Deloitte Vietnam insights
- kpmg.com/vn — KPMG Vietnam tax alerts
- gdt.gov.vn — General Department of Taxation
- ifrs.org — IFRS standards

---

*End of BRD — Next document: Use Cases (use_cases.md)*
