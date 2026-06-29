# BRD: Accounts Receivable (AR) Module
## SmartACCT ERP — Vietnamese Accounting System

**Version:** 1.0  
**Date:** 2026-06-29  
**Author:** BA Lead (20+ yrs) + Chief Accountant (20k hrs)  
**Status:** DRAFT — Pending implementation  

---

## 1. Executive Summary

### 1.1 Purpose
Build the Accounts Receivable (AR) module for SmartACCT ERP to manage customer billing, invoice lifecycle, payment collection, aging analysis, dunning workflows, and bad debt provisions per Vietnamese Accounting Standards (VAS) and regulatory requirements.

### 1.2 Current State Assessment
**VERDICT: NOT PRODUCTION-READY.**

The Tax module has `EInvoice` entity, but it is NOT a full AR system:
- No Customer Master Data (buyer_name is just a string field, no FK)
- No AR aging buckets, no Dunning Engine
- No Payment Allocation logic
- No TK 630 Bad Debt Provision per Circular 200/2014
- No AR-to-GL journal posting (Dr 131 / Cr 511 / Cr 3331)
- No IFRS 9 ECL calculation
- Zero AR-specific API routes
- Zero AR test coverage

**PROD Readiness Score: 2.0/5**

### 1.3 Scope
In scope:
- Customer Master Data (create/read/update/search customers with tax code validation)
- AR Invoice lifecycle (create, send, partial pay, fully pay, overdue, write-off)
- Aging report engine (6 IFRS-standard buckets + 3 VAS buckets for provisions)
- Dunning workflow (5 escalation levels with automated notifications)
- Payment allocation (full/partial/overpayment handling)
- TK 630 Bad Debt Provision per Circular 200/2014
- GL auto-posting per TT99/2025 (TK 131, TK 511, TK 333, TK 630, TK 111/112)
- E-invoice auto-submission to GDT (NĐ70/2025 compliance)
- i18n support (vi/en error codes + Jinja2 templates)
- IFRS 9 ECL calculation (3-stage model for enterprises transitioning to IFRS)

Out of scope (v2.0+):
- Advanced credit scoring (external bureau integration)
- Multi-currency AR with automatic hedge accounting
- Customer self-service portal
- Automated legal escalation (only notification stubs)
- ePayment gateway integration
- AR factoring / securitization

---

## 2. Regulatory & Compliance Framework

### 2.1 Primary Legislation

| Citation | Title | AR Impact | Status |
|----------|-------|-----------|--------|
| **NĐ70/2025/NĐ-CP** | E-Invoice Decree | Mandatory e-invoice for ALL enterprises from 01/01/2026; account blocking for non-compliance | Must auto-submit to GDT |
| **TT99/2025/TT-BTC** | Accounting Regime (replaces TT133/2016) | AR posting (TK 131), revenue at invoice date, VAT accrued at invoice, not cash | Core posting logic |
| **Circular 200/2014/TT-BTC** | Bad Debt Provisions + Write-offs | 3-bucket provision rates (5%, 20-50%, 50-100%), write-off conditions (legal/bankruptcy/3yr) | TK 630 logic |
| **TT 111/2013/TT-BTC** | PIT Withholding | Overdue personal debt interest subject to 5-35% PIT withholding | Edge case implementation |
| **TT 78/2021/TT-BTC** | Tax treatment of provisions vs write-offs | Provisions not CIT-deductible; only actual write-offs are deductible | Tax reporting |
| **Law on Tax Admin 108/2025/QH15** | Digitale obligation + data mining | GDT can cross-reference AR vs buyer tax-codes; overstatement = red flag | Compliance |
| **Decree 245/2026/NĐ-CP** | Deadline extensions June 2026 | VAT/CIT/PIT extensions in 2026 | Calendar impact |
| **Civil Code 2015** | Legal basis for debt collection | Only enforceable ground for write-off + legal action | Audit trail |

### 2.2 Chart of Accounts (TK) Mapping for AR

