# Cash Management Module — BRD

**Version**: 1.0  
**Date**: 2026-06-29  
**Author**: BA Lead + Chief Accountant (reviewed)  
**Regulatory Basis**: Circular 133/2016/TT-BTC, Circular 99/2025/TT-BTC, VAS 01, VAS 24, IAS 7, Luat Ke toan 88/2015/QH13, ND 52/2024/ND-CP, ND 123/2020/ND-CP, COSO 2013  

---

## 1. PROD Readiness Assessment

**Verdict: NOT ready for production.**

| Layer | Status | Detail |
|-------|--------|--------|
| AccountType enum (CASH/BANK) | ✅ Done | `domain/__init__.py:72-73` |
| COA templates (111/112/113) | ✅ Done | `use_cases/coa_template_use_case.py` |
| DCR direction validation | ✅ Done | `use_cases/coa_validate_use_case.py` |
| Journal entry infra | ✅ Done | GL module — can post cash transactions |
| FinancialStatement cash_flow type | ⚠️ Skeleton | Type exists, NO cash flow logic |
| **Dedicated cash domain entities** | ❌ Missing | CashReceipt, CashPayment, PettyCash, BankAccount, BankReconciliation, CashTransfer, Cheque, CashForecast |
| **Cash SQLAlchemy models** | ❌ Missing | No `cash_models.py` |
| **Cash repository** | ❌ Missing | No `cash_repository.py` |
| **Cash use cases** | ❌ Missing | No `cash_use_cases.py` |
| **Cash routes** | ❌ Missing | No `cash_routes.py` |
| **Cash tests** | ❌ Missing | Zero dedicated tests |
| **Cash migrations** | ❌ Missing | No Alembic migrations |
| **Cash BRD** | ❌ Missing | This document fills gap |

**Why not PROD**: Cash management is high-risk (fraud, misstatement, regulatory penalty). Current code can post cash entries via GL but provides ZERO cash-specific controls: no Vietnamese voucher forms (Phieu thu/Phieu chi), no cashier/accountant segregation, no bank reconciliation, no daily cash count tracking, no imprest/petty cash, no cheque management, no cash forecasting, no internal control enforcement. Running this in PROD = unacceptable audit risk.

---

## 2. Executive Summary

Cash Management covers physical cash (111), demand deposits (112), and cash-in-transit (113). Vietnamese law (Luat Ke toan 2015 Die 39) mandates internal controls for cash. Circular 99/2025 (effective 2026) adds mandatory internal governance regulations. This module must enforce segregation of duties, Vietnamese voucher workflows, daily reconciliation, and full audit trail.

### Scope

| In Scope | Out of Scope (Phase 2) |
|----------|----------------------|
| Cash receipt/payment with Phieu thu/Phieu chi | Cash flow statement generation (VAS 24) |
| Petty cash (imprest fund) management | E-wallet integration (ND 52/2024) |
| Bank account master data | L/C (Letter of Credit) management |
| Bank statement import + reconciliation | Supply chain finance (ND 52/2024) |
| Cash transfer between accounts | Digital currency (intangible, not cash per IFRS) |
| Daily cash count + discrepancy handling | |
| Cheque register | |
| Cash book / bank book generation | |
| Payment approval workflow | |
| Audit trail for all cash movements | |

---

## 3. Regulatory References

| Regulation | Key Articles | Impact on Module |
|------------|-------------|------------------|
| TT 133/2016/TT-BTC (Dieu 12) | Cash accounting principles, Phieu thu/Phieu chi requirements | Mandates voucher forms, signatures, cash book |
| TT 99/2025/TT-BTC (Dieu 3, 11) | Internal governance, TK 112 renamed, IFRS alignment | Mandatory internal control charter; bank deposits renamed |
| VAS 01 | Accrual basis, historical cost, going concern | Cash transactions recorded at actual amount |
| VAS 24 | Cash flow statement (direct/indirect) | Cash flow analysis module must follow VAS 24 |
| Luat Ke toan 88/2015 (Dieu 39) | Internal control systems for accounting units | Segregation of duties must be enforced |
| ND 52/2024/ND-CP | Cashless payments, e-money, e-wallets | Payment integration standards |
| ND 123/2020/ND-CP | E-invoice regulations | Cash sales e-invoice linkage |
| IAS 7 / IFRS (reference) | Cash equivalents definition, cash flow classification | IFRS alignment for dual-reporting enterprises |

---

## 4. Use Cases

### UC-CASH-01: Create Cash Receipt (Phieu thu)

