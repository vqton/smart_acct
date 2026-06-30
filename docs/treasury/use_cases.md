# Treasury Module — Use Cases

**Date**: 2026-06-30
**Regulatory Basis**: TT 99/2025/TT-BTC, TT 157/2025/TT-BTC, ND 347/2025/NĐ-CP

---

## UC-TRS-01: Consolidated Cash Position

**Actor**: CFO, Treasurer
**Trigger**: Daily review / on-demand
**Pre**: Accounts synced
**Post**: Real-time position displayed

### Happy Path
1. User opens Treasury Dashboard
2. System aggregates: all CashAccount + BankAccount + CashInTransit
3. System classifies by: currency, entity, bank
4. Display: total liquidity, available vs. blocked
5. Show: 1-day change, 7-day trend

### Alternative
- Multi-entity: group rollup + per-entity drilldown
- Multi-currency: VND equivalent + original amounts
- Include KBNN deposits in consolidated view

### Exception
- Stale data (>24h since last sync) → warning
- Unreconciled bank diff flagged

### Rules
- Available = balance - blocked (margin, escrow, etc.)
- VND equivalent uses bank avg rate per TT 99 Điều 13

---

## UC-TRS-02: Cash Flow Forecasting

**Actor**: Treasurer, CFO
**Trigger**: Weekly / on-demand
**Pre**: AR aging, AP aging, payroll, loan schedule available
**Post**: 7/30/90-day forecast generated

### Happy Path
1. User selects horizon (7/30/90d) + scenario (best/base/worst)
2. System pulls: AR collections, AP payments, payroll, loans, tax, capex
3. Calculator: opening + inflows - outflows = closing
4. Flag: min balance breach (<threshold), surplus (>threshold)
5. Display: daily chart, cumulative position, alert list

### Alternative
- Scenario modeling: adjust assumptions (e.g., "20% customer delay")
- Manual override: add off-system items
- Budget-based: fallback if AR/AP data unavailable

### Exception
- Partial data: forecast runs; missing sources flagged
- Stale AR/AP data (>7d) → warning on forecast

### Rules
- Opening = actual cash position
- Forecast deviation >50% from actual → investigation flag
- Min cash threshold configurable per entity

---

## UC-TRS-03: Short-term Investment (TK 121, 128)

**Actor**: CFO, Treasurer
**Trigger**: Surplus cash / maturity / new opportunity
**Pre**: Treasury policy configured; approval limits set
**Post**: Investment recorded; GL posted

### Happy Path (Term Deposit TK 1281)
1. Surplus identified (UC-TRS-02)
2. Enter: amount, term, interest rate, maturity, counterparty
3. Validate: policy limits, counterparty approved
4. Approval workflow (if >threshold → CFO approve)
5. DR 1281 CR 112 (principal)
6. At maturity: DR 112 CR 1281 + DR 112 CR 515 (interest)
7. Auto-rollover if configured

### Happy Path (Trading Securities TK 121)
1. Purchase: DR 121 CR 112 (cost); fees → DR 635
2. Period-end: FV adjustment DR 121 CR 515 or DR 635 CR 121
3. Sale: DR 112 CR 121; diff → 515/635

### Alternative
- Early withdrawal: penalty → 635; pro-rated interest
- Partial maturity rollover

### Exception
- Counterparty downgraded below policy → mandatory divest alert
- Investment matures on non-business day → next day processing

### Rules
- Max % of cash per policy
- Max per counterparty per policy
- Min counterparty credit rating per policy
- Maturity > today

---

## UC-TRS-04: Debt Management (TK 341)

**Actor**: CFO, Treasurer
**Trigger**: New loan / payment due / refinancing
**Pre**: Loan agreement executed
**Post**: Loan recorded; schedule created; GL posted

### Happy Path
1. Record loan: type, principal, rate, drawdown, maturity, repayment
2. Drawdown: DR 112 CR 341
3. Auto-generate repayment schedule
4. Payment: DR 341 (principal) + DR 635 (interest) CR 112
5. Alert: 7/3/1 day before due

### Alternative
- Early repayment: penalty → 635; remaining schedule cancelled
- Refinancing: close old, create new; net to 112
- Floating rate: revalue at reset date
- Covenant tracking: DSCR, ICR, LTV

### Exception
- Overdue > grace period → escalation alert
- Covenant breach → CFO notification + action plan

### Rules
- Drawdown <= approved principal
- Payment must follow schedule
- Interest calc: actual/365 or 30/360 per agreement

---

## UC-TRS-05: KBNN Integration

**Actor**: Kế toán viên, Kế toán trưởng
**Trigger**: Budget allocation / payment request / reconciliation
**Pre**: Unit registered with KBNN; DVC account active
**Post**: Payment submitted; budget consumed

### Happy Path
1. Budget allocation from KBNN (TABMIS sync)
2. System records budget availability
3. Payment request: Giấy rút dự toán per ND 347 form
4. Internal approval: KTV → KTT → Thủ trưởng
5. Submit to KBNN via DVC API
6. KBNN processes (1 day per ND 347)
7. Status: approved/rejected
8. Dr Chi phí CR 112 (KBNN)

### Alternative
- Advance + clearance workflow
- ODA disbursement (special per ND 347)
- Budget transfer between items