| TK Code | Vietnamese Name | DCR | AR Role |
|---------|-----------------|-----|---------|
| **TK 131** | Phải thu khách hàng | Debit | Main AR — amounts owed by customers |
| **TK 1311** | Phải thu ngắn hạn khách hàng | Debit | Short-term AR ≤ 12 months |
| **TK 1312** | Phải thu dài hạn khách hàng | Debit | Long-term AR > 12 months |
| **TK 1313** | Phải thu về bán TSCĐ | Debit | AR from sale of fixed assets |
| **TK 1314** | Phải thu về bán TSCĐ vô hình | Debit | AR from sale of intangible assets |
| **TK 331** | Phải trả người bán | Credit | AP cross-reference for matching |
| **TK 511** | Doanh thu bán hàng | Credit | Revenue recognition at invoice date |
| **TK 3331** | Thuế GTGT đầu ra | Credit | Output VAT on sales |
| **TK 111** / **TK 112** | Tiền mặt / Tiền gửi NH | Debit | Payment clearing |
| **TK 630** | Dự phòng nợ xấu | Credit | Bad debt provision (contra-asset) |
| **TK 631** | Chi phí khác | Debit | Bad debt recovery income |

### 2.3 E-Invoice (NĐ70/2025) Requirements

| Requirement | Detail | SmartACCT Gap |
|-------------|--------|---------------|
| Mandatory for ALL enterprises from 01/01/2026 | No paper invoices | EInvoice entity exists; not wired into AR |
| Content requirements | Invoice number, series, date, seller/buyer tax code (10-13 digits), name, address, product lines, subtotal, discount, VAT, grand total | EInvoice covers this |
| Cross-period adjustments | Thông tư 78 regulates adjustments across periods | EInvoice has adjustment types |
| POS threshold | HKD with annual revenue ≥ 1bn VND must use POS-integrated e-invoice | Not in scope |
| Account blocking (NĐ70) | Tax authority can freeze taxpayer accounts for non-compliance | Monitoring not impl |
| VAT registration | New threshold: 1bn VND/year (raised from 500m) per Luật Thuế GTGT 48/2024 | Validation needed |

---

## 3. User Roles & Responsibilities

| Role | Vietnamese Title | AR Responsibilities |
|------|------------------|---------------------|
| **Sales Accountant** | Kế toán bán hàng | Create customers, issue AR invoices, submit e-invoices, daily collection calls |
| **Collections Officer** | Kế toán thu hồi công nợ | Run aging reports, execute dunning workflow, log collection attempts, escalate |
| **CFO/Controller** | Kế toán trưởng | Approve provisions (TK 630), approve write-offs, review KPIs, sign BCTC disclosures |
| **Finance Director** | Giám đốc tài chính |战略 credit policy, approve major provisions, regulator liaison |
| **System Administrator** | Quản trị hệ thống | Customer master data maintenance, credit limit configuration, dunning templates |

---

## 4. System Actors (External)

| Actor | Role in AR |
|-------|-----------|
| **Customer** | Receives e-invoice, makes payments, receives dunning notices |
| **GDT (Tổng cục Thuế)** | Receives e-invoices via thuedientu.gdt.gov.vn API; returns verification_code + signed_file_url |
| **Signing Service** | RSA-SHA256 signs e-invoice before GDT submission |
| **Bank** | Payment settlement via TK 111/112 |
| **Legal Authority** | Debt collection enforcement (when dunning exhausted) |

---

## 5. Key Performance Indicators (KPIs)

| KPI | Formula | Frequency | Owner |
|-----|---------|-----------|-------|
| **DSO** (Days Sales Outstanding) | (Average AR ÷ Total Credit Sales) × 365 | Monthly | CFO |
| **CEI** (Collection Effectiveness Index) | (Beg AR + Sales - End AR - Bad Debt) / (Beg AR + Sales) × 100 | Monthly | CFO |
| **Aging %** | Balance in each bucket / Total AR | Monthly | Controller |
| **Bad Debt Ratio** | Bad Debt Write-offs / Total Revenue | Quarterly | CFO |
| **Overdue Rate** | Overdue AR / Total AR | Weekly | Collections |
| **GDT Rejection Rate** | Rejected e-invoices / Total submitted | Real-time | Sales Acct |
| **Payment On-Time Rate** | Paid within terms / Total invoices | Monthly | Sales Acct |
| **Write-off Recovery Rate** | Recovered write-offs / Total written off | Annual | CFO |

---

## 6. Happy Path: End-to-End AR Transaction

### Step 1: Customer Creation
```
Actor: Sales Accountant
Action: POST /ar/customers
Request: { customer_code: "CUST-001", tax_code: "0123456789", name: "ABC Corp", address: "...", credit_limit: 500000000, payment_terms_days: 30 }
Response: 201 { customer_id: 1, customer_code: "CUST-001", ... }
System Action: Validate tax_code format (10-13 digits, Mã số thuế rules). Check for duplicate customer_code.
```