| Field | Value |
|-------|-------|
| **Actor** | Cashier (Thu quy) creates; Ke toan truong approves |
| **Trigger** | Cash received (sales, AR collection, bank withdrawal) |
| **Preconditions** | Cash account exists and is active; receipt type valid |
| **Postconditions** | Phieu thu generated; cash book updated; bank entry created (if from bank) |

**Happy Path**:
1. Cashier enters: date, payer name, amount (VNĐ + words), reason, account code (1111)
2. System generates Phieu thu number (auto-increment: PT-YYYYMM-NNNNN)
3. System validates amount > 0, account is CASH type, DCR debit
4. Cashier counts money, confirms receipt
5. System records: journal entry DR 1111 CR [counter-account]
6. Phieu thu printed with signatures (cashier, payer, KTT)
7. Cash book updated

**Alternative Paths**:
- **Foreign currency**: Record at actual exchange rate; DR 1112 (ngoai te) CR [counter-account], track FX rate
- **Cash from bank**: DR 1111 CR 1121 — requires bank withdrawal slip reference
- **Customer pays debt**: DR 1111 CR 131 — auto-references AR invoice
- **Over-the-counter sales with e-invoice**: DR 1111 CR 511, 3331 — triggers e-invoice issuance

**Validation Rules**:
- Amount must match Vietnamese currency precision (2 decimals)
- Amount in words must match amount in figures
- Counter-account must be valid non-cash account (cannot DR cash CR cash)
- Cannot create receipt for closed period
- Phieu thu numbers must be sequential, no gaps allowed per audit req

---

### UC-CASH-02: Create Cash Payment (Phieu chi) with Approval Workflow

| Field | Value |
|-------|-------|
| **Actor** | Requester → Approver → Cashier |
| **Trigger** | Payment request submitted |
| **Preconditions** | Requester authorized; budget available; cash balance sufficient; supporting docs attached |
| **Postconditions** | Phieu chi generated; cash book updated; GL posted; audit logged |

**Phieu chi lifecycle**: `draft → pending_approval → approved → paid → cancelled`

**Approval Matrix**:

| Amount Range | Approver Level |
|-------------|----------------|
| < 5M VND | Truong phong (Department head) |
| 5M - 50M VND | Giam doc (Director) |
| 50M - 500M VND | Hoi dong quan tri (Board) |
| > 500M VND | Shareholders (if required by charter) |

**Happy Path**:
1. Requester submits: payee, amount, purpose, supporting docs
2. System routes to approver based on amount + department (escalation for > 20M VND recommends electronic payment per ND 52/2024)
3. Approver reviews, approves (electronic signature per ND 130/2018)
4. System generates Phieu chi in `pending_approval` status
5. Cashier creates Phieu chi: date, receiver, amount, reason, account
6. System validates: sufficient balance, account is CASH debit-normal
7. Cashier disburses, recipient signs
8. System records: DR [counter-account] CR 1111, Phieu chi status → `paid`
9. Phieu chi printed with signatures (requester, approver, cashier)

**Alternative Paths**:
- **Petty cash replenishment**: DR 141 (advance to employee) CR 1111 — requires advance settlement first
- **Salary payment**: DR 334 CR 1111 — batch processing for multiple employees
- **Large payment > 20M VND**: System warning — recommend electronic payment per ND 52/2024
- **Cash shortage on payment**: DR 1381 (asset shortage) / DR 642 (expense) — discrepancy handling
- **Rejection**: Requester notified with reason; can resubmit
- **Delegation**: Approver delegates to deputy (logged)
- **Urgent payment**: Bypass workflow with director override (audit-logged)
- **Recurring payment**: Pre-approved template (rent, utilities)

**Validation Rules**:
- Cash balance must be sufficient (cannot go negative per VAS)
- Payment > threshold requires dual approval
- Supporting document reference mandatory
- Cannot pay to same party without proper invoice
- Segregation: Requester ≠ Approver ≠ Cashier
- Payment to blocked vendor rejected
- Duplicate payment detection (same invoice, same amount, same payee)
- Electronic signatures valid per ND 130/2018

---

### UC-CASH-03a: Advance Management (Tam ung — TK 141)

| Field | Value |
|-------|-------|
| **Actor** | Employee requests; KTT approves; Cashier disburses |
| **Trigger** | Employee needs advance for business trip, purchase, etc. |
| **Preconditions** | Employee exists in system; no outstanding unsettled advance (except director override) |
| **Postconditions** | Advance recorded in TK 141; Phieu chi generated; settlement tracked |

