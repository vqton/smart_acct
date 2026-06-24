import { DomainEvent } from "../../shared/domain-event.js";

export class ReportDefinitionCreated implements DomainEvent {
  readonly eventName = "ReportDefinitionCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ReportDefinitionActivated implements DomainEvent {
  readonly eventName = "ReportDefinitionActivated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ReportInstanceGenerated implements DomainEvent {
  readonly eventName = "ReportInstanceGenerated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ReportInstanceApproved implements DomainEvent {
  readonly eventName = "ReportInstanceApproved";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ConsolidationRunStarted implements DomainEvent {
  readonly eventName = "ConsolidationRunStarted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ConsolidationRunCompleted implements DomainEvent {
  readonly eventName = "ConsolidationRunCompleted";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class ConsolidationEntryCreated implements DomainEvent {
  readonly eventName = "ConsolidationEntryCreated";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}