### Step 2: Create AR Invoice
```
Actor: Sales Accountant
Action: POST /ar/invoices
Request: { customer_id: 1, items: [{ description: "Product A", qty: 10, unit_price: 10000000 }], payment_terms: "NET30" }
System Checks:
  1. Customer exists → validate tax code completeness
  2. Period is OPEN (AccountingPeriod check)
  3. Outstanding AR + new invoice ≤ credit_limit
  4. Auto-calculate due_date = invoice_date + payment_terms_days
System Actions:
  1. Create ARInvoice (status=DRAFT)
  2. Create ARInvoiceLines
  3. Auto-generate EInvoice (for GDT)
  4. Post GL entry: Dr TK131 / Cr TK511 / Cr TK3331
  5. Submit to GDT via GDTClient.submit_invoice() (retry 3×)
  6. Update status → SENT, store verification_code
Response: 201 { ar_invoice_id: 1, status: "sent", verification_code: "xxx", due_date: "2026-01-30" }
```

### Step 3: Pre-Dunning (Auto)
```
Trigger: 7 days before due_date
System Action:
  - Send email reminder (friendly)
  - Log ARDunningLog (level=0, method="email_pre_due")
  - If email bounces → flag customer record
```

### Step 4: Receive Payment
```
Actor: Collections Officer
Action: POST /ar/payments
Request: { customer_id: 1, amount_received: 50000000, payment_method: "transfer", reference_number: "TXN-123" }
System Actions:
  1. Create ARPayment (status=applied)
  2. Auto-allocate to oldest outstanding invoices (FIFO)
  3. For each allocation: update ARInvoice.balance_due, status (PARTIALLY_PAID or PAID)
  4. Post GL: Dr TK111 / Cr TK131 (net of VAT portion)
  5. If overpayment: ARPayment.amount_unapplied > 0, issue refund notice
Response: 201 { ar_payment_id: 1, allocations: [...], amount_unapplied: 0 }
```

### Step 5: Dunning Escalation (Triggered Daily)
```
Trigger: days_past_due > 0 (cron/scheduler)
System Action:
  - Compute aging_bucket for each overdue invoice
  - Auto-advance dunning_level if next_due_date passed
  - D1 (1-7 days): Email reminder → ARDunningLog L1
  - D2 (8-30 days): SMS + follow-up call → ARDunningLog L2
  - D3 (31-60 days): Formal letter + internal escalation → ARDunningLog L3
  - D4 (61-90 days): Legal notice → ARDunningLog L4
  - D5 (>90 days): External collector engagement → ARDunningLog L5
  - If > 6 months overdue: auto-calculate TK 630 provision, request CFO approval
Response: Background job — no HTTP response to actor
```

### Step 6: Monthly Aging Snapshot
```
Trigger: APScheduler job — 1st of month at 00:00
System Actions:
  1. Lock previous period (AccountingPeriod must be CLOSED before snapshot)
  2. Compute balances per customer per aging bucket
  3. Write ARAgingSnapshot rows
  4. Compute DSO, CEI, Bad Debt Ratio
  5. Send KPI email to CFO
Response: Background job — stored in DB + emailed report
```

### Step 7: Bad Debt Write-Off (Year-End)
```
Actor: CFO
Action: POST /ar/bad-debt/write-off { ar_invoice_id: 123, reason: "Customer bankrupt", approval_by: "CFO Nguyen" }
System Checks:
  1. Invoice is > 6 months overdue (Circular 200/2014 minimum)
  2. All collection levels exhausted (D1-D5 completed)
  3. CFO approval flag present
System Actions:
  1. Create BadDebtProvision (if not already provisioned)
  2. Update ARInvoice.status → WRITTEN_OFF
  3. Post GL: Dr TK630 / Cr TK131 (full balance)
  4. Log audit event
Response: 201 { provision_id: 1, journal_entry_id: 456, status: "written_off" }
```

---

## 7. Alternative / Error Paths

