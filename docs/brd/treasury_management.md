# Treasury Management Module — BRD (Quản trị Ngân quỹ)

**Version**: 1.0
**Date**: 2026-06-30
**Author**: BA Lead + Chief Accountant (20+ yrs)
**Regulatory Basis**: TT 99/2025/TT-BTC (eff. 01/01/2026), TT 157/2025/TT-BTC (KBNN), ND 347/2025/NĐ-CP (KBNN procedures), TT 200/2014/TT-BTC (replaced), TT 133/2016/TT-BTC, VAS 01/10/24, IAS 7/IFRS 9, Luat Ketoan 88/2015/QH13, ND 52/2024/ND-CP, Luat NSNN 89/2025/QH15 (eff. 01/01/2026)

---

## 1. PRODUCTION READINESS ASSESSMENT

**Verdict: NOT ready for production. Score: 0/5.**

| Layer | Status | Detail |
|-------|--------|--------|
| Cash module (TK 111) | ✅ Complete | UC-CASH-01 to UC-CASH-11, 111 tests |
| Bank module (TK 112) | ✅ 97% ready | Bank BRD v1.0, 55+ bank tests |
| **Treasury module** | ❌ **Missing** | No domain entities, no models, no repo, no use cases, no routes, no tests |
| KBNN integration | ❌ Missing | No connection to DVC KBNN portal |
| Cash flow forecasting | ❌ Missing | No forecasting logic |
| Liquidity management | ❌ Missing | No cash positioning |
| Debt management (TK 341) | ❌ Missing | No loan tracking |
| Investment mgmt (TK 121/128) | ❌ Missing | No investment tracking |
| Treasury dashboard | ❌ Missing | No KPIs or BI |
| Bank connectivity API | ❌ Missing | No direct bank API |
| Intercompany cash mgmt | ❌ Missing | No multi-entity support |
| FX risk management | ❌ Missing | No hedging tracking |

**Why not PROD**: Current code covers ONLY cash-on-hand (TK 111) and demand deposits (TK 112). Enterprise treasury management requires: (a) consolidated cash position across all accounts, (b) short-term cash flow forecasting, (c) KBNN integration for public sector units, (d) debt & investment tracking, (e) bank connectivity APIs, (f) FX risk management, (g) liquidity KPIs. Without these, running in PROD = blind cash management.

---

## 2. EXECUTIVE SUMMARY

### 2.1 What is Treasury Management?

Treasury Management (Quản trị Ngân quỹ) is the **strategic layer** above cash and banking operations. It answers:
- "How much cash do we have RIGHT NOW across all accounts?"
- "Will we have enough cash to pay suppliers next month?"
- "Should we invest surplus cash or repay loans?"
- "Are we exposed to FX risk?"
- "How efficient is our working capital?"

### 2.2 Scope

| In Scope | Out of Scope (Phase 2) |
|----------|----------------------|
| Consolidated cash position | L/C (Letter of Credit) management |
| Short-term cash flow forecasting (7/30/90 day) | Supply chain finance |
| Long-term cash flow forecasting (annual) | M&A treasury integration |
| Liquidity management & KPIs | Crypto/digital asset treasury |
| Debt management (TK 341) | Derivatives & hedging instruments |
| Investment management (TK 121, 128) | Credit rating monitoring |
| KBNN integration (public sector) | Global cash pooling |
| Bank connectivity (API) | In-house banking / netting |
| FX exposure monitoring | Commodity risk management |
| Intercompany cash management | ESG treasury reporting |
| Treasury dashboard & reporting | |
| Payment factory / batch payments | |

### 2.3 Relationship to Existing Modules

```
                    ┌─────────────────────────┐
                    │   TREASURY MODULE        │
                    │  (Quản trị Ngân quỹ)     │
                    └──────────┬──────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Cash Module │  │  Bank Module │  │  GL Module   │
    │  (TK 111)    │  │  (TK 112)    │  │  (Tong hop)  │
    └──────────────┘  └──────────────┘  └──────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
            ┌──────────────┐    ┌───────────────────┐
            │  AR Module   │    │  AP Module        │
            │  (TK 131)    │    │  (TK 331)         │
            └──────────────┘    └───────────────────┘
```

---

## 3. REGULATORY REFERENCES

