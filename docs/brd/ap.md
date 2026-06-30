# BRD: Accounts Payable (AP) Module
## SmartACCT ERP — Vietnamese Accounting System

**Version:** 1.0
**Date:** 2026-06-30
**Author:** Lead BA (20+ yrs) + Chief Accountant (20+ yrs)
**Status:** DRAFT — Pending Implementation

---

## 1. Executive Summary

### 1.1 Purpose

Build AP module for SmartACCT ERP. Manage vendor purchases, invoice lifecycle, payment processing, withholding tax, AP aging, provisioning, and regulatory compliance per VAS (TT99/2025, TT200/2014, TT133/2016) and Vietnamese tax laws.

### 1.2 Current State Assessment

**VERDICT: NOT PRODUCTION-READY. SCORE: 0/5**

AP module = **zero code**. No domain entities, use cases, repository, models, routes, or tests.

**What exists (usable but NOT AP):**
| Asset | Status | AP Reuse |
|-------|--------|----------|
| COA TK 331 (Phải trả người bán) | AccountType.ACCOUNTS_PAYABLE defined | Reuse for GL posting |
| COA TK 3311/3312/3318 sub-accounts | AccountType.ACCOUNTS_PAYABLE_TO_VENDOR defined | Reuse |
| JournalEntry (GL) | Full CRUD + period-gated posting | Reuse for AP→GL auto-post |
| CashUseCases | Payment execution, bank integration | Reuse for payment runs |
| TaxUseCases | VAT input, EInvoice, WHT | Reuse for withholding tax |
| ARUseCases | Vendor cross-ref (TK 331) | Reference pattern only |
| GDTClient | Stub for e-tax submission | Extend for purchase e-invoice |
| SigningService | Stub for RSA signing | Reuse |

**Gap: EVERYTHING** — vendor master, purchase invoice, credit/debit note, prepayment, payment proposal, AP aging, provisioning, WHT, FCT, auto-GL posting, vendor statement reconciliation, aging snapshot.

### 1.3 Scope

**In scope (UC-AP-01 through UC-AP-15):**
- UC-AP-01: Vendor Master (supplier CRUD, tax code validation, status lifecycle)
- UC-AP-02: Purchase Invoice (PO-based + non-PO, 2-way/3-way matching)
- UC-AP-03: Debit Note / Credit Note (adjustments linked to original invoice)
- UC-AP-04: Prepayment to Vendor (advance payment, apply to invoice)
- UC-AP-05: Payment Processing (proposal, approval, execution, remittance)
- UC-AP-06: Payment Scheduling (due date calc, early payment discount, aging)
- UC-AP-07: AP Aging Report (live + snapshot, 6 buckets + VAS provision buckets)
- UC-AP-08: Provision for Payables (Circular 48/2019 + 24/2022 rates)
- UC-AP-09: Withholding Tax (FCT per Circular 103/2014, updated 86/2024, 69/2025)
- UC-AP-10: Foreign Currency AP (FX revaluation, realized/unrealized gain/loss)
- UC-AP-11: AP→GL Auto-Posting (Dr Expense/Inventory/Asset, Cr AP 331)
- UC-AP-12: Vendor Statement Reconciliation (auto-match + discrepancy handling)
- UC-AP-13: Intercompany Payables (TK 336, netting, centralized payment)
- UC-AP-14: Purchase E-Invoice (NĐ70/2025, input VAT deduction, GDT integration)
- UC-AP-15: AP Reporting (DPO, AP turnover, cash flow forecast, tax reports)

**Out of scope (v2.0+):**
- PO/Procurement full module (requisition → RFQ → PO)
- Automated OCR invoice capture
- Supplier self-service portal
- Dynamic discounting / supply chain finance
- Blockchain-based payment confirmation
- Procurement analytics / spend intelligence

---

## 2. Regulatory & Compliance Framework

### 2.1 Primary Legislation

| Citation | Title | AP Impact | Status |
|----------|-------|-----------|--------|
| **TT99/2025/TT-BTC** | Accounting Regime (replaces TT133/2016) | TK 331 posting, purchase recording, FX revaluation at period-end | Core posting logic |
| **TT200/2014/TT-BTC** | Accounting Regime (large enterprises) | Full chart of accounts, TK 331 sub-ledger detail | Compliance |
| **TT133/2016/TT-BTC** | Accounting Regime (SMEs) | Simplified COA, TK 331 rules | SME compliance |
| **NĐ70/2025/NĐ-CP** | E-Invoice Decree | Mandatory e-invoice from 01/01/2026 for ALL purchases | Purchase e-invoice |
| **NĐ123/2020/NĐ-CP** | E-Invoice (replaced by NĐ70) | Input VAT deduction requires valid e-invoice + bank payment ≥ 20M VND | VAT deduction |
| **TT78/2021/TT-BTC** | E-Invoice implementation | Cross-period adjustments, invoice cancellation | E-invoice adjustments |
| **Circular 103/2014/TT-BTC** | Foreign Contractor Tax | WHT on payments to foreign vendors without PE (VAT 2-5%, CIT 1-10%) | FCT processing |
| **Circular 86/2024/TT-BTC** | Updated FCT | Expanded scope, updated rates | FCT update |
| **Circular 69/2025/TT-BTC** | Updated FCT | Further clarifications on hybrid method | FCT update |
| **Circular 48/2019/TT-BTC** | Bad Debt Provisions | Provision rates: 30% at 6mo, 50% at 12mo, 70% at 24mo, 100% at 36mo | AP provisioning |
| **Circular 24/2022/TT-BTC** | Updated Provisions | Netting rule: provision on balance after offsetting receivables | Provision calculation |
| **Law 48/2024/QH15** | VAT Law (2025) | VAT registration threshold 1bn VND/year; input VAT deduction conditions | VAT processing |
| **Law 108/2025/QH15** | Tax Admin | Digital obligation; GDT data cross-referencing | Compliance audit |
| **IFRS 9** | Financial Instruments | Amortized cost for AP, no fair value option | IFRS transition |
| **IAS 37** | Provisions & Contingencies | Legal vs constructive obligations for payables | Provision framework |

### 2.2 Chart of Accounts (TK) Mapping for AP

| TK Code | Vietnamese Name | DCR | AP Role |
|---------|-----------------|-----|---------|
| **TK 331** | Phải trả người bán | Credit | Main AP — amounts owed to vendors |
| **TK 3311** | Phải trả ngắn hạn người bán | Credit | Short-term AP ≤ 12 months |
| **TK 3312** | Phải trả dài hạn người bán | Credit | Long-term AP > 12 months |
| **TK 3318** | Phải trả khác người bán | Credit | Other payables |
| **TK 133** | Thuế GTGT đầu vào được khấu trừ | Debit | Input VAT deductible |
| **TK 1331** | Thuế GTGT đầu vào hàng hóa, dịch vụ | Debit | Input VAT on goods/services |
| **TK 1332** | Thuế GTGT đầu vào TSCĐ | Debit | Input VAT on fixed assets |
| **TK 152** | Nguyên liệu, vật liệu | Debit | Inventory receipt (goods) |
| **TK 153** | Công cụ, dụng cụ | Debit | Tools/supplies receipt |
| **TK 156** | Hàng hóa | Debit | Merchandise receipt |
| **TK 211** | TSCĐ hữu hình | Debit | Fixed asset purchase |
| **TK 241** | XDCB dở dang | Debit | Construction in progress |
| **TK 611** | Mua hàng | Debit | Purchase (simplified) |
| **TK 632** | Giá vốn hàng bán | Debit | COGS |
| **TK 641** | Chi phí bán hàng | Debit | Selling expenses |
| **TK 642** | Chi phí quản lý doanh nghiệp | Debit | Admin expenses |
| **TK 111** / **TK 112** | Tiền mặt / Tiền gửi NH | Credit | Payment clearing |
| **TK 333** | Thuế & các khoản phải nộp NN | Credit | WHT payable |
| **TK 3331** | Thuế GTGT phải nộp | Credit | VAT payable |
| **TK 3335** | Thuế TNCN | Credit | PIT payable (FCT) |
| **TK 3338** | Thuế TNDN | Credit | CIT payable (FCT) |
| **TK 338** | Phải trả, phải nộp khác | Credit | Insurance, union fees |
| **TK 3383** | BHXH | Credit | Social insurance |
| **TK 3384** | BHYT | Credit | Health insurance |
| **TK 3385** | BHTN | Credit | Unemployment insurance |
| **TK 3386** | BHTNLĐ, BNN | Credit | Occupational accident insurance |
| **TK 336** | Phải trả nội bộ | Credit | Intercompany payables |
| **TK 341** | Vay & nợ thuê TC | Credit | Borrowings |

### 2.3 Input VAT Deduction Rules (TT78/2021 + NĐ70/2025)

