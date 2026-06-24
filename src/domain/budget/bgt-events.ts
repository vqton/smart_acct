export abstract class BgtDomainEvent {
  abstract readonly eventName: string;
  readonly occurredAt: Date = new Date();
  readonly eventId: string;

  constructor() { this.eventId = crypto.randomUUID(); }
}

// ─── Budget Plan Events ───────────────────────────────────────────────────────

export class BgtBudgetPlanCreated extends BgtDomainEvent {
  readonly eventName = "BgtBudgetPlanCreated";
  constructor(
    public readonly budgetPlanId: string,
    public readonly code: string,
    public readonly name: string,
    public readonly budgetType: string,
    public readonly fiscalYearId: string,
  ) { super(); }
}

export class BgtBudgetPlanSubmitted extends BgtDomainEvent {
  readonly eventName = "BgtBudgetPlanSubmitted";
  constructor(
    public readonly budgetPlanId: string,
    public readonly submittedById: string,
  ) { super(); }
}

export class BgtBudgetPlanApproved extends BgtDomainEvent {
  readonly eventName = "BgtBudgetPlanApproved";
  constructor(
    public readonly budgetPlanId: string,
    public readonly approvedById: string,
    public readonly totalAmount: number,
  ) { super(); }
}

export class BgtBudgetPlanRejected extends BgtDomainEvent {
  readonly eventName = "BgtBudgetPlanRejected";
  constructor(
    public readonly budgetPlanId: string,
    public readonly rejectedById: string,
    public readonly reason: string,
  ) { super(); }
}

export class BgtBudgetPlanPublished extends BgtDomainEvent {
  readonly eventName = "BgtBudgetPlanPublished";
  constructor(
    public readonly budgetPlanId: string,
    public readonly publishedById: string,
  ) { super(); }
}

export class BgtBudgetPlanActivated extends BgtDomainEvent {
  readonly eventName = "BgtBudgetPlanActivated";
  constructor(public readonly budgetPlanId: string) { super(); }
}

export class BgtBudgetPlanFrozen extends BgtDomainEvent {
  readonly eventName = "BgtBudgetPlanFrozen";
  constructor(
    public readonly budgetPlanId: string,
    public readonly frozenById: string,
  ) { super(); }
}

export class BgtBudgetPlanClosed extends BgtDomainEvent {
  readonly eventName = "BgtBudgetPlanClosed";
  constructor(
    public readonly budgetPlanId: string,
    public readonly closedById: string,
  ) { super(); }
}

// ─── Budget Version Events ────────────────────────────────────────────────────

export class BgtBudgetVersionCreated extends BgtDomainEvent {
  readonly eventName = "BgtBudgetVersionCreated";
  constructor(
    public readonly budgetPlanId: string,
    public readonly versionId: string,
    public readonly versionNumber: number,
  ) { super(); }
}

export class BgtBudgetVersionApproved extends BgtDomainEvent {
  readonly eventName = "BgtBudgetVersionApproved";
  constructor(
    public readonly versionId: string,
    public readonly budgetPlanId: string,
    public readonly approvedById: string,
  ) { super(); }
}

export class BgtBudgetVersionFrozen extends BgtDomainEvent {
  readonly eventName = "BgtBudgetVersionFrozen";
  constructor(
    public readonly versionId: string,
    public readonly budgetPlanId: string,
  ) { super(); }
}

// ─── Budget Transfer Events ───────────────────────────────────────────────────

export class BgtBudgetTransferCreated extends BgtDomainEvent {
  readonly eventName = "BgtBudgetTransferCreated";
  constructor(
    public readonly transferId: string,
    public readonly sourceBudgetPlanId: string,
    public readonly targetBudgetPlanId: string,
    public readonly totalAmount: number,
  ) { super(); }
}

export class BgtBudgetTransferCompleted extends BgtDomainEvent {
  readonly eventName = "BgtBudgetTransferCompleted";
  constructor(
    public readonly transferId: string,
    public readonly sourceBudgetPlanId: string,
    public readonly targetBudgetPlanId: string,
  ) { super(); }
}

// ─── Budget Reservation Events ────────────────────────────────────────────────

export class BgtReservationCreated extends BgtDomainEvent {
  readonly eventName = "BgtReservationCreated";
  constructor(
    public readonly reservationId: string,
    public readonly budgetPlanId: string,
    public readonly amount: number,
  ) { super(); }
}