| Regulation | Key Articles | Impact |
|------------|-------------|--------|
| **TT 99/2025/TT-BTC** (eff. 01/01/2026) | Điều 3, 11, 17; Phụ lục II TK 111/112/113/121/128/341 | TK system for all treasury accounts; mandatory internal control charter |
| **TT 157/2025/TT-BTC** (eff. 01/01/2026) | Điều 7, 9, 10 | KBNN account registration, 2-signature rule, reconciliation |
| **ND 347/2025/NĐ-CP** (eff. 01/01/2026) | Toàn bộ (15 Điều) | KBNN admin procedures, 84% paperwork reduction, digital-only |
| **TT 133/2016/TT-BTC** (effective for SMEs) | Điều 12, Phụ lục 2 | Simplified cash accounting (may still apply for SMEs in 2026) |
| **VAS 01** | Nguyên tắc cơ bản | Accrual, going concern, historical cost |
| **VAS 10** | Ảnh hưởng của việc thay đổi tỷ giá hối đoái | FX revaluation at period end |
| **VAS 24** | Báo cáo lưu chuyển tiền tệ | Cash flow statement classification |
| **IAS 7 / IFRS** | Cash equivalents, cash flow classification | IFRS alignment for dual-reporting |
| **IFRS 9** | Financial instruments, ECL | Impairment of financial assets |
| **Luat Ke toan 88/2015/QH13** | Điều 39 | Internal control systems |
| **Luat NSNN 89/2025/QH15** (eff. 01/01/2026) | Toàn bộ | State budget law — replaces 83/2015/QH13 |
| **ND 52/2024/ND-CP** | Cashless payments | E-payment integration standards |
| **Circular 23/2014/TT-NHNN** | Cheques | Cheque issuance, payment, endorsement |

### 3.1 Outdated Documents (Replaced/Revoked)

| Old Document | Replaced By | Effective |
|-------------|-------------|-----------|
| TT 200/2014/TT-BTC (Chế độ kế toán DN) | TT 99/2025/TT-BTC | 01/01/2026 |
| TT 18/2020/TT-BTC (KBNN account registration) | TT 157/2025/TT-BTC | 01/01/2026 |
| ND 11/2020/ND-CP (KBNN procedures) | ND 347/2025/ND-CP | 01/01/2026 |
| TT 324/2016/TT-BTC (Mục lục NSNN) | Incorporated into TT 157/2025 | 01/01/2026 |
| Luat NSNN 83/2015/QH13 | Luat NSNN 89/2025/QH15 | 01/01/2026 |

---

## 4. DOMAIN MODEL

### 4.1 Entities

```
TreasuryAccount (base):
  ├── CashAccount (TK 111) ← existing Cash module
  ├── BankAccount (TK 112) ← existing Bank module
  ├── CashInTransit (TK 113) ← new
  └── KBNNAccount (TK 112 at KBNN) ← new

Investment:
  ├── SecurityInvestment (TK 121)
  ├── HeldToMaturityInvestment (TK 128)
  │   ├── TermDeposit (1281)
  │   ├── Bond (1282)
  │   ├── Loan (1283)
  │   └── Other (1288)
  └── OtherInvestment (TK 228)

Debt:
  └── Loan (TK 341)
      ├── BankLoan
      ├── BondPayable
      └── IntercompanyLoan

CashFlowForecast:
  ├── ForecastLine
  └── Scenario (best/base/worst)

TreasuryPosition:
  ├── ConsolidatedBalance
  ├── LiquidityIndicator
  └── FXExposure

TreasuryPolicy:
  ├── ApprovalLimit
  ├── CounterpartyLimit
  └── InvestmentLimit
```

### 4.2 TK Mapping per TT 99/2025/TT-BTC

| TK | Name (TT 99) | Treasury Function |
|----|-------------|-------------------|
| 111 | Tiền mặt | Physical cash management |
| 112 | Tiền gửi không kỳ hạn | Bank account management |
| 113 | Tiền đang chuyển | Cash in transit tracking |
| 121 | Chứng khoán kinh doanh | Trading securities |
| 128 | Đầu tư nắm giữ đến ngày đáo hạn | HTM investments |
| 1281 | Tiền gửi có kỳ hạn | Term deposits |
| 1282 | Trái phiếu | Bonds held to maturity |
| 1283 | Cho vay | Loans receivable |
| 1288 | Đầu tư khác nắm giữ đến ngày đáo hạn | Other HTM |
| 221 | Đầu tư vào công ty con | Subsidiary investment |
| 222 | Đầu tư vào công ty liên doanh, liên kết | JV/associate investment |
| 228 | Đầu tư khác | Other investments |
| 341 | Vay và nợ thuê tài chính | Borrowings |
| 413 | Chênh lệch tỷ giá hối đoái | FX revaluation |
| 515 | Doanh thu hoạt động tài chính | Investment income |
| 635 | Chi phí tài chính | Finance costs |