| Condition | Rule | AP Impact |
|-----------|------|-----------|
| Valid e-invoice | Must have valid seller tax code, invoice number, series | Validate on invoice entry |
| Payment threshold | ≥ 20M VND must pay via bank transfer for deduction | Payment method validation |
| Timing | Deduct in period when both goods received AND invoice received | Period matching |
| Non-deductible VAT | VAT on entertainment, non-business use, certain imports | Separate TK 1332 vs expense |
| Partial deduction | Mixed-use goods: proportional deduction | Allocation logic |
| Export threshold | 10% export/total revenue → monthly refund | Reporting |
| FCT invoices | Foreign vendor without PE: reverse charge mechanism | FCT processing |

### 2.4 Foreign Contractor Tax (FCT) — Circular 103/2014 + 86/2024 + 69/2025

| Method | VAT Rate | CIT Rate | Condition |
|--------|----------|----------|-----------|
| **Direct** | 2% (services) / 3% (construction) / 5% (other) | 1% (services) / 2% (construction) / 10% (royalties) | Foreign contractor has PE in Vietnam |
| **Deduction** | 10% (standard) / 5% (transport) / 0% (insurance/reinsurance) | 10% (trading) / 5% (services) / 10% (royalties/interest) | No PE; buyer responsible for withholding |
| **Hybrid** | As per deduction method | As per direct method | Mixed services/goods contract |

**Key rules:**
- Vietnamese buyer MUST withhold and remit FCT within 20 days of payment
- Gross-up calculation: if contract says "net after FCT", buyer bears FCT + CIT on behalf
- FCT does NOT apply to goods shipped to Vietnam with title transfer at border (CIF/FOB)
- FCT applies to: services performed in Vietnam, royalties, interest, rents, technical fees
- FCT exempt: international transportation (reciprocal exemption), certain financial services
- E-tax submission: FCT declarations via thuedientu.gdt.gov.vn

### 2.5 AP Provisioning — Circular 48/2019 + 24/2022

| Overdue Period | Provision Rate |
|----------------|---------------|
| 6 months (180 days) | 30% |
| 1 year (365 days) | 50% |
| 2 years (730 days) | 70% |
| 3 years (1095 days) | 100% |

**Netting rule (Circular 24/2022):** Calculate provision on balance after offsetting same-vendor receivables.
**Tax treatment:** Provision is CIT-deductible if properly documented (written evidence of overdue, debt collection attempts).

---

## 3. User Roles & Responsibilities

| Role | Vietnamese Title | AP Responsibilities |
|------|------------------|---------------------|
| **AP Clerk** | Nhân viên phải trả | Enter purchase invoices, match POs, process payments |
| **AP Supervisor** | Giám sát phải trả | Approve invoice exceptions, resolve disputes, manage aging |
| **AP Manager** | Trưởng bộ phận phải trả | Approve payment runs, sign off on vendor banking changes |
| **Procurement** | Bộ phận mua hàng | Create POs, receive goods, verify delivery |
| **Warehouse** | Thủ kho | Confirm goods receipt (GR), quality inspection |
| **Chief Accountant** | Kế toán trưởng | Approve provisioning, write-offs, period-end close |
| **CFO** | Giám đốc tài chính | Approve payments > threshold, approve new vendor onboarding |
| **Tax Accountant** | Kế toán thuế | FCT remittance, VAT input deduction, e-invoice reporting |
| **Treasury** | Thủ quỹ / Ngân quỹ | Execute payments, manage cash position |

---

## 4. Material (GL) Accounts Affected

### 4.1 Balance Sheet

| Account | Posting Logic |
|---------|---------------|
| AP Control (331) | Credit on vendor invoice; Debit on payment/credit note |
| Prepayment to Vendor (331 debit balance) | Classified as current asset on BS, netted per vendor |
| Input VAT (133) | Debit on vendor invoice; Credit on VAT settlement |
| Insurance Payable (3383/3384/3385/3386) | Credit on payroll; Debit on payment |
| Intercompany (336) | Credit on IC invoice; Debit on IC settlement |

### 4.2 Income Statement

| Account | Posting Logic |
|---------|---------------|
| Expense/Inventory (152/156/621/627/641/642) | Debit on vendor invoice |
| COGS (632) | Debit on inventory consumption, linked to purchase |
| Provision Expense (6422) | Debit on provision creation |
| FX Loss (635) | Debit on unfavorable FX revaluation |
| FX Gain (515) | Credit on favorable FX revaluation |
| Purchase Discount (515) | Credit on early payment discount captured |
| Late Payment Penalty (811) | Debit on late payment interest/penalty |

### 4.3 GL Posting Matrix

| Transaction | Debit | Credit | Amount |
|-------------|-------|--------|--------|
| Goods receipt (no invoice) | Inventory (152/156) | GR/IR Accrual (3318) | Purchase price |
| Vendor invoice (goods) | GR/IR Accrual (3318) | AP Control (331) | Purchase price |
| Vendor invoice (expense) | Expense (641/642) | AP Control (331) | Expense amount |
| Vendor invoice with VAT | Expense/Inventory | AP Control (331) | Net amount |
| | Input VAT (133) | | VAT amount |
| Prepayment to vendor | AP Control (331) | Bank (112) | Prepaid amount |
| Apply prepayment to invoice | Expense/Inventory | AP Control (331) | Invoice amount |
| | AP Control (331) | AP Control (331) | Prepayment offset |
| Payment (net) | AP Control (331) | Bank (112) | Payment amount |
| Payment with discount | AP Control (331) | Bank (112) | Net payment |
| | | Discount Income (515) | Discount amount |
| Credit note from vendor | AP Control (331) | Inventory/Expense | Return/adjustment |
| | | Input VAT (133) | VAT adjustment |
| Debit note to vendor | Expense/Inventory | AP Control (331) | Additional charge |
| FX revaluation (loss) | FX Loss (635) | AP Control (331) | Unrealized loss |
| FX revaluation (gain) | AP Control (331) | FX Gain (515) | Unrealized gain |
| FCT withholding | AP Control (331) | WHT Payable (3335/3338) | Withheld amount |
| Provision creation | Provision Exp (6422) | Provision (229) | Provision amount |

---

## 5. Use Cases (UC-AP-01 to UC-AP-15)

### UC-AP-01: Vendor Master Management

**Description:** Create, read, update, search, suspend, block vendors.

**Happy Path:**
1. User submits vendor registration (vendor_code, name, tax_code, address, bank_account, payment_terms, currency)
2. System validates: tax_code format (10/13/14 digits for VN, configurable for foreign), vendor_code unique
3. System auto-checks tax_code against GDT database (optional: return warning if not found)
4. System creates vendor with status `ACTIVE`, generates vendor_id
5. Return vendor data + 201

**Alternative Paths:**
- **A1 - Duplicate tax_code:** Warn user, allow override if admin-approved
- **A2 - Foreign vendor:** Skip GDT tax_code check, require WHT configuration (FCT method/rates)
- **A3 - Bulk import:** CSV/Excel upload with row-level validation errors
- **A4 - Duplicate vendor_code:** Reject with error

**Exception Paths:**
- **E1 - Missing tax_code (VN vendor):** Block save; require valid tax_code
- **E2 - Invalid bank account (IBAN/account format):** Warn; allow save but mark "unverified"
- **E3 - Tax_code fails GDT validation (blocking mode):** Reject registration, return GDT error

**Rules:**
- vendor_code: unique, max 20 chars, alphanumeric + `-_`
- tax_code: 10 digits (VN), 13 digits (VN extended), 14 digits (foreign format)
- payment_terms: one of `net_30`, `net_60`, `net_45`, `due_on_receipt`, `custom`
- currency: ISO 4217, default VND
- status lifecycle: `ACTIVE → SUSPENDED → BLOCKED → ARCHIVED`, no reverse from BLOCKED
- Banking changes require dual approval + audit trail

**Data Flow:**
```
User → POST /api/v1/ap/vendors → ARUseCases.create_vendor()
  → ARRepository.create_vendor()
    → Validate domain model (Vendor entity)
    → Check tax_code uniqueness
    → Optional: GDTClient.verify_tax_code()
    → INSERT into vendors table
  → Return Vendor domain object
  → Controller → JSON response 201
```

**States:**
```
                    ┌─────────────┐
                    │   ACTIVE    │◄────────────┐
                    └──────┬──────┘             │
                           │                    │
                    ┌──────▼──────┐             │
                    │  SUSPENDED  │─────────────┘
                    └──────┬──────┘  (re-activate)
                           │
                    ┌──────▼──────┐
                    │   BLOCKED   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  ARCHIVED   │
                    └─────────────┘
```

---

### UC-AP-02: Purchase Invoice Processing

**Description:** Record vendor invoice, PO matching (2-way/3-way), validation, approval routing, GL posting.

**Happy Path (PO-based, 3-way match):**
1. User enters invoice: invoice_number, vendor_id, invoice_date, due_date, PO_number, lines (item, qty, unit_price, tax_rate), total_amount
2. System validates: invoice_number + vendor_id unique, vendor status == ACTIVE
3. System fetches PO: validates PO exists, status == APPROVED
4. System fetches Goods Receipt: validates goods received qty >= invoice qty
5. 3-way matching:
   - PO qty >= invoice qty
   - GR qty >= invoice qty
   - PO unit_price == invoice unit_price (within tolerance ±2%)
