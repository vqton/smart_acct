# BRD: TT 58/2026 Micro-Enterprise Module

**Author:** BA Lead + Chief Accountant  
**Date:** 01/07/2026  
**Status:** DRAFT  
**Priority:** CRITICAL (new regulation effective 01/07/2026)

---

## 1. Objective

Implement micro-enterprise accounting module per TT 58/2026/TT-BTC (effective 01/07/2026, replaces TT 132/2018).

## 2. Regulatory Basis

TT 58/2026/TT-BTC:
- **Điều 1-3:** Scope, subjects (micro-enterprises, business households opt-in)
- **Điều 4:** Accounting regime selection based on tax method
- **Điều 5:** Both GTGT + TNDN at % on revenue
- **Điều 6:** GTGT % on revenue + TNDN on taxable income
- **Điều 7:** GTGT deduction + TNDN % on revenue
- **Điều 8:** GTGT deduction + TNDN on taxable income
- **Điều 10:** Financial statements (B01-DNSN, B02-DNSN)
- **Điều 12:** Effective 01/07/2026, replaces TT 132/2018

## 3. Current State

- No micro-enterprise entities/models
- No simplified bookkeeping
- No tax-method-based accounting variants
- TT 132/2018 not implemented (now superseded)

## 4. Requirements

### 4.1 Domain Entities

Enums:
- `MicroTaxMethod`: GTGT_PCT_REVENUE_TNDN_PCT_REVENUE (Điều 5), GTGT_PCT_REVENUE_TNDN_INCOME (Điều 6), GTGT_DEDUCTION_TNDN_PCT_REVENUE (Điều 7), GTGT_DEDUCTION_TNDN_INCOME (Điều 8)
- `MicroBookType`: REVENUE_BOOK, EXPENSE_BOOK, MATERIAL_BOOK, CASH_BOOK, TAX_DETAIL

Entities:
- `MicroEnterpriseSetup`: enterprise profile, tax method, accounting method
- `MicroRevenueBook`: simplified revenue tracking by product/service group
- `MicroExpenseBook`: simplified expense tracking
- `MicroMaterialBook`: basic material/inventory tracking
- `MicroCashBook`: cash-in/cash-out tracking
- `MicroTaxCalculation`: GTGT+TNDN computation per method

### 4.2 Simplified Books

| Book | Điều | Purpose |
|------|------|---------|
| Sổ doanh thu bán hàng hóa, dịch vụ | 5-6 | Revenue tracking with tax rate groups |
| Sổ chi tiết doanh thu, chi phí | 6-8 | For TNDN-on-income method |
| Sổ chi tiết vật liệu, dụng cụ, SP, HH | 7-8 | Material tracking |
| Sổ chi tiết tiền | All | Cash tracking |
| Sổ theo dõi thuế GTGT | 7-8 | VAT input/output tracking |

### 4.3 Financial Statements

- **B01-DNSN:** Báo cáo tình hình tài chính (micro) — simplified: cash, receivables, payables, equity
- **B02-DNSN:** Báo cáo kết quả hoạt động (micro) — simplified: revenue, expenses, tax, net profit
- **Not mandatory** for Điều 5 enterprises (TNDN % on revenue)

### 4.4 Organizational Rules
- No mandatory chief accountant
- Related parties may serve as accountants
- External accounting service allowed
- Flexible template design permitted

## 5. Success Criteria

- [ ] 4 tax-method-based bookkeeping flows implemented
- [ ] Simplified BCTC: B01-DNSN + B02-DNSN generation
- [ ] Tax calculation for each method (GTGT + TNDN)
- [ ] B01-DNSN/B02-DNSN for TNDN-on-income; option to skip for %-on-revenue
- [ ] 40+ integration tests
- [ ] All existing tests pass

## 6. Implementation Notes

- Micro-enterprise is a **separate module** — simpler than full ERP
- Reuse existing COA (TT 133 or TT 99) at reduced account count
- Focus on cash-basis accounting with minimal accruals
- GTGT tracking must handle deduction vs %-on-revenue variants

## 7. User Journeys

### Happy Path — Điều 5 (Simplest)
1. User registers as micro-enterprise, selects "GTGT % + TNDN % on revenue"
2. System shows revenue book template
3. User enters monthly revenue by product group
4. System auto-calculates GTGT + TNDN at prescribed rates
5. System generates simplified tax return data
6. BCTC not required

### Alternative Path — Điều 8 (Full Accounting)
1. User selects "GTGT deduction + TNDN on income"
2. System shows all 4 books (revenue, expense, material, cash)
3. User records GTGT input invoices for deduction
4. System computes TNDN on taxable income
5. System generates B01-DNSN + B02-DNSN

### Exception Path — Method Change
1. User's tax method changes mid-year
2. Warning: "Method change only at fiscal year start"
3. Recommends completing current year on existing method
4. New method applied next fiscal year
