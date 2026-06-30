# BRD: Tools & Equipment (Công cụ, Dụng cụ — CCDC) Module
## SmartACCT ERP — Vietnamese Accounting System

**Version:** 1.0
**Date:** 2026-06-30
**Author:** Lead BA (20+ yrs) + Chief Accountant (20+ yrs)
**Status:** DRAFT — Pending Implementation

---

## 1. Executive Summary

### 1.1 Purpose

Build **Tools & Equipment (CCDC)** module for SmartACCT ERP. Manage full lifecycle of Công cụ, Dụng cụ: acquisition/receipt, warehouse storage, issue to production/admin/sales, cost allocation (1-time/2-time/multi-period up to 36 months), inventory/check, disposal/liquidation, and regulatory reporting per Vietnamese accounting regime **TT 99/2025/TT-BTC** (effective 01/01/2026, replacing TT 200/2014) and parallel reference **TT 133/2016/TT-BTC** for SMEs.

### 1.2 Current State Assessment

**VERDICT: NOT PRODUCTION-READY. SCORE: 0/5**

CCDC module = **zero code**. No domain entities, use cases, repository, models, routes, or tests.

**What exists (usable but NOT CCDC):**
| Asset | Status | CCDC Reuse |
|-------|--------|------------|
| COA TK 153 (Công cụ, dụng cụ) | Account exists in ChartOfAccounts | Reuse for GL posting |
| COA TK 242 (Chi phí trả trước) | Account exists | Reuse for multi-period allocation |
| COA cost accounts (TK 621, 623, 627, 641, 642) | Defined | Reuse for allocation destination |
| JournalEntry (GL) | Full CRUD + period-gated posting | Reuse for CCDC→GL auto-post |
| FAUseCases (Fixed Assets) | Full module | Reference for TSCĐ vs CCDC boundary logic |
| Inventory FA models | FASparePart, FAComponent | Reference for inventory tracking pattern |

**Gap: EVERYTHING** — CCDC master data, receipt/import, issue/export, allocation engine (3 methods), inventory/kiểm kê, disposal/liquidation, report Form 07-VT, CCDC→GL auto-posting.

### 1.3 Scope

**In scope (UC-CCDC-01 through UC-CCDC-12):**
- UC-CCDC-01: CCDC Category & Master Data (type classification, unit, standard useful life)
- UC-CCDC-02: CCDC Receipt (purchase, self-made, contributed capital, donor, surplus from inventory)
- UC-CCDC-03: CCDC Issue to Use (one-time allocation, multi-period allocation via TK 242)
- UC-CCDC-04: CCDC Allocation Engine (1-time, 2-time equal split, multi-period ≤ 36 months)
- UC-CCDC-05: CCDC Return to Warehouse (from production, from rental)
- UC-CCDC-06: CCDC Transfer (between departments, between warehouses)
- UC-CCDC-07: CCDC Inventory/Count (annual/periodic, discrepancy handling: surplus/shortage/damage)
- UC-CCDC-08: CCDC Disposal/Liquidation (sale, scrap, donation, theft, destruction)
- UC-CCDC-09: CCDC→GL Auto-Posting (all CCDC transactions post to GL)
- UC-CCDC-10: CCDC Reporting (Form 07-VT allocation table, CCDC detailed ledger, usage by department)
- UC-CCDC-11: CCDC User Physical Responsibility Tracking (by holder, department, location)
- UC-CCDC-12: CCDC Lifecycle End (fully allocated, physically retired, write-off)

**Out of scope (v2.0+):**
- Barcode/RFID integration for physical tracking
- Procurement PO integration for CCDC purchase
- Direct integration with e-invoice (handled by existing Tax/E-Invoice module)
- Automated useful life suggestion based on historical data
- CCDC budget/planning module
- Mobile app for field inventory check

---

## 2. Regulatory & Compliance Framework

### 2.1 Primary Legislation — DOUBLE-CHECKED ✅ (as of 30/06/2026)

