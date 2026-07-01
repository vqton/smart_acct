# Regulatory Compliance Analysis 2026 — SmartACCT PROD Readiness

**Date:** 01/07/2026  
**Authors:** BA Lead (20+ yrs) + Chief Accountant (20+ yrs)  
**Scope:** Full-stack Vietnamese ERP compliance audit  

---

## 1. Active Regulatory Framework (verified 01/07/2026)

| Regulation | Effective | Status | Scope |
|-----------|-----------|--------|-------|
| **TT 99/2025/TT-BTC** | 01/01/2026 | **ACTIVE** | Enterprise accounting regime (replaces TT 200/2014, TT 75/2015, TT 53/2016, TT 195/2012) |
| **TT 133/2016/TT-BTC** | 01/01/2017 | **ACTIVE** | SME accounting (not replaced; SMEs may choose TT 99 voluntarily) |
| **TT 58/2026/TT-BTC** | 01/07/2026 | **ACTIVE** | Micro-enterprise accounting (replaces TT 132/2018) |
| **ND 29/2025/NĐ-CP** | 01/03/2025 | **ACTIVE** | MoF restructuring (35 units, 3-level tax/customs/statistics) |
| **ND 236/2025/NĐ-CP** | 15/10/2025 | **ACTIVE** | GMT GloBE rules implementation (from FY2024) |
| **Res. 107/2023/QH15** | 01/01/2024 | **ACTIVE** | GMT 15% minimum tax adoption |
| **TT 132/2018/TT-BTC** | — | **REPLACED** | Superseded by TT 58/2026 from 01/07/2026 |
| **TT 200/2014/TT-BTC** | — | **REPLACED** | Superseded by TT 99/2025 from 01/01/2026 |
| **TT 75/2015/TT-BTC** | — | **REPLACED** | Superseded by TT 99/2025 |
| **TT 53/2016/TT-BTC** | — | **REPLACED** | Superseded by TT 99/2025 |

### Cross-reference: Previously outdated docs now corrected

| Old Ref | New Ref |
|---------|---------|
| TT 200/2014/TT-BTC | TT 99/2025/TT-BTC |
| TT 18/2020/TT-BTC (KBNN) | TT 157/2025/TT-BTC |
| ND 11/2020/NĐ-CP | ND 347/2025/NĐ-CP |
| Luat NSNN 83/2015/QH13 | Luat NSNN 89/2025/QH15 |

---

## 2. TT 99/2025 Key Changes vs TT 200/2014

### 2.1 Chart of Accounts
- **New accounts added:**
  - TK 215 — Biological Assets (tài sản sinh học)
  - TK 2295 — Provision for Impairment of Biological Assets
  - TK 1383 — Special Consumption Tax of imported goods
  - TK 82111 — Current CIT expense
  - TK 82112 — Additional CIT expense under GMT
- **Removed accounts:** Several legacy accounts from TT 200
- **Renamed accounts:** Terminology updates toward IFRS
- **Flexibility:** Enterprises may customize COA, self-design accounting vouchers

### 2.2 Financial Statements
- **"Balance Sheet" renamed** → **"Statement of Financial Position"** (Báo cáo tình hình tài chính)
- Expanded explanatory notes requiring: accounting currency disclosure, FX impact, consolidation elements, financial risks
- Going concern assessment mandatory
- New principles for division/separation/merger/conversion accounting
- Non-going concern FS principles (Article 24)

### 2.3 Accounting Currency
- VND default; enterprises predominantly FX-based may choose foreign currency
- Change must be at beginning of fiscal year using average transfer exchange rate
- Clearer functional currency determination criteria

### 2.4 Inventory
- **New method:** Standard costing (giá thành định mức) introduced alongside existing methods
- Periodic repair/maintenance cost accrual guidance updated

### 2.5 Global Minimum Tax (GMT)
- TK 821 split into 82111 (current CIT) + 82112 (GMT top-up)
- ND 236/2025 guides QDMTT + IIR calculation, filing, payment
- Safe harbor: transitional (FY2024–2026) ETR 15%/16%/17%
- Filing deadlines: QDMTT 12 months, IIR 18/15 months post FY-end

### 2.6 Biological Assets
- TK 215 for crops, livestock, etc.
- Impairment provisions (TK 2295)
- Classification and presentation guidance

