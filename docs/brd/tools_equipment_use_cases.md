# CCDC Module — Use Cases
## SmartACCT ERP — Công cụ, Dụng cụ (Tools & Equipment)

**Version:** 1.0
**Date:** 2026-06-30
**Author:** Lead BA (20+ yrs) + Chief Accountant (20+ yrs)
**Regulatory Base:** TT 99/2025/TT-BTC (eff. 01/01/2026), TT 133/2016/TT-BTC (SME)

---

## UC-CCDC-01: CCDC Category & Master Data

**Actor:** CCDC Accountant, System Admin
**Trigger:** Enterprise needs to define CCDC classification

### Happy Path
1. Actor selects "New Category"
2. System displays form: code, name_vn, description, parent_category, default_allocation_method, default_useful_months, account_sub_type
3. Actor fills required fields, selects default allocation method (one_time/two_time/multi_period)
4. System validates:
   - code unique, not empty
   - default_useful_months ≤ 36 (if multi_period)
   - parent_category exists (if provided)
5. System saves category, returns 201 + category object
6. Actor can create CCDC master items under this category

### Alternative Path — Category Hierarchy
- A1. Category with parent = root (top-level)
- A2. Category nested up to 3 levels deep
- A3. Sub-category inherits default allocation from parent (overridable)

### Exception Paths
- E1. Code already exists → 409 Conflict: "CCDC_CATEGORY_CODE_EXISTS"
- E2. default_useful_months > 36 → 422 Validation: "CCDC_ALLOCATION_PERIOD_EXCEEDS_MAXIMUM"
- E3. Parent category inactive → 422: "CCDC_PARENT_CATEGORY_INACTIVE"
- E4. Category has active CCDC items → soft-delete only (cannot hard-delete): "CCDC_CATEGORY_HAS_ACTIVE_ITEMS"

### Business Rules
- BR-01: Category code: uppercase letters + digits, max 10 chars
- BR-02: At least 1 category required before CCDC item can be created
- BR-03: Default sub-account for TK 153 is configurable per category
- BR-04: TT 99 permits enterprise-defined classification (no mandated sub-accounts)

---

## UC-CCDC-02: CCDC Receipt (Nhập kho)

**Actor:** Warehouse Keeper, CCDC Accountant
**Trigger:** CCDC items arrive at warehouse

### Happy Path
1. Actor selects "New Receipt"
2. System displays form: receipt_date (default=today), receipt_type (purchase/self_made/contribution/donor/inventory_surplus/return), document_ref, warehouse, notes
3. Actor adds lines: select CCDC item (or create new item inline), quantity, unit_price, vat_rate
4. System calculates: total_line = quantity × unit_price, total_amount = sum(lines)
5. Actor submits
6. System validates:
   - All required fields present
   - Supplier exists (if purchase type)
   - Quantity > 0
   - Unit price > 0 for purchase/self_made
7. System posts:
   - Dr 153 → Cr 111/112/331 (purchase), Cr 154 (self_made), Cr 411 (contribution), Cr 711 (donor)
   - Dr 1331 (VAT if deductible) → Cr payables (purchase with VAT)
8. System updates stock quantity
9. Returns 201 + receipt object

### Alternative Path — Return from Issue
- A1. receipt_type = "return": selects original issue document
- A2. System copies lines from issue, reverses allocation
- A3. Dr 153 (remaining value) → Cr 242 (if multi-period) or Cr cost account (if 1-time already expensed)

### Alternative Path — Inventory Surplus
- A1. receipt_type = "inventory_surplus": links to inventory count document
- A2. Valuation at fair market value
- A3. Dr 153 → Cr 711 (income)

### Exception Paths
- E1. Duplicate document_ref (same supplier + amount) → 409: "CCDC_DUPLICATE_RECEIPT"
- E2. Quantity = 0 → 422: "CCDC_ZERO_QUANTITY"
- E3. Supplier doesn't exist (for purchase) → 422: "CCDC_SUPPLIER_NOT_FOUND"
- E4. CCDC item disabled → 422: "CCDC_ITEM_INACTIVE"
- E5. Receipt date in closed period → 422: "CCDC_PERIOD_CLOSED"
- E6. Self-made CCDC: no production order reference → warning but allowed