**Happy Path**:
1. Employee submits advance request: purpose, amount, expected settlement date
2. KTT approves (escalation for > 20M VND)
3. Phieu chi created: DR 141 (employee) CR 1111
4. Employee receives cash
5. Settlement submitted (receipts + Phieu thanh toan tam ung):
   - Full settlement: DR [expense accounts] CR 141
   - With remainder return: DR [expense] + DR 1111 CR 141
6. Remaining balance updated

**Validation Rules**:
- Maximum outstanding advance per employee (configurable, default 50M VND)
- Settlement deadline 30 days (configurable)
- No new advance until previous settled (except director override)
- Individual tracking per employee (not pooled)

### UC-CASH-03b: Petty Cash Imprest Fund

| Field | Value |
|-------|-------|
| **Actor** | Petty cash custodian (Thu quy nho) |
| **Trigger** | Establish imprest fund; replenishment request |
| **Preconditions** | Fund limit approved by director; custodian assigned |
| **Postconditions** | Fund balance updated; replenishment cycle maintained |

**Happy Path (Establish)**:
1. Director approves petty cash limit (e.g., 10M VND)
2. Phieu chi created: DR 1111 CR 1121 (transfer from bank) or DR [expense] CR 1111
3. Custodian receives cash, recorded in So quy tam ung (Petty Cash Book)

**Happy Path (Replenish)**:
1. Custodian submits receipts for small expenses
2. Accountant reviews: receipts valid, amounts match, business purpose approved
3. Replenishment Phieu chi created: DR [expense accounts] CR 1111
4. Fund restored to imprest level

**Validation Rules**:
- Fund cannot exceed approved limit
- Custodian personally liable for fund balance
- Surprise count at least once per month

---

### UC-CASH-04: Bank Account Management

| Field | Value |
|-------|-------|
| **Actor** | Accountant (Ke toan cong no) |
| **Trigger** | Open/close/change bank account |
| **Preconditions** | Bank account exists physically |
| **Postconditions** | Bank account master updated; COA 112 sub-accounts created |

**Happy Path**:
1. User creates bank account: bank name, branch, account number, currency, account holder
2. System auto-creates COA sub-account (1121 for VND, 1122 for foreign currency)
3. System records in So chi tiet tien gui NH (Bank Detail Book)
4. Account activated for transactions

**Fields**:
- Bank name + branch (Tieng Viet + Tieng Anh)
- Account number (so tai khoan)
- Account holder (chu tai khoan)
- Currency (VND/USD/EUR/JPY/GBP)
- SWIFT code
- IBAN (if applicable)
- E-banking URL / API endpoint
- Signatory list (nhuong quyen ky)
- Opening balance
- Status (active/closed/blocked)
- Authorization limit per transaction

**Validation Rules**:
- Account number must be unique per bank
- Cannot delete bank account with transaction history (soft-delete)
- Currency must match account owner tax registration

---

### UC-CASH-05: Bank Statement Import

| Field | Value |
|-------|-------|
| **Actor** | Accountant (system-assisted) |
| **Trigger** | Monthly bank statement received |
| **Preconditions** | Bank account exists in system |
| **Postconditions** | Bank transactions imported; matching ready |

**Happy Path**:
1. Download sao ke (bank statement) from e-banking portal
2. Import file (MT940/SWIFT/CSV/PDF-parsed)
3. System maps fields: date, amount, reference, description, balance
4. Validates: file not duplicate (by statement date + account), amounts match running balance
5. Stores imported transactions in `bank_transactions` table
6. Flags transactions already matched to GL entries (by reference number)

**Supported Formats**:
- MT940 (SWIFT) — international standard
- CSV/Excel — common Vietnam bank format
- PDF — OCR fallback (Phase 2)
- Open API — direct bank API integration (Phase 2)

**Validation Rules**:
- Duplicate import detection by statement date, bank account, opening/closing balance
- Running balance check: opening + sum(is_debit ? -amount : amount) = closing
- Currency matches bank account currency
- Statement period must align with accounting period

---

### UC-CASH-06: Bank Reconciliation (Bang doi chieu tien gui NH)

| Field | Value |
|-------|-------|
| **Actor** | Accountant; reviewed by KTT |
| **Trigger** | Monthly close or on-demand |
| **Preconditions** | Entries posted; bank statement imported |
| **Postconditions** | Reconciliation report generated; discrepancies resolved |

**Happy Path**:
1. System presents two sides:
   - **Book side**: GL entries for 112 (grouped by date/reference)
   - **Bank side**: Imported bank statement lines
