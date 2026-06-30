# Accounts Payable (AP) Module — Vietnamese Regulatory Research

> Compiled: 2026-06-30
> Sources: 14 categories across MOF, GDT, Customs, Social Insurance, VACPA, VAA, IFRS, Big 4, Vietnamese accounting portals

---

## 1. CIRCULAR 133/2016/TT-BTC (SME Accounting Regime)

### 1.1 Account 331 — Phải trả người bán (Trade Payables)

**Legal basis**: Article 39 (liabilities principles) + Article 40 (account 331) of TT 133.

**Scope**: Records payables to vendors of materials, goods, services, fixed assets, real estate investments, financial investments, and construction contractors (main & sub). **Excludes** cash-on-delivery purchases.

**Detail tracking**: Must be tracked per vendor. Includes prepayments made to vendors before goods/services received.

**Key sub-items to track**:
- Payment discounts (chiết khấu thanh toán)
- Trade discounts (chiết khấu thương mại)
- Purchase returns and allowances (giảm giá hàng bán)
- **Must be recorded clearly** if not reflected on the purchase invoice

**Structure**:
| Side | Content |
|------|---------|
| Debit | Payments made, prepayments, discounts/settlements, purchase returns, FX loss revaluation |
| Credit | Payables arising, provisional price adjustments (upward), FX gain revaluation |
| Credit balance | Amounts still owed |
| Debit balance (possible) | Prepayments made or overpayment to vendor |

**Foreign currency (FC) rules**:
- **Initial recognition (Credit side)**: Convert at actual transaction rate (bank selling rate of the bank the entity usually transacts with)
- **Exception for prepayments**: When prepayment meets asset/expense recognition conditions, apply actual specific identification exchange rate for the prepaid portion
- **Settlement (Debit side)**: Apply actual specific identification exchange rate per creditor. If multiple transactions with same creditor: weighted average moving method
- **Prepayment disbursement**: Debit side uses actual transaction rate (bank selling rate) at prepayment date
- **Period-end revaluation**: All FC AP balances revalued at closing rate (bank selling rate at reporting date). Group entities may use parent-specified rate.

### 1.2 Accounting entries (TT 133)

**Purchase on credit**:
```
Dr 152/153/156/211   (purchase cost excl. VAT)
Dr 1331/1332        (deductible VAT)
   Cr 331           (total payable)
```

**Payment** (VND):
```
Dr 331
   Cr 111/112
```

**Payment** (FC):
```
Dr 331       (book rate — specific identification / moving weighted avg)
Dr 635       (FX loss if settlement rate > book rate)
   Cr 1112/1122  (book rate)
   Cr 515    (FX gain if settlement rate < book rate)
```

**Prepayment to vendor**:
```
Dr 331
   Cr 111/112
```

**Trade discount / settlement discount received**:
```
Dr 331
   Cr 152/156/.... (trade discount reducing inventory cost)
   Cr 515          (settlement discount = financial income)
```

**Goods received without invoice (end of month)**:
```
Dr 152/156   (provisional price)
   Cr 331
```
Adjust when actual invoice arrives.

**Bad debt — unrecoverable AP (creditor cannot be found, no longer claims)**:
```
Dr 331
   Cr 711 (other income)
```

---

## 2. CIRCULAR 200/2014/TT-BTC (Full Enterprise Accounting Regime)

### 2.1 Account 331 — Phải trả cho người bán

**Legal basis**: Article 50 (liability principles) + Article 51 (account 331).

**Same scope and principles** as TT 133, but with additional detail for:
- Larger enterprises
- Import-commission transactions
- More complex FX treatments

**Additional FX rule detail (TT 200 Article 51)**:
- When paying advance in FC: Debit 331 uses actual transaction rate at prepayment time
- When paying balance: Debit 331 uses specific identification book rate
- For creditors with multiple transactions: moving weighted average
- Period-end revaluation at bank selling rate

**End-of-period AP revaluation entry**:
```
If exchange rate increases:
Dr 635 (FX loss)
   Cr 331
If exchange rate decreases:
Dr 331
   Cr 515 (FX gain)
```

