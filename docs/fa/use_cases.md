# Fixed Assets Module — Use Cases

**Version**: 1.0
**Date**: 2026-06-30
**Total Use Cases**: 12 (UC-FA-01 through UC-FA-12)

---

## Conventions

- **Actor**: Chief Accountant (Kế toán trưởng) / FA Accountant / System
- **Preconditions**: Must pass before use case starts
- **Postconditions**: Must hold after success
- **ID** format: `UC-FA-NN`
- **CRUD** endpoints: `/api/v1/fa/`
- **Error codes**: Defined in `domain/i18n.py` (prefix `FA_`)

---

## UC-FA-01: Manage FA Category (Nhóm TSCĐ)

**Actor**: FA Accountant, System Admin
**Trigger**: Setup/changes to FA classification groups

### Happy Path

1. Actor requests `POST /api/v1/fa/categories` with `{code, name, type (tangible/intangible/biological/lease), default_useful_life_min, default_useful_life_max, default_depreciation_method, asset_classification (loại 1-7 TT 147)}`
2. System validates: code unique, name non-empty, type is valid enum, life min <= max, method in valid set
3. System creates `FACategory` record, returns 201 with category detail

### Alternatives

- **Bulk import**: `POST /api/v1/fa/categories/import` with Excel/CSV. System validates each row, returns import summary with errors
- **Update**: `PUT /api/v1/fa/categories/{id}` — cannot change type if assets exist under this category

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Code already exists | `FA_CATEGORY_CODE_DUPLICATE` | 409 |
| Type invalid | `FA_INVALID_CATEGORY_TYPE` | 400 |
| Life min > max | `FA_USEFUL_LIFE_RANGE_INVALID` | 400 |
| Cannot change type (assets exist) | `FA_CATEGORY_HAS_ASSETS` | 409 |
| Category not found | `FA_CATEGORY_NOT_FOUND` | 404 |
| Depreciation method unsupported | `FA_UNSUPPORTED_DEPRECIATION_METHOD` | 400 |

### Data Flow

```
[Client] → POST /fa/categories → [Route] → [UseCase.create_category]
  → validate input → check unique code → build FACategory domain entity
  → repository.save() → return 201
```

---

## UC-FA-02: Register New Fixed Asset (Ghi tăng TSCĐ)

**Actor**: FA Accountant
**Trigger**: Purchase, construction completion, donation, capital contribution, discovery

### Happy Path

1. Actor requests `POST /api/v1/fa/assets` with:
   ```
   {
     code, name, category_id, type (tangible/intangible/biological/lease),
     original_cost, acquisition_date, in_use_date, useful_life_months,
     depreciation_method, residual_value, department_id, location,
     fund_source, supplier, invoice_ref, asset_classification (1-7),
     spare_parts: [{code, name, value}],
     components: [{name, value, useful_life}]
   }
   ```
2. System validates:
   - All 4 FA recognition criteria met (value ≥ 30M, life ≥ 12 months, etc.)
   - Depreciation method allowed for asset type
   - Useful life within category min-max range
   - In-use date ≥ acquisition date
   - No duplicate asset code
3. System creates `FixedAsset` record with status = `active`
4. System generates initial depreciation schedule
5. System posts GL entry: `Nợ TK 211/213/212/215 / Có TK 111/112/331/241/...`
6. System logs audit trail: `FA_ACQUISITION {code} by {user}`
7. Returns 201 with asset detail

### Alternatives

- **CIP completion**: `POST /fa/assets/from-cip/{cip_id}` — uses CIP accumulated cost + completion certificate to create FA
- **Bulk import**: `POST /fa/assets/import` Excel — validate each row, skip/create with error list
- **Donated asset**: special handling per TT 99 — 3387 if conditional, 711 if unconditional
- **Installment purchase**: separate principal (FA cost) vs interest (finance cost)
- **Lease capitalization**: `POST /fa/assets/from-lease` — use lower of fair value and PV of min lease payments

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Code duplicate | `FA_ASSET_CODE_DUPLICATE` | 409 |
| Value < 30M VND | `FA_VALUE_BELOW_THRESHOLD` | 400 |
| Useful life < 12 months | `FA_USEFUL_LIFE_TOO_SHORT` | 400 |
| Category not found | `FA_CATEGORY_NOT_FOUND` | 404 |
| In-use date before acquisition | `FA_IN_USE_DATE_BEFORE_ACQUISITION` | 400 |
| Depreciation method mismatch | `FA_DEPRECIATION_METHOD_MISMATCH` | 400 |
| Period closed for acquisition | `FA_PERIOD_CLOSED` | 400 |
| Fund source invalid | `FA_INVALID_FUND_SOURCE` | 400 |
| CIP not found (from-cip) | `FA_CIP_NOT_FOUND` | 404 |
| Cannot determine fair value (donation) | `FA_FAIR_VALUE_UNDETERMINED` | 400 |

