# ADR-003: Chart of Accounts Design

## Status
Accepted

## Context
Must support the standard VN chart of accounts (Circular 99/2025/TT-BTC) while allowing enterprise customization.

## Decision

### Account Code Structure
- 1-4 digit numeric codes
- Class 1: Short-term assets (1xxx)
- Class 2: Long-term assets (2xxx)
- Class 3: Liabilities (3xxx)
- Class 4: Equity (4xxx)
- Class 5: Revenue (5xxx)
- Class 6: Cost of goods sold (6xxx)
- Class 7: Operating expenses (7xxx)
- Class 8: Other income/expenses (8xxx)
- Class 9: Manufacturing (9xxx)

### Account Types
- **Control accounts** (1-3 digit codes) - cannot post directly, used for hierarchy
- **Detail accounts** (4 digit codes) - can post transactions

### Categories
Accounts grouped by `AccountCategory` for financial statement mapping:
- Short/Long term asset, liability
- Equity, Revenue, Operating expense, etc.

### Nature
Each account has a natural balance:
- **Debit nature**: Assets, Expenses
- **Credit nature**: Liabilities, Equity, Revenue

## Seed Data
- ~80 standard accounts provided in seed script
- Enterprises can add custom accounts under existing categories

## References
- Circular 99/2025/TT-BTC Article 14-18 (Account system)
- Circular 200/2014/TT-BTC (partially superseded, some SOE equitization rules remain)