| # | Scenario | System Behavior | Error Code |
|---|----------|-----------------|------------|
| ALT-AR-01 | Customer tax_code format invalid | REJECT 400; return specific validation error (10-13 digits, no leading zeros) | CUSTOMER_TAX_CODE_INVALID |
| ALT-AR-02 | Duplicate customer_code | REJECT 409 conflict | CUSTOMER_CODE_DUPLICATE |
| ALT-AR-03 | Credit limit exceeded | REJECT 422; return current utilization + new total + limit | CREDIT_LIMIT_EXCEEDED |
| ALT-AR-04 | GL Period is CLOSED | REJECT 403; cannot create AR in closed period (same gating as GL) | PERIOD_CLOSED |
| ALT-AR-05 | Aging snapshot period already closed | CONFLICT 409; snapshot tied to locked period | PERIOD_ALREADY_CLOSED |
| ALT-AR-06 | GDT rejects e-invoice | status → ERROR; retry 3× with backoff; notify Sales Accountant; manual correction required | GDT_SUBMISSION_FAILED |
| ALT-AR-07 | Payment amount > invoice balance | OVERPAYMENT: ARPayment.amount_unapplied > 0; issue refund notice | OVERPAYMENT_DETECTED |
| ALT-AR-08 | Partial payment allocates to wrong invoice | REJECT 400; require explicit invoice_id in allocation body | ALLOCATION_INVALID |
| ALT-AR-09 | Write-off < 6 months overdue | REJECT 422; must exhaust dunning + wait 6 months | WRITE_OFF_PERIOD_NOT_MET |
| ALT-AR-10 | Bad debt provision reversed | If subsequently collected: Dr 131 + Cr 631 (NOT Cr 630) | BAD_DEBT_RECOVERED |
| ALT-AR-11 | Customer deleted with open AR | BLOCK 409; must settle or write off all open invoices before deactivation | CUSTOMER_HAS_OPEN_AR |
| ALT-AR-12 | Duplicate GDT verification | EInvoice.status already SENT; idempotent return | EINVOICE_ALREADY_SUBMITTED |

---

## 8. Data Model (ER Overview)

```
Customer (1) ──< (N) ARInvoice ──< (N) ARInvoiceLine
                        │
                        ├── FK: einvoice_id → EInvoice (Tax domain)
                        ├── FK: gl_entry_id → JournalEntry (GL domain)
                        │
                        └──< (N) ARPaymentAllocation ──> ARPayment
                                        │
                                        └── FK: ar_invoice_id back to ARInvoice

ARDunningLog (many) linked to ARInvoice (1): dunning_level, date, method, notes

BadDebtProvision: linked to Customer (nullable) + ARInvoice (nullable) + Period

AR AgingSnapshot: per Customer + Period + 6 aging buckets + totals
```

### Key Constraints
- UNIQUE(Customer.tax_code) — Mã số thuế must be unique per legal entity
- UNIQUE(ARInvoice.invoice_number, customer_id) — per customer, invoice number must be unique
- CHECK(ARInvoice.days_past_due >= 0) — computed field, never negative
- CHECK(ARPayment.amount_received >= 0) — cannot create negative payment
- FK: ARInvoice.customer_id → Customer.customer_id ON DELETE RESTRICT (cannot delete customer with open AR)

---

## 9. API Endpoints

### AR Routes (presentation/ar/)

| Method | Path | Description |
|--------|------|-------------|
| **CUSTOMERS** |
| POST | /ar/customers | Create customer (validate tax_code) |
| GET | /ar/customers | List/search (q, tax_code, is_active) |
| GET | /ar/customers/{id} | Get customer detail |
| PUT | /ar/customers/{id} | Update customer (credit_limit, terms) |
| DELETE | /ar/customers/{id} | Deactivate (blocked if open AR) |
| **AR INVOICES** |
| POST | /ar/invoices | Create AR invoice → auto-GL post → auto-GDT submit |
| GET | /ar/invoices | List (filter: customer_id, status, from_date, to_date, overdue) |
| GET | /ar/invoices/{id} | Get AR invoice detail |
| PUT | /ar/invoices/{id} | Update (limited fields before SENT) |
| POST | /ar/invoices/{id}/send | Transition DRAFT→SENT + GDT submit |
| POST | /ar/invoices/{id}/void | Cancel DRAFT invoice |
| **PAYMENTS** |
| POST | /ar/payments | Record payment + auto-allocate to invoices |
| GET | /ar/payments | List (filter: customer_id, date range) |
| GET | /ar/payments/{id} | Get payment detail |
| POST | /ar/payments/{id}/reverse | Reverse payment (before period close) |
| **AGING** |
| GET | /ar/aging | Live aging report (computed, not snapshot) |
| POST | /ar/aging/snapshot | Generate period-locked snapshot (requires CLOSED period) |
| GET | /ar/aging/snapshots | List historical snapshots |
| GET | /ar/aging/snapshots/{id} | Get specific snapshot |
| **DUNNING** |
| POST | /ar/invoices/{id}/dunning | Advance dunning level (manual or trigger) |
| GET | /ar/dunning | List overdue invoices with dunning status |
| GET | /ar/dunning/queue | Collection queue (sorted by days_past_due DESC) |
| **BAD DEBT** |
| POST | /ar/bad-debt/provisions | Create/adjust provision for invoice |
| GET | /ar/bad-debt/provisions | List provisions (filter: period, customer) |
| POST | /ar/bad-debt/write-off | Approve + write-off (CFO only) |
| GET | /ar/bad-debt/recoveries | List recovered bad debts |
| **REPORTS** |
| GET | /ar/reports/balance | Customer AR balance summary |
| GET | /ar/reports/collection-effectiveness | CEI + DSO per customer |
| GET | /ar/reports/statement | Customer AR statement (aged) |