| Citation | Title | CCDC Impact | Status |
|----------|-------|-------------|--------|
| **TT 99/2025/TT-BTC** (27/10/2025) | Enterprise Accounting Regime (replaces TT 200/2014) | TK 153 — Công cụ, dụng cụ; TK 242 — Chi phí trả trước; allocation rules; Form 07-VT | **ACTIVE** from 01/01/2026 |
| **TT 200/2014/TT-BTC** (22/12/2014) | Enterprise Accounting Regime (superseded) | Điều 26 — TK 153 rules (historical reference) | **SUPERSEDED** by TT 99 |
| **TT 133/2016/TT-BTC** (26/08/2016) | SME Accounting Regime | Điều 25 — TK 153 rules for SMEs | **ACTIVE** for SMEs |
| **VAS 02 — Hàng tồn kho** (QĐ 149/2001/QĐ-BTC) | Inventory Standard | Cost measurement: actual cost, FIFO, weighted average, specific identification | **ACTIVE** |
| **Law on Accounting 88/2015/QH13** (as amended 2024) | Accounting Law | Art 10 — accounting principles; Art 16 — voucher requirements | **ACTIVE** |
| **TT 45/2013/TT-BTC** (as amended by 147/2016, 28/2017, 30/2025) | FA Management | Điều 3: TSCĐ criteria (≥30M VND, ≥1 year) — below = CCDC | **ACTIVE** — boundary definition |
| **NĐ 70/2025/NĐ-CP** (replacing NĐ 123/2020) | E-Invoice Decree | Input VAT deduction requires valid e-invoice + bank payment ≥20M VND | **ACTIVE** from 01/01/2026 |
| **TT 80/2021/TT-BTC** | Tax Administration | CCDC purchase cost deductibility; allocation period ≤36 months for tax purposes | **ACTIVE** |

### 2.2 Key Regulatory Changes (TT 99/2025 vs TT 200/2014) Affecting CCDC

| Area | TT 200/2014 | TT 99/2025 |
|------|-------------|------------|
| **TK 153 sub-accounts** | Mandatory: 1531 (CCDC), 1532 (Bao bì luân chuyển), 1533 (Đồ dùng cho thuê), 1534 (Thiết bị, phụ tùng thay thế) | **No mandated sub-accounts.** Enterprise may define sub-accounts per management needs. Must issue Accounting Policy Regulation. |
| **COA customization** | MOF approval required for COA changes | Enterprise autonomy with internal regulation |
| **TK 242 usage** | CCDC allocation via 242 for multi-period | **Preserved** — same treatment |
| **Form 07-VT** | Under Phụ lục 3 TT 200 | **Updated** — under Phụ lục I TT 99 (same form code, updated layout) |
| **Inventory method** | Perpetual and periodic inventory methods separate | **Standard cost method introduced**; periodic inventory concepts removed |
| **Spare parts >12 months** | Accounted as CCDC | Must classify as long-term assets (not CCDC) if storage exceeds 12 months or one operating cycle |
| **Financial statements** | Bảng CĐKT (Balance Sheet) | Báo cáo tình hình tài chính (Statement of Financial Position) |
| **Document autonomy** | Prescribed forms mandatory | Enterprise may adapt forms while meeting Art 16 Law on Accounting |

### 2.3 CCDC Recognition Criteria (TT 45/2013 Điều 3 + TT 99/2025)

**A labor tool is classified as CCDC (NOT Fixed Asset) if:**

1. Value < 30,000,000 VND **OR**
2. Useful life < 1 year **OR**
3. Does NOT meet ALL 4 TSCĐ criteria simultaneously

**Specific items ALWAYS classified as CCDC regardless of value** (TT 200 Điều 26, preserved in TT 99):
- Specialized molds, jigs, fixtures (khuôn mẫu, đồ gá)
- Packaging for circulation (bao bì luân chuyển)
- Items for rent (đồ dùng cho thuê)
- Protective equipment (bảo hộ lao động)
- Low-value office supplies (văn phòng phẩm giá trị lớn dùng nhiều kỳ)

### 2.4 CCDC vs Related Accounts Boundary