### Data Flow

```
[Client] → POST /fa/assets → [Route] → [UseCase.register_asset]
  → validate FA criteria (value, life, completeness)
  → check period is open → build FixedAsset domain entity
  → category_repo.get() to validate category
  → dept_repo.get() to validate department
  → fa_repository.save(asset) → generate initial depreciation plan
  → gl_repository.post_entry(debit FA, credit AP/Cash/Supplier)
  → audit_repository.log(FA_ACQUISITION, asset_id, snapshot)
  → return 201
```

### GL Posting Matrix — Acquisition

| Source | Debit | Credit |
|--------|-------|--------|
| Direct purchase (cash) | TK 211/213 @ NG | TK 111/112 |
| Direct purchase (AP) | TK 211/213 @ NG | TK 331 |
| Purchase with installment >12m | TK 211/213 @ discounted price | TK 331 (principal) + TK 338 (interest) |
| Self-constructed (CIP complete) | TK 211/213 @ actual cost | TK 241 |
| Donated (unconditional) | TK 211/213 @ fair value | TK 711 |
| Donated (conditional) | TK 211/213 @ fair value | TK 3387 |
| Capital contribution | TK 211/213 @ valuation | TK 4111 |
| Finance lease | TK 212 @ lower(FV, PV min lease) | TK 341 (lease liability) |

---

## UC-FA-03: Calculate Monthly Depreciation (Tính & trích khấu hao)

**Actor**: System (scheduled), FA Accountant (manual trigger)
**Trigger**: Monthly depreciation run

### Happy Path

1. System triggers `POST /api/v1/fa/depreciation/run` for period `YYYY-MM`
2. System identifies all active assets with depreciation due:
   - Acquisition date ≤ period end
   - Not yet disposed before period start
   - Not fully depreciated
3. For each asset, calculate monthly depreciation:
   - **Straight-line**: `(original_cost - residual_value) / useful_life_months`
   - **Declining balance**: `NBV * (2 / useful_life) * adjustment_factor` (switch to SL when SL > DB)
   - **Units of production**: `(original_cost - residual_value) * (actual_output / estimated_total_output)`
4. System generates `DepreciationRecord` for each asset
5. System posts GL entry: `Nợ TK 623/627/641/642/241/... / Có TK 2141/2142/2143/2147`
6. System updates accumulated depreciation on asset card
7. System logs audit trail

### Alternatives

- **Manual override**: Allow adjusting depreciation amount for specific assets before posting
- **Partial period**: New assets: depreciation starts from in_use_date (pro-rata if mid-month)
- **Reversal**: `POST /depreciation/reverse/{period}` — reverses prior month run (audit-logged)

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Period already closed | `FA_PERIOD_CLOSED` | 400 |
| Period depreciation already run | `FA_DEPRECIATION_ALREADY_RUN` | 409 |
| No assets due for depreciation | `FA_NO_ASSETS_FOR_DEPRECIATION` | 200 (empty result) |
| GL account mapping missing | `FA_GL_ACCOUNT_MISSING` | 500 |

### Data Flow

```
[Schedule/User] → POST /fa/depreciation/run → [UseCase.run_depreciation]
  → validate period open → check not already run for period
  → repo.get_assets_due_for_depreciation(period)
  → for each asset: calc_method = get_method(asset.depreciation_method)
    → compute monthly amount → create DepreciationRecord
  → if all computed: post GL batch:
    dept_account_map = get_dept_account(asset.department, asset.type)
    DR cost_account, CR 214X
  → fa_repository.batch_update_depreciation(records)
  → audit log: FA_DEPRECIATION_RUN {period}, {count} assets, {total_amount}
  → return 200 with summary
```

