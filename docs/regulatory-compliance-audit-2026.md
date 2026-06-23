# Regulatory Compliance Audit & Gap Analysis — 2026

> **Author:** BA Lead (20k hrs) + Chief Accountant (20k hrs)
> **Date:** 2026-06-23
> **Context:** smart_acct rewrite to NestJS + Prisma + MariaDB

---

## 1. REGULATORY LANDSCAPE — LATEST STATUS

### 1.1 Accounting Regime

| Regulation | Status | Effective | Note |
|---|---|---|---|
| **TT 99/2025/TT-BTC** | **ACTIVE** | 01/01/2026 | Replaces TT200 |
| TT 200/2014/TT-BTC | **REPLACED** | — | Superseded by TT 99 |
| TT 133/2016/TT-BTC | **REPLACED** | — | For SMEs, superseded by TT 99 |
| Luật KT 88/2015/QH13 | **ACTIVE** (amended) | 01/01/2017 | Amended by 56/2024/QH15 |
| ND 70/2025/NĐ-CP | **ACTIVE** | 01/06/2025 | E-invoice amendment to ND 123 |
| ND 123/2020/NĐ-CP | **ACTIVE** (amended) | 01/07/2022 | Base e-invoice regulation |
| VAS (VAS 01-30) | **ACTIVE** | — | Transitioning to IFRS per QĐ 345/QĐ-BTC |
| IFRS (adoption) | **IN PROGRESS** | 2025-2030 | Mandatory for listed cos |

### 1.2 Tax Regulations

| Regulation | Status | Effective |
|---|---|---|
| Luật QLT 56/2024/QH15 | ACTIVE | 2025 |
| Luật GTGT 48/2024/QH15 | ACTIVE | 2025 |
| Luật TNDN 67/2025/QH15 | ACTIVE | 2026 |
| Luật TNCN 109/2025/QH15 | ACTIVE | 2026 |
| Luật BHXH 2024 | ACTIVE | 2025 |

### 1.3 Key Changes: TT 99 vs TT 200

1. **Bảng CĐKT renamed** → "Báo cáo tình hình tài chính"
2. **Account system:** 71 level-1 accounts (vs 68 in TT200), 101 level-2
3. **Removed accounts:** TK 611 (mua hàng), TK 1562 (chi phí thu mua)
4. **New accounts:** TK 171 (giao dịch mua bán lại TPCP), etc.
5. **Internal control mandate:** Doanh nghiệp must build internal accounting control charter
6. **Self-designed vouchers:** No more mandatory form templates — just 7 essential elements
7. **Impairment:** Mandatory asset impairment assessment (tiệm cận IAS 36)
8. **Revenue recognition:** 5-step model per IFRS 15
9. **Currency:** Detailed rules for foreign currency as accounting currency

---

## 2. GAP ANALYSIS — CURRENT APP vs LEGAL REQUIREMENTS

### 2.1 CRITICAL: Outdated Regulatory Reference

```
Current app:  references TT 200/2014/TT-BTC (in schema.sql comments)
Requirement:  MUST comply with TT 99/2025/TT-BTC from 01/01/2026
Impact:       PRODUCTION BLOCKER — illegal to use TT 200 regime after 01/01/2026
```

### 2.2 Account Code Validation — BROKEN

```typescript
// Current: src/domain/gl/account.ts:173
validateCode: /^\d{1,4}$/   // Max 4 digits
```
- TT 99 account codes go to **level 4** (e.g., 1331, 1332, 1361-1368)
- Required: support **1→7 digit codes** matching TT 99 Phụ lục II

### 2.3 Monetary Type — CRITICAL

```typescript
// Current: uses JavaScript number (IEEE 754 float64) for ALL money
balance: number;       // src/domain/gl/account.ts
debitAmount: number;   // src/domain/gl/journal.ts
totalDebit: number;
```
- Float64 CANNOT represent VND precisely (e.g., 0.01 + 0.02 = 0.030000000000000002)
- **TT 99 Điều 4:** VND is accounting currency, requires exact decimal precision
- Required: **decimal.js** or **BigInt** (store as xu, display as VND)

