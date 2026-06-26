# BRD: Hệ thống tài khoản kế toán (COA Module)
## Business Requirements Document

**Version:** 1.0 | **Date:** 2026-06-26
**Author:** BA Lead / Chief Accountant (20+ yrs)
**Status:** Draft for Review

---

## 1. Executive Summary

Xây dựng **COA Module** cho SmartACCT ERP — quản lý hệ thống tài khoản kế toán VN. Module phải hỗ trợ đồng thời **Thông tư 99/2025/TT-BTC** (hiệu lực 01/01/2026, thay thế TT200/2014), **Thông tư 133/2016/TT-BTC** (SME), và chuẩn mực **IFRS** (theo lộ trình QĐ 345/QĐ-BTC 2020). Cho phép DN tùy biến TK theo Điều 11 TT99 trong khi vẫn đảm bảo BCTC hợp nhất.

---

## 2. Regulatory Landscape (Research Synthesis)

### 2.1 Current Active Regulations

| Regulation | Issuer | Effective | Scope | Status |
|---|---|---|---|---|
| **TT 99/2025/TT-BTC** | MoF | 01/01/2026 | All enterprises | **PRIMARY** — replaced TT200/2014 |
| **TT 133/2016/TT-BTC** | MoF | 01/01/2017 | SMEs (< 200 tỷ VND) | Active, coexists with TT99 |
| **Luật Kế toán 2015** | NA | 01/01/2017 | All | Foundation law |
| **Luật Quản lý thuế 56/2025/QH15** | NA | 01/07/2026 | All | New tax management |
| **QĐ 345/QĐ-BTC 2020** | MoF | 2020+ | Listed companies | IFRS roadmap |
| **VAS (26 chuẩn mực)** | MoF | 2000-2020 | All | Based on IAS/IFRS |

### 2.2 Key Regulatory Changes: TT99/2025 vs TT200/2014

- Account system restructured in **Phụ lục II** — new accounts added, obsolete removed
- Doanh nghiệp **được sửa đổi, bổ sung** tên/số hiệu/kết cấu TK (Điều 11.2)
- Phải ban hành **Quy chế hạch toán** nếu tự sửa đổi
- Không được làm thay đổi/ảnh hưởng chỉ tiêu BCTC
- TT99 chỉ hướng dẫn nghiệp vụ chủ yếu — nghiệp vụ đặc thù dựa trên VAS + nguyên tắc TT99

### 2.3 IFRS Convergence

- Decision 345: listed companies and SOEs must adopt IFRS for consolidated FS
- IFRS for SMEs considered as alternative for unlisted SMEs
- **IFRS 20** (new, in preparation): Subsidiaries without public accountability — disclosure简化
- IFRS Digital subscription available via IFRS Foundation

### 2.4 Big4 & Professional Community (Sources)

| Source | Relevance |
|---|---|
| **VACPA** (vacpa.org.vn) | Auditing standards, practice review |
| **Tạp chí Kế toán & Kiểm toán** | Academic/practice research |
| **Webketoan.com** (652K+ members) | Largest practitioner community, FAQ on COA |
| **Ketoanthienung.net** | Practical training, TT99 guidance |
| **Ketoanleanh.edu.vn** | Certified training, MoF-approved |
| **GDT.gov.vn** | Tax authority — official tax account codes |
| **MoF.gov.vn** | Policy-making, circular issuance |
| **Deloitte/PwC/EY/KPMG Vietnam** | IFRS advisory, compliance services |

---

## 3. Business Objectives

1. **Compliance-first**: Ensure 100% adherence to TT99/2025 (primary), TT133/2016 (SME fallback)
2. **Flexibility**: Allow enterprise-specific account customization per Điều 11 TT99
3. **Dual-reporting**: Support VAS↔IFRS mapping for consolidation
4. **Audit-ready**: Full audit trail on all COA changes
5. **Multi-entity**: Group-level chart with subsidiary-specific overrides

---

## 4. COA Module — Detailed Specification

### 4.1 Account Types (Type 1-9)

```
1.x.x — TÀI SẢN (ASSETS)               Dr normal
2.x.x — NỢ PHẢI TRẢ (LIABILITIES)      Cr normal
3.x.x — VỐN CHỦ SỞ HỮU (EQUITY)        Cr normal
4.x.x — DOANH THU (REVENUE)             Cr normal
5.x.x — CHI PHÍ (EXPENSES)              Dr normal
6.x.x — CHI PHÍ SXKD (COGS)             Dr normal
7.x.x — THU NHẬP HĐ (OPERATING INCOME)  Cr normal
8.x.x — KẾT QUẢ KINH DOANH (P&L)       Cr normal
9.x.x — THU NHẬP KHÁC (OTHER INCOME)   Cr normal
```