### Depreciation Allocation

| Asset Use | Debit Account |
|-----------|--------------|
| Production (trực tiếp SX) | TK 623, 627 |
| Selling | TK 641 |
| Administration | TK 642 |
| Construction (XDCB) | TK 241 |
| Welfare/Phúc lợi | TK 353 (fund reduction) |
| R&D | TK 642 (or project cost) |

---

## UC-FA-04: Revalue Fixed Asset (Đánh giá lại TSCĐ)

**Actor**: Chief Accountant
**Trigger**: Periodic revaluation, SOE equitization, business combination

### Happy Path

1. Actor requests `POST /api/v1/fa/assets/{id}/revalue` with `{new_original_cost?, new_accumulated_depreciation?, appraised_by, appraisal_date, reason}`
2. System validates: asset exists, revaluation reason is valid
3. System checks that revaluation covers entire class (per TT 99 requirement)
4. System computes:
   - **Surplus** (↑ value): `DR TK 211, CR TK 412 (equity)` and `DR TK 412, CR TK 214`
   - **Deficit** (↓ value): `DR TK 632 (expense), CR TK 211` and `DR TK 214, CR TK 632`
   - **Deficit offsetting prior surplus**: `DR TK 412 (first), then TK 632 (excess)`
5. System creates `FAAdjustment` record with type = `revaluation`
6. System updates asset card (original_cost, accumulated_depreciation)
7. System logs audit trail

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Asset not found | `FA_ASSET_NOT_FOUND` | 404 |
| Revaluation not covering full class | `FA_REVALUATION_CLASS_INCOMPLETE` | 400 |
| Appraisal date in future | `FA_APPRAISAL_DATE_IN_FUTURE` | 400 |
| New value < carrying amount (unsupported) | `FA_REVALUATION_BELOW_NBV` | 400 |
| Period closed | `FA_PERIOD_CLOSED` | 400 |

---

## UC-FA-05: Transfer Fixed Asset (Điều chuyển TSCĐ)

**Actor**: FA Accountant
**Trigger**: Inter-department/cost center relocation

### Happy Path

1. Actor requests `POST /api/v1/fa/assets/{id}/transfer` with `{new_department_id, new_location, effective_date, reason, new_cost_center?}`
2. System validates: asset exists, status = active
3. System transfers asset: update department/location on asset card
4. System updates future depreciation allocation (pro-rata from effective date)
5. System creates audit trail entry
6. Returns 200

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Asset not found | `FA_ASSET_NOT_FOUND` | 404 |
| Asset disposed | `FA_ASSET_ALREADY_DISPOSED` | 400 |
| Department invalid | `FA_DEPARTMENT_NOT_FOUND` | 404 |
| Transfer to same department | `FA_NO_CHANGE` | 400 |

---

## UC-FA-06: Adjust Fixed Asset Value (Điều chỉnh giá trị TSCĐ)

**Actor**: FA Accountant, Chief Accountant
**Trigger**: Upgrade, partial dismantling, correction of cost

### Happy Path

1. Actor requests `PUT /api/v1/fa/assets/{id}/adjust` with:
   ```
   {
     adjustment_type: "upgrade" / "partial_dismantle" / "cost_correction" / "impairment",
     amount: Decimal,
     description: str,
     document_ref: str?,
     effective_date: date
   }
   ```
2. System validates:
   - `upgrade`: increases future economic benefits (TT 99 Điều 35.e) → increase NG
   - `partial_dismantle`: TT 99 allows removing component value → decrease NG + decrease KH lũy kế
   - `cost_correction`: original cost recording error
   - `impairment`: permanent decline → ghi nhận vào TK 632
3. System creates `FAAdjustment` record
4. System modifies asset card values
5. System adjusts future depreciation prospectively
6. System posts GL entries
7. Audit trail recorded

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Asset disposed | `FA_ASSET_ALREADY_DISPOSED` | 400 |
| Adjustment type invalid | `FA_INVALID_ADJUSTMENT_TYPE` | 400 |
| Adjustment reduces NG below accumulated KH | `FA_ADJUSTMENT_EXCEEDS_COST` | 400 |

### GL — Upgrade (Nâng cấp)

```
DR TK 211/213 @ cost of upgrade
CR TK 111/112/331/2414
```

