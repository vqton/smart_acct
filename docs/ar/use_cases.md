# AR Use Cases
## SmartACCT ERP — Vietnamese AR Module

---

## UC-AR-01: Customer CRUD

**Priority:** P0 — CRITICAL  
**Actor:** Sales Accountant, System Administrator  
**Preconditions:** User has AR_CUSTOMER_WRITE permission; accounting period is OPEN  

**Main Flow (Happy Path):**
1. User calls `POST /ar/customers` with required fields: `customer_code`, `tax_code`, `name`, `address`, `credit_limit`, `payment_terms_days`
2. System validates: tax_code is 10–13 digits, Mã số thuế format; customer_code unique; credit_limit > 0; payment_terms_days > 0
3. System creates Customer record with `is_active = true`
4. System generates `customer_id` and `created_at` timestamp
5. Returns `201 Created` with full customer object

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-01 | tax_code format invalid | REJECT 400; highlight field | CUSTOMER_TAX_CODE_INVALID |
| ALT-AR-02 | customer_code already exists | REJECT 409 | CUSTOMER_CODE_DUPLICATE |
| ALT-AR-03 | credit_limit missing or ≤ 0 | REJECT 400 | CREDIT_LIMIT_INVALID |
| ALT-AR-04 | payment_terms_days missing | REJECT 400; default to 30 | PAYMENT_TERMS_INVALID |
| ALT-AR-11 | Customer has open AR invoices | BLOCK 409 on DELETE/DEACTIVATE | CUSTOMER_HAS_OPEN_AR |

**Post-conditions:** Customer record persisted; available for AR Invoice creation

---

## UC-AR-02: Create AR Invoice

**Priority:** P0 — CRITICAL  
**Actor:** Sales Accountant  
**Preconditions:** Customer exists and is ACTIVE; Accounting Period is OPEN; user has AR_INVOICE_WRITE permission  

**Main Flow (Happy Path):**
1. User calls `POST /ar/invoices` with `customer_id`, `items[]`, optional `payment_terms`
2. System fetches Customer record, reads `credit_limit` and `payment_terms_days`
3. System computes line totals, subtotal, VAT (per item vat_rate), grand_total
4. System checks: `customer.outstanding_balance + grand_total ≤ credit_limit` → [ALT-AR-03]
5. System computes due_date = invoice_date + payment_terms_days (default uses customer.payment_terms_days)
6. System creates ARInvoice (status=DRAFT) + ARInvoiceLine rows
7. System auto-generates EInvoice entity (in Tax domain) with buyer_* fields from Customer
8. System triggers `POST /ar/invoices/{id}/send`:
   a. Signs EInvoice via RSA-SHA256 signing service
   b. Submits to GDT via `GDTClient.submit_invoice()` — 3 retries with exponential backoff
   c. Stores `verification_code`, `gdt_transaction_id`, `signed_file_url` from GDT response
   d. Posts GL: Dr TK131 / Cr TK511 / Cr TK3331 (per TT99/2025)
   e. Updates ARInvoice.status = SENT, `einvoice_id` = FK to EInvoice
9. Returns `201 Created` with ARInvoice + EInvoice metadata

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-04 | GL Period is CLOSED | REJECT 403 | PERIOD_CLOSED |
| ALT-AR-03 | Credit limit exceeded | REJECT 422 | CREDIT_LIMIT_EXCEEDED |
| ALT-AR-06 | GDT rejects e-invoice | status → ERROR; 3 retries; notify Sales Acct | GDT_SUBMISSION_FAILED |
| ALT-AR-07 | Payment already exists | Cannot modify SENT invoice | INVOICE_ALREADY_PAID |
| ALT-AR-15 | Customer not found | REJECT 404 | CUSTOMER_NOT_FOUND |

**Post-conditions:** ARInvoice persisted; GL balanced; GDT acknowledged; aging bucket = current

---

## UC-AR-03: AR Aging Report (Live)

**Priority:** P0 — CRITICAL  
**Actor:** Sales Accountant, Collections Officer, CFO  
**Preconditions:** User authenticated; optional `?period=YYYY-MM` (defaults to current period)  

