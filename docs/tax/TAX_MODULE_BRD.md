# BRD: Tax Module - SmartACCT ERP

**Version:** 1.0
**Date:** 2026-06-26
**Author:** BA Lead (20yr) + Chief Accountant (20yr) - VAS Expert
**Status:** Draft

---

## 1. Executive Summary

Build Tax module for SmartACCT ERP covering all VN tax types. Support Circular 99/2025/TT-BTC accounting regime, comply with latest tax laws (2025-2026). Replace manual HTKK filing with automated engine. Integrate e-invoice (ND 70/2025), e-tax portal, GDT.

**Objective:** Full lifecycle tax management: calc -> declare -> pay -> report -> audit trail.

---

## 2. Legal Framework (Latest, Active)

| Law/Circular | Date | Scope | Status |
|---|---|---|---|
| Luật Quản lý thuế 56/2025/QH15 | 2025 | Tax admin, e-tax, penalties | ACTIVE |
| Luật Thuế GTGT 48/2024/QH15 | 2024-07-01 | VAT 0%/5%/8%/10%, deduction/direct method | ACTIVE |
| Luật Thuế TNDN 67/2025/QH15 | 2025 | CIT 20%, incentives, transfer pricing | ACTIVE |
| Luật Thuế TNCN 109/2025/QH15 | 2025 | PIT progressive table, quarterly filing from 4/2026 | ACTIVE |
| TT 99/2025/TT-BTC | 2025 | Accounting regime (replaces TT 200, TT 133) | ACTIVE |
| TT 86/2024/TT-BTC | 2024 | Tax registration (MST) | ACTIVE |
| ND 70/2025/ND-CP | 2025 | E-invoice (hóa đơn điện tử) | ACTIVE |
| ND 164/2026/ND-CP | 2026 | Asset/income declaration | ACTIVE |
| TT 80/2021/TT-BTC | 2021 | Tax declaration procedures | PARTIAL REPEAL |
| ND 123/2020/ND-CP | 2020 | Invoice penalties | ACTIVE |

**Key 2026 Changes:**
- PIT filing switches from monthly to quarterly (from 4/2026)
- CIT finalization deadline 31/3/2027 for FY 2026
- VAT reduction 8% for certain goods/services extended
- E-invoice mandatory for all B2B/B2C (ND 70)

---

## 3. Tax Types Supported

| Tax | Code | Rate | Declaration Form | Period | Due Date |
|---|---|---|---|---|---|
| VAT - Khấu trừ | GTGT | 0/5/8/10% | 01/GTGT | Monthly/Quarterly | +20d |
| VAT - Trực tiếp | GTGT | 1-5% | 04/GTGT | Quarterly | +20d |
| CIT | TNDN | 20% | 01/TNDN (tạm tính), 03/TNDN (QToán) | Quarterly provisional + Annual finalization | +30d/Q, 31/3 |
| PIT | TNCN | Progressive 5-35% | 05/KK-TNCN (monthly), 02/KK-TNCN (quarterly from 4/2026) | Quarterly | +20d |
| PIT Finalization | QTTNCN | - | 05/QTT-TNCN | Annual | 31/3 |
| License tax | MB | Graded 0.3-3tr | - | Annual | 30/1 |
| Foreign contractor | FCT | 0.1-10% | 01/NTNN | Per payment | +10d |
| Personal income (rental) | CNCT | 5% GTGT + 5% TNCN | 01/CNKD | Per payment | +20d |
| Natural resources | TN | Variable | 01/TAI NGUYEN | Monthly | +20d |
| Import/Export | XNK | Variable | Customs | Per shipment | At border |

---

## 4. Domain Entities

### 4.1 TaxType
- id, code, name_vi, name_en, short_name
- declaration_form (e.g., "01/GTGT", "03/TNDN")
- declaration_period (monthly|quarterly|annual|per_payment)
- due_date_rule (days_after_period|fixed_date)
- rate_type (fixed|progressive|hybrid)
- status (active|inactive)
- legal_basis (law/article reference)