---

## 5. USE CASES

### UC-TRS-01: Consolidated Cash Position

| Field | Value |
|-------|-------|
| **Actor** | CFO, Treasurer (Kế toán trưởng, Thủ quỹ) |
| **Trigger** | Daily/on-demand cash position review |
| **Preconditions** | Bank accounts synced; cash balances updated |
| **Postconditions** | Real-time consolidated position displayed |

**Happy Path:**
1. User opens Treasury Dashboard
2. System aggregates: all CashAccount balances + all BankAccount balances + CashInTransit
3. System classifies by: currency (VND, USD, EUR, JPY, GBP), by entity, by bank
4. System calculates: total liquidity, available cash, blocked cash
5. Display: current balance, 1-day change, 7-day trend

**Alternative Paths:**
- **Multi-entity**: Show consolidated group position + per-entity breakdown
- **Multi-currency**: Convert to VND at current rate; show original amounts
- **KBNN accounts**: Include KBNN deposits in consolidated view

**Validation:**
- Last sync timestamp must be < 24h old (warning if stale)
- Unreconciled bank differences flagged

---

### UC-TRS-02: Cash Flow Forecasting

| Field | Value |
|-------|-------|
| **Actor** | Treasurer, CFO |
| **Trigger** | Weekly forecast run; on-demand |
| **Preconditions** | AR aging, AP aging, payroll schedule, loan schedule available |
| **Postconditions** | 7/30/90-day forecast generated; alerts triggered |

**Happy Path:**
1. User selects forecast horizon (7/30/90 days) and scenario (best/base/worst)
2. System pulls:
   - Expected AR collections (from AR aging + AR forecast)
   - Expected AP payments (from AP aging + purchase orders)
   - Payroll date (from Payroll module)
   - Loan payments (from Loan schedule)
   - Tax payments (from Tax module)
   - Known Capex (from FA/AP)
3. System calculates: opening balance + inflows - outflows = closing balance
4. System flags: minimum balance breaches (< threshold), surplus > threshold
5. Display: daily cash flow chart, cumulative position, alerts

**Alternative Paths:**
- **Scenario modeling**: User adjusts assumptions (e.g., "what if 20% of customers delay payment")
- **Manual overrides**: User adds off-system expected inflows/outflows
- **Budget-based**: Use budget data if AR/AP not yet implemented

**Exception Paths:**
- **Missing data**: Forecast still runs with partial data; missing sources flagged
- **Stale AR/AP data**: Warning if > 7 days since last AR/AP update

**Validation Rules:**
- Opening balance must tie to actual cash position
- Forecast cannot exceed +- 50% of actual without trigger investigation flag
- Minimum cash threshold configurable per entity

---

### UC-TRS-03: Short-term Investment Management (TK 121, 128)

| Field | Value |
|-------|-------|
| **Actor** | CFO, Treasurer |
| **Trigger** | Surplus cash identified; investment maturity; new investment opportunity |
| **Preconditions** | Treasury policy configured; approval limits set |
| **Postconditions** | Investment recorded; GL entries posted; cash balance updated |

**Happy Path (Term Deposit - TK 1281):**
1. Surplus cash identified (from UC-TRS-02)
2. Treasurer selects investment type (Term deposit, Bond, etc.)
3. Enter: amount, term, interest rate, maturity date, bank/counterparty
4. System validates: within investment policy limits, counterparty approved
5. Approval workflow (if > threshold): send to CFO for approval
6. On approval: DR 1281 CR 112 — principal moved to term deposit
7. At maturity: DR 112 CR 1281 + DR 112 CR 515 (interest income)
8. Automatic rollover if configured

**Happy Path (Trading Securities - TK 121):**
1. Purchase: DR 121 CR 112 (at cost); transaction fees to 635
2. Period-end: fair value adjustment (DR 121 CR 515 or DR 635 CR 121)
3. Sale: DR 112 CR 121; gain/loss to 515/635

