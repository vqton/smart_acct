# ADR-004: Database Partitioning Strategy

## Status
Proposed

## Context
Enterprise GL systems handle millions of journal entries. Need strategy for performance at scale.

## Decision

### Partitioning
- `journal_entry_lines` partitioned by RANGE on posting_date (yearly)
- `journal_batches` indexed by period_id, status, posting_date
- `accounts` indexed by code, parent_id

### Index Strategy
```sql
-- Core query indexes
journal_entry_lines(batch_id, account_id)     -- GL listing
journal_batches(status, period_id)             -- Period closing
journal_batches(created_at, posted_at)         -- Posting performance
accounts(code)                                 -- COA lookup
accounts(parent_id)                            -- Hierarchy traversal
```

### Archival
- Fiscal year closing archives data
- Read replicas for reporting queries

## Consequences
- Partition pruning speeds up period-end queries
- Index overhead manageable for <10M rows/year
- Archive strategy needed for >5 years retention (Accounting Law Art. 13: 5 years)