### 2.4 DEBIT_EPSILON = 1 — Audit Risk

```typescript
const DEBIT_EPSILON = 1;  // src/domain/gl/journal.ts:162
```
- Allows 1 VND imbalance in double-entry
- **Every auditor rejects this.** TT 99 + Luật KT 88/2015 both demand strict Nợ=Có
- Fix: Use ε=0. Use `decimal.js` comparison

### 2.5 Account Category Mapping — WRONG Classes

```
Current: CostOfGoodsSold = class "6", OperatingExpense = class "5"
TT 99:   TK 6 = "Chi phí sản xuất, kinh doanh" includes both
         TK 632 (Giá vốn hàng bán) is Level-2 under TK 6
         TK 641, 642 are also Level-2 under TK 6
```
- The current class mapping conflates account numbering with category semantics
- TT 99 has different hierarchy

### 2.6 Transaction Isolation — Race Condition Risk

```
Current: MariaDbUnitOfWork uses manual connection, but repo methods
         use pool.query() separately → NOT in same transaction
```
- Required: ALL operations in posting pipeline must use the SAME transaction
- Use `SELECT ... FOR UPDATE` on account balances

### 2.7 Audit Log — Insufficient

```
Current: AuditLog stores only { entityType, entityId, action, changes }
Required: MUST store BEFORE and AFTER values per field
          TT 99 Điều 3 + Luật KT 88/2015 Điều 11 require tracing
```

### 2.8 No Internal Control Module

```
TT 99 Điều 3:  Bắt buộc xây dựng Quy chế quản trị và kiểm soát nội bộ
Current app:   No segregation of duties enforcement beyond basic check
Required:      Full RBAC + approval workflow + SoD matrix
```

---

## 3. CAN THIS APP OPERATE IN PRODUCTION?

**VERDICT: NO — NOT IN CURRENT FORM**

### 3.1 Production Killers (must fix before ANY deployment)

| # | Issue | Severity | Fix Priority |
|---|---|---|---|
| 1 | TT 200 reference → illegal from 01/01/2026 | **BLOCKER** | P0 |
| 2 | `number` type for money → float errors | **CRITICAL** | P0 |
| 3 | DEBIT_EPSILON = 1 → audit failure | **CRITICAL** | P0 |
| 4 | No `SELECT FOR UPDATE` → race conditions | **HIGH** | P1 |
| 5 | Account code validation too restrictive | **HIGH** | P1 |
| 6 | Account category mismatch with TT 99 | **HIGH** | P1 |
| 7 | Audit log missing before/after diff | **MEDIUM** | P2 |
| 8 | No internal control module | **MEDIUM** | P2 |
| 9 | No Swagger/API docs | **LOW** | P3 |
| 10 | No Docker Compose | **MEDIUM** | P2 |

### 3.2 What WORKS (can keep in rewrite)

- Posting pipeline (13-step chain-of-responsibility) → solid design
- Domain events (AccountCreated, JournalBatchPosted, etc.) → keep
- Repository pattern with in-memory test doubles → good DX
- UnitOfWork abstraction → keep, move to Prisma
- Status state machine for JournalBatch (Draft→Submitted→Approved→Posted→Reversed)
- Fiscal Year + Period management

---

## 4. USE CASES (Detailed)

### UC-01: Create Journal Entry (Double-Entry)

**ID:** UC-GL-01
**Priority:** P0
**Actor:** Accountant

**Preconditions:**
- User authenticated with role ≥ "accountant"
- Period is OPEN (not closed/locked)
- Fiscal Year is ACTIVE (not closed)
- All referenced accounts exist, ACTIVE, isPosting=true

**Happy Path:**
```
1. User submits { journalType, periodId, fiscalYearId, voucherDate, 
   postingDate, description, lines[{accountId, debitAmount, creditAmount}] }
2. System validates: 
   - All required fields present
   - Period is open
   - FY is active
   - All accounts exist, active, posting-enabled
   - Total Debit === Total Credit (strict, ε=0)
   - At least 2 lines
   - No negative amounts
   - Each line has debit XOR credit (not both)
3. System creates JournalBatch with status=DRAFT
4. System reserves voucher number from VoucherSeries (if configured)
5. Return JournalBatchState with id, batchNumber, status=draft
```