### GL — Partial Dismantle

```
DR TK 2141 @ KH lũy kế of dismantled part
DR TK 632/138 @ NBV of dismantled part
CR TK 211 @ NG of dismantled part
```

---

## UC-FA-07: Dispose Fixed Asset (Thanh lý/Nhượng bán TSCĐ)

**Actor**: FA Accountant, Chief Accountant
**Trigger**: End of useful life, sale, donation, theft, destruction

### Happy Path

1. Actor requests `POST /api/v1/fa/assets/{id}/dispose` with:
   ```
   {
     disposal_type: "sale" / "liquidation" / "donation" / "theft" / "destruction",
     disposal_date: date,
     proceeds: Decimal?,
     costs: Decimal?,
     buyer_info: str?,
     reason: str,
     approved_by: str
   }
   ```
2. System validates: asset exists, status = active/suspended
3. System computes:
   - NBV = original_cost - accumulated_depreciation
   - Gain/Loss = proceeds - NBV - costs
4. System posts GL entries:
   - Remove asset: `DR TK 2141, DR TK 811 (NBV) / CR TK 211 (NG)`
   - Record proceeds: `DR TK 111/112/131 / CR TK 711`
   - Record costs: `DR TK 811 / CR TK 111/112`
   - Output VAT on sale: `DR TK 111/112 / CR TK 3331 (VAT)`
5. System sets asset status = `disposed`
6. System creates `FADisposal` record
7. System logs audit trail

### Alternatives

- **SOE infrastructure assets (Loại 6)**: require written owner representative approval per TT 147/2016; proceeds remitted to state budget
- **Partial disposal**: reduce NG by proportional amount, keep asset active

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Asset already disposed | `FA_ASSET_ALREADY_DISPOSED` | 400 |
| Disposal date in future | `FA_DISPOSAL_DATE_IN_FUTURE` | 400 |
| SOE approval missing (Loại 6) | `FA_SOE_APPROVAL_REQUIRED` | 400 |
| Proceeds < NBV without reason | `FA_DISPOSAL_LOSS_UNEXPLAINED` | 400 (warning) |

### GL Summary — Disposal

```
1. Remove asset and accumulated depreciation:
   DR TK 2141 (accumulated KH)
   DR TK 811 (NBV = residual loss)
   CR TK 211 (original cost)

2. Record sale proceeds:
   DR TK 111/112/131
   CR TK 711 (gain on disposal)
   CR TK 3331 (output VAT)

3. Record disposal costs:
   DR TK 811
   CR TK 111/112

4. Net result = Gain/Loss
   If CR balance > DR balance: net gain (TK 711)
   If DR balance > CR balance: net loss (TK 811)
```

---

## UC-FA-08: Perform FA Inventory (Kiểm kê TSCĐ)

**Actor**: Inventory Committee (Hội đồng kiểm kê)
**Trigger**: Annual/year-end requirement, periodic spot check

### Happy Path

1. Actor requests `POST /api/v1/fa/inventories` with physical count data
2. System compares physical count to book records
3. System identifies discrepancies (surplus/deficit)
4. System categorizes discrepancies:
   - **Surplus**: record at fair value (DR TK 211, CR TK 711) or market value
   - **Deficit (normal)**: DR TK 2141, DR TK 811 / CR TK 211
   - **Deficit (with responsible party)**: DR TK 138 (receivable from responsible), DR TK 811 (excess)
5. System generates `FAInventory` report with signed-off discrepancies
6. System logs audit trail: `FA_INVENTORY {date}, {surplus_count}, {deficit_count}`

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| No assets found for inventory scope | `FA_NO_ASSETS_IN_SCOPE` | 400 |
| Inventory date during period close | `FA_PERIOD_CLOSED` | 400 |
| Discrepancy resolution incomplete | `FA_INVENTORY_UNRESOLVED` | 400 |

---

## UC-FA-09: Manage Biological Assets (Quản lý tài sản sinh học) — NEW (TT 99)

**Actor**: FA Accountant
**Trigger**: Biological asset lifecycle events

### Happy Path

