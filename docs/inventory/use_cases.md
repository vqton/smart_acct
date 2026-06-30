# Inventory Module — Detailed Use Cases
## SmartACCT ERP — Vietnamese Accounting System

**Version:** 1.0
**Date:** 2026-06-30
**Author:** Lead BA (20+ yrs) + Chief Accountant (20+ yrs)

---

## UC-HTK-01: Inventory Master Data (Hàng hóa — Danh mục)

### Actor
Accountant / Inventory Manager

### Pre-conditions
- At least 1 Warehouse exists
- Chart of Accounts exists (TK 152, 155, 156, 632 configured)
- InventoryCategory seeded (Nguyên liệu, Vật liệu phụ, Nhiên liệu, etc.)

### Happy Path
1. User navigates to "Inventory → Master Data"
2. Clicks "Add Item"
3. Enters: code, name, select category, unit (dropdown: cái, kg, thùng, mét, lit, etc.)
4. Selects inventory type: RAW_MATERIAL(152), MERCHANDISE(156), FINISHED_GOOD(155)
5. Selects valuation method: FIFO / WEIGHTED_AVG / SPECIFIC_ID
6. Default accounts auto-filled based on type (override allowed)
7. Sets warehouse assignment (1+ warehouses)
8. Optional: min_level, max_level, description, barcode
9. Saves → system creates item with ACTIVE status

### Alternative Paths
- **A1 — Import from Excel/CSV:** Upload file with code, name, category, unit, valuation method columns. System validates each row (code unique, category exists, account mapping valid). Partial failure allowed — error report returned.
- **A2 — Clone from existing item:** Select existing item → Clone → Edit changed fields → Save.

### Exception Paths
- **E1 — Duplicate code:** System rejects with "INVENTORY_CODE_DUPLICATE" error
- **E2 — Invalid account:** TK must be 152/155/156/157; error "INVALID_INVENTORY_ACCOUNT"
- **E3 — No warehouse assigned:** Error "WAREHOUSE_REQUIRED"
- **E4 — Category not found:** Error "CATEGORY_NOT_FOUND"

### Validation Rules
| Field | Rule |
|-------|------|
| code | Required, unique, max 50 chars, alphanumeric + `-_/` |
| name | Required, max 255 chars |
| category | Required, must exist in InventoryCategory |
| unit | Required, max 20 chars |
| valuation_method | Required; one of FIFO, WEIGHTED_AVERAGE, SPECIFIC_ID |
| account | Must be inventory account type (151-158) |
| min_level | Optional, >= 0 |
| max_level | Optional, >= min_level |

### Post-conditions
- Inventory item created with ACTIVE status
- Stock card opened with zero balance for assigned warehouse(s)
- Audit log: "Created inventory item [code] — [name]"

---

## UC-HTK-02: Warehouse Management (Quản lý kho)

### Actor
Admin / Warehouse Manager

### Happy Path
1. Navigate to "Inventory → Warehouses"
2. Clicks "Add Warehouse"
3. Enters: code, name, type (RAW_MATERIAL, WIP, FINISHED_GOOD, etc.)
4. Optional: address, contact, description
5. Assigns warehouse keeper(s)
6. Optionally creates bin locations (A-01-01, A-01-02...)
7. Saves

### Alternative Paths
- **A1 — Deactivate warehouse:** No new transactions allowed; existing data retained. GL balance stays.
- **A2 — Edit warehouse:** Change name, keeper, bin structure.

### Exception Paths
- **E1 — Cannot deactivate warehouse with non-zero stock:** Error "WAREHOUSE_HAS_STOCK"
- **E2 — Duplicate warehouse code:** Error "WAREHOUSE_CODE_DUPLICATE"

---

## UC-HTK-03: Goods Receipt — Purchase (Nhập kho mua ngoài)

### Actor
Warehouse Keeper

### Pre-conditions
- Inventory items exist
- Warehouse exists
- For PO-linked: Purchase Order exists in AP module (optional)

### Happy Path
1. Navigate to "Inventory → Goods Receipt"
2. Select type: "Purchase Receipt (Mua ngoài)"
3. Select warehouse
4. Select supplier (optional — links to AP)
5. Enter/scan items:
   - Select inventory item (search by code/name/barcode)
   - Enter quantity
   - Enter unit price (VND or foreign currency)
   - Select VAT rate (0%, 5%, 8%, 10%, KCT — Không chịu thuế)
   - Enter import duty/customs cost (for import) — auto-adds to cost