**Alternative Paths:**
| Condition | Response |
|---|---|
| Period is closed/locked | Error "FIS_001: Period is closed" |
| FY is closed | Error "FIS_003: FY is closed" |
| Account inactive | Error "ACC_003: Account is inactive" |
| Total Debit != Total Credit | Error "ACC_001: Debit != Credit" |
| Duplicate batchNumber | Retry reservation |
| Voucher series exhausted | Error "SER_001: Sequence exhausted" |

**Business Rules:**
```
BR-01: Tổng Nợ = Tổng Có (Luật KT 88/2015 Điều 7, TT 99 Điều 16)
BR-02: Mỗi dòng chỉ ghi Nợ HOẶC Có, không cả hai
BR-03: Số tiền >= 0
BR-04: Bút toán tối thiểu 2 dòng (trừ bút toán khai trương đầu năm)
BR-05: Ngày hạch toán <= ngày hiện tại (không được ghi sổ tương lai)
```

---

### UC-02: Post Journal Entry

**ID:** UC-GL-02
**Priority:** P0
**Actor:** Chief Accountant (or authorized user with role "poster")

**Preconditions:**
- Batch exists, status=APPROVED
- Approver != Creator (segregation of duties)
- User has "poster" role

**Happy Path:**
```
1. System selects batch for posting
2. BEGIN Prisma.$transaction:
3.   SELECT ... FOR UPDATE on all referenced accounts
4.   Re-validate: debit=credit, accounts, period, FY
5.   For each line:
6.     Update account.balance += (debitAmount - creditAmount)
7.       If account.nature=debit: balance += debit - credit
8.       If account.nature=credit: balance += credit - debit
9.   Update batch status = POSTED, postedById, postedAt
10.  Create AuditLog entry with before/after balance
11.  Publish JournalBatchPosted domain event
12. COMMIT
13. Return PostingResult { batchId, batchNumber, postedAt, totals }
```

**Alternative Paths:**
| Condition | Response |
|---|---|
| Idempotency key provided + already processed | Return cached result |
| Account version mismatch (optimistic lock fail) | Retry transaction |
| DB crash during step 5-11 | Auto ROLLBACK via MariaDB redo log |
| Network failure after commit | Client retry with idempotency key |

---

### UC-03: Reverse Journal Entry

**ID:** UC-GL-03
**Priority:** P1
**Actor:** Chief Accountant

**Preconditions:**
- Batch exists, status=POSTED
- Period is OPEN

**Happy Path:**
```
1. System creates reversal batch with inverted debits/credits
2. Original batch lines: Dr 111=1000, Cr 511=1000
   Reversal: Dr 511=1000, Cr 111=1000
3. Use same posting pipeline as UC-02
4. Original batch status → REVERSED
5. Reversal batch status → POSTED
6. Link: reversedBatchId on reversal points to original
```

---

### UC-04: Close Period

**ID:** UC-GL-04
**Priority:** P1
**Actor:** Chief Accountant

**Preconditions:**
- All batches in period are POSTED
- User has role "admin"

**Happy Path:**
```
1. Check no DRAFT/SUBMITTED batches in period
2. Update period status = CLOSED
3. No further posting allowed
```

**Alternative:**
- Period can be REOPENED by admin (for adjustments)
- Reopening triggers audit log

---

## 5. DATA FLOW

```
[User (Browser/Desktop)] 
    ↓ POST /api/gl/journals { data }
    ↓
[NestJS Controller] 
    ↓ @Body() validated via class-validator + DTO
    ↓
[JournalService]
    ↓ 1. Validate business rules
    ↓ 2. Create JournalBatch domain entity
    ↓ 3. Call Prisma $transaction
    ↓
[Prisma Client]
    ↓ 1. INSERT journal_batch
    ↓ 2. INSERT journal_entry_lines (batch)
    ↓ 3. Audit log
    ↓
[MariaDB InnoDB]
    ↓ WAL → redo log → data file
    ↓
[Cache Invalidation]
    ↓ cacheManager.del('batch:*', 'account:*')
    ↓
[Response → Client]
```