**Alternative Paths:**
- **Early withdrawal**: Penalty recorded to 635; pro-rated interest adjusted
- **Partial maturity rollover**: Only part rolled; remainder credited to 112

**Validation Rules:**
- Investment policy limits enforced (max % of cash, max per counterparty, min credit rating)
- Maturity date must be > today's date
- Interest rate must be positive (zero allowed for demand deposits)
- Counterparty must be in approved list

---

### UC-TRS-04: Debt/Loan Management (TK 341)

| Field | Value |
|-------|-------|
| **Actor** | CFO, Treasurer |
| **Trigger** | New loan; payment due; refinancing |
| **Preconditions** | Loan agreement executed |
| **Postconditions** | Loan recorded; payment schedule created; GL entries posted |

**Happy Path:**
1. Treasurer records new loan: type (bank/ bond/ intercompany), principal, interest rate, drawdown date, maturity, repayment schedule
2. On drawdown: DR 112 CR 341
3. System generates repayment schedule (monthly/quarterly/ bullet)
4. At each payment: DR 341 (principal portion) + DR 635 (interest) CR 112
5. System alerts: upcoming payment 7/3/1 day before due

**Alternative Paths:**
- **Early repayment**: Prepayment penalty recorded; remaining schedule cancelled
- **Refinancing**: Old loan closed; new loan created; net impact to 112
- **Interest rate change**: Floating rate revaluation at reset date
- **Covenant tracking**: DSCR, ICR, LTV ratios calculated and monitored

**Validation Rules:**
- Drawdown amount cannot exceed approved principal
- Repayment dates must follow schedule
- Overdue payment flags after grace period

---

### UC-TRS-05: KBNN Integration (Public Sector)

| Field | Value |
|-------|-------|
| **Actor** | Kế toán viên, Kế toán trưởng (đơn vị SN) |
| **Trigger** | Budget allocation; payment request; reconciliation |
| **Preconditions** | Unit registered with KBNN; DVC account active |
| **Postconditions** | Payment submitted; budget consumed |

**Happy Path:**
1. Unit receives budget allocation from KBNN (via TABMIS integration)
2. System records budget availability
3. Unit prepares payment request (Giấy rút dự toán NSNN — Form per ND 347)
4. Internal approval: Kế toán viên → Kế toán trưởng → Thủ trưởng đơn vị
5. Submit to KBNN via DVC portal (API integration)
6. KBNN processes (1 day per ND 347: routine expenditure)
7. System receives status update: approved/rejected
8. On approval: DR Chi phí CR 112 (KBNN account)

**Alternative Paths:**
- **Rejection**: System records rejection reason; unit revises and resubmits
- **Advance/clearance**: Advance drawn; clearance documents submitted later
- **ODA disbursement**: Special ODA procedures per ND 347

**Validation Rules:**
- Budget balance must be sufficient
- Documents must match KBNN format per ND 347
- Two-signature rule per TT 157/2025 (KTT + Thủ trưởng)
- Digital signatures via VNeID or CA-certified

---

### UC-TRS-06: FX Exposure Monitoring

| Field | Value |
|-------|-------|
| **Actor** | CFO, Treasurer |
| **Trigger** | Period-end; significant FX movement; on-demand |
| **Preconditions** | Foreign currency accounts exist; FX rates configured |
| **Postconditions** | FX exposure report generated; hedging recommendations |

**Happy Path:**
1. System aggregates all FC positions (cash, AR, AP, loans) by currency
2. Apply current exchange rate (bank avg rate per TT 99 Điều 13)
3. Calculate: net exposure per currency (long/short)
4. Display: exposure by currency, by entity, by time bucket (1M/3M/6M/1Y)
5. Flag: positions exceeding policy thresholds
6. Generate FX revaluation entries: DR/CR 413 (FX difference)

**Alternative Paths:**
- **Hedging**: If forward contract exists, show hedged vs. unhedged exposure
- **Sensitivity analysis**: What if VND weakens/strengthens by 1%/3%/5%?

**Validation Rules:**
- FX rate source must be verifiable (bank avg rate per TT 99)
- Revaluation entries generated at period-end per VAS 10
- Unrealized FX gains/losses tracked separately from realized