6. System calculates:
   - Line amount = quantity × unit price
   - Line cost = line amount + allocated procurement cost
   - VAT amount = line amount × VAT rate (if VAT deductible → TK 133)
   - Total receipt = sum of line costs + non-deductible taxes
7. Enter reference: supplier invoice no., PO no., delivery note
8. Optional: upload scanned delivery note / invoice
9. Save (DRAFT) or Post

### Alternative Paths
- **A1 — PO-linked receipt:** Select PO → system auto-populates expected items, quantities, prices. Keeper enters actual received qty (may differ from PO — partial receipt).
- **A2 — Import goods:** Add "Import declaration no.", "Customs duty" field → duty cost added to inventory cost. May add "CIF value" for duty calculation reference.
- **A3 — Non-PO receipt (direct):** Keeper enters all fields manually.
- **A4 — Receipt without invoice:** Still possible — system flags as "Chưa có hóa đơn" (pending invoice). TK 331 recorded based on receipt value. When invoice arrives, match to receipt.

### Exception Paths
- **E1 — Inventory item not found:** Error "ITEM_NOT_FOUND"
- **E2 — Zero or negative quantity:** Error "INVALID_QUANTITY"
- **E3 — Negative price:** Error "PRICE_MUST_BE_POSITIVE" (gift/donation use other type)
- **E4 — Warehouse mismatch:** Item not assigned to selected warehouse → Error "ITEM_NOT_IN_WAREHOUSE"
- **E5 — Period closed:** Error "PERIOD_CLOSED_CANNOT_POST"
- **E6 — Post fails due to GL error:** Rollback entire transaction

### Post-conditions (POSTED)
- Stock increased: Warehouse stock qty + amount updated
- Cost layer created (FIFO) / WAC recalculated
- Stock card updated
- GL entries:
  - Dr TK 152/155/156 (cost amount)
  - Dr TK 133 (VAT deductible amount, if applicable)
  - Cr TK 331 (supplier payable — total invoice amount)
  - Or: Cr TK 111/112 (if paid directly)
- Audit log: "Goods receipt [PNK-no] — [n] items — [total_amount]"

---

## UC-HTK-04: Goods Receipt — Production (Nhập kho sản xuất)

### Actor
Production Supervisor / Warehouse Keeper

### Pre-conditions
- Production batch exists with COMPLETED status
- Finished goods inventory item exists

### Happy Path
1. Navigate to "Inventory → Goods Receipt → Production"
2. Select production batch reference
3. Select finished goods warehouse
4. System displays: product, planned quantity, actual produced qty
5. Enter: actual quantity produced, by-product qty (if any)
6. System calculates unit cost = total batch cost / actual qty
7. Optional: enter adjustment (scrap loss, rework cost)
8. Post

### Alternative Paths
- **A1 — Partial completion:** Batch may complete in multiple receipts (e.g., 50 units in Week 1, 30 in Week 2). Each receipt assigns proportion of cost.
- **A2 — By-product receipt:** Enter by-product item + qty. By-product value deducted from main product cost per VAS 02 paragraph 13.

### Exception Paths
- **E1 — Batch already fully closed:** Error "BATCH_ALREADY_CLOSED"
- **E2 — Negative production:** Error "INVALID_PRODUCTION_QTY"
- **E3 — WIP total cost mismatch:** Error "BATCH_COST_MISMATCH" — sum of receipts ≠ batch cost

### Post-conditions
- Finished goods stock increased
- WIP (TK 154) cost transferred to FG (TK 155)
- GL: Dr TK 155 Cr TK 154

---

## UC-HTK-05: Goods Issue to Production (Xuất kho sản xuất)

### Actor
Warehouse Keeper

### Pre-conditions
- Raw material items exist in warehouse
- Production batch exists (or create on-the-fly)

### Happy Path
1. Navigate to "Inventory → Goods Issue → Production"
2. Select production batch reference (or create new batch)
3. Select warehouse (raw material)
4. Enter items + quantities (search + qty)
5. System calculates cost using valuation method:
   - FIFO: consume oldest cost layers
   - WAC: use current weighted average unit cost
   - Specific ID: user selects specific lot
