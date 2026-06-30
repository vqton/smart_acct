# FS Module — Detailed Use Cases

**Coverage**: UC-FS-01 through UC-FS-14  
**Status**: Complete spec for Phase 1 (MVP) + Phase 2/3 outline  
**Regulatory Base**: TT 99/2025/TT-BTC (Phụ lục IV), IFRS 18, VAS 01/21

---

## UC-FS-01: Generate B01-DN (Báo cáo tình hình tài chính)

### Scope
Generate TT99-compliant Statement of Financial Position (going concern).

### Preconditions
- Period open + GL entries posted
- COA-to-FS mapping configured
- Prior period FS exists (for comparative)

### Happy Path
1. User POST `/api/v1/fs/generate` with `{period: "2026-05", type: "B01_DN", entity_id: 1}`
2. System validates period is open
3. System queries GLRepository.get_account_balance() for each account in FS mapping
4. Sum balances by FS mã số
5. Compute subtotals: Mã số 100 = 110+120+130+140+150; Mã số 200 = 210+220+230+240+250+260; Mã số 270 = 100+200
6. Compute Mã số 300 = 310+320+330; Mã số 400 = 410+420+430
7. Compute Mã số 440 = 300+400
8. Verify: Mã số 270 == Mã số 440 (tolerance 0.001 VND)
9. Query prior period FS for comparative column
10. Create FS record with status DRAFT, version 1
11. Log FS_CREATED audit event
12. Return FS with all line items

### Alternative Paths
- **A1: First period (no prior)**: Comparative column = 0, note "Doanh nghiệp mới thành lập"
- **A2: Partial mapping**: Unmapped accounts listed in warnings; excluded from FS; generation continues
- **A3: Re-generation after adjustment**: Replaces prior draft; version incremented; old version archived

### Exception Paths
- **E1: Period closed**: Error `PERIOD_CLOSED_FS_GEN`
- **E2: No posted entries**: Warning `NO_POSTED_ENTRIES`; allow generation with zero FS
- **E3: Balance sheet imbalance**: Error `BALANCE_SHEET_IMBALANCE` with diff amount; reject generation
- **E4: No FS mapping**: Error `FS_MAPPING_NOT_CONFIGURED`
- **E5: Entity not found**: Error `ENTITY_NOT_FOUND`
- **E6: Concurrent generation**: Error `FS_ALREADY_EXISTS_DRAFT` — use existing draft

---

## UC-FS-02: Generate B02-DN (Báo cáo kết quả HĐKD)

### Scope
Generate TT99-compliant Income Statement (going concern).

### Happy Path
1. POST `/api/v1/fs/generate` with `{period: "2026-05", type: "B02_DN"}`
2. Query revenue accounts (TK 511, 515, 711) — credit balances
3. Query expense accounts (TK 632, 635, 641, 642, 811, 821) — debit balances
4. Compute: Mã số 10 = 01 - 02; Mã số 20 = 10 - 11; Mã số 30 = 20 + 21 - 22 - 23 - 24; Mã số 50 = 30 + 40 - 41; Mã số 60 = 50 - 51 - 52
5. Populate prior year comparative
6. Create draft FS

### Exception Paths
- **E1: Revenue/expense not closed**: Warning — auto-close via 911 recommended
- **E2: Negative gross margin**: Warning flagged but generation continues

---

## UC-FS-03: Generate B03-DN (Báo cáo lưu chuyển tiền tệ)

### Scope
Generate Cash Flow Statement (both direct + indirect methods).

### Happy Path (Direct)
1. POST `/api/v1/fs/generate` with `{period: "2026-05", type: "B03_DN", method: "direct"}`
2. Query CashRepository for all cash transactions in period
3. Classify by cash flow category (operating/investing/financing)
4. Compute Mã số 01-05 (direct inflows/outflows)
5. Compute Mã số 20 (investing: FA purchases/sales, investments)
6. Compute Mã số 30 (financing: loans, equity, dividends)
7. Mã số 50 = 01 + 20 + 30; Mã số 70 = 60 + 50
8. Verify Mã số 70 = GL cash balance (TK 111+112)

### Happy Path (Indirect)
1. Start with LNST (B02 Mã số 60)
2. Add back depreciation (TK 214), provisions (TK 229)
3. Adjust for working capital changes (AR, inventory, AP)
4. Result = Mã số 01 (indirect)
5. Verify Mã số 01 (indirect) == Mã số 01 (direct)

### Exception Paths
- **E1: Cash balance mismatch**: Error `CASH_FLOW_MISMATCH` — Tiền cuối kỳ ≠ GL balance
- **E2: Missing cash transactions**: Warning — some periods may lack detailed cash data

---

## UC-FS-04: Generate B09-DN (Bản thuyết minh BCTC)

### Scope
Generate Notes to Financial Statements.

### Happy Path
1. POST `/api/v1/fs/generate` with `{period: "2026-05", type: "B09_DN"}`
2. Auto-populate: entity info, accounting policies, period
3. Auto-fill: breakdowns for B01/B02/B03 items
4. Manual sections: contingent liabilities, related-party transactions
5. Create draft B09-DN linked to main FS

### Sections
- I: Đặc điểm hoạt động — from entity master data
- II: Kỳ kế toán, đơn vị tiền tệ — from config
- III: Chuẩn mực kế toán — from entity config
- IV: Chính sách kế toán — template per account type
- V-VIII: B01 supplementary — auto from GL
- IX-XI: B02 supplementary — auto from GL
- XII-XIV: B03 supplementary — auto from cash module
- XV-XIX: Other — manual input

