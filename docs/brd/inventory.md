# BRD: Inventory Module (Hàng tồn kho — HTK)
## SmartACCT ERP — Vietnamese Accounting System

**Version:** 1.0
**Date:** 2026-06-30
**Author:** Lead BA (20+ yrs) + Chief Accountant (20+ yrs)
**Status:** DRAFT — Pending Implementation

---

## 1. Executive Summary

### 1.1 Purpose

Build **Inventory (Hàng tồn kho)** module for SmartACCT ERP. Manage full lifecycle of inventory: goods receipt/purchase, production (manufacturing → WIP → finished goods), warehouse transfers, goods issue for sale, inventory counting, provision for obsolescence, cost valuation (FIFO/Weighted Average/Specific ID), and regulatory reporting per **VAS 02 — Hàng tồn kho** (IAS 2 equivalent), **TT 99/2025/TT-BTC** (effective 01/01/2026, replacing TT 200/2014), and parallel reference **TT 133/2016/TT-BTC** for SMEs.

### 1.2 Current State Assessment

**VERDICT: NOT PRODUCTION-READY. SCORE: 0/5**

Inventory module = **zero code**. No domain entities, use cases, repository, models, routes, or tests.

**What exists (usable but NOT HTK):**

| Asset | Status | HTK Reuse |
|-------|--------|-----------|
| COA TK 151–158 (Inventory accounts) | Accounts defined in ChartOfAccounts | Reuse for GL posting |
| COA TK 2294 (Dự phòng giảm giá HTK) | Account exists | Reuse for provision |
| COA TK 632 (Giá vốn hàng bán) | Account exists | Reuse for COGS posting |
| COA cost accounts (TK 621, 622, 623, 627, 641, 642) | Defined | Reuse for production cost |
| JournalEntry (GL) | Full CRUD + period-gated posting | Reuse for HTK→GL auto-post |
| FAUseCases (Fixed Assets) | Full module | Reference pattern |
| CCDCUseCases (Tools & Equipment) | Full module | Reference for TK 153 boundary |
| APUseCases (Accounts Payable) | Vendor/purchase invoice | Reuse for purchase receipt→AP link |
| TaxUseCases | EInvoice, VAT | Reuse for input VAT on purchase |

**Gap: EVERYTHING** — Inventory master data, goods receipt/purchase, manufacturing entry (TK 621→154→155), goods issue/COGS, inventory valuation engine (3 methods: FIFO/Weighted Avg/Specific ID), perpetual (KKTX) + periodic (KKĐK) methods, inventory counting (kiểm kê), provision for obsolescence (TK 2294), warehouse transfer, goods in transit (TK 151), bonded warehouse (TK 158), inventory reports (Form 01-VT→07-VT), HTK→GL auto-posting.

### 1.3 Scope

**In scope (UC-HTK-01 through UC-HTK-15):**

| UC | Name | Description |
|----|------|-------------|
| UC-HTK-01 | Inventory Master Data | SKU/product master: categories, units, valuation method, warehouse, min/max levels |
| UC-HTK-02 | Warehouse Management | Multi-warehouse, location/bin, warehouse types (raw material, WIP, FG, bonded) |
| UC-HTK-03 | Goods Receipt (Purchase) | Nhập kho mua ngoài: PO-based, non-PO, import (customs), donation, capital contribution |
| UC-HTK-04 | Goods Receipt (Production) | Nhập kho sản xuất: finished goods from production (TK 154→155) |
| UC-HTK-05 | Goods Issue to Production | Xuất kho sản xuất: raw material→TK 621 (cost element) |
| UC-HTK-06 | Goods Issue for Sale / COGS | Xuất kho bán hàng: TK 155/156→632, cost layer consumption |
| UC-HTK-07 | Warehouse Transfer | Chuyển kho between warehouses, between locations |
| UC-HTK-08 | Goods in Transit (TK 151) | Hàng mua đang đi đường: tracking goods not yet received |
| UC-HTK-09 | Inventory Valuation Engine | Cost calculation: FIFO, Weighted Average (BQGQ), Specific ID; periodic/perpetual |
| UC-HTK-10 | Inventory Counting (Kiểm kê) | Count sheet, discrepancy (surplus/shortage/damage), adjustment |
| UC-HTK-11 | Provision for Inventory (TK 2294) | Dự phòng giảm giá HTK: NRV test, provision/ reversal per VAS 02 + TT 48/2019 |
| UC-HTK-12 | WIP/Manufacturing Cost (TK 154) | Chi phí SXKD dở dang: cost collection, allocation, completion |
| UC-HTK-13 | HTK→GL Auto-Posting | All inventory transactions post to GL in real-time |
| UC-HTK-14 | Inventory Reporting | Stock card (Sổ kho), Form 01-07 VT, inventory aging, slow-moving, inventory turnover |
| UC-HTK-15 | Inventory Month-End Close | Cost revaluation, provision calc, reconciliation (GL ↔ Stock), close |

**Out of scope (v2.0+):**
- Barcode/RFID integration for warehouse operations
- Automated PO generation (reorder point / MRP)
- Lot/Serial/batch tracking with full traceability
- Consignment inventory with third-party warehouses
- Production BOM (Bill of Materials) — separate Manufacturing module
- WMS (Warehouse Management System) — putaway/picking/packing
- Integration with e-commerce platforms for real-time stock sync

### 1.4 Key Dependencies