6. Review and Post

### Exception Paths
- **E1 — Insufficient stock:** Error "INSUFFICIENT_STOCK" — issue quantity > available
- **E2 — Item not raw material type:** Error "ITEM_NOT_RAW_MATERIAL"
- **E3 — Negative issue:** Error "INVALID_ISSUE_QTY"

### Post-conditions
- Raw material stock decreased
- WIP cost (TK 154) increased
- GL: Dr TK 621 (→ TK 154 via cost allocation) Cr TK 152
- Cost layers consumed (FIFO) or WAC updated

---

## UC-HTK-06: Goods Issue for Sale / COGS (Xuất kho bán hàng)

### Actor
Warehouse Keeper / Automated via Sales Order

### Happy Path
1. Navigate to "Inventory → Goods Issue → Sale"
2. Select warehouse
3. Select sales order / delivery note (from Sales module)
4. System auto-populates items + quantities from SO
5. System calculates COGS:
   - FIFO: consume oldest layers → COGS
   - WAC: current avg cost × qty
   - Specific ID: user selects lot
6. Post

### Alternative Paths
- **A1 — Direct sale issue (no SO):** Keeper enters items manually.
- **A2 — Consignment issue (TK 157):** Special type — goods sent to agent/consignee. Dr TK 157 Cr TK 155/156. When sale confirmed by agent → Dr TK 632 Cr TK 157.
- **A3 — Sales return receipt:** Reverses previous issue. Dr TK 155/156 Cr TK 632. Stock returned at same cost (if same condition) or adjusted cost (if damaged).

### Exception Paths
- **E1 — Insufficient stock:** Warning (configurable: block vs override with reason)
- **E2 — Negative price (sales return):** Must be ≤ original unit cost
- **E3 — Consignment item not found in consignment warehouse:** Error

### Post-conditions
- FG/merchandise stock decreased
- COGS recorded in TK 632
- Cost layers consumed
- GL: Dr TK 632 Cr TK 155/156

---

## UC-HTK-07: Warehouse Transfer (Chuyển kho)

### Actor
Warehouse Manager

### Happy Path
1. Navigate to "Inventory → Transfer"
2. Select source warehouse + destination warehouse
3. Enter items + quantities
4. System validates: stock available at source
5. Optional: enter transport cost (allocated to cost)
6. Post

### Exception Paths
- **E1 — Insufficient stock at source:** Error
- **E2 — Same source & destination warehouse:** Error "SAME_WAREHOUSE_TRANSFER"
- **E3 — Item not in source warehouse:** Error

### Post-conditions
- Source: Stock decreased (TRANSFER_OUT)
- Destination: Stock increased (TRANSFER_IN)
- GL: Dr TK 152/155/156 (dest) Cr TK 152/155/156 (source)
- Same account — only sub-account changes

---

## UC-HTK-08: Goods in Transit (TK 151 — Hàng mua đang đi đường)

### Actor
Accountant

### Happy Path
1. Navigate to "Inventory → Goods in Transit"
2. Clicks "Add Goods in Transit"
3. Select supplier, contract/PO reference
4. Enter items, quantity, unit price (per supplier shipping doc)
5. Post → creates GIT record
6. When goods physically received:
   - Find GIT record → click "Receive to Warehouse"
   - Select destination warehouse, enter actual received qty
   - Post → TK 151 cleared; TK 152/155/156 increased

### Exception Paths
- **E1 — GIT aging > 30 days:** System shows alert (configurable threshold)
- **E2 — Partial receipt:** GIT partially cleared; remaining stays in TK 151
- **E3 — Goods never received:** After investigation, write off: Dr TK 632/1381 Cr TK 151

### Post-conditions
- TK 151: decreased by received amount
- TK 152/155/156: increased
- GL: Dr TK 152/155/156 Cr TK 151

---

## UC-HTK-09: Inventory Valuation Engine (Tính giá hàng tồn kho)

### Actor
System (automated) / Accountant (recalculation)

### Happy Path — FIFO
1. Transaction posted (receipt):
   - New cost layer created: inventory_id, warehouse_id, receipt_date, qty_remaining, unit_cost
