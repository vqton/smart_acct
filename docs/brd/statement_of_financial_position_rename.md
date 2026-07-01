# BRD: Rename "Balance Sheet" to "Statement of Financial Position"

**Author:** BA Lead + Chief Accountant  
**Date:** 01/07/2026  
**Status:** DRAFT  
**Priority:** HIGH (TT 99 Art. 18 requirement)

---

## 1. Objective

Rename all "Balance Sheet" / "Bảng cân đối kế toán" references to "Statement of Financial Position" / "Báo cáo tình hình tài chính" per TT 99/2025 Art. 18.

## 2. Regulatory Basis

TT 99/2025/TT-BTC Art. 18:
- "Bảng cân đối kế toán" (Balance Sheet) → "Báo cáo tình hình tài chính" (Statement of Financial Position)
- IFRS alignment: IAS 1 uses "Statement of Financial Position"

## 3. Current State

Domain layer uses `balance_sheet` as `statement_type` enum value in:
- `domain/gl.py:434` — `STATEMENT_TYPES = ["balance_sheet", ...]`
- `domain/fs.py:13` — `BALANCE_SHEET_GC = "B01_DN"` (OK — code name stays, UI label changes)
- `use_cases/gl/__init__.py` — `generate_balance_sheet()` method name
- `presentation/gl/reports.py` — route labels
- Templates: `templates/trial_balance.html` — hardcoded references
- i18n: translation keys

## 4. Requirements

### 4.1 Code Changes

| Location | Change | Scope |
|----------|--------|-------|
| `domain/gl.py:419` | `statement_type` validator description | Comment only |
| `domain/gl.py:434` | `STATEMENT_TYPES` list | Keep `balance_sheet` as internal code |
| `domain/gl.py` method names | `calculate_balance_sheet_totals`, `generate_balance_sheet` | Add alias methods; old deprecated |
| `domain/fs.py:13` | `BALANCE_SHEET_GC` enum | Keep code, update docstring |
| `use_cases/gl/__init__.py` | `generate_balance_sheet` → `generate_statement_of_financial_position` | Add new; deprecate old |
| `use_cases/fs/__init__.py` | `verify_balance_sheet` → `verify_statement_of_financial_position` | Add alias |
| `presentation/gl/reports.py` | Route docstrings, response labels | Update |
| `presentation/fs/routes.py` | API response labels | Update |

### 4.2 UI / Template Changes

- `templates/trial_balance.html` — title, headers
- `templates/fs/*.html` — B01-DN template header "BÁO CÁO TÌNH HÌNH TÀI CHÍNH"
- i18n `.po` files — update Vietnamese labels

### 4.3 API Compatibility

- Old route `/api/v1/gl/reports/balance-sheet` → keep with redirect
- New route `/api/v1/gl/reports/statement-of-financial-position`
- Internal code still `"balance_sheet"` for backward compat

## 5. Success Criteria

- [ ] All user-facing "Balance Sheet" → "Statement of Financial Position"
- [ ] B01-DN header: "BÁO CÁO TÌNH HÌNH TÀI CHÍNH"
- [ ] API backward compatibility maintained
- [ ] All 112 GL tests + 102 FS tests pass
- [ ] i18n updated for vi + en

## 6. Impact Analysis

| Module | Impact | Effort |
|--------|--------|--------|
| domain/gl.py | Low — code aliases only | 1 file |
| domain/fs.py | Low — docstrings | 1 file |
| use_cases/gl | Medium — method aliases | 1 file |
| use_cases/fs | Low — method rename | 1 file |
| presentation/gl | Low — route labels | 2 files |
| presentation/fs | Low — route labels | 1 file |
| templates/fs | Low — header text | 4+ files |
| i18n | Low — translation keys | 2 .po files |

## 7. User Journeys

### Happy Path
1. User generates B01-DN from FS module
2. Header displays "BÁO CÁO TÌNH HÌNH TÀI CHÍNH" (not "BẢNG CÂN ĐỐI KẾ TOÁN")
3. HTML/PDF/XLSX export shows correct name
4. Legal compliance satisfied

### Exception Path
1. User calls old API endpoint `/api/v1/gl/reports/balance-sheet`
2. System returns 301 redirect to `/api/v1/gl/reports/statement-of-financial-position`
3. No data loss