---

## 10. Business Rules

### BR-AR-01: Customer Tax Code Validation
- Must be strictly 10–13 digits (no hyphens, no spaces after cleaning)
- First digit determines entity type (1-9 per Circular 55/2021/TT-BTC)
- Cannot create duplicate tax_code across Customer table
- Cannot update tax_code after creation (regulatory identity)

### BR-AR-02: Credit Limit Enforcement
- Before invoice creation: check `customer.outstanding_balance + new_invoice_total <= customer.credit_limit`
- At 80% utilization: auto-warn (log + return warning in response headers)
- At 100%: reject invoice with HTTP 422 + AR-level error
- CFO can temporarily override credit limit via PUT /ar/customers/{id} with `override_reason`

### BR-AR-03: Aging Buckets (IFRS + Management)
| Bucket ID | Name | Days Past Due | Provision Rate (VAS) |
|-----------|------|---------------|----------------------|
| 0 | Current | 0 | 0% |
| 1 | 1-30 days | 1–30 | 0% |
| 2 | 31-60 days | 31–60 | 0% |
| 3 | 61-90 days | 61–90 | 0% (provision trigger > 6mo) |
| 4 | 91-180 days | 91–180 | 5% |
| 5 | 181-365 days | 181–365 | 20–50% |
| 6 | 365+ days | > 365 | 50–100% |

**Note**: provisions applied at year-end close, not transaction-by-transaction.

### BR-AR-04: Dunning Escalation Rules
| Level | Timing | Method | Actor |
|-------|--------|--------|-------|
| L0 | 7 days before due | Automated email | System |
| L1 | 1–7 days overdue | Email reminder | System |
| L2 | 8–30 days overdue | SMS + phone call | Collections Officer |
| L3 | 31–60 days overdue | Formal demand letter | Collections + Legal |
| L4 | 61–90 days overdue | Legal notice | Legal |
| L5 | > 90 days | External collector engagement | CFO approval required |

### BR-AR-05: Payment Allocation (FIFO)
- Default: allocate to oldest invoice first (FIFO)
- Customer can specify invoice allocation in request body
- Partial payment: update invoice status to PARTIALLY_PAID, recalc balance_due
- Overpayment → ARPayment.amount_unapplied (refund flow TBD v2.0)

### BR-AR-06: GL Posting Rules
| Transaction | Dr Account | Cr Account | Notes |
|-------------|-----------|-----------|-------|
| Create AR Invoice | TK 131 | TK 511 | Revenue at invoice date |
| | (VAT portion) | TK 3331 | Output VAT accrual |
| Receive Full Payment | TK 111/112 | TK 131 | Cash clearing |
| Receive Partial Payment | TK 111/112 | TK 131 | Proportional clearing |
| Bad Debt Provision | TK 632 | TK 630 | Provision expense |
| Write-off | TK 630 | TK 131 | Actual write-off (NOT Cr 631) |
| Write-off Reversal | TK 131 | TK 631 | If subsequently collected |

### BR-AR-07: E-Invoice Auto-Submission
- On `ARInvoice.status → SENT`, auto-trigger GDT submission
- Sign invoice via RSA-SHA256 signing service BEFORE submission
- Retry: 3 attempts with exponential backoff (1s, 5s, 30s)
- Fail: mark status → ERROR; notify Sales Accountant; block further changes

### BR-AR-08: Period Gating
- Cannot create AR Invoice in CLOSED AccountingPeriod (same gate as GL entries)
- Cannot record payment in CLOSED period (same gate)
- Cannot run aging snapshot in OPEN period (must wait for period close)
- Payment reversal: only allowed in same period as original payment

### BR-AR-09: Provision Calculation (Circular 200/2014)
- Run at year-end (Dec 31) or when CFO triggers
- Apply provision rates by aging bucket:
  - 91-180 days: 5%
  - 181-365 days: 20%
  - 365+ days: 50%
- Maximum: 100% of outstanding balance for > 3 years overdue
- Provisions are estimates only; actual write-offs when uncollectible confirmed