| Account | Name | CCDC Relationship |
|---------|------|-------------------|
| **TK 152** | Nguyên liệu, vật liệu | Raw materials consumed in production — NOT tracked as CCDC |
| **TK 153** | Công cụ, dụng cụ | **CCDC master account** — THIS MODULE |
| **TK 211** | TSCĐ hữu hình | Fixed Assets ≥30M + ≥1 year — see FA module |
| **TK 242** | Chi phí trả trước | Prepaid expenses — holds CCDC value during multi-period allocation |
| **TK 6233** | Chi phí dụng cụ sản xuất (TT99 — renamed from TT200) | Allocation DESTINATION — machine operation tools |
| **TK 6273** | Chi phí dụng cụ sản xuất | Allocation DESTINATION — production overhead tools |
| **TK 6413** | Chi phí dụng cụ, đồ dùng | Allocation DESTINATION — selling expenses tools |
| **TK 6423** | Chi phí đồ dùng văn phòng | Allocation DESTINATION — admin office supplies |
| **TK 621** | Chi phí NVL trực tiếp | Allocation DESTINATION — direct material (rare for CCDC) |

---

## 3. Business Rules & Concepts

### 3.1 CCDC Classification (TT 99/2025 — Enterprise-defined)

TT 99/2025 allows enterprises to define their own sub-account structure. Recommended multi-dimensional classification:

**Dimension 1 — By Physical Nature:**
| Code | Type | Example |
|------|------|---------|
| 01 | Molds & dies (Khuôn mẫu, đồ gá) | Injection molds, stamping dies |
| 02 | Circulation packaging (Bao bì luân chuyển) | Pallets, returnable containers |
| 03 | Rental items (Đồ dùng cho thuê) | Equipment rental |
| 04 | Tools & instruments (Dụng cụ, thiết bị) | Power tools, measuring instruments |
| 05 | Protective equipment (BHLĐ) | Helmets, gloves, safety gear |
| 06 | Office equipment (Đồ dùng VP) | Desk, chair, cabinet, fan |
| 07 | Replacement parts (Phụ tùng thay thế) | Spare parts for machinery |

**Dimension 2 — By Value/Allocation Method:**
| Category | Value Threshold | Default Allocation |
|----------|----------------|-------------------|
| Low-value CCDC | < 1,000,000 VND | 1-time to expense |
| Medium-value CCDC | 1,000,000 - 10,000,000 VND | 2-time or ≤12 months |
| High-value CCDC | 10,000,000 - < 30,000,000 VND | Multi-period ≤36 months |
| CCDC for rent | Any | Over rental period |
| Circulation packaging | Any | Over expected usage cycles |

### 3.2 Allocation Methods (Điều 26 TT 200 → TT 99)

**Method 1 — One-Time Allocation (Phân bổ 1 lần):**
- Full cost charged to expense immediately on issue
- Applies to: low-value CCDC, CCDC with single-use period
- Journal: Dr 6233/6273/6413/6423, Cr 153

**Method 2 — Two-Time Allocation (Phân bổ 2 lần):**
- 50% charged on issue, 50% on return/damage report
- Applies to: circulation packaging, rental items
- Journal on issue: Dr 242, Cr 153; Dr 6273/6413 (50%), Cr 242
- Journal on return: Dr 153, Cr 242 (50% remaining); Dr cost account, Cr 242 (remaining to expense)

**Method 3 — Multi-Period Allocation (Phân bổ nhiều kỳ):**
- Cost spread evenly over useful life (max 36 months)
- Journal on issue: Dr 242, Cr 153 (full value)
- Monthly allocation: Dr 6233/6273/6413/6423, Cr 242 (value / useful months)
- Period: from month of issue to month N (max 36 months)
- If CCDC is retired before full allocation: remaining value charged immediately

### 3.3 Cost Measurement (VAS 02)

**Purchase:**
- Actual cost = purchase price (ex-VAT if creditable) + import duties + transport + handling + installation + other directly attributable costs — trade discounts

