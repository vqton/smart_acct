# ADR-001: General Ledger Module Architecture

## Status
Accepted

## Context
Need to implement a production-grade General Ledger (GL) module compliant with Vietnamese accounting regulations (Circular 99/2025/TT-BTC, Accounting Law 88/2015/QH13).

## Decision

### Architecture
- **Clean Architecture** with strict layer dependency: Domain -> Application -> Infrastructure -> Presentation
- **Domain-Driven Design** with aggregate roots, value objects, and domain events
- **CQRS** pattern for posting (Command) and reporting (Query) separation
- **Repository pattern** for data access abstraction
- **Unit of Work** for transaction management

### Key Patterns
1. **Journal Batch as Aggregate Root** - enforces debit=credit invariant
2. **Account as Aggregate Root** - maintains balance as derived state
3. **Posting Engine** - validates, updates balances, publishes events atomically
4. **Period/FiscalYear** - controls posting windows
5. **VoucherSeries** - guarantees sequential numbering
6. **Budget** - enforces spending limits

### Legal Compliance
- Chart of accounts follows Circular 99/2025/TT-BTC (effective Jan 1, 2026)
- Period locking prevents postings to closed periods
- Fiscal year close prevents any modification
- Audit trail records all changes immutably

## Consequences
- Straightforward to test (domain logic is framework-free)
- Easy to swap MariaDB/PostgreSQL via repository interface
- Event-driven integration with other modules (AP, AR, FA)

## References
- Circular 99/2025/TT-BTC: https://thuvienphapluat.vn (verified active)
- Accounting Law 88/2015/QH13 as amended by Law 56/2024/QH15
- Circular 133/2016/TT-BTC (SME regime, still active)