### BR-AR-10: IFRS 9 ECL Stages (for IFRS adopters)
| Stage | Trigger | Measurement | Disclose |
|-------|---------|-------------|----------|
| 1 | No significant credit risk increase | 12-month ECL | Only |
| 2 | Significant credit risk increase | Lifetime ECL | Aging + risk factors |
| 3 | Credit-impaired (default > 90 days) | Lifetime ECL, interest on net | Full IFRS 7 disclosure |

---

## 11. Workflows

### WF-AR-01: Invoice Creation → GDT Submission
```
1. Sales Acct → POST /ar/invoices (DRAFT)
2. System → validate customer, credit limit, period
3. System → create ARInvoice + ARInvoiceLines
4. System → auto-generate EInvoice (seller/buyer fields from Customer)
5. System → sign via RSA-SHA256 signing service
6. System → submit to GDT (GDTClient.submit_invoice) — 3 retries
7. System → post GL: Dr 131 / Cr 511 / Cr 3331
8. System → update ARInvoice.status = SENT, store verification_code
9. System → return 201 to Sales Acct
```

### WF-AR-02: Payment Receipt + Allocation
```
1. Collections → POST /ar/payments {customer_id, amount, method, reference}
2. System → create ARPayment
3. System → auto-allocate FIFO to oldest open ARInvoice(s)
4. For each allocation:
   a. Update ARInvoice.balance_due, status (PARTIALLY_PAID or PAID)
   b. Post GL: Dr 111/112 / Cr 131 (per invoice)
5. If overpayment: ARPayment.amount_unapplied > 0 → issue refund notice
6. System → log collection event in ARDunningLog
```

### WF-AR-03: Daily Dunning Cron Job
```
1. APScheduler → daily at 08:00
2. Query: ARInvoice where status in (SENT, PARTIALLY_PAID) AND due_date < today AND dunning_level < 5
3. For each:
   a. Compute days_past_due, aging_bucket
   b. Advance dunning_level per schedule
   c. Execute notification (email/SMS/letter stub)
   d. Log ARDunningLog entry
   e. If days_past_due > 180 AND no provision: create BadDebtProvision draft
4. Alert CFO if any invoice enters D5 (> 90 days)
```

### WF-AR-04: Month-End Aging Snapshot
```
1. GL Period CLOSE triggers → set needs_reconciliation = true
2. CFO reviews + approves period close
3. APScheduler → 1st of month at 00:01 (after period close)
4. Query: all open ARInvoice per customer, compute bucket balances
5. Write ARAgingSnapshot per customer (locked)
6. Compute KPIs: DSO, CEI, Bad Debt Ratio
7. Send PDF report to CFO + Controller
8. Set snapshot.period = CLOSED (cannot modify)
```

### WF-AR-05: Bad Debt Write-Off Approval
```
1. Collections → trigger write-off request for invoice
2. System → validate: overdue > 6 months, dunning_level == 5, no provision exists
3. System → PUT /ar/bad-debt/write-off (requires CFO approval token)
4. CFO approves → provide `approval_by`, `approval_reason`
5. System → create BadDebtProvision (TK 630)
6. System → post GL: Dr TK630 / Cr TK131
7. System → update ARInvoice.status = WRITTEN_OFF
8. System → log audit event (user, timestamp, reason)
9. If later recovered (ALT-AR-10): Dr TK131 / Cr TK631 (NOT reverse provision)
```

---

## 12. User Journeys

### UJ-AR-01: Sales Accountant — Create Customer + Invoice
```
Persona: Nguyễn Thị Mai, Sales Accountant at ABC Corp
Context: New customer "Công ty XYZ" signs contract, needs billing setup

1. Login → SmartACCT
2. Navigate to AR → Customers → New Customer
3. Enter details: tax_code "0123456789", name, address, credit_limit 500m VND, terms NET30
   → [ALT-AR-01] if tax_code invalid: error highlights field → fix and retry
   → [ALT-AR-02] if duplicate: conflict message → use search to find existing
4. Customer created → redirect to AR Invoice creation
5. Select customer "Công ty XYZ" → system shows credit available (380m remaining)
   → [ALT-AR-03] if would exceed: warning + request CFO override
6. Add line items: Product A × 10 @ 10m VND = 100m VND
   Subtotal 100m + VAT 10% = 110m total
7. Submit → [BR-AR-07] auto-post to GDT
   → [ALT-AR-06] if GDT rejects: ticket created → manual correction
8. GL posted → view journal entry: Dr TK131(110m) / Cr TK511(100m) / Cr TK3331(10m)
9. Email sent to customer with e-invoice link
10. Invoice appears in aging report (Current bucket)
```