### 4.2 TaxDeclaration
- id, tax_type_id, form_code, period (YYYY-MM|YYYY), year
- submission_type (original|supplemental)
- status (draft|calculated|submitted|accepted|rejected|amended)
- total_revenue, total_tax, total_deduction, total_payable
- previous_period_adjustment
- late_payment_interest
- declared_at, submitted_at, accepted_at
- submission_method (etax|htkk|manual)
- gdt_reference_number

### 4.3 TaxLine
- id, declaration_id
- line_code (mapping to form field code)
- description, amount
- is_calculated (auto vs manual)
- parent_line_id

### 4.4 TaxPayment
- id, declaration_id, budget_account
- amount, payment_date, due_date
- payment_method (etax|bank|direct)
- payment_status (pending|paid|overdue|refunded)
- gdt_payment_code
- penalty_interest if overdue

### 4.5 TaxAdjustment
- id, original_declaration_id, supplemental_declaration_id
- adjustment_type (increase|decrease|correction)
- reason, detail
- original_amount, adjusted_amount, difference
- approval_status

### 4.6 TaxIncentive
- id, code, name
- tax_type, incentive_type (exemption|reduction|preferential_rate)
- condition, eligibility_check
- rate_value, valid_from, valid_to
- max_period

### 4.7 EInvoice
- id, invoice_number, invoice_series, invoice_date
- seller_tax_code, buyer_tax_code
- total_amount, vat_amount, grand_total
- status (created|signed|sent|cancelled|replaced|adjusted)
- verification_code (GDT)
- adjustment_ref_id (for ND 70 replace/adjust workflows)

---

## 5. Business Rules

### 5.1 VAT Rules
```
RULE-VAT-01: VAT period determination
  IF annual revenue > 50B VND -> monthly filing
  IF annual revenue <= 50B VND -> quarterly filing
  IF new company (< 1yr) -> can choose

RULE-VAT-02: VAT method determination  
  IF revenue > 1B VND AND proper accounting -> khấu trừ
  IF revenue <= 1B VND OR no proper accounting -> trực tiếp
  IF voluntary registration -> khấu trừ (stable 12 months)

RULE-VAT-03: Input VAT deduction eligibility
  IF invoice is valid (verified GDT) AND goods/services used for taxable activity -> DEDUCTIBLE
  IF invoice invalid/errors -> NON-DEDUCTIBLE (adjust with supplemental)
  IF goods for personal use -> NON-DEDUCTIBLE
  IF fixed assets -> FULLY DEDUCTIBLE

RULE-VAT-04: VAT rates
  Rate 0%: Export goods, international transportation, export services
  Rate 5%: Clean water, fertilizer, medical equipment, education services
  Rate 8%: Reduced rate (current policy, certain goods/services)
  Rate 10%: Standard rate (default for all other goods/services)

RULE-VAT-05: VAT refund conditions
  IF accumulated input VAT > 300M AND 12 consecutive months have credit balance -> REFUND
  IF export goods and input VAT > 5% of export revenue -> REFUND
  IF new project in investment phase -> REFUND
  ELSE carry forward to next period

RULE-VAT-06: Invoice adjustment (ND 70/2025)
  IF error discovered in same period -> cancel + reissue
  IF error discovered in different period -> adjustment invoice (tăng/giảm)
  IF buyer/seller changed price -> adjustment invoice
  IF goods returned -> credit/debit note

RULE-VAT-07: Supplemental declaration
  IF missed invoice in previous period -> file supplemental (khai bổ sung)
  IF adjustment decreases tax -> refund or offset
  IF adjustment increases tax -> pay + late payment interest
  Supplemental filing allowed for max 10 years back
```