### 2.2 VAT — Input VAT deduction

**Article 19 (Account 133 — Deductible VAT)**:
- Must separate deductible vs non-deductible input VAT
- If cannot separate, record all as 133; determine at period-end
- Non-deductible input VAT goes to asset value, COGS, or operating costs
- Input VAT on imports: recorded as 1331 (goods/services) or 1332 (fixed assets)

**On AP module impact**: When booking purchase invoices, system must:
- Auto-split VAT-exclusive amount (Dr 152/156/211) vs VAT (Dr 133)
- Support full-amount, partial-amount, or 0% VAT invoices
- Support different VAT rates (0%, 5%, 8%, 10%)

---

## 3. NEWEST REGULATION — CIRCULAR 99/2025/TT-BTC

Effective for accounting periods from 2025 onward. **Account 331 rules reconfirmed** with updates:

- Same scope: vendors, suppliers, contractors (main & sub)
- Detail tracking per vendor including prepayments
- Must track discounts, trade discounts, purchase returns separately
- Can have debit balance (= prepayments or overpayment), shown as asset on balance sheet
- **New**: Payment discount (CK thanh toán) received for early payment is deducted from AP and recognized as financial revenue (TK 515)
- Same FC rules as TT 200/133

---

## 4. PROVISIONS FOR BAD DEBTS (AP-related)

### 4.1 Circular 48/2019/TT-BTC (as amended by Circular 24/2022/TT-BTC)

**Key point**: This circular governs **receivables** provisioning, but for AP module, it defines when AP balances can be written off.

**Provision rates for overdue receivables**:

| Overdue Period | Provision Rate |
|----------------|----------------|
| 6 months – < 1 year | 30% |
| 1 year – < 2 years | 50% |
| 2 years – < 3 years | 70% |
| ≥ 3 years | 100% |

**Special rates for telecom/retail**:

| Overdue Period | Provision Rate |
|----------------|----------------|
| 3 months – < 6 months | 30% |
| 6 months – < 9 months | 50% |
| 9 months – < 12 months | 70% |
| ≥ 12 months | 100% |

**Netting rule**: If a debtor has both receivables and payables, provision is calculated on the **net balance** after clearing.

**Write-off of AP**: When creditor no longer exists or debt is unrecoverable, AP can be written off as other income (TK 711).

---

## 5. E-INVOICE REQUIREMENTS FOR PURCHASES

### 5.1 Decree 123/2020/ND-CP + Circular 78/2021/TT-BTC

**Mandatory e-invoices**: All businesses use e-invoices from 1 July 2022.

**Invoice contents (Article 10, Decree 123)**:
- Invoice number, date
- Seller/buyer name, tax code, address
- Item description, unit, quantity, unit price, amount
- VAT rate, VAT amount, total payment
- Currency (VND or FC)
- E-signature of seller

**Purchase invoice processing rules**:
- Seller must issue invoice when transferring goods/services (including promotions, samples, gifts, internal use)
- E-invoice must be transmitted to buyer on same day as issuance
- E-invoice with or without tax authority code
- Correction process: if errors in tax code, amount, rate → issue replacement invoice. If errors in name/address → notify tax authorities (no re-issue required)

**Cash register e-invoices**: POS-connected e-invoices with real-time data transmission to tax authority.

**Goods received without invoice**: Must use provisional price, adjust when invoice arrives.

### 5.2 VAT input deduction requirements

For input VAT to be deductible:
- Must have valid e-invoice
- Goods/services must be for taxable business activities
- Payment via bank for transactions ≥ VND 20 million (per Circular 78/2021)
- Must declare VAT in correct period

---

## 6. FOREIGN CONTRACTOR TAX (FCT) — WITHHOLDING TAX ON FOREIGN VENDORS

### 6.1 Circular 103/2014/TT-BTC (primary) + Circular 86/2024/TT-BTC (procedural reforms) + Circular 69/2025/TT-BTC (VAT clarity)

**Three payment methods**:

