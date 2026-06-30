# Inventory Module — Research & Reference
## SmartACCT ERP — Vietnamese Accounting System

**Date:** 2026-06-30
**Sources checked:** ketoanthienung.net, ketoanleanh.edu.vn, webketoan.com, vbpl.vn, mof.gov.vn, thuedientu.gdt.gov.vn, customs.gov.vn, baohiemxahoi.gov.vn, dichvucong.gov.vn, EY/PwC/Deloitte/KPMG Vietnam, gdt.gov.vn, vacpa.org.vn, vaa.net.vn, ifrs.org

---

## 1. Regulatory Status Summary

### 1.1 Active Regulations (as of 30/06/2026)

| Regulation | Effective | Status | Notes |
|------------|-----------|--------|-------|
| **VAS 02** — QĐ 149/2001/QĐ-BTC (31/12/2001) | 01/01/2003 | **ACTIVE** | Core inventory standard; 26 paragraphs; based on IAS 2 |
| **TT 99/2025/TT-BTC** (27/10/2025) | 01/01/2026 | **ACTIVE** | Replaces TT 200/2014; enterprise accounting regime |
| **TT 133/2016/TT-BTC** (26/08/2016) | 01/09/2016 | **ACTIVE** | SME accounting regime (parallel to TT 99) |
| **TT 48/2019/TT-BTC** (08/08/2019) | 01/10/2019 | **ACTIVE** | Provision regulations (tax perspective) |
| **NĐ 70/2025/NĐ-CP** (replaces NĐ 123/2020) | 01/01/2026 | **ACTIVE** | E-Invoice decree — purchase input VAT |
| **Luật Kế toán 88/2015/QH13** (+ amendments) | 01/01/2017 | **ACTIVE** | Revised 2024 |
| **TT 80/2021/TT-BTC** | 01/01/2022 | **ACTIVE** | Tax administration; inventory cost deductibility |
| **Circular 103/2014/TT-BTC** | 01/10/2014 | **ACTIVE** | FCT (WHT) on foreign vendor payments |

### 1.2 Superseded Regulations

| Regulation | Superseded By | Superseded Date |
|------------|---------------|-----------------|
| TT 200/2014/TT-BTC (enterprise accounting regime) | TT 99/2025/TT-BTC | 01/01/2026 |
| TT 75/2015/TT-BTC (amendments) | TT 99/2025/TT-BTC | 01/01/2026 |
| TT 53/2016/TT-BTC (amendments) | TT 99/2025/TT-BTC | 01/01/2026 |
| NĐ 123/2020/NĐ-CP (e-invoice) | NĐ 70/2025/NĐ-CP | 01/01/2026 |
| TK 159 (separate provision account) | TT 99 (→ TK 2294) | 01/01/2026 |

### 1.3 Outdated Reference — DO NOT USE
- Circular 15/2006/TT-BTC (provision guidance) → Superseded by TT 48/2019
- Decision 15/2006/QĐ-BTC (accounting regime) → Superseded by TT 200/2014 → TT 99/2025
- Decision 149/2001/QĐ-BTC (VAS 02) — **STILL ACTIVE** — the standard itself is active; the *implementation guidance* has been updated several times

---

## 2. Key Changes: TT 99/2025 vs TT 200/2014 for Inventory

### 2.1 Consolidated Provision Account
**TT 200:** TK 159 (Dự phòng giảm giá hàng tồn kho) — separate account
**TT 99:** TK 2294 (sub-account of 229 — Dự phòng tổn thất tài sản)

Impact: Module must post to TK 2294, NOT TK 159.

### 2.2 Bonded Warehouse Expansion
**TT 200:** TK 158 (Hàng hóa tại kho bảo thuế) — limited scope
**TT 99:** TK 158 (Nguyên liệu, vật tư tại kho bảo thuế) — expanded to include raw materials

Impact: TK 158 now handles BOTH raw materials and goods at bonded warehouse.

### 2.3 Chart of Accounts Flexibility
**TT 200:** Mandated sub-accounts (e.g., 1521-1528 were mandatory)
**TT 99:** Enterprise may define sub-accounts per management needs

Impact: Default sub-accounts provided, but enterprise can customize. Must issue internal Accounting Policy.