### 4.2 Account Hierarchy

- **Level 1**: Type (1 char, 1-9) — `1`, `2`, ..., `9`
- **Level 2**: Group (2-3 chars) — `11`, `12`, `21`, `111`
- **Level 3**: Sub-group (3-4 chars) — `111`, `1111`
- **Level 4**: Detail (4-6 chars) — `1111`, `11111`, `111111`

Max **4 levels** per VAS standard. Max **6 numeric digits** total.

### 4.3 COA Code Patterns

| Pattern | Example | Valid |
|---|---|---|
| `[1-9]` | `1` | Yes — Level 1 |
| `[1-9]\.[0-9]+` | `1.1`, `2.1` | Yes — Level 2 |
| `[1-9]\.[0-9]+\.[0-9]+` | `1.1.1`, `4.1.1` | Yes — Level 3 |
| `[1-9]\.[0-9]+\.[0-9]+\.[0-9]+` | `1.1.1.1` | Yes — Level 4 |
| `[0-9]{4,6}` | `1111`, `11111` | Yes — flat numeric |
| Starts with `0` | `0111` | **INVALID** |
| Non-numeric chars | `A111`, `1A11` | **INVALID** |

### 4.4 DCR Direction Rules

| Account Category | Normal Balance | DRCr Direction |
|---|---|---|
| ASSET (Type 1) | Debit | Dr |
| LIABILITY (Type 2) | Credit | Cr |
| EQUITY (Type 3) | Credit | Cr |
| REVENUE (Type 4) | Credit | Cr |
| EXPENSE (Type 5) | Debit | Dr |
| COGS (Type 6) | Debit | Dr |
| OPERATING INCOME (Type 7) | Credit | Cr |
| P&L (Type 8) | Credit/Dr | Dual |
| OTHER INCOME (Type 9) | Credit | Cr |

### 4.5 Account States

```
DRAFT → ACTIVE → SUSPENDED → CLOSED
  │                    │
  └────→ REJECTED     └────→ ARCHIVED
```

- **DRAFT**: Template, not usable in transactions
- **ACTIVE**: Open for posting
- **SUSPENDED**: Temporarily blocked (balance preserved)
- **CLOSED**: No new postings, year-end close
- **ARCHIVED**: Historical only, moved to archive
- **REJECTED**: Creation rejected by approver

### 4.6 Validation Rules

1. Code must be unique across chart
2. Code must match pattern `^[1-9](\.[0-9]+){0,3}$` or `^[1-9][0-9]{3,5}$`
3. Max 6 numeric digits (excluding dots)
4. Max 4 hierarchy levels
5. Parent must exist before child creation
6. Can't delete account with non-zero balance
7. Can't delete account with transaction history — only deactivate
8. Currency must be in supported list: VND, USD, EUR, JPY, GBP
9. Balance precision: 2 decimal places (quantize to 0.01)
10. Name required, max 300 chars
11. DCR direction must match account type
12. Account with IFRS mapping must pass IFRS validation

---

## 5. Use Cases

### UC-01: Create Chart of Accounts
**Actor:** Kế toán trưởng (Chief Accountant)
**Precondition:** User has COA_ADMIN role

**Happy Path:**
1. User selects regulatory regime (TT99/TT133/IFRS)
2. System loads default chart template from Phụ lục II
3. User can add/modify/delete accounts within template
4. User assigns account type, level, DCR direction
5. User sets currency, parent-child hierarchy
6. System validates all rules
7. User submits for approval (if workflow enabled)
8. COA saved to database with versioning

**Alternative Paths:**
- **A1**: Custom account via Điều 11.2 — user must provide justification, system flags as non-standard, requires approval
- **A2**: Import from Excel/CSV — batch validation, error report
- **A3**: Clone from existing entity — copies chart with optional overrides

### UC-02: Manage Individual Account
**Actor:** Kế toán viên (Accountant)
**Precondition:** COA exists, user has COA_EDIT role

**Happy Path:**
1. User searches account by code/name
2. System returns account details (code, name, type, balance, status)
3. User edits name, description, currency (if balance=0)
4. User saves changes
5. System logs audit trail