**Main Flow:**
1. User calls `GET /ar/aging?customer_id=1&period=2026-05`
2. System queries ARInvoice where `balance_due > 0` (live, from DB)
3. System computes `days_past_due = today() - due_date` (if status != PAID)
4. System assigns `aging_bucket` per BR-AR-03 rules
5. System aggregates: SUM(balance_due) per bucket per customer
6. Returns:
   ```json
   {
     "period": "2026-05",
     "generated_at": "2026-05-31T23:59:59Z",
     "customers": [
       {
         "customer_id": 1,
         "customer_code": "CUST-001",
         "name": "ABC Corp",
         "total_outstanding": 550000000,
         "current": 200000000,
         "bucket_1_30": 150000000,
         "bucket_31_60": 100000000,
         "bucket_61_90": 50000000,
         "bucket_91_180": 30000000,
         "bucket_181_365": 20000000,
         "bucket_365_plus": 0,
         "days_past_due_oldest": 45
       }
     ],
     "totals": { "total_ar": 2000000000, ... }
   }
   ```

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-14 | No period | Use current GL period | N/A (defaults) |
| ALT-AR-15 | Period doesn't exist | REJECT 404 | PERIOD_NOT_FOUND |

**Post-conditions:** Read-only; no DB writes

---

## UC-AR-04: Aging Snapshot (Period-Locked)

**Priority:** P0 — CRITICAL  
**Actor:** System (cron job), CFO can manually trigger  
**Preconditions:** GL Period must be CLOSED  

**Main Flow:**
1. System calls `POST /ar/aging/snapshot?period=2026-05`
2. System validates: `AccountingPeriod("2026-05").is_closed == True` → [ALT-AR-05] if not
3. System computes live aging balances per customer (same logic as UC-AR-03)
4. System writes ARAgingSnapshot rows (one per customer with non-zero balance)
5. System sets `snapshot.locked = true`, `snapshot.generated_at = now()`
6. System computes KPIs: DSO, CEI, Bad Debt Ratio
7. Returns `201 Created` with snapshot summary

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-05 | Period not CLOSED | REJECT 409 | PERIOD_NOT_CLOSED |
| ALT-AR-16 | Snapshot already exists for period | REJECT 409 | SNAPSHOT_ALREADY_EXISTS |

**Post-conditions:** Snapshot locked; historical record; used for BCTC disclosure

---

## UC-AR-05: Dunning Workflow

**Priority:** P0 — CRITICAL  
**Actor:** System (cron), Collections Officer (manual trigger)  
**Preconditions:** Invoice is SENT or PARTIALLY_PAID; days_past_due > 0; dunning_level < 5  

**Main Flow (Automated):**
1. APScheduler triggers daily 08:00 → `POST /ar/dunning/advance-all`
2. System queries: ARInvoice where `status in (SENT, PARTIALLY_PAID) AND due_date < today() AND dunning_level < 5`
3. For each invoice:
   a. Compute `days_past_due = today() - due_date`
   b. Determine new_dunning_level:
      - days_past_due 1-7 → level 1 (L1)
      - days_past_due 8-30 → level 2 (L2)
      - days_past_due 31-60 → level 3 (L3)
      - days_past_due 61-90 → level 4 (L4)
      - days_past_due > 90 → level 5 (L5)
   c. Increment ARInvoice.dunning_level if next_due_date has passed
   d. Execute notification action per level (email stub / SMS stub / PDF letter stub)
   e. Log ARDunningLog: `{ar_invoice_id, dunning_level, dunning_date, dunning_method, notes, performed_by}`
   f. Set ARInvoice.next_dunning_date = today() + cooldown_period(level)
   g. If days_past_due > 180 AND no BadDebtProvision: create draft provision, notify CFO
4. Returns `200 OK` with count of processed records

**Manual Trigger (Collections Officer):**
1. Collections calls `POST /ar/invoices/{id}/dunning` with optional `dunning_method`, `notes`
2. System validates: invoice is overdue; can advance max 1 level per manual call
3. System logs action + executes notification
4. Returns `200 OK`

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-17 | Invoice already at max level (5) | REJECT 400 on manual advance | DUNNING_MAX_LEVEL_REACHED |
| ALT-AR-18 | Invoice is PAID | Skip — no action needed | N/A (filtered out) |

