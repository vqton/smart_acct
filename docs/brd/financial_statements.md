# BRD: Financial Statement Module (Báo cáo tài chính)

**Version**: 1.0  
**Status**: Draft  
**Author**: BA Lead + Chief Accountant (20+ yrs)  
**Regulatory Basis**: TT 99/2025/TT-BTC (eff. 01/01/2026), TT 200/2014/TT-BTC (replaced), VAS, IFRS 18 (eff. 01/01/2027)  
**Last Updated**: 2026-06-30

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Regulatory Framework](#2-regulatory-framework)
3. [Current System Gap Analysis](#3-current-system-gap-analysis)
4. [Module Scope](#4-module-scope)
5. [Functional Requirements](#5-functional-requirements)
6. [Use Cases (UC-FS-01 through UC-FS-14)](#6-use-cases)
7. [Business Rules](#7-business-rules)
8. [Data Model](#8-data-model)
9. [Data Flow Diagrams](#9-data-flow-diagrams)
10. [Workflows](#10-workflows)
11. [User Journeys](#11-user-journeys)
12. [Report Templates per TT 99/2025](#12-report-templates)
13. [GL Posting Matrix](#13-gl-posting-matrix)
14. [Non-Functional Requirements](#14-non-functional-requirements)
15. [Implementation Roadmap](#15-implementation-roadmap)
16. [Appendix: Legal References](#16-appendix)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose
Build complete Financial Statement (FS) module for SmartACCT ERP compliant with **TT 99/2025/TT-BTC** (effective 01/01/2026) replacing TT 200/2014/TT-BTC, with IFRS 18 convergence path.

### 1.2 Current Assessment
**SCORE: 1/10 — NOT PRODUCTION-READY**

| Criterion | Status | Detail |
|-----------|--------|--------|
| Domain model | ❌ | Basic stub only (3 types, no TT99 structure) |
| Use cases | ❌ | None |
| Repository | ❌ | No FS queries exist |
| Routes/API | ❌ | None |
| Templates | ❌ | None |
| Tests | ❌ | None |
| Approval workflow | ❌ | Missing |
| Multi-entity | ❌ | Missing |
| e-Submission | ❌ | Missing |

### 1.3 Gap Summary
Current `FinancialStatement` in `domain/gl.py:280-434`:
- Only 3 statement types: `balance_sheet`, `income_statement`, `cash_flow`
- Missing TT99 naming: B01-DN, B02-DN, B03-DN, B09-DN
- Missing DNKLT (non-going-concern) templates
- Missing interim reports (B01a/b-DN, B02a/b-DN, B03a/b-DN, B09a-DN)
- No structured line-item hierarchy with `ma_so` (code) per TT99
- No comparative columns (đầu năm / cuối năm)
- No approval/signing workflow
- No consolidation engine
- No XBRL/e-submission
- No IFRS 18 convergence mapping

---

## 2. REGULATORY FRAMEWORK

### 2.1 Active Regulations

| Document | Issuer | Effective | Status | Scope |
|----------|--------|-----------|--------|-------|
| **TT 99/2025/TT-BTC** | MoF | 01/01/2026 | ✅ ACTIVE | Replaces TT 200/2014 — full enterprise accounting regime incl. FS |
| **TT 200/2014/TT-BTC** | MoF | 05/02/2015 | ❌ REPLACED | Replaced by TT99 from 01/01/2026 |
| **TT 75/2015/TT-BTC** | MoF | 14/07/2015 | ❌ REPLACED | Amendment to TT200 |
| **TT 53/2016/TT-BTC** | MoF | 21/03/2016 | ❌ REPLACED | Amendment to TT200 |
| **VAS 01-30** | MoF | Various | ✅ ACTIVE | Vietnamese Accounting Standards (21 standards) |
| **Luật Kế toán 88/2015/QH13** | NA | 01/01/2017 | ✅ ACTIVE | Accounting Law |
| **Luật Kế toán 89/2025/QH15** | NA | 01/01/2026 | ✅ ACTIVE | New Accounting Law (replaces 88/2015) |
| **IFRS 18** | IASB | 01/01/2027 | ✅ FUTURE | Presentation & Disclosure in FS (replaces IAS 1) |
| **QĐ 345/2020/QĐ-BTC** | MoF | 2020 | ✅ ACTIVE | IFRS convergence roadmap |

### 2.2 Key TT 99/2025 Changes Impacting FS

1. **Renaming**: "Bảng cân đối kế toán" → "Báo cáo tình hình tài chính" (B01-DN)
2. **New set**: Non-going-concern templates (B01-DNKLT → B09-DNKLT)
3. **New set**: Interim full (B01a-DN → B09a-DN) and condensed (B01b-DN → B03b-DN)
4. **B09-DN**: Significantly expanded notes requirements
5. **Materiality**: Emphasized — items without data may be omitted (but mã số preserved)
6. **Consistency**: Comparative information must be reclassifiable

### 2.3 IFRS 18 Key Changes (2027)

1. **New subtotals**: Operating profit, profit before financing & income taxes
2. **MPMs**: Management-defined performance measures disclosure
3. **Aggregation/disaggregation**: New principles
4. **Classification**: Operating, investing, financing categories refined
5. Must design FS domain to accommodate both VAS TT99 AND IFRS 18

---

## 3. CURRENT SYSTEM GAP ANALYSIS

### 3.1 Domain Layer (`domain/gl.py`)

| Current | Required | Gap |
|---------|----------|-----|
| `FinancialStatement` with 3 types | 12 TT99 statement types + IFRS 18 | Missing 9 types |
| Dict-based categories | Structured line items with mã số | Full redesign |
| No B09-DN | B09-DN with 30+ sections | Missing entirely |
| No DNKLT | Non-going-concern separate templates | Missing |
| No interim | B01a/b, B02a/b, B03a/b, B09a | Missing |
| Simple generate_monthly() | Full GL-to-FS engine | Missing |
| No approval workflow | Multi-step sign-off | Missing |
| No consolidation | Multi-entity consolidation | Missing |

### 3.2 Use Case Layer (`use_cases/`)

**Zero FS use cases exist.** GL use cases only cover period management and journal entries.

### 3.3 Repository Layer (`infrastructure/repositories/`)

`GLRepository` has:
- `get_account_balance()` — usable for FS generation
- Period management methods
- **No** FS-specific queries (no trial balance aggregation by account type, no comparative period queries, no consolidation queries)

### 3.4 Route Layer (`presentation/`)

**Zero FS endpoints exist.**

---

## 4. MODULE SCOPE

### 4.1 In Scope (Phase 1 — MVP)

| # | Feature | Priority |
|---|---------|----------|
| FS-01 | B01-DN — Báo cáo tình hình tài chính (going concern) | P0 |
| FS-02 | B02-DN — Báo cáo kết quả hoạt động kinh doanh | P0 |
| FS-03 | B03-DN — Báo cáo lưu chuyển tiền tệ (direct + indirect) | P0 |
| FS-04 | B09-DN — Bản thuyết minh BCTC (core sections) | P0 |
| FS-05 | GL-to-FS data engine (trial balance → structured FS) | P0 |
| FS-06 | Period-end FS generation workflow | P0 |
| FS-07 | FS approval workflow (drafter → reviewer → signer) | P0 |
| FS-08 | PDF/Excel/HTML export | P0 |
| FS-09 | FS audit trail | P1 |
| FS-10 | Comparative period (đầu năm / cuối năm / năm trước) | P1 |

### 4.2 In Scope (Phase 2)

| # | Feature | Priority |
|---|---------|----------|
| FS-11 | DNKLT — Non-going-concern templates | P1 |
| FS-12 | Interim reports (B01a-DN → B09a-DN full, B01b-DN → B03b-DN condensed) | P1 |
| FS-13 | Multi-entity consolidation | P1 |
| FS-14 | e-Submission (GDT, customs,统计局) | P2 |
| FS-15 | XBRL taxonomy export | P2 |
| FS-16 | IFRS 18 convergence mapping | P2 |
| FS-17 | MPM disclosure (IFRS 18) | P2 |
| FS-18 | Dashboard with key financial KPIs | P2 |

### 4.3 Out of Scope

- Tax declaration generation (handled by Tax module)
- Budget variance reporting (handled by Budget module)
- Costing reports (handled by Costing Center module)

---

## 5. FUNCTIONAL REQUIREMENTS

### 5.1 FS Generation Engine

**FR-FS-01**: System shall generate B01-DN from posted GL account balances per period.
**FR-FS-02**: Account-to-FS-line mapping shall be configurable (COA account code → FS mã số).
**FR-FS-03**: System shall support both direct method (B03-DN direct) and indirect method (B03-DN indirect) for cash flow.
**FR-FS-04**: System shall auto-calculate: Tổng tài sản = Tài sản ngắn hạn + Tài sản dài hạn.
**FR-FS-05**: System shall auto-verify: Tổng tài sản = Nợ phải trả + Vốn chủ sở hữu (balance sheet identity).
**FR-FS-06**: System shall carry forward retained earnings from prior period.
**FR-FS-07**: System shall populate comparative columns from prior period data.

### 5.2 FS Management

**FR-FS-08**: System shall create FS draft with status `DRAFT`.
**FR-FS-09**: System shall support FS approval workflow: DRAFT → REVIEW → APPROVED → SIGNED.
**FR-FS-10**: System shall lock approved FS against modification.
**FR-FS-11**: System shall allow amendment only via new version (not edit-in-place).
**FR-FS-12**: System shall maintain complete audit trail of all FS actions.

### 5.3 FS Export

**FR-FS-13**: System shall export FS to PDF with TT99-compliant formatting.
**FR-FS-14**: System shall export FS to Excel (.xlsx) with TT99 biểu mẫu layout.
**FR-FS-15**: System shall export FS to HTML for inline viewing.
**FR-FS-16**: PDF export shall include signature blocks (Người lập, Kế toán trưởng, Tổng giám đốc).

### 5.4 FS Comparison & Analysis

**FR-FS-17**: System shall provide period-over-period comparison.
**FR-FS-18**: System shall compute basic financial ratios.
**FR-FS-19**: System shall flag unusual movements (>20% change vs prior period).

---

## 6. USE CASES

### UC-FS-01: Generate B01-DN (Báo cáo tình hình tài chính)

**Description**: Generate Statement of Financial Position (balance sheet) per TT99 B01-DN format.

**Preconditions**:
- Period exists and is not closed
- GL entries for period are posted
- COA-to-FS-line mapping exists

**Happy Path**:
1. User selects period and entity
2. System queries posted GL balances by account
3. System maps each account to B01-DN line items via configurable mapping
4. System calculates: Tài sản ngắn hạn (Mã số 100), Tài sản dài hạn (Mã số 200), Tổng tài sản (Mã số 270)
5. System calculates: Nợ phải trả (Mã số 300), Vốn chủ sở hữu (Mã số 400), Tổng nguồn vốn (Mã số 440)
6. System verifies balance sheet identity: A = L + E (tolerance 0.001 VND)
7. System populates comparative column (đầu năm) from prior period FS
8. System creates FS record with status DRAFT
9. System returns FS data with full line-item breakdown

**Alternative Paths**:
- **A1 — No prior period data**: Comparative column shows "—" with note
- **A2 — New entity (first period)**: No đầu năm data, all zeros
- **A3 — Map incomplete (unmapped accounts)**: Flag unmapped accounts, exclude from FS, warn user
- **A4 — Balance sheet imbalance**: Reject generation, show imbalance amount

**Exception Paths**:
- **E1 — Period closed**: Error "Cannot generate FS for closed period"
- **E2 — Period has unposted entries**: Warning + option to include unposted or require posting
- **E3 — No GL data for period**: Warning "No transactions found for period"
- **E4 — Account mapping missing**: Error "FS mapping not configured for account type"

**B01-DN Structure**:
```
Mã số 100 — TÀI SẢN NGẮN HẠN
  110 — Tiền và các khoản tương đương tiền
  111 — Tiền
  112 — Các khoản tương đương tiền
  120 — Đầu tư tài chính ngắn hạn
  130 — Các khoản phải thu ngắn hạn
  140 — Hàng tồn kho
  150 — Tài sản ngắn hạn khác
Mã số 200 — TÀI SẢN DÀI HẠN
  210 — Các khoản phải thu dài hạn
  220 — Tài sản cố định
  230 — Bất động sản đầu tư
  240 — Tài sản dở dang dài hạn
  250 — Đầu tư tài chính dài hạn
  260 — Tài sản dài hạn khác
Mã số 270 — TỔNG TÀI SẢN
Mã số 300 — NỢ PHẢI TRẢ
  310 — Nợ ngắn hạn
  330 — Nợ dài hạn
Mã số 400 — VỐN CHỦ SỞ HỮU
  410 — Vốn góp của chủ sở hữu
  420 — Thặng dư vốn cổ phần
  430 — Lợi nhuận sau thuế chưa phân phối
  440 — TỔNG NGUỒN VỐN
```

---

### UC-FS-02: Generate B02-DN (Báo cáo kết quả hoạt động kinh doanh)

**Description**: Generate Income Statement per TT99 B02-DN format.

**Happy Path**:
1. User selects period
2. System queries revenue/expense account balances
3. System calculates: Doanh thu (Mã số 01) → Lợi nhuận gộp (Mã số 20) → Lợi nhuận thuần (Mã số 30) → Lợi nhuận kế toán trước thuế (Mã số 50) → Lợi nhuận sau thuế (Mã số 60)
4. System populates columns: Năm nay / Năm trước

**B02-DN Structure**:
```
Mã số 01 — Doanh thu bán hàng và cung cấp dịch vụ
Mã số 02 — Các khoản giảm trừ doanh thu
Mã số 10 — Doanh thu thuần (10 = 01 - 02)
Mã số 11 — Giá vốn hàng bán
Mã số 20 — Lợi nhuận gộp (20 = 10 - 11)
Mã số 21 — Doanh thu hoạt động tài chính
Mã số 22 — Chi phí tài chính
Mã số 23 — Chi phí bán hàng
Mã số 24 — Chi phí quản lý doanh nghiệp
Mã số 30 — Lợi nhuận thuần từ HĐKD (30 = 20 + 21 - 22 - 23 - 24)
Mã số 40 — Thu nhập khác
Mã số 41 — Chi phí khác
Mã số 50 — Lợi nhuận kế toán trước thuế (50 = 30 + 40 - 41)
Mã số 51 — Chi phí thuế TNDN hiện hành
Mã số 52 — Chi phí thuế TNDN hoãn lại
Mã số 60 — Lợi nhuận sau thuế TNDN (60 = 50 - 51 - 52)
Mã số 70 — Lãi cơ bản trên cổ phiếu
```

---

### UC-FS-03: Generate B03-DN (Báo cáo lưu chuyển tiền tệ)

**Description**: Generate Cash Flow Statement per TT99 B03-DN (both direct and indirect methods).

**Happy Path (Direct)**:
1. System collects cash receipts/payments from cash module
2. Classifies into: Lưu chuyển tiền từ HĐKD, HĐĐT, HĐTC
3. Calculates: Tiền thu từ bán hàng, tiền chi cho nhà cung cấp, tiền trả lương, tiền trả lãi vay, tiền nộp thuế TNDN
4. Computes: Lưu chuyển tiền thuần → Tiền đầu kỳ → Tiền cuối kỳ

**Happy Path (Indirect)**:
1. Starts with LNST (Mã số 60 from B02-DN)
2. Adjusts for non-cash items (khấu hao, dự phòng, lãi/lỗ chênh lệch tỷ giá)
3. Adjusts for changes in working capital
4. Arrives at same net cash flow as direct method

**B03-DN Structure**:
```
Mã số 01 — Lưu chuyển tiền từ HĐKD (direct)
  01 — Tiền thu từ bán hàng
  02 — Tiền chi cho nhà cung cấp
  03 — Tiền chi trả lương
  04 — Tiền chi trả lãi vay
  05 — Tiền chi nộp thuế TNDN
Mã số 20 — Lưu chuyển tiền từ HĐĐT
Mã số 30 — Lưu chuyển tiền từ HĐTC
Mã số 50 — Lưu chuyển tiền thuần trong kỳ
Mã số 60 — Tiền đầu kỳ
Mã số 70 — Tiền cuối kỳ
```

---

### UC-FS-04: Generate B09-DN (Bản thuyết minh BCTC)

**Description**: Generate Notes to Financial Statements per TT99 B09-DN.

**Happy Path**:
1. System collects data from all modules
2. Populates sections: Đặc điểm hoạt động, Chính sách kế toán, Thông tin bổ sung
3. Each section has mã số and structured line items
4. Supports text, numeric, and percentage fields

**B09-DN Sections (30+)**:
```
I. Đặc điểm hoạt động của doanh nghiệp
II. Kỳ kế toán, đơn vị tiền tệ sử dụng
III. Chuẩn mực và chế độ kế toán áp dụng
IV. Các chính sách kế toán áp dụng
  - Nguyên tắc ghi nhận tiền và các khoản tương đương
  - Nguyên tắc ghi nhận hàng tồn kho
  - Nguyên tắc ghi nhận TSCĐ và khấu hao
  - Nguyên tắc ghi nhận doanh thu
  - ...
V-VIII. Thông tin bổ sung cho các khoản mục trên B01
IX-XI. Thông tin bổ sung cho các khoản mục trên B02
XII-XIV. Thông tin bổ sung cho các khoản mục trên B03
XV-XIX. Thông tin khác (công cụ tài chính, bên liên quan, ...)
```

---

### UC-FS-05: FS Approval Workflow

**Description**: Multi-step approval process for FS sign-off.

**Roles**:
- **Người lập (Drafter)**: Creates FS draft
- **Kế toán trưởng (Chief Accountant)**: Reviews, approves
- **Tổng giám đốc (CEO/Director)**: Final sign-off

**States**: `DRAFT` → `IN_REVIEW` → `REVIEWED` → `APPROVED` → `SIGNED`

**Happy Path**:
1. Drafter generates FS → status DRAFT
2. Drafter submits for review → IN_REVIEW
3. Chief Accountant reviews → REVIEWED (or REJECTED → back to DRAFT)
4. Chief Accountant approves → APPROVED
5. CEO signs → SIGNED (PDF with digital signatures)
6. FS locked — no further edits

**Alternative Paths**:
- **Rejection**: FS returns to DRAFT with rejection reason
- **Delegate**: Approver may delegate to deputy
- **Batch sign**: CEO signs multiple FS in one operation

---

### UC-FS-06: FS Versioning & Audit Trail

**Description**: Track all changes to FS with full version history.

**Happy Path**:
1. Each generation creates version record
2. Approval actions logged with timestamp + user + action
3. Modification of signed FS creates new version (v2, v3...)
4. System stores complete version diff (line-item level)

**Audit Events**:
- FS_CREATED, FS_SUBMITTED, FS_REVIEWED, FS_APPROVED, FS_SIGNED
- FS_REJECTED, FS_AMENDED, FS_EXPORTED
- FS_VERSION_CREATED, FS_DELETED

---

### UC-FS-07: FS Export (PDF/Excel/HTML)

**Description**: Export FS in multiple formats.

**Happy Path**:
1. User selects period, statement type, format
2. System generates TT99-compliant formatted output
3. PDF: A4 portrait/landscape, proper Vietnamese typography (font, spacing)
4. Excel: Exact TT99 biểu mẫu layout with formulas
5. HTML: Web-responsive view with expand/collapse

**Rules**:
- PDF includes signature blocks: Người lập (ký, họ tên), Kế toán trưởng (ký, họ tên), Tổng giám đốc (ký, họ tên, đóng dấu)
- Vietnam locale number format: 1.234.567.890,50
- Date format: Ngày ... tháng ... năm ...

---

### UC-FS-08: GL-to-FS Mapping Configuration

**Description**: Configure which COA accounts map to which FS line items.

**Happy Path**:
1. Admin assigns COA accounts to FS mã số
2. Multiple accounts can map to one FS line (sum)
3. Supports percentage allocation (account → 60% FS-line-A + 40% FS-line-B)
4. Supports negative mapping (contra accounts)

**Data**:
- FS_MAPPING: fs_code, account_code, weight (%), direction (debit/credit/both)

---

### UC-FS-09: Multi-Entity Consolidation (Phase 2)

**Description**: Consolidate FS from multiple legal entities.

**Happy Path**:
1. Define consolidation group (parent + subsidiaries)
2. System collects individual entity FS
3. Applies consolidation adjustments (intercompany elimination, NCI)
4. Produces consolidated FS per VAS/IFRS

**Rules**:
- Eliminate intercompany balances
- Eliminate intercompany transactions
- Calculate NCI (non-controlling interest) per VAS 25/IFRS 10
- FX translation per VAS 10/IFRS 21

---

### UC-FS-10: DNKLT Generation (Phase 2)

**Description**: Generate non-going-concern FS per TT99 B01-DNKLT → B09-DNKLT.

**Happy Path**:
1. Entity flagged as "not meeting going-concern assumption"
2. System uses liquidation basis instead of going concern
3. Assets valued at net realizable value
4. Separate templates applied

---

### UC-FS-11: Interim FS (Phase 2)

**Description**: Generate interim financial reports per TT99.

**Full (B01a-DN → B09a-DN)**: Same as annual but for shorter period.
**Condensed (B01b-DN → B03b-DN)**: Selected line items only.

---

### UC-FS-12: FS Analysis & Ratios

**Description**: Compute financial ratios from FS data.

**Ratios**:
| Ratio | Formula | VAS Ref |
|-------|---------|---------|
| Current ratio | TS ngắn hạn / Nợ ngắn hạn | VAS 01 |
| Quick ratio | (TS ngắn hạn - HTK) / Nợ ngắn hạn | VAS 01 |
| Debt-to-equity | Tổng nợ / VCSH | VAS 01 |
| ROA | LNST / Tổng tài sản bình quân | VAS 01 |
| ROE | LNST / VCSH bình quân | VAS 01 |
| Gross margin | LN gộp / Doanh thu thuần | VAS 01 |
| Net margin | LNST / Doanh thu thuần | VAS 01 |

---

### UC-FS-13: IFRS 18 Convergence (Phase 2)

**Description**: Map VAS TT99 FS to IFRS 18 presentation.

**Mapping**:
- B01-DN → IFRS 18 Statement of Financial Position
- B02-DN → IFRS 18 Statement of Profit or Loss (with operating profit subtotal)
- B03-DN → IAS 7 Statement of Cash Flows (no change)
- B09-DN → IFRS 18 Notes (with MPM disclosure per para 121-125)

---

### UC-FS-14: FS e-Submission (Phase 2)

**Description**: Submit FS to regulatory portals.

**Targets**:
- GDT (thuedientu.gdt.gov.vn): Annual FS submission
- Statistics Bureau: Statistical FS
- Tax authorities: FS attached to CIT finalization

**Formats**: PDF (signed), XBRL (future)

---

## 7. BUSINESS RULES

### BR-FS-01: Balance Sheet Identity
`Total Assets = Total Liabilities + Equity` within ±0.001 VND tolerance

### BR-FS-02: Income Statement Check
`Net Profit (Mã số 60) = Profit Before Tax (Mã số 50) - Current Tax (Mã số 51) - Deferred Tax (Mã số 52)`

### BR-FS-03: Cash Flow Check
`Tiền cuối kỳ (Mã số 70) = Tiền đầu kỳ (Mã số 60) + Lưu chuyển tiền thuần (Mã số 50)`
AND `Tiền cuối kỳ = Cash balance in GL (TK 111+112)`

### BR-FS-04: Cross-Statement Consistency
`LNST (B02 Mã số 60) = Retained earnings change (B01 Mã số 430) +/- Dividends`  
`Cash & equivalents (B01 Mã số 110) = Tiền cuối kỳ (B03 Mã số 70)`

### BR-FS-05: Period-Locked Generation
FS can only be generated for open periods. Closed periods require reopen.

### BR-FS-06: Version Lock
Approved/Signed FS cannot be modified. Amendments create new version.

### BR-FS-07: Signature Requirement
Signed FS must have: Người lập + Kế toán trưởng + Tổng giám đốc (or authorized delegates).

### BR-FS-08: Comparative Data
FS always shows current period + prior period (năm nay / năm trước) data.

### BR-FS-09: Materiality Threshold
Items <5% of total category may be aggregated. Per TT99 Điều 19.

### BR-FS-10: Submission Deadline
Quarterly: 20 days after quarter end (TT99 Điều 18)  
Year-end: 90 days after fiscal year end

---

## 8. DATA MODEL

### 8.1 Domain Entities

```python
# ===== Core FS Entities =====

class FinancialStatementType(str, Enum):
    BALANCE_SHEET_GC = "B01_DN"           # Going concern
    BALANCE_SHEET_NGC = "B01_DNKLT"       # Non-going concern
    INCOME_STATEMENT_GC = "B02_DN"
    INCOME_STATEMENT_NGC = "B02_DNKLT"
    CASH_FLOW_GC = "B03_DN"
    CASH_FLOW_NGC = "B03_DNKLT"
    NOTES_GC = "B09_DN"
    NOTES_NGC = "B09_DNKLT"
    INTERIM_FULL_BALANCE = "B01a_DN"
    INTERIM_FULL_INCOME = "B02a_DN"
    INTERIM_FULL_CASHFLOW = "B03a_DN"
    INTERIM_FULL_NOTES = "B09a_DN"
    INTERIM_CONDENSED_BALANCE = "B01b_DN"
    INTERIM_CONDENSED_INCOME = "B02b_DN"
    INTERIM_CONDENSED_CASHFLOW = "B03b_DN"

class FSStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    SIGNED = "SIGNED"
    REJECTED = "REJECTED"
    AMENDED = "AMENDED"

class FSLineItem(BaseModel):
    ma_so: str                          # Mã số chỉ tiêu (e.g., "100", "110")
    ten_chi_tieu: str                   # Tên chỉ tiêu
    so_thu_tu: int                      # Số thứ tự
    parent_ma_so: Optional[str]         # Parent mã số (for hierarchy)
    current_year: Decimal               # Năm nay
    previous_year: Optional[Decimal]    # Năm trước
    is_subtotal: bool = False           # Is this a subtotal/total line?
    is_calculated: bool = False         # Auto-calculated (not direct input)
    calculation_formula: Optional[str]  # Formula if calculated

class FinancialStatement(BaseModel):
    id: Optional[int] = None
    entity_id: int
    period: str                         # YYYY-MM (for monthly) or YYYY (for annual)
    statement_type: FinancialStatementType
    lines: List[FSLineItem]            # Structured line items
    status: FSStatus = FSStatus.DRAFT
    version: int = 1
    approved_by: Optional[str] = None
    approval_date: Optional[date] = None
    signed_by: Optional[str] = None
    signed_date: Optional[date] = None
    generated_by: Optional[str] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_consolidated: bool = False
    consolidation_group_id: Optional[int] = None
    notes: Optional[str] = None

class FSAuditLog(BaseModel):
    id: Optional[int] = None
    fs_id: int
    action: str                         # CREATED, SUBMITTED, APPROVED, SIGNED, REJECTED, AMENDED
    user: str
    timestamp: datetime
    details: Optional[str] = None
    version: int

class FSAccountMapping(BaseModel):
    id: Optional[int] = None
    fs_ma_so: str                       # FS mã số
    account_code: str                   # COA account code
    weight: Decimal = Decimal("1.00")    # Allocation weight
    direction: str = "both"             # debit, credit, both
    statement_type: FinancialStatementType

class FSConsolidationGroup(BaseModel):
    id: Optional[int] = None
    name: str
    parent_entity_id: int
    subsidiary_ids: List[int]
    consolidation_method: str = "full"  # full, equity, proportional
    ownership_percentages: Dict[int, Decimal]

class FSConsolidationAdjustment(BaseModel):
    id: Optional[int] = None
    period: str
    group_id: int
    adjustment_type: str                # intercompany_elimination, NCI, FX
    line_items: List[FSLineItem]
    created_by: str
    created_at: datetime
```

### 8.2 Database Tables

```sql
CREATE TABLE fs_statements (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL,
    period VARCHAR(7) NOT NULL,
    statement_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    version INTEGER NOT NULL DEFAULT 1,
    approved_by VARCHAR(100),
    approval_date DATE,
    signed_by VARCHAR(100),
    signed_date DATE,
    generated_by VARCHAR(100),
    generated_at TIMESTAMP DEFAULT NOW(),
    is_consolidated BOOLEAN DEFAULT FALSE,
    consolidation_group_id INTEGER,
    notes TEXT,
    data JSONB,                        -- Full FS line items JSON
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE fs_line_items (
    id SERIAL PRIMARY KEY,
    fs_id INTEGER REFERENCES fs_statements(id),
    ma_so VARCHAR(10) NOT NULL,
    ten_chi_tieu VARCHAR(500) NOT NULL,
    so_thu_tu INTEGER NOT NULL,
    parent_ma_so VARCHAR(10),
    current_year NUMERIC(18,2) DEFAULT 0,
    previous_year NUMERIC(18,2),
    is_subtotal BOOLEAN DEFAULT FALSE,
    is_calculated BOOLEAN DEFAULT FALSE,
    calculation_formula VARCHAR(200)
);

CREATE TABLE fs_audit_log (
    id SERIAL PRIMARY KEY,
    fs_id INTEGER REFERENCES fs_statements(id),
    action VARCHAR(50) NOT NULL,
    user VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    details TEXT,
    version INTEGER
);

CREATE TABLE fs_account_mapping (
    id SERIAL PRIMARY KEY,
    fs_ma_so VARCHAR(10) NOT NULL,
    account_code VARCHAR(10) NOT NULL,
    weight NUMERIC(5,2) DEFAULT 1.00,
    direction VARCHAR(10) DEFAULT 'both',
    statement_type VARCHAR(20) NOT NULL,
    UNIQUE(account_code, fs_ma_so, statement_type)
);

CREATE TABLE fs_consolidation_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    parent_entity_id INTEGER NOT NULL,
    consolidation_method VARCHAR(20) DEFAULT 'full'
);

CREATE TABLE fs_consolidation_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES fs_consolidation_groups(id),
    entity_id INTEGER NOT NULL,
    ownership_percentage NUMERIC(5,2) NOT NULL,
    consolidation_method VARCHAR(20) DEFAULT 'full'
);

CREATE TABLE fs_consolidation_adjustments (
    id SERIAL PRIMARY KEY,
    period VARCHAR(7) NOT NULL,
    group_id INTEGER REFERENCES fs_consolidation_groups(id),
    adjustment_type VARCHAR(50) NOT NULL,
    adjustment_data JSONB,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 9. DATA FLOW DIAGRAMS

### 9.1 FS Generation Data Flow

```
GL Journal Entries (posted)
    │
    ▼
GL Repository: get_account_balance(account_id, period)
    │
    ▼
COA Accounts → FS Account Mapping
    │
    ▼
Aggregate by FS mã số (sum all accounts mapped to same mã số)
    │
    ▼
Calculate subtotals (Mã số 100, 200, 270, 300, 400, 440)
    │
    ▼
Verify balance sheet identity (A = L + E)
    │
    ▼
Populate comparative column from prior period FS
    │
    ▼
Create FinancialStatement (status DRAFT)
    │
    ▼
Return to user / Trigger approval workflow
```

### 9.2 Cash Flow (Indirect Method) Data Flow

```
B02 LNST (Mã số 60)
    │
    ▼
+ Non-cash adjustments (depreciation, provisions, FX)
    │
    ▼
± Working capital changes (receivables, inventory, payables)
    │
    ▼
= Cash from operations (Mã số 01 indirect)
    │
    ▼
± Investing activities (FA purchases/sales, investments)
    │
    ▼
± Financing activities (loans, equity, dividends)
    │
    ▼
= Net cash flow (Mã số 50)
    │
    ▼
+ Opening cash (Mã số 60)
    │
    ▼
= Closing cash (Mã số 70)
```

### 9.3 Approval Workflow Data Flow

```
Drafter                    Kế toán trưởng               Tổng giám đốc
    │                           │                           │
    │-- DRAFT --> Review ------>│-- APPROVED --> Sign ----->│-- SIGNED
    │                           │                           │
    │<-- REJECTED --------------│                           │
```

---

## 10. WORKFLOWS

### 10.1 Month-End FS Workflow

```
1. Post all journal entries for period
2. Run GL account balance verification
3. Auto-generate B01-DN, B02-DN, B03-DN draft
4. Fill in B09-DN notes (manual + auto)
5. Review FS for accuracy
6. Chief Accountant approves
7. CEO signs
8. Export signed PDF
9. Submit to authorities (if annual)
10. Close period (blocks further entries)
```

### 10.2 Year-End FS Workflow

Includes all month-end steps plus:
- Carry forward revenue/expense to 911 → 421
- Generate annual FS (full year data)
- External audit review
- Board approval
- Submission to tax authority + statistics
- Public disclosure (if listed company)

---

## 11. USER JOURNEYS

### 11.1 Chief Accountant: Monthly FS Close

1. Receives notification "Period 2026-05 ready for FS generation"
2. Clicks "Generate FS" → system creates B01, B02, B03 drafts
3. Reviews line items on-screen with drill-down to GL detail
4. Compares to prior period — flags 15% increase in receivables
5. Investigates: opens AR aging report, identifies customer late payments
6. Adjusts provision for doubtful debts (new journal entry)
7. Re-generates FS with updated data
8. Notifies CFO of unusual movement
9. Approves FS → status APPROVED
10. System sends notification to CEO for signing

### 11.2 CEO: Year-End FS Sign-off

1. Logs in for year-end FS sign-off (April 2026 for FY2025)
2. Sees dashboard: 3 entities ready for signing
3. Opens consolidated FS — reviews highlights vs prior year
4. Drills into revenue breakdown by segment
5. Confirms no material issues
6. Signs digitally (RSA-SHA256 via signing service)
7. System generates signed PDF with timestamp + digital signatures
8. PDF automatically submitted to GDT portal
9. Receives confirmation receipt from GDT

---

## 12. REPORT TEMPLATES PER TT 99/2025

### 12.1 Template Files Required

| Template | File | Description |
|----------|------|-------------|
| B01-DN | `templates/fs/b01_dn.html` | Balance sheet - going concern |
| B02-DN | `templates/fs/b02_dn.html` | Income statement |
| B03-DN-direct | `templates/fs/b03_dn_direct.html` | Cash flow - direct |
| B03-DN-indirect | `templates/fs/b03_dn_indirect.html` | Cash flow - indirect |
| B09-DN | `templates/fs/b09_dn.html` | Notes to FS |
| B01-DNKLT | `templates/fs/b01_dnklt.html` | Balance sheet - non-going concern |
| B02-DNKLT | `templates/fs/b02_dnklt.html` | Income statement - non-going concern |
| B03-DNKLT | `templates/fs/b03_dnklt.html` | Cash flow - non-going concern |
| B09-DNKLT | `templates/fs/b09_dnklt.html` | Notes - non-going concern |
| Interim | `templates/fs/b01a_dn.html` + ... | Interim reports |

### 12.2 Template Structure (Jinja2)

```html
{# templates/fs/b01_dn.html #}
{% extends "fs/base_fs.html" %}
{% block content %}
<div class="fs-report">
    <div class="fs-header">
        <div class="entity-info">
            <p><strong>{{ entity.name }}</strong></p>
            <p>Địa chỉ: {{ entity.address }}</p>
        </div>
        <div class="report-title">
            <h1>BÁO CÁO TÌNH HÌNH TÀI CHÍNH</h1>
            <p><em>(Tại ngày {{ period.end_date | vietnamese_date }})</em></p>
            <p>Mẫu số B 01 – DN</p>
        </div>
        <div class="unit-info">
            <p>Đơn vị tính: {{ currency_unit }}</p>
        </div>
    </div>

    <table class="fs-table">
        <thead>
            <tr>
                <th>Mã số</th>
                <th>Chỉ tiêu</th>
                <th>Thuyết minh</th>
                <th>Cuối năm</th>
                <th>Đầu năm</th>
            </tr>
        </thead>
        <tbody>
            {% for line in lines %}
            <tr class="{{ 'subtotal' if line.is_subtotal else 'detail' }}">
                <td>{{ line.ma_so }}</td>
                <td>{{ line.ten_chi_tieu }}</td>
                <td>{{ line.thuyet_minh or '' }}</td>
                <td class="amount">{{ line.cuoi_nam | vnd_format }}</td>
                <td class="amount">{{ line.dau_nam | vnd_format if line.dau_nam else '—' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <div class="signature-block">
        <table class="signatures">
            <tr>
                <td>
                    <p><strong>Người lập</strong></p>
                    <p><em>(Ký, họ tên)</em></p>
                    <div class="sig-space"></div>
                    <p>{{ signature.drafter }}</p>
                </td>
                <td>
                    <p><strong>Kế toán trưởng</strong></p>
                    <p><em>(Ký, họ tên)</em></p>
                    <div class="sig-space"></div>
                    <p>{{ signature.chief_accountant }}</p>
                </td>
                <td>
                    <p><strong>Tổng giám đốc</strong></p>
                    <p><em>(Ký, họ tên, đóng dấu)</em></p>
                    <div class="sig-space"></div>
                    <p>{{ signature.ceo }}</p>
                </td>
            </tr>
        </table>
    </div>

    <div class="fs-footer">
        <p>Ngày ... tháng ... năm ...</p>
    </div>
</div>
{% endblock %}
```

---

## 13. GL POSTING MATRIX

### 13.1 B01-DN Account Mapping

| FS Mã số | Chỉ tiêu | COA Accounts (TT99) | D/N |
|----------|----------|---------------------|-----|
| 110 | Tiền và tương đương tiền | 111, 112 | N |
| 120 | Đầu tư TC ngắn hạn | 121, 128 | N |
| 130 | Phải thu ngắn hạn | 131, 133, 136, 137, 138, 141 | N |
| 140 | Hàng tồn kho | 151, 152, 153, 154, 155, 156, 157 | N |
| 150 | Tài sản NH khác | 242, 331, 333, 334, 335, 336, 338 | N |
| 210 | Phải thu dài hạn | 211, 212, 213, 218 | N |
| 220 | TSCĐ | 221, 222, 223, 224, 227 | N |
| 310 | Nợ ngắn hạn | 311, 312, 313, 314, 315, 318, 319, 321, 322, 323, 337 | D |
| 330 | Nợ dài hạn | 331, 332, 333, 334, 335, 336, 337, 338, 339 | D |
| 410 | Vốn góp CSH | 4111, 4112 | D |
| 430 | LN chưa phân phối | 421 | D |

### 13.2 B02-DN Account Mapping

| FS Mã số | Chỉ tiêu | COA Accounts (TT99) |
|----------|----------|---------------------|
| 01 | Doanh thu bán hàng | 5111, 5112, 5113 |
| 02 | Giảm trừ doanh thu | 5211, 5212, 5213 |
| 11 | Giá vốn hàng bán | 632 |
| 21 | Doanh thu HĐTC | 515 |
| 22 | Chi phí tài chính | 635 |
| 23 | Chi phí bán hàng | 641 |
| 24 | Chi phí QLDN | 642 |
| 40 | Thu nhập khác | 711 |
| 41 | Chi phí khác | 811 |
| 51 | Chi phí thuế TNDN | 821 |

---

## 14. NON-FUNCTIONAL REQUIREMENTS

| Requirement | Target |
|-------------|--------|
| Response time (FS generation) | <5s for 10,000 GL lines |
| Response time (FS view) | <2s |
| Concurrent users | 50 |
| PDF generation | <10s per report |
| Data retention | 10 years (per Luật Kế toán) |
| Audit trail | Immutable logs |
| Security | Role-based access (drafter/reviewer/approver/signer) |
| Digital signature | RSA-SHA256 integration with signing_service.py |

---

## 15. IMPLEMENTATION ROADMAP

### Phase 1 — MVP (8 weeks)

| Task | Duration | Dependencies |
|------|----------|-------------|
| Domain entities design | 1 week | None |
| FS Account mapping config | 1 week | Domain |
| B01-DN generation engine | 2 weeks | GL Repository |
| B02-DN generation engine | 1 week | GL Repository |
| B03-DN generation engine | 2 weeks | Cash Repository |
| B09-DN (core) | 2 weeks | All modules |
| FS CRUD repository | 1 week | Domain |
| FS routes (basic) | 1 week | Use cases |
| PDF export | 1 week | Templates |
| Approval workflow | 1 week | FS Repository |
| Audit trail | 0.5 week | FS Repository |
| Tests | Parallel | All |

### Phase 2 — Enhancement (4 weeks)

| Task | Duration |
|------|----------|
| DNKLT templates | 1 week |
| Interim reports | 1 week |
| Multi-entity consolidation | 2 weeks |
| Financial ratios | 0.5 week |
| Excel export | 0.5 week |

### Phase 3 — Advanced (4 weeks)

| Task | Duration |
|------|----------|
| IFRS 18 convergence | 2 weeks |
| e-Submission (GDT) | 1 week |
| XBRL export | 1 week |
| FS dashboard | 1 week |

---

## 16. APPENDIX: LEGAL REFERENCES

### Primary Documents
- **TT 99/2025/TT-BTC**: Điều 17 (FS system), Điều 18 (FS deadlines), Điều 19 (FS presentation requirements), Phụ lục IV (FS templates)
- **Luật Kế toán 89/2025/QH15** (eff. 01/01/2026): Articles on FS preparation and disclosure
- **VAS 01**: Framework for preparation of FS
- **VAS 21**: Presentation of FS (currently aligned with IAS 1, will align with IFRS 18)
- **IFRS 18** (eff. 01/01/2027): Presentation and Disclosure in FS

### Replaced Documents (Verified Outdated)
- ❌ TT 200/2014/TT-BTC (replaced by TT 99/2025)
- ❌ TT 75/2015/TT-BTC (amendment to TT200, now superseded)
- ❌ TT 53/2016/TT-BTC (amendment to TT200, now superseded)
- ❌ TT 195/2012/TT-BTC (investment accounting, replaced by TT99)

### Verification Sources
- `vbpl.vn` — National legal database (VBPL) — TT99 confirmed active
- `mof.gov.vn` — Ministry of Finance — TT99 published
- `thuedientu.gdt.gov.vn` — GDT eTax portal — FS submission guidelines
- `ifrs.org` — IFRS 18 effective 01/01/2027, active development
- `vacpa.org.vn` — VACPA audit standards reference
- `vaa.net.vn` — VAA accounting standards updates

---

*End of BRD — Financial Statement Module*