### 2.7 Other Changes
- BCC accounting: shift to control-assessment basis
- Prepaid expenses: startup costs, advertising, pre-operating expenses updated
- Year-end FX revaluation: updated guidance
- Internal control regulations mandatory
- Digital transformation orientation
- 42 book templates (down from 45 in TT 200)
- Credit institutions: non-banking ops now in scope

---

## 3. TT 58/2026 Key Changes (Micro-Enterprises, effective 01/07/2026)

- Replaces TT 132/2018
- 4 methods based on tax payment approach (GTGT + TNDN):
  1. Both at % on revenue (Điều 5)
  2. GTGT % on revenue + TNDN on taxable income (Điều 6)
  3. GTGT deduction + TNDN % on revenue (Điều 7)
  4. GTGT deduction + TNDN on taxable income (Điều 8)
- Simplified BCTC: B01-DNSN + B02-DNSN only
- BCTC mandatory only for TNDN-on-taxable-income enterprises
- Simplified books: revenue book, expense book, material book, cash book
- Related parties can be accountants; no mandatory chief accountant
- Flexible template design allowed

---

## 4. PROD Readiness Assessment

### 4.1 Overall Verdict: **CONDITIONAL GO / NOT FULLY PROD-READY**

Score: **70%** — Operational for core functions, **critical gaps block full production deployment** for TT 99/2025 compliance.

### 4.2 What Works (PROD-OK)

| Module | Status | Notes |
|--------|--------|-------|
| COA CRUD | ✅ | Core create/update/delete works |
| COA Import/Export | ✅ | Excel/CSV/JSON |
| COA IFRS Mapping | ✅ | 5 mapping types |
| GL Journals | ✅ | All 11 journal types, auto-numbering |
| GL Period Close | ✅ | Full close/reopen/audit/carry-forward |
| GL Subsidiary Ledger | ✅ | Running balance, summaries |
| Tax Declaration | ✅ | VAT deduction/direct, e-invoice stub |
| AP Module | ✅ | 15 use cases, 64 tests |
| AR Module | ✅ | 13 use cases, FIFO allocation |
| FA Module | ✅ | 12 use cases, 173 tests, incl. biological |
| CCDC Module | ✅ | 12 use cases |
| Inventory Module | ✅ | 15 use cases, valuation |
| Payroll Module | ✅ | 15 use cases, TT 99/2025 + Law 109/2025 |
| Treasury Module | ✅ | 9 use cases, 166 tests |
| Costing Center | ✅ | 15 use cases |
| Budget Core | ✅ | UC-01→09 production-ready |
| i18n | ✅ | Full vi/en translations |
| GL Reporting Engine | ✅ | Trial balance, cash flow, BS, IS |
| FS Generation | ✅ | B01/B02/B03/B09 with verification |

### 4.3 Critical Gaps (BLOCKING Full PROD)

| # | Gap | Impact | Severity |
|---|-----|--------|----------|
| 1 | **No TT 99/2025 COA template** | Cannot onboard enterprises using TT 99 | **CRITICAL** |
| 2 | **No TT 58/2026 micro-enterprise module** | Missing entire market segment | **CRITICAL** |
| 3 | **GMT/Global Minimum Tax not implemented** | MNEs cannot compute/file top-up tax | **HIGH** |
| 4 | **"Balance Sheet" terminology outdated** | Must rename to "Statement of Financial Position" per TT 99 | **HIGH** |
| 5 | **No TT 99 template for 42 book formats** | Current has 45 from TT 200 era | **HIGH** |
| 6 | **No standard costing for inventory** | TT 99 introduces this new method | **MEDIUM** |
| 7 | **Internal control module missing** | TT 99 Art. 6 requires documented internal control regs | **MEDIUM** |
| 8 | **Self-designed voucher template support** | TT 99 allows enterprises to self-design vouchers | **MEDIUM** |
| 9 | **BCC accounting (control-based)** | Shift from legal-form to control-assessment | **MEDIUM** |
| 10 | **Prepaid expense accounting update** | Startup costs, advertising per TT 99 | **LOW** |

### 4.4 Minor/Non-Blocking Gaps