### Business Rules
- BR-05: Purchase CCDC: cost = purchase_price - trade_discount + transport + handling (VAS 02)
- BR-06: VAT input deductible only if: valid e-invoice + payment ≥ 20M via bank (NĐ 70/2025)
- BR-07: Import CCDC: cost includes import duty, TTĐB (if applicable), BVMT (if applicable), transport
- BR-08: Receipt cannot be deleted after GL posting — must cancel with reversal entry

---

## UC-CCDC-03: CCDC Issue to Use (Xuất dùng)

**Actor:** CCDC Accountant, Department Head (request)
**Trigger:** Department requests CCDC for operations

### Happy Path — One-Time Allocation
1. Actor selects "New Issue"
2. System displays: issue_date, department_id, responsible_person_id, issue_type (production/admin/sales/rental/transfer), notes
3. Actor selects items, quantities
4. Actor selects allocation_method = "one_time"
5. System validates:
   - Sufficient stock quantity
   - Department exists, person exists
6. System posts:
   - Dr 6233/6273/6413/6423 (per department/cost account mapping) → Cr 153
7. System reduces stock, creates allocation record (status = fully_allocated)
8. Returns 201 + issue document

### Happy Path — Multi-Period Allocation (via TK 242)
1-3. Same as above
4. Actor selects allocation_method = "multi_period", sets useful_months
5. System validates: useful_months ≤ 36
6. System posts:
   - Dr 242 → Cr 153 (full value)
7. System creates CCDCAllocation record: total_value, monthly_amount = value/useful_months, status = active
8. Monthly allocation batch (UC-CCDC-04) will handle periodic entries

### Happy Path — Two-Time Allocation
1-3. Same as above
4. Actor selects allocation_method = "two_time"
5. System posts:
   - Dr 242 → Cr 153 (100% value)
   - Dr cost_account → Cr 242 (50% immediate)
6. System creates allocation record: remaining 50% allocated on return/damage

### Exception Paths
- E1. Insufficient stock → 422: "CCDC_INSUFFICIENT_STOCK" (shows available qty)
- E2. Issue to inactive department → 422: "CCDC_DEPARTMENT_INACTIVE"
- E3. Useful_months > 36 → 422: "CCDC_ALLOCATION_PERIOD_EXCEEDS_MAXIMUM"
- E4. CCDC item already fully issued (quantity_in_stock = 0) → 422: "CCDC_ITEM_OUT_OF_STOCK"
- E5. Issue date in closed period → 422: "CCDC_PERIOD_CLOSED"
- E6. Two_time allocation not applicable for consumable CCDC (e.g., protective equipment) → 422

### Business Rules
- BR-09: Issue reduces stock quantity but CCDC remains in physical tracking (sổ theo dõi)
- BR-10: TK 242 balance = remaining unallocated value of all multi-period CCDC
- BR-11: Monthly allocation = total_value / useful_months, rounded to nearest VND, final period adjusts rounding
- BR-12: CCDC issued to personnel must be tracked by responsible_person_id for asset custody

---

## UC-CCDC-04: CCDC Monthly Allocation Engine (Phân bổ hàng tháng)

**Actor:** System (batch), CCDC Accountant (trigger)
**Trigger:** Monthly period close or accountant runs allocation

### Happy Path
1. Actor/System triggers "Run Monthly Allocation" for period YYYY-MM
2. System queries all CCDCAllocation records WHERE:
   - status = active
   - start_date ≤ period end
   - end_date ≥ period start (or end_date IS NULL for ongoing)
   - allocated_value < total_value
3. For each record, system calculates: month_amount = min(monthly_amount, remaining_value)
4. System creates CCDCAllocationLine for each record
5. System posts GL batch:
   - Dr 6233/6273/6413/6423 → Cr 242 (sum of all month_amounts)
6. System updates: allocated_value += month_amount
7. If allocated_value = total_value → status = fully_allocated
8. Returns summary: total_allocated, count_items, gl_posting_ref

### Alternative Path — Partial Month
- A1. Issue date mid-month: first month allocation = monthly_amount × (days_remaining / total_days_in_month)
- A2. Or: first month = full amount (simplified, enterprise-configurable)

### Alternative Path — Early Termination
- A1. CCDC disposed before full allocation
- A2. Remaining value charged immediately: Dr cost_account → Cr 242
- A3. Allocation status = terminated