**Alternative Paths:**
- **A1**: Cannot edit account_type or DCR_direction if balance ≠ 0
- **A2**: Cannot edit code — must deactivate and create new
- **A3**: Currency change requires zero balance first

### UC-03: Import COA from Excel
**Actor:** Kế toán trưởng
**Precondition:** Excel template matches required columns

**Happy Path:**
1. User downloads official import template
2. User fills codes, names, types, parent codes
3. User uploads file
4. System validates row by row
5. Validation report shows pass/fail per row
6. User confirms import
7. System commits valid rows, rejects invalid

**Alternative Paths:**
- **A1**: Partial import — valid rows committed, invalid reported
- **A2**: Duplicate codes — all duplicates rejected
- **A3**: Circular parent-child — detected and reported

### UC-04: Export COA
**Actor:** Any authenticated user
**Precondition:** COA exists

**Happy Path:**
1. User selects export format (Excel/CSV/PDF)
2. User selects scope (all/active/type filter)
3. System generates file with:
   - Account code, name, type, DCR direction, level
   - Parent code, currency, status
   - Opening balance, current balance
4. File downloaded

### UC-05: Map VAS↔IFRS
**Actor:** Kế toán trưởng / CFO
**Precondition:** Both VAS COA and IFRS COA exist

**Happy Path:**
1. User opens mapping screen
2. System shows VAS accounts (left) and IFRS accounts (right)
3. User drags/draws mapping lines
4. User sets mapping type (1:1, N:1, 1:N, expression-based)
5. System validates no orphan accounts
6. Mapping saved for consolidation engine

### UC-06: COA Versioning & Audit
**Actor:** Kiểm toán viên (Auditor)
**Precondition:** COA has at least 2 versions

**Happy Path:**
1. Auditor selects date range
2. System shows version timeline
3. Auditor can diff two versions (added/changed/deleted accounts)
4. System shows who made each change, when, why
5. Audit report generated

### UC-07: Check Account Usage
**Actor:** Kế toán viên
**Precondition:** Account exists

**Happy Path:**
1. User queries account
2. System shows:
   - Current balance, monthly balances
   - Open transactions count
   - Last transaction date
   - Related parties
3. User can decide to deactivate/close

### UC-08: Validate COA Compliance
**Actor:** Kế toán trưởng / Auditor
**Precondition:** COA exists

**Happy Path:**
1. User runs compliance check
2. System validates against selected regime
3. Report shows:
   - Missing mandatory accounts (per Phụ lục II)
   - Invalid DCR directions
   - Circular references
   - Orphan child accounts
   - Non-standard custom accounts
4. Actionable recommendations

---

## 6. Business Rules (Rule Engine)

### BR-001: Account Code Uniqueness
`No two active accounts may share the same code within an entity.`

### BR-002: Parent-Child Integrity
`A child account's type must be compatible with its parent's type group.`

### BR-003: Balance Consistency
`Sum of child account balances must equal parent account balance (at period-end).`

### BR-004: Delete Protection
`An account with non-zero balance or linked transactions cannot be deleted — only deactivated.`

### BR-005: Mandatory Accounts
`The following accounts are mandatory per TT99 Phụ lục II:`
- Type 1: 111 (Tiền mặt), 112 (Tiền gửi), 131 (Phải thu KH)
- Type 2: 331 (Phải trả NB), 333 (Thuế), 334 (Phải trả NLĐ)
- Type 3: 411 (Vốn đầu tư CSH), 421 (LN chưa PP)
- Type 4: 511 (DT bán hàng)
- Type 5: 641 (CP bán hàng), 642 (CP QLDN)
- Type 6: 631 (Giá thành SX), 632 (Giá vốn hàng bán)
- Type 7: 711 (Thu nhập khác)
- Type 8: 811 (Chi phí khác), 821 (CP thuế TNDN)
- Type 9: 911 (XĐKQKD)

### BR-006: Custom Account Rule (Điều 11 TT99)
`Custom accounts must not overlap with standard codes and must not affect BCTC indicators. Must be documented in Quy chế hạch toán.`

### BR-007: IFRS Mapping Completeness
`All VAS accounts used in consolidation must have at least one IFRS mapping.`

### BR-008: DCR Direction Invariant
`Account DCR direction cannot change if there are any postings in current or prior periods.`

### BR-009: Currency Restriction
`Account currency can only change when balance is zero (opening + period = 0).`

### BR-010: Year-End Closure
`At year-end, all revenue/expense accounts (Type 4-6, 8) must close to 911 (P&L), then to 421 (Retained Earnings).`

---

## 7. Data Flow