2. Transaction posted (issue):
   - System finds oldest layer(s) with qty_remaining > 0
   - If issue qty ≤ layer qty: consume from single layer
   - If issue qty > layer qty: consume layer fully, move to next layer
   - COGS = sum of consumed layer qty × layer unit_cost
   - Each layer's qty_remaining decreased

### Happy Path — Weighted Average (perpetual)
1. Transaction posted (receipt):
   - New WAC = (current_total_value + new_receipt_value) / (current_total_qty + new_receipt_qty)
   - Update item WAC in master
2. Transaction posted (issue):
   - COGS = issue qty × current WAC
3. Period-end:
   - Full recalculation: total_value / total_qty
   - Adjust if floating-point drift detected

### Happy Path — Specific ID
1. User selects specific receipt lot at issue time
2. COGS = qty × that lot's unit_cost
3. That lot's qty_remaining decreased

### Exception Paths
- **E1 — No cost layers exist for FIFO at issue time:** Error "NO_COST_LAYER"
- **E2 — Floating-point drift in WAC > 1 VND:** System flags for manual review
- **E3 — Specific ID: selected lot has insufficient qty:** Error "LOT_INSUFFICIENT"

### Post-conditions
- COGS recorded at correct cost
- Cost layers updated
- Stock card reflects correct valuation

---

## UC-HTK-10: Inventory Counting (Kiểm kê hàng tồn kho)

### Actor
Inventory Committee (≥ 3 members)

### Happy Path
1. Navigate to "Inventory → Counting"
2. Clicks "Create Count"
3. Select warehouse, select items/categories (or "all items in warehouse")
4. System generates count sheet with:
   - Inventory code, name, unit, book qty, book amount
   - Blank columns: physical qty, difference, reason
5. Print count sheet or use mobile device
6. Physical team counts and records physical qty
7. Enter physical results into system
8. System calculates: difference_qty = physical_qty - book_qty
9. Committee reviews discrepancies and records reasons
10. Resolution: SURPLUS / SHORTAGE / DAMAGE per item
11. Send for approval (KTT → GĐ approval workflow)
12. Post adjustments:
    - Surplus: Dr TK 152/155/156 Cr TK 3381 → then Cr TK 3381 to Dr TK 632 (if sold) or income
    - Shortage (recoverable): Dr TK 1381 (individual) Cr TK 152/155/156
    - Shortage (unrecoverable): Dr TK 632 Cr TK 152/155/156
    - Damage: Dr TK 1381 → investigation → write-off or recovery

### Alternative Paths
- **A1 — Blind count:** Physical count entered before system shows book qty (better integrity).
- **A2 — Partial count (cycle count):** Count specific category or high-value items (A-class).
- **A3 — Zero-discrepancy count:** Count confirms all book quantities → system auto-approves.

### Exception Paths
- **E1 — Count in progress during transaction:** Cannot post inventory transactions to counted warehouse until count resolved.
- **E2 — Material discrepancy > VND 10M:** Requires GD approval (escalation workflow).
- **E3 — Committee member is also warehouse keeper:** Conflict of interest — cannot be sole counter for own warehouse.

### Rules
- Annual mandatory count at fiscal year-end
- Minimum 3 committee members: Keeper + Accountant + Supervisor
- Same person cannot be both counter and recorder
- Count ALL locations for selected items (not just some bins)
- Temporary holds on inventory movements during count

---

## UC-HTK-11: Provision for Inventory (TK 2294 — Dự phòng giảm giá HTK)

### Actor
Accountant (month-end/year-end)

### Pre-conditions
- Inventory balances finalized for the period
- Market price data available (use recent sales price or external valuation)

### Happy Path
1. Navigate to "Inventory → Provision → Calculate"
2. Select period (MM/YYYY)
3. System scans all inventory items:
   - For each item: compare cost (giá gốc) vs NRV (giá trị thuần có thể thực hiện được)
   - NRV = estimated selling price — estimated completion cost — estimated selling cost
   - Provision required = max(0, cost — NRV) × qty
4. Compare with existing provision balance:
   - provision_required > existing → additional provision: Dr TK 632 Cr TK 2294
   - provision_required < existing → reversal: Dr TK 2294 Cr TK 632
5. Generate provision schedule:
   - Item, cost, NRV, qty, existing provision, new provision, adjustment