**Post-conditions:** Dunning levels escalated; notifications logged; CFO alerted on L5

---

## UC-AR-06: Payment Allocation (FIFO)

**Priority:** P1 — HIGH  
**Actor:** Collections Officer, System (auto-allocate flag)  
**Preconditions:** Customer exists; at least one open ARInvoice with `balance_due > 0`; GL Period is OPEN  

**Main Flow:**
1. User calls `POST /ar/payments` with `customer_id`, `amount_received`, `payment_method`, `reference_number`
2. System creates ARPayment (status=PENDING_ALLOCATION)
3. System auto-allocates FIFO to oldest open ARInvoice(s):
   - Query: ARInvoice for customer where `balance_due > 0` ORDER BY due_date ASC
   - For each: `allocated = min(invoice.balance_due, amount_received - already_allocated)`
   - Create ARPaymentAllocation: `{ar_payment_id, ar_invoice_id, allocated_amount}`
   - Update ARInvoice: `balance_due -= allocated`, `amount_paid += allocated`
   - Update ARInvoice.status:
     - If balance_due == 0 → PAID
     - Else → PARTIALLY_PAID
4. For each affected invoice, post GL: Dr TK111 (or TK112) / Cr TK131
5. System computes `ARPayment.amount_applied = sum(allocated)`
6. System computes `ARPayment.amount_unapplied = amount_received - amount_applied`
7. If amount_unapplied > 0: create ARPaymentAllocation with `is_adjustment = true`; issue refund notice
8. Returns `201 Created` with ARPayment + allocation details

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-07 | amount_received > total outstanding | OVERPAYMENT: amount_unapplied > 0 → refund notice | OVERPAYMENT_DETECTED |
| ALT-AR-08 | amount_received = 0 | REJECT 400 | PAYMENT_AMOUNT_ZERO |
| ALT-AR-09 | Customer has no open invoices | REJECT 400; suggest credit balance or advance | NO_OPEN_INVOICES |
| ALT-AR-04 | Payment in CLOSED period | REJECT 403 | PERIOD_CLOSED |

**Post-conditions:** ARInvoice(s) balance_due reduced; GL balanced; unapplied cash tracked

---

## UC-AR-07: Bad Debt Provision (TK 630)

**Priority:** P1 — HIGH  
**Actor:** CFO (approval), System (calculation)  
**Preconditions:** GL Period is CLOSED; invoice is > 6 months overdue  

**Main Flow (Annual Provision — Year-End):**
1. System (cron) calls `POST /ar/bad-debt/provisions?period=2026-12`
2. System queries: ARInvoice where `balance_due > 0 AND days_past_due > 180 AND status != WRITTEN_OFF AND dunning_level = 5`
3. For each, computes provision_pct_per BR-AR-03:
   - 91-180 days: 5%
   - 181-365 days: 20%
   - >365 days: 50%
4. Sums per customer; creates BadDebtProvision rows (per customer batch)
5. Returns `201 Created` with provision summary
6. CFO reviews `/ar/bad-debt/provisions?period=2026-12`
7. CFO calls `POST /ar/bad-debt/write-off` with `provision_ids[]`, `approval_by`, `notes`
8. System creates ARDunningLog for write-off; posts GL: Dr TK630 / Cr TK131

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-20 | Invoice < 6 months overdue | REJECT 422 | PROVISION_PERIOD_NOT_MET |
| ALT-AR-21 | Provision already created for invoice | SKIP (idempotent) | ALREADY_PROVISIONED |
| ALT-AR-10 | Write-off recovered later | Dr 131 / Cr 631 (NOT reverse provision) | BAD_DEBT_RECOVERED |

**Post-conditions:** Provision recorded; TK 630 balance updated; audit trail complete

---

## UC-AR-08: Credit Limit Check

**Priority:** P2 — MEDIUM  
**Actor:** System (at invoice creation)  
**Preconditions:** Customer exists  

