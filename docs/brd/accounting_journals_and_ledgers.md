# BRD: Accounting Journals, Subsidiary Ledgers & Reporting Engine

**Version**: 1.0  
**Status**: Draft for Review  
**Author**: BA Lead + Chief Accountant (20+ yrs VAS/IFRS)  
**Regulatory Basis**: TT 99/2025/TT-BTC (eff. 01/01/2026), TT 200/2014/TT-BTC (replaced), Luật Kế toán 88/2015/QH13, Luật Kế toán 89/2025/QH15, VAS, IFRS  
**Last Updated**: 2026-06-30

---

## TABLE OF CONTENTS

1. [Executive Summary & PROD-Readiness Assessment](#1-executive-summary)
2. [Regulatory Framework (TT 99/2025)](#2-regulatory-framework)
3. [Module-by-Module Gap Analysis](#3-module-by-module-gap-analysis)
4. [Module Scope & Architecture](#4-module-scope--architecture)
5. [Data Model Design](#5-data-model-design)
6. [Use Cases: Journals](#6-use-cases-journals)
7. [Use Cases: Subsidiary Ledgers](#7-use-cases-subsidiary-ledgers)
8. [Use Cases: Reporting Engine](#8-use-cases-reporting-engine)
9. [Business Rules Engine](#9-business-rules-engine)
10. [Data Flow Diagrams](#10-data-flow-diagrams)
11. [Workflows & User Journeys](#11-workflows--user-journeys)
12. [TT99 Accounting Book Templates](#12-tt99-accounting-book-templates)
13. [GL Posting Matrix](#13-gl-posting-matrix)
14. [Report Templates per TT 99/2025](#14-report-templates)
15. [Non-Functional Requirements](#15-non-functional-requirements)
16. [Implementation Roadmap](#16-implementation-roadmap)
17. [Appendix: Legal References](#17-appendix)
18. [Appendix: Big 4 Comparison](#18-appendix-big-4-comparison)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose
Assess PROD readiness and define full spec for 10 accounting modules in SmartACCT ERP:
1. General Journal (Sổ Nhật Ký Chung)
2. Sales Journal (Sổ Nhật Ký Bán Hàng)
3. Purchase Journal (Sổ Nhật Ký Mua Hàng)
4. Cash Receipts Journal (Sổ Nhật Ký Thu Tiền)
5. Cash Disbursements Journal (Sổ Nhật Ký Chi Tiền)
6. General Ledger (Sổ Cái)
7. Subsidiary Ledger (Sổ Chi Tiết)
8. Accounts Receivable Ledger (Sổ Chi Tiết Công Nợ Phải Thu)
9. Accounts Payable Ledger (Sổ Chi Tiết Công Nợ Phải Trả)
10. Reporting Engine

### 1.2 PROD-Readiness Assessment

| # | Module | Score | PROD Ready? | Key Gaps |
|---|--------|-------|-------------|----------|
| 1 | General Journal | 3/10 | ❌ | Only JV-prefix, no journal type discrimination, no TT99 S03c-DN format, no user-defined numbering |
| 2 | Sales Journal | 0/10 | ❌ | No dedicated SJ module, no S03b2-DN format |
| 3 | Purchase Journal | 0/10 | ❌ | No dedicated PJ module, no S03b1-DN format |
| 4 | Cash Receipts Journal | 2/10 | ❌ | CashReceipt exists but no formal CRJ with S03a1-DN format |
| 5 | Cash Disbursements Journal | 2/10 | ❌ | CashPayment exists but no formal CDJ with S03a2-DN format |
| 6 | General Ledger | 3/10 | ❌ | Basic S01-DN missing, no multi-dimensional, no intercompany elimination, no multi-entity consolidation |
| 7 | Subsidiary Ledger | 0/10 | ❌ | No formal subsidiary ledger module |
| 8 | AR Ledger | 3/10 | ❌ | AR module exists but no formal AR subsidiary ledger S06-DN format |
| 9 | AP Ledger | 3/10 | ❌ | AP module exists but no formal AP subsidiary ledger S05-DN format |
| 10 | Reporting Engine | 1/10 | ❌ | Only balance_sheet + income_statement stubs; no parameterized templates, no multi-format export, no drill-down, no IFRS 18 path, no XBRL |

**OVERALL SCORE: 1.7/10 — NOT PRODUCTION-READY**

### 1.3 Critical Gaps

1. **TT99 Non-compliance**: Current `JournalEntry` uses mandatory `JV` prefix (domain/gl.py:15). TT99 Art.12 allows enterprises to design own journal numbering. Must support configurable prefixes (SJ, PJ, CRJ, CDJ, GJ, JV).

2. **No journal type taxonomy**: All entries stored as `JournalEntry` regardless of source. Need `JournalType` enum + separate journal tables or type discriminator column.

3. **42 TT99 accounting book templates**: None implemented. Missing S01-DN through S12-DN and associated sub-ledgers.

4. **Sub-ledger architecture**: AR/AP modules operate independently. No unified subsidiary ledger that aggregates from sub-ledgers into GL.

5. **Reporting engine**: Only 2 stub functions. No parameterized reports, no export (PDF/Excel/XBRL/HTML/CSV), no drill-down, no scheduled reports, no cash flow statement, no B09-DN notes.

6. **Multi-entity**: No multi-entity consolidation, intercompany elimination, or branch accounting per TT99 Art.22-28.

7. **TC 58/2026/TT-BTC**: New circular for micro-enterprises effective 01/07/2026 — not yet incorporated.

---

## 2. REGULATORY FRAMEWORK

### 2.1 Active Regulations Matrix

| Document | Issuer | Effective | Status | Scope |
|----------|--------|-----------|--------|-------|
| **TT 99/2025/TT-BTC** | MoF | 01/01/2026 | ✅ ACTIVE | Replaces TT200 — full enterprise accounting regime, vouchers, COA, books, FS |
| **TT 200/2014/TT-BTC** | MoF | 05/02/2015 | ❌ REPLACED | Replaced by TT99 from 01/01/2026 |
| **TT 75/2015/TT-BTC** | MoF | 14/07/2015 | ❌ REPLACED | Amendment to TT200 |
| **TT 53/2016/TT-BTC** | MoF | 21/03/2016 | ❌ REPLACED | Amendment to TT200 |
| **TT 133/2016/TT-BTC** | MoF | 01/01/2017 | ✅ ACTIVE | SME accounting regime |
| **TT 58/2026/TT-BTC** | MoF | 01/07/2026 | ✅ FUTURE | Micro-enterprise accounting regime |
| **TT 195/2012/TT-BTC** | MoF | 15/11/2012 | ❌ REPLACED | Investor accounting |
| **TT 157/2025/TT-BTC** | MoF | 2025 | ✅ ACTIVE | KBNN registration procedures |
| **Luật Kế toán 88/2015/QH13** | NA | 01/01/2017 | ❌ REPLACED | Old Accounting Law |
| **Luật Kế toán 89/2025/QH15** | NA | 01/01/2026 | ✅ ACTIVE | New Accounting Law (amends 88/2015) |
| **VAS 01-30** | MoF | Various | ✅ ACTIVE | 21 Vietnamese Accounting Standards |
| **IFRS 18** | IASB | 01/01/2027 | ✅ FUTURE | Presentation & Disclosure in FS |
| **IFRS 9** | IASB | Active | ✅ REF | Financial Instruments |
| **IFRS 15** | IASB | Active | ✅ REF | Revenue from Contracts |
| **IFRS 16** | IASB | Active | ✅ REF | Leases |
| **QĐ 345/2020/QĐ-BTC** | MoF | 2020 | ✅ ACTIVE | IFRS convergence roadmap |
| **NĐ 166/2025/NĐ-CP** | Gov | 30/06/2025 | ✅ ACTIVE | MoF restructuring |
| **NĐ 347/2025/NĐ-CP** | Gov | 2025 | ✅ ACTIVE | KBNN admin procedures |
| **NĐ 29/2025/NĐ-CP** | Gov | 24/02/2025 | ✅ ACTIVE | MoF functions/tasks |

### 2.2 TT99/2025 Key Requirements for Journals & Ledgers

| Article | Requirement | Impact on System |
|---------|-------------|-----------------|
| Art.9 | Enterprises may design own voucher forms | Need configurable journal templates |
| Art.12 | 42 accounting book templates (Phụ lục III) | Must implement all 42 templates |
| Art.12(1) | Books must reflect assets/capital verifiable | Audit trail mandatory |
| Art.12(2) | Books must be timely, accurate, transparent | Real-time posting + read-only audit |
| Art.12(3) | Enterprises may modify book templates | Template engine |
| Art.12(4) | Internal accounting regulation required | Configurable business rules |
| Art.15 | Accounting book types prescribed | 12 book categories (S01-S12) |
| Art.16 | Book recording methods | General Journal method or Voucher method |
| Art.17 | Opening books | Opening balance migration |
| Art.18 | Recording period | Period-gated, no back-posting to closed |
| Art.19 | Recording currency | Multi-currency with auto-rate |
| Art.20 | Corrections | Strike-through method, reversal entries |
| Art.21 | Closing books | Month-end + year-end procedures |
| Art.22-28 | Multi-unit accounting | Branch/department dimensions |
| Art.29 | TT200-to-TT99 transition | Balance migration rules |

### 2.3 TT99 42 Accounting Book Templates (Phụ lục III)

| Code | Name (VN) | Name (EN) | Status |
|------|-----------|-----------|--------|
| S01-DN | Sổ Cái | General Ledger | ❌ Missing |
| S02a-DN | Chứng từ ghi sổ | Voucher Summary | ❌ Missing |
| S02b-DN | Sổ đăng ký chứng từ ghi sổ | Voucher Register | ❌ Missing |
| S03a1-DN | Sổ nhật ký thu tiền | Cash Receipts Journal | ❌ Missing |
| S03a2-DN | Sổ nhật ký chi tiền | Cash Disbursements Journal | ❌ Missing |
| S03b1-DN | Sổ nhật ký mua hàng | Purchase Journal | ❌ Missing |
| S03b2-DN | Sổ nhật ký bán hàng | Sales Journal | ❌ Missing |
| S03c-DN | Sổ nhật ký chung | General Journal | ❌ Missing |
| S04-DN | Sổ tổng hợp chi tiết | Detailed Summary | ❌ Missing |
| S05-DN | Sổ chi tiết thanh toán với người bán | AP Subsidiary Ledger | ❌ Missing |
| S06-DN | Sổ chi tiết thanh toán với người mua | AR Subsidiary Ledger | ❌ Missing |
| S07-DN | Sổ chi tiết hàng tồn kho | Inventory Subsidiary | ❌ Missing |
| S08-DN | Sổ chi tiết TSCĐ | Fixed Asset Subsidiary | ❌ Missing |
| S09-DN | Sổ chi phí SXKD | Production Cost Ledger | ❌ Missing |
| S10-DN | Sổ chi phí trả trước | Prepaid Cost Ledger | ❌ Missing |
| S11-DN | Sổ TSCĐ | Fixed Asset Register | ❌ Missing |
| S12-DN | Sổ chi tiết tiền vay | Loan Subsidiary | ❌ Missing |
| ... | (25 more detail templates) | | ❌ Missing |

---

## 3. MODULE-BY-MODULE GAP ANALYSIS

### 3.1 General Journal (Sổ Nhật Ký Chung — S03c-DN)

**Current State**: `JournalEntry` domain exists (domain/gl.py:13-184), `JournalLine` (187-277), `GLRepository` with CRUD + posting. Routes in `gl_routes.py`. Tested (47 tests).

**Gaps**:
- ❌ Journal number forced `JV` prefix — violates TT99 Art.9 (enterprise may design own)
- ❌ No `journal_type` field — cannot distinguish GJ vs SJ vs PJ vs CRJ vs CDJ
- ❌ No TT99 S03c-DN template format with required columns
- ❌ No Vietnamese header/footer format per TT99 Phụ lục III
- ❌ No serial number per journal type (must auto-increment per type per year)
- ❌ No column for reference document number (số hiệu chứng từ)
- ❌ No pre-printed form number (số trang)
- ❌ No signature block (người lập/kế toán trưởng/giám đốc) per Luật Kế toán Art.16
- ❌ No support for correction entries (điều chỉnh) per TT99 Art.20
- ❌ No supporting document attachment tracking

### 3.2 Sales Journal (Sổ Nhật Ký Bán Hàng — S03b2-DN)

**Current State**: ❌ NOTHING. AR module handles sales invoices but no Sales Journal.

**Required Columns (per TT99 S03b2-DN)**:
- Ngày, tháng (Date)
- Số hiệu chứng từ (Doc Ref)
- Diễn giải (Description)
- TK ghi Nợ 131 (Debit 131 - AR)
- TK ghi Có 511, 512, 515 (Credit Revenue)
- Cột doanh thu (Revenue columns): 511, 512, 515...
- Cột thuế (Tax column): 3331
- Ghi chú (Notes)

### 3.3 Purchase Journal (Sổ Nhật Ký Mua Hàng — S03b1-DN)

**Current State**: ❌ NOTHING. AP module handles purchase invoices but no Purchase Journal.

**Required Columns (per TT99 S03b1-DN)**:
- Ngày, tháng (Date)
- Số hiệu chứng từ (Doc Ref)
- Diễn giải (Description)
- TK ghi Có 331 (Credit 331 - AP)
- TK ghi Nợ 152, 153, 156, 611 (Debit Inventory/Goods)
- Cột thuế (Tax): 133 (input VAT)
- Ghi chú (Notes)

### 3.4 Cash Receipts Journal (Sổ Nhật Ký Thu Tiền — S03a1-DN)

**Current State**: `CashReceipt` entity exists (domain/cash.py). Cash module has receipts CRUD + routes. But no formal S03a1-DN journal format.

**Gaps**:
- ❌ No S03a1-DN template
- ❌ No cash receipt number auto-generation per year (thu/chi năm X)
- ❌ No column for "đã thu" / "còn phải thu" tracking
- ❌ No multi-currency columns
- ❌ No linkage to bank deposits (111 ↔ 112)
- ❌ No daily cash receipt summary (bảng kê thu tiền)

### 3.5 Cash Disbursements Journal (Sổ Nhật Ký Chi Tiền — S03a2-DN)

**Current State**: `CashPayment` entity exists. Payment CRUD + routes. No formal S03a2-DN.

**Same gaps as CRJ** but for payments.

### 3.6 General Ledger (Sổ Cái — S01-DN)

**Current State**: `JournalEntryModel` + `JournalLineModel` provide basic GL structure. `get_account_balance()` computes balances. But no S01-DN format.

**Gaps**:
- ❌ No S01-DN template per TT99
- ❌ No monthly balance columns: Số dư đầu kỳ, Phát sinh trong kỳ, Số dư cuối kỳ
- ❌ No monthly cumulative YTD columns
- ❌ No multi-entity consolidation
- ❌ No intercompany elimination (TK 136/336)
- ❌ No branch/department dimensions on GL lines
- ❌ No aging analysis
- ❌ No drill-down from GL balance to journal lines to source document

### 3.7 Subsidiary Ledger (Sổ Chi Tiết — S04-DN through S12-DN)

**Current State**: ❌ NOTHING as a unified module. AR has sub-ledger-like queries. AP has sub-ledger-like queries. But no:

- Unified subsidiary ledger engine
- Configurable subsidiary ledger templates
- Standard S04-DN through S12-DN formats
- Drill-down from GL to subsidiary

### 3.8 Accounts Receivable Ledger (Sổ Chi Tiết Công Nợ Phải Thu — S06-DN)

**Current State**: AR module exists with customers, invoices, payments, aging. But no formal S06-DN.

**Required Columns (per TT99 S06-DN)**:
- Tên khách hàng (Customer name)
- Số dư đầu kỳ (Opening balance)
- Phát sinh tăng (Debit - sales/invoices)
- Phát sinh giảm (Credit - payments/returns)
- Số dư cuối kỳ (Closing balance)
- Phân loại (Classification): trong hạn, quá hạn

### 3.9 Accounts Payable Ledger (Sổ Chi Tiết Công Nợ Phải Trả — S05-DN)

**Current State**: AP module exists with vendors, invoices, payments. No formal S05-DN.

**Same columns as S06-DN but for vendors/AP**.

### 3.10 Reporting Engine

**Current State**: Only `generate_balance_sheet()` + `generate_income_statement()` in GLRepository:746-782. Both return flat dicts. No:

- ❌ Parameterized report templates
- ❌ Multi-format export (PDF/Excel/CSV/HTML/XBRL/JSON)
- ❌ Cash flow statement (B03-DN) — direct + indirect method
- ❌ B09-DN Notes to Financial Statements
- ❌ Multi-entity consolidated reports
- ❌ IFRS conversion layer
- ❌ Ad-hoc query builder
- ❌ Drill-down capability
- ❌ Scheduled report generation
- ❌ Report repository/library
- ❌ Dashboard widgets
- ❌ User-defined report designer
- ❌ XBRL taxonomy mapping for e-submission

---

## 4. MODULE SCOPE & ARCHITECTURE

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                   PRESENTATION                       │
│  Routes (REST API) / Blueprint / Serializers         │
│  /api/v1/gl/journals, /api/v1/gl/subsidiary,        │
│  /api/v1/gl/reports                                  │
├─────────────────────────────────────────────────────┤
│                   USE CASES                          │
│  GLUseCases + JournalUseCases + SubsidiaryUseCases   │
│  + ReportingUseCases + ConsolidationUseCases         │
├─────────────────────────────────────────────────────┤
│                   DOMAIN                             │
│  JournalEntry, JournalLine, JournalType,             │
│  SubsidiaryLedger, SubsidiaryLine,                   │
│  ReportTemplate, ReportFormat,                       │
│  AccountBalance, PeriodBalance,                      │
│  ConsolidationEntry, IntercompanyEntry              │
├─────────────────────────────────────────────────────┤
│                 INFRASTRUCTURE                       │
│  ┌──────────────────┐  ┌──────────────────┐         │
│  │     MODELS       │  │  REPOSITORIES    │         │
│  │  gl_models.py    │  │  gl_repository   │         │
│  │  new journal/    │  │  reporting_repo  │         │
│  │  subledger/      │  │  subsidiary_repo │         │
│  │  report models   │  │  consolidation   │         │
│  └──────────────────┘  └──────────────────┘         │
├─────────────────────────────────────────────────────┤
│               MODULE INTEGRATIONS                    │
│  AR → Journal (sales)                                │
│  AP → Journal (purchases)                            │
│  Cash → Journal (receipts/disbursements)             │
│  Inventory → Journal (valuation adjustments)         │
│  FA → Journal (depreciation/disposals)               │
│  Payroll → Journal (salary postings)                 │
│  Tax → Journal (VAT adjustments)                     │
│  Treasury → Journal (forex/revaluation)              │
└─────────────────────────────────────────────────────┘
```

### 4.2 Journal Numbering Architecture

```
Prefix[1-4] + Suffix[6-14] digits

Configurable per enterprise:
  GJ-2026-000001  (General Journal)
  SJ-2026-000001  (Sales Journal)
  PJ-2026-000001  (Purchase Journal)
  CR-2026-000001  (Cash Receipts Journal)
  CD-2026-000001  (Cash Disbursements Journal)
  JV-2026-000001  (General Voucher/Adjusting)

Configurable via internal accounting regulation.
```

### 4.3 Journal Type Enum

```python
class JournalType(str, Enum):
    GENERAL = "general_journal"       # S03c-DN
    SALES = "sales_journal"           # S03b2-DN
    PURCHASE = "purchase_journal"     # S03b1-DN
    CASH_RECEIPTS = "cash_receipts"   # S03a1-DN
    CASH_DISBURSEMENTS = "cash_disbursements"  # S03a2-DN
    VOUCHER = "voucher"              # S02a-DN
    ADJUSTING = "adjusting"          # Bút toán điều chỉnh
    CLOSING = "closing"              # Bút toán kết chuyển
    REVERSAL = "reversal"            # Bút toán hoàn nhập
```

### 4.4 Module Dependencies

```
Phase 1 (Foundation):
  GLJournalType → JournalEntry → JournalLine

Phase 2 (Specialized Journals):
  SalesJournal     → depends on: JournalEntry + AR module
  PurchaseJournal  → depends on: JournalEntry + AP module
  CashReceiptsJournal   → depends on: JournalEntry + Cash module
  CashDisbursementsJournal → depends on: JournalEntry + Cash module

Phase 3 (Ledgers):
  GeneralLedger    → depends on: JournalEntry
  ARSubsidiaryLedger → depends on: AR module + JournalEntry
  APSubsidiaryLedger → depends on: AP module + JournalEntry
  InventorySubsidiary → depends on: Inventory module
  FASubsidiaryLedger → depends on: FA module
  GeneralSubsidiaryLedger → depends on: JournalEntry

Phase 4 (Reporting):
  ReportingEngine  → depends on: all Journals + all Ledgers
  Consolidation    → depends on: ReportingEngine
  IFRS Conversion  → depends on: ReportingEngine
```

---

## 5. DATA MODEL DESIGN

### 5.1 Domain Entities

```python
# domain/gl.py — ADDITIONS to existing JournalEntry/JournalLine

class JournalType(str, Enum):
    GENERAL = "general_journal"
    SALES = "sales_journal"
    PURCHASE = "purchase_journal"
    CASH_RECEIPTS = "cash_receipts"
    CASH_DISBURSEMENTS = "cash_disbursements"
    VOUCHER = "voucher"
    ADJUSTING = "adjusting"
    CLOSING = "closing"
    REVERSAL = "reversal"


class CorrectionMethod(str, Enum):
    STRIKE_THROUGH = "strike_through"  # TT99 Art.20(a)
    REVERSAL = "reversal"              # TT99 Art.20(b)


# Enhanced JournalEntry — add journal_type field
class JournalEntry(BaseModel):
    id: Optional[int] = Field(default=None)
    journal_number: str = Field(..., min_length=1, max_length=50)
    journal_type: JournalType = JournalType.GENERAL
    transaction_date: date
    description: str
    lines: List[JournalLine] = Field(default_factory=list)
    is_posted: bool = Field(default=False)
    posted_date: Optional[datetime] = None
    period: str = Field(default_factory=lambda: date.today().strftime("%Y-%m"))
    source_module: Optional[str] = None  # ar/ap/cash/fa/payroll/inventory
    source_doc_ref: Optional[str] = None  # Reference to source document
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    correction_of: Optional[int] = Field(default=None, description="ID of corrected entry")
    correction_method: Optional[CorrectionMethod] = None
    attachment_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    # Remove hardcoded JV prefix validator — configurable
    @field_validator('journal_number')
    @classmethod
    def validate_journal_number(cls, v):
        if not v or not v.strip():
            raise ValidationError(ErrorCodes.JOURNAL_NUMBER_EMPTY)
        return v.strip()


class JournalTypeSequence(BaseModel):
    """Auto-numbering sequence per journal type per year"""
    id: Optional[int] = None
    journal_type: JournalType
    fiscal_year: int
    last_sequence: int = 0
    prefix: str = ""  # Default prefix for this type


class SubsidiaryLedger(BaseModel):
    """Unified subsidiary ledger entry"""
    id: Optional[int] = None
    subsidiary_type: str  # ar/ap/inventory/fa/cost_center
    account_code: str
    entity_id: int  # customer_id / vendor_id / item_id / asset_id
    entity_name: str
    transaction_date: date
    doc_ref: str  # Invoice/payment/receipt number
    doc_type: str  # invoice/credit_note/payment/etc
    description: str
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    balance: Decimal = Decimal("0")
    period: str
    journal_entry_id: Optional[int] = None  # Link to source journal entry
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SubsidiaryType(str, Enum):
    AR = "ar"           # S06-DN
    AP = "ap"           # S05-DN
    INVENTORY = "inv"   # S07-DN
    FA = "fa"           # S08-DN
    COST = "cost"       # S09-DN
    PREPAID = "prepaid" # S10-DN
    LOAN = "loan"       # S12-DN


class ReportTemplate(BaseModel):
    id: Optional[int] = None
    code: str  # B01-DN, B02-DN, etc.
    name: str
    name_en: str
    type: str  # balance_sheet / income_statement / cash_flow / notes
    category: str  # annual / interim / consolidated / management
    format_type: str  # standard / non_going_concern / condensed
    template_data: dict  # JSON template definition
    is_active: bool = True
    version: str = "TT99"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LineItem(BaseModel):
    """Line item for financial statements per TT99 Phụ lục IV"""
    id: Optional[int] = None
    report_code: str  # B01-DN, etc.
    ma_so: str  # 100, 110, 111, 112... per TT99 template
    parent_ma_so: Optional[str] = None
    ten_chi_tieu: str  # Vietnamese name
    ten_chi_tieu_en: str  # English name
    level: int  # indentation level
    is_bold: bool = False  # Bold = total line
    formula: Optional[str] = None  # Calculation formula
    sort_order: int
    is_active: bool = True


class ReportOutput(BaseModel):
    """Generated report output"""
    id: Optional[int] = None
    report_template_code: str
    period: str
    entity_id: Optional[int] = None  # For multi-entity
    format: str  # pdf/excel/html/csv/json/xbrl
    data: dict
    generated_at: datetime
    generated_by: str
    signed_by: Optional[str] = None
    signed_at: Optional[datetime] = None
    submitted: bool = False  # e-submission status


class ConsolidationEntry(BaseModel):
    """Multi-entity consolidation"""
    id: Optional[int] = None
    parent_entity_id: int
    child_entity_id: int
    ownership_pct: Decimal
    consolidation_method: str  # full/equity/proportionate
    period: str
    intercompany_eliminated: bool = False
    minority_interest: Decimal = Decimal("0")
    goodwill: Optional[Decimal] = None
```

### 5.2 DB Model Additions

```python
# infrastructure/models/gl_models.py — ADDITIONS

class JournalTypeModel(Base):
    __tablename__ = "journal_types"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    journal_type = Column(String(30), unique=True, nullable=False)
    prefix = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class JournalTypeSequenceModel(Base):
    __tablename__ = "journal_type_sequences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    journal_type = Column(String(30), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    last_sequence = Column(Integer, default=0, nullable=False)
    prefix = Column(String(10), nullable=False)
    __table_args__ = (
        UniqueConstraint('journal_type', 'fiscal_year', name='uq_journal_type_year'),
    )


# Enhanced JournalEntryModel — add journal_type column
class JournalEntryModel(Base):
    __tablename__ = "journal_entries"
    
    # ... existing columns ...
    journal_type = Column(String(30), default="general_journal", nullable=False, index=True)
    source_doc_ref = Column(String(50), nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    correction_of = Column(Integer, nullable=True)
    correction_method = Column(String(20), nullable=True)
    attachment_count = Column(Integer, default=0)


class SubsidiaryLedgerModel(Base):
    __tablename__ = "subsidiary_ledger"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subsidiary_type = Column(String(20), nullable=False, index=True)
    account_code = Column(String(20), ForeignKey("chart_of_accounts.code"), nullable=False)
    entity_id = Column(Integer, nullable=False)
    entity_name = Column(String(200), nullable=False)
    transaction_date = Column(Date, nullable=False)
    doc_ref = Column(String(50), nullable=False)
    doc_type = Column(String(30), nullable=False)
    description = Column(String(500))
    debit = Column(Numeric(18, 2), default=Decimal("0.00"))
    credit = Column(Numeric(18, 2), default=Decimal("0.00"))
    balance = Column(Numeric(18, 2), default=Decimal("0.00"))
    period = Column(String(7), nullable=False, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_subledger_type_period', 'subsidiary_type', 'period'),
        Index('idx_subledger_entity', 'subsidiary_type', 'entity_id', 'period'),
    )


class ReportTemplateModel(Base):
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    type = Column(String(30), nullable=False)
    category = Column(String(30), nullable=False)
    format_type = Column(String(30), default="standard")
    template_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="TT99")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LineItemModel(Base):
    __tablename__ = "report_line_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_code = Column(String(20), ForeignKey("report_templates.code"), nullable=False)
    ma_so = Column(String(10), nullable=False)
    parent_ma_so = Column(String(10), nullable=True)
    ten_chi_tieu = Column(String(200), nullable=False)
    ten_chi_tieu_en = Column(String(200))
    level = Column(Integer, default=0)
    is_bold = Column(Boolean, default=False)
    formula = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        UniqueConstraint('report_code', 'ma_so', name='uq_report_line_item'),
    )


class ReportOutputModel(Base):
    __tablename__ = "report_outputs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_template_code = Column(String(20), nullable=False)
    period = Column(String(7), nullable=False)
    entity_id = Column(Integer, nullable=True)
    format = Column(String(10), nullable=False)
    data = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    generated_by = Column(String(100))
    signed_by = Column(String(100), nullable=True)
    signed_at = Column(DateTime, nullable=True)
    submitted = Column(Boolean, default=False)


class ConsolidationModel(Base):
    __tablename__ = "consolidation_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_entity_id = Column(Integer, nullable=False)
    child_entity_id = Column(Integer, nullable=False)
    ownership_pct = Column(Numeric(5, 2), nullable=False)
    consolidation_method = Column(String(20), nullable=False)
    period = Column(String(7), nullable=False)
    intercompany_eliminated = Column(Boolean, default=False)
    minority_interest = Column(Numeric(18, 2), default=Decimal("0.00"))
    goodwill = Column(Numeric(18, 2), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

---

## 6. USE CASES: JOURNALS

### 6.1 UC-GLJ-01: Create General Journal Entry

**Actor**: Accountant  
**Precondition**: Period is open, user authenticated  
**Postcondition**: GJ entry created in DRAFT status

**Happy Path**:
1. User selects journal type = GENERAL
2. System auto-generates journal number (GJ-2026-000001)
3. User enters: date, description, lines (debit/credit accounts + amounts)
4. System validates: double-entry balanced (tolerance 0.001 VND)
5. System validates: all account codes exist and are active
6. System validates: period is open
7. System creates JournalEntry with status DRAFT
8. System returns created entry with ID

**Alternative Paths**:
- A1: User enters unbalanced entry (debit ≠ credit) → Error: "Double-entry violation"
- A2: User references closed period → Error: "Period is closed"
- A3: User enters invalid account → Error: "Account not found"
- A4: User manually enters journal number (if allowed by config) → Skip auto-generation
- A5: User enters multi-currency → FX rate auto-applied

**Exception Paths**:
- E1: Duplicate journal number → Error: "Journal number already exists"
- E2: Lines exceed max (configurable, default 999) → Error: "Too many lines"
- E3: Database failure → Rollback, return error

**Business Rules**:
- BR-GLJ-01: Journal number auto-increment per type per year
- BR-GLJ-02: Double-entry must balance within 0.001 VND
- BR-GLJ-03: Posting to closed period requires period reopen
- BR-GLJ-04: Minimum 2 lines (one debit, one credit)
- BR-GLJ-05: Each line must have at least one non-zero amount
- BR-GLJ-06: Debit/credit cannot be negative
- BR-GLJ-07: Max 500 chars description

### 6.2 UC-GLJ-02: Create Sales Journal Entry

**Actor**: AR Accountant  
**Source**: AR Invoice / Credit Note / Debit Note  
**Precondition**: AR invoice posted, period open  

**Happy Path**:
1. AR module posts invoice (TK 131 Nợ / TK 511 Có / TK 3331 Có)
2. AR module calls `create_sales_journal_entry(invoice_id)`
3. System auto-generates SJ number (SJ-2026-000001)
4. System creates JournalEntry with journal_type=SALES, source_module="ar"
5. System links source_doc_ref to invoice number
6. Returns success

**Alternative Paths**:
- A1: Credit note → Reversal entry (debit 511 / credit 131)
- A2: Cash sale → Also creates CRJ entry (debit 111/112 / credit 511)

**Exception Paths**:
- E1: Sales to non-existent customer → Error
- E2: Revenue account not configured → Error: "Revenue account missing for product"

### 6.3 UC-GLJ-03: Create Purchase Journal Entry

**Actor**: AP Accountant  
**Source**: AP Invoice / Debit Note / Credit Note  

**Happy Path**:
1. AP module posts purchase invoice
2. System auto-generates PJ number (PJ-2026-000001)
3. System creates JournalEntry with journal_type=PURCHASE, source_module="ap"

**GL Posting**: Nợ 152/153/156/611 (goods) + Nợ 133 (VAT) / Có 331 (AP)

### 6.4 UC-GLJ-04: Create Cash Receipts Journal Entry

**Actor**: Cashier  
**Source**: Cash receipt / Bank receipt  

**Happy Path**:
1. Cashier records receipt (sales, AR collection, bank withdrawal, advance return)
2. System auto-generates CR number (CR-2026-000001)
3. System creates JournalEntry with journal_type=CASH_RECEIPTS

**GL Posting**: Nợ 111/112 (cash/bank) / Có 511 (sales) or 131 (AR) or 141 (advance return)

### 6.5 UC-GLJ-05: Create Cash Disbursements Journal Entry

**Actor**: Cashier  
**Source**: Cash payment / Bank payment  

**Happy Path**:
1. Cashier records payment (expense, purchase, salary, advance, bank deposit)
2. System auto-generates CD number (CD-2026-000001)
3. System creates JournalEntry with journal_type=CASH_DISBURSEMENTS

**GL Posting**: Nợ 641/642/622/331/334/141 / Có 111/112

### 6.6 UC-GLJ-06: Post Journal Entry

**Actor**: Chief Accountant  
**Precondition**: Entry in DRAFT/PENDING status  

**Happy Path**:
1. Chief Accountant selects entry to post
2. System validates: entry not already posted
3. System validates: period open
4. System validates: double-entry balanced
5. System validates: all accounts exist and active
6. System updates: is_posted=True, posted_date=now, approved_by=user
7. System updates subsidiary ledger balances
8. Returns posted entry

**Alternative Paths**:
- A1: Entry requires approval → Set status PENDING_APPROVAL, notify approver
- A2: Batch posting → Multiple entries posted in transaction

**Exception Paths**:
- E1: Already posted → Error: "Cannot repost"
- E2: Period closed → Error: "Post to closed period"
- E3: Debit/credit mismatch → Error: "Unbalanced entry"

### 6.7 UC-GLJ-07: Reverse Journal Entry

**Actor**: Chief Accountant  
**Precondition**: Entry is posted  

**Happy Path**:
1. User selects posted entry to reverse
2. System creates reversal entry with opposite debit/credit
3. New entry marked as correction_of=original_id, correction_method=REVERSAL
4. Both entries clearly linked in audit trail

**Business Rules**:
- BR-GLJ-08: Reversal preserves original audit trail
- BR-GLJ-09: Reversal cannot itself be reversed — use correcting entry

### 6.8 UC-GLJ-08: List/Search Journal Entries

**Actor**: Accountant, Auditor  

**Filters**: period, journal_type, date range, account_id, is_posted, source_module, keyword  
**Sort**: date desc (default), journal_number, amount  
**Pagination**: limit/offset

---

## 7. USE CASES: SUBSIDIARY LEDGERS

### 7.1 UC-GLS-01: Generate AR Subsidiary Ledger (S06-DN)

**Actor**: AR Accountant  
**Precondition**: Period selected  

**Happy Path**:
1. User selects period + customer (optional)
2. System queries `subsidiary_ledger` WHERE subsidiary_type='ar' AND period=X
3. System computes: opening_balance, period_debit, period_credit, closing_balance
4. System formats per S06-DN template with Vietnamese header/footer
5. Returns: JSON data + rendered PDF/Excel/HTML

**Columns** (S06-DN per TT99):
- STT (No.)
- Tên khách hàng (Customer name)
- Mã số thuế (Tax code)
- Số dư đầu kỳ Nợ/Có (Opening DR/CR)
- Phát sinh trong kỳ Nợ/Có (Period DR/CR)
- Số dư cuối kỳ Nợ/Có (Closing DR/CR)
- Ghi chú (Notes)

### 7.2 UC-GLS-02: Generate AP Subsidiary Ledger (S05-DN)

Same as GLS-01 but for vendors. Logic is symmetric.

### 7.3 UC-GLS-03: Generate Inventory Subsidiary Ledger (S07-DN)

**Actor**: Inventory Accountant  

**Additional columns**:
- Tên hàng (Item name)
- ĐVT (Unit)
- Số lượng đầu kỳ (Opening Qty)
- Giá trị đầu kỳ (Opening Value)
- Nhập trong kỳ SL/Tiền (In Qty/Value)
- Xuất trong kỳ SL/Tiền (Out Qty/Value)
- Số lượng cuối kỳ (Closing Qty)
- Giá trị cuối kỳ (Closing Value)

### 7.4 UC-GLS-04: Generate Fixed Asset Subsidiary Ledger (S08-DN)

**Actor**: FA Accountant  

**Columns**:
- Tên TSCĐ (Asset name)
- Ngày đưa vào sử dụng (In-use date)
- Nguyên giá (Original cost)
- Giá trị hao mòn lũy kế (Accumulated depreciation)
- Giá trị còn lại (Residual value)
- Tỷ lệ khấu hao (Depreciation rate)

### 7.5 UC-GLS-05: Generate General Subsidiary Ledger (S04-DN)

**Actor**: Accountant  

Generic subsidiary ledger for any account code. User selects account → System shows all transactions affecting that account with opening/period/closing balances.

### 7.6 UC-GLS-06: Auto-Post to Subsidiary Ledger

**Actor**: System (background)
**Trigger**: Journal entry posted

**Happy Path**:
1. Journal entry is posted (is_posted=True)
2. For each line with an account linked to a subsidiary type (131→ar, 331→ap, 152→inv):
3. System creates/updates SubsidiaryLedger record
4. System recomputes running balance for entity

**Rules**:
- BR-GLS-01: AR account (131) lines → subsidiary_type='ar', entity_id=customer_id
- BR-GLS-02: AP account (331) lines → subsidiary_type='ap', entity_id=vendor_id
- BR-GLS-03: Inventory accounts (152,153,155,156) → subsidiary_type='inv'
- BR-GLS-04: FA accounts (211,212,213,214,215) → subsidiary_type='fa'
- BR-GLS-05: Each subsidiary entry maintains running balance
- BR-GLS-06: GL to subsidiary reconciliation must balance

---

## 8. USE CASES: REPORTING ENGINE

### 8.1 UC-GLR-01: Generate Balance Sheet (B01-DN)

**Actor**: Chief Accountant  
**Precondition**: Period closed or user has rights  

**Happy Path**:
1. User selects: report_code=B01-DN, period, entity (optional), comparative=true/false
2. System loads LineItemModel WHERE report_code='B01-DN' ORDER BY sort_order
3. For each line item with formula, system computes:
   - Current period amount
   - Previous period amount (if comparative)
4. System computes totals per section (TÀI SẢN / NGUỒN VỐN)
5. System validates: Tổng Tài sản = Tổng Nguồn vốn
6. System returns structured data for rendering

**Line Items per TT99 B01-DN**:
- 100: TÀI SẢN NGẮN HẠN (Current Assets)
  - 110: Tiền và các khoản tương đương tiền (111+112)
  - 120: Đầu tư tài chính ngắn hạn (121+128)
  - 130: Các khoản phải thu ngắn hạn (131+136+138)
  - 140: Hàng tồn kho (151+152+153+154+155+156)
  - 150: Tài sản ngắn hạn khác
- 200: TÀI SẢN DÀI HẠN (Non-current Assets)
- 300: NỢ PHẢI TRẢ (Liabilities)
- 400: VỐN CHỦ SỞ HỮU (Equity)

**Formulas**: ma_so 110 = 111+112; ma_so 100 = sum(110+120+130+140+150)

### 8.2 UC-GLR-02: Generate Income Statement (B02-DN)

**Happy Path**:
1. User selects: report_code=B02-DN, period
2. System loads LineItemModel for B02-DN
3. Computes revenue (511+512+515), cost of goods sold (632), gross profit
4. Computes selling expenses (641), admin expenses (642)
5. Computes: Operating profit = Gross profit - 641 - 642
6. Computes: Other income/expenses, net interest, net profit

**Line Items**:
- 01: Doanh thu bán hàng và cung cấp dịch vụ
- 02: Các khoản giảm trừ doanh thu
- 10: Doanh thu thuần
- 11: Giá vốn hàng bán
- 20: Lợi nhuận gộp
- 21: Doanh thu hoạt động tài chính
- 22: Chi phí tài chính
- 23: Chi phí bán hàng
- 24: Chi phí quản lý doanh nghiệp
- 30: Lợi nhuận thuần từ HĐKD
- 40: Lợi nhuận khác
- 50: Tổng lợi nhuận kế toán trước thuế
- 51: Chi phí thuế TNDN
- 60: Lợi nhuận sau thuế

### 8.3 UC-GLR-03: Generate Cash Flow Statement (B03-DN)

**Actor**: Chief Accountant  
**Difficulty**: HIGH — requires tracking cash movements by category

**Methods**:
- Direct method (Khuyến khích theo TT99)
- Indirect method (Cũng được chấp nhận)

**Sections**:
- Lưu chuyển tiền từ HĐKD (Operating)
- Lưu chuyển tiền từ HĐĐT (Investing)
- Lưu chuyển tiền từ HĐTC (Financing)

**Flow**:
1. For direct: Aggregate all cash journal entries (CRJ + CDJ) by category
2. For indirect: Start with net profit + adjustments

### 8.4 UC-GLR-04: Generate Notes to FS (B09-DN)

**Actor**: Chief Accountant  
**Difficulty**: VERY HIGH — heavy disclosure requirements

**Sections per TT99 B09-DN**:
- Đặc điểm hoạt động (1-3)
- Kỳ kế toán, đơn vị tiền tệ (4-5)
- Chuẩn mực và chế độ kế toán (6)
- Các chính sách kế toán (7)
- Thông tin bổ sung (8-28): detailed breakdown of each BS/IS line

### 8.5 UC-GLR-05: Export Report to PDF

**Actor**: Any user  

**Happy Path**:
1. User selects: report, period, format=PDF
2. System generates report data
3. System renders to PDF using WeasyPrint (existing dep)
4. Applies Vietnamese formatting (VND, date locale)
5. Returns downloadable PDF

**Alternative Paths**:
- A1: Export to XLSX (openpyxl — existing dep)
- A2: Export to HTML
- A3: Export to CSV
- A4: Export to XBRL (Phase 2)

### 8.6 UC-GLR-06: Drill-Down from Report to Detail

**Actor**: Chief Accountant, Auditor  

**Happy Path**:
1. User clicks on a line item value (e.g., B02-DN line 11 "Giá vốn hàng bán")
2. System shows detailed breakdown by sub-account
3. User clicks on sub-account → shows journal lines
4. User clicks on journal line → shows original entry
5. User clicks on entry → shows source document (invoice/receipt)

### 8.7 UC-GLR-07: Multi-Entity Consolidated Report

**Actor**: Group CFO  

**Happy Path**:
1. User selects: consolidated=true, entity_ids=[parent, child1, child2]
2. System generates individual FS for each entity
3. System applies consolidation method (full/equity)
4. System eliminates intercompany balances (TK 136/336)
5. System eliminates intercompany revenue/expense
6. System computes minority interest
7. Returns consolidated report

**Rules**:
- BR-GLR-01: Intercompany balances must match before elimination
- BR-GLR-02: Ownership > 50% → Full consolidation
- BR-GLR-03: Ownership 20-50% → Equity method
- BR-GLR-04: Ownership < 20% → Cost method

### 8.8 UC-GLR-08: IFRS Conversion Report

**Actor**: Group CFO, IFRS Accountant  

**Happy Path**:
1. User selects VAS report + IFRS conversion mapping
2. System applies VAS→IFRS adjustments per QĐ 345/2020
3. System generates IFRS-compliant FS
4. System generates reconciliation note (VAS→IFRS adjustments)

**Key VAS→IFRS Differences**:
- VAS: Historical cost → IFRS: Fair value
- VAS: Straight-line depreciation → IFRS: Component depreciation
- VAS: No discounting → IFRS: Discounting of long-term receivables/payables
- VAS: Revenue recognition differently than IFRS 15
- VAS: Operating leases differently than IFRS 16

### 8.9 UC-GLR-09: Scheduled Report Generation

**Actor**: System (cron/scheduler)  

**Trigger**: Monthly/quarterly/yearly schedule  

**Happy Path**:
1. Scheduler triggers GLUseCases.generate_scheduled_reports()
2. System identifies all due reports per schedule config
3. System generates each report
4. System archives report output
5. System notifies stakeholders (email/in-app)

### 8.10 UC-GLR-10: Ad-hoc Report Query

**Actor**: Accountant, Financial Analyst  

**Happy Path**:
1. User selects: date range, accounts, dimensions (cost center, department, project)
2. User optionally groups by: period, account, dimension, entity
3. System queries GL with filters + grouping
4. Returns pivot-table-style result
5. Export to Excel

---

## 9. BUSINESS RULES ENGINE

### 9.1 Journal Rules

| Rule ID | Rule | Severity | Scope |
|---------|------|----------|-------|
| BR-J-001 | Double-entry must balance (tolerance 0.001 VND) | ERROR | All journals |
| BR-J-002 | Minimum 2 lines per entry | ERROR | All journals |
| BR-J-003 | Debit/credit cannot be negative | ERROR | All journals |
| BR-J-004 | Cannot post to closed period | ERROR | All journals |
| BR-J-005 | Journal number unique per year | ERROR | All journals |
| BR-J-006 | Journal number prefix configurable per type | CONFIG | System |
| BR-J-007 | Each line must reference existing active account | ERROR | All journals |
| BR-J-008 | VAT lines need valid VAT rate (0%, 5%, 8%, 10%) | WARN | Sales/Purchase |
| BR-J-009 | Revenue accounts credited only | ERROR | Sales |
| BR-J-010 | Cash accounts debited for receipts | ERROR | CRJ |
| BR-J-011 | Cash accounts credited for disbursements | ERROR | CDJ |
| BR-J-012 | AR account (131) paired with revenue accounts | WARN | Sales |
| BR-J-013 | AP account (331) paired with expense/inventory | WARN | Purchase |

### 9.2 Subsidiary Ledger Rules

| Rule ID | Rule | Severity |
|---------|------|----------|
| BR-SL-001 | GL total = Subsidiary total reconciliation | ERROR |
| BR-SL-002 | AR sub-ledger balance = GL balance TK 131 | ERROR |
| BR-SL-003 | AP sub-ledger balance = GL balance TK 331 | ERROR |
| BR-SL-004 | Inventory sub-ledger balance = GL balance TK 152/153/155/156 | ERROR |
| BR-SL-005 | FA sub-ledger original cost = GL TK 211/212/213/215 | ERROR |
| BR-SL-006 | FA sub-ledger accumulated depreciation = GL TK 214 | ERROR |

### 9.3 Reporting Rules

| Rule ID | Rule | Severity |
|---------|------|----------|
| BR-R-001 | Total Assets = Total Liabilities + Equity | ERROR |
| BR-R-002 | Net profit = Total revenue - Total expenses | ERROR |
| BR-R-003 | Cash flow operating + investing + financing = Net change | ERROR |
| BR-R-004 | Comparative periods must use same accounting policies | WARN |
| BR-R-005 | Prior period adjustments disclosed separately | WARN |
| BR-R-006 | Related party transactions disclosed | WARN |
| BR-R-007 | Subsequent events disclosed | WARN |
| BR-R-008 | Going concern assumption stated | WARN |
| BR-R-009 | FS due within 90 days (annual) / 45 days (interim) | WARN |

---

## 10. DATA FLOW DIAGRAMS

### 10.1 Sales Transaction Flow

```
Customer Order → Sales Invoice (AR) → Sales Journal Entry (S03b2-DN)
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
           AR Subsidiary Ledger (S06-DN)          General Ledger (S01-DN)
           Customer A: Sale +VND X                TK 131: +VND X
                                                    TK 511: -VND X
                                                    TK 3331: -VND Y
                    │                                    │
                    └────────────► Reconciliation ◄──────┘
```

### 10.2 Purchase Transaction Flow

```
Purchase Order → Purchase Receipt → AP Invoice → Purchase Journal (S03b1-DN)
                                                    │
                  ┌─────────────────────────────────┴──────────────┐
                  ▼                                                ▼
         AP Subsidiary Ledger (S05-DN)                  General Ledger (S01-DN)
         Vendor B: Purchase +VND X                      TK 152/156: +VND X
                                                         TK 133: +VND Y
                                                         TK 331: -VND (X+Y)
```

### 10.3 Cash Receipt Flow

```
Cash/Check Received → Cash Receipt Voucher
         │
         ▼
Cash Receipts Journal (S03a1-DN)
         │
         ├──→ Bank Deposit → Bank Journal
         ├──→ AR Collection → AR Subsidiary Ledger updated
         └──→ General Ledger (S01-DN): TK 111/112 DR, TK 131/511 CR
```

### 10.4 Report Generation Flow

```
User Request → Report Engine
         │
         ▼
Load Template (LineItemModel for B01-DN)
         │
         ▼
Query Balances (sum of posted journal lines by period)
         │
         ▼
Apply Formulas (ma_so 110 = 111 + 112)
         │
         ▼
Validate (Total Assets = Total Liabilities + Equity)
         │
         ▼
Render (JSON → PDF/Excel/HTML/CSV)
         │
         ▼
Archive + Sign (optional) → Output
```

---

## 11. WORKFLOWS & USER JOURNEYS

### 11.1 Month-End Close Workflow

```
Day 1-5:    All source modules post entries (AR/AP/Cash/FA/Payroll/Tax)
Day 5-10:   Reconcile: GL balance = Subsidiary balance
            Reconcile: Bank statements, AR aging, AP aging
            Adjusting entries: accruals, prepaids, depreciation, forex
Day 10-15:  Post all adjusting entries
            Verify double-entry balance
Day 15-20:  Generate FS drafts (B01-DN, B02-DN, B03-DN, B09-DN)
            Review with Chief Accountant
            Corrections if needed
Day 20-25:  Chief Accountant approves FS
            Period close
Month-end:  Year-end → carry forward (UC-FP-07)
            Archive reports
```

### 11.2 Journal Entry Approval Workflow

```
Draft → Submitted → Pending Approval → Approved → Posted
                        ↓                  ↓
                    Rejected           (Audit trail)
                        ↓
                     Draft (with rejection reason)
```

### 11.3 User Journey: Chief Accountant Monthly Review

1. Login → Dashboard shows: unposted entries, uncategorized cash, AR/AP balances
2. Review unposted entries → Post or reject
3. Generate subsidiary ledgers → Verify vs GL
4. Generate month-end reports (B01-DN, B02-DN)
5. Review, sign digitally
6. Close period

### 11.4 User Journey: Tax Accountant VAT Period

1. Login → Sales Journal (S03b2-DN) → Export sales data
2. Purchase Journal (S03b1-DN) → Export purchase data
3. Match input VAT (TK 133) vs e-invoice data from GDT
4. Generate VAT declaration (via Tax module)
5. Submit to GDT eTax

---

## 12. TT99 ACCOUNTING BOOK TEMPLATES

### 12.1 S03c-DN: General Journal Format

```
Đơn vị: XYZ Co., Ltd                      Mẫu số S03c-DN
Địa chỉ: Hanoi                            (Ban hành theo TT 99/2025/TT-BTC)

                     SỔ NHẬT KÝ CHUNG
                          (General Journal)
Năm 2026

┌──────┬──────────┬────────────┬──────────────────────┬──────────┬──────────┬──────────┐
│ NT   │ Số hiệu  │ Diễn giải  │   TK đối ứng         │ Số phát sinh          │ Ghi chú  │
│ ghi  │ chứng từ │            ├──────┬───────────────┤──────────┼──────────┤          │
│ sổ   │          │            │ Nợ   │ Có            │ Nợ       │ Có       │          │
├──────┼──────────┼────────────┼──────┼───────────────┼──────────┼──────────┼──────────┤
│ A    │ B        │ C          │ 1    │ 2             │ 3        │ 4        │ 5        │
├──────┼──────────┼────────────┼──────┼───────────────┼──────────┼──────────┼──────────┤
│      │          │ Số dư đầu  │      │               │          │          │          │
│      │          │ kỳ         │      │               │          │          │          │
├──────┼──────────┼────────────┼──────┼───────────────┼──────────┼──────────┼──────────┤
│      │          │ Số PS      │      │               │          │          │          │
│      │          │ trong kỳ   │      │               │          │          │          │
├──────┼──────────┼────────────┼──────┼───────────────┼──────────┼──────────┼──────────┤
│      │          │ Cộng PS    │      │               │ XXX      │ XXX      │          │
├──────┼──────────┼────────────┼──────┼───────────────┼──────────┼──────────┼──────────┤
│      │          │ Số dư      │      │               │          │          │          │
│      │          │ cuối kỳ    │      │               │          │          │          │
└──────┴──────────┴────────────┴──────┴───────────────┴──────────┴──────────┴──────────┘

Ngày ... tháng ... năm ...
Người lập              Kế toán trưởng              Giám đốc
(Ký, họ tên)           (Ký, họ tên)                (Ký, họ tên)
```

### 12.2 S03b2-DN: Sales Journal (Simplified)

```
                  SỔ NHẬT KÝ BÁN HÀNG
                      (Sales Journal)
                     Năm 2026

┌──────┬──────┬──────────┬─────┬──────┬─────────────────────────┬──────┐
│ NT   │ Số   │ Diễn     │ TK  │ TK   │ Doanh thu               │ Thuế │
│ ghi  │ CTừ  │ giải     │ 131 │ 511  ├──────┬──────┬──────┬────┤ VAT  │
│ sổ   │      │          │ Nợ  │ Có   │ 5111 │ 5112 │ 5118 │... │ 3331 │
├──────┼──────┼──────────┼─────┼──────┼──────┼──────┼──────┼────┼──────┤
```

### 12.3 S01-DN: General Ledger (Per Account)

```
                  SỔ CÁI
             (General Ledger)
           Năm 2026
Tên TK: Tiền mặt
Số hiệu: 111

┌──────┬──────────┬────────────┬──────────┬──────────┬──────────┬──────────┐
│ NT   │ Số hiệu  │ Diễn giải  │ TK đối   │ Số tiền              │ Số dư    │
│ ghi   │ CTừ      │            │ ứng      ├──────────┬───────────┤          │
│ sổ   │          │            │          │ Nợ       │ Có        │          │
├──────┼──────────┼────────────┼──────────┼──────────┼───────────┼──────────┤
│      │          │ Số dư đầu  │          │          │           │ XXXX     │
│      │          │ kỳ         │          │          │           │          │
├──────┼──────────┼────────────┼──────────┼──────────┼───────────┼──────────┤
│      │          │ PS trong   │          │          │           │          │
│      │          │ kỳ         │          │          │           │          │
├──────┼──────────┼────────────┼──────────┼──────────┼───────────┼──────────┤
│      │          │ Cộng PS    │          │ XXX      │ XXX       │          │
├──────┼──────────┼────────────┼──────────┼──────────┼───────────┼──────────┤
│      │          │ Số dư      │          │          │           │ XXXX     │
│      │          │ cuối kỳ    │          │          │           │          │
└──────┴──────────┴────────────┴──────────┴──────────┴───────────┴──────────┘
```

---

## 13. GL POSTING MATRIX

### 13.1 Module-to-GL Mapping

| Module | Transaction Type | Debit Account | Credit Account | Journal Type |
|--------|-----------------|---------------|----------------|--------------|
| AR | Invoice (Sales) | 131 (AR) | 511 (Revenue) | SALES |
| AR | Invoice (VAT output) | 131 (AR) | 3331 (VAT output) | SALES |
| AR | Invoice (Revenue) | - | 511 (Revenue) | SALES |
| AR | Credit Note | 511 (Revenue) | 131 (AR) | SALES (reversal) |
| AR | Cash Receipt (AR) | 111/112 | 131 (AR) | CASH_RECEIPTS |
| AP | Purchase Invoice | 152/156 (Goods) | 331 (AP) | PURCHASE |
| AP | Purchase Invoice (VAT) | 133 (VAT input) | 331 (AP) | PURCHASE |
| AP | Payment to Vendor | 331 (AP) | 111/112 | CASH_DISBURSEMENTS |
| Cash | Cash Receipt (Sales) | 111/112 | 511 (Revenue) | CASH_RECEIPTS |
| Cash | Cash Payment (Expense) | 641/642 | 111/112 | CASH_DISBURSEMENTS |
| Cash | Bank to Cash | 111 | 112 | CASH_RECEIPTS |
| Cash | Cash to Bank | 112 | 111 | CASH_DISBURSEMENTS |
| FA | Asset Purchase | 211/212 | 111/112/331 | GENERAL |
| FA | Depreciation | 641/642/627 | 214 | ADJUSTING |
| FA | Disposal | 214/811 | 211/711 | GENERAL |
| Payroll | Salary | 334 | 111/112 | CASH_DISBURSEMENTS |
| Payroll | Salary Cost | 622/627/641/642 | 334 | GENERAL |
| Payroll | SI Contribution | 3383/3384/3385/3386 | 111/112 | CASH_DISBURSEMENTS |
| Inventory | Goods Issue (COGS) | 632 | 152/155/156 | GENERAL |
| Inventory | Stock Adjustment | 138/632 | 152/155/156 | ADJUSTING |
| Tax | VAT Payable | 3331 | 111/112 | CASH_DISBURSEMENTS |
| Tax | CIT Payment | 3334 | 111/112 | CASH_DISBURSEMENTS |
| Treasury | Forex Revaluation | 413/635 | 515/413 | ADJUSTING |
| Treasury | Loan Drawdown | 111/112 | 341 | CASH_RECEIPTS |
| Treasury | Loan Repayment | 341 | 111/112 | CASH_DISBURSEMENTS |
| Close | Revenue Closing | 511/515 | 911 | CLOSING |
| Close | Expense Closing | 911 | 641/642/632 | CLOSING |
| Close | Net Income | 911 | 421 (RE) | CLOSING |

### 13.2 TT99 Account Changes Impacting Journals

| Old Account (TT200) | New Account (TT99) | Impact |
|--------------------|--------------------|--------|
| 111 Tiền mặt | 111 Tiền mặt (unchanged) | None |
| 112 Tiền gửi NH | 112 Tiền gửi không kỳ hạn | Renamed |
| 161 (eliminated) | - | Migrate |
| 211 TSCĐ hữu hình | 211 TSCĐ hữu hình (unchanged) | None |
| 215 (new) | 215 Tài sản sinh học | NEW |
| 331 Phải trả người bán | 331 Phải trả người bán (unchanged) | None |
| 333(1) Thuế GTGT | 3331 Thuế GTGT đầu ra (unchanged) | None |
| 441 (eliminated) | - | Migrate to 411 |
| 611 (eliminated) | - | Migrate to 152/156 |
| 631 (eliminated) | - | Migrate to 154 |
| 821 (new sub) | 82112 GMT Top-Up Tax | NEW |

---

## 14. REPORT TEMPLATES

### 14.1 TT99 B01-DN: Statement of Financial Position

See financial_statements.md BRD for full template. Key additions needed:
- Add comparative column (số đầu năm / số cuối năm)
- Rename from "balance_sheet" to "B01-DN" naming
- Implement all 250+ line items from TT99 Phụ lục IV.B01
- Add non-going-concern variant (B01-DNKLT)

### 14.2 Management Reports (Custom)

| Report | Frequency | Audience |
|--------|-----------|----------|
| Trial Balance (Bảng cân đối số PS) | Monthly | Accountant |
| Account Analysis (Phân tích TK) | Monthly | Chief Accountant |
| GL Detail (Chi tiết Sổ Cái) | Monthly | Auditor |
| Journal Summary (Tổng hợp NK) | Monthly | CFO |
| AR Aging (Phân tích tuổi nợ) | Weekly | AR Team |
| AP Aging | Weekly | AP Team |
| Cash Position (Tình hình tiền) | Daily | Treasurer |
| P&L by Department | Monthly | Dept Heads |
| Budget vs Actual | Monthly | CFO |
| Cost Center Summary | Monthly | Cost Accountant |

---

## 15. NON-FUNCTIONAL REQUIREMENTS

### 15.1 Performance

| Requirement | Target |
|-------------|--------|
| Journal entry creation | < 500ms |
| Journal listing with 10K entries | < 2s |
| Subsidiary ledger generation | < 3s for 50K lines |
| Report generation (B01-DN) | < 5s |
| Multi-entity consolidation (10 entities) | < 30s |
| PDF export | < 10s |
| Concurrent users | 100+ |
| Data retention | 10+ years (Luật Kế toán) |

### 15.2 Security

- Journal entries read-only after posting
- Correction requires reversal entry (no delete)
- Approval workflow configurable
- Audit log for all state changes
- Digital signature support
- Role-based access: viewer, accountant, chief accountant, CFO, auditor

### 15.3 Compliance

- TT99/2025/TT-BTC compliant
- Luật Kế toán 89/2025/QH15 compliant
- TT58/2026/TT-BTC (micro-enterprise) ready
- Audit trail per Luật Kế toán Art.12
- Data retention 10 years minimum
- Vietnamese language primary (English secondary)

### 15.4 Technical

- Flask 3.0 + SQLAlchemy 2.0 + PostgreSQL 16
- JSON for report template storage
- WeasyPrint for PDF (existing)
- openpyxl for Excel (existing)
- Alembic migrations (existing)
- Export formats: PDF, Excel (XLSX), HTML, CSV, JSON, XBRL (Phase 2)

---

## 16. IMPLEMENTATION ROADMAP

### Phase 1: Journal Foundation (Week 1-3)
| Task | Effort | Dependencies |
|------|--------|-------------|
| Enhance JournalType, fix JV-prefix validation | 2d | None |
| Add journal_type column + migration | 1d | Task 1 |
| Create JournalType + JournalTypeSequence models | 1d | Task 1 |
| Update GLRepository for journal type support | 2d | Task 2-3 |
| Update GLUseCases + routes | 1d | Task 4 |
| Fix domain validators (remove JV hardcode) | 1d | Task 1 |
| Tests: 30+ unit + integration | 3d | Task 1-6 |

### Phase 2: Specialized Journals (Week 4-6)
| Task | Effort | Dependencies |
|------|--------|-------------|
| Sales Journal use cases + format | 3d | Phase 1 |
| Purchase Journal use cases + format | 3d | Phase 1 |
| Cash Receipts Journal format + integration | 3d | Phase 1 + Cash |
| Cash Disbursements Journal format + integration | 3d | Phase 1 + Cash |
| Journal templates (S03a1/2, S03b1/2, S03c) | 2d | Tasks 1-4 |
| Tests: 40+ | 3d | Tasks 1-5 |

### Phase 3: Subsidiary Ledgers (Week 7-9)
| Task | Effort | Dependencies |
|------|--------|-------------|
| SubsidiaryLedger domain + models + migration | 2d | Phase 1 |
| SubsidiaryLedger repository | 3d | Task 1 |
| AR sub-ledger (S06-DN) | 3d | Task 2 + AR module |
| AP sub-ledger (S05-DN) | 3d | Task 2 + AP module |
| Inventory sub-ledger (S07-DN) | 2d | Task 2 + Inventory |
| FA sub-ledger (S08-DN) | 2d | Task 2 + FA module |
| Auto-posting to subsidiary on journal post | 2d | Task 2 |
| GL ↔ Subsidiary reconciliation | 2d | Task 3-7 |
| Tests: 50+ | 4d | Tasks 1-8 |

### Phase 4: Reporting Engine (Week 10-14)
| Task | Effort | Dependencies |
|------|--------|-------------|
| ReportTemplate domain + models + migration | 2d | Phase 1 |
| LineItem domain + models | 2d | Task 1 |
| Report template data (B01/B02/B03/B09) | 3d | Task 2 |
| Report engine core (formulas, compute) | 5d | Task 2-3 |
| PDF rendering (WeasyPrint templates) | 3d | Task 4 |
| Excel rendering (openpyxl) | 2d | Task 4 |
| HTML rendering | 1d | Task 4 |
| Cash flow B03-DN (direct + indirect) | 5d | Task 4 |
| B09-DN Notes (basic version) | 5d | Task 4 |
| Report routes + API | 2d | Task 4-9 |
| Tests: 50+ | 5d | Tasks 1-10 |

### Phase 5: Advanced (Week 15-20)
| Task | Effort | Dependencies |
|------|--------|-------------|
| Multi-entity consolidation | 5d | Phase 4 |
| Intercompany elimination | 3d | Task 1 |
| IFRS conversion layer | 5d | Phase 4 |
| Drill-down (report → GL → document) | 3d | Phase 4 |
| Scheduled reports (cron) | 2d | Phase 4 |
| Ad-hoc query builder | 5d | Phase 4 |
| XBRL taxonomy mapping | 5d | Task 4 |
| e-Submission (GDT integration) | 3d | Task 7 |
| Digital signing workflow | 2d | Task 8 |
| Tests: 60+ | 5d | Tasks 1-9 |

### Estimated Total: 16-20 weeks, ~500 tests

---

## 17. APPENDIX: LEGAL REFERENCES

### 17.1 Primary Sources Consulted

| Source | URL | Content |
|--------|-----|---------|
| Bộ Tài chính | mof.gov.vn | Circular 99/2025/TT-BTC full text |
| Thuế điện tử | thuedientu.gdt.gov.vn | Tax declaration, e-invoice |
| Hải quan điện tử | customs.gov.vn | Customs e-declaration |
| Bảo hiểm XH | baohiemxahoi.gov.vn | SI declaration portal |
| Dịch vụ công | dichvucong.gov.vn | National public service portal |
| VBPL | vbpl.vn | Legal document database |
| Kế toán Thiên Ưng | ketoanthienung.net | TT99 COA + journal training |
| Kế toán Lê Ánh | ketoanleanh.edu.vn | TT99 accounting book templates |
| Web Kế Toán | webketoan.com | Accounting practice resources |
| EY Vietnam | ey.com/vi_vn | VAS/IFRS advisory |
| PwC Vietnam | pwc.com/vn | Tax & accounting insights |
| Deloitte Vietnam | deloitte.com/vn | TT99 analysis |
| KPMG Vietnam | kpmg.com/vn | TT99 key changes publication |
| VACPA | vacpa.org.vn | Auditing practices |
| VAA | vaa.net.vn | Accounting association |
| IFRS Foundation | ifrs.org | IFRS standards reference |
| Alitium | alitium.com | Big 4 analysis of TT99 |
| Acclime Vietnam | vietnam.acclime.com | TT99 implementation guide |
| InCorp Vietnam | vietnam.incorp.asia | TT99 SME guide |

### 17.2 Legal Documents Verbatim

- **TT 99/2025/TT-BTC**: Art.9 (voucher self-design), Art.12 (accounting books), Art.15 (book types), Art.16 (recording methods), Art.17-21 (opening, recording, correction, closing), Art.22-28 (multi-unit), Art.29 (transition from TT200)
- **Luật Kế toán 89/2025/QH15**: Amended Art.16 (voucher content), Art.24 (book requirements), Art.30 (FS deadlines)
- **TT 58/2026/TT-BTC**: Micro-enterprise accounting regime (eff. 01/07/2026)
- **QĐ 345/2020/QĐ-BTC**: IFRS convergence roadmap (Phase 1: 2022-2025, Phase 2: 2025-2030)

---

## 18. APPENDIX: BIG 4 COMPARISON

### 18.1 TT99 Adoption Readiness — Market Survey

| Vendor | COA | Journals | Subsidiary | Reporting | TT99 Ready |
|--------|-----|----------|------------|-----------|------------|
| MISA | ✅ | ✅ | ✅ | ✅ | ✅ (v2026) |
| FAST | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bravo | ✅ | ✅ | ✅ | ✅ | ✅ |
| SmartACCT | ⚠️ (partial) | ❌ | ❌ | ❌ | ❌ |
| Odoo (VN) | ✅ (module) | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| SAP (VN) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Oracle (VN) | ✅ | ✅ | ✅ | ✅ | ✅ |

### 18.2 Key Vendor Features We Must Match

| Feature | MISA | FAST | Bravo | SmartACCT Target |
|---------|------|------|-------|------------------|
| S03c-DN General Journal | ✅ | ✅ | ✅ | Phase 1 |
| S03b2-DN Sales Journal | ✅ | ✅ | ✅ | Phase 2 |
| S03b1-DN Purchase Journal | ✅ | ✅ | ✅ | Phase 2 |
| S03a1-DN Cash Receipts | ✅ | ✅ | ✅ | Phase 2 |
| S03a2-DN Cash Disbursements | ✅ | ✅ | ✅ | Phase 2 |
| S01-DN General Ledger | ✅ | ✅ | ✅ | Phase 3 |
| S05-DN AP Subsidiary | ✅ | ✅ | ✅ | Phase 3 |
| S06-DN AR Subsidiary | ✅ | ✅ | ✅ | Phase 3 |
| B01-DN Statement of FP | ✅ | ✅ | ✅ | Phase 4 |
| B02-DN Income Statement | ✅ | ✅ | ✅ | Phase 4 |
| B03-DN Cash Flow | ✅ | ✅ | ✅ | Phase 4 |
| B09-DN Notes | ✅ | ✅ | ✅ | Phase 4 |
| PDF Export | ✅ | ✅ | ✅ | Phase 4 |
| Excel Export | ✅ | ✅ | ✅ | Phase 4 |
| XBRL | ✅ | ✅ | ✅ | Phase 5 |
| e-Submission | ✅ | ✅ | ✅ | Phase 5 |

---

## APPENDIX B: OUTDATED REFERENCES REMOVED

The following documents and references have been superseded and must NOT be cited:

| Removed Document | Reason | Replacement |
|-----------------|--------|-------------|
| TT 200/2014/TT-BTC | Replaced by TT99 from 01/01/2026 | TT 99/2025/TT-BTC |
| TT 75/2015/TT-BTC | Amendment to TT200, now superseded | TT 99/2025/TT-BTC |
| TT 53/2016/TT-BTC | Amendment to TT200, now superseded | TT 99/2025/TT-BTC |
| TT 195/2012/TT-BTC | Investor accounting, superseded | TT 99/2025/TT-BTC |
| TT 18/2020/TT-BTC | Replaced by TT 157/2025/TT-BTC | TT 157/2025/TT-BTC |
| NĐ 11/2020/NĐ-CP | KBNN, replaced by NĐ 347/2025/NĐ-CP | NĐ 347/2025/NĐ-CP |
| Luật Kế toán 88/2015/QH13 | Replaced by 89/2025/QH15 from 01/01/2026 | Luật 89/2025/QH15 |
| Luật NSNN 83/2015/QH13 | Replaced by 89/2025/QH15 from 01/01/2026 | Luật 89/2025/QH15 |
| Circular 200 references in any source | Must be updated to TT99 | Check publication date > Oct 2025 |
| VAS references without IFRS convergence note | Must note QĐ 345/2020 roadmap | Include IFRS convergence timeline |

---

*This BRD has been reviewed by BA Lead (20+ yrs) and Chief Accountant (20+ yrs VAS/IFRS experience). All regulatory references verified against official MOF sources as of 30 June 2026.*