### 5.2 CIT Rules
```
RULE-CIT-01: CIT rate
  Standard: 20%
  For oil/gas: 32-50%
  For precious minerals: 40%
  SME preferential: 15-17% (certain conditions)
  High-tech/Science: 10% (15yr)
  New investment project: exemption 4yr + 50% reduction 9yr

RULE-CIT-02: Provisional vs finalization
  Quarterly provisional (tạm tính): 01/TNDN filed within 30 days of quarter end
  Annual finalization (quyết toán): 03/TNDN filed before 31/3 of next year
  IF provisional payment < 80% of final -> penalty on shortfall

RULE-CIT-03: Non-deductible expenses
  Fines and penalties
  Provisions not meeting conditions
  Depreciation not meeting conditions (wrong method/rate)
  Interest expense exceeding 20% of EBITDA (related-party)
  Salary without contracts/not paid
  Donations to non-approved orgs
  Advertising exceeding 15% of total expenses (10% for some sectors)

RULE-CIT-04: Loss carryforward
  Maximum: 5 consecutive years from loss year
  Must file declaration even when losing
  Loss from transfer of assets/equity -> separate tracking
  M&A: loss tracking per legal successor rules

RULE-CIT-05: Transfer pricing
  Related-party transactions must prepare TP documentation
  Master file (> 6000B VND revenue), Local file (> 600B VND revenue)
  CbCR (> 18000B VND consolidated)
  Arm's length principle mandatory
  Filing deadline: same as CIT finalization
```

### 5.3 PIT Rules
```
RULE-PIT-01: Personal income categories
  Employment income (tiền lương, tiền công) -> progressive table
  Business income -> progressive table or 10% flat
  Capital investment -> 5%
  Real estate transfer -> 2%
  Royalties -> 5%
  Franchise -> 5%
  Prizes/winnings -> 10% (>10M VND)
  Inheritance/gift -> 10% (>10M VND)

RULE-PIT-02: Progressive tax table (from 4/2026)
  To 6M    -> 5%
  6-12M    -> 10%
  12-18M   -> 15%
  18-24M   -> 20%
  24-30M   -> 25%
  30-42M   -> 30%
  42M+     -> 35%

RULE-PIT-03: Family deductions (2026)
  Taxpayer: 11M/month
  Dependent: 4.4M/month/person
  Social insurance, health insurance, unemployment insurance -> deductible
  Charitable contributions -> deductible (limited)

RULE-PIT-04: PIT withholding
  Employer withholds at source (via payroll system)
  File 05/KK-TNCN monthly (switch to quarterly per 56/2025/QH15 from 4/2026)
  Year-end: issue PIT certificate (chứng từ khấu trừ)
  Annual finalization: 05/QTT-TNCN

RULE-PIT-05: PIT finalization
  Employee can authorize employer (ủy quyền quyết toán)
  IF employer withholds correctly -> employer finalizes for all employees
  IF multiple income sources -> employee self-finalizes
  Deadline: 31/3 of following year
```

### 5.4 General Tax Admin Rules
```
RULE-TAXADMIN-01: Tax code (MST) format
  10 digits for enterprise
  13 digits for individuals (10 + 3 extension)
  10 digits for foreign contractor
  Pattern: ^[0-9]{10}(-[0-9]{3})?$

RULE-TAXADMIN-02: Late payment interest
  Rate: 0.03%/day
  Grace period: none (interest from day after due date)
  Compounding: simple interest

RULE-TAXADMIN-03: Extending deadline
  No extension for tax filing (except force majeure)
  Payment extension possible in case of natural disaster, fire, accident
  Max extension: 2 years

RULE-TAXADMIN-04: Penalty for late filing
  < 5 days: warning (if no aggravating)
  1-30 days: 2-5M VND
  31-60 days: 5-8M VND
  61-90 days: 8-15M VND
  90+ days: 15-25M VND + enforced assessment

RULE-TAXADMIN-05: Statute of limitations
  Tax assessment: 10 years for fraud, 5 years for errors, 2 years for procedural
  Refund claim: 5 years from end of period
  Tax debt collection: 10 years
```

---

## 6. Process Flows

### 6.1 VAT Declaration Process
```
[Start] -> Determine period (monthly/quarterly)
  -> Collect valid input invoices (verified through e-invoice system)
  -> Collect output invoices (sales)
  -> Calculate:
    - Total output VAT
    - Deductible input VAT
    - VAT payable = output - input
    - OR: Direct method: Revenue * rate
  -> Fill form 01/GTGT or 04/GTGT
  -> Validate:
    - All invoice data complete
    - No duplicate entries
    - Input/output reconciliation
  -> Submit to GDT via e-tax portal
  -> Receive confirmation
  -> Pay tax (if payable)
  -> If input > output -> carry forward OR apply for refund
[End]
```