6. If match pass: auto-approve (straight-through processing)
7. GL posting: Dr Inventory/Expense, Dr Input VAT, Cr AP Control
8. Return invoice + 201

**Happy Path (Non-PO):**
1. User enters standalone invoice: vendor, lines, GL coding
2. System validates basic fields
3. Route to AP Supervisor for approval (no PO = higher risk)
4. On approval: GL posting as configured
5. Return invoice + 201

**Alternative Paths:**
- **A1 - Price tolerance exceeded (< 5%):** Flag for AP Supervisor review
- **A2 - Price tolerance exceeded (≥ 5%):** Block; require Procurement re-approval
- **A3 - Qty mismatch (invoice > GR):** Partial match; pay matched qty, hold remainder
- **A4 - No PO reference:** Route to manual approval (non-PO path)
- **A5 - Invoice received before GR:** Hold in "awaiting receipt" queue; auto-post when GR arrives
- **A6 - Discount on invoice:** Apply to AP liability; check PO discount terms

**Exception Paths:**
- **E1 - Duplicate invoice (number+vendor+date):** Reject with error
- **E2 - Vendor blocked/suspended:** Hold invoice, notify AP Manager
- **E3 - PO already fully invoiced:** Reject; require debit note for additional charges
- **E4 - Missing mandatory fields (vendor, invoice_date, lines):** Reject with field-level errors
- **E5 - Invoice VAT mismatch vs expected:** Flag for tax accountant review
- **E6 - Currency mismatch (invoice != vendor default):** Warn; require confirmation

**Rules:**
- Matching tolerance: price ±2% auto-approve, ±2-5% supervisor, >5% procurement
- GR must precede invoice for 3-way match (allow 5 business day grace)
- Invoice without PO: mandatory approval, cannot auto-approve
- Non-PO invoices max 20% of total AP volume (configurable)
- Input VAT: auto-calculate from line tax rates if missing
- Period: lock to open per period-gated posting (GL module)
- Approval routing: amount-based DOA matrix

**Workflow:**
```
Invoice Entry → Validation → PO Match → Match OK? → Yes → Auto-Approve → GL Post
                                   │                    │
                                   ├─ Price Tol <5% ─── Supervisor Review ──┤
                                   ├─ Price Tol ≥5% ─── Procurement Review ─┤
                                   ├─ Qty Mismatch ─── Partial Appr ────────┤
                                   └─ No PO ────────── AP Manager Appr ─────┘
```

**Data Flow:**
```
Invoice Entry → Validation Engine
  → PO Repository (get PO + lines)
  → GR Repository (get GR qty)
  → Matching Engine (3-way match)
  → Approval Router (DOA matrix)
  → GL Posting Engine
    → Dr Inventory/Expense
    → Dr Input VAT
    → Cr AP Control
  → Update PO invoiced_qty
  → Return Invoice
```

---

### UC-AP-03: Debit Note / Credit Note

**Description:** Record adjustments to posted invoices. Must reference original invoice.

**Happy Path (Credit Note):**
1. User selects original invoice, enters credit note (reason, lines, amount)
2. System validates: original invoice exists, status != CANCELLED
3. System creates credit note linked to original invoice
4. GL posting: Dr AP Control, Cr Inventory/Expense (+ Dr Input VAT reversal if applicable)
5. Update original invoice: balance_due = balance_due - credit_note.amount
6. Return credit note + 201

**Happy Path (Debit Note):**
1. User selects original invoice, enters debit note (reason, lines, amount)
2. Same validation as credit note
3. GL posting: Dr Expense/Inventory, Cr AP Control
4. Update original invoice: balance_due += debit_note.amount
5. Return debit note + 201

**Alternative Paths:**
- **A1 - Credit note after payment:** Create as standalone AP credit; apply to next invoice or ask vendor to refund
- **A2 - Tax adjustment on credit note:** Reverse input VAT proportionally

**Exception Paths:**
- **E1 - Original invoice fully paid:** Credit note creates negative balance (AP debit); refund required
- **E2 - Amount > original invoice:** Block; require admin override
- **E3 - Original invoice written off:** Reject adjustment

**Rules:**
- Credit/debit note MUST reference original invoice_number + vendor_id
- Max adjustment: original invoice total amount
- VAT adjustment: must reverse input VAT at original rate
- Credit note after payment: refund via bank transfer (separate transaction)
- Debit note for additional charges: only valid if not already covered by PO

---

### UC-AP-04: Prepayment to Vendor

**Description:** Record advance payment to vendor before goods/services delivered.

**Happy Path:**
1. User creates prepayment request: vendor_id, amount, expected_invoice_date, reason
2. System validates: vendor active, amount > 0
3. GL posting: Dr AP Control (331 debit — classified as prepayment), Cr Bank (112)
4. System marks AP vendor with debit balance (prepayment)
5. Return prepayment + 201

**Apply Prepayment to Invoice:**
1. User selects invoice, applies prepayment (full or partial)
2. System validates: prepayment vendor == invoice vendor, prepayment unapplied balance >= amount
3. GL posting: Dr Expense/Inventory (net), Dr Input VAT (133), Cr AP Control (331)
4. Offset: Dr AP Control (331 — prepayment), Cr AP Control (331 — invoice) — netting
5. Update prepayment: applied_amount += amount, unapplied_balance -= amount
6. Return applied prepayment

**Alternative Paths:**
- **A1 - Partial prepayment:** Unapplied balance remains for future invoices
- **A2 - Prepayment not applied within 90 days:** Flag for AP Supervisor review (possible unreconciled)
- **A3 - Prepayment > invoice:** Remainder stays as prepayment for next invoice

**Exception Paths:**
- **E1 - Prepayment to blocked vendor:** Block; require activation first
- **E2 - Prepayment currency != vendor currency:** Warn; FX rate applied at payment date

**Rules:**
- Prepayment is NOT AP liability; classified as short-term asset (TK 331 debit balance)
- BS presentation: net per vendor (debit balance = asset, credit balance = liability)
- Separate GL account for vendor prepayments recommended (tracking)
- VAT: no input VAT deduction on prepayment (deduct on final invoice per NĐ70)

---

### UC-AP-05: Payment Processing

**Description:** Payment proposal, approval, execution, remittance.

**Happy Path (Payment Run):**
1. User initiates payment proposal: vendor(s), due_date_from, due_date_to, payment_method
2. System selects all due invoices for selected vendors, criteria:
   - Status == APPROVED
   - Due date <= cutoff date
   - Vendor not BLOCKED
   - Balance_due > 0
3. System creates payment proposal (list of invoices grouped by vendor)
4. User reviews proposal: can exclude individual invoices, adjust amount (partial pay OK)
5. AP Manager approves proposal (if total > threshold, CFO approval)
6. System executes payment:
   - For each vendor: group invoices, sum total, create payment document
   - GL posting: Dr AP Control (331), Cr Bank (112)
   - Generate payment file (format per bank requirement)
7. Update invoice status: balance_due = 0 (or partial), paid_amount += payment_amount
8. Send remittance advice to vendor (email + portal notification)
9. Return payment batch + payment_file

**Alternative Paths:**
- **A1 - Partial payment:** Pay portion of invoice; balance remains open
- **A2 - Payment with discount:** Apply early payment discount (2/10 Net 30)
- **A3 - Bulk payment:** Single wire for multiple invoices to same vendor
- **A4 - Urgent payment (out-of-cycle):** One-off payment for single invoice; highest approval route
- **A5 - Hold payment:** Block individual invoice in proposal; must enter reason

**Exception Paths:**
- **E1 - Payment exceeds cash balance:** Warn; CFO must confirm availability
- **E2 - Bank account invalid/closed:** Block vendor from proposal; flag to AP Manager
- **E3 - Duplicate payment detection:** System checks vendor + invoice + amount against last 90 days
- **E4 - Payment fails at bank (NSF, account frozen):** Automatic retry (max 3); escalate to treasury

**Rules:**
- Segregation: proposal preparer ≠ approver ≠ payment executor
- Payment approval thresholds: config in DOA matrix
- Discount capture: auto-calculate if payment within discount period
- Positive Pay: send check file to bank before check issuance
- Payment file formats: NACHA ACH (VN banks), ISO 20022, SWIFT MT101
- Min payment amount: VND 100,000 (configurable); below threshold accumulates

**DOA Matrix:**
| Payment Amount | Required Approver | Escalation |
|----------------|-------------------|------------|
| < 50M VND | AP Supervisor | 48h → AP Manager |
| 50M - 500M VND | AP Manager | 24h → CFO |
| 500M - 5B VND | CFO | 12h → CEO |
| > 5B VND | CEO + Board | — |

**State Machine:**
```
PROPOSAL → REVIEW → APPROVED → EXECUTING → EXECUTED → POSTED
   │          │          │          │           │
   └──CANCELLED┘          └──REJECTED┘          └──FAILED
```

---