| Method | VAT | CIT | Conditions |
|--------|-----|-----|------------|
| Deduction | Declaration method | Declaration method | PE in Vietnam, 183+ days, full VAS books |
| Direct (Withholding) | Withheld by Vietnamese party | Withheld by Vietnamese party | Default for foreign contractors without PE |
| Hybrid | Deduction method | Withheld by Vietnamese party | 183+ days, VAS books, no full deduction conditions |

**Withholding rates (Direct method)**:

| Business Line | VAT rate | CIT rate |
|---------------|----------|----------|
| Services | 5% | 5% |
| Services with machinery/equipment | 3% | 2% |
| Construction (no materials) | 5% | 2% |
| Construction (with materials) | 3% | 2% |
| Machinery/equipment leasing | 5% | 2% |
| Transportation | 3% | 2% |
| Interest | — | 5% |
| Royalties | — | 10% |
| Insurance | 5% | 5% |
| Restaurant/hotel | 5% | 2% |
| Other goods/services | 2% | 1% |

**Key AP module implications**:
- Vietnamese buyer **must** withhold FCT on payments to foreign vendors without PE
- If contract is "net" price → must gross-up to compute withholding
- WHT declared within 10 working days from tax liability arising
- Withholding amount = expense to Vietnamese entity BUT can claim input VAT credit on VAT portion
- DTA (Double Tax Agreement) relief available with valid tax residence certificate
- **New from 2025**: Foreign e-commerce/digital suppliers must register directly; platform operators may need to withhold

---

## 7. CUSTOMS — IMPORT PAYABLES

### 7.1 Account 3333 — Import/Export Duties

**Legal basis**: Article 41 (TT 133) / Article 52 (TT 200), confirmed by TT 99/2025.

**Import duty accounting**:

- Import duty = cost of goods (Dr 152/156/211)
```
Dr 152/156/211   (CIF value + import duty + excise tax)
Dr 1331          (input VAT on imports, if deductible)
   Cr 331         (payable to foreign vendor — CIF value in VND at transaction rate)
   Cr 3333        (import duty payable)
   Cr 3332        (excise tax, if applicable)
   Cr 33312       (VAT on imports)
```

- When paying duties:
```
Dr 3333
Dr 3332
Dr 33312
   Cr 111/112
```

**Import commission (ủy thác nhập khẩu)**:
- Principal (bên giao ủy thác): records 3333
- Agent (bên nhận ủy thác): does NOT record 3333, only records payment on behalf

**Tax refund on re-export**: Import duties paid can be refunded when goods are re-exported (processing, temporary import).

### 7.2 VAT on imports

- VAT on imported goods = (CIF value + import duty + excise tax) × VAT rate
- 33312 used for VAT on imports
- Can be deducted as input VAT if goods used for taxable activities

---

## 8. SOCIAL INSURANCE PAYABLES (ACCOUNT 334/338)

### 8.1 Contribution rates (2026)

| Component | Employer | Employee | Total |
|-----------|----------|----------|-------|
| Social Insurance (retirement/survivorship) | 14% | 8% | 22% |
| Social Insurance (sickness/maternity) | 3% | — | 3% |
| Occupational accident/disease | 0.5% | — | 0.5% |
| Health Insurance | 3% | 1.5% | 4.5% |
| Unemployment Insurance | 1% | 1% | 2% |
| **Total Vietnamese** | **21.5%** | **10.5%** | **32%** |
| **Total Foreign employees** | **20.5%** | **9.5%** | **30%** |

**Trade Union**: Employer 2% of salary; Employee 0.5% (if member). Effective from 1 July 2025.

**Caps**: Maximum salary for SI contribution = 20 × reference level (VND 46,800,000/month in 2026).

**AP module impact**:
- Insurance payable = Account 338 (3383: SI, 3384: HI, 3385: UI, 3386: TU)
- Monthly computation required
- Withholding from salary (employee portion) via Account 334
- Payment to Social Insurance agency by 25th of following month

---

## 9. VACPA — AUDIT STANDARDS FOR AP

### 9.1 Vietnamese Standards on Auditing (VSA)