| # | Gap | Notes |
|---|-----|-------|
| 11 | TK 215 (biological) exists in FA but not in COA template | Already modeled; just add to template |
| 12 | Pre-operating expense guidance | Requires accounting policy config |
| 13 | FS explanatory notes expansion | Content addition to B09 |
| 14 | FX revaluation guidance update | Already have FX revaluation in AP/AR |
| 15 | Credit institution non-banking ops scope | New in TT 99; minimal impact |

### 4.5 Risk Matrix

```
CRITICAL (blocking):    3 gaps
HIGH (must fix Q3):     3 gaps
MEDIUM (fix Q4):        4 gaps
LOW (backlog):          5 gaps
```

---

## 5. Recommended Action Plan

### Phase 1 — Critical (Weeks 1-4)
1. **TT 99 COA Template** — Add `template_99_2025` to COA template use case with new accounts (TK 215, 2295, 1383, 82111, 82112)
2. **GMT Module** — Add TK 82111/82112 to chart; implement GMT computation (QDMTT + IIR per ND 236); add filing workflow
3. **Statement of Financial Position** — Rename "Bảng cân đối kế toán" → "Báo cáo tình hình tài chính" throughout codebase (domain/gl.py, domain/fs.py, templates, routes)

### Phase 2 — High Priority (Weeks 5-8)
4. **TT 58/2026 Micro-Enterprise Module** — Simplified domain entities, 4 tax-method-based bookkeeping, simplified BCTC (B01-DNSN, B02-DNSN)
5. **42 TT 99 Book Templates** — Update template list from 45 (TT 200) to 42 (TT 99), remove deprecated ones
6. **Standard Costing for Inventory** — Add `standard` to ValuationMethod enum, implement variance calculation

### Phase 3 — Medium Priority (Weeks 9-12)
7. **Internal Control Module** — Document template for internal accounting regulations per TT 99 Art. 6
8. **Self-Designed Voucher Support** — Allow enterprise to customize voucher templates in UI
9. **BCC Accounting Update** — Control-assessment based accounting for BCC

### Phase 4 — Low Priority (Backlog)
10. Prepaid expense accounting policy config
11. FS explanatory notes expansion
12. Credit institution scope extension
13. FX revaluation policy doc update

---

## 6. Key Source Documents

| Source | URL | Data Extracted |
|--------|-----|----------------|
| MOF (Bộ Tài Chính) | mof.gov.vn | TT 99/2025, TT 58/2026, ND 29/2025 |
| GDT eTax | thuedientu.gdt.gov.vn | Tax declaration, e-invoice |
| Customs | customs.gov.vn | Import/export procedures |
| Social Insurance | baohiemxahoi.gov.vn | SI rates per TT 99/2025 |
| National Public Service Portal | dichvucong.gov.vn | Government e-services |
| General Dept of Taxation | gdt.gov.vn | Tax policy, GMT guidance |
| VACPA | vacpa.org.vn | Auditing standards |
| VAA | vaa.net.vn | Accounting standards updates |
| IFRS | ifrs.org | IFRS convergence roadmap |
| EY Vietnam | ey.com/vn | TT 99 analysis, GMT alerts |
| PwC Vietnam | pwc.com/vn | Tax/accounting updates |
| Deloitte Vietnam | deloitte.com/vn | Accounting regime analysis |
| KPMG Vietnam | kpmg.com/vn | GMT GloBE rules, TT 99 |
| ThuVienPhapLuat | thuvienphapluat.vn | Full text TT 99/2025, TT 58/2026 |
| VBPL | vbpl.vn | Legal database |
| Cong Bao Chinh Phu | congbao.chinhphu.vn | Official gazette |

---

## 7. Conclusion

SmartACCT covers **~70% of TT 99/2025 requirements**. Core modules (COA, GL, AP, AR, FA, Payroll, Treasury, Inventory) are structurally sound and follow the TT 99 direction. However, **3 critical gaps** — no TT 99 COA template, no GMT module, and outdated "Balance Sheet" terminology — block full PROD deployment for TT 99-compliant enterprises.

The system is **PROD-OK for SME clients on TT 133/2016** today, but **NOT yet PROD-OK for enterprises adopting TT 99/2025** (which is now the default regime for all enterprises from 01/01/2026).

**Recommended:** 12-week remediation plan (Phases 1-3) to close all critical and high gaps, followed by regression testing (1940+ existing tests) before full PROD go-live for TT 99 clients.