### UC-AP-06: Payment Scheduling

**Description:** Auto-calculate due dates, track early payment discounts, schedule optimization.

**Happy Path:**
1. On invoice creation, system calculates due_date based on vendor payment_terms
2. If terms include discount window (e.g., 2/10 Net 30):
   - discount_due_date = invoice_date + 10 days
   - net_due_date = invoice_date + 30 days
3. System auto-schedules invoice in payment calendar
4. If current_date within discount window AND cash_balance sufficient → flag as "discount eligible"
5. Return payment schedule

**Alternative Paths:**
- **A1 - Custom terms per invoice:** Override vendor default terms
- **A2 - Installment plan:** Multiple due dates with % splits (e.g., 50% 30 days, 50% 60 days)
- **A3 - Negotiated early payment (dynamic discount):** Offer vendor early payment at negotiated rate

**Rules:**
- Due date = invoice_date + vendor_payment_terms (in days)
- If due_date falls on holiday → next business day
- Discount capture rate KPI tracked
- Overdue auto-flag: due_date passed + not paid = OVERDUE status

---

### UC-AP-07: AP Aging Report

**Description:** Live aging report + period-locked snapshot for financial statements.

**Happy Path (Live Aging):**
1. User requests aging report: as_of_date, vendor_filter (optional), currency_filter
2. System queries open AP items (balance_due > 0):
   - For each vendor: group invoices by due_date buckets
3. Buckets: Current (not due), 1-30, 31-60, 61-90, 91-180, 181-365, 365+
4. Calculate subtotals per bucket, overall total
5. Return aging report

**Happy Path (Snapshot):**
1. User creates aging snapshot: period (YYYY-MM)
2. System freezes current aging data for period
3. Locked = true (cannot be modified after close)
4. Return snapshot created

**Alternative Paths:**
- **A1 - Vendor-level detail:** Drill-down by vendor showing individual invoices
- **A2 - Currency-specific:** Show aging in original currency + VND equivalent
- **A3 - Aging with provisions:** Show provision amount per aging bucket

**Rules:**
- Aging = balance_due > 0; exclude fully paid, cancelled, written-off
- Bucket days = as_of_date - due_date
- Negative aging (not yet due) = Current bucket
- Snapshot locked after period close; cannot be re-run for closed period

---

### UC-AP-08: Provision for Payables

**Description:** Create bad debt provision for payables per Circular 48/2019.

**Happy Path:**
1. User triggers provision calculation: period, as_of_date
2. System calculates for each overdue vendor:
   - Calculate days overdue from each invoice's due_date to as_of
   - Per Circular 48/2019 rates: 6mo→30%, 12mo→50%, 24mo→70%, 36mo→100%
   - Apply netting rule (Circular 24/2022): offset same-vendor receivables
3. System creates provision entries per vendor
4. GL posting: Dr Provision Expense (6422), Cr Provision (229)
5. Return provision summary

**Alternative Paths:**
- **A1 - Existing provision carried forward:** Adjust difference (increase/decrease)
- **A2 - Vendor has both AP and AR:** Net before provision calculation
- **A3 - Written-off payables:** Reverse provision, remove from AP

**Rules:**
- Provision rate per vendor, not per invoice (aggregate overdue balance)
- Netting: provision on (AP_total - AR_same_vendor) if AR < AP
- Provision is CIT-deductible with proper documentation
- Provision must be reviewed at each year-end close
- Written-off AP > 3 years: reversal to Other Income (711)

---

### UC-AP-09: Withholding Tax (FCT)

**Description:** WHT on payments to foreign vendors per Circular 103/2014.

**Happy Path:**
1. User flags foreign vendor on registration (FCT_required = true)
2. On invoice entry, system checks vendor.is_foreign && FCT_type
3. System auto-calculates WHT:
   - VAT_FCT = invoice_amount * applicable_VAT_rate (2-5%)
   - CIT_FCT = (invoice_amount - VAT_FCT) * applicable_CIT_rate (1-10%)
   - Net_payment = invoice_amount - VAT_FCT - CIT_FCT
4. GL posting (full deduction method):
   - Dr Expense (invoice_amount)
   - Cr AP Control (net_payment)
   - Cr WHT Payable - VAT (3338)
   - Cr WHT Payable - CIT (3335)
5. Generate FCT declaration for GDT submission (thuedientu)
6. On payment: Dr AP Control (net), Cr Bank (net)
7. On FCT remittance: Dr WHT Payable, Cr Bank

**Alternative Paths:**
- **A1 - Direct method:** Vendor pays taxes in Vietnam; buyer pays gross amount
- **A2 - Hybrid method:** Split contract: goods portion (no FCT) + service portion (FCT)
- **A3 - FCT exemption:** Validate treaty exemption; require documentation

**Rules:**
- FCT must be remitted within 20 days of payment to foreign vendor
- Gross-up: if contract says "net", calculate gross = (net_amount) / (1 - combined_FCT_rate)
- Treaty rates: double taxation agreements may reduce rates (US: 5% CIT, 0% VAT for royalties)
- FCT declaration via GDT e-tax portal
- E-invoice: FCT is NOT VAT-deductible on buyer side (reverse charge)

---

### UC-AP-10: Foreign Currency AP

**Description:** Handle AP in foreign currency, FX revaluation.

**Happy Path:**
1. Vendor registered with foreign currency (USD/EUR/JPY)
2. Invoice entered in foreign currency + exchange rate
3. AP recorded in VND equivalent at invoice-date rate
4. On payment: convert at payment-date rate
5. Realized FX gain/loss: Dr AP, Cr Bank @ payment_rate, difference → 635/515
6. Period-end (monthly): revalue all open FX AP at bank selling rate
7. Unrealized FX gain/loss: Dr/Cr AP Control, Cr/Dr 635/515

**VAS rules for FX revaluation (TT200/2014):**
- Use bank selling rate at period-end (Tỷ giá bán của ngân hàng thương mại)
- Both realized and unrealized FX gains/losses to P&L (515/635)
- FX differences on purchase of fixed assets: capitalize (TK 211/241)

**Rules:**
- Currency per vendor, override per transaction allowed
- Exchange rate source: configurable (central bank, commercial bank, daily feed)
- Minimum 2 decimal places for VND equivalent, 4-6 for foreign currency
- Realized FX: actual payment date rate
- Unrealized FX: period-end revaluation of all open foreign currency items
- FX gain on AP settlement before invoice maturity: must be disclosed (rare in practice)

---

### UC-AP-11: AP to GL Auto-Posting

**Description:** Auto-generate GL journal entries from AP transactions.

**Happy Path:**
1. On every AP transaction (invoice, payment, credit note, etc.), system generates GL entries per posting matrix (Section 4.3)
2. System validates: debit_total == credit_total (within 0.001 VND tolerance)
3. System posts to GL module (JournalEntry + JournalLine)
4. GL period must be open (period-gated posting via GLUseCases)
5. Each AP transaction linked to its GL entries (audit trail)

**Rules:**
- AP Control account (331) must NEVER be posted via manual GL journal — only through AP subledger
- Periodic reconciliation: AP aging total = GL AP Control account balance
- Posting profile per transaction type: configurable GL accounts
- Rounding difference tolerance: 0.001 VND

---

### UC-AP-12: Vendor Statement Reconciliation

**Description:** Match vendor-issued statements against AP ledger.

**Happy Path:**
1. User uploads vendor statement (PDF/CSV) or imports via API
2. System parses statement: opening_balance, invoices, payments, credits, closing_balance
3. System auto-matches statement line items to AP ledger by:
   - Invoice number + amount + date (exact match)
   - Payment reference + amount (exact match)
4. Calculate difference: statement_closing vs ledger_closing
5. If difference == 0: reconciliation complete
6. If difference != 0: flag discrepancies for manual review

**Alternative Paths:**
- **A1 - Partial match (amount difference < 1%):** Flag for supervisor, auto-match with warning
- **A2 - Missing ledger entry:** Create missing entry from statement line (requires approval)
- **A3 - Statement item not in ledger:** Investigate; may be vendor error

**Rules:**
- Reconcile monthly before period close for high-volume vendors
- Foreign currency: compare in original currency, not VND equivalent
- Discrepancy aging: unresolved > 60 days = escalation

---

### UC-AP-13: Intercompany Payables

**Description:** AP transactions between group companies.

**Happy Path:**
1. Company A records IC invoice to Company B for services/products
2. System auto-generates:
   - Company A: Dr Expense, Cr IC Payable (336)
   - Company B: Dr IC Receivable (136), Cr Revenue (511)
3. IC settlement via centralized treasury or netting
4. Netting: calculate IC balances across all entities, settle net difference

**Rules:**
- IC accounts: 136 (Due From), 336 (Due To)
- Zero intercompany profit elimination at consolidation
- Transfer pricing documentation required
- VAS requires all IC transactions at arm's length

---

### UC-AP-14: Purchase E-Invoice

**Description:** E-invoice receipt, validation, input VAT deduction.