2. Automatic matching by: amount + reference number + date (within 3 days)
3. Matched items shown as "Da doi chieu" (Reconciled)
4. Unmatched items shown as "Chua doi chieu":
   - **Deposits in transit**: recorded in GL, not yet in bank
   - **Outstanding checks**: recorded in GL, not yet cleared
   - **Bank charges/interest**: in bank statement, not yet in GL
   - **Errors**: discrepancies requiring investigation
5. Accountant reviews unmatched, creates adjustment entries:
   - Bank charges: DR 642 CR 1121
   - Bank interest: DR 1121 CR 515
   - Unidentified deposits: DR 1121 CR 3387
   - Unidentified debits: DR 1388 CR 1121
6. Both sides balance after adjustments
7. KTT reviews and signs Bang doi chieu

**Alternative Paths**:
- **Force reconcile**: With unreconciled items (requires reason, audit-logged)
- **Partial reconcile**: Reconcile subset of transactions, leave others for next period
- **Auto-adjust**: System creates adjustment entries from bank-only items (configurable)

**Validation Rules**:
- Mandatory monthly reconciliation per TT 133/2016 + TT 99/2025
- Cannot close month if bank not reconciled (configurable)
- Cumulative unreconciled items > 30 days flagged to KTT
- Adjusted balance must equal bank statement closing balance

---

### UC-CASH-07: Cash Transfer (Chuyen tien giua cac tai khoan)

| Field | Value |
|-------|-------|
| **Actor** | Cashier/Accountant; dual approval |
| **Trigger** | Transfer between cash-bank or bank-bank |
| **Preconditions** | Source account has sufficient balance |
| **Postconditions** | Both accounts updated; GL entries created |

**Happy Path (Cash to Bank — deposit)**:
1. User creates transfer: source 1111, destination 1121, amount
2. System records: DR 1121 CR 1111 (Chuyen tien gui vao NH)
3. Phieu chi for cash disbursement
4. Destination bank entry pending confirmation (113 — Tien dang chuyen)

**Happy Path (Bank to Cash — withdrawal)**:
1. User creates transfer: source 1121, destination 1111, amount
2. System records: DR 1111 CR 1121 (Rut tien NH ve quy)
3. Requires bank withdrawal slip reference
4. Cash receipt recorded

**Happy Path (Bank to Bank)**:
1. Source bank account debited
2. Destination bank credited
3. Transit time tracked via 113 (Tien dang chuyen) if inter-bank

**Validation Rules**:
- Source != destination (no self-transfer)
- Amount > 0
- Currency conversion handled if different (FX rate at transaction date)
- Dual approval for amount > threshold (configurable)
- In-transit flag cleared when destination confirms receipt

---

### UC-CASH-08: Daily Cash Count (Kiem ke quy)

| Field | Value |
|-------|-------|
| **Actor** | Thu quy (Cashier) daily; KTT surprise monthly |
| **Trigger** | End of working day |
| **Preconditions** | All Phieu thu/Phieu chi recorded |
| **Postconditions** | Cash count report generated; discrepancies handled |

**Happy Path**:
1. Cashier counts physical cash by denomination
2. System shows expected balance (GL balance for 1111)
3. Cashier enters actual count per currency
4. System compares:
   - Actual = Expected → "Phu hop" (Match)
   - Actual > Expected → Thua quy (Surplus) → handled via 3381
   - Actual < Expected → Thieu quy (Shortage) → handled via 1381
5. Cashier prints Bien ban kiem ke quy (Cash Count Report)
6. KTT reviews and signs

**Surplus/Shortage Resolution**:
| Scenario | Entry | |
|----------|-------|-|
| Surplus (unidentified) | DR 1111 CR 3381 | Tai san thua cho giai quyet |
| Shortage (unidentified) | DR 1381 CR 1111 | Tai san thieu cho xu ly |
| Employee compensates | DR 1388/334 CR 1381 | |
| Write-off as expense | DR 642 CR 1381 | |
| Surplus becomes income | DR 3381 CR 711 | |

**Validation Rules**:
- Daily count mandatory per VAS
- Surprise count at least once per month
- Cashier cannot override system expected balance
- Discrepancy > 1% of total cash requires immediate KTT notification
- Repeated discrepancies (> 3 per month) trigger audit alert

---

---

### UC-CASH-10: Cheque Management (So theo doi sec)

| Field | Value |
|-------|-------|
| **Actor** | Accountant |
| **Trigger** | Cheque issued/received/cancelled/cleared |
| **Preconditions** | Cheque book registered |
| **Postconditions** | Cheque status tracked; bank statement matched |

**Happy Path (Cheque Issued)**:
1. Register cheque book from bank (cheque numbers range)
2. Issue cheque: payee, amount, date, cheque number
3. System records: DR [expense/payable] CR 1121 (when cheque issued or when cleared)
4. Cheque status = "Issued" (Da phat hanh)