6. Accountant reviews and approves
7. Post adjustment

### Alternative Paths
- **A1 — Bulk provision via Excel upload:** Use external valuation file → upload → map to items.
- **A2 — Selective provision:** Only run for specified items/categories.

### Exception Paths
- **E1 — Missing NRV data:** Item flagged "NO_NRV_DATA" — provision cannot be calculated without evidence.
- **E2 — Provision reversal triggers negative balance:** System enforces TK 2294 >= 0.

### Tax Rules (TT 48/2019)
- Provision deductible for CIT only if:
  1. Enterprise has documented NRV evidence (market price quote, appraisal)
  2. Provision ≤ cost - NRV (not excessive)
  3. Per individual item (no group offsetting)
  4. Reported at fiscal year-end
- Reversal: Mandatory when NRV recovers → taxed as income recovery

### Post-conditions
- Provision balance updated
- GL: Dr/Cr TK 632 ↔ TK 2294
- BCTC: Inventory value = Cost - Provision

---

## UC-HTK-12: WIP / Manufacturing Cost (TK 154)

### Actor
Product Cost Accountant

### Pre-conditions
- Production batch started
- Materials issued (UC-05), labor and overhead posted

### Happy Path
1. Navigate to "Manufacturing → WIP"
2. View production batch in IN_PROCESS status
3. Cost summary:
   - Direct materials (TK 621): from material issues
   - Direct labor (TK 622): from labor allocation
   - Manufacturing overhead (TK 627): from overhead allocation
   - Total WIP cost = sum of above
4. Allocate overhead:
   - Select allocation base: direct labor hours, machine hours, material qty, or production qty
   - System distributes TK 627 balance across active batches
5. View per-batch WIP cost
6. Complete batch:
   - Enter actual produced quantity
   - Enter by-product quantity (if any)
   - System calculates unit cost: (total batch cost - by-product value) / produced qty
   - Post → Dr TK 155 Cr TK 154

### Alternative Paths
- **A1 — Multi-product batch (joint products):** Allocate joint costs based on relative sales value per VAS 02 paragraph 13.
- **A2 — Scrap / waste:** Abnormal waste → excluded from WIP cost → charged to expense (Dr TK 632).
- **A3 — Batch with no production (cancelled):** WIP cost written off: Dr TK 632 Cr TK 154.

### Exception Paths
- **E1 — Insufficient allocation data:** Error "NO_ALLOCATION_BASE" — cannot post without allocation basis.
- **E2 — Negative WIP cost:** Error "WIP_COST_NEGATIVE" — check overhead allocation.
- **E3 — Batch WIP > actual physical WIP:** Discrepancy flag — manual review required.

---

## UC-HTK-13: HTK→GL Auto-Posting (Kết nối nghiệp vụ kho → Sổ cái)

### Actor
System (automated)

### Triggers
Every inventory transaction at POST status executes GL posting sequence:

```
Transaction POST
  → Validate: Debits = Credits (per transaction)
  → Validate: Inventory accounts exist
  → Generate JournalEntry lines per GL Matrix (BRD Section 4.5)
  → Post to GL (period must be OPEN)
  → Mark transaction: posted_gl = True
  → On GL post failure: ROLLBACK
```

### Validation Rules
- Each transaction generates at least 2 GL lines
- Total Debit = Total Credit (within 0.001 VND tolerance)
- Inventory account must balance: Σ warehouse stock value = GL balance per account
- Period must be OPEN (not closed)

### Post-conditions
- GL Journal Entry created
- Inventory GL account balance updated
- Transaction marked as posted_gl = True

---

## UC-HTK-14: Inventory Reporting (Báo cáo hàng tồn kho)

### Actor
Accountant / Manager

### Reports

**R01 — Stock Card (Sổ kho)**
- Per inventory item × warehouse × period
- Columns: Opening, Receipt (qty+amt), Issue (qty+amt), Closing (qty+amt)
- Detailed: lists each transaction with reference

**R02 — Form 01-VT / 02-VT (Phiếu nhập/xuất kho)**
- Single document print: Company info, document no., date, items, signatures
- Format per TT 99/2025 Phụ lục I

**R03 — Form 05-VT (Biên bản kiểm kê)**
- Count document print: Committee members, item list, book vs physical, discrepancy, resolution