**Main Flow:**
1. Before UC-AR-02 Step 4, System computes `total_exposure = customer.outstanding_balance + new_invoice.grand_total`
2. If `total_exposure <= credit_limit`: proceed normally
3. If `80% <= total_exposure / credit_limit < 100%`: log WARNING; add `X-AR-Credit-Warning: 80%` response header
4. If `total_exposure >= credit_limit`: REJECT 422; return current balance, limit, new total

**Allowed override (CFO only):**
- CFO sets `customer.credit_limit_override = true` with reason via PUT /ar/customers/{id}
- Override nullified after 30 days (auto-expire)

---

## UC-AR-09: AR-to-GL Journal Posting (Auto)

**Priority:** P1 — HIGH  
**Actor:** System (triggered by invoice/payment events)  
**Preconditions:** Period is OPEN; use case ARUseCases has `session`  

**Main Flow:**
1. On ARInvoice.create (status=SENT): System creates JournalEntry
   ```
   Lines:
   - Dr TK131 (AR amount excluding VAT): 100,000,000
   - Cr TK511 (Revenue): 100,000,000
   - Cr TK3331 (VAT output): 10,000,000
   ```
2. On ARPayment.allocate: System creates JournalEntry
   ```
   Lines:
   - Dr TK111 (Cash received): 50,000,000
   - Cr TK131 (AR cleared): 50,000,000
   ```
3. On BadDebtProvision.create: Dr TK632 (if via expense) / Cr TK630
4. On Write-off: Dr TK630 / Cr TK131
5. All entries reference `source_module = "AR"`, `created_by = system or user_id`

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-04 | Period CLOSED | REJECT 403 on posting | PERIOD_CLOSED |
| ALT-AR-22 | GL balance mismatch | ROLLBACK entire AR transaction | GL_BALANCE_MISMATCH |

---

## UC-AR-10: NĐ70 E-Invoice Auto-Submission

**Priority:** P1 — HIGH (regulatory mandate)  
**Actor:** System  
**Preconditions:** ARInvoice.status = SENT; EInvoice entity created and signed  

**Main Flow:**
1. On ARInvoice.send, System creates timeout job (max 30s)
2. Step 1: Sign EInvoice via `SigningService.sign(einvoice)` → RSASignedPayload
3. Step 2: Call `GDTClient.submit_invoice(signed_payload)`
4. On success: update EInvoice.status = SENT, store `verification_code` + `gdt_transaction_id`
5. On failure: retry → backoff 1s → 5s → 30s (3 attempts max)
6. If all retries fail: mark EInvoice.status = ERROR; notify Sales Accountant; block further changes until manual correction
7. System logs each submission attempt in GDTSubmissionLog table

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-12 | Duplicate submission | EInvoice already SENT; idempotent return | EINVOICE_ALREADY_SUBMITTED |
| ALT-AR-06 | All retries exhausted | ERROR status; manual correction flow | GDT_SUBMISSION_FAILED |

---

## UC-AR-11: Write-Off Approval Workflow

**Priority:** P1 — HIGH  
**Actor:** Collections Officer (initiate), CFO (approve)  
**Preconditions:** Invoice > 6 months overdue; all dunning levels exhausted; no existing provision  

**Main Flow:**
1. Collections calls `POST /ar/bad-debt/write-off-request` with `ar_invoice_id`, `reason`, supporting_docs
2. System creates `BadDebtWriteOffRequest` (status=PENDING_APPROVAL)
3. System notifies CFO via internal notification
4. CFO reviews detail → calls `POST /ar/bad-debt/write-off` with `request_id`, `approval_by`, `approval_notes`
5. System validates CFO role via JWT
6. System executes TK 630 posting
7. System updates ARInvoice.status = WRITTEN_OFF
8. System logs in ARDunningLog + PeriodAuditLog (linked to GL Period)

**Alternative Flows:**

