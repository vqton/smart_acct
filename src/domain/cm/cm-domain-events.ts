import { DomainEvent } from "../../shared/domain-event.js";

export class CashBoxOpened implements DomainEvent {
  readonly eventName = "CashBoxOpened";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashBoxClosed implements DomainEvent {
  readonly eventName = "CashBoxClosed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashBoxBalanceChanged implements DomainEvent {
  readonly eventName = "CashBoxBalanceChanged";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashSessionOpened implements DomainEvent {
  readonly eventName = "CashSessionOpened";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashSessionClosed implements DomainEvent {
  readonly eventName = "CashSessionClosed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashSessionDiscrepancyFound implements DomainEvent {
  readonly eventName = "CashSessionDiscrepancyFound";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashReceiptCreated implements DomainEvent {
  readonly eventName = "CashReceiptCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashReceiptPosted implements DomainEvent {
  readonly eventName = "CashReceiptPosted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashReceiptReversed implements DomainEvent {
  readonly eventName = "CashReceiptReversed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashPaymentCreated implements DomainEvent {
  readonly eventName = "CashPaymentCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashPaymentPosted implements DomainEvent {
  readonly eventName = "CashPaymentPosted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashPaymentReversed implements DomainEvent {
  readonly eventName = "CashPaymentReversed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashAdvanceDisbursed implements DomainEvent {
  readonly eventName = "CashAdvanceDisbursed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class AdvanceSettled implements DomainEvent {
  readonly eventName = "AdvanceSettled";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class CashTransferCompleted implements DomainEvent {
  readonly eventName = "CashTransferCompleted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class BankTransferCompleted implements DomainEvent {
  readonly eventName = "BankTransferCompleted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class BankStatementReconciled implements DomainEvent {
  readonly eventName = "BankStatementReconciled";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ChequeIssued implements DomainEvent {
  readonly eventName = "ChequeIssued";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ChequeCleared implements DomainEvent {
  readonly eventName = "ChequeCleared";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ChequeReturned implements DomainEvent {
  readonly eventName = "ChequeReturned";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PettyCashReplenished implements DomainEvent {
  readonly eventName = "PettyCashReplenished";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}