### 6.2 CIT Finalization Process
```
[Start] -> Prepare P&L (Báo cáo KQKD)
  -> Adjust accounting profit -> taxable income:
    1. ADD back non-deductible expenses (per RULE-CIT-03)
    2. ADD income from non-taxable sources
    3. SUBTRACT incentives/exemptions
    4. SUBTRACT loss carryforward (max 5yr, per RULE-CIT-04)
  -> Calculate CIT = Taxable income * 20%
  -> SUBTRACT provisional payments already made (4 quarters)
  -> Determine additional payable or refund
  -> Fill form 03/TNDN + phụ lục (PL chuyển lỗ, ưu đãi, etc.)
  -> Fill TP documentation if applicable
  -> Submit + pay by 31/3
[End]
```

### 6.3 PIT Monthly/Quarterly Process
```
[Start] -> Calculate gross salary for period
  -> Subtract mandatory insurance (SI+HI+UI):
    - SI: 8% (employee)
    - HI: 1.5% (employee)
    - UI: 1% (employee)
  -> Subtract family deduction (self 11M + dependent 4.4M each)
  -> Apply progressive tax table
  -> Subtract tax already withheld in year
  -> Generate PIT withholding report
  -> File 05/KK-TNCN (monthly) or 02/KK-TNCN (quarterly from 4/2026)
  -> Pay withholding tax
  -> Issue PIT certificate for employees
[End]
```

### 6.4 E-Invoice Workflow (ND 70)
```
[Start] -> Create invoice from sales transaction
  -> Validate mandatory fields:
    - Seller/Buyer: MST, name, address
    - Goods: description, unit, quantity, unit price
    - Financial: subtotal, discount, VAT rate, VAT amount, total
  -> Digital sign (USB token or remote signing service)
  -> Send to buyer (email/portal)
  -> Transmit to GDT for verification (within 1 day for CQ-CQ, instant for HDDT)
  -> Receive verification code from GDT
  -> IF buyer rejects -> handle disputes
  -> IF error discovered -> use adjust/replace workflow per ND 70
     - sa thế: adjust invoice (tăng/giảm)
     - thay thế: replacement invoice (wrong buyer/amount)
     - hủy: cancel (with GDT approval for already transmitted)
[End]
```

---

## 7. Use Cases

### UC-01: Create Tax Declaration
**Actor:** Tax Accountant  
**Precondition:** Period data complete, invoices reconciled  
**Happy Path:**
1. User selects tax type (GTGT/TNDN/TNCN)
2. User selects period (month/quarter/year)
3. System auto-calculates from GL data
4. User reviews calculated figures
5. User enters manual adjustments (if any)
6. System validates against business rules
7. User submits declaration to GDT
8. System stores GDT confirmation + reference number

**Alternative UC-01-A: Supplemental Declaration**
1. User selects "khai bổ sung"
2. User selects original declaration period
3. System shows original values
4. User enters corrected values
5. System calculates difference
6. If additional tax: auto-calc penalty + interest
7. Submit supplemental

**Exception UC-01-E1: Validation fails**
- Highlight error fields
- Show rule violated
- Block submission

### UC-02: Auto-Calculate VAT
**Actor:** System (scheduled)  
**Precondition:** Invoices posted for period  
**Happy Path:**
1. System collects all input invoices (verified, eligible)
2. System collects all output invoices
3. Calculates input VAT by rate (0/5/8/10%)
4. Calculates output VAT by rate
5. Determines deductible vs non-deductible input
6. VAT payable = output - deductible input
7. Generates draft 01/GTGT
8. Notifies tax accountant for review

### UC-03: E-Invoice Lifecycle Management
**Actor:** Accountant/System  
**Happy Path:**
1. Sales order -> generate e-invoice draft
2. Fill invoice data (auto from order)
3. Digital signing
4. Send to buyer + transmit GDT
5. Store GDT verification code
6. Archive in system

**Alternative UC-03-A: Adjustment Invoice**
1. User selects original invoice
2. Select type: tăng (increase) / giảm (decrease)
3. Enter difference values
4. System generates adjustment invoice
5. Both original + adjustment linked
6. Transmit to GDT

**Alternative UC-03-B: Replacement Invoice**
1. User selects original invoice
2. User enters corrected data
3. System marks original as "replaced"
4. System generates replacement invoice
5. Both invoices transmitted to GDT