| Dependency | Module | Purpose |
|------------|--------|---------|
| Chart of Accounts | COA | TK 151–158, TK 2294, TK 621–627, TK 632, TK 641–642 |
| Journal Entry | GL | Auto-posting of all inventory transactions |
| Payment Period | GL | Period-gated posting, month-end close sequence |
| Vendor Invoice | AP | Purchase goods receipt ↔ invoice matching (2/3-way) |
| E-Invoice (Purchase) | Tax/AP | Input VAT deduction requires e-invoice |
| Cash Payment | Cash/AP | Payment to supplier for goods purchase |
| FA/Capex | FA | TK 152 for construction materials vs TK 211 for fixed assets |
| CCDC | CC | TK 153 boundary — CCDC vs Inventory (TK 152/156) |
| Tax VAT Deduction | Tax | Input VAT tracking on goods purchase |

---

## 2. Regulatory & Compliance Framework

### 2.1 Primary Legislation — DOUBLE-CHECKED ✅ (as of 30/06/2026)

| Citation | Title | HTK Impact | Status |
|----------|-------|------------|--------|
| **VAS 02 — Hàng tồn kho** (QĐ 149/2001/QĐ-BTC, 31/12/2001, eff. 01/01/2003) | Inventory Standard — 26 paragraphs | Cost measurement, NRV, FIFO/WAC/Specific ID, provision rules, disclosure | **ACTIVE** — core standard |
| **TT 99/2025/TT-BTC** (27/10/2025, eff. 01/01/2026) | Enterprise Accounting Regime (replaces TT 200/2014) | TK 151–158, TK 2294, TK 632 rules; Forms 01-VT→07-VT; perpetual (KKTX) + periodic (KKĐK) | **ACTIVE** from 01/01/2026 |
| **TT 200/2014/TT-BTC** (22/12/2014) | Enterprise Accounting Regime | Điều 22–27: HTK accounts (historical reference) | **SUPERSEDED** by TT 99 |
| **TT 133/2016/TT-BTC** (26/08/2016) | SME Accounting Regime | Điều 22–24: HTK rules for SMEs (simplified COA) | **ACTIVE** for SMEs |
| **TT 48/2019/TT-BTC** (08/08/2019) | Provision for Inventory (tax perspective) | Deductibility conditions for provision expense, NRV calculation, rate limits | **ACTIVE** — tax compliance |
| **Law on Accounting 88/2015/QH13** (as amended 2024) | Accounting Law | Art 10 — principles of inventory valuation; Art 16 — voucher requirements | **ACTIVE** |
| **NĐ 70/2025/NĐ-CP** (replacing NĐ 123/2020, eff. 01/01/2026) | E-Invoice Decree | Input VAT deduction requires valid e-invoice (purchase) + bank payment ≥ 20M VND | **ACTIVE** |
| **NĐ 175/2016/NĐ-CP** (superseded by TT 48/2019) | Provision rules (historical) | Reference only | **SUPERSEDED** |
| **Circular 103/2014/TT-BTC** | Foreign Contractor Tax (FCT) | Import goods purchase — WHT on service element | **ACTIVE** |
| **TT 80/2021/TT-BTC** | Tax Administration | Inventory cost deductibility; allocation period for multi-period cost | **ACTIVE** |
| **IAS 2 — Inventories** (IFRS, current 2026) | International Standard | Reference for VAS→IFRS conversion; measurement at lower of cost and NRV | **REFERENCE** |

### 2.2 Key Regulatory Changes (TT 99/2025 vs TT 200/2014)

| Area | TT 200/2014 | TT 99/2025 | Impact |
|------|-------------|------------|--------|
| **TK 159** | Separate provision account | Removed — use TK 2294 (Dự phòng tổn thất tài sản) | Consolidation of provision accounts |
| **TK 158** | Kho bảo thuế (bonded warehouse) | Expanded — includes Nguyên liệu, vật tư tại kho bảo thuế | Separate tracking for bonded goods |
| **COA flexibility** | Mandated detail | Enterprise may add sub-accounts per management needs | More flexible — must issue Accounting Policy |
| **Periodic (KKĐK)** | Permitted | Still permitted but requires adequate internal controls | Both KKTX and KKĐK supported |
| **Form 01-VT→07-VT** | Mandated templates | Still reference templates but enterprise may customize | Non-mandatory — can use own design |
| **Báo cáo Tài chính** | Bảng CĐKT | Renamed "Báo cáo Tình hình Tài chính" | New presentation format |
| **Hàng tồn kho presentation** | Current assets | Same — but added detail for long-cycle WIP | Must track WIP duration ≥ 12 months |

### 2.3 VAS 02 vs IAS 2 Key Differences

| Aspect | VAS 02 | IAS 2 (IFRS) |
|--------|--------|--------------|
| **Scope** | All inventories (no exclusions) | Excludes financial instruments, biological assets, agricultural produce |
| **LIFO** | Permitted (with disclosure of FIFO/WAC difference) | **Prohibited** |
| **Borrowing costs** | Not capitalizable | Capitalizable per IAS 23 |
| **Deferred settlement** | Not addressed | Explicit guidance: difference is financing cost |
| **Biological assets** | No specific guidance | IAS 41 — fair value |
| **NRV measurement** | Per individual item | Per individual item (same) |
| **Cost formulas** | FIFO, WAC, Specific ID, LIFO | FIFO, WAC, Specific ID (no LIFO) |

### 2.4 Chart of Accounts — Inventory (TT 99/2025)