| ID | Condition | Behavior | Error Code |
|----|-----------|----------|------------|
| ALT-AR-20 | Invoice < 6 months overdue | REJECT 422 | WRITE_OFF_PERIOD_NOT_MET |
| ALT-AR-23 | Non-CFO attempts approval | REJECT 403 | INSUFFICIENT_PERMISSIONS |
| ALT-AR-24 | Request not in PENDING state | REJECT 400 | REQUEST_ALREADY_PROCESSED |

---

## UC-AR-12: Collection Effectiveness Index (CEI)

**Priority:** P2 — MEDIUM  
**Actor:** CFO, Controller  
**Preconditions:** At least 2 consecutive periods of data exist  

**Main Flow:**
1. User calls `GET /ar/reports/collection-effectiveness?periods=2026-01,2026-02,...,2026-05`
2. System computes for each period:
   ```
   CEI = (Beg_AR + Sales - End_AR - Bad_Debt) / (Beg_AR + Sales) × 100%
   DSO  = (Average_AR / Total_Credit_Sales) × (Days_in_Period)
   ```
3. Returns time-series data + trend analysis
4. System flags if CEI < 90% or DSO > 45 days (configurable thresholds)

**Post-conditions:** Read-only; used for management reporting

---

## UC-AR-13: IFRS 9 ECL Calculator

**Priority:** P2 — MEDIUM  
**Actor:** CFO (for IFRS reporters only)  
**Preconditions:** `customer.credit_rating` populated; IFRS mode enabled in config  

**Main Flow:**
1. System calls internal ECL service with `customer_id`, `reporting_date`
2. Classify stage:
   - Stage 1: days_past_due ≤ 30, no SICR
   - Stage 2: days_past_due 31-90 OR SICR detected
   - Stage 3: days_past_due > 90 OR default confirmed
3. Compute:
   - Stage 1: 12-month ECL = PD × LGD × EAD (1-year horizon)
   - Stage 2: Lifetime ECL = weighted-average over full contract life
   - Stage 3: Lifetime ECL on net exposure (interest accrual on net AR)
4. Returns ECL by stage + total + allowance adjustment per customer
5. Post to GL: Dr TK632 (IFRS ECL expense) / Cr provision account

**Post-conditions:** ECL provision booked; disclosure data ready for BCTC

---

## UC-AR-14: AR-to-AP Netting

**Priority:** P2 — MEDIUM (v2.0)  
**Actor:** CFO  
**Preconditions:** Both AR and AP modules operational; same customer is both debtor and creditor  

**Main Flow:**
1. CFO calls `POST /ar/netting` with `customer_id`, settlement_date, `notes`
2. System computes: net_position = AR.balance_due - AP.balance_due
3. If net > 0: Customer pays net amount → clear AR invoices + reduce AP
4. If net < 0: Company refunds net amount → clear AP invoices + reduce AR
5. System creates offsetting GL entries; log in ARDunningLog + AP log
6. Returns settlement confirmation

---

## Summary: Use Case Priority Matrix

| ID | Name | Priority | Estimated Story Points |
|----|------|----------|------------------------|
| UC-AR-01 | Customer CRUD | P0 | 5 |
| UC-AR-02 | Create AR Invoice | P0 | 8 |
| UC-AR-03 | AR Aging Report | P0 | 5 |
| UC-AR-04 | Aging Snapshot (locked) | P0 | 3 |
| UC-AR-05 | Dunning Workflow | P0 | 8 |
| UC-AR-06 | Payment Allocation | P1 | 8 |
| UC-AR-07 | Bad Debt Provision (TK 630) | P1 | 5 |
| UC-AR-08 | Credit Limit Check | P1 | 3 |
| UC-AR-09 | AR→GL Journal Posting | P1 | 8 |
| UC-AR-10 | NĐ70 E-Invoice Auto-Submission | P1 | 5 |
| UC-AR-11 | Write-Off Approval Workflow | P1 | 5 |
| UC-AR-12 | CEI + DSO Reporting | P2 | 5 |
| UC-AR-13 | IFRS 9 ECL Calculator | P2 | 8 |
| UC-AR-14 | AR-to-AP Netting | P2 | 5 |
| **TOTAL** | | | ~77 SP (~11 days with 2 devs) |
