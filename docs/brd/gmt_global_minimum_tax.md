# BRD: Global Minimum Tax Module — SmartACCT

**Author:** BA Lead + Chief Accountant  
**Date:** 01/07/2026  
**Status:** DRAFT  
**Priority:** CRITICAL (blocks MNEs from using SmartACCT)

---

## 1. Objective

Implement GMT (Global Minimum Tax 15%) computation, filing, and accounting per ND 236/2025/NĐ-CP and Res. 107/2023/QH15.

## 2. Regulatory Basis

- **Res. 107/2023/QH15** (29/11/2023) — GloBE rules adoption, effective FY2024
- **ND 236/2025/NĐ-CP** (29/08/2025) — Detailed guidance, effective 15/10/2025
- **TT 99/2025/TT-BTC** Art. 14 — Account 82111 (current CIT) + 82112 (GMT additional CIT)
- **OECD GloBE Rules** — Pillar Two model rules

## 3. Current State

- TK 821 not split (exists as single account)
- No GMT computation engine
- No GMT filing workflow
- No safe harbor test
- No QDMTT/IIR distinction

## 4. Requirements

### 4.1 Chart of Accounts
- TK 82111 — Chi phí thuế TNDN hiện hành (Current CIT)
- TK 82112 — Chi phí thuế TNDN bổ sung theo GMT (GMT Top-up CIT)
- Mapping to FS B02-DN lines 51/52

### 4.2 GMT Computation Engine

**Inputs:**
- Ultimate Parent Entity (UPE) consolidated FS
- GloBE income/loss per jurisdiction
- Covered taxes per jurisdiction
- Substance-based income exclusion (payroll + tangible assets)
- Transitional safe harbor flags

**Calculations:**
- Jurisdictional ETR = Adjusted Covered Taxes / Net GloBE Income
- Top-up Tax % = max(0, 15% - ETR)
- Top-up Tax = max(0, Excess Profit × Top-up Tax %)
- QDMTT: Vietnam domestic top-up
- IIR: Parent jurisdiction top-up
- Safe harbor: De minimis (€10M/€1M), ETR test, routine profit test

### 4.3 Filing Workflow

| Form | Description | Deadline |
|------|-------------|----------|
| Notice of filing CE | Identify Vietnamese constituent entities | 30 days post FY-end |
| QDMTT return | Domestic top-up calculation | 12 months post FY-end |
| IIR return | Foreign top-up calculation | 18 months (1st year), 15 months (subsequent) |
| GloBE information return | Global data | Same as QDMTT/IIR |
| CbCR notification | Country-by-country reporting | Per CbCR rules |

### 4.4 Transitional Safe Harbor (FY2024–2026)

| FY | Simplified ETR |
|----|---------------|
| 2024 | ≥15% |
| 2025 | ≥16% |
| 2026 | ≥17% |

If any test met → top-up tax = 0.

### 4.5 Accounting Entries

```
1. Current CIT accrual:
   Nợ TK 82111 / Có TK 3334

2. GMT top-up accrual:
   Nợ TK 82112 / Có TK 3334 (or separate GMT payable)
```

## 5. Success Criteria

- [ ] TK 82111 + 82112 in COA with correct DCR/type
- [ ] GMT computation engine: ETR, top-up, safe harbor
- [ ] QDMTT + IIR return generation
- [ ] Filing deadline tracking
- [ ] FS mapping B02-DN lines 51/52 updated
- [ ] 30+ integration tests (all safe harbor scenarios, QDMTT/IIR, edge cases)

## 6. Files Touched

- `domain/gl.py` — Add TK 82111/82112 to GL account list
- `domain/tax.py` — Add GMT entity/enums
- `use_cases/tax/__init__.py` — Add GMT computation
- `infrastructure/models/tax_models.py` — Add GMT tables
- `infrastructure/repositories/tax_repository.py` — GMT CRUD
- `presentation/tax_routes.py` — GMT endpoints
- `use_cases/coa/template_use_case.py` — Add TK 82111/82112 to TT 99 template

## 7. User Journeys

### Happy Path — MNE Compliance
1. User enters UPE consolidated data (or uploads CbCR)
2. System computes ETR per jurisdiction
3. System tests safe harbor → none met
4. System computes top-up tax = (15% - 12%) × Excess Profit
5. Generates QDMTT return for Vietnam
6. Generates IIR return for foreign jurisdictions
7. Shows filing deadlines
8. Posts accounting entries (Nợ 82112/Có 3334)

### Alternative Path — Safe Harbor Met
1-2. Same
3. Safe harbor ETR test passes (ETR ≥17% for FY2026)
4. Top-up tax = 0
5. System shows "No GMT liability — safe harbor met"
6. No return needed (but notification still required)

### Exception Path — Insufficient Data
1. User has no UPE consolidated data
2. System shows estimated computation based on local data
3. Warning: "GloBE data required for accurate computation"
4. Files estimated QDMTT with note