| TK | Name (Vietnamese) | Name (English) | DR/CR Balance | Type |
|----|--------------------|----------------|---------------|------|
| **151** | Hàng mua đang đi đường | Goods in Transit | Debit | Current Asset |
| **152** | Nguyên liệu, vật liệu | Raw Materials | Debit | Current Asset |
| **153** | Công cụ, dụng cụ | Tools & Equipment | Debit | Current Asset |
| **154** | Chi phí SXKD dở dang | WIP — Manufacturing Cost | Debit | Current Asset |
| **155** | Sản phẩm | Finished Goods | Debit | Current Asset |
| **156** | Hàng hóa | Merchandise/Trading Goods | Debit | Current Asset |
| **1561** | Giá mua hàng hóa | Purchase Cost of Goods | Debit | Sub-account |
| **1562** | Chi phí thu mua hàng hóa | Procurement Cost | Debit | Sub-account |
| **157** | Hàng gửi đi bán | Goods Sent on Consignment | Debit | Current Asset |
| **158** | Nguyên liệu, vật tư tại kho bảo thuế | Bonded Warehouse Inventory | Debit | Current Asset |
| **2294** | Dự phòng giảm giá hàng tồn kho | Inventory Provision | Credit | Contra-Asset |
| **632** | Giá vốn hàng bán | Cost of Goods Sold | Debit (expense) | Expense |
| **621** | Chi phí nguyên liệu, vật liệu trực tiếp | Direct Material Cost | Debit (expense) | Production |
| **622** | Chi phí nhân công trực tiếp | Direct Labor Cost | Debit (expense) | Production |
| **623** | Chi phí sử dụng máy thi công | Machine Usage Cost | Debit (expense) | Production |
| **627** | Chi phí sản xuất chung | Manufacturing Overhead | Debit (expense) | Production |

**Note:** TK 153 is handled by the **CCDC module** (not duplicated here). All other accounts are Inventory scope.

---

## 3. Domain Model

### 3.1 Core Entities

```
Inventory (Master Data)
├── id: Optional[int]
├── code: str                    # SKU / Mã hàng
├── name: str                    # Tên hàng
├── category_id: int             # FK → InventoryCategory
├── unit: str                    # Đơn vị tính (kg, cái, thùng, v.v.)
├── valuation_method: ValuationMethod  # FIFO, WEIGHTED_AVG, SPECIFIC_ID
├── account_id_151: Optional[int]      # TK 151 override
├── account_id_152: Optional[int]      # TK 152 override
├── account_id_155: Optional[int]      # TK 155 override
├── account_id_156: Optional[int]      # TK 156 override
├── account_id_632: Optional[int]      # TK 632 override
├── min_level: Optional[Decimal]       # Tồn tối thiểu
├── max_level: Optional[Decimal]       # Tồn tối đa
├── is_active: bool
├── is_trading: bool              # True = hàng hóa (TK 156), False = raw/FG
└── description: Optional[str]

InventoryCategory
├── id: int
├── name: str                    # Nguyên liệu, Nhiên liệu, Vật liệu phụ, v.v.
├── parent_id: Optional[int]     # Hierarchical
└── inventory_type: InventoryType  # RAW_MATERIAL, SUPPLIES, FUEL, PACKAGING, SPARE_PART, etc.

Warehouse
├── id: int
├── code: str                    # Mã kho
├── name: str
├── type: WarehouseType          # RAW_MATERIAL, WIP, FINISHED_GOOD, MERCHANDISE, BONDED, GENERAL
├── location: Optional[str]
├── is_active: bool
└── warehouse_keepers: List[Employee]

WarehouseBin
├── id: int
├── warehouse_id: int
├── code: str                    # Mã vị trí (A-01-01)
└── max_capacity: Optional[Decimal]

StockCard — Sổ kho (per inventory item per warehouse)
├── id: int
├── inventory_id: int
├── warehouse_id: int
├── period: str                  # Kỳ (MM/YYYY)
├── opening_qty: Decimal
├── opening_amount: Decimal
├── receipt_qty: Decimal
├── receipt_amount: Decimal
├── issue_qty: Decimal
├── issue_amount: Decimal
└── closing_qty: Decimal
└── closing_amount: Decimal

InventoryTransaction
├── id: int
├── transaction_no: str          # Số chứng từ (PNK/PXK/CPK)
├── transaction_date: date
├── type: TransactionType        # RECEIPT_PURCHASE, RECEIPT_PRODUCTION, ISSUE_PRODUCTION,
│                                # ISSUE_SALE, TRANSFER_IN, TRANSFER_OUT, COUNT_ADJUST,
│                                # GOODS_IN_TRANSIT, ISSUE_CONSIGNMENT, RETURN
├── warehouse_id: int
├── ref_inventory_id: Optional[int]   # Link to related transaction (e.g., transfer pair)
├── ref_document: Optional[str]       # Reference PO/SO number
├── description: Optional[str]
├── lines: List[TransactionLine]
├── posted_gl: bool
├── created_by: str
├── created_at: datetime
└── status: TransactionStatus    # DRAFT, POSTED, CANCELLED

TransactionLine
├── id: int
├── transaction_id: int
├── line_no: int
├── inventory_id: int
├── warehouse_bin: Optional[str]
├── quantity: Decimal
├── unit_price: Decimal
├── amount: Decimal
├── lot_ref: Optional[str]       # Batch/lot reference
├── vat_rate: Optional[Decimal]
├── vat_amount: Optional[Decimal]
├── cost_layer_id: Optional[int] # FK → CostLayer (FIFO layer consumed)
└── notes: Optional[str]

CostLayer (FIFO layer / WAC pool)
├── id: int
├── inventory_id: int
├── warehouse_id: int
├── receipt_date: date
├── receipt_transaction_id: int
├── quantity_remaining: Decimal
├── unit_cost: Decimal
└── original_amount: Decimal

InventoryCount (Kiểm kê)
├── id: int
├── count_date: date
├── warehouse_id: int
├── count_no: str                # BBKK number
├── status: CountStatus          # DRAFT, COUNTING, RESOLVED, CANCELLED
├── committee: List[Employee]    # Hội đồng kiểm kê
├── lines: List[CountLine]
├── resolved_at: Optional[datetime]
└── notes: Optional[str]

CountLine
├── id: int
├── count_id: int
├── inventory_id: int
├── book_qty: Decimal            # Sổ sách
├── book_amount: Decimal
├── physical_qty: Decimal        # Thực tế
├── difference_qty: Decimal      # Chênh lệch
├── unit_cost: Decimal
├── difference_amount: Decimal
├── reason: Optional[str]        # Giải trình
└── resolution: Optional[str]    # SURPLUS, SHORTAGE, DAMAGE

InventoryProvision (Dự phòng giảm giá HTK)
├── id: int
├── period: str                  # MM/YYYY
├── inventory_id: int
├── warehouse_id: int
├── cost_amount: Decimal         # Giá gốc trên sổ
├── nrv: Decimal                 # Giá trị thuần có thể thực hiện được
├── provision_required: Decimal  # Mức dự phòng cần trích
├── provision_existing: Decimal  # Số dự phòng đã trích
├── adjustment: Decimal          # Trích lập thêm (+) / Hoàn nhập (-)
├── notes: Optional[str]
└── posted_gl: bool

ProductionBatch (Lô sản xuất — simplified)
├── id: int
├── batch_no: str
├── product_id: int              # FK → Inventory (finished good)
├── quantity_planned: Decimal
├── quantity_produced: Decimal
├── start_date: date
├── end_date: Optional[date]
├── status: BatchStatus          # IN_PROCESS, COMPLETED, CANCELLED
├── cost_material: Decimal       # TK 621 → 154
├── cost_labor: Decimal          # TK 622 → 154
├── cost_overhead: Decimal       # TK 627 → 154
├── cost_total: Decimal
└── unit_cost: Decimal
```

