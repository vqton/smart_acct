# Fixed Assets (Tài sản cố định) — BRD

**Version**: 1.0
**Date**: 2026-06-30
**Author**: BA Lead + Chief Accountant (20+ yrs)
**Regulatory Basis**:
- **Circular 99/2025/TT-BTC** (eff. 01/01/2026 — replaces TT 200/2014) — Enterprise Accounting Regime
- **Circular 45/2013/TT-BTC** as amended by **Circular 147/2016/TT-BTC**, **Circular 28/2017/TT-BTC**, **Circular 30/2025/TT-BTC** (eff. 15/07/2025) — consolidated as **VBHN 12/VBHN-BTC 2025** — Management, Use & Depreciation of Fixed Assets
- **VAS 03** — Tangible Fixed Assets (QĐ 149/2001/QĐ-BTC)
- **VAS 04** — Intangible Fixed Assets (QĐ 149/2001/QĐ-BTC)
- **Law on Accounting 88/2015/QH13** as amended in 2024
- **Luật Quản lý, sử dụng tài sản công 15/2017/QH14** (for SOEs)
- **Nghị định 29/2025/NĐ-CP** (replacing NĐ 14/2023/NĐ-CP) — functions of MOF
- **IFRS convergence roadmap**: QĐ 345/QĐ-BTC (16/03/2020), Phase II compulsory from FY 2026
- **Thông tư 133/2016/TT-BTC** (SME accounting regime, parallel reference)
- **GDT eTax**: Circular 80/2021/TT-BTC, Circular 78/2021/TT-BTC

---

## 1. Executive Summary

Fixed Assets (TSCĐ) represent the largest capital investment for most enterprises. The FA module manages the complete asset lifecycle: acquisition recognition, depreciation calculation (3 methods), revaluation, impairment, maintenance tracking, transfer, disposal, and reporting. Vietnamese regulatory requirements under TT 99/2025 (eff. Jan 2026) introduce significant changes: new Account 215 (Biological Assets), fair value option for PPE, IFRS-aligned revenue recognition, autonomous COA customization, removal of Accounts 441/466 (capital sources for FA), and enhanced depreciation rules.

**Current status**: NO FA module exists in codebase. Must be built from scratch.

**Production readiness**: NOT ready. Estimated 12-16 weeks to MVP with full TT 99/2025 compliance.

---

## 2. Regulatory Regime Analysis (as of 2026-06-30)

### 2.1 Active Laws — DOUBLE-CHECKED ✅

| Document | Effective | Status | Applies To |
|----------|-----------|--------|------------|
| TT 99/2025/TT-BTC | 01/01/2026 | **ACTIVE** — replaces TT 200/2014 | All enterprises (incl. credit institutions for non-banking ops) |
| TT 45/2013/TT-BTC | 10/06/2013 | **ACTIVE** as amended | All enterprises |
| TT 147/2016/TT-BTC | 28/11/2016 | **ACTIVE** — amends TT 45 | All enterprises |
| TT 28/2017/TT-BTC | 26/05/2017 | **ACTIVE** — amends TT 45 + 147 | All enterprises |
| TT 30/2025/TT-BTC | 15/07/2025 | **ACTIVE** — amends TT 45 | SOEs with stalled projects (QĐ 1468/QĐ-TTg) |
| VBHN 12/VBHN-BTC 2025 | 15/07/2025 | **ACTIVE** — consolidated text | All enterprises |
| VAS 03 (TSCĐ HH) | 31/12/2001 | **ACTIVE** | All enterprises |
| VAS 04 (TSCĐ VH) | 31/12/2001 | **ACTIVE** | All enterprises |
| TT 200/2014/TT-BTC | 05/02/2015 | **EXPIRED** 01/01/2026 (partial: SOE equitization rules remain) | Reference only |
| QĐ 345/QĐ-BTC | 16/03/2020 | **ACTIVE** — IFRS roadmap Phase II | Listed cos, SOEs, large public cos |

### 2.2 Key Regulatory Changes (TT 99/2025 vs TT 200/2014) Affecting FA