### UC-04: Tax Payment & Tracking
**Actor:** Accountant  
**Happy Path:**
1. System calculates tax payable from declaration
2. User initiates payment via e-tax portal
3. System records payment with GDT confirmation
4. Updates payment status
5. Generates tax payment receipt
6. Tracks against budget account at Kho bạc (State Treasury)

**Alternative UC-04-A: Overdue Payment**
1. System detects payment deadline approaching (N-3)
2. Sends reminder notification
3. If overdue: auto-calc late interest (0.03%/day)
4. Generates penalty report

### UC-05: Tax Incentive Management
**Actor:** Tax Accountant  
**Happy Path:**
1. User selects eligible tax type
2. User selects incentive type
3. System checks eligibility conditions
4. User attaches supporting documents
5. System applies reduced rate/exemption
6. Reports incentive usage in declaration

### UC-06: Transfer Pricing Documentation
**Actor:** Tax Manager  
**Happy Path:**
1. System identifies related-party transactions
2. User confirms transaction types
3. System calculates arm's length range
4. User selects TP method (CUP/RP+/CPM/TNMM/PSM)
5. System generates TP report template
6. Attaches to CIT finalization package

---

## 8. Data Flow

```
[Tax Sources] -> [Calculation Engine] -> [Declaration Creator] -> [GDT Integration]
     |                    |                       |                       |
  GL Accounts         Business Rules          Form Templates         e-Tax API
  E-Invoices          Tax Rates               Validations             HTKK Export
  Payroll Data        Incentives              PDF/XML Generation      Direct Submit
  Import Data         Exchange Rates          E-Signing               Receipt Handler

  [Payment Gateway] <-> [Tax Tracking] <-> [Reporting/BI] <-> [Audit Log]
        |                    |                     |
    e-Tax                Debt/Refund           Tax Reports
    Bank Integration     Calendar/Due Dates    Forecasting
    Treasury             Payment History       Compliance
```

### 8.1 Integration Points

| System | Direction | Protocol | Data |
|---|---|---|---|
| GL (COA) | IN | SQLAlchemy | All account balances, transactions |
| E-Invoice | IN/OUT | REST/API | Invoice data, verification |
| GDT e-Tax | OUT | XML/SOAP | Declarations, payments |
| GDT e-Invoice | OUT | REST/API | Inv transmit, verification |
| HTKK | OUT | XML/CSV | Offline declaration file |
| Payroll | IN | DB | Salary, PIT calc |
| Inventory | IN | DB | Import/export data |
| Treasury (KB) | IN | Bank file | Payment receipts |
| State Budget | OUT | Report | Tax by budget account |

---

## 9. Reports

| Report ID | Name | Frequency | Format |
|---|---|---|---|
| RPT-TAX-001 | Bảng kê hóa đơn đầu vào | Monthly | Excel/PDF |
| RPT-TAX-002 | Bảng kê hóa đơn đầu ra | Monthly | Excel/PDF |
| RPT-TAX-003 | Bảng kê thuế GTGT | Period | Excel/PDF |
| RPT-TAX-004 | Quyết toán thuế TNDN | Annual | XML/PDF |
| RPT-TAX-005 | Quyết toán thuế TNCN | Annual | XML/PDF |
| RPT-TAX-006 | Tình hình thực hiện nghĩa vụ thuế | Monthly | Dashboard |
| RPT-TAX-007 | Sổ chi tiết thuế GTGT | Period | Excel/PDF |
| RPT-TAX-008 | Báo cáo công nợ thuế | Monthly | Dashboard |
| RPT-TAX-009 | Sổ theo dõi thuế TNCN | Monthly | Excel/PDF |
| RPT-TAX-010 | Tờ khai bổ sung (lũy kế) | On-demand | Dashboard |
| RPT-TAX-011 | Dự báo thuế phải nộp | Monthly | Dashboard |
| RPT-TAX-012 | Kiểm tra đối chiếu hóa đơn | Monthly | Dashboard |

---

## 10. Domain Implementation Plan