### 3.2 Enumerations

```python
class ValuationMethod(str, Enum):
    FIFO = "fifo"                  # Nhập trước, xuất trước
    WEIGHTED_AVERAGE = "weighted_avg"  # Bình quân gia quyền
    SPECIFIC_ID = "specific_id"    # Thực tế đích danh

class InventoryType(str, Enum):
    RAW_MATERIAL = "raw_material"      # Nguyên liệu chính
    SUPPLIES = "supplies"              # Vật liệu phụ
    FUEL = "fuel"                      # Nhiên liệu
    PACKAGING = "packaging"            # Bao bì
    SPARE_PART = "spare_part"          # Phụ tùng thay thế
    CONSTRUCTION = "construction"      # Vật liệu XDCB
    WIP = "wip"                        # SPDD
    FINISHED_GOOD = "finished_good"    # Thành phẩm
    MERCHANDISE = "merchandise"        # Hàng hóa
    CONSIGNMENT = "consignment"        # Hàng gửi bán
    BONDED = "bonded"                  # Kho bảo thuế

class TransactionType(str, Enum):
    RECEIPT_PURCHASE = "receipt_purchase"          # Nhập mua ngoài
    RECEIPT_PRODUCTION = "receipt_production"      # Nhập sản xuất
    RECEIPT_RETURN = "receipt_return"              # Nhập trả lại (từ sx/bán)
    RECEIPT_OTHER = "receipt_other"                # Nhập khác (góp vốn, biếu tặng)
    ISSUE_PRODUCTION = "issue_production"          # Xuất sản xuất
    ISSUE_SALE = "issue_sale"                      # Xuất bán (COGS)
    ISSUE_CONSIGNMENT = "issue_consignment"        # Xuất gửi bán (TK 157)
    ISSUE_PROCESSING = "issue_processing"          # Xuất gia công
    ISSUE_CAPITAL = "issue_capital"                # Xuất XDCB
    ISSUE_OTHER = "issue_other"                    # Xuất khác
    TRANSFER_IN = "transfer_in"                    # Nhập từ chuyển kho
    TRANSFER_OUT = "transfer_out"                  # Xuất chuyển kho
    COUNT_ADJUST_PLUS = "count_adjust_plus"        # Điều chỉnh tăng (kiểm kê)
    COUNT_ADJUST_MINUS = "count_adjust_minus"      # Điều chỉnh giảm (kiểm kê)
    WRITE_OFF = "write_off"                        # Xóa sổ (hỏng, mất)

class WarehouseType(str, Enum):
    RAW_MATERIAL = "raw_material"       # Kho nguyên vật liệu
    WIP = "wip"                         # Kho bán thành phẩm/dở dang
    FINISHED_GOOD = "finished_good"     # Kho thành phẩm
    MERCHANDISE = "merchandise"         # Kho hàng hóa
    BONDED = "bonded"                   # Kho bảo thuế
    CONSIGNMENT = "consignment"         # Kho gửi bán
    GENERAL = "general"                 # Kho tổng hợp
    DESTROYED = "destroyed"             # Kho chờ hủy/thanh lý

class CountStatus(str, Enum):
    DRAFT = "draft"
    COUNTING = "counting"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"

class BatchStatus(str, Enum):
    IN_PROCESS = "in_process"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

---

## 4. Business Rules

### 4.1 Valuation Rules

#### FIFO (First-In, First-Out)
- Oldest purchase lot assigned to COGS first
- Remaining inventory valued at most recent purchase cost
- Cost layers maintained per inventory item per warehouse
- Layer consumed in chronological receipt order
- Both perpetual and periodic produce SAME result for FIFO

#### Weighted Average (Bình quân gia quyền)
- **Perpetual (BQGQ sau mỗi lần nhập):** Unit cost recalculated after each purchase
  - Formula: `(Current stock value + New receipt value) / (Current qty + New receipt qty)`
- **Periodic (BQGQ cuối kỳ):** Unit cost calculated at period-end
  - Formula: `(Opening value + Total receipt value in period) / (Opening qty + Total receipt qty in period)`

#### Specific ID (Thực tế đích danh)
- Each inventory item tracked individually with actual cost
- Required for: unique items, high-value items, jewelry, real estate
- COGS = actual cost of the specific item sold

#### LIFO (Last-In, First-Out)
- **Permitted under VAS 02** but **PROHIBITED under IAS 2**
- If used, must disclose LIFO vs FIFO/WAC difference in financial statements
- Rarely used in practice in Vietnam — strong recommendation: **DO NOT USE**

### 4.2 Perpetual (KKTX) vs Periodic (KKĐK)

| Aspect | KKTX (Perpetual) | KKĐK (Periodic) |
|--------|-------------------|-----------------|
| **Inventory tracking** | Real-time: every receipt/issue recorded | Only at period-end via physical count |
| **TK 151–156** | Continuously updated | Opening balance at start; only closing balance at end |
| **COGS calculation** | Real-time: accumulated to TK 632 | Calculated: `Opening + Purchases - Closing` |
| **Suitable** | All enterprises (default for TT 99) | Small enterprises, retail stores |
| **Granted** | Required for production enterprises | Only for trading/retail |

**Default: Perpetual (KKTX).** Periodic (KKĐK) offered as alternative only for trading enterprises with many SKUs and low unit value.

### 4.3 Inventory Counting Rules

- **Annual mandatory** physical count at fiscal year-end
- **Periodic** count: quarterly or monthly per enterprise policy
- **Cycle counting** for high-value items (ABC analysis)
- **Count committee** (Hội đồng kiểm kê): minimum 3 members (Keeper + Accountant + Supervisor)
- **Discrepancy resolution:**
  - Surplus (thừa): Nợ TK 152/155/156 / Có TK 3381 → adjust after approval
  - Shortage (thiếu): Nợ TK 1381 / Có TK 152/155/156 → investigate → write-off or recovery
  - Damage (hỏng): Nợ TK 1381 / Có TK 152/155/156 → approval for write-off
- **Tax treatment:** Shortage/damage beyond norm → disallowed expense for CIT unless force majeure

### 4.4 Provision Rules (TK 2294)

- **Condition:** NRV < Carrying cost (Giá trị thuần < Giá gốc)
- **NRV formula:** Estimated selling price — Estimated completion cost — Estimated selling cost
- **Per item** — no offsetting between items
- **Timing:** At BCTC preparation date (TT 99/2025); year-end per TT 48/2019 (tax)
- **Accounting entries:**
  - Provision increase: Nợ TK 632 / Có TK 2294
  - Provision reversal: Nợ TK 2294 / Có TK 632
- **Tax deduction:** Only allowable if:
  1. Enterprise has valid NRV evidence
  2. Provision calculated per TT 48/2019
  3. Not more than NRV = 10% of cost at time of market downturn
- **Reversal:** Mandatory if NRV recovers in subsequent period

### 4.5 GL Posting Matrix

| Transaction | Debit | Credit | Note |
|------------|-------|--------|------|
| Purchase receipt (domestic) | TK 152/155/156 | TK 331 (gross) | Input VAT → TK 133 |
| Purchase receipt (import) | TK 152/155/156 | TK 331 + TK 3333 (import duty) | Tax not refundable → cost |
| Purchase return | TK 331 | TK 152/155/156 + TK 133 | Reversal |
| Material issue to production | TK 621 | TK 152 | Direct material cost |
| Labor cost to production | TK 622 | TK 334/338 | Direct labor |
| Overhead to production | TK 627 | TK 214/331/334/338 | Manufacturing overhead |
| WIP → Finished goods | TK 155 | TK 154 | Production completion |
| COGS (goods sold) | TK 632 | TK 155/156 | At valuation cost |
| Revenue recognition | TK 131/111/112 | TK 511 + TK 3331 | Sales (separate module) |
| Goods in transit received | TK 152/155/156 | TK 151 | Receipt confirmation |
| Warehouse transfer | TK 152(2) | TK 152(1) | Same account, different sub-account |
| Consignment issue | TK 157 | TK 155/156 | Not yet sold |
| Consignment sale confirmed | TK 632 | TK 157 | COGS recognition |
| Inventory surplus (count) | TK 152/155/156 | TK 3381 | Pending resolution |
| Inventory shortage (count) | TK 1381 | TK 152/155/156 | Pending resolution |
| Shortage write-off (after approval) | TK 632 | TK 1381 | Approved loss |
| Inventory provision | TK 632 | TK 2294 | Period-end |
| Provision reversal | TK 2294 | TK 632 | NRV recovery |
| Gift/donation issue | TK 641/642 | TK 155/156 | Marketing/CSR expense |

### 4.6 Multi-Warehouse Rules

- Each inventory item may exist in multiple warehouses simultaneously
- Cost calculated independently per warehouse (or per company — configurable)
- Warehouse transfer: recorded as TRANSFER_OUT (source) + TRANSFER_IN (destination)
- Transfer between same-cost-method warehouses: cost transferred at carrying value
- Transfer between different-cost-method warehouses: cost revalued at destination method

---

## 5. Use Cases (High-Level)

### UC-HTK-01: Inventory Master Data
**Actor:** Accountant / Inventory Manager
**Flow:**
1. Create inventory item with code, name, category, unit
2. Select valuation method (FIFO/WAC/Specific ID)
3. Map to default accounts (TK 152/155/156)
4. Set warehouse assignment
5. Set min/max levels (optional)
6. Activate item for transactions
**Alternative:** Import from Excel/CSV
**Validation:** Code must be unique; account must be valid inventory account

### UC-HTK-02: Warehouse Management
**Actor:** Admin / Warehouse Manager
**Flow:**
1. Create warehouse with code, name, type
2. Assign warehouse keeper
3. Create bin locations (optional)
4. Activate/deactivate warehouse
**Rules:** At least 1 warehouse must exist before any inventory transaction

### UC-HTK-03: Goods Receipt (Purchase)
**Actor:** Warehouse Keeper
**Pre-condition:** Purchase invoice exists (AP module) or direct receipt
**Flow:**
1. Select transaction type = RECEIPT_PURCHASE
2. Select warehouse
3. Enter/scan inventory items, quantity, unit price
4. Enter invoice reference (optional)
5. System validates receipt qty ≤ invoice qty (3-way match)
6. Calculate cost + VAT per line
7. Post → system creates receipt + GL entries + updates cost layers
**Post-condition:** Stock quantity increased; GL: Dr TK 152/155/156 Cr TK 331

### UC-HTK-04: Goods Receipt (Production)
**Actor:** Production / Warehouse Keeper
**Pre-condition:** Production batch COMPLETED
**Flow:**
1. Select transaction type = RECEIPT_PRODUCTION
2. Select warehouse (finished goods)
3. Select production batch reference
4. Enter finished product, quantity produced, unit cost
5. Post → system creates receipt + GL: Dr TK 155 Cr TK 154

### UC-HTK-05: Goods Issue to Production
**Actor:** Warehouse Keeper
**Flow:**
1. Select transaction type = ISSUE_PRODUCTION
2. Select warehouse (raw material)
3. Select production batch reference
4. Enter items + quantities
5. System calculates cost using FIFO/WAC per item
6. Post → stock decreased; GL: Dr TK 621 Cr TK 152

### UC-HTK-06: Goods Issue for Sale / COGS
**Actor:** Warehouse Keeper / Automated from Sales
**Flow:**
1. Select transaction type = ISSUE_SALE
2. Select warehouse
3. Select sales order / delivery note reference
4. Enter items + quantities
5. System calculates COGS using FIFO/WAC/Specific ID
6. Post → stock decreased; GL: Dr TK 632 Cr TK 155/156

### UC-HTK-07: Warehouse Transfer
**Actor:** Warehouse Manager
**Flow:**
1. Create transfer with source + destination warehouse
2. Enter items + quantities
3. Post → source: TRANSFER_OUT, destination: TRANSFER_IN
4. GL: (same cost account) Dr TK 152(2) Cr TK 152(1)

### UC-HTK-08: Goods in Transit (TK 151)
**Actor:** Accountant
**Flow:**
1. Upon supplier shipment (not yet received): Dr TK 151 Cr TK 331
2. Upon physical receipt: Dr TK 152/155/156 Cr TK 151
**Rules:** Goods in transit ≤ 30 days (or per contract terms); automated aging alert

### UC-HTK-09: Inventory Valuation Engine
**Actor:** System (automated)
**Executes:**
1. **At every receipt:** For FIFO — create cost layer; For WAC — recalculate weighted average
2. **At every issue:** FIFO — consume oldest layers; WAC — use current weighted avg; Specific ID — use actual cost
3. **At period-end:** Recalculate WAC if periodic method; verify cost layers balance
4. **Support:** Cost revaluation (manual override with audit trail)

### UC-HTK-10: Inventory Counting (Kiểm kê)
**Actor:** Inventory Committee (≥3 members)
**Flow:**
1. Create count document for specific warehouse/category
2. System generates count sheet with book quantities
3. Physical count entered (mobile or paper-based)
4. System calculates discrepancies
5. Committee investigates and records reasons
6. Approval workflow for adjustment (hội đồng kiểm kê → KTT → Giám đốc)
7. Post adjustments → creates COUNT_ADJUST transactions + GL entries
**Exception:** Material shortage > VND 10M requires General Director approval

### UC-HTK-11: Provision for Inventory (TK 2294)
**Actor:** Accountant (month-end)
**Flow:**
1. Run NRV analysis per inventory item
2. System calculates: Max(0, cost — NRV) × quantity
3. Compare existing provision balance → determine adjustment
4. Generate provision schedule
5. Post adjustment: Dr/Cr TK 632 ↔ TK 2294
**Rules:** Per-item basis; no offsetting; evidence required (market price, aging)

### UC-HTK-12: WIP/Manufacturing Cost (TK 154)
**Actor:** Product Cost Accountant
**Flow:**
1. Collect direct materials (UC-05: TK 621→154)
2. Collect direct labor (TK 622→154)
3. Collect overhead (TK 627→154)
4. Allocate overhead using allocation basis (labor hours, machine hours, quantity)
5. Complete production batch → transfer to FG (UC-04: TK 154→155)
6. Remaining WIP balance = period-end WIP value

### UC-HTK-13: HTK→GL Auto-Posting
**Actor:** System (real-time)
**Triggers:** Every inventory transaction at POST status
**Logic:** Generate GL JournalEntry per matrix (Section 4.5)
**Validation:** Debit = Credit for each entry; inventory balance reconciled
**Post-condition:** Inventory movement viewable in GL account inquiry (Sổ cái TK 152/155/156)

### UC-HTK-14: Inventory Reporting
**Reports:**
1. **Stock Card (Sổ kho):** Per inventory item per warehouse — opening, receipt, issue, closing qty/amount
2. **Form 01-VT** — Phiếu nhập kho (Goods receipt voucher)
3. **Form 02-VT** — Phiếu xuất kho (Goods issue voucher)
4. **Form 05-VT** — Biên bản kiểm kê (Inventory count report)
5. **Inventory Aging:** By age bucket (0-30d, 30-60d, 60-90d, 90-180d, 180-365d, >365d)
6. **Slow-moving / Obsolete:** Items with zero movement > 90 days
7. **Inventory Turnover:** COGS / Average inventory
8. **ABC Analysis:** Inventory value ranking (A=80%, B=15%, C=5%)
9. **Inventory Provision Schedule:** Per item provision calc
10. **WIP Status:** Open production batches, cost collection status

### UC-HTK-15: Inventory Month-End Close
**Sequence (aligned with GL close):**
1. Complete ALL inventory transactions for the period
2. Run cost revaluation (if periodic WAC)
3. Run inventory counting (if scheduled)
4. Calculate and post provisions
5. Reconcile GL ↔ Stock (TK balance = Σ item value per warehouse)
6. Close inventory period — no new transactions for closed period
7. Generate period-end reports

---

## 6. Data Flows

### 6.1 Purchase → Inventory Flow
```
Sales/Purchase Ledger (AP)
    │
    ▼