**R04 — Inventory Aging**
- Aging buckets: 0-30d, 31-60d, 61-90d, 91-180d, 181-365d, >365d
- Based on last receipt date vs report date
- Calculates: inventory value per bucket, % of total, risk classification

**R05 — Slow-moving / Obsolete Report**
- Items with zero movement (no receipt, no issue) > 90 days
- Items exceeding min/max levels
- Items nearing or exceeding shelf life

**R06 — Inventory Turnover**
- Formula: COGS / Average Inventory
- Per item, per category, per warehouse
- Period: monthly, quarterly, yearly

**R07 — ABC Analysis**
- A-class (80% value): Tight control, cycle count monthly
- B-class (15% value): Moderate control, cycle count quarterly
- C-class (5% value): Simplified control, annual count

**R08 — Provision Schedule**
- Per item: cost, NRV, qty, provision required, existing provision, adjustment
- Summary by category

**R09 — WIP Status Report**
- Open batches: batch no., product, start date, cost collected (materials+labor+OH), % complete

**R10 — GL-Stock Reconciliation**
- Per inventory account: GL balance vs stock value
- Difference = errors or in-process transactions

---

## UC-HTK-15: Inventory Month-End Close (Khóa sổ cuối kỳ)

### Actor
Accountant

### Sequence
1. **Pre-close checks:**
   - All inventory transactions for period are POSTED (no DRAFT)
   - No in-progress inventory counts for period
   - No unbalanced transactions
2. **Cost revaluation (if periodic WAC):** Recalculate WAC for period
3. **Provision calculation (if year-end):** Run UC-11
4. **GL reconciliation:**
   - Σ stock value per TK = GL balance
   - If mismatch > 0.001 VND → error → investigation
5. **Close period:**
   - Mark period as CLOSED for inventory module
   - No new transactions allowed
   - Open next period (auto-create if not exist)

### Exception Paths
- **E1 — Open transactions:** Error "OPEN_TRANSACTIONS_REMAINING" — list of DRAFT/cancelled unposted items
- **E2 — GL/Stock mismatch:** Error "GL_STOCK_MISMATCH" — amount, account, warehouse
- **E3 — Already closed:** Error "PERIOD_ALREADY_CLOSED"

### Post-conditions
- Period closed
- Next period available for transactions
- Period-end reports generated and archived
- Opening balance for next period = closing balance of this period

---

## Appendix: Pricing / Effort Estimation

| Use Case | Domain | Model | Repo | Use Case | Routes | Tests | Est. (days) |
|----------|--------|-------|------|----------|--------|-------|-------------|
| UC-HTK-01 | 0.5 | 0.5 | 0.5 | 0.5 | 1 | 1 | 4 |
| UC-HTK-02 | — | 0.5 | 0.5 | 0.5 | 1 | 1 | 3.5 |
| UC-HTK-03 | — | 1 | 1.5 | 1.5 | 1 | 2 | 7 |
| UC-HTK-04 | — | 0.5 | 0.5 | 1 | 0.5 | 1.5 | 4 |
| UC-HTK-05 | — | 0.5 | 0.5 | 1 | 0.5 | 1.5 | 4 |
| UC-HTK-06 | — | 0.5 | 1 | 1.5 | 1 | 2 | 6 |
| UC-HTK-07 | — | 0.5 | 0.5 | 0.5 | 0.5 | 1 | 3 |
| UC-HTK-08 | — | 0.5 | 0.5 | 0.5 | 0.5 | 1 | 3 |
| UC-HTK-09 | 1.5 | 1 | 2 | 2 | — | 3 | 9.5 |
| UC-HTK-10 | 0.5 | 0.5 | 1 | 1 | 1 | 2 | 6 |
| UC-HTK-11 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 1.5 | 4 |
| UC-HTK-12 | 1 | 1 | 1 | 1.5 | 1 | 2 | 7.5 |
| UC-HTK-13 | — | — | 0.5 | 1 | — | 1.5 | 3 |
| UC-HTK-14 | — | — | 1.5 | 1 | 1.5 | 2 | 6 |
| UC-HTK-15 | — | — | 1 | 1 | 1 | 1.5 | 4.5 |
| **Total** | **4.5** | **7** | **12.5** | **14.5** | **10.5** | **23.5** | **75 team-days** |