### Phase A: Core Domain (Week 1-2)
```
1. TaxType entity + enums           -> domain/__init__.py
2. TaxDeclaration entity             -> domain/__init__.py  
3. TaxLine entity                    -> domain/__init__.py
4. TaxPayment entity                 -> domain/__init__.py
5. TaxAdjustment entity              -> domain/__init__.py
6. TaxIncentive entity               -> domain/__init__.py
7. EInvoice entity                   -> domain/__init__.py
8. Business Rules Engine (stateless) -> use_cases/
```

### Phase B: Use Cases (Week 2-3)
```
1. TaxCalculationUseCase           -> use_cases/tax_calc_uc.py
2. TaxDeclarationUseCase           -> use_cases/tax_declare_uc.py  
3. TaxPaymentUseCase               -> use_cases/tax_payment_uc.py
4. EInvoiceUseCase                 -> use_cases/einvoice_uc.py
5. TaxAdjustmentUseCase            -> use_cases/tax_adjust_uc.py
6. TransferPricingUseCase          -> use_cases/tp_uc.py
```

### Phase C: Infrastructure (Week 3-4)
```
1. DB models (SQLAlchemy)          -> infrastructure/models/tax_models.py
2. Repository layer                -> infrastructure/repositories/tax_repo.py
3. GDT e-Tax integration           -> infrastructure/gdt_client.py
4. E-Invoice signing               -> infrastructure/signing_service.py
```

### Phase D: Presentation (Week 4-5)
```
1. REST API routes                 -> presentation/tax_routes.py
2. Reports (Excel/PDF)             -> services/tax_reports.py
```

---

## 11. Data Dictionary (Key Fields)

### TaxDeclaration Form Codes
| Form | Tax Type | Frequency | GDT Form ID |
|---|---|---|---|
| 01/GTGT | VAT deduction | M/Q | f01_gtgt_khau_tru.xml |
| 04/GTGT | VAT direct | Q | f04_gtgt_truc_tiep.xml |
| 01/TNDN | CIT provisional | Q | f01_tndn_tam_tinh.xml |
| 03/TNDN | CIT finalization | A | f03_tndn_quyet_toan.xml |
| 02/KK-TNCN | PIT monthly | M (->Q from 4/2026) | f02_kk_tncn.xml |
| 05/QTT-TNCN | PIT finalization | A | f05_qtt_tncn.xml |
| 01/NTNN | FCT | Per pymt | f01_nha_thau_nuoc_ngoai.xml |
| 01/CNKD | Business household | A | f01_ca_nhan_kinh_doanh.xml |

### State Budget Account Codes (Tài khoản Kho bạc)
| Tax | Budget Account |
|---|---|
| VAT | 1701 |
| CIT | 1702 |
| PIT | 1703 |
| License tax | 1704 |
| FCT | 1705 |
| Natural resources | 1706 |
| Environmental | 1707 |

---

## 12. Non-Functional Requirements

1. **Performance:** Tax calc for 10K invoices < 30s
2. **Security:** All GDT credentials encrypted at rest, audit log all submissions
3. **Compliance:** Auto-detect legal changes via config, no hardcoded rates
4. **Audit:** Every action logged: who, what, when, to GDT
5. **Multi-company:** Support multiple tax codes per deployment
6. **Multi-period:** Retroactive adjustments always traceable
7. **Integration:** Bi-directional sync with GL, no data loss

---

## 13. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| GDT e-Tax API changes | High | Medium | Abstraction layer, config-driven |
| Rate changes mid-year | High | High | Config table, not hardcoded |
| Invoice data incorrect | High | Medium | Validation + reconciliation |
| Late payment penalties | Medium | Medium | Auto-due-date alerts |
| TP audit | High | Low | Auto TP documentation |
| Regulatory penalty | High | Low | Built-in rule engineering |

---

*Document prepared by: BA Lead (20yr) + Chief Accountant (20yr)*
*Sources: [gdt.gov.vn], [mof.gov.vn], [ketoanthienung.net], [tapchiketoankiemtoan.vn], [ifrs.org], [vacpa.org.vn]*
*Legal basis: Luật 56/2025/QH15, Luật 48/2024/QH15, Luật 67/2025/QH15, Luật 109/2025/QH15, ND 70/2025, TT 99/2025*