**Happy Path (Cheque Cleared)**:
1. Bank statement shows cheque cleared
2. System matches by cheque number + amount + bank account
3. Status = "Cleared" (Da thanh toan)
4. No further action needed

**Cheque Status Lifecycle**:
```
NEW → ISSUED → CLEARED
  → CANCELLED (if lost/damaged)
  → STOPPED (payment stop order)
  → BOUNCED (insufficient funds — DSB)
```

**Validation Rules**:
- Cheque numbers must be sequential within cheque book
- Cannot issue cheque for amount > account balance
- Cheque issued > 6 months uncleared flagged for stale cheque
- Lost cheque requires immediate stop payment + police report reference

---

### UC-CASH-11: Cash Book / Bank Book Generation (So quy / So NH)

| Field | Value |
|-------|-------|
| **Actor** | Any user (view) |
| **Trigger** | Period-end report; on-demand |
| **Preconditions** | Cash/bank transactions recorded |
| **Postconditions** | Report generated (PDF/Excel/CSV) |

**Cash Book (So quy tien mat)** columns:
- Date, Phieu thu/chi number, explanation, account code
- Debit (Thu), Credit (Chi), Balance (Ton quy)
- Running balance after each entry

**Bank Book (So tien gui NH)** columns:
- Date, reference, bank code, explanation
- Debit (Gui vao), Credit (Rut ra), Balance
- Bank running balance

**Report Formats**:
- Daily: So quy chi tiet
- Monthly: So quy tong hop
- Excel export for KTT review
- PDF for audit

**Validation Rules**:
- Running balance must never go below 0 for cash accounts
- Bank book running balance reflects GL, not bank statement balance
- Foreign currency books maintained separately per TT 133/2016

---

### UC-CASH-12: Cash Forecast (Du bao dong tien)

| Field | Value |
|-------|-------|
| **Actor** | CFO / Chief Accountant |
| **Trigger** | Weekly/monthly planning |
| **Preconditions** | Historical cash data available |
| **Postconditions** | Forecast generated; alerts configured |

**Happy Path**:
1. User selects forecast period (7/14/30/90 days)
2. System computes from:
   - AR aging → expected inflows
   - AP aging → expected outflows
   - Salary schedule
   - Tax payment calendar (from Tax Module)
   - Historical patterns (same period last month/year)
3. System projects daily cash balance
4. Alerts if minimum threshold breached
5. User can adjust assumptions (what-if scenarios)

**Output**:
- Daily cash position chart
- Weekly rolling forecast
- Cash budget vs actual variance analysis
- Liquidity ratios: current ratio, quick ratio, cash ratio

**Validation Rules**:
- Historical data minimum 3 months for meaningful forecast
- Forecast tagged with version (actual/committed/projected)
- Alert threshold configurable per account

---

## 5. Data Model

### Domain Entities (domain/__init__.py — new)