Promulgated by Circular 214/2012/TT-BTC (37 standards based on ISA).

**AP-specific audit procedures (VSA 200, 315, 330, 500)**:

Key procedures for AP:
1. **Analytical procedures**: Compare AP balance vs prior year; calculate DPO (Days Payable Outstanding = AP / COGS × days)
2. **Confirmations**: Send AP confirmations to selected vendors (positive confirmations)
3. **Cut-off testing**: Ensure AP recorded in correct period (goods received before period-end included)
4. **Search for unrecorded liabilities**: Review subsequent payments, unmatched receipts, open AP files
5. **FX revaluation check**: Verify period-end revaluation at correct rates
6. **Related-party AP**: Identify and disclose related-party payables separately
7. **Debt clearing review**: Ensure proper accounting for offsetting
8. **Prepayment review**: Ensure prepayments to vendors are properly tracked and provisioned

**VACPA resources**: E-book tool (Ebook 1.12) for legal document lookup; Sample Audit Program for Group FS (SAP-AGFS); AP audit template B22.

---

## 10. VAS — VIETNAMESE ACCOUNTING STANDARDS (AP-RELEVANT)

### 10.1 VAS 01 — Framework

**Liability definition**: Present obligation arising from past transactions that must be settled using enterprise resources.

**Recognition criteria**: (a) Probable outflow of economic benefits; (b) Reliable measurement.

### 10.2 VAS 18 — Provisions, Contingent Liabilities & Contingent Assets

**Key principle**: Provisions distinguished from trade payables — trade payables are certain in timing/amount; provisions are uncertain.

**Provision recognition**: (a) Present obligation from past event; (b) Probable outflow; (c) Reliable estimate.

**Measurement**: Best estimate at balance sheet date. Discount to present value if time value material.

### 10.3 VAS differences from IFRS

| Aspect | VAS | IFRS |
|--------|-----|------|
| Chart of Accounts | Fixed, MOF-prescribed (incl. 331) | Flexible |
| Financial instruments | No equivalent IFRS 9 — AP at historical cost | AP at amortized cost (amortized cost under IFRS 9) |
| Impairment | No ECL model; Circular 48/2019 provisioning rates | ECL model |
| Fair value | Not required for liabilities | FVTPL option |
| Mandatory COA | Yes (MOF approval to modify Level 1/2) | No |

---

## 11. PAYMENT TERMS & AP BEST PRACTICES — VIETNAM

### 11.1 Market data (Atradius 2025 survey)

| Metric | Value |
|--------|-------|
| B2B sales on credit | 65% |
| Average payment terms | 45 days from invoice |
| Overdue invoices | 39% of B2B invoices |
| Bad debts | 3% of B2B invoices |
| DPO (Days Payable Outstanding) | Mixed — nearly equal split between faster/slower |
| Most-used trade finance | Bank loans + supplier credit |

### 11.2 AP best practices in Vietnamese context

1. **Three-way matching**: PO → Goods receipt note → Invoice
2. **Per-vendor tracking**: Mandatory per TT 133/200/99
3. **Payment prioritization**: Due date, vendor importance, early payment discount
4. **Credit limit controls**: Per contract terms
5. **Regular reconciliation**: Monthly debt confirmation (đối chiếu công nợ)
6. **Payment automation**: ACH, virtual cards, integration with accounting software
7. **Dispute management**: Flag and resolve discrepancies quickly
8. **Document retention**: Contracts, delivery receipts, invoices, payment evidence, email correspondence

---

## 12. CROSS-CURRENCY AP HANDLING — SUMMARY

### Accounting rules (all regimes)

1. **Initial recording**: Credit 331 at transaction rate (bank selling rate)
2. **Prepayment**: Credit 331 at specific identification rate
3. **Settlement**: Debit 331 at weighted average book rate (per vendor)
4. **Period-end revaluation**: All FC AP at bank selling rate → Dr/Cr 635/515
5. **Prepayment disbursement**: Debit 331 at actual transaction rate at prepayment time