---

## UC-FS-05: FS Approval Workflow

### Happy Path
1. Drafter POST `/api/v1/fs/{id}/submit` → status IN_REVIEW
2. Chief Accountant GET `/api/v1/fs/review` → lists IN_REVIEW FS
3. CA reviews → POST `/api/v1/fs/{id}/approve` → status APPROVED
4. CEO GET `/api/v1/fs/approve` → lists APPROVED FS
5. CEO signs → POST `/api/v1/fs/{id}/sign` → status SIGNED
6. Signed PDF generated with digital signatures
7. FS locked — no modifications

### Alternative Paths
- **A1: Rejection**: POST `/api/v1/fs/{id}/reject` with reason → status REJECTED → back to DRAFT
- **A2: Delegate**: Approver delegates to deputy via config
- **A3: Batch sign**: POST `/api/v1/fs/batch-sign` with ID list

### Exception Paths
- **E1: Wrong role**: Error `UNAUTHORIZED_FS_ACTION`
- **E2: Bad state transition**: Error `INVALID_FS_TRANSITION` (e.g., DRAFT → SIGNED)
- **E3: Missing signature key**: Error `SIGNING_KEY_NOT_CONFIGURED`

### State Machine
```
                   reject
DRAFT ──submit──▶ IN_REVIEW ──approve──▶ APPROVED ──sign──▶ SIGNED
  ▲                   │                      │
  └───reject◀─────────┘                      │
       reject                                │
  ▲──────────────────────────────────────────┘
```

---

## UC-FS-06: FS Versioning & Audit

### Happy Path
1. Each FS create → version 1
2. Re-generate → version incremented (v2, v3)
3. Full line-item diff stored between versions
4. All audit events logged immutably
5. GET `/api/v1/fs/{id}/audit-log` returns full trail

---

## UC-FS-07: FS Export

### Happy Path
1. GET `/api/v1/fs/{id}/export?format=pdf` → returns PDF
2. GET `/api/v1/fs/{id}/export?format=xlsx` → returns Excel
3. GET `/api/v1/fs/{id}/export?format=html` → returns HTML

### Rules
- PDF: A4, margins top 20mm/bottom 20mm/left 30mm/right 15mm
- Excel: Exact TT99 biểu mẫu layout with merged cells
- HTML: Mobile-responsive with collapsible sections

### Exception Paths
- **E1: FS not found**: Error 404
- **E2: Unsupported format**: Error `UNSUPPORTED_EXPORT_FORMAT`

---

## UC-FS-08: GL-to-FS Mapping Config

### Happy Path
1. POST `/api/v1/fs/mappings` with mapping rules
2. GET `/api/v1/fs/mappings` lists all mappings
3. PUT `/api/v1/fs/mappings/{id}` updates
4. DELETE removes mapping
5. Validation: account_code must exist in COA; fs_ma_so must be valid per statement_type

---

## UC-FS-09: Multi-Entity Consolidation (Phase 2)

### Happy Path
1. POST `/api/v1/fs/consolidation/groups` create group
2. POST `/api/v1/fs/consolidation/generate` with group_id + period
3. System collects individual FS from all members
4. Applies intercompany eliminations (AR/AP, revenue/expense)
5. Calculates NCI
6. Produces consolidated FS

---

## UC-FS-10 through UC-FS-14 (Phase 2-3)

See BRD sections for detailed scope of:
- UC-FS-10: DNKLT generation
- UC-FS-11: Interim FS
- UC-FS-12: FS analysis & ratios
- UC-FS-13: IFRS 18 convergence
- UC-FS-14: e-Submission

---

## API Endpoints Summary

| Method | Path | UC | Phase |
|--------|------|----|-------|
| POST | `/api/v1/fs/generate` | FS-01/02/03/04 | P0 |
| GET | `/api/v1/fs` | List FS | P0 |
| GET | `/api/v1/fs/{id}` | Get FS detail | P0 |
| POST | `/api/v1/fs/{id}/submit` | FS-05 | P0 |
| POST | `/api/v1/fs/{id}/approve` | FS-05 | P0 |
| POST | `/api/v1/fs/{id}/sign` | FS-05 | P0 |
| POST | `/api/v1/fs/{id}/reject` | FS-05 | P0 |
| GET | `/api/v1/fs/{id}/audit-log` | FS-06 | P0 |
| GET | `/api/v1/fs/{id}/export` | FS-07 | P0 |
| GET/POST/PUT/DELETE | `/api/v1/fs/mappings` | FS-08 | P0 |
| POST | `/api/v1/fs/consolidation/generate` | FS-09 | P1 |
| GET | `/api/v1/fs/ratios/{id}` | FS-12 | P1 |

---

## Test Coverage Plan

| Use Case | Unit Tests | Integration Tests | Edge Cases |
|----------|-----------|-------------------|------------|
| UC-FS-01 | 15 | 8 | 10 |
| UC-FS-02 | 10 | 6 | 8 |
| UC-FS-03 | 12 | 8 | 10 |
| UC-FS-04 | 8 | 4 | 6 |
| UC-FS-05 | 10 | 6 | 8 |
| UC-FS-06 | 5 | 4 | 3 |
| UC-FS-07 | 5 | 4 | 3 |
| UC-FS-08 | 8 | 4 | 4 |
| UC-FS-09 | 10 | 6 | 6 |
| **Total** | **83** | **50** | **58** |

Target: 130+ tests for Phase 1, 40+ for Phase 2.