**Self-manufactured:**
- Actual cost = direct materials + direct labor + manufacturing overhead allocated

**Contributed capital:**
- Fair value at contribution date as agreed by contributors

**Inventory valuation:**
- FIFO, Weighted Average, or Specific Identification (per VAS 02)

### 3.4 Key Rules

| Rule | Description | Violation Consequence |
|------|-------------|---------------------|
| R-01 | CCDC must be allocated — cannot sit in 153 indefinitely after issue | Distorted cost; audit finding |
| R-02 | Max allocation period = 36 months | Tax adjustment (disallowed expense) |
| R-03 | CCDC consumed within 1 period → 1-time allocation | Proper matching principle |
| R-04 | CCDC physically tracked by holder/department until fully allocated or disposed | Loss/theft unaccounted |
| R-05 | Annual inventory count mandatory per Law on Accounting | Legal non-compliance |
| R-06 | Surplus CCDC from inventory → recorded at fair value | Wrong valuation |
| R-07 | Shortage CCDC → responsible person compensation | Tax deduction only if documented |
| R-08 | CCDC conversion from TSCĐ (asset fails FA criteria) | Reclassification with proper documentation |
| R-09 | CCDC with storage >12 months classified as long-term assets (TT 99) | Balance sheet misclassification |
| R-10 | Enterprise must issue Accounting Policy Regulation for COA sub-accounts (TT 99) | Tax audit risk |

---

## 4. User Roles & Permissions

| Role | CCDC Permissions | Notes |
|------|------------------|-------|
| **Warehouse Keeper** | Create receipt/issue vouchers, view inventory | Execute physical movements |
| **CCDC Accountant** | Full CRUD: master data, allocation, inventory, disposal | Daily operations |
| **Chief Accountant** | Approve disposals, configure allocation templates, period-end close | Oversight |
| **Department Head** | View CCDC assigned to department, request issue/return | User department |
| **Internal Auditor** | Read-only: all CCDC data, audit trail | Compliance |
| **System Admin** | Configure CCDC categories, allocation methods, COA mapping | Setup |

---

## 5. Suggested Implementation Plan

### Phase 1 — Core (UC-CCDC-01 through UC-CCDC-05) — Est. 4 weeks
- Domain entities + enums
- SQLAlchemy models + migration
- Repository: CRUD + balance + allocation
- Use cases: Category CRUD, Receipt, Issue (1-time), Issue (multi-period via 242), Return
- GL auto-posting for receipt/issue/return

### Phase 2 — Lifecycle (UC-CCDC-06 through UC-CCDC-09) — Est. 3 weeks
- Transfer between departments/warehouses
- Inventory/kiểm kê: count input, discrepancy calculation, surplus/shortage/damage → GL
- Disposal: sale, scrap, donation, theft
- Allocation engine: monthly batch for multi-period CCDC (auto-calc)
- CCDC→GL full integration (all transaction types)

### Phase 3 — Reporting & Admin (UC-CCDC-10 through UC-CCDC-12) — Est. 2 weeks
- Form 07-VT: Bảng phân bổ nguyên liệu, vật liệu, công cụ, dụng cụ
- CCDC detailed ledger by item/warehouse/department
- CCDC usage report by cost center
- User physical responsibility tracking
- Lifecycle end / write-off for fully-allocated CCDC

### Phase 4 — API & Testing — Est. 2 weeks
- Flask routes (REST API)
- Integration tests
- API documentation

**Total: ~11 weeks to MVP**

---

## 6. Data Model Overview

### 6.1 Core Entities