### UJ-AR-02: Collections Officer — Daily Dunning Routine
```
Persona: Trần Văn Hùng, Collections Officer
Context: Daily morning routine — review overdue invoices

1. Login → SmartACCT → AR → Dunning Queue
2. View: 15 invoices overdue, sorted by days_past_due DESC
   - D2: 8 invoices (8-30 days overdue)
   - D3: 5 invoices (31-60 days overdue)
   - D4: 2 invoices (61-90 days overdue)
3. For each D2: send email reminder → mark as "contacted_email"
4. For each D3: send SMS + call customer → log note in ARDunningLog
5. For each D4: escalate to Legal team → generate demand letter PDF
6. Review: "Công ty DEF" — D5 (95 days) → propose write-off
7. Submit write-off request → CFO receives notification
8. End of day: status dashboard shows 10 contacted, 5 escalated, 1 write-off pending
```

### UJ-AR-03: CFO — Month-End Review
```
Persona: Lê Thị Hương, CFO
Context: Month-end close review

1. Login → SmartACCT → GL → Periods → Close Period 2026-05
2. Pre-close check: aging snapshot NOT yet generated → OK to close
3. Approve period close → GL generates closing entries
4. System auto-triggers CRP-AR-04: Aging Snapshot job runs
5. Review Aging Report:
   - Current: 2.5bn (65%) ✓
   - 1-30: 800m (21%) ⚠ slightly elevated
   - 31-60: 450m (12%) ⚠
   - 61-90: 200m (5%) 🔴
   - 91+: 150m (4%) 🔴 (potential write-offs)
6. KPIs:
   - DSO: 42 days (target: 35) → flag for collections team
   - CEI: 87% (target: 90%) → investigate 3 major disputes
7. Approve TK 630 provisions for 3 customers in 91+ bucket
   → Provisions total: 75m VND
8. Sign-off: AR balance sheet disclosure for BCTC (VAS-compliant)
9. Email report to Board of Directors
```

---

## 13. Implementation Plan

### Phase 1: Foundation (Weeks 1–3)
| Week | Tasks | Acceptance Criteria |
|------|-------|---------------------|
| 1 | `domain/ar.py` — 7 domain entities (Customer, ARInvoice, ARInvoiceLine, ARPayment, ARPaymentAllocation, ARDunningLog, BadDebtProvision, ARAgingSnapshot) | All entities pass domain validation tests |
| 1 | `infrastructure/models/ar_models.py` — 8 SQLAlchemy models | Models importable, test DB roundtrip |
| 2 | `migrations/versions/xxxx_ar_tables.py` — Alembic migration | `alembic upgrade head` creates all 8 tables |
| 2 | `infrastructure/repositories/ar_repository.py` — CRUD + aging queries | All 15+ repo methods unit tested |
| 3 | `use_cases/ar/__init__.py` — ARUseCases class | 15 use case methods defined |

### Phase 2: Core AR (Weeks 4–7)
| Week | Tasks | Acceptance Criteria |
|------|-------|---------------------|
| 4 | `presentation/ar/__init__.py` + `presentation/ar/routes.py` — customer routes | 5 customer endpoints working |
| 4 | `presentation/ar/invoice_routes.py` — 8 invoice endpoints | Invoice CRUD + GL posting tested |
| 5 | Payment allocation logic + routes | 3 payment endpoints FIFI allocation working |
| 5 | Wire GDTClient.submit_invoice() into AR invoice flow | GDT integration test passes |
| 6 | Aging engine (computed) + `GET /ar/aging` | 6-bucket report accurate for test data |
| 6 | ARAgingSnapshot + `POST /ar/aging/snapshot` | Snapshot locked to period, idempotent |

### Phase 3: Collection & Provisions (Weeks 8–10)
| Week | Tasks | Acceptance Criteria |
|------|-------|---------------------|
| 8 | Dunning workflow engine + ARDunningLog routes | 5 dunning levels auto-advance; logs persist |
| 8 | APScheduler cron job — daily dunning + monthly aging | Jobs registered, manual trigger works |
| 9 | TK 630 Bad Debt Provision calculator + routes | Rates match Circular 200/2014 |
| 9 | Write-off approval workflow + GL posting | CFO approval required Dr 630 / Cr 131 |
| 10 | ECL calculator (IFRS 9 3-stage) | Stage 1/2/3 classification works |