1. Actor requests `POST /api/v1/fa/biological-assets` with `{code, name, biological_type (2151/2152/2153), growth_stage, original_cost, acquisition_date, useful_life_months?, location, quantity, unit, herd_id?}`
2. System validates:
   - Biological asset standard criteria per TT 99
   - Growth stage transitions: immature → mature (21511 → 21512)
   - Working animals/perennial plants go to TK 211 (not 215)
3. System records asset on TK 215
4. System calculates depreciation (for mature periodic producers) on TK 215
5. System records provision for loss (TK 2295) if impairment indicators present

### Alternatives

- **Harvest/reap**: Biological product harvested → transfer to inventory (TK 152/155)
- **Growth stage transition**: automatic reclassification 21511 → 21512 when criteria met
- **One-time product (2152/2153)**: depreciate fully, derecognize at harvest/sale

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Biological type invalid | `FA_INVALID_BIOLOGICAL_TYPE` | 400 |
| Growth stage transition invalid | `FA_INVALID_STAGE_TRANSITION` | 400 |
| Asset should be TK 211 per MOF ruling | `FA_WRONG_ACCOUNT_ASSIGNMENT` | 400 |

---

## UC-FA-10: Generate FA Reports (Báo cáo TSCĐ)

**Actor**: FA Accountant, Chief Accountant, Manager
**Trigger**: Period-end, on-demand

### Happy Path

1. Actor requests `GET /api/v1/fa/reports/{type}` with `{period?, department?, category?, format: html|json|pdf|xlsx}`
2. Report types:
   - `fa_ledger` — Sổ TSCĐ (per-asset lifecycle)
   - `depreciation_schedule` — Bảng tính khấu hao
   - `fa_movement` — Bảng tổng hợp tăng giảm
   - `asset_card` — Thẻ TSCĐ
   - `inventory_report` — Báo cáo kiểm kê
   - `depreciation_allocation` — Bảng phân bổ khấu hao
   - `fully_depreciated` — Danh sách TSCĐ hết khấu hao
   - `by_fund_source` — TSCĐ theo nguồn hình thành
3. System queries FA data, computes totals, generates report in requested format
4. Returns report content (JSON/HTML) or file download (PDF/XLSX)

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Report type not found | `FA_REPORT_TYPE_NOT_FOUND` | 404 |
| No data for period | `FA_NO_DATA` | 200 (empty report) |
| Format not supported | `FA_FORMAT_NOT_SUPPORTED` | 400 |

---

## UC-FA-11: Transfer/Convert to IFRS (Chuyển đổi IFRS)

**Actor**: Chief Accountant, External Auditor
**Trigger**: IFRS reporting requirement, business combination

### Happy Path

1. Actor requests `POST /api/v1/fa/ifrs-conversion` with `{conversion_date, method: "full_retrospective" / "deemed_cost"}`
2. System identifies all FA requiring IFRS adjustment:
   - Revaluation model election per IAS 16
   - Component depreciation identification
   - Residual value and useful life review
   - Impairment testing per IAS 36
3. System computes IFRS carrying amounts vs VAS carrying amounts
4. System generates IFRS adjustment journal entries
5. System records IFRS parallel book values
6. Returns conversion summary

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| No IFRS book configured | `FA_IFRS_NOT_CONFIGURED` | 400 |
| Conversion already performed for date | `FA_IFRS_CONVERSION_EXISTS` | 409 |

---

## UC-FA-12: Upgrade/Convert to TT 99/2025 COA

**Actor**: System Admin
**Trigger**: Migration from TT 200/2014 to TT 99/2025

### Happy Path

1. Actor requests `POST /api/v1/fa/migrate-to-tt99`
2. System:
   - Remaps accounts: 441/466 → 4118
   - Renames 2413 → new name, adds 2414
   - Reclassifies biological assets from 211 → 215
   - Creates 2295 provisions for biological assets
   - Updates COA to new account structure
3. System generates migration report: count of affected assets, accounts
4. Returns 200 with migration summary

### Exceptions

| Condition | Error | HTTP |
|-----------|-------|------|
| Migration already applied | `FA_MIGRATION_ALREADY_DONE` | 409 |
| Data integrity check failed | `FA_MIGRATION_INTEGRITY_FAIL` | 500 |

---

## Process Flow Diagrams

### FA Lifecycle — End-to-End