```
CCDCCategory
├── id, code, name_vn, description
├── default_allocation_method (one_time/two_time/multi_period)
├── default_useful_months (max 36)
├── account_sub_type (1531/1532/1533/1534 — enterprise-defined)
├── is_active
└── parent_category_id (self-referencing hierarchy)

ToolEquipment (CCDC Master)
├── id, code, name_vn, specification
├── category_id → CCDCCategory
├── unit_of_measure
├── quantity_in_stock
├── unit_cost (giá gốc)
├── total_cost
├── location (kho)
├── image_url
├── is_valuable_item (quý hiếm — special handling)
├── status (in_stock/issued/disposed)
└── custom_fields (JSON — enterprise-defined)

CCDCReceipt (Nhập kho)
├── id, receipt_date, receipt_type (purchase/self_made/contribution/donor/inventory_surplus/return)
├── document_ref (hóa đơn/chứng từ number)
├── warehouse_keeper_id
├── total_amount
├── notes
├── status (draft/posted/cancelled)
└── lines[] → CCDCReceiptLine
    ├── tool_equipment_id
    ├── quantity, unit_price
    ├── vat_rate, vat_amount
    └── total_line

CCDCissue (Xuất kho)
├── id, issue_date, issue_type (production/admin/sales/rental/transfer)
├── department_id, responsible_person_id
├── allocation_method (one_time/two_time/multi_period)
├── useful_months (for multi-period)
├── total_value
├── status (draft/posted/cancelled)
└── lines[] → CCDCissueLine
    ├── tool_equipment_id
    ├── quantity, unit_price
    ├── total_line
    └── allocation_detail → CCDCAllocation

CCDCAllocation (Phân bổ)
├── id, source_issue_id
├── tool_equipment_id
├── total_value, allocated_value, remaining_value
├── method (one_time/two_time/multi_period)
├── start_date, end_date
├── useful_months
├── monthly_amount
├── current_period_number
├── status (active/fully_allocated/suspended)
└── lines[] → CCDCAllocationLine (monthly detail)
    ├── period_year, period_month
    ├── allocated_amount
    ├── cost_account_id (TK 6233/6273/6413/6423)
    ├── department_id
    ├── gl_posting_id
    └── status (pending/posted)

CCDCTransfer (Điều chuyển)
├── id, transfer_date
├── from_department_id, to_department_id
├── from_warehouse, to_warehouse
├── responsible_person_from, responsible_person_to
├── status
└── lines[] → CCDCTransferLine

CCDCInventory (Kiểm kê)
├── id, count_date
├── committee_members[] (JSON)
├── status (in_progress/completed/approved)
└── lines[] → CCDCInventoryLine
    ├── tool_equipment_id
    ├── book_quantity, actual_quantity
    ├── damaged_quantity
    ├── difference (surplus/shortage/damage)
    ├── handling_recommendation
    └── gl_posting_for_discrepancy_id

CCDCDisposal (Thanh lý)
├── id, disposal_date
├── disposal_type (sale/scrap/donation/theft/destruction)
├── approval_document
├── proceeds_amount (for sale)
├── expense_amount
├── status (draft/approved/executed/cancelled)
└── lines[] → CCDCDisposalLine
    ├── tool_equipment_id
    ├── quantity, remaining_value
    ├── proceeds
    └── gl_posting_id
```

### 6.2 GL Posting Matrix

| Transaction | Debit | Credit | Notes |
|-------------|-------|--------|-------|
| CCDC purchase receipt | 153 (cost) + 1331 (VAT if deductible) | 111/112/331 | Per receipt |
| CCDC issue — 1-time allocation | 6233/6273/6413/6423 | 153 | Full value |
| CCDC issue — multi-period | 242 | 153 | Full value to prepaid |
| Monthly allocation — multi-period | 6233/6273/6413/6423 | 242 | value/useful_months |
| CCDC return to warehouse | 153 | 242 | Remaining value |
| Disposal — sale (cost) | 632 | 153 | Remaining book value |
| Disposal — sale (revenue) | 111/112 | 711 | Proceeds |
| Inventory surplus | 153 | 711/338 | At fair value |
| Inventory shortage | 138/334 | 153 | Responsible person |
| Transfer (no GL impact except reclassification) | — | — | Internal tracking only |

---

## 7. Production Readiness Assessment

**CURRENT STATUS: NOT PRODUCTION-READY. SCORE: 0/5**