| Area | TT 200/2014 | TT 99/2025 |
|------|-------------|------------|
| **Account 215** | None | NEW — Biological Assets (separated from TK 211) |
| **Account 2295** | None | NEW — Provision for Biological Asset Impairment |
| **Accounts 441, 466** | Active | **REMOVED** — balance converted to 4118 |
| **Account 2413** | "Sửa chữa lớn TSCĐ" | Renamed "Sửa chữa, bảo dưỡng định kỳ TSCĐ" |
| **Account 2414** | None | NEW — "Nâng cấp, cải tạo TSCĐ" |
| **COA customization** | MOF approval required | Enterprise autonomy with internal regulation |
| **FA valuation** | Historical cost only | Fair Value Model option introduced |
| **Installment purchase >12 months** | Lãi trả chậm treo ở 242 | MUST separate interest, record as finance cost |
| **Donated assets** | Record as income directly | Conditional: 3387 if conditions apply |
| **Spare parts with FA purchase** | Must separate at fair value | Clarified: specialized parts inseparable from main FA |
| **Financial statements** | Bảng CĐKT (Balance Sheet) | Báo cáo tình hình tài chính (Statement of Financial Position) |
| **Revenue recognition** | Risk/reward transfer | IFRS 15 5-step model convergence |

### 2.3 FA Recognition Criteria (TT 45/2013 + VAS 03, 04)

Tangible FA (TSCĐ HH) must satisfy ALL 4 criteria:
1. **Certain future economic benefits**
2. **Original cost reliably determined**
3. **Useful life ≥ 1 year**
4. **Value ≥ 30,000,000 VND** (TT 45/2013 Điều 3)

Intangible FA (TSCĐ VH) must satisfy:
1. **Same 4 criteria above**
2. **Identifiability** (separable or arising from contractual/legal rights)
3. **Enterprise controls the resource**

### 2.4 Depreciation Framework (TT 45/2013 as amended)

#### 2.4.1 Depreciation Groups & Useful Life (Phụ lục I TT 45)

| Group | Min (years) | Max (years) | Examples |
|-------|-------------|-------------|----------|
| A - Buildings, structures | 10 | 50 | Factory, office, warehouse |
| B - Machinery, power equipment | 6 | 20 | Generators, transformers |
| C - Working machinery | 5 | 15 | Production lines, CNC |
| D - Measuring instruments | 3 | 8 | Test equipment, lab |
| E - Transport equipment | 6 | 10 | Cars, trucks, forklifts |
| F - Management equipment | 3 | 8 | Computers, office furniture |
| G - Perennial plants, working animals | 4 | 15 | Rubber, coffee, dairy cows |
| H - Other tangible FA | 5 | 15 | Per Phụ lục I |
| I - Intangible FA | 2 | 20 | Software, patents, licenses |

#### 2.4.2 Depreciation Methods (Điều 13 TT 45)

1. **Straight-line (Đường thẳng)** — Default, most common
2. **Declining balance (Số dư giảm dần có điều chỉnh)** — Max 2x straight-line rate, requires economic justification
3. **Units of production (Theo sản lượng)** — For assets where wear correlates with output

#### 2.4.3 Special Depreciation Rules

- **Accelerated depreciation**: Max 2x straight-line for high-tech/high-efficiency enterprises
- **Suspended depreciation**: Only for SOEs with stalled projects per QĐ 1468/QĐ-TTg (added by TT 30/2025)
- **Fully depreciated but still in use**: Stop charging depreciation, continue tracking at residual value (0 if fully depreciated)
- **Component depreciation**: TT 99/2025 allows separate depreciation for significant components
- **Leasehold improvements**: Depreciated over lease term or useful life, whichever shorter

---

## 3. FA Charter of Accounts (TT 99/2025)

### 3.1 Core FA Accounts

| Account | Name | Type | Notes |
|---------|------|------|-------|
| **211** | TSCĐ hữu hình | Tangible FA | No mandatory sub-accounts in TT 99 |
| **212** | TSCĐ thuê tài chính | Finance Lease FA | 2121 HH, 2122 VH — enterprise-defined |
| **213** | TSCĐ vô hình | Intangible FA | 2131-2138 sub-accounts defined |
| **214** | Hao mòn TSCĐ | Accum. Depreciation | 2141 HH, 2142 Thuê TC, 2143 VH, 2147 BĐS |
| **215** | Tài sản sinh học | Biological Assets | NEW in TT 99 — 2151, 2152, 2153 |
| **217** | BĐS đầu tư | Investment Property | Kept unchanged |
| **241** | XDCB dở dang | CIP | 2411, 2412, 2413, 2414 |