**Happy Path:**
1. Vendor sends e-invoice (XML format per NĐ70/2025 + TT78/2021)
2. System validates:
   - GDT-issued invoice number (not duplicate)
   - Seller tax code valid
   - Buyer tax code matches enterprise
   - Invoice content valid (date, amount, VAT)
3. System creates AP invoice from e-invoice data
4. Input VAT registered for deduction (TK 133)
5. If payment > 20M VND: flag that bank transfer required for deduction

**Alternative Paths:**
- **A1 - E-invoice correction (TT78):** Vendor issues replacement e-invoice; system matches to original
- **A2 - E-invoice cancellation:** Reverse original AP invoice, remove VAT deduction

**Rules:**
- E-invoice must be stored in original XML format (legal requirement)
- Input VAT deduction requires: valid e-invoice + bank payment proof (≥ 20M VND) + goods receipt
- E-invoice import: auto-create AP invoice if PO match found
- E-invoice without PO: route to manual entry queue

---

### UC-AP-15: AP Reporting

**Description:** Standard AP reports.

**Reports:**
| Report | Content | Frequency | Regulatory |
|--------|---------|-----------|------------|
| AP Aging Detail | Vendor-level aging by invoice | Weekly | Internal |
| AP Aging Summary | Bucket totals by vendor | Monthly | BS footnote |
| AP Turnover (Vòng quay phải trả) | (Purchases / Avg AP) | Monthly | Internal |
| DPO | Days Payable Outstanding | Monthly | KPI |
| Cash Flow Forecast | Scheduled payments next 30/60/90 days | Weekly | Treasury |
| VAT Input Summary | Deductible input VAT by period | Monthly | VAT return |
| FCT Report | WHT amounts per foreign vendor | Quarterly | FCT declaration |
| AP Provision Report | Provision balance by vendor | Year-end | CIT filing |
| AP vs GL Reconciliation | Aging total vs GL 331 balance | Monthly | Audit |
| Vendor Statement | Monthly statement of account | Monthly | Vendor |
| Intercompany AP | IC transactions by entity | Monthly | Consolidation |
| AP by Currency | AP exposure in each currency | Monthly | FX risk |
| Purchase Invoice Register | All invoices in period | Monthly | Audit trail |
| Discount Capture | Discounts offered vs captured | Monthly | KPI |

---

## 6. Domain Entities

### 6.1 Vendor

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | Optional[int] | No | Auto PK |
| vendor_code | str | Yes | Unique, max 20 chars |
| vendor_name | str | Yes | Max 300 chars |
| legal_name | Optional[str] | No | For foreign vendors |
| tax_code | Optional[str] | Yes (VN) | 10/13 digit VN, 14 foreign |
| vendor_type | VendorType | Yes | INDIVIDUAL, ENTERPRISE, GOVERNMENT, FOREIGN |
| vendor_group | VendorGroup | Yes | DOMESTIC, IMPORT, VIP, GOVT |
| status | VendorStatus | Yes | ACTIVE, SUSPENDED, BLOCKED, ARCHIVED |
| email | Optional[str] | No | Contact email |
| phone | Optional[str] | No | Contact phone |
| address | Optional[str] | No | Registered address |
| city | Optional[str] | No | City |
| country | str | Yes | ISO 3166-1 alpha-3, default VN |
| contact_person | Optional[str] | No | |
| payment_terms | str | Yes | net_30, net_60, etc. |
| currency | str | Yes | ISO 4217, default VND |
| bank_name | Optional[str] | No | |
| bank_account | Optional[str] | No | |
| bank_swift | Optional[str] | No | For international transfers |
| credit_limit | Decimal | Yes | Default 0 |
| coa_code | Optional[str] | No | Default AP GL account (331) |
| foreign_ct_type | Optional[str] | No | FCT method: direct, deduction, hybrid |
| foreign_vat_rate | Optional[Decimal] | No | FCT VAT rate (0.02-0.05) |
| foreign_cit_rate | Optional[Decimal] | No | FCT CIT rate (0.01-0.10) |
| notes | Optional[str] | No | |
| created_at | datetime | Auto | |
| updated_at | Optional[datetime] | Auto | |

### 6.2 APInvoice

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | Optional[int] | No | Auto PK |
| invoice_number | str | Yes | Unique per vendor |
| vendor_id | int | Yes | FK → vendors |
| vendor_code | str | No | Denormalized |
| vendor_name | str | No | Denormalized |
| invoice_type | APInvoiceType | Yes | PO_BASED, NON_PO, PREPAYMENT |
| status | APInvoiceStatus | Yes | See state machine |
| invoice_date | date | Yes | |
| due_date | date | Yes | Calculated from terms |
| discount_date | Optional[date] | No | Early payment discount window |
| discount_percent | Optional[Decimal] | No | e.g., 0.02 for 2% |
| posted_date | Optional[date] | No | Date posted to GL |
| amount | Decimal | Yes | Total before tax |
| discount_amount | Decimal | Yes | Line discounts |
| tax_amount | Decimal | Yes | Input VAT |
| total_amount | Decimal | Yes | net + tax |
| paid_amount | Decimal | Yes | Cumulatively paid |
| written_off_amount | Decimal | Yes | Written off |
| balance_due | Decimal | Yes | total - paid - written_off |
| currency | str | Yes | ISO 4217 |
| fx_rate | Optional[Decimal] | No | Applied at invoice date |
| fx_gl_rate | Optional[Decimal] | No | Rate used for GL |
| po_number | Optional[str] | No | Reference PO |
| gr_number | Optional[str] | No | Reference GR |
| reference | Optional[str] | No | Vendor's reference |
| description | Optional[str] | No | |
| period | Optional[str] | No | YYYY-MM |
| coa_code | str | Yes | Default AP account 331 |
| created_by | Optional[str] | No | |
| approved_by | Optional[str] | No | |
| approved_at | Optional[datetime] | No | |
| created_at | datetime | Auto | |
| updated_at | Optional[datetime] | Auto | |

### 6.3 APInvoiceLine

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | Optional[int] | No | |
| ap_invoice_id | int | Yes | FK → ap_invoices |
| line_number | int | Yes | |
| description | str | Yes | |
| quantity | Decimal | Yes | |
| unit_price | Decimal | Yes | |
| line_amount | Decimal | Yes | |
| tax_rate | Decimal | Yes | Default 0.10 (10% VAT) |
| tax_amount | Decimal | Yes | |
| coa_code | Optional[str] | No | GL account for this line |
| po_line_number | Optional[int] | No | Link to PO line |
| gr_line_number | Optional[int] | No | Link to GR line |

### 6.4 APPayment

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | Optional[int] | No | |
| payment_number | str | Yes | Unique, auto-generated |
| vendor_id | int | Yes | FK |
| payment_date | date | Yes | |
| amount | Decimal | Yes | Total payment |
| discount_taken | Decimal | Yes | Early discount captured |
| net_amount | Decimal | Yes | amount - discount |
| payment_method | PaymentMethod | Yes | CASH, BANK_TRANSFER, CHEQUE, CARD |
| bank_account_id | Optional[int] | No | FK → bank_accounts |
| reference | Optional[str] | No | Bank reference |
| status | PaymentStatus | Yes | DRAFT, PROPOSED, APPROVED, EXECUTED, FAILED, CANCELLED |
| is_batch_payment | bool | No | Part of batch |
| batch_id | Optional[int] | No | FK → payment_batches |
| approval_by | Optional[str] | No | |
| approval_at | Optional[datetime] | No | |
| created_by | str | Yes | |
| created_at | datetime | Auto | |

### 6.5 APPaymentAllocation

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | Optional[int] | No | |
| ap_payment_id | int | Yes | FK |
| ap_invoice_id | int | Yes | FK |
| allocated_amount | Decimal | Yes | |
| is_adjustment | bool | No | For manual adjustments |
| created_at | datetime | Auto | |

### 6.6 VendorPrepayment

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | Optional[int] | No | |
| vendor_id | int | Yes | FK |
| amount | Decimal | Yes | |
| unapplied_balance | Decimal | Yes | |
| payment_date | date | Yes | |
| expected_invoice_date | Optional[date] | No | |
| reference | Optional[str] | No | |
| status | PrepaymentStatus | Yes | PENDING, APPLIED, CANCELLED |
| created_by | str | Yes | |
| created_at | datetime | Auto | |

### 6.7 APProvision

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | Optional[int] | No | |
| vendor_id | int | Yes | FK |
| period | str | Yes | YYYY-MM |
| provision_percent | Decimal | Yes | 0.30, 0.50, 0.70, 1.00 |
| overdue_days | int | Yes | |
| invoice_total | Decimal | Yes | Total overdue balance |
| provision_amount | Decimal | Yes | invoice_total * provision_percent |
| created_at | datetime | Auto | |

### 6.8 APInvoice Status State Machine

