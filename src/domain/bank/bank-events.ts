import { DomainEvent } from "../../shared/domain-event.js";

export class BankCreated implements DomainEvent {
  readonly eventName = "BankCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BankUpdated implements DomainEvent {
  readonly eventName = "BankUpdated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BankDeactivated implements DomainEvent {
  readonly eventName = "BankDeactivated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BankAccountOpened implements DomainEvent {
  readonly eventName = "BankAccountOpened";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BankAccountClosed implements DomainEvent {
  readonly eventName = "BankAccountClosed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BankAccountSuspended implements DomainEvent {
  readonly eventName = "BankAccountSuspended";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BankAccountActivated implements DomainEvent {
  readonly eventName = "BankAccountActivated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class BankAccountBalanceChanged implements DomainEvent {
  readonly eventName = "BankAccountBalanceChanged";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class TransactionInitiated implements DomainEvent {
  readonly eventName = "TransactionInitiated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class TransactionAuthorized implements DomainEvent {
  readonly eventName = "TransactionAuthorized";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class TransactionExecuted implements DomainEvent {
  readonly eventName = "TransactionExecuted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class TransactionCompleted implements DomainEvent {
  readonly eventName = "TransactionCompleted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class TransactionFailed implements DomainEvent {
  readonly eventName = "TransactionFailed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class TransactionReversed implements DomainEvent {
  readonly eventName = "TransactionReversed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class StatementImported implements DomainEvent {
  readonly eventName = "StatementImported";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class StatementBalanceValidated implements DomainEvent {
  readonly eventName = "StatementBalanceValidated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReconciliationCreated implements DomainEvent {
  readonly eventName = "ReconciliationCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReconciliationMatched implements DomainEvent {
  readonly eventName = "ReconciliationMatched";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReconciliationApproved implements DomainEvent {
  readonly eventName = "ReconciliationApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PaymentRequestCreated implements DomainEvent {
  readonly eventName = "PaymentRequestCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PaymentRequestApproved implements DomainEvent {
  readonly eventName = "PaymentRequestApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PaymentBatchReleased implements DomainEvent {
  readonly eventName = "PaymentBatchReleased";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class FXRevaluationPosted implements DomainEvent {
  readonly eventName = "FXRevaluationPosted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CashPositionUpdated implements DomainEvent {
  readonly eventName = "CashPositionUpdated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class GLJournalPosted implements DomainEvent {
  readonly eventName = "GLJournalPosted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