### 3.2 Account 213 Sub-accounts (TT 99/2025)

| Account | Name |
|---------|------|
| 2131 | Quyền sử dụng đất |
| 2132 | Quyền phát hành |
| 2133 | Bản quyền, bằng sáng chế |
| 2134 | Nhãn hiệu hàng hóa |
| 2135 | Chương trình phần mềm |
| 2136 | Giấy phép và giấy phép nhượng quyền |
| 2138 | TSCĐ vô hình khác |

### 3.3 Account 215 Sub-accounts (NEW in TT 99/2025)

| Account | Name |
|---------|------|
| 2151 | Súc vật nuôi cho sản phẩm định kỳ |
| 21511 | Chưa đến giai đoạn trưởng thành |
| 21512 | Đã đến giai đoạn trưởng thành |
| 215121 | Nguyên giá |
| 215122 | Giá trị khấu hao lũy kế |
| 2152 | Súc vật nuôi lấy sản phẩm một lần |
| 2153 | Cây trồng theo mùa vụ hoặc lấy sản phẩm một lần |
| 2295 | Dự phòng tổn thất tài sản sinh học |

---

## 4. Scope & Boundaries

### 4.1 In Scope (Phase 1 — MVP)

- [x] FA category management (HH, VH, cho thuê TC, sinh học)
- [x] FA master data (asset card with full attributes)
- [x] FA acquisition recognition (purchase, construction, donation, contribution)
- [x] 3 depreciation methods (straight-line, declining balance, units of production)
- [x] Monthly depreciation run with automatic GL posting
- [x] FA value adjustments (revaluation, impairment, upgrade)
- [x] FA transfer (department/location/cost center)
- [x] FA disposal (sale, liquidation)
- [x] FA inventory/stocktake
- [x] FA reports (card, list, depreciation schedule,增减表, inventory report)
- [x] Integration with GL, AP, Budget modules
- [x] Audit trail for all FA transactions
- [x] TT 99/2025 compliance (new accounts, fair value option, COA autonomy)

### 4.2 Out of Scope (Phase 2)

- [ ] IFRS revaluation model full implementation (partial in Phase 1)
- [ ] Biological asset fair value measurement (IAS 41) — cost model only in Phase 1
- [ ] Component depreciation automation
- [ ] FA barcode/RFID integration
- [ ] Lease management (IFRS 16) — basic finance lease tracking in Phase 1
- [ ] CIP to FA auto-conversion workflow
- [ ] FA budgeting and CAPEX approval workflow

### 4.3 Integration Points

| Module | Integration |
|--------|-------------|
| **GL** | Depreciation posting, FA disposal P&L, revaluation reserves |
| **AP** | FA acquisition from supplier invoices, CIP tracking |
| **Budget** | CAPEX budget control |
| **Tax** | Fixed asset CIT depreciation tracking, VAT on FA purchases |
| **Period** | Depreciation gated by open periods |
| **Cash** | FA purchase payments, disposal proceeds |

---

## 5. Business Rules

### 5.1 FA Acquisition Rules

1. Acquisition date = date asset is ready for use (not invoice date)
2. Original cost = purchase price (ex-VAT if deductible) + directly attributable costs (transport, installation, testing, professional fees)
3. Installment purchase >12 months: separate principal vs interest. Principal = FA cost (discounted to cash price). Interest = finance cost over term, NOT added to FA cost
4. Donated assets: record at fair value. If conditional, 3387 → income when conditions met. If unconditional, ghi nhận vào thu nhập khác (TK 711)
5. Spare parts received with FA purchase: separate at fair value. If specialized/inseparable, treat as part of FA
6. Self-constructed assets: capitalize all direct costs + borrowing costs during construction
7. Barter transactions: FA acquired recorded at fair value of asset given up (or FA received if more reliable)

### 5.2 Depreciation Rules

1. Depreciation starts from the date asset is ready for use (đưa vào sử dụng)
2. Depreciation stops when asset is fully depreciated or disposed
3. Monthly depreciation = (Original cost - Residual value) / Useful life (months)
4. Residual value = estimated net realizable value at end of useful life (VAS 03: must be estimated; TT 99: reviewed at year-end)
5. Method change: allowed with economic justification, prospectively (not retroactively)
6. Useful life review: at least annually (year-end), adjust prospectively
7. Depreciation of fully-depreciated assets still in use: ZERO, continue tracking
8. Temporarily idle assets: continue depreciation EXCEPT for SOEs with stalled projects (TT 30/2025)