### 2.4 Financial Statement Presentation Changes
- "Bảng cân đối kế toán" → "Báo cáo Tình hình Tài chính" (Balance Sheet renamed)
- Inventory line item still in Current Assets
- New: long-cycle WIP (>12 months) → non-current asset
- New: long-cycle spare parts (>12 months) → non-current asset

### 2.5 Forms (still applicable but optional)
Forms 01-VT through 07-VT continue to be reference templates in TT 99.
Enterprise may design own forms but must maintain minimum required content per Luật Kế toán.

---

## 3. VAS 02 — Key Provisions

### 3.1 Scope (Paragraph 03)
Inventory includes:
- Goods held for sale in ordinary course of business
- Goods in production (WIP)
- Raw materials, supplies for production or service delivery

Specifically:
- Merchandise purchased for resale: in stock, in transit, on consignment, sent for processing
- Finished goods: in stock, on consignment
- WIP: not yet completed, or completed but not yet entered FG warehouse
- Raw materials, supplies: in stock, sent for processing, in transit
- Service work in progress (CP dịch vụ dở dang)

### 3.2 Exclusions (NOT inventory)
- Products/goods held for others (consignment-in, custodianship, processing-in) — tracked off-balance sheet
- Assets with storage >12 months or >1 operating cycle → non-current assets

### 3.3 Cost Determination (Paragraphs 05-14)
Cost = Purchase cost + Processing cost + Other direct costs

**Purchase cost** (Paragraph 06):
- Purchase price (invoice amount)
- Non-recoverable taxes (non-deductible VAT, import duty, excise tax, environmental tax)
- Transport, handling, storage during purchase
- LESS: trade discount, purchase rebate, quantity discount

**Processing cost** (Paragraphs 07-13):
- Direct labor
- Fixed production overhead (allocated based on normal capacity)
- Variable production overhead (allocated based on actual production)
- Abnormal waste → NOT included → expense immediately
- Joint product cost: allocate based on relative sales value
- By-product: measure at NRV, deduct from main product cost

**Other costs** (Paragraph 14):
- Costs to bring inventory to present location and condition
- Borrowing costs: NOT capitalized for VAS (unlike IAS 23)

### 3.4 Valuation Methods (Paragraphs 15-18)
- Specific identification: for items not ordinarily interchangeable
- FIFO (First-In, First-Out)
- WAC (Weighted Average Cost)
- LIFO (Last-In, First-Out) — allowed under VAS; DISALLOWED under IAS 2

### 3.5 NRV Test (Paragraphs 19-22)
- At each period-end: compare cost vs NRV
- NRV = estimated selling price — estimated completion cost — estimated selling cost
- Write-down: per individual item (no group offsetting)
- Reversal: mandatory if NRV recovers

### 3.6 Disclosure (Paragraphs 23-26)
- Accounting policy for valuation method
- Cost and NRV
- Provision amounts (opening, addition, reversal, closing)
- Inventory pledged as collateral
- LIFO → FIFO/WAC difference disclosure

---

## 4. IAS 2 vs VAS 02 Comparison

| Aspect | VAS 02 | IAS 2 (IFRS) |
|--------|--------|--------------|
| Scope | All inventories inclusive | Excludes biological assets (IAS 41), financial instruments |
| Cost measurement | Lower of cost and NRV | Same |
| Cost formulas | FIFO, WAC, Specific ID, LIFO | FIFO, WAC, Specific ID (NO LIFO) |
| Borrowing costs | Not capitalizable | Capitalizable per IAS 23 |
| Deferred purchase | Not addressed | Explicit: financing element recognized as interest |
| Reversal of write-down | Required if NRV recovers | Same |
| Allocation of fixed overhead | Based on normal capacity | Same |
| Joint products | Relative sales value | Same |
| Disclosure LIFO | Required: LIFO vs FIFO/WAC difference | N/A (LIFO not permitted) |
| Agricultural produce | No specific guidance | IAS 41 — fair value less costs to sell |

---

## 5. ERP Inventory Module — International Best Practices