Purchase Invoice (TK 331)
    │
    ▼
Goods Receipt (UC-03)
    ├─ KKTX: Direct stock update + GL (Dr TK 152/155/156 Cr TK 331)
    └─ KKĐK: No stock update until period-end
    │
    ▼
Cost Layer Created/Updated (UC-09)
    │
    ▼
Stock Card Updated
    │
    ▼
Period-End: COGS calculated from cost layers
```

### 6.2 Production Flow
```
Raw Material Issue (UC-05) → Dr TK 621 (DM cost)
Labor Cost → Dr TK 622 (DL cost)
Overhead → Dr TK 627 (OH cost)
          │
          ▼
    WIP Collection (TK 154)
          │
          ▼
    Production Batch COMPLETE
          │
          ▼
    Finished Goods Receipt (UC-04) → Dr TK 155 Cr TK 154
          │
          ▼
    Goods Issue Sale (UC-06) → Dr TK 632 Cr TK 155
```

### 6.3 Inventory Count Flow
```
Schedule Count → Generate Sheet (book qty)
    │
    ▼
Physical Count → Enter Results
    │
    ▼
Discrepancy Analysis
    ├── Match → No action
    ├── Surplus → Dr TK 3381 → Investigation → Approval → Dr TK 152/155/156 Cr TK 3381
    └── Shortage → Dr TK 1381 → Investigation → Approval → Dr TK 632/1388 Cr TK 1381
    │
    ▼