```python
class CashReceiptType(str, Enum):
    SALES = "sales"              # Thu ban hang
    COLLECTION = "collection"    # Thu cong no
    BANK_WITHDRAWAL = "bank_withdrawal"  # Rut tien NH
    ADVANCE_RETURN = "advance_return"    # Thu hoi tam ung
    OTHER = "other"              # Thu khac

class CashPaymentType(str, Enum):
    EXPENSE = "expense"          # Chi phi
    PURCHASE = "purchase"        # Mua hang
    SALARY = "salary"            # Luong
    ADVANCE = "advance"          # Tam ung
    BANK_DEPOSIT = "bank_deposit"  # Gui tien NH
    OTHER = "other"              # Chi khac

class CashReceipt(BaseModel):
    receipt_number: str        # PT-YYYYMM-NNNNN
    receipt_date: date
    receipt_type: CashReceiptType
    payer_name: str
    amount: Decimal
    amount_in_words: str
    currency: str = "VND"
    fx_rate: Optional[Decimal] = None
    account_code: str          # 1111 or 1112
    counter_account: str
    reference_number: Optional[str]  # Invoice/contract ref
    description: str
    status: str = "draft"     # draft/pending/posted/cancelled
    created_by: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]

class CashPayment(BaseModel):
    payment_number: str        # PC-YYYYMM-NNNNN
    payment_date: date
    payment_type: CashPaymentType
    receiver_name: str
    amount: Decimal
    amount_in_words: str
    currency: str = "VND"
    fx_rate: Optional[Decimal] = None
    account_code: str          # 1111 or 1112
    counter_account: str
    reference_number: Optional[str]
    description: str
    status: str = "draft"
    created_by: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]

class BankAccount(BaseModel):
    bank_name: str
    branch: str
    account_number: str
    account_holder: str
    currency: str = "VND"
    coa_code: str              # 1121 or 1122
    swift_code: Optional[str]
    iban: Optional[str]
    opening_balance: Decimal = Decimal("0")
    status: str = "active"
    signatories: List[str]     # Nguoi duoc uy quyen ky

class BankTransaction(BaseModel):
    bank_account_id: int
    transaction_date: date
    value_date: Optional[date]
    amount: Decimal
    is_debit: bool             # True = giam so du (withdrawal)
    reference: str             # Bank reference number
    description: str
    matched_entry_id: Optional[int]  # Link to JournalEntry
    statement_id: int          # Link to bank statement

class BankStatement(BaseModel):
    bank_account_id: int
    statement_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    transactions: List[BankTransaction]
    imported_at: datetime
    source: str                # mt940/csv/pdf/api

class ReconciliationDiscrepancy(BaseModel):
    reconciliation_id: int
    discrepancy_type: ReconciliationDiscrepancyType
    amount: Decimal
    entry_side: str                     # book/bank
    reference: Optional[str]
    description: Optional[str]
    status: str = "unresolved"
    resolution_entry_id: Optional[int]

class BankReconciliation(BaseModel):
    bank_account_id: int
    period: str                # YYYY-MM
    book_balance: Decimal
    bank_balance: Decimal
    deposits_in_transit: Decimal = Decimal("0")
    outstanding_checks: Decimal = Decimal("0")
    unrecorded_credits: Decimal = Decimal("0")
    unrecorded_debits: Decimal = Decimal("0")
    adjusted_book_balance: Decimal
    adjusted_bank_balance: Decimal
    is_balanced: bool
    reconciled_at: Optional[datetime]
    reconciled_by: Optional[str]
    discrepancies: List[ReconciliationDiscrepancy]

class PettyCashFund(BaseModel):
    fund_code: str
    custodian: str
    limit_amount: Decimal
    current_balance: Decimal
    currency: str = "VND"
    established_date: date
    status: str = "active"

class CashTransfer(BaseModel):
    source_account: str
    destination_account: str
    amount: Decimal
    transfer_date: date
    fx_rate: Optional[Decimal]
    reference: str
    status: str = "pending"    # pending/in_transit/completed

class Cheque(BaseModel):
    cheque_number: str
    cheque_book_id: int
    payee: str
    amount: Decimal
    issue_date: date
    status: str = "new"        # new/issued/cleared/cancelled/stopped/bounced
    bank_account_id: int

class ChequeBook(BaseModel):
    bank_account_id: int
    start_number: str
    end_number: str
    issued_date: date
    status: str = "active"

class DailyCashCount(BaseModel):
    count_date: date
    account_code: str
    expected_balance: Decimal
    actual_balance: Decimal
    difference: Decimal = Decimal("0")
    denomination_breakdown: Dict[str, int] = {}
    notes: Optional[str]
    counted_by: str
    witnessed_by: Optional[str]

class Advance(BaseModel):
    """TK 141 — Tam ung (advance to individual employee)"""
    employee_name: str
    employee_id: str
    amount: Decimal
    advance_date: date
    purpose: str
    settlement_deadline: date
    settlement_amount: Decimal = Decimal("0")
    remaining_balance: Decimal
    status: str = "outstanding"
```

### SQLAlchemy Models (infrastructure/models/cash_models.py — new)

Tables: `cash_receipts`, `cash_payments`, `bank_accounts`, `bank_statements`, `bank_transactions`, `bank_reconciliations`, `reconciliation_discrepancies`, `petty_cash_funds`, `petty_cash_transactions`, `cash_transfers`, `cheque_books`, `cheques`, `cash_forecasts`, `cash_forecast_lines`, `daily_cash_counts`, `advances`.

### Key Relationships

```
BankAccount 1─N BankStatement 1─N BankTransaction
BankAccount 1─N BankReconciliation
BankReconciliation 1─N ReconciliationDiscrepancy
CashReceipt/CashPayment N─1 JournalEntry (via reference)
ChequeBook 1─N Cheque N─1 BankAccount
PettyCashFund 1─N PettyCashTransaction
```

---

## 6. API Endpoints