```
┌─────────────────────────────────────────────────────────┐
│                    FA LIFECYCLE                          │
├──────────────┬──────────────┬───────────────┬────────────┤
│ ACQUISITION  │   IN USE     │   ADJUSTMENT  │  DISPOSAL  │
│              │              │               │            │
│ Purchase     │ Depreciation │ Revaluation   │ Sale       │
│ ──► 211/213 │ ──► 214      │ ──► 412/632   │ ──► 711/811│
│              │              │               │            │
│ Construction │ Monthly run  │ Upgrade       │ Liquidation│
│ ──► CIP→211  │ @ period-end │ ──► +NG       │ ──► 811    │
│              │              │               │            │
│ Donation     │ Transfer     │ Impairment    │ Donation   │
│ ──► 711/3387 │ dept/CC      │ ──► 632       │ ──► 811    │
│              │              │               │            │
│ Capital      │ Inventory    │ Dismantle     │ Theft      │
│ ──► 4111     │ count check  │ ──► -NG+214   │ ──► 811    │
└──────────────┴──────────────┴───────────────┴────────────┘
```

### Monthly Depreciation Run Process

```
Start of Month (Period YYYY-MM)
        │
        ▼
Check Period is OPEN ────NO────→ Error: Period Closed
        │ YES
        ▼
Check depreciation NOT already run ────NO────→ Error: Already Run
        │ YES
        ▼
Query active assets due for depreciation
        │
        ▼
For each asset:
  ├── Check in_use_date ≤ period_end
  ├── Check not disposed before period start
  ├── Check useful life not exhausted
  │
  └── Calculate:
      ├── Straight-line → (NG - RV) / months
      ├── Declining balance → NBV × rate
      └── Units of production → (NG - RV) × (output/total)
        │
        ▼
  Create DepreciationRecord (asset_id, period, amount)
        │
        ▼
Post GL Batch:
  DR: Cost account (by dept/use)
  CR: 2141/2142/2143/2147
        │
        ▼
Update Asset.accumulated_depreciation
        │
        ▼
Log Audit Trail
        │
        ▼
Return Summary: {period, count, total_amount}
```

### FA Acquisition Data Flow

```
[User Input] ──→ POST /fa/assets
                    │
                    ▼
              ┌─────────────┐
              │  Validate   │
              │  ─────────  │
              │ • Value≥30M │
              │ • Life≥12m  │
              │ • Code uniq │
              │ • Cat valid │
              │ • Period op │
              └──────┬──────┘
                     │ OK
                     ▼
              ┌─────────────┐
              │  Build      │
              │  Domain     │
              │  Entity     │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  Save to DB │
              │  fa_assets  │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  Post GL    │
              │  ─────────  │
              │ DR 211/213  │
              │ CR 111/331  │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  Audit Log  │
              └──────┬──────┘
                     │
                     ▼
             Return 201 Created
```

---

## User Journeys

### Journey 1: Chief Accountant — Year-End FA Close

1. Login → Open FA Dashboard
2. Run depreciation for December: `POST /fa/depreciation/run` for Dec period
3. Review reconciliation report: FA subsidiary ledger vs GL 211/214 balances
4. Run physical inventory: `POST /fa/inventories` with count data
5. Resolve discrepancies → adjust FA/GL entries
6. Generate annual FA reports: movement, depreciation, fully-depreciated
7. Submit FA schedule with financial statements
8. Close period when verified

### Journey 2: FA Accountant — New Asset Acquisition

1. Receive purchase invoice from AP module (or direct FA purchase)
2. Enter FA details: `POST /fa/assets`
3. Attach scanned documents: invoice, delivery note, acceptance certificate
4. System auto-computes initial depreciation schedule
5. System posts GL entry
6. Print asset card for physical tagging

### Journey 3: FA Accountant — Asset Transfer

1. Receive internal transfer request
2. Select asset → `POST /fa/assets/{id}/transfer`
3. Enter new department, location, effective date
4. System updates records and future depreciation allocation
5. Print transfer certificate (Biên bản bàn giao)

### Journey 4: FA Accountant — Disposal

1. Receive disposal approval (Board/Chief Accountant)
2. Select asset → `POST /fa/assets/{id}/dispose`
3. Enter disposal type, proceeds, buyer, costs
4. System computes gain/loss, posts GL
5. System generates disposal certificate
6. Asset removed from active depreciation run