### 7.1 COA Creation Flow

```
User Input → Validator → Account Factory → Repository → DB
                │                            │
                ▼                            ▼
           Error Report                 Audit Log
```

### 7.2 Transaction Posting Flow (COA Integration)

```
Journal Entry → Validate Accounts Exist → Check DCR → Balance Check → Post
                    │                        │
                    ▼                        ▼
               Account Lookup          Validate Direction
```

### 7.3 Financial Statement Flow

```
COA Master → Monthly Balances → Trial Balance → Adjustment → BCTC
  │                              │
  ▼                              ▼
Account Types              Balance Aggregation
```

---

## 8. Workflow

### 8.1 Account Lifecycle

```
┌─────────┐    Approve    ┌────────┐    Use     ┌────────┐   Year-end  ┌────────┐
│  DRAFT  │ ────────────→ │ ACTIVE │ ──────────→ │SUSPEND │ ──────────→ │ CLOSED │
│         │               │        │             │  ED    │             │        │
└─────────┘               └────────┘             └────────┘             └────────┘
     │                        │                      │                     │
     │ Reject                 │ Reactivate            │ Archive             │ Archive
     ▼                        ▼                      ▼                     ▼
 ┌─────────┐              ┌────────┐             ┌────────┐           ┌────────┐
 │REJECTED │              │ ACTIVE │             │ ACTIVE │           │ARCHIVED│
 └─────────┘              └────────┘             └────────┘           └────────┘
```

### 8.2 Approval Workflow

```
DRAFT → Submit → Pending Approval → Approve → ACTIVE
                    │                   │
                    ↓                   ↓
                 Reject → REJECTED   Return → DRAFT (revised)
```

---

## 9. User Journey

### Journey 1: Chief Accountant sets up new company

1. Login → System detects no COA → Wizard starts
2. Select regime: TT99/2025 (default)
3. System pre-populates 100+ standard accounts from Phụ lục II
4. Customize: Add 2 industry-specific accounts (justification required)
5. Set currency: VND + 1 USD tracking account
6. Review hierarchy tree (expand/collapse, drag to re-parent)
7. Submit → Pending Approval → CFO approves
8. COA ACTIVE → Ready for transactions

### Journey 2: Accountant imports legacy COA

1. Download template from Export Center
2. Map old codes to new TT99 codes in Excel
3. Upload → Validation: 2 errors (circular parent, invalid code)
4. Fix errors → Re-upload → Pass
5. 145 accounts imported, 142 active, 3 suspended (zero balance)
6. Import report saved to audit trail

### Journey 3: Auditor reviews COA changes

1. Open Audit → COA Versioning
2. Select: Compare Q1 2026 vs Q2 2026
3. Diff shows: 2 accounts added, 1 deactivated, 3 modified
4. Click each change → See who/when/why
5. Export audit report as PDF

---

## 10. Process Specifications

### P-01: Year-End COA Close

```
Input: Current COA with balances
Steps:
1. Verify all transactions posted
2. Close revenue accounts (Type 4) → 911
3. Close expense accounts (Type 5, 6) → 911
4. Calculate P&L → 421 (or 411 if loss)
5. Verify 911 balance = 0 after close
6. Generate closing report
7. Flag accounts as CLOSED for prior year
8. Open new fiscal year COA (copy structure, zero balances)
Output: Closed prior year, open current year
```

### P-02: Multi-Entity Consolidation

```
Input: COA from parent + subsidiaries
Steps:
1. Map each subsidiary's COA to parent COA
2. Validate mapping completeness
3. Convert subsidiary balances at FX rate
4. Aggregate mapped accounts
5. Eliminate intercompany transactions
6. Generate consolidated BCTC
Output: Consolidated financial statements (VAS + IFRS)
```

### P-03: Regulatory Compliance Check

```
Input: Active COA
Steps:
1. Load mandatory accounts for selected regime
2. Check each mandatory code exists and is ACTIVE
3. Validate DCR direction per account type
4. Check account code format compliance
5. Flag custom accounts (non-standard)
6. Check Quy chế hạch toán exists if custom accounts present
7. Generate compliance score (0-100%)
Output: Compliance report with action items
```

---

## 11. System Architecture Recommendations

### 11.1 Domain Model (Current + Proposed)

```
ChartOfAccounts (1) ──→  Account (*)
     │                         │
     │                         ├── MonthlyBalance (*)
     │                         ├── AuditLog (*)
     │                         └── IFRSMapping (0..1)
     │
     └── AccountingRegime (1)
           ├── TT99/2025
           ├── TT133/2016
           └── IFRS
```