| Method | Endpoint | UC |
|--------|----------|----|
| POST | /api/v1/cash/receipts | UC-CASH-01 |
| GET | /api/v1/cash/receipts | List receipts |
| GET | /api/v1/cash/receipts/{id} | Get receipt |
| PATCH | /api/v1/cash/receipts/{id} | Update receipt (if draft) |
| DELETE | /api/v1/cash/receipts/{id} | Cancel receipt |
| POST | /api/v1/cash/payments | UC-CASH-02 |
| GET | /api/v1/cash/payments | List payments |
| GET | /api/v1/cash/payments/{id} | Get payment |
| POST | /api/v1/cash/transfers | UC-CASH-07 |
| POST | /api/v1/cash/petty-cash | UC-CASH-03b |
| GET | /api/v1/cash/petty-cash/{id} | Get fund |
| POST | /api/v1/cash/advances | UC-CASH-03a |
| GET | /api/v1/cash/advances/{id} | Get advance |
| GET | /api/v1/cash/advances/{id}/settle | Settle advance |
| POST | /api/v1/cash/daily-count | UC-CASH-08 |
| GET | /api/v1/cash/reports/cash-book | UC-CASH-11 |
| GET | /api/v1/cash/reports/bank-book | UC-CASH-11 |
| POST | /api/v1/cash/bank-accounts | UC-CASH-04 |
| GET | /api/v1/cash/bank-accounts | List bank accounts |
| POST | /api/v1/cash/bank-statements/import | UC-CASH-05 |
| GET | /api/v1/cash/bank-statements/{id} | Get statement |
| POST | /api/v1/cash/reconciliations | UC-CASH-06 |
| GET | /api/v1/cash/reconciliations/{id} | Get reconciliation |
| GET | /api/v1/cash/reconciliations/{id}/report | Export report |
| POST | /api/v1/cash/cheques | UC-CASH-10 |
| GET | /api/v1/cash/forecasts | UC-CASH-12 |
| POST | /api/v1/cash/advances/{id}/settle | Settle advance |

---

## 7. Workflows (Text Diagrams)

### Cash Receipt Workflow

```
[Customer/AR] → Phieu thu request → [Cashier counts] → [System posts GL]
      │                                                │
      └── Payer signs PT ◄────────────────────────────┘
                          │
                          ▼
                    [Cash book updated]
                          │
                          ▼
                    [E-invoice issued] (if sales)
```

### Cash Payment Workflow

```
[Requester] → Phieu chi request → [Approver] → [Cashier disburses]
      │                              │               │
      └── Supporting docs ──────────┘               │
                                                     │
                              [Receiver signs PC] ◄──┘
                                          │
                                          ▼
                                    [Cash book updated]
```

### Bank Reconciliation Workflow

```
[Bank portal] ──→ [Export sao ke] ──→ [Import to system]
                                            │
                                            ▼
                                   [Auto-match with GL]
                                            │
                                    ┌───────┴────────┐
                                    ▼                ▼
                              [Matched]       [Unmatched]
                                                    │
                                          ┌─────────┴──────────┐
                                          ▼                    ▼
                                     [Deposits in      [Bank charges/
                                      transit]          interest]
                                     [Outstanding
                                      checks]
                                          │                    │
                                          ▼                    ▼
                                    [Clear next     [Create adjustment
                                     period]         entries]
                                                    │
                                                    ▼
                                          [Reconcile report]
                                                    │
                                                    ▼
                                          [KTT reviews + signs]
```

---

## 8. Validation Rules Summary

### Structure Rules
- `receipt_number` / `payment_number` format: `(PT|PC)-YYYYMM-NNNNN`
- Amount in words must match figures
- Amount > 0 for all transactions
- Currency default VND; foreign currency requires FX rate
- Counter-account cannot be same as account (no cash-to-cash)

### Balance Rules
- Cash balance must be >= 0 (no negative cash per VAS)
- Bank reconciliation required monthly per TT 133/2016
- Petty cash fund cannot exceed approved limit
- Outstanding cheque > 6 months flagged stale

### Approval Rules
- Segregation: Requester ≠ Approver ≠ Cashier
- Dual approval for > 20M VND (electronic payment recommended)
- Director approval for > 50M VND
- Urgent bypass requires audit record

### Audit Rules
- All voucher numbers sequential, no gaps
- System timestamp for all status changes
- Cannot modify posted receipt/payment (reverse instead)
- Audit log for: create, approve, pay, cancel, reverse

---

## 9. Segregation of Duties Matrix