GL Posting + Stock Adjustment
```

### 6.4 Cost Flow (FIFO Example)
```
Layer 1: Buy 100 units @ 10,000 → Layer opened
Layer 2: Buy 200 units @ 12,000 → Layer opened
Sell 150 units → Consume Layer 1 (100) + Layer 2 (50) → COGS = 100×10k + 50×12k = 1,600,000
Layer 1: exhausted (qty_remaining = 0)
Layer 2: qty_remaining = 150
```

---

## 7. Regulatory Reports Mapping

| Report | Form | Frequency | Regulator |
|--------|------|-----------|-----------|
| Phiếu nhập kho | 01-VT (TT 99) | Per transaction | Internal / Tax audit |
| Phiếu xuất kho | 02-VT (TT 99) | Per transaction | Internal / Tax audit |
| Biên bản kiểm nghiệm | 03-VT (TT 99) | Per receipt | Internal |
| Bảng kê chi tiết vật tư còn lại CK | 04-VT (TT 99) | Period-end | Internal |
| Biên bản tổng hợp kiểm kê | 05-VT (TT 99) | Period-end / Annual | Internal / Tax audit |
| Bảng kê mua hàng | 06-VT (TT 99) | Period-end | Tax / VAT audit |
| Bảng phân bổ NVL, CCDC | 07-VT (TT 99) | Period-end | Internal / CIT audit |
| Inventory aging schedule | Enterprise-defined | Monthly | Internal |
| Provision for inventory schedule | Per TT 48/2019 | Year-end | Tax (CIT) |
| Inventory note (Bản thuyết minh BCTC) | B09-DN | Year-end | MOF / Auditor |
| Inventory turnover report | Enterprise-defined | Monthly/Quarterly | Internal management |

---

## 8. Current State vs Target

| Capability | Current | Target (v1.0) |
|-----------|---------|---------------|
| Master inventory data | ❌ | ✅ — CRUD, category, unit, valuation method |
| Multi-warehouse | ❌ | ✅ — Unlimited warehouses, bin locations |
| Goods receipt (purchase) | ❌ | ✅ — PO-linked + direct, 3-way match support |
| Goods receipt (production) | ❌ | ✅ — Batch completion → TK 155 |
| Goods issue (production) | ❌ | ✅ — Cost layer consumption |
| Goods issue (sale / COGS) | ❌ | ✅ — FIFO/WAC/Specific ID |
| Warehouse transfer | ❌ | ✅ |
| Goods in transit (TK 151) | ❌ | ✅ |
| Cost valuation engine | ❌ | ✅ — FIFO, WAC (perpetual + periodic), Specific ID |
| Inventory counting | ❌ | ✅ — Annual, periodic, cycle count |
| Provision (TK 2294) | ❌ | ✅ — NRV test, provision/reversal |
| WIP / Manufacturing | ❌ | ✅ — Basic production batch (621→154→155) |
| GL auto-posting | ❌ | ✅ — Transaction→GL in real-time |
| Stock card (Sổ kho) | ❌ | ✅ |
| Forms 01-VT→05-VT | ❌ | ✅ |
| Inventory aging / turnover | ❌ | ✅ |
| Month-end close | ❌ | ✅ — Reconciliation + close workflow |
| Barcode / serial tracking | ❌ | ❌ (v2.0) |
| MRP / reorder point | ❌ | ❌ (v2.0) |

---

## 9. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Inventory valuation error (FIFO layers out of balance) | High — material | Medium | Unit test: 100+ transactions; FIFO layer integrity check at post time |
| Negative stock (xuất vượt tồn) | High — invalid transaction | Medium | Block issue if quantity > available (configurable — allow override with warning) |
| Cost drift in WAC (floating point errors) | Medium | Low | Use Decimal(18,6) precision; recalc at period-end |
| Multi-warehouse cost discrepancy | Medium | Medium | Separate costing per warehouse; reconciliation per warehouse |
| Month-end GL/Stock mismatch | High | Medium | Automated reconciliation at close; blocking close if mismatch > 0.001 VND |
| NRV estimation provision error | Medium — tax exposure | Medium | Document NRV basis; require approval for provision > threshold |
| Physical count quality | Medium | Medium | Mandatory ≥ 3 committee members; supervisor spot checks |
| Production cost allocation error | High — WIP/FG value | Medium | Predefined allocation bases; review before posting |

---

## 10. Success Criteria

1. All 15 use cases implemented and tested (unit + integration)
2. Inventory valuation engine passes 100+ test scenarios (FIFO, WAC, Specific ID)
3. Multi-warehouse transactions with correct per-warehouse costing
4. GL/Stock reconciliation with zero discrepancy at period-end
5. All 7 Forms (01-VT→07-VT) generated correctly
6. Provision calculation matches VAS 02 + TT 48/2019 requirements
7. Production flow (621→154→155) correctly tracks cost
8. Month-end close sequence prevents post-close transactions
9. Negative stock prevention blocks invalid issues
10. All 7 regulatory forms exportable to Excel/PDF
11. Integration tests cover all transaction types with GL validation
12. Migration IDEMPOTENT — can be reversed via rollback

---

## 11. Technical Architecture Notes

### 11.1 Database Design — Cost Layer Model (FIFO)

```sql
-- Core: cost_layers table for FIFO tracking
CREATE TABLE inventory_cost_layers (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER NOT NULL REFERENCES inventory(id),
    warehouse_id INTEGER NOT NULL REFERENCES inventory_warehouse(id),
    receipt_date DATE NOT NULL,
    receipt_transaction_id INTEGER REFERENCES inventory_transactions(id),
    quantity_remaining NUMERIC(18,6) NOT NULL DEFAULT 0,
    unit_cost NUMERIC(18,2) NOT NULL,
    original_amount NUMERIC(18,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Check: quantity_remaining >= 0 (no over-consumption)
ALTER TABLE inventory_cost_layers
    ADD CONSTRAINT chk_qty_remaining_non_negative
    CHECK (quantity_remaining >= 0);
```

### 11.2 Transaction Numbering

- PNK-{YYYYMM}-{NNNNNN}: Receipt (Phiếu nhập kho)
- PXK-{YYYYMM}-{NNNNNN}: Issue (Phiếu xuất kho)
- CPK-{YYYYMM}-{NNNNNN}: Transfer (Chuyển kho)
- BBKK-{YYYYMM}-{NNNNNN}: Count (Biên bản kiểm kê)

### 11.3 Sequencing Rules

```
Transaction Order → Cost Layer Update → GL Posting
    1                  2                   3

Post MUST be atomic: if step 3 fails, steps 1-2 rollback
Use SQL transaction with SAVEPOINT
```

---

## 12. References

- VAS 02: Quyết định 149/2001/QĐ-BTC (full text: 26 paragraphs)
- TT 99/2025/TT-BTC: Điều 22–27 (Nguyên tắc kế toán hàng tồn kho)
- TT 133/2016/TT-BTC: Điều 22–24 (SME counterpart)
- TT 48/2019/TT-BTC: Provision for inventory (tax)
- IAS 2 (IFRS): ifrs.org → issued standards → IAS 2
- MOF: mof.gov.vn
- GDT eTax: thuedientu.gdt.gov.vn

---

## Appendix A: COA Account Configuration for Inventory

```json
{
  "151": {"name": "Hàng mua đang đi đường", "type": "current_asset", "drcr": "debit"},
  "152": {"name": "Nguyên liệu, vật liệu", "type": "current_asset", "drcr": "debit",
    "sub_accounts": [
      {"code": "1521", "name": "Nguyên liệu, vật liệu chính"},
      {"code": "1522", "name": "Vật liệu phụ"},
      {"code": "1523", "name": "Nhiên liệu"},
      {"code": "1524", "name": "Phụ tùng thay thế"},
      {"code": "1525", "name": "Vật tư XDCB"},
      {"code": "1528", "name": "Vật liệu khác"}
    ]
  },
  "154": {"name": "Chi phí SXKD dở dang", "type": "current_asset", "drcr": "debit"},
  "155": {"name": "Sản phẩm", "type": "current_asset", "drcr": "debit",
    "sub_accounts": [
      {"code": "1551", "name": "Thành phẩm"},
      {"code": "1557", "name": "Bán thành phẩm"}
    ]
  },
  "156": {"name": "Hàng hóa", "type": "current_asset", "drcr": "debit",
    "sub_accounts": [
      {"code": "1561", "name": "Giá mua hàng hóa"},
      {"code": "1562", "name": "Chi phí thu mua hàng hóa"}
    ]
  },
  "157": {"name": "Hàng gửi đi bán", "type": "current_asset", "drcr": "debit"},
  "158": {"name": "NVL, vật tư tại kho bảo thuế", "type": "current_asset", "drcr": "debit"},
  "2294": {"name": "Dự phòng giảm giá HTK", "type": "contra_asset", "drcr": "credit"},
  "632":  {"name": "Giá vốn hàng bán", "type": "expense", "drcr": "debit"}
}
```

## Appendix B: Test Strategy

| Level | Scope | Tests |
|-------|-------|-------|
| **Unit** | Domain entities (InventoryItem, CostLayer, Transaction) | Validation rules, cost calculation, NRV calc |
| **Integration** | Repository (CRUD, FIFO layer, WAC calculation, GL posting) | DB operations, multi-warehouse, cost layer integrity |
| **Use Case** | UC-HTK-01→15 | Happy path + alternative paths + exception paths |
| **Edge Cases** | Negative stock, zero-cost items, multi-currency purchase, fractional quantities, decimal precision | 50+ edge case scenarios |
| **Reports** | Forms 01-VT→07-VT, aging, turnover | Output format, data correctness |
| **Performance** | 10K+ SKU, 100K+ transactions/year | Cost layer query performance (< 100ms) |