### FCT on cross-border payments

Payments to foreign vendors without PE in Vietnam:
- Withhold VAT + CIT at applicable rates
- Declare within 10 working days
- DTA relief available
- If "net" contract → gross-up

---

## 13. WITHHOLDING TAX TYPES — QUICK REFERENCE

| Payment Type | WHT Rate | Legal Basis |
|-------------|----------|-------------|
| Dividends to non-resident | 5% | CIT Law |
| Interest to non-resident | 5% | CIT Law |
| Royalties to non-resident | 10% | CIT Law + DTA |
| Service fees to non-resident (FCT) | 5-10% CIT + 2-5% VAT | Circular 103/2014 |
| Domestic services (no WHT generally) | 0% | — |
| PIT on salary (employer withholds) | Progressive (5-35%) | PIT Law |

---

## 14. KEY DOCUMENTS & REFERENCES

| Document | Description |
|----------|-------------|
| Circular 133/2016/TT-BTC | SME accounting (Art. 39-40 for AP) |
| Circular 200/2014/TT-BTC | Full enterprise accounting (Art. 50-51 for AP) |
| Circular 99/2025/TT-BTC | Newest accounting regime |
| Circular 48/2019/TT-BTC + 24/2022 | Provisions for bad debts |
| Circular 103/2014/TT-BTC | Foreign Contractor Tax |
| Circular 86/2024/TT-BTC | FCT procedural reforms |
| Circular 69/2025/TT-BTC | VAT for foreign contractors |
| Decree 123/2020/ND-CP | E-invoices |
| Circular 78/2021/TT-BTC | E-invoice guidance |
| VAS 01 | Framework — liability definition |
| VAS 18 | Provisions, contingent liabilities |
| Law on Tax Administration 38/2019/QH14 | Tax admin |
| CIT Law 67/2025/QH15 | Corporate income tax (effective 1 Oct 2025) |
| VAT Law 48/2024/QH15 | VAT (effective 1 Jul 2025) |
| Social Insurance Law 2024 | SI (effective 1 Jul 2025) |
| Circular 214/2012/TT-BTC | Audit standards (VSA) |

---

## 15. AP MODULE — FUNCTIONAL REQUIREMENTS DERIVED

### Core features needed

1. **Vendor master**: Per-vendor tracking with tax code, address, currency, payment terms
2. **Invoice processing**: E-invoice support, 3-way matching, auto-split VAT
3. **AP aging**: By vendor, by due date, by overdue bucket (30/60/90/180/365+ days)
4. **Payment processing**: VND + FC, partial payments, prepayments, discount capture
5. **Payment scheduling**: Based on due date, cash position, vendor priority
6. **Debt reconciliation**: Monthly confirmation letters (đối chiếu công nợ)
7. **FX management**: Auto-revaluation at period-end, FX gain/loss tracking
8. **FCT computation**: Auto-calculate withholding for foreign vendors
9. **AP provisioning**: Track overdue for provision calculation per Circular 48
10. **AP write-off**: When creditor unreachable → transfer to 711
11. **E-invoice verification**: Validate invoice against PO/goods receipt
12. **Multi-currency**: Track per-currency, per-vendor balances
13. **Audit trail**: All AP changes logged per audit standards
14. **Integration**: GL (331, 133, 3333, 33312, 338), COA, Cash, Tax modules
15. **Reporting**: AP aging, DPO, vendor payments, FX exposure, provision schedule, FCT returns

### Vietnamese-specific features

1. Account code 331 (mandatory chart of accounts)
2. VAT at 0%/5%/8%/10% rates — correct rate handling by goods type
3. 3333 import duty tracking
4. FCT withholding for foreign vendors (Circular 103/2014 + updates)
5. Electronic invoice compliance (Decree 123/2020)
6. VND locale formatting (1.000.000,00 đ)
7. Insurance payable computation (334/338)
8. Social insurance/health insurance/unemployment insurance rates tracking
9. Bad debt provision per Vietnamese aging brackets
10. Debt offset (bù trừ công nợ) when same entity is both customer and vendor