| Function | Cashier | Cash Accountant | KTT | Director |
|----------|---------|----------------|-----|----------|
| Handle physical cash | ✅ Execute | ❌ | ❌ | ❌ |
| Record cash transactions | ❌ | ✅ Record | ✅ Review | ❌ |
| Approve payments < 5M | ❌ | ❌ | ✅ | ❌ |
| Approve payments 5-50M | ❌ | ❌ | ✅ | ✅ |
| Count cash daily | ✅ Execute | ✅ Witness | ❌ | ❌ |
| Reconcile bank | ❌ | ✅ Execute | ✅ Review | ❌ |
| Surprise cash count | ❌ | ❌ | ✅ Initiate | ✅ Approve |
| Sign cheques | ❌ | ❌ | ✅ (co-sign) | ✅ (co-sign) |
| Access accounting system | ❌ | ✅ | ✅ | ✅ (view) |

---

## 10. Integration Points

| Integration | Direction | Purpose |
|-------------|-----------|---------|
| GL Module | Read/Write | Post cash/bank journal entries; read period status |
| COA Module | Read | Validate account codes; get DCR direction |
| Tax Module | Read | Tax payment calendar for cash forecasting |
| AR Module (future) | Read | Customer payments, AR aging for forecast |
| AP Module (future) | Read | Vendor payments, AP aging for forecast |
| E-Invoice (existing stub) | Write | Trigger e-invoice on cash sales |
| Bank API (external) | Read | Auto-import bank statements |
| E-Signature (external) | Verify | Payment approval signing |

---

## 11. Gap Analysis (Current vs Target)

| # | Feature | Priority | Complexity | Current State |
|---|---------|----------|------------|---------------|
| 1 | Cash receipt w/ Phieu thu | P0 | M | ❌ |
| 2 | Cash payment w/ Phieu chi | P0 | M | ❌ |
| 3 | Daily cash count + discrepancy | P0 | S | ❌ |
| 4 | Bank account master data | P0 | S | ❌ |
| 5 | Bank statement import (CSV) | P0 | M | ❌ |
| 6 | Bank reconciliation | P0 | L | ❌ |
| 7 | Cash book / bank book reports | P1 | S | ❌ |
| 8 | Petty cash / advance management | P1 | M | ❌ |
| 9 | Cash transfer (cash↔bank) | P1 | S | ❌ |
| 10 | Payment approval workflow (folded into UC-CASH-02) | P0 | M | ❌ |
| 11 | Cheque register | P1 | M | ❌ |
| 12 | Cash forecasting | P2 | L | ❌ |
| 13 | MT940/SWIFT bank import | P2 | M | ❌ |
| 14 | Direct bank API integration | P3 | L | ❌ |
| 15 | Cash flow statement (VAS 24) | P3 | L | ⚠️ Skeleton |

---

## 12. Implementation Plan

### Phase 1 (P0 — Must Have)
1. Domain entities: all cash entities (CashReceipt, CashPayment, BankAccount, BankReconciliation, ReconciliationDiscrepancy, PettyCashFund, CashTransfer, Cheque, DailyCashCount, Advance, etc.)
2. SQLAlchemy models: cash_receipts, cash_payments, bank_accounts, bank_reconciliations, bank_statements, bank_transactions, petty_cash_funds, cash_transfers, cheques, cheque_books, daily_cash_counts, advances
3. Repository: CRUD for all cash entities
4. Use cases: create_receipt, create_payment, reconcile_bank, manage_bank_account, import_statement, petty_cash, advance, transfer, daily_count, cheque
5. Routes: /api/v1/cash/receipts, /api/v1/cash/payments, /api/v1/cash/bank-accounts, /api/v1/cash/bank-statements, /api/v1/cash/reconciliations, /api/v1/cash/transfers, /api/v1/cash/petty-cash, /api/v1/cash/advances, /api/v1/cash/daily-count, /api/v1/cash/cheques
6. Tests: 30+ integration tests
7. Migration: Alembic for cash tables

### Phase 2 (P1 — Should Have)
1. Cash book / bank book reports (Excel/PDF)
2. Cash forecasting with AR/AP integration
3. Cheque register remaining features

### Phase 3 (P2/P3 — Nice to Have)
1. MT940 bank import + Direct bank API
2. Cash flow statement (VAS 24)

### Phase 3 (P2/P3 — Nice to Have)
1. Cash forecasting with AR/AP integration
2. MT940 bank import + Direct bank API
3. Cash flow statement (VAS 24)

---

## 13. Success Criteria

1. All P0 use cases implemented and tested (30+ tests)
2. All 268 existing tests still pass
3. Bank reconciliation: match auto-rate > 80% for same-bank transactions
4. Cash book balances match GL 1111 balance within 0.001 VND
5. Audit trail captured for all cash operations
6. All Vietnamese voucher forms printable (Phieu thu, Phieu chi, Bien ban kiem ke quy)
7. API endpoints return consistent error format matching existing codebase pattern