### Exception
- Rejection: record reason; revise + resubmit
- Budget insufficient → payment blocked
- System unavailable → offline mode with batch upload

### Rules
- Budget balance must be sufficient
- Two-signature: KTT + Thủ trưởng per TT 157/2025
- Digital signature via VNeID
- Forms per ND 347 templates (Mẫu 01-07)

---

## UC-TRS-06: FX Exposure Monitoring

**Actor**: CFO, Treasurer
**Trigger**: Period-end / significant FX move / on-demand
**Pre**: FC accounts exist; rates configured
**Post**: Exposure report generated

### Happy Path
1. Aggregate all FC positions (cash, AR, AP, loans) by currency
2. Apply bank avg rate per TT 99
3. Net exposure = long - short per currency
4. Display by currency, entity, time bucket (1M/3M/6M/1Y)
5. Flag: positions > policy threshold
6. Revaluation entries: DR/CR 413

### Alternative
- Hedged vs. unhedged (if forward contracts exist)
- Sensitivity: VND +/- 1%/3%/5% → P&L impact

### Exception
- Rate source unavailable → use last available + flag
- Significant unrealized loss → mandatory CFO notification

### Rules
- Rate = bank avg transfer rate per TT 99 (not buying/selling)
- Period-end revaluation per VAS 10
- Unrealized vs. realized tracked separately

---

## UC-TRS-07: Intercompany Cash Management

**Actor**: Group Treasurer
**Trigger**: End of day / IC loan need / surplus identified
**Pre**: Multiple entities; IC agreements exist
**Post**: Cash sweeps executed; IC loans recorded

### Happy Path
1. EOD: each entity's cash position calculated
2. Surplus (>target) + deficit (<target) identified
3. Optimal sweep proposal generated
4. Treasurer approves
5. DR 112 (recipient) CR 112 (sender)
6. IC loan: DR 1368/CR 3368
7. Interest accrued per transfer pricing policy

### Alternative
- Zero-balancing: all surplus → master account
- Target-balancing: only excess above target
- Manual override: adjust amounts

### Exception
- Entity with deficit has no IC agreement → external loan suggested
- Cross-border: FCT withholding calculated
- Regulatory limit per entity breached

### Rules
- IC agreements must be executed
- Transfer pricing per OECD/VN regulations
- Minimum operating balance per entity
- Interest rate at arm's length

---

## UC-TRS-08: Treasury Dashboard & KPIs

**Actor**: CFO, CEO, Treasurer
**Trigger**: Daily / period-end / on-demand
**Pre**: All data sources connected
**Post**: Dashboard displayed

### KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Days Cash on Hand | 30-90d | Cash / avg daily opex |
| Cash Conversion Cycle | Industry benchmark | DSO + DIO - DPO |
| Current Ratio | >1.5x | Current assets / liabilities |
| Quick Ratio | >1.0x | (Cash + AR) / CL |
| DSO | <45d | Avg AR / Revenue * 365 |
| DPO | >60d | Avg AP / COGS * 365 |
| Forecast Accuracy | >80% | Actual / Forecast |
| Debt Service Coverage | >1.5x | EBITDA / Debt service |
| FX Exposure / Equity | <10% | Net FC / Equity |

### Happy Path
1. Open dashboard → all KPIs computed live
2. Color: green (ok), yellow (watch), red (breach)
3. Drill-down on any KPI for detail
4. Period comparison: MoM, YoY, vs. budget
5. Export: PDF, Excel

### Exception
- Data unavailable → "N/A" with reason
- KPI breach → auto-alert to manager

### Rules
- KPI targets configurable per entity
- Historical data retained 3 years (minimum)

---

## UC-TRS-09: Payment Factory

**Actor**: Treasurer, AP Clerk
**Trigger**: Payment run date / on-demand
**Pre**: Approved AP invoices; sufficient cash
**Post**: Batch file generated; GL posted

### Happy Path
1. Select criteria: due date range, supplier, currency
2. Aggregate: AP invoices + payroll + tax payments
3. Cash sufficiency check (UC-TRS-02)
4. Review payment proposal
5. Approve batch
6. Generate payment file (VNBC/MT103/CSV)
7. DR 331/334/333 CR 112
8. Status: sent to bank

### Alternative
- Partial payment: prioritize if cash insufficient
- Split payment: single supplier from multiple accounts

### Exception
- Bank reject → re-queue with reason
- Duplicate invoice → block payment

### Rules
- Same currency batch per bank file
- Min payment amount per bank
- Approval threshold per role

---

## UC-TRS-10: Bank Connectivity

**Actor**: System (automated)
**Trigger**: Scheduled / on-demand
**Pre**: Bank API credentials configured
**Post**: Bank data synced

### Happy Path
1. Connect to bank (EBanking XML/ISO 20022/API REST)
2. Fetch: balance, transactions, statements
3. Match to existing GL entries
4. Unmatched → flag for review
5. Auto-reconciliation proposal

### Alternative
- CSV/MT940 fallback (no API)
- Manual statement entry (no file)

### Exception
- Connection failure → retry 3x → alert IT
- Invalid credentials → lock + notify admin
- Transaction download timeout → partial data

### Security
- AES-256 encrypted credentials
- TLS 1.3 for bank connections
- IP whitelisting
- Full audit log
