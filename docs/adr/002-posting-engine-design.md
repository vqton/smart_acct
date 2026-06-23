# ADR-002: Posting Engine Design

## Status
Accepted

## Context
Journal posting is the most critical operation in a GL system. Must be atomic, auditable, and performant.

## Decision

### Posting Flow
1. **Validate** - Check accounts active/posting, period open, debit=credit
2. **Begin transaction** (Unit of Work)
3. **Update account balances** - Debit-nature: balance += debit - credit; Credit-nature: balance += credit - debit
4. **Update batch status** -> Posted
5. **Publish domain events** -> JournalBatchPosted
6. **Commit transaction**

### Idempotency
- Each batch has unique batch_number (via VoucherSeries)
- Posting checks batch status before proceeding
- Duplicate posting fails at status check

### Reversal
- Reverse batches swap debit/credit on all lines
- Reverse requires an open period
- Original batch marked as Reversed

### Batch Posting
- Posts batches in sequence
- Each batch is individually atomic
- Failure in one batch does not roll back others

## Consequences
- Single-threaded per-batch atomicity
- Balance updates are simple arithmetic (not recalculated from scratch)
- Reversal creates new batch (audit trail preserved)

## Performance Targets
- <100ms per single batch post
- <5s for batch posting of 1000 batches
- Support 1M+ journal lines per fiscal year