```
DRAFT → SUBMITTED → MATCHED → APPROVED → PAID_PARTIAL → PAID_FULL
   │         │          │          │            │
   └──── CANCELLED ─────┴─ REJECTED┴──── OVERDUE ┘
                      
WAITING_RECEIPT → (GR arrives → SUBMITTED)
                      
                        ┌────────────────┐
                        │      DRAFT     │
                        └────────┬───────┘
                                 │ submit
                        ┌────────▼───────┐
                        │   SUBMITTED    │
                        └────────┬───────┘
                           ┌─────┴──────┐
                     ┌─────▼────┐ ┌─────▼──────┐
                     │ MATCHED  │ │ WAITING_RC │ (awaiting goods receipt)
                     └─────┬────┘ └─────┬──────┘
                           │            │
                     ┌─────▼────┐       │
                     │ APPROVED │◄──────┘
                     └─────┬────┘
                           │
              ┌────────────┼────────────┐
      ┌──────▼──────┐ ┌───▼────┐ ┌─────▼──────┐
      │ PAID_PARTIAL │ │PAID_FUL│ │  OVERDUE   │
      └──────────────┘ └────────┘ └─────┬──────┘
                                        │
                                 ┌──────▼──────┐
                                 │  WRITTEN_OFF │
                                 └─────────────┘
```

### 6.9 Payment Status State Machine

```
DRAFT → PROPOSED → APPROVED → EXECUTING → EXECUTED → POSTED
  │         │           │           │          │
  └──CANCELLED┘          └──REJECTED┘          └──FAILED
```

---

## 7. Business Rules

### 7.1 Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| VR-01 | Invoice_number + vendor_id + invoice_date duplicate | Reject |
| VR-02 | vendor_id must reference ACTIVE vendor | Reject |
| VR-03 | PO_number format must match existing PO | Reject if PO required |
| VR-04 | Invoice date cannot be in future (max 5 days ahead) | Warn |
| VR-05 | Invoice date cannot be in closed period (per GL) | Block |
| VR-06 | Total = sum(lines) + tax - discount (tolerance 0.001) | Validate |
| VR-07 | VAT rate must be one of: 0, 5, 8, 10 (per VN law) | Validate |
| VR-08 | Payment amount cannot exceed invoice balance_due | Block |
| VR-09 | Prepayment amount cannot exceed credit_limit | Warn |
| VR-10 | Payment to BLOCKED vendor requires CFO override | Block |

### 7.2 Approval Rules

| Rule | Condition | Action |
|------|-----------|--------|
| AR-01 | Invoice with PO + 3-way match pass | Auto-approve (STP) |
| AR-02 | Invoice with PO + match price tol < 5% | Supervisor approve |
| AR-03 | Invoice with PO + match price tol ≥ 5% | Procurement re-approve |
| AR-04 | Invoice without PO | AP Manager approve |
| AR-05 | Non-PO invoice amount > 100M VND | CFO approve |
| AR-06 | Payment > 50M VND (single or batch) | Per DOA matrix |
| AR-07 | Vendor banking change | Dual approval required |
| AR-08 | Write-off request > 50M VND | CFO approve |
| AR-09 | Provision creation > 500M VND total | CFO approve |

### 7.3 Compliance Rules

| Rule | Condition | Action |
|------|-----------|--------|
| CR-01 | Payment ≥ 20M VND must be bank transfer (for VAT deduction) | Validate payment method |
| CR-02 | Foreign vendor must have FCT method configured | Block invoice if missing |
| CR-03 | FCT remittance within 20 days of payment | Reminder + auto-deadline calc |
| CR-04 | E-invoice must be stored in original XML | System archive |
| CR-05 | AP period must be open (GL period check) | Block posting |
| CR-06 | FX revaluation at period-end for all open FX items | Auto-trigger on period close |
| CR-07 | Provision review at year-end | Auto-reminder |
| CR-08 | AP aging snapshot before period close | Auto-reminder |

### 7.4 Accounting Rules

| Rule | Condition | Action |
|------|-----------|--------|
| AR-01 | AP Control (331) never posted via manual GL | System enforced |
| AR-02 | AP aging total = GL AP Control at month-end | Reconciliation |
| AR-03 | Rounding difference tolerance 0.001 VND | Auto-adjust to nearest |
| AR-04 | Prepayment balance > 0 at year-end | Classify as current asset |
| AR-05 | Credit note after payment creates AP debit | Require refund or offset |
| AR-06 | Discount captured posted to 515 (Financial Income) | Auto-posting |
| AR-07 | FX loss/gain posted to 635/515 | Auto-posting |
| AR-08 | Provision posted to 6422/229 | Auto-posting |

---

## 8. Data Flows

### 8.1 Purchase Invoice Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Vendor  │───▶│   PO     │───▶│   GR     │───▶│ Invoice  │───▶│ Payment  │
│  Master  │    │  (Purch) │    │(W/house) │    │  (AP)    │    │(Treasury)│
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │    GL Post   │
                                               │  Dr Inv/Exp  │
                                               │  Dr VAT      │
                                               │  Cr AP 331   │
                                               └──────────────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │ Aging Update │
                                               └──────────────┘
```

### 8.2 Payment Run Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐
│  Payment │───▶│ Proposal │───▶│Approval  │───▶│    Execute   │───▶│  GL Post │
│  Trigger │    │  (System) │   │(DOA)     │    │  (Bank File) │    │ Dr AP 331│
└──────────┘    └──────────┘    └──────────┘    └──────┬───────┘    │ Cr Bank  │
                                                        │           └──────────┘
                                                        ▼
                                                 ┌──────────────┐
                                                 │  Remittance  │
                                                 │  Advice sent │
                                                 └──────────────┘
```

### 8.3 FCT Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│  Invoice │───▶│   Calc   │───▶│  GL Post │───▶│  Payment to  │
│(Foreign) │    │  FCT     │    │   WHT    │    │  Vendor (net)│
└──────────┘    └──────────┘    └──────────┘    └──────┬───────┘
                                                        │ within 20 days
                                                        ▼
                                                 ┌──────────────┐
                                                 │  FCT Remit   │
                                                 │  to GDT      │
                                                 │  (thuedientu) │
                                                 └──────────────┘