### 5.3 Revaluation Rules (TT 99/2025)

1. Fair Value Model option introduced — enterprises may elect to revalue PPE
2. Revaluation must cover entire class of assets
3. Revaluation surplus: ghi nhận vào TK 412 (Chênh lệch đánh giá lại tài sản)
4. Revaluation deficit: ghi nhận vào chi phí (TK 632) unless offsetting prior surplus
5. Frequency: regular enough that carrying value ≈ fair value at reporting date
6. SOE equitization: mandatory revaluation per TT 200/2014 (transition rules remain active)

### 5.4 Impairment Rules

1. FA carried at recoverable amount if impairment indicators exist
2. Recoverable amount = higher of fair value less costs to sell and value in use
3. Impairment loss: ghi nhận vào chi phí (TK 632)
4. Reversal of impairment: permitted if conditions improve (limited to cost model carrying amount)
5. Biological assets: use TK 2295 (new in TT 99)

### 5.5 Disposal Rules

1. Proceeds from sale: ghi nhận vào TK 711 (Thu nhập khác) or TK 511 (if core business)
2. Net book value (NG - KH lũy kế): ghi nhận vào TK 811 (Chi phí khác)
3. Loss on disposal = NBV - Proceeds + disposal costs
4. Gain on disposal = Proceeds - NBV - disposal costs
5. Output VAT: payable on FA sale
6. SOE infrastructure assets (Loại 6 per TT 147): require written approval from owner representative; proceeds remitted to state budget

### 5.6 FA Classification (per TT 147/2016 — 7 Types for tangible FA)

| Loại | Description |
|------|-------------|
| 1 | Nhà cửa, vật kiến trúc (Buildings, structures) |
| 2 | Máy móc, thiết bị (Machinery, equipment) |
| 3 | Phương tiện vận tải, thiết bị truyền dẫn (Transport, transmission) |
| 4 | Thiết bị, dụng cụ quản lý (Management equipment, tools) |
| 5 | Vườn cây lâu năm, súc vật làm việc và/hoặc cho sản phẩm |
| 6 | Kết cấu hạ tầng NN đầu tư (SOE infrastructure — NO depreciation, track wear only) |
| 7 | Các loại TSCĐ khác |

---

## 6. Data Model — Preliminary

### 6.1 Domain Entities

```
FixedAssetCategory (nhóm TSCĐ) — type, useful_life_min/max, depreciation_method
FixedAsset (thẻ TSCĐ) — code, name, category, original_cost, accumulated_depreciation,
  residual_value, useful_life, depreciation_method, acquisition_date, in_use_date,
  department_id, location, status, fund_source, asset_classification (loại 1-7)
DepreciationRecord (bảng tính KH) — asset_id, period, amount, accumulated_total, nbv
FAAdjustment (điều chỉnh) — type (revaluation/impairment/upgrade/transfer), amount, reason
FADisposal (thanh lý/nhượng bán) — type, disposal_date, proceeds, costs, gain_loss
FAInventory (kiểm kê) — check_date, difference, resolution
BiologicalAsset (tài sản sinh học) — extends FA, growth_stage, provision_for_loss
```

### 6.2 Database Tables (12 tables planned)

```
fa_categories, fa_assets, fa_depreciation_records, fa_adjustments,
fa_disposals, fa_inventories, fa_transfers, fa_spare_parts,
fa_biological_assets, fa_biological_provisions, fa_depreciation_methods,
fa_audit_log
```

---

## 7. Technical Architecture

### 7.1 Layer Mapping (per SmartACCT conventions)

| Layer | Component | Location |
|-------|-----------|----------|
| **Domain** | Pure Pydantic entities, enums | `domain/fa.py` |
| **Use Cases** | Business logic, validation | `use_cases/fa/__init__.py` |
| **Infrastructure** | SQLAlchemy models, repository | `infrastructure/models/fa_models.py`, `infrastructure/repositories/fa_repository.py` |
| **Presentation** | Flask blueprint, routes | `presentation/fa_routes.py` |
| **Migration** | Alembic scripts | `migrations/versions/` |

### 7.2 Key Design Decisions