export class BgtReservationConsumed extends BgtDomainEvent {
  readonly eventName = "BgtReservationConsumed";
  constructor(
    public readonly reservationId: string,
    public readonly amount: number,
    public readonly remaining: number,
  ) { super(); }
}

export class BgtReservationReleased extends BgtDomainEvent {
  readonly eventName = "BgtReservationReleased";
  constructor(
    public readonly reservationId: string,
    public readonly budgetPlanId: string,
    public readonly releasedAmount: number,
  ) { super(); }
}

// ─── Budget Allocation Events ─────────────────────────────────────────────────

export class BgtAllocationExecuted extends BgtDomainEvent {
  readonly eventName = "BgtAllocationExecuted";
  constructor(
    public readonly ruleId: string,
    public readonly resultId: string,
    public readonly allocatedAmount: number,
  ) { super(); }
}

export class BgtAllocationPostedToGL extends BgtDomainEvent {
  readonly eventName = "BgtAllocationPostedToGL";
  constructor(
    public readonly resultId: string,
    public readonly glBatchId: string,
  ) { super(); }
}

// ─── Budget Control Events ────────────────────────────────────────────────────

export class BgtBudgetCheckPerformed extends BgtDomainEvent {
  readonly eventName = "BgtBudgetCheckPerformed";
  constructor(
    public readonly budgetDetailId: string,
    public readonly requestedAmount: number,
    public readonly availableAmount: number,
    public readonly passed: boolean,
    public readonly controlLevel: string,
  ) { super(); }
}

export class BgtBudgetExceeded extends BgtDomainEvent {
  readonly eventName = "BgtBudgetExceeded";
  constructor(
    public readonly budgetDetailId: string,
    public readonly requestedAmount: number,
    public readonly availableAmount: number,
    public readonly controlLevel: string,
  ) { super(); }
}

// ─── Forecast Events ──────────────────────────────────────────────────────────

export class BgtForecastCreated extends BgtDomainEvent {
  readonly eventName = "BgtForecastCreated";
  constructor(
    public readonly forecastId: string,
    public readonly budgetPlanId: string,
    public readonly forecastMethod: string,
  ) { super(); }
}

export class BgtForecastApproved extends BgtDomainEvent {
  readonly eventName = "BgtForecastApproved";
  constructor(
    public readonly forecastId: string,
    public readonly approvedById: string,
  ) { super(); }
}

// ─── Approval Events ──────────────────────────────────────────────────────────

export class BgtApprovalRequestCreated extends BgtDomainEvent {
  readonly eventName = "BgtApprovalRequestCreated";
  constructor(
    public readonly requestId: string,
    public readonly budgetPlanId: string,
    public readonly totalAmount: number,
  ) { super(); }
}

export class BgtApprovalStepCompleted extends BgtDomainEvent {
  readonly eventName = "BgtApprovalStepCompleted";
  constructor(
    public readonly requestId: string,
    public readonly stepOrder: number,
    public readonly decision: string,
    public readonly approverId: string,
  ) { super(); }
}

export class BgtApprovalCompleted extends BgtDomainEvent {
  readonly eventName = "BgtApprovalCompleted";
  constructor(
    public readonly requestId: string,
    public readonly budgetPlanId: string,
    public readonly status: string,
  ) { super(); }
}

// ─── Snapshot Events ──────────────────────────────────────────────────────────

export class BgtSnapshotCreated extends BgtDomainEvent {
  readonly eventName = "BgtSnapshotCreated";
  constructor(
    public readonly snapshotId: string,
    public readonly budgetPlanId: string,
    public readonly snapshotType: string,
  ) { super(); }
}

export class BgtSnapshotRestored extends BgtDomainEvent {
  readonly eventName = "BgtSnapshotRestored";
  constructor(
    public readonly snapshotId: string,
    public readonly budgetPlanId: string,
  ) { super(); }
}

// ─── Period Close Events ──────────────────────────────────────────────────────

export class BgtPeriodClosed extends BgtDomainEvent {
  readonly eventName = "BgtPeriodClosed";
  constructor(
    public readonly fiscalYearId: string,
    public readonly periodId: string,
    public readonly budgetPlanId: string | null,
  ) { super(); }
}

// ─── Journal Events ───────────────────────────────────────────────────────────

export class BgtJournalPosted extends BgtDomainEvent {
  readonly eventName = "BgtJournalPosted";
  constructor(
    public readonly journalId: string,
    public readonly glBatchId: string,
  ) { super(); }
}