```

---

## 9. Integration Points

### 9.1 Module Integrations

| Module | Integration | Direction | Key Data |
|--------|-------------|-----------|----------|
| **COA** | Account validation for AP GL accounts | AP→COA | Account codes, DCR direction |
| **GL** | Auto-post AP journals, period check | AP→GL | Journal entries, lines |
| **Cash** | Payment execution, bank transfer | AP→Cash | Payment orders, bank txns |
| **Tax** | VAT input deduction, FCT, E-invoice | AP↔Tax | VAT amounts, WHT, XML e-invoice |
| **AR** | Vendor cross-reference, netting | AP↔AR | Same-vendor AP/AR offset |
| **GL (Period)** | Period-gated posting | GL→AP | Period open/closed status |

### 9.2 External Integrations

| External System | Integration | Direction | Protocol |
|----------------|-------------|-----------|----------|
| **GDT eTax** | E-invoice validation, FCT submission | AP→GDT | REST API |
| **Bank** | Payment file upload, statement import | AP↔Bank | SFTP, API, NACHA |
| **Vendor** | Remittance advice, statement receipt | AP↔Vendor | Email, Portal |

---

## 10. API Endpoints

### 10.1 Vendors

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | /api/v1/ap/vendors | create_vendor | JWT |
| GET | /api/v1/ap/vendors | list_vendors | JWT |
| GET | /api/v1/ap/vendors/{id} | get_vendor | JWT |
| PUT | /api/v1/ap/vendors/{id} | update_vendor | JWT |
| DELETE | /api/v1/ap/vendors/{id} | delete_vendor | JWT |
| POST | /api/v1/ap/vendors/{id}/suspend | suspend_vendor | JWT |
| POST | /api/v1/ap/vendors/{id}/block | block_vendor | JWT |
| POST | /api/v1/ap/vendors/{id}/activate | activate_vendor | JWT |
| POST | /api/v1/ap/vendors/{id}/bank-change | request_bank_change | JWT+OTP |

### 10.2 Invoices

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | /api/v1/ap/invoices | create_invoice | JWT |
| GET | /api/v1/ap/invoices | list_invoices | JWT |
| GET | /api/v1/ap/invoices/{id} | get_invoice | JWT |
| POST | /api/v1/ap/invoices/{id}/approve | approve_invoice | JWT |
| POST | /api/v1/ap/invoices/{id}/cancel | cancel_invoice | JWT |
| POST | /api/v1/ap/invoices/{id}/hold | hold_invoice | JWT |
| POST | /api/v1/ap/invoices/{id}/release | release_invoice | JWT |

### 10.3 Debit/Credit Notes

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | /api/v1/ap/invoices/{id}/credit-note | create_credit_note | JWT |
| POST | /api/v1/ap/invoices/{id}/debit-note | create_debit_note | JWT |

### 10.4 Prepayments

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | /api/v1/ap/prepayments | create_prepayment | JWT |
| POST | /api/v1/ap/prepayments/{id}/apply | apply_prepayment | JWT |
| GET | /api/v1/ap/prepayments | list_prepayments | JWT |

### 10.5 Payments

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | /api/v1/ap/payments/proposal | create_proposal | JWT |
| GET | /api/v1/ap/payments/proposal/{id} | get_proposal | JWT |
| PUT | /api/v1/ap/payments/proposal/{id} | update_proposal | JWT |
| POST | /api/v1/ap/payments/proposal/{id}/approve | approve_proposal | JWT+Role |
| POST | /api/v1/ap/payments/proposal/{id}/execute | execute_proposal | JWT+Role |
| GET | /api/v1/ap/payments | list_payments | JWT |
| GET | /api/v1/ap/payments/{id} | get_payment | JWT |

### 10.6 Reports & Aging

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| GET | /api/v1/ap/aging | get_aging_report | JWT |
| POST | /api/v1/ap/aging/snapshot | create_snapshot | JWT |
| GET | /api/v1/ap/aging/snapshot/{period} | get_snapshot | JWT |
| POST | /api/v1/ap/provisions/calculate | create_provisions | JWT |
| GET | /api/v1/ap/provisions/{period} | get_provisions | JWT |
| GET | /api/v1/ap/reports/turnover | get_turnover | JWT |
| GET | /api/v1/ap/reports/dpo | get_dpo | JWT |
| GET | /api/v1/ap/reports/cash-forecast | get_cash_forecast | JWT |
| GET | /api/v1/ap/reports/vat-input | get_vat_input_summary | JWT+Tax |

### 10.7 FCT

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | /api/v1/ap/fct/calculate | calculate_fct | JWT |
| POST | /api/v1/ap/fct/remit | remit_fct | JWT+Tax |
| GET | /api/v1/ap/fct/declarations | list_fct_declarations | JWT+Tax |

### 10.8 Vendor Statement

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | /api/v1/ap/vendors/{id}/statements/import | import_statement | JWT |
| POST | /api/v1/ap/vendors/{id}/statements/{sid}/reconcile | reconcile_statement | JWT |
| GET | /api/v1/ap/vendors/{id}/statements | list_statements | JWT |

### 10.9 Intercompany

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | /api/v1/ap/intercompany/invoice | create_ic_invoice | JWT |
| POST | /api/v1/ap/intercompany/netting | create_netting | JWT+CFO |

---

## 11. Database Schema (Migration Plan)

### 11.1 New Tables

| Table | Entity | Key Columns | FKs |
|-------|--------|-------------|-----|
| vendors | Vendor | code, name, tax_code, type, status, terms, currency, fct_config | — |
| ap_invoices | APInvoice | invoice_number, vendor_id, type, status, amount, tax, total, due_date, currency, fx_rate | → vendors |
| ap_invoice_lines | APInvoiceLine | ap_invoice_id, line_number, desc, qty, price, amount, tax, coa_code | → ap_invoices |
| ap_credit_notes | CreditNote | original_invoice_id, reason, amount, tax_adjustment | → ap_invoices |
| ap_debit_notes | DebitNote | original_invoice_id, reason, amount | → ap_invoices |
| ap_prepayments | Prepayment | vendor_id, amount, unapplied, payment_date, status | → vendors |
| ap_prepayment_applications | PrepaymentApplication | prepayment_id, invoice_id, amount | → ap_prepayments, ap_invoices |
| ap_payments | APPayment | payment_number, vendor_id, date, amount, method, status, batch_id | → vendors |
| ap_payment_allocations | APPaymentAllocation | payment_id, invoice_id, amount | → ap_payments, ap_invoices |
| ap_payment_batches | PaymentBatch | batch_number, total, status, created_by, approved_by | — |
| ap_provisions | APProvision | vendor_id, period, overdue_days, rate, amount | → vendors |
| ap_aging_snapshots | ARAgingSnapshot (reuse AR pattern) | period, vendor_id, buckets, total | → vendors |
| ap_vendor_statements | VendorStatement | vendor_id, period, opening, closing, imported_at | → vendors |
| ap_fct_declarations | FCTDeclaration | vendor_id, period, invoice_id, fct_type, vat_amount, cit_amount, status | → vendors, ap_invoices |
| ap_intercompany_invoices | ICInvoice | from_entity, to_entity, invoice_number, amount, ic_account | — |

### 11.2 Migration Script

```python
# migration: 8a9b0c1d2e3f — AP tables
# Depends: 7d8e9f0a1b2c (cash tables)
```

### 11.3 Modified Tables

| Table | Change | Reason |
|-------|--------|--------|
| vendors | Reuse AR customer pattern or create separate | AP-only vendor |
| coa_models | No change needed | TK 331 already defined |
| gl_models | No change needed | Reuse JournalEntry |

---

## 12. Test Plan

### 12.1 Unit Tests (Domain)

| Test | Count | Focus |
|------|-------|-------|
| Vendor validation | 8 | tax_code, vendor_code, status transitions |
| APInvoice validation | 10 | amounts, dates, status transitions |
| Payment validation | 6 | amounts, status, approvals |
| FCT calculation | 8 | Direct, deduction, hybrid, gross-up |
| Provision calculation | 6 | Circular 48 rates, netting |
| FX revaluation | 4 | Gain/loss calculation |
| Total | 42 | |

### 12.2 Integration Tests (Repository + Use Cases)

| Test | Count | Focus |
|------|-------|-------|
| Vendor CRUD | 6 | Create, read, update, list, suspend, block |
| Invoice lifecycle | 8 | Create, match, approve, pay, cancel |
| PO matching | 4 | 2-way, 3-way, tolerance, exception |
| Credit/Debit notes | 4 | Create, apply, reverse |
| Prepayment | 4 | Create, apply, leftover, cancel |
| Payment run | 6 | Proposal, review, approve, execute |
| AP aging | 3 | Live, snapshot, snapshot closed |
| Provisions | 4 | Create, get, netting, year-end |
| FCT | 4 | Calculate, remit, gross-up, exempt |
| FX revaluation | 3 | Realized, unrealized, period-end |
| Vendor statement | 3 | Import, auto-match, discrepancy |
| GL posting | 4 | Invoice→GL, Payment→GL, FCT→GL, Provision→GL |
| Period gating | 2 | Open period OK, closed period blocked |
| i18n | 4 | Vietnamese error codes, English fallback |
| Total | 59 | |

### 12.3 Edge Case Tests

| Test | Count | Focus |
|------|-------|-------|
| Duplicate invoice number | 2 | Same vendor, diff vendor |
| Future invoice date | 2 | >5 days, ≤5 days |
| Zero-amount invoice | 1 | Reject |
| Overpayment | 2 | Small overpayment, large overpayment |
| Partial payment multiple | 2 | 3 partials, full at last |
| Discount capture timing | 2 | Within window, outside window |
| Prepayment > 90 days | 1 | Flag for review |
| Vendor blocked mid-process | 2 | Hold invoice, payment blocked |
| GR/invoice qty zero | 2 | Zero receipt, zero invoice line |
| FCT gross-up overflow | 1 | Combined rate > 100% |
| Currency rate zero | 1 | Rate = 0, use default |
| Period close mid-transaction | 1 | Block posting on closed |
| Bulk import errors | 2 | Row-level errors, partial success |
| Intercompany loop | 1 | A→B→C→A detection |
| Large payment > 5B VND | 2 | DOA escalation, board approval |
| Total | 25 | |

### 12.4 Total Test Count: ~126 tests

---

## 13. User Journeys

### 13.1 Journey: AP Clerk Processing Purchase Invoice

```
1. Receive email from vendor with PDF invoice attachment
2. Download PDF, open AP module, click "New Invoice"
3. Search vendor by code/name → auto-fill vendor details
4. Enter invoice_number, invoice_date, amount, lines
5. Enter PO_number → system auto-fills PO lines, prices
6. Upload PDF attachment (for audit trail)
7. Click "Submit" → system validates:
   - Duplicate check PASS
   - Vendor ACTIVE
   - PO match (3-way) AUTO-PASS
8. Invoice auto-approved (STP), GL posted
9. Status: APPROVED. Invoice due in 30 days.
10. Happy AP Clerk. Next invoice.
```

### 13.2 Journey: AP Manager Escalation Handling

```
1. Dashboard shows 3 invoices in exception queue
2. Invoice A: price tolerance 3.5% (Supervisor review)
   - Check PO price, vendor quote, approve
3. Invoice B: no PO reference, 75M VND
   - Check department budget, approve as non-PO
4. Invoice C: vendor blocked (tax code changed)
   - Investigate: vendor sent new tax registration
   - Update vendor tax_code → unblock → auto-approve