### Phase 4: Polish & Compliance (Weeks 11–12)
| Week | Tasks | Acceptance Criteria |
|------|-------|---------------------|
| 11 | IFRS 15 contract asset vs AR distinction | Contract asset for unbilled amounts |
| 11 | Credit limit enforcement + 80% warning | Credit check at invoice creation |
| 12 | i18n error codes for all AR paths | vi/en translations for 50+ error codes |
| 12 | 40+ AR tests (domain + use case + integration) | All tests pass |

### Phase 5: Reporting (Weeks 13–14) — MEDIUM Priority
| Week | Tasks | Acceptance Criteria |
|------|-------|---------------------|
| 13 | AR Balance report per customer | Accurate, period-filtered |
| 13 | Collection Effectiveness Index (CEI) + DSO | Formula matches Big4 standards |
| 14 | Customer AR statement PDF (aged) | Jinja2 template, i18n |
| 14 | Year-end BCTC disclosure blocks (IFRS 7) | Ready for audit |

### Phase 6: Advanced (Weeks 15–18+) — v2.0
- Multi-currency AR + hedge accounting
- Customer self-service portal (view invoices, pay online)
- External credit scoring integration
- Automated legal escalation
- AR factoring / invoice discounting

---

## 14. Success Criteria

1. **Functional**: All 15 P0+P1 use cases implemented and tested (UC-AR-01 through UC-AR-10)
2. **Regulatory**: E-invoices auto-submitted to GDT; TK 131/630/511/333 posting verified by accountant
3. **Quality**: 40+ AR tests, all 379 existing tests remain green
4. **Performance**: Aging report computes < 2s for 10k invoices; dunning job processes 1k invoices/min
5. **i18n**: All AR error messages available in vi/en
6. **Audit**: Full audit trail on all AR actions (created_by, updated_by, approval chain)
7. **Documentation**: Vietnamese-language user guide for accountants (ketoanleanh.edu.vn standard)
8. **Compliance**: VAS + IFRS 15 + IFRS 9 + NĐ70/2025 compliance matrix complete

---

## 15. Open Questions

1. **Q1**: Should EInvoice (Tax domain) and ARInvoice be unified or remain separate? Current thinking: separate but linked via FK (EInvoice = legal doc; ARInvoice = financial ledger)
2. **Q2**: For PIT withholding on overdue personal debt (TT 111/2013) — is this a high-priority requirement or can it be deferred to v2.0?
3. **Q3**: Collection letters — email only or also postal? Vietnam practice uses postal for D3+ — decide before writing templates
4. **Q4**: AR factoring or securitization — in scope? (Probably v2.0, but flag for legal)
5. **Q5**: Credit rating input — auto-calculate from external bureau or manual-entry by CFO only? (Manual safer for v1.0)
6. **Q6**: Should ARAgingSnapshot include projected cash flow (expected payment dates) or just historical balances?
7. **Q7**: Overpayment handling — should system auto-apply to next invoice or require manual refund? (Vietnamese accountants prefer manual control)

---

## 16. References

| Source | URL | Key Takeaway |
|--------|-----|-------------|
| Kế toán Thiên Ưng | ketoanthienung.net | Full practical AR posting + HTKK/Excel training content |
| Kế toán Lê Ánh | ketoanleanh.edu.vn | TT99/2025, TT133/2016, Circular 200/2014, NĐ70 training |
| Web Kế toán | webketoan.com | (unreachable at fetch time) |
| Văn bản PL | vbpl.vn | National legal DB |
| MOF | mof.gov.vn | Finance ministry policy |
| Tổng cục Thuế | gdt.gov.vn | e-invoice requirements, Decree 245/2026 June 2026 |
| Cổng Dịch vụ công | dichvucong.gov.vn | Government service portal |
| VAA | vaa.net.vn | Vietnam Accountancy Association standards |
| VACPA | vacpa.org.vn | Auditor professional body |
| IFRS Foundation | ifrs.org | IFRS 9 (ECL), IFRS 15 (Revenue), IFRS 7 (Disclosure) |
| EY Vietnam | ey.com/vn | Working capital, receivables optimization, IFRS advisory |
| PwC Vietnam | pwc.com/vn | Revenue recognition (IFRS 15), VAT compliance |
| Deloitte Vietnam | deloitte.com/vn | IFRS 9 transition advisory |
| KPMG Vietnam | kpmg.com/vn | IFRS Academy, digital receivables management |
| BHXH | baohiemxahoi.gov.vn | Social insurance — relevant for customer employee benefits deductions |