### 11.2 API Endpoints (Proposed)

```
GET    /api/v1/coa                     — List chart templates
POST   /api/v1/coa                     — Create COA
GET    /api/v1/coa/{id}                — Get COA detail
PUT    /api/v1/coa/{id}                — Update COA
DELETE /api/v1/coa/{id}                — Delete COA (if unused)

GET    /api/v1/coa/{id}/accounts       — List accounts in COA
POST   /api/v1/coa/{id}/accounts       — Create account
GET    /api/v1/coa/{id}/accounts/{aid} — Get account detail
PUT    /api/v1/coa/{id}/accounts/{aid} — Update account
DELETE /api/v1/coa/{id}/accounts/{aid} — Deactivate account

POST   /api/v1/coa/{id}/import         — Import from Excel
GET    /api/v1/coa/{id}/export         — Export to Excel/CSV/PDF
POST   /api/v1/coa/{id}/validate       — Validate compliance
GET    /api/v1/coa/{id}/versions       — Version history
GET    /api/v1/coa/{id}/diff?v1=&v2=   — Compare versions
POST   /api/v1/coa/{id}/ifrs-mapping   — Set VAS→IFRS mapping
```

### 11.3 Component Dependencies

```
Domain Layer:
  └── ChartOfAccounts (entity)
  └── Account (entity)
  └── AccountType (value object)
  └── DCRDirection (value object)
  └── AccountingRegime (value object)
  └── IFRSMapping (value object)

Use Case Layer:
  └── CreateCOAUseCase
  └── ManageAccountUseCase
  └── ImportCOAUseCase
  └── ExportCOAUseCase
  └── ValidateCOAUseCase
  └── MapIFRSUseCase
  └── VersioningUseCase

Infrastructure Layer:
  └── COARepository (SQLAlchemy)
  └── AccountRepository (SQLAlchemy)
  └── ExcelImporter (openpyxl)
  └── ExcelExporter (openpyxl)
  └── PDFExporter (WeasyPrint)
  └── AuditLogger

Presentation Layer:
  └── COABlueprint (Flask routes)
  └── COATemplates (Jinja2)
  └── COASchemas (marshmallow/jsonschema)
```

---

## 12. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Response time (API) | < 500ms P95 for single account ops |
| Import throughput | > 1000 accounts/min |
| Concurrent users | 50 simultaneous |
| Audit retention | All changes, indefinite |
| Multi-language | Vietnamese (primary), English |
| Export formats | Excel (.xlsx), CSV, PDF |
| Browser support | Chrome, Firefox, Edge latest |
| DB transactions | ACID-compliant, serializable isolation for COA mutations |

---

## 13. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| TT99/2025 amendment | High | Medium | Regime abstraction layer, config-driven |
| IFRS mandatory by law | High | Medium | IFRS mapping built-in from day 1 |
| Custom accounts break BCTC | High | Low | Validation engine, trial balance check |
| Data migration from legacy | Medium | High | Import wizard with rollback |
| User creates circular parent | Medium | Medium | DAG validation on each save |

---

## 14. Open Questions

1. TT99 applies to fiscal year starting 01/01/2026 — what about mid-year adoption?
2. IFRS for SMEs vs full IFRS — which to support first?
3. Approval workflow: mandatory or optional?
4. Number of pre-seeded accounts in official Phụ lục II TT99?
5. Migration path for existing TT200 users — auto-convert or manual re-map?
6. Need real-time sync with GDT tax account codes?

---

## 15. References

- **TT 99/2025/TT-BTC**: Hướng dẫn Chế độ kế toán DN (hiệu lực 01/01/2026)
- **TT 133/2016/TT-BTC**: Chế độ kế toán DN nhỏ và vừa
- **TT 200/2014/TT-BTC**: (Replaced by TT99)
- **QĐ 345/QĐ-BTC 2020**: IFRS adoption roadmap
- **Luật Kế toán 2015**: Số 88/2015/QH13
- **Luật Quản lý thuế 56/2025/QH15**: (hiệu lực 01/07/2026)
- **IFRS Foundation**: ifrs.org
- **VACPA**: vacpa.org.vn
- **GDT**: gdt.gov.vn
- **MoF**: mof.gov.vn

---

*Document prepared by BA Lead / Chief Accountant — 20+ years experience in Vietnamese accounting, tax, and ERP systems. Reviewed against current regulations (June 2026).*