5. End of day: 3 invoices processed, 0 aged > 5 days
```

### 13.3 Journey: CFO Payment Run Approval

```
1. Weekly payment proposal lands in CFO's approval queue
2. Review total: 2.3B VND, 47 invoices, 23 vendors
3. Drill down: top 5 vendors by amount (1.8B = 78%)
4. Check cash balance: sufficient
5. Note: 2 invoices with early payment discount (+2.5M savings)
6. Approve with comment: "Proceed"
7. System auto-executes: generates NACHA file
8. Remittance advices emailed to all 23 vendors
9. GL posted: Dr AP Control 2.3B, Cr Bank 2.3B
10. CFO dashboard shows DPO improved 2 days vs last month
```

### 13.4 Journey: Treasury FCT Remittance

```
1. Monthly FCT report shows 4 foreign vendors due
2. Total FCT payable: 45M VND (VAT 15M + CIT 30M)
3. Check: all invoices verified, FCT rates correct
4. Generate FCT declaration XML for GDT
5. Upload to thuedientu.gdt.gov.vn via API
6. System records FCT submission, tracks payment deadline
7. Remit payment to State Budget (KBNN)
8. GL: Dr WHT Payable 45M, Cr Bank 45M
9. FCT status: REMITTED. Next remittance: 20 days
```

---

## 14. User Interface (Wireframe Specs)

### 14.1 Vendor List Page
```
┌─────────────────────────────────────────────────────────────┐
│ [Search vendors...] [Filter: Active ▾]  [+ New Vendor]      │
├──────┬──────────┬───────────┬────────┬──────────┬──────────┤
│ Code │   Name   │  Tax Code │ Status │   Terms  │ Balance  │
├──────┼──────────┼───────────┼────────┼──────────┼──────────┤
│ V001 │ ABC Co   │ 0123456789│ ACTIVE │ Net 30   │125,000,000│
│ V002 │ XYZ Ltd  │ (Foreign) │ ACTIVE │ Net 60   │ 45,000 USD│
│ V003 │ DEF JSC  │ 9876543210│BLOCKED │ Net 45   │ 12,300,000│
└──────┴──────────┴───────────┴────────┴──────────┴──────────┘
```

### 14.2 AP Invoice Entry
```
┌─────────────────────────────────────────────────────────────┐
│ [New Purchase Invoice]                                      │
│ Vendor: [_____________]    Invoice #: [____________]        │
│ Invoice Date: [__/__/____] Due Date: [auto-calc]           │
│ PO Reference: [___________]  GR Reference: [_________]      │
├─────────────────────────────────────────────────────────────┤
│ Lines:                                                      │
│ # │ Item        │ Qty      │ Price    │ VAT% │ Amount      │
│ 1 │ [_______]   │ [______] │ [______] │ [10] │ [auto]      │
│ 2 │ [_______]   │ [______] │ [______] │ [8]  │ [auto]      │
│ [+] Add Line                                                │
├─────────────────────────────────────────────────────────────┤
│ Subtotal: [auto]     VAT: [auto]      Total: [auto]        │
│ Currency: [VND ▾]      FX Rate: [auto if foreign]          │
│ Attachment: [Choose File] → invoice_123.pdf                │
│                                                             │
│ [Save as Draft]  [Submit]  [Cancel]                         │
└─────────────────────────────────────────────────────────────┘
```

### 14.3 AP Aging Report
```
┌─────────────────────────────────────────────────────────────┐
│ AP Aging Report — As of 30/06/2026                         │
│ [All Vendors ▾]  [VND ▾]  [Refresh] [Snapshot: Create ▾]   │
├──────────┬─────────┬────────┬────────┬────────┬────────────┤
│ Vendor   │ Current │ 1-30   │ 31-60  │ 61-90  │ 90+        │
├──────────┼─────────┼────────┼────────┼────────┼────────────┤
│ ABC Co   │ 50.0M   │ 75.0M  │ 25.0M  │  —     │  —         │
│ XYZ Ltd  │  —      │ 45.0K  │  —     │  —     │  —         │
│ ...      │         │        │        │        │            │
├──────────┼─────────┼────────┼────────┼────────┼────────────┤
│ Total    │ 850.0M  │ 320.0M │ 120.0M │ 45.0M  │ 12.0M     │
└──────────┴─────────┴────────┴────────┴────────┴────────────┘
```

---

## 15. Security & Audit

### 15.1 Audit Log

Every AP transaction must be audited:

| Event | Data Captured |
|-------|---------------|
| Vendor create/update | Who, what field, old value, new value, timestamp |
| Invoice create | Full invoice data, user, timestamp, IP |
| Invoice status change | From → to status, user, reason |
| Payment proposal | User, date, criteria, invoices included |
| Payment approval | Approver, date, decision, reason if rejected |
| Payment execution | User, date, bank file hash, GL entries |
| Banking change request | Dual approval records, old/new bank account |
| FCT calculation | Invoice, rates, calculation detail |
| Provision create | Vendor, period, rates, amount |
| FX revaluation | Rate source, rate, gain/loss per vendor |
| Vendor statement import | File hash, auto-match results, discrepancies |

### 15.2 Segregation of Duties

| Role | Can Create Vendor | Can Approve Invoice | Can Execute Payment | Can Reconcile |
|------|:---:|:---:|:---:|:---:|
| AP Clerk | ✓ | ✗ | ✗ | ✗ |
| AP Supervisor | ✓ | ✓ (<50M) | ✗ | ✗ |
| AP Manager | ✗ | ✓ (<500M) | ✓ (review only) | ✗ |
| CFO | ✗ | ✓ (>500M) | ✓ (approve) | ✗ |
| Treasury | ✗ | ✗ | ✓ (execute) | ✗ |
| Controller | ✗ | ✗ | ✗ | ✓ |

---

## 16. Implementation Plan

### Phase 1 (Core — 3 weeks)
- Domain entities: Vendor, APInvoice, APInvoiceLine, APPayment, APPaymentAllocation
- Repository: CRUD + query
- Use cases: UC-AP-01, UC-AP-02, UC-AP-05 (basic), UC-AP-11
- Routes: vendor CRUD, invoice CRUD, basic payment
- Tests: unit (vendor, invoice) + integration (CRUD)
- Migration: vendor + ap_invoice + ap_payment tables

### Phase 2 (Processing — 2 weeks)
- Debit/Credit notes (UC-AP-03)
- Prepayment (UC-AP-04)
- PO matching (2-way/3-way)
- Payment scheduling (UC-AP-06)
- Tests: matching, notes, prepayment

### Phase 3 (Reporting — 2 weeks)
- AP Aging (UC-AP-07)
- Provisions (UC-AP-08)
- GL auto-posting enhancement (UC-AP-11)
- Tests: aging, provisions, GL integration

### Phase 4 (Compliance — 2 weeks)
- FCT/WHT (UC-AP-09)
- Foreign currency (UC-AP-10)
- Purchase e-invoice (UC-AP-14)
- FCT declaration via GDT
- Tests: FCT, FX, e-invoice, i18n

### Phase 5 (Advanced — 2 weeks)
- Vendor statement reconciliation (UC-AP-12)
- Intercompany (UC-AP-13)
- AP reporting suite (UC-AP-15)
- Tests: statement, IC, reporting

### Total: 11 weeks → ~3 months

---

## 17. Appendix

### 17.1 Glossary

| Term | Definition |
|------|------------|
| AP | Accounts Payable — money owed to vendors/suppliers |
| PO | Purchase Order — procurement document |
| GR | Goods Receipt — warehouse confirms delivery |
| 2-way match | Invoice ↔ PO comparison |
| 3-way match | Invoice ↔ PO ↔ Goods Receipt comparison |
| GRNI | Goods Received Not Invoiced (accrual account, TK 3318) |
| FCT | Foreign Contractor Tax (WHT on payments to foreign vendors) |
| WHT | Withholding Tax |
| DPO | Days Payable Outstanding |
| STP | Straight-Through Processing (touchless auto-approve) |
| DOA | Delegation of Authority (approval matrix) |
| VND | Vietnamese Dong |
| GL | General Ledger |
| VAS | Vietnamese Accounting Standards |
| TT99/2025 | Thông tư 99/2025/TT-BTC — new accounting regime |
| TK 331 | Tài khoản 331 — Phải trả người bán |
| FCT | Foreign Contractor Tax (thuế nhà thầu nước ngoài) |
| IC | Intercompany |

### 17.2 Reference Documents

| Document | Source | Relevance |
|----------|--------|-----------|
| TT99/2025/TT-BTC | mof.gov.vn | Core accounting regime |
| TT200/2014/TT-BTC | mof.gov.vn | Full chart of accounts |
| TT133/2016/TT-BTC | mof.gov.vn | SME simplified |
| NĐ70/2025/NĐ-CP | mof.gov.vn | E-invoice mandate |
| NĐ123/2020/NĐ-CP | mof.gov.vn | E-invoice (predecessor) |
| TT78/2021/TT-BTC | mof.gov.vn | E-invoice implementation |
| Circular 103/2014 | mof.gov.vn | FCT regulation |
| Circular 86/2024 | mof.gov.vn | FCT update |
| Circular 69/2025 | mof.gov.vn | FCT further update |
| Circular 48/2019 | mof.gov.vn | Bad debt provisions |
| Circular 24/2022 | mof.gov.vn | Provision update |
| VAS Standards | vaa.net.vn | VAS framework |
| IFRS 9 | ifrs.org | Financial instruments |
| IAS 37 | ifrs.org | Provisions & contingencies |