### 5.1 Core Features (per industry research)
1. **Inventory master data** — SKU, barcode, category, unit, costing method
2. **Multi-warehouse / multi-location** — physical + logical locations
3. **Goods receipt** — PO-linked, direct, return
4. **Goods issue** — production, sales, internal consumption
5. **Stock transfer** — inter-warehouse, inter-bin
6. **Inventory counting** — annual, cycle, blind
7. **Cost management** — FIFO, WAC, Specific ID, Standard Cost
8. **ABC analysis** — valuation-based classification
9. **Inventory aging** — by receipt date, by shelf life
10. **Re-order point** — min/max levels (simplified MRP)

### 5.2 Database Design Patterns
- **Master tables:** inventory_item, warehouse, warehouse_bin, inventory_category
- **Transaction tables:** inventory_transaction (header), inventory_transaction_line
- **Cost tables:** cost_layer (FIFO), wac_pool (WAC)
- **Stock tables:** stock_card (periodic snapshot), stock_balance (real-time)
- **Count tables:** inventory_count, count_line
- **Provision tables:** inventory_provision

### 5.3 Key Design Decisions
- Real-time vs batch costing: Real-time recommended for FIFO, batch for periodic WAC
- Cost per warehouse vs per company: Per warehouse for accuracy
- Negative stock: Block by default; allow override with audit trail
- Decimal precision: Cost: decimal(18,2) or decimal(18,6); Quantity: decimal(18,6)

---

## 6. Vietnamese Accounting Software Market — Inventory Features

_Research: MISA, FAST, BRAVO, Effect, 1C, SAP Vietnam_

### MISA AMIS Features
- Goods receipt/issue with cost calculation
- FIFO + WAC (bình quân cuối kỳ / bình quân tức thời)
- Multi-warehouse
- Stock card, inventory aging, slow-moving
- Provision for inventory
- Integration with e-invoice, purchase, sales
- Form 01-VT → 07-VT

### FAST Features
- Full KKTX + KKĐK support
- FIFO, WAC, specific ID
- Multi-warehouse with per-warehouse costing
- Production/WIP tracking
- Inventory count with discrepancy
- Aging, turnover, ABC analysis
- GL auto-posting

### Key Differentiator for SmartACCT
- **Domain-first architecture** (Pydantic + validation) — stronger data integrity
- **FIFO cost layers as first-class entities** — trackable, auditable
- **Real-time GL integration** — no batch posting delay
- **TT 99/2025 native** — designed for current regime, not retrofitted
- **i18n** — Vietnamese-first with English support
- **API-first** — all functions available via REST

---

## 7. References

### Standards & Regulations
- VAS 02 full text: `docs.kreston.vn/vbpl/ke-toan/chuan-muc-ke-toan/vas-02/`
- TT 99/2025 full PDF: `drive.google.com/file/d/1frZsmjDc0VDL09x1X_RTyy0fTHihVhTP/`
- IAS 2 (IFRS): `ifrs.org/issued-standards/list-of-standards/ias-2-inventories/`
- TT 48/2019/TT-BTC: thuvienphapluat.vn

### Vietnamese Accounting Websites
- ketoanthienung.net — Hạch toán TK 152, 153, 154, 155, 156, 157, 158 theo TT 99
- ketoanleanh.edu.vn — Nguyên tắc kế toán HTK theo TT 99/2025
- ketoan.vn — VAS 02, TT 99/2025 analysis, TK 152/153 guidance
- vbpl.vn — Legal document database
- mof.gov.vn — Ministry of Finance (official)
- gdt.gov.vn — General Department of Taxation
- thuedientu.gdt.gov.vn — GDT eTax portal
- customs.gov.vn — Customs e-declaration
- baohiemxahoi.gov.vn — Social Insurance portal
- dichvucong.gov.vn — National Public Service Portal

### Big 4 Vietnam
- EY Vietnam: ey.com/vi_vn
- PwC Vietnam: pwc.com/vn
- Deloitte Vietnam: deloitte.com/vn
- KPMG Vietnam: kpmg.com/vn

### Professional Bodies
- vacpa.org.vn — VACPA (Auditing practitioners)
- vaa.net.vn — VAA (Accounting & Auditing Association)

### IFRS Reference
- ifrs.org — IAS 2 full text
- IAS 2: `ifrs.org/content/dam/ifrs/publications/html-standards/english/2026/issued/ias2.html`