**Posting flow (expanded):**
```
JournalService.approve() → status=APPROVED
                           ↓
PostingEngine.post()      → BEGIN TX
                           → SELECT ... FOR UPDATE accounts
                           → Validate (13-step pipeline)
                           → Calculate balance changes (decimal.js)
                           → UPDATE accounts SET balance
                           → UPDATE journal_batches SET status=POSTED
                           → INSERT audit_log
                           → COMMIT TX
                           → Invalidate cache
                           → Publish DomainEvent
```

---

## 6. WORKFLOW DIAGRAM (Text)

```
                    ┌──────────┐
                    │   DRAFT  │
                    └────┬─────┘
                         │ submit()
                         ▼
                    ┌──────────┐
                    │ SUBMITTED│
                    └────┬─────┘
                         │ approve(userId)
                         ▼
                    ┌──────────┐
                    │ APPROVED │
                    └────┬─────┘
                         │ post(userId)
                         ▼
                    ┌──────────┐
                    │  POSTED  │◄────┐
                    └────┬─────┘     │
                         │           │ reverse()
                         ▼           │
                    ┌──────────┐     │
                    │ REVERSED │─────┘
                    └──────────┘

                    DRAFT → CANCELLED (delete before post)
                    POSTED → REVERSED (reverse only)
```

---

## 7. RULES ENGINE (for TT 99 Compliance)

```
Rule Set "Posting Validation":
  R01: [MANDATORY] TotalDebit == TotalCredit (decimal compare)
  R02: [MANDATORY] All accounts exist & active & isPosting
  R03: [MANDATORY] Period is open
  R04: [MANDATORY] Fiscal year is active
  R05: [MANDATORY] Posting date <= current date
  R06: [MANDATORY] At least 2 lines (except opening entries)
  R07: [MANDATORY] No line has both debit AND credit > 0
  R08: [MANDATORY] Creator != Approver (SoD)
  R09: [MANDATORY] Each line has description
  R10: [WARNING]   Account balance will become negative debit-nature
  R11: [WARNING]   Foreign currency totals match
```

---

## 8. USER JOURNEY

```
Day 1: Admin creates Fiscal Year + Periods (12 months)
Day 1: Admin creates/imports Chart of Accounts (TT 99 Phụ lục II)
Day 2: Admin creates Voucher Types + Voucher Series
Week 1: Accountant creates Journal Entries (DRAFT)
         → System validates Nợ=Có, accounts, period
         → Status = DRAFT
Week 1: Accountant SUBMITS batch
         → Status = SUBMITTED
Week 1: Chief Accountant APPROVES batch
         → Status = APPROVED  
         (system checks: approver != creator)
Week 1: Chief Accountant POSTES batch
         → Transaction atomic: balances updated
         → Status = POSTED
         → Audit trail recorded
Month-end: Chief Accountant closes period
            → All batches must be POSTED
            → Period status = CLOSED
Year-end:  Close Fiscal Year
            → All 12 periods closed
            → FY status = CLOSED
            → Opening entry for next year
```

---

## 9. IMMEDIATE ACTION ITEMS

| # | Action | Owner | Timeline |
|---|---|---|---|
| 1 | Replace `number` with `Decimal` from decimal.js | Tech | Week 1 |
| 2 | Update account code validation to support TT 99 | Tech | Week 1 |
| 3 | Remove DEBIT_EPSILON, enforce strict Nợ=Có | Tech | Week 1 |
| 4 | Update AccountCategory enum to match TT 99 | BA+Tech | Week 2 |
| 5 | Fix transaction isolation (SELECT FOR UPDATE) | Tech | Week 2 |
| 6 | Add before/after balance to AuditLog | Tech | Week 2 |
| 7 | Update schema.sql comments to reference TT 99 | BA | Week 1 |
| 8 | Add idempotency support to posting endpoint | Tech | Week 2 |
| 9 | Add Swagger docs for all endpoints | Tech | Week 3 |
| 10 | Build Docker Compose | Tech | Week 3 |
