import { DomainEvent } from "../../shared/domain-event.js";

export class PayrollGroupCreated implements DomainEvent {
  readonly eventName = "PayrollGroupCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollGroupUpdated implements DomainEvent {
  readonly eventName = "PayrollGroupUpdated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class SalaryComponentCreated implements DomainEvent {
  readonly eventName = "SalaryComponentCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class EmployeePayrollCreated implements DomainEvent {
  readonly eventName = "EmployeePayrollCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class EmployeePayrollUpdated implements DomainEvent {
  readonly eventName = "EmployeePayrollUpdated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class EmployeePayrollTerminated implements DomainEvent {
  readonly eventName = "EmployeePayrollTerminated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollRunCreated implements DomainEvent {
  readonly eventName = "PayrollRunCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollRunCalculated implements DomainEvent {
  readonly eventName = "PayrollRunCalculated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollRunApproved implements DomainEvent {
  readonly eventName = "PayrollRunApproved";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollRunPosted implements DomainEvent {
  readonly eventName = "PayrollRunPosted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollRunPaid implements DomainEvent {
  readonly eventName = "PayrollRunPaid";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollRunReversed implements DomainEvent {
  readonly eventName = "PayrollRunReversed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollLineCalculated implements DomainEvent {
  readonly eventName = "PayrollLineCalculated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollPaymentCreated implements DomainEvent {
  readonly eventName = "PayrollPaymentCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollPaymentConfirmed implements DomainEvent {
  readonly eventName = "PayrollPaymentConfirmed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class PayrollJournalCreated implements DomainEvent {
  readonly eventName = "PayrollJournalCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class InsuranceRateCreated implements DomainEvent {
  readonly eventName = "InsuranceRateCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class TaxBracketCreated implements DomainEvent {
  readonly eventName = "TaxBracketCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}