---

### UC-TRS-07: Intercompany Cash Management

| Field | Value |
|-------|-------|
| **Actor** | Group Treasurer |
| **Trigger** | End of day; intercompany loan need; surplus identified |
| **Preconditions** | Multiple entities configured; intercompany agreements exist |
| **Postconditions** | Cash sweeps executed; intercompany loans recorded |

**Happy Path:**
1. End-of-day: system calculates each entity's cash position
2. Identify: entities with surplus (> target balance), entities with deficit (< target)
3. Generate: optimal cash sweep proposal
4. Treasurer reviews and approves
5. System executes: DR 112 (receiving entity) CR 112 (sending entity)
6. Intercompany loan recorded: DR 1368/CR 3368
7. Interest calculated and accrued per transfer pricing policy

**Alternative Paths:**
- **Zero-balancing**: All surplus swept to master account daily
- **Target balancing**: Only cash above target balance swept
- **Manual override**: Treasurer adjusts sweep amounts

**Validation Rules:**
- Intercompany agreements must be executed
- Transfer pricing must follow OECD/ Vietnamese regulations
- Tax implications (FCT for cross-border intercompany loans)
- Entity cash cannot go below minimum operating balance

---

### UC-TRS-08: Treasury Dashboard & KPIs

| Field | Value |
|-------|-------|
| **Actor** | CFO, CEO, Treasurer |
| **Trigger** | Daily review; period-end; on-demand |
| **Preconditions** | All treasury data sources connected |
| **Postconditions** | Dashboard displayed; alerts generated |

**KPIs:**
| KPI | Formula | Target | Frequency |
|-----|---------|--------|-----------|
| Cash Position | Total cash + bank balances | > min threshold | Daily |
| Days Cash on Hand | Cash / Avg daily opex | 30-90 days | Daily |
| Cash Conversion Cycle | DSO + DIO - DPO | Industry benchmark | Monthly |
| Current Ratio | Current assets / Current liabilities | > 1.5x | Monthly |
| Quick Ratio | (Cash + AR) / Current liabilities | > 1.0x | Monthly |
| DSO | (Avg AR / Revenue) * 365 | < 45 days | Monthly |
| DPO | (Avg AP / COGS) * 365 | > 60 days | Monthly |
| Liquidity Coverage | Cash inflows 30d / Cash outflows 30d | > 1.0x | Weekly |
| FX Exposure | Net FC position / Equity | < 10% | Weekly |
| Investment Yield | Interest income / Avg investments | Benchmark | Monthly |
| Debt Service Coverage | EBITDA / Debt service | > 1.5x | Quarterly |
| Forecast Accuracy | Actual cash flow / Forecast | > 80% | Monthly |

**Happy Path:**
1. User opens dashboard
2. System computes all KPIs from live data
3. Color coding: green (on target), yellow (watch), red (breach)
4. Drill-down: click any KPI for detail
5. Period comparison: vs. last month, vs. budget, vs. prior year
6. Export: PDF, Excel

**Exception Paths:**
- **Data unavailable**: KPI marked as "N/A" with reason
- **KPI breach**: Automated alert to responsible manager

---

### UC-TRS-09: Payment Factory / Batch Payments

| Field | Value |
|-------|-------|
| **Actor** | Treasurer, AP Clerk |
| **Trigger** | Payment run date; on-demand |
| **Preconditions** | Approved AP invoices; sufficient cash |
| **Postconditions** | Batch payment file generated; GL posted |

**Happy Path:**
1. Treasurer selects payment run criteria (due date range, supplier group, currency)
2. System aggregates approved AP invoices + Payroll + Tax payments
3. System checks cash sufficiency (UC-TRS-02)
4. Treasurer reviews payment proposal
5. Treasurer approves batch
6. System generates: payment file (VNBC/MT103/CSV) per bank format
7. System posts: DR 331/334/333 CR 112
8. Status: sent to bank for execution

**Alternative Paths:**
- **Partial payment**: If cash insufficient, prioritize by supplier rank
- **Split payment**: Single supplier paid from multiple accounts

**Exception Paths:**
- **Bank reject**: System records rejection; payment re-queued
- **Duplicate prevention**: Check supplier invoice number before payment

---

### UC-TRS-10: Bank Connectivity & API Integration