### Exception Paths
- E1. Period already allocated → 409: "CCDC_ALLOCATION_ALREADY_RUN" (allows re-run with override)
- E2. GL period closed → 422: "CCDC_PERIOD_CLOSED" (will be queued for next open period)
- E3. No active CCDC allocations → 200 with message: "CCDC_NO_ALLOCATIONS_FOR_PERIOD"
- E4. TK 242 balance insufficient (shouldn't happen but defensive check) → 500: "CCDC_242_BALANCE_MISMATCH"

### Business Rules
- BR-13: Allocation engine runs ONCE per period (idempotent — re-run overwrites with adjustment)
- BR-14: Max allocation period = 36 months from issue date
- BR-15: After full allocation, CCDCAllocation.status = fully_allocated
- BR-16: Fully-allocated CCDC still tracked physically until disposal/write-off (UC-CCDC-12)
- BR-17: Tax: allocation expense deductible if ≤36 months (TT 80/2021)

---

## UC-CCDC-05: CCDC Return to Warehouse (Thu hồi)

**Actor:** Warehouse Keeper, Department Head
**Trigger:** Department returns unused/damaged CCDC to warehouse

### Happy Path
1. Actor selects "New Return" → selects original issue document (or enters manually)
2. System displays issued items with remaining value
3. Actor selects items, quantities to return, condition (good/damaged/scrap)
4. If condition = good:
   - Dr 153 (remaining value) → Cr 242 (for multi-period) or cost_account (reversal of 1-time)
   - Reverses proportion of allocation
5. If condition = damaged/scrap:
   - Routes to UC-CCDC-08 (Disposal)
6. System updates stock, deactivates allocation for returned portion
7. Returns 201

### Alternative Path — Two-Time Allocation Return
- A1. Original issue used two_time method
- A2. Second 50% charged at return: Dr cost_account → Cr 242
- A3. Remaining stock value returned: Dr 153 → Cr 242

### Exception Paths
- E1. Return quantity > issued quantity (unused) → 422: "CCDC_RETURN_EXCEEDS_ISSUED"
- E2. CCDC already disposed → 422: "CCDC_ALREADY_DISPOSED"
- E3. Return after allocation period ended → valid, last allocation line adjusted
- E4. Responsible person mismatch (returning person ≠ original receiver) → warning

---

## UC-CCDC-06: CCDC Transfer (Điều chuyển)

**Actor:** CCDC Accountant, Department Head (both departments)
**Trigger:** CCDC moves between departments or warehouses

### Happy Path
1. Actor selects "New Transfer"
2. System displays: transfer_date, from_department, to_department, from_warehouse, to_warehouse, responsible_person_from, responsible_person_to
3. Actor selects items, quantities
4. System validates:
   - Sufficient stock/allocated quantity at origin
   - Destination exists
5. No GL impact (internal tracking only)
6. System updates:
   - department_id → to_department
   - responsible_person_id → to_person
   - warehouse → to_warehouse
7. If CCDC was in allocation, allocation continues but tracked under new department
8. Returns 201

### Exception Paths
- E1. Insufficient quantity at origin → 422
- E2. Same department requested → 400: "CCDC_SAME_DEPARTMENT_TRANSFER"
- E3. CCDC disposed → 422: "CCDC_ALREADY_DISPOSED"
- E4. Department inactive → 422

### Business Rules
- BR-18: Transfer does NOT change GL posting (allocation continues unchanged)
- BR-19: Must have signature/acknowledgment from both responsible persons
- BR-20: Transfer can cross cost centers but allocation account follows original department

---

## UC-CCDC-07: CCDC Inventory / Count (Kiểm kê)

**Actor:** Inventory Committee (multi-person), CCDC Accountant
**Trigger:** Year-end/periodic physical count

### Happy Path
1. Actor creates "New Inventory Count" — sets count_date, location/warehouse
2. Actor adds committee members (at least 2: one counter, one recorder)
3. System pre-fills book quantities for all CCDC items at selected location
4. Counters enter actual quantities, damaged quantities
5. System calculates differences:
   - surplus = actual - book (if actual > book)
   - shortage = book - actual (if book > actual)
   - damaged = entered damaged_qty
6. For each difference, actor selects handling recommendation:
   - Surplus: record as income (Dr 153 → Cr 711)
   - Shortage: responsible person compensation (Dr 138/334 → Cr 153)
   - Damage: write-off to expense (Dr 632 → Cr 153) or compensation
7. Committee chair approves final result
8. System posts GL for discrepancies
9. System adjusts stock quantities to actual
10. Returns 201 with summary

### Alternative Path — Ad-hoc Count
- A1. Spot-check on specific high-value items
- A2. No full committee required (but at least 2 persons)

### Exception Paths
- E1. Active inventory count already exists for same location/date → 409: "CCDC_INVENTORY_ALREADY_IN_PROGRESS"
- E2. Committee < 2 members → 422: "CCDC_INVENTORY_COMMITTEE_TOO_SMALL"
- E3. Difference unreasonably large (configurable threshold %) → warning but allowed
- E4. Surplus CCDC value cannot be determined (no market price) → 422: "CCDC_VALUE_INDETERMINATE"
- E5. Responsible person disputes shortage → status = "disputed", escalation required

### Business Rules
- BR-21: Annual inventory count mandatory per Law on Accounting Art 37
- BR-22: Count must include ALL CCDC (in stock + issued + in use) — issued items counted at user location
- BR-23: Surplus recorded at fair market value per VAS 02
- BR-24: Shortage with identified responsible person → Dr 138/334 (receivable from individual)
- BR-25: Shortage without responsible person → Dr 632 (loss)
- BR-26: Damaged CCDC: remaining value after partial recovery → expense
- BR-27: Report: Biên bản kiểm kê vật tư, công cụ, sản phẩm, hàng hóa (Mẫu 05-VT, TT 99)

---

## UC-CCDC-08: CCDC Disposal / Liquidation (Thanh lý)

**Actor:** CCDC Accountant, Chief Accountant (approval)
**Trigger:** CCDC is worn out, sold, donated, stolen, or destroyed

### Happy Path — Sale
1. Actor selects "New Disposal" → disposal_type = "sale"
2. Selects CCDC items, quantities
3. System displays: remaining book value, accumulated allocation
4. Actor enters: proceeds_amount, counterparty, approval_document_ref
5. If multi-period: remaining 242 balance charged immediately
   - Dr cost_account → Cr 242 (flush remaining value)
6. System posts GL:
   - Dr 632 (remaining book value) → Cr 153 (cost of disposal)
   - Dr 111/112 → Cr 711 (proceeds income)
   - Dr 3331 (VAT output if any) → Cr 111/112
7. System updates: CCDC status = "disposed", allocation status = "terminated"
8. Returns 201

### Happy Path — Scrap
1. disposal_type = "scrap"
2. No proceeds (or nominal scrap value)
3. GL: Dr 632 → Cr 153 (full remaining value as loss)
4. CCDC status = "disposed"

### Happy Path — Donation
1. disposal_type = "donation"
2. GL: Dr 632 → Cr 153 (remaining value as charitable expense)
3. Tax: donation deductible per Law on Corporate Income Tax (limited to 10% of taxable income)

### Exception Paths
- E1. CCDC already disposed → 422: "CCDC_ALREADY_DISPOSED"
- E2. Disposal by theft without police report → warning: "CCDC_THEFT_NO_POLICE_REPORT"
- E3. Disposal proceeds < remaining book value → warning (loss recognized automatically)
- E4. Disposal requires chief accountant approval if value > configurable threshold (e.g., 10M VND)
- E5. CCDC still actively allocated → must terminate allocation first

### Business Rules
- BR-28: Disposal flushes ALL remaining 242 balance immediately
- BR-29: Sale proceeds > remaining value → gain (Cr 711); proceeds < remaining → loss (Dr 632)
- BR-30: Theft disposal requires police report for tax deduction of loss
- BR-31: Donation + tax deduction requires: recipient is eligible charity, proper documentation
- BR-32: Destruction requires environmental authority clearance for certain items (e.g., chemical containers)

---

## UC-CCDC-09: CCDC → GL Auto-Posting

**Actor:** System (automatic on save)
**Trigger:** Any CCDC transaction is posted

### Happy Path
1. Any UC-CCDC-02/03/04/05/07/08 results in GL-posting data
2. System constructs double-entry based on posting matrix (see BRD §6.2)
3. System validates: Debits = Credits (within 0.001 VND tolerance)
4. System creates JournalEntry via existing GLUseCases.create_entry()
5. Links gl_posting_id back to source CCDC transaction
6. Returns gl_posting reference

### Exception Paths
- E1. GL period closed → 422: "CCDC_PERIOD_CLOSED"
- E2. Debits ≠ Credits → 500: "CCDC_GL_IMBALANCE" (should never happen — defensive)
- E3. Cost account invalid/inactive → 422: "CCDC_COST_ACCOUNT_INVALID"

### Business Rules
- BR-33: Every CCDC transaction must have corresponding GL entry
- BR-34: GL entry inherits period from CCDC transaction date
- BR-35: Reversal entries for cancellations link to original GL entry

---

## UC-CCDC-10: CCDC Reporting

**Actor:** CCDC Accountant, Chief Accountant, Internal Auditor
**Trigger:** Period-end, audit, management request

### Report 1: Form 07-VT — Bảng phân bổ NVL, CCDC
- Period: month/quarter/year
- Columns: Item, Cost Account, Total Cost, Allocation Method, Period Amount, Accumulated, Remaining
- Format: matches TT 99/2025 Phụ lục I template exactly
- Output: HTML, JSON, Excel, PDF

### Report 2: CCDC Detailed Ledger (Sổ chi tiết CCDC)
- By item, warehouse, department, responsible person
- Columns: Date, Document, Receipt Qty, Issue Qty, Unit Price, Total, Balance
- Running balance

### Report 3: CCDC Usage by Cost Center
- Group by department, cost account
- Compare budget vs actual allocation
- Monthly trend

### Report 4: CCDC Allocation Schedule
- Future allocation commitments by month (up to 36 months)
- Useful for cash flow planning

### Report 5: CCDC Inventory Status
- Stock on hand, issued in use, fully allocated, pending write-off
- By location

---

## UC-CCDC-11: Physical Responsibility Tracking

**Actor:** CCDC Accountant, Department Head, HR
**Trigger:** Employee on/offboarding, periodic review

### Happy Path
1. System maintains register of CCDC by responsible_person_id
2. On employee transfer/resignation: system flags unreturned CCDC
3. Clearance process:
   - HR checks system for pending CCDC
   - Employee returns CCDC or pays compensation
   - System generates clearance certificate
4. Reports: "CCDC by Employee", "Overdue Returns"

### Exception Paths
- E1. Employee resigned without clearance → debt receivable (Dr 138 → employee)
- E2. Lost CCDC → compensation amount configurable (market value or book value)

---

## UC-CCDC-12: CCDC Lifecycle End / Write-Off

**Actor:** CCDC Accountant, Chief Accountant
**Trigger:** CCDC fully allocated + physically retired

### Happy Path
1. System identifies CCDC records WHERE:
   - status = fully_allocated (allocation complete)
   - no active physical tracking requirement
   - disposed OR not used for > configurable period (e.g., 12 months)
2. Actor reviews list, selects items for write-off
3. System removes from active CCDC register, moves to history
4. Physical tracking flag = false

### Business Rules
- BR-36: Fully-allocated CCDC can remain in register if still physically in use (management choice)
- BR-37: Write-off is NON-GL event (all expense already recognized through allocation)
- BR-38: Historical data retained for audit trail (soft-delete with disposed_date)

---

## Summary Table

| UC | Name | Primary Actor | GL Impact | Est. Complexity |
|----|------|--------------|-----------|----------------|
| 01 | Category & Master Data | CCDC Accountant | None | Low |
| 02 | Receipt (Nhập kho) | Warehouse Keeper | Dr 153 → Cr 111/331 | Medium |
| 03 | Issue (Xuất dùng) | CCDC Accountant | Dr cost/242 → Cr 153 | Medium |
| 04 | Monthly Allocation Engine | System (batch) | Dr cost → Cr 242 | Medium |
| 05 | Return (Thu hồi) | Warehouse Keeper | Dr 153 → Cr 242 | Medium |
| 06 | Transfer (Điều chuyển) | CCDC Accountant | None (internal) | Low |
| 07 | Inventory (Kiểm kê) | Committee | Dr/ Cr 153 + gain/loss | High |
| 08 | Disposal (Thanh lý) | CCDC Accountant | Dr 632/Cr 711 → Cr 153 | Medium |
| 09 | CCDC→GL Auto-Posting | System | Varies | Medium |
| 10 | Reporting | CCDC Accountant | N/A | Medium |
| 11 | Physical Tracking | HR/CCDC Acct | Contingent | Low |
| 12 | Lifecycle End | CCDC Accountant | None | Low |