| Criteria | Score | Reason |
|----------|-------|--------|
| Domain entities | 0/5 | Not implemented |
| DB models + migration | 0/5 | Not implemented |
| Repository | 0/5 | Not implemented |
| Use cases | 0/5 | Not implemented |
| Routes (API) | 0/5 | Not implemented |
| Tests | 0/5 | Not implemented |
| TT 99/2025 compliance | 0/5 | Not verified |
| GL integration | 0/5 | Not connected |
| i18n error codes | 0/5 | Not implemented |
| Audit trail | 0/5 | Not implemented |
| **TOTAL** | **0/50** | **0% ready** |

---

## 8. Open Questions

1. **TT 99 sub-account detail**: Should SmartACCT define default sub-accounts for TK 153 (like 1531-1534) or leave fully customizable? **Recommendation**: Provide defaults but allow enterprise override via Accounting Policy Regulation.

2. **CCDC vs Spare Parts boundary**: FASparePart in FA module tracks spare parts for machinery. Should CCDC module include spare parts or delegate to FA? **Recommendation**: CCDC covers low-value spare parts (<30M); FA covers high-value spare parts held for specific machinery.

3. **Allocation method per item vs per issue**: Can a single issue batch contain CCDC items with different allocation methods? **Recommendation**: Yes — allocation is per line item, not per document.

4. **Monthly allocation batch**: Should allocation run automatically on period close or on-demand? **Recommendation**: On-demand with scheduler capability (user triggers monthly allocation run).

5. **Legacy migration**: How to import manual CCDC data (existing opening balances) from Excel/legacy system? **Recommendation**: Build bulk import endpoint for go-live.

---

## 9. Success Criteria

1. Full CRUD for all CCDC entities via REST API
2. Three allocation methods (1-time, 2-time, multi-period ≤36 months) correctly calculate and post to GL
3. Form 07-VT report matches TT 99/2025 template
4. All CCDC transactions auto-post to GL (balanced double-entry)
5. Inventory count with discrepancy handling (surplus/shortage/damage) → correct GL entries
6. Disposal/liquidation correctly handles remaining value
7. Physical responsibility tracking by department and person
8. All 12 use cases implemented and tested
9. i18n: all error codes in domain/i18n.py, Vietnamese+English translations
10. Audit trail for every CCDC transaction (created_at, created_by, updated_at, updated_by)

---

## 10. References

### Legal Documents
- TT 99/2025/TT-BTC: https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Thong-tu-99-2025-TT-BTC-huong-dan-Che-do-ke-toan-doanh-nghiep-565484.aspx
- TT 200/2014/TT-BTC: https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Thong-tu-200-2014-TT-BTC-huong-dan-Che-do-ke-toan-Doanh-nghiep-263599.aspx
- TT 133/2016/TT-BTC: https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Thong-tu-133-2016-TT-BTC-huong-dan-che-do-ke-toan-doanh-nghiep-nho-va-vua-284997.aspx
- TT 45/2013/TT-BTC (TSCĐ): https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Thong-tu-45-2013-TT-BTC-huong-dan-quan-ly-su-dung-trich-khau-hao-tai-san-co-dinh-175943.aspx
- Công báo TT 99: https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm
- KPMG Analysis: https://kpmg.com/vn/en/insights/2025/11/key-changes-in-vietnamese-accounting-system-for-enterprises.html
- MISA ASP migration guide: https://helpasp.misa.vn/accounting/kb/huong-dan-cap-nhat-len-thong-tu-99-2025-tt-btc/

### Professional Sources (Researched 30/06/2026)
- Ketoanthienung.net — CCDC allocation, TT 99 form 07-VT
- Ketoleanh.edu.vn — CCDC training, accounting practices
- Webketoan.com — Practitioner forum, CCDC management discussion
- MISA AMIS — CCDC module documentation, allocation workflow
- VACPA Ebook 1.12 — Legal document reference tool
- GDT eTax: thuedientu.gdt.gov.vn
- MOF: mof.gov.vn, vbpl.vn
- Customs: customs.gov.vn
- Social Insurance: baohiemxahoi.gov.vn
- National Public Service: dichvucong.gov.vn