| Field | Value |
|-------|-------|
| **Actor** | System (automated) |
| **Trigger** | Scheduled (hourly/daily); on-demand |
| **Preconditions** | Bank API credentials configured |
| **Postconditions** | Bank data synced; accounts reconciled |

**Supported Banks (Phase 1):**
- Vietcombank (VCB)
- VietinBank (eFAST X-Mate)
- BIDV
- Techcombank (F@st)
- MB Bank (MB MMS)
- ACB (ACB Online)

**Happy Path:**
1. System connects to bank API (EBanking XML/ISO 20022/API REST)
2. Fetch: account balance, transaction history, statements
3. System matches imported transactions to existing GL entries
4. Unmatched transactions flagged for review
5. Automatic reconciliation proposal generated

**Alternative Paths:**
- **CSV/MT940 fallback**: If no API, parse bank statement file
- **Manual entry**: If neither API nor file, manual statement entry

**Security:**
- API credentials encrypted at rest (AES-256)
- TLS 1.3 for all bank connections
- IP whitelisting per bank requirement
- Audit log of all bank data access

---

## 6. DATA FLOWS

### 6.1 Cash Flow Forecasting Flow

```
[AR Module] ── Expected collections ──┐
[AP Module] ── Expected payments ─────┤
[Payroll] ──── Payroll date ──────────┤
[Tax Module] ─ Tax payment dates ─────┤
[Loan Sched] ─ Loan payments ─────────┤
[Manual] ───── Manual entries ────────┤
                                       ▼
                              ┌─────────────────┐
                              │ Forecast Engine  │
                              │ (Scenario calc)  │
                              └────────┬────────┘
                                       ▼
                              ┌─────────────────┐
                              │ 7/30/90 day      │
                              │ Forecast Report  │
                              └─────────────────┘
                                       │
                              ┌────────┴────────┐
                              ▼                 ▼
                      ⚠️ Alert if        ✅ OK — no alert
                      breach threshold
```

### 6.2 KBNN Payment Flow (ND 347/2025)

```
[Unit ERP] ─── Giấy rút dự toán ──→ [DVC KBNN Portal]
                                          │
                                          ▼
                                  KBNN Processing
                                  (1 day — routine)
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                         Approved                 Rejected
                              │                       │
                              ▼                       ▼
                    ┌────────────────┐      ┌────────────────┐
                    │  DR Chi phí    │      │  Return to     │
                    │  CR 112(KBNN)  │      │  unit for fix  │
                    └────────────────┘      └────────────────┘
```

### 6.3 Intercompany Cash Sweep Flow

```
                    Entity A (surplus)
                           │
                    ┌──────┴──────┐
                    │  Excess VND │
                    │  +500M      │
                    └──────┬──────┘
                           │ Sweep instruction
                           ▼
                    ┌──────────────┐
                    │ Master Acct  │
                    │ (HoldCo)     │
                    └──────┬──────┘
                           │ Allocate
                           ▼
                    Entity B (deficit)
                    ┌──────────────┐
                    │  Short VND   │
                    │  -300M       │
                    └──────────────┘
                    
Journal: DR 1368(A) CR 112(A) [sweep out]
         DR 112(B) CR 3368(B) [sweep in]
```

---

## 7. WORKFLOWS

### 7.1 Treasury Daily Cycle

```
09:00 — Bank connectivity sync (overnight transactions)
09:30 — Cash position report generated
10:00 — Payment run (if scheduled)
11:00 — KBNN submission cut-off
14:00 — FX rate check + exposure update
15:00 — Cash forecast update (intraday adjustments)
16:00 — End-of-day cash position
17:00 — Intercompany sweep (if configured)
```

### 7.2 Monthly Treasury Close

```
Day 1-3:  ── Bank reconciliation (all accounts)
Day 3-5:  ── KBNN reconciliation (if applicable)
Day 5-7:  ── FX revaluation (VAS 10/TT 99)
Day 7-10: ── Investment revaluation (FV changes)
Day 10:   ── Treasury dashboard + KPI report
Day 10:   ── Cash flow forecast for next month
```

---

## 8. TEMPLATES

### 8.1 ND 347/2025 Forms (via KBNN DVC)

