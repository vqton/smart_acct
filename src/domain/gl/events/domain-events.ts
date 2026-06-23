import { DomainEvent } from "../../../shared/domain-event.js";

export class VoucherCreated implements DomainEvent {
  readonly eventName = "VoucherCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class VoucherSubmitted implements DomainEvent {
  readonly eventName = "VoucherSubmitted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class VoucherApproved implements DomainEvent {
  readonly eventName = "VoucherApproved";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class VoucherRejected implements DomainEvent {
  readonly eventName = "VoucherRejected";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class VoucherCancelled implements DomainEvent {
  readonly eventName = "VoucherCancelled";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PostingStarted implements DomainEvent {
  readonly eventName = "PostingStarted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PostingCompleted implements DomainEvent {
  readonly eventName = "PostingCompleted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PostingFailed implements DomainEvent {
  readonly eventName = "PostingFailed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PostingRolledBack implements DomainEvent {
  readonly eventName = "PostingRolledBack";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class LedgerUpdated implements DomainEvent {
  readonly eventName = "LedgerUpdated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class BalanceUpdated implements DomainEvent {
  readonly eventName = "BalanceUpdated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class TrialBalanceUpdated implements DomainEvent {
  readonly eventName = "TrialBalanceUpdated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ExchangeDifferenceCalculated implements DomainEvent {
  readonly eventName = "ExchangeDifferenceCalculated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class BudgetConsumed implements DomainEvent {
  readonly eventName = "BudgetConsumed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PeriodClosed implements DomainEvent {
  readonly eventName = "PeriodClosed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PeriodReopened implements DomainEvent {
  readonly eventName = "PeriodReopened";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class YearClosed implements DomainEvent {
  readonly eventName = "YearClosed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class JournalReversed implements DomainEvent {
  readonly eventName = "JournalReversed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class AuditRecorded implements DomainEvent {
  readonly eventName = "AuditRecorded";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class IdempotencyChecked implements DomainEvent {
  readonly eventName = "IdempotencyChecked";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class SequenceNumberGenerated implements DomainEvent {
  readonly eventName = "SequenceNumberGenerated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}