1. **Depreciation engine**: pure Python with Decimal for precision — no SQL computation
2. **Period gating**: respect AccountingPeriod open/close status
3. **Audit trail**: every state change logged with before/after snapshot
4. **Biological assets**: separate hierarchy (TK 215) from traditional FA (TK 211)
5. **TT 99/2025 COA**: new accounts (215, 2295, 2414) mapped; removed accounts (441, 466) migrated to 4118
6. **i18n**: error codes per domain/i18n.py convention, Vietnamese + English translations

---

## 8. Reports

| Report | Description | Format |
|--------|-------------|--------|
| **Sổ TSCĐ** (FA Ledger) | Per-asset lifecycle record | HTML/PDF/Excel |
| **Bảng tính khấu hao** (Depreciation Schedule) | Monthly depreciation by asset | HTML/PDF/Excel |
| **Bảng tổng hợp tăng giảm TSCĐ** | FA movement summary | HTML/PDF/Excel |
| **Thẻ TSCĐ** (Asset Card) | Individual asset details | HTML/PDF |
| **Báo cáo kiểm kê TSCĐ** | Physical count vs book | HTML/PDF/Excel |
| **Bảng phân bổ khấu hao** | Depreciation by department/cost center | HTML/PDF/Excel |
| **Danh sách TSCĐ hết khấu hao** | Fully-depreciated assets still in use | HTML/PDF/Excel |
| **Báo cáo TSCĐ theo nguồn hình thành** | FA by source of funding | HTML/PDF/Excel |

---

## 9. Assumptions & Constraints

1. **Default depreciation method**: straight-line (adopt TT 45 default)
2. **Minimum FA value**: 30,000,000 VND per TT 45
3. **Exchange rate**: FA purchased in foreign currency recorded at spot rate on acquisition date
4. **Year-end**: per enterprise fiscal year, typically calendar year (01/01-31/12)
5. **VAT**: deductible VAT excluded from FA cost; non-deductible VAT included
6. **COA customization**: enterprise allowed per TT 99/2025 Điều 11 — internal regulation required

---

## 10. Open Questions

1. Fair Value Model adoption: Phase 1 minimal (cost model only), Phase 2 full? Need client decision.
2. Biological assets: cost model only or partial fair value? IAS 41 requires FV.
3. Accelerated depreciation: auto-approve up to 2x or require manual approval workflow?
4. Integration with Tax module: automatic CIT depreciation schedule alignment?
5. IFRS parallel books: required for listed companies from FY 2026 — Phase 2 feature.

---

## 11. Success Criteria

- [ ] All 7 FA types (TT 147/2016) supported
- [ ] 3 depreciation methods correctly computed
- [ ] TT 99/2025 COA implemented (incl. 215, 2295, 2414)
- [ ] FA acquisition/disposal/adjustment GL posting integrated
- [ ] Period-gated depreciation (closed-period protection)
- [ ] Comprehensive audit trail
- [ ] All reports generated in HTML/PDF/Excel
- [ ] Full i18n (vi + en)
- [ ] All existing tests continue passing
- [ ] 100+ tests specific to FA module

---

## 12. References

| Source | URL | Content |
|--------|-----|---------|
| MOF | mof.gov.vn | Official regulatory texts |
| GDT eTax | thuedientu.gdt.gov.vn | Tax declaration integration |
| Customs | customs.gov.vn | Import FA customs clearance |
| Social Insurance | baohiemxahoi.gov.vn | FA related to labor |
| National Public Service | dichvucong.gov.vn | Public services portal |
| VBPL | vbpl.vn | Legal document database |
| VACPA | vacpa.org.vn | Auditing standards |
| VAA | vaa.net.vn | Accounting association |
| IFRS Foundation | ifrs.org | International standards |
| EY Vietnam | ey.com/vn | Tax/accounting guidance |
| PwC Vietnam | pwc.com/vn | Market insights |
| Deloitte Vietnam | deloitte.com/vn | Regulatory updates |
| KPMG Vietnam | kpmg.com/vn | VAS-IFRS comparison |
| TT 99/2025 | thuvienphapluat.vn | Full text |
| VBHN 12/2025 | thuvienphapluat.vn | Consolidated depreciation rules |
| Webketoan | webketoan.vn | Vietnamese accounting community |
| Ketoanthienung | ketoanthienung.net | Training resources |
| Ketoan Leanh | ketoanleanh.edu.vn | Accounting education |