| Form | Code | Use Case |
|------|------|----------|
| Giấy rút dự toán NSNN | Mẫu 01/ND347 | Budget drawdown |
| Giấy nộp NSNN | Mẫu 02/ND347 | Tax/budget payment |
| Bảng kê nộp NSNN | Mẫu 03/ND347 | Batch payment list |
| Giấy đề nghị thanh toán | Mẫu 04/ND347 | Payment request |
| Cam kết chi NSNN | Mẫu 05/ND347 | Commitment (abolished per ND347) |
| Giấy đề nghị tạm ứng | Mẫu 06/ND347 | Advance request |
| Giấy thanh toán tạm ứng | Mẫu 07/ND347 | Advance clearance |

### 8.2 Treasury Report Templates

| Report | Frequency | Audience |
|--------|-----------|----------|
| Daily Cash Position | Daily | CFO, Treasurer |
| Weekly Cash Forecast | Weekly | CFO |
| Monthly Treasury Report | Monthly | CFO, Board |
| Investment Portfolio | Monthly | CFO |
| Debt Schedule | Monthly | CFO |
| FX Exposure Report | Weekly | CFO, Treasurer |
| KBNN Transaction Log | Monthly | Kế toán trưởng |
| Intercompany Loan Statement | Monthly | Group Treasurer |

---

## 9. IMPLEMENTATION PLAN

### Phase 0: Foundation (Week 1-3)
- [ ] Domain entities (treasury.py): TreasuryAccount, CashFlowForecast, ForecastLine, TreasuryPosition, Investment, Loan, IntercompanyLoan, FXExposure
- [ ] SQLAlchemy models (treasury_models.py): 8-10 tables
- [ ] Alembic migration: `3fa4b5c6d7e8`
- [ ] Repository (treasury_repository.py): CRUD + aggregation queries

### Phase 1: Core Treasury Operations (Week 4-6)
- [ ] UC-TRS-01: Consolidated cash position
- [ ] UC-TRS-02: Cash flow forecasting (basic)
- [ ] UC-TRS-08: Treasury dashboard
- [ ] Routes + serializers
- [ ] Tests: 40+ domain + integration

### Phase 2: Investments & Debt (Week 7-9)
- [ ] UC-TRS-03: Investment management
- [ ] UC-TRS-04: Debt management
- [ ] UC-TRS-06: FX exposure monitoring
- [ ] GL integration (auto-posting)
- [ ] Tests: 30+

### Phase 3: KBNN & Intercompany (Week 10-12)
- [ ] UC-TRS-05: KBNN integration
- [ ] UC-TRS-07: Intercompany cash management
- [ ] UC-TRS-09: Payment factory
- [ ] UC-TRS-10: Bank connectivity API
- [ ] Tests: 30+

**Total estimated tests**: 100+ (40 domain + 60 integration)
**Total routes**: 25+ endpoints under `/api/v1/treasury/*`

---

## 10. RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bank API changes | High | Adapter pattern; abstraction layer per bank |
| KBNN regulatory changes | Medium | Parameterized forms; configurable rules |
| Cash forecast accuracy < 50% | High | Ensemble approach (statistical + driver-based) |
| FX volatility | Medium | Real-time rate feeds; automated alerts |
| Intercompany tax implications | High | FCT withholding calc; transfer pricing docs |
| Data latency (stale positions) | Medium | Last-sync timestamps; stale-data warnings |

---

## 11. SUCCESS CRITERIA

- [ ] Consolidated cash position refreshable within 5 seconds
- [ ] Forecast accuracy > 75% after 3 months of training
- [ ] KBNN integration: 100% of ND 347 procedures supported
- [ ] Bank connectivity: top 5 VN banks supported via API
- [ ] All treasury GL entries auto-posted (zero manual entry)
- [ ] Treasury close within 5 business days of month-end
- [ ] All 100+ tests passing
- [ ] Audit trail for every treasury transaction

---

## 12. OPEN QUESTIONS

1. KBNN DVC Gateway API — is there a documented API or only web portal?
2. Which bank APIs are available for Vietnamese banks in 2026?
3. Cash flow forecast — statistical (moving avg) vs. driver-based (AR/AP) vs. both?
4. Intercompany — zero-balancing or target-balancing as default?
5. Payment factory — batch file format: VNBC, MT103, ISO 20022, or bank-specific?
6. FX hedging — forward contracts to Phase 2 or Phase 1 basic?
7. Multi-currency — real-time rate source? (SBV rate vs. bank rate)
