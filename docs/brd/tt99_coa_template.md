# BRD: TT 99/2025 COA Template — SmartACCT

**Author:** BA Lead + Chief Accountant  
**Date:** 01/07/2026  
**Status:** DRAFT  
**Priority:** CRITICAL (blocks TT 99 PROD go-live)

---

## 1. Objective

Add TT 99/2025 Chart of Accounts template to SmartACCT, enabling enterprises using the new regime (default from 01/01/2026) to onboard with correct account structure.

## 2. Regulatory Basis

TT 99/2025/TT-BTC, Phụ lục 2 — Hệ thống tài khoản kế toán doanh nghiệp:
- 800-page document with full account list
- 42 book templates (down from 45 in TT 200)
- New accounts: TK 215, 2295, 1383, 82111, 82112
- Removed accounts from TT 200
- Renamed accounts toward IFRS alignment
- Enterprises may customize sub-accounts

## 3. Current State

- Only `template_133_2016` exists in `use_cases/coa/template_use_case.py`
- No TT 99 template
- TT 99 new accounts (215, 2295, 1383, 8211x) not in system

## 4. Requirements

### 4.1 New Accounts (vs TT 200 / TT 133)

| TK | Name (VN) | Name (EN) | Type | DCR |
|----|-----------|-----------|------|-----|
| 215 | Tài sản sinh học | Biological Assets | ASSET | Debit |
| 2295 | Dự phòng giảm giá TSBH | Provision for Biological Assets | ASSET | Credit |
| 1383 | Thuế TTĐB hàng nhập khẩu | SCT of Imported Goods | ASSET | Debit |
| 82111 | Chi phí thuế TNDN hiện hành | Current CIT Expense | EXPENSE | Debit |
| 82112 | Chi phí thuế TNDN bổ sung (GMT) | GMT Additional CIT Expense | EXPENSE | Debit |

### 4.2 Account Changes from TT 200

- TK 821 → split into 82111 + 82112
- TK 214 → updated terminology
- Equity accounts → IFRS-aligned names
- Remove legacy accounts per TT 99 Appendix 2

### 4.3 Template Implementation

- `template_99_2025` — Standard enterprise (replaces TT 200)
- `template_99_2025_sme` — SME opt-in (simplified subset of TT 99 accounts)
- Both include all 33+ account types, DCR directions, VAS compliance flags

### 4.4 Migration Path

- Existing TT 133 accounts → TT 99 mapping table
- User option: continue TT 133 OR migrate to TT 99 at fiscal year start
- Notice to tax authority required per TT 99 Art. 31(2)

## 5. Success Criteria

- [ ] `template_99_2025` loads 500+ accounts with correct codes, names, types, DCR
- [ ] New accounts (215, 2295, 1383, 82111, 82112) present
- [ ] TT 99 book template list = 42 (not 45)
- [ ] All existing COA CRUD/import/export/IFRS mapping work with TT 99 template
- [ ] VAS compliance scan passes for TT 99 accounts

## 6. Files Touched

- `domain/coa.py` — Add TT 99 enum values if needed
- `use_cases/coa/template_use_case.py` — Add `template_99_2025` + `template_99_2025_sme`
- `tests/test_coa_domain.py` — Update for TT 99 template

## 7. User Journeys

### Happy Path
1. Admin selects "TT 99/2025" template on COA setup
2. System loads 500+ accounts with correct codes, names, DCR
3. Admin customizes sub-accounts as needed
4. System validates VAS compliance
5. Template saved; ready for journal posting

### Alternative Path
1. Admin selects "TT 99/2025 (SME opt-in)" — simplified account subset
2. Same flow but with fewer accounts

### Exception Path
1. Admin selects TT 99 but has existing TT 133 data
2. System shows migration mapping
3. Migration runs at fiscal year start per TT 99 Art. 31
4. Tax authority notification generated
