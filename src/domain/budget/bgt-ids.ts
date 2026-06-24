import { createId } from "@paralleldrive/cuid2";

export class BgtBudgetPlanId {
  constructor(public readonly value: string) {}
  static generate(): BgtBudgetPlanId { return new BgtBudgetPlanId(createId()); }
  static from(value: string): BgtBudgetPlanId { return new BgtBudgetPlanId(value); }
  equals(other: BgtBudgetPlanId): boolean { return this.value === other.value; }
}

export class BgtBudgetVersionId {
  constructor(public readonly value: string) {}
  static generate(): BgtBudgetVersionId { return new BgtBudgetVersionId(createId()); }
  static from(value: string): BgtBudgetVersionId { return new BgtBudgetVersionId(value); }
  equals(other: BgtBudgetVersionId): boolean { return this.value === other.value; }
}

export class BgtBudgetDetailId {
  constructor(public readonly value: string) {}
  static generate(): BgtBudgetDetailId { return new BgtBudgetDetailId(createId()); }
  static from(value: string): BgtBudgetDetailId { return new BgtBudgetDetailId(value); }
  equals(other: BgtBudgetDetailId): boolean { return this.value === other.value; }
}

export class BgtPeriodBalanceId {
  constructor(public readonly value: string) {}
  static generate(): BgtPeriodBalanceId { return new BgtPeriodBalanceId(createId()); }
  static from(value: string): BgtPeriodBalanceId { return new BgtPeriodBalanceId(value); }
  equals(other: BgtPeriodBalanceId): boolean { return this.value === other.value; }
}

export class BgtScenarioId {
  constructor(public readonly value: string) {}
  static generate(): BgtScenarioId { return new BgtScenarioId(createId()); }
  static from(value: string): BgtScenarioId { return new BgtScenarioId(value); }
  equals(other: BgtScenarioId): boolean { return this.value === other.value; }
}

export class BgtForecastHeaderId {
  constructor(public readonly value: string) {}
  static generate(): BgtForecastHeaderId { return new BgtForecastHeaderId(createId()); }
  static from(value: string): BgtForecastHeaderId { return new BgtForecastHeaderId(value); }
  equals(other: BgtForecastHeaderId): boolean { return this.value === other.value; }
}

export class BgtForecastLineId {
  constructor(public readonly value: string) {}
  static generate(): BgtForecastLineId { return new BgtForecastLineId(createId()); }
  static from(value: string): BgtForecastLineId { return new BgtForecastLineId(value); }
  equals(other: BgtForecastLineId): boolean { return this.value === other.value; }
}

export class BgtForecastDriverId {
  constructor(public readonly value: string) {}
  static generate(): BgtForecastDriverId { return new BgtForecastDriverId(createId()); }
  static from(value: string): BgtForecastDriverId { return new BgtForecastDriverId(value); }
  equals(other: BgtForecastDriverId): boolean { return this.value === other.value; }
}

export class BgtAllocationRuleId {
  constructor(public readonly value: string) {}
  static generate(): BgtAllocationRuleId { return new BgtAllocationRuleId(createId()); }
  static from(value: string): BgtAllocationRuleId { return new BgtAllocationRuleId(value); }
  equals(other: BgtAllocationRuleId): boolean { return this.value === other.value; }
}

export class BgtAllocationRuleLineId {
  constructor(public readonly value: string) {}
  static generate(): BgtAllocationRuleLineId { return new BgtAllocationRuleLineId(createId()); }
  static from(value: string): BgtAllocationRuleLineId { return new BgtAllocationRuleLineId(value); }
  equals(other: BgtAllocationRuleLineId): boolean { return this.value === other.value; }
}

export class BgtAllocationResultId {
  constructor(public readonly value: string) {}
  static generate(): BgtAllocationResultId { return new BgtAllocationResultId(createId()); }
  static from(value: string): BgtAllocationResultId { return new BgtAllocationResultId(value); }
  equals(other: BgtAllocationResultId): boolean { return this.value === other.value; }
}

export class BgtBudgetControlId {
  constructor(public readonly value: string) {}
  static generate(): BgtBudgetControlId { return new BgtBudgetControlId(createId()); }
  static from(value: string): BgtBudgetControlId { return new BgtBudgetControlId(value); }
  equals(other: BgtBudgetControlId): boolean { return this.value === other.value; }
}

export class BgtReservationId {
  constructor(public readonly value: string) {}
  static generate(): BgtReservationId { return new BgtReservationId(createId()); }
  static from(value: string): BgtReservationId { return new BgtReservationId(value); }
  equals(other: BgtReservationId): boolean { return this.value === other.value; }
}

export class BgtReservationLineId {
  constructor(public readonly value: string) {}
  static generate(): BgtReservationLineId { return new BgtReservationLineId(createId()); }
  static from(value: string): BgtReservationLineId { return new BgtReservationLineId(value); }
  equals(other: BgtReservationLineId): boolean { return this.value === other.value; }
}

export class BgtTransferId {
  constructor(public readonly value: string) {}
  static generate(): BgtTransferId { return new BgtTransferId(createId()); }
  static from(value: string): BgtTransferId { return new BgtTransferId(value); }
  equals(other: BgtTransferId): boolean { return this.value === other.value; }
}

export class BgtTransferLineId {
  constructor(public readonly value: string) {}
  static generate(): BgtTransferLineId { return new BgtTransferLineId(createId()); }
  static from(value: string): BgtTransferLineId { return new BgtTransferLineId(value); }
  equals(other: BgtTransferLineId): boolean { return this.value === other.value; }
}

export class BgtApprovalRequestId {
  constructor(public readonly value: string) {}
  static generate(): BgtApprovalRequestId { return new BgtApprovalRequestId(createId()); }
  static from(value: string): BgtApprovalRequestId { return new BgtApprovalRequestId(value); }
  equals(other: BgtApprovalRequestId): boolean { return this.value === other.value; }
}

export class BgtApprovalStepId {
  constructor(public readonly value: string) {}
  static generate(): BgtApprovalStepId { return new BgtApprovalStepId(createId()); }
  static from(value: string): BgtApprovalStepId { return new BgtApprovalStepId(value); }
  equals(other: BgtApprovalStepId): boolean { return this.value === other.value; }
}

export class BgtSnapshotId {
  constructor(public readonly value: string) {}
  static generate(): BgtSnapshotId { return new BgtSnapshotId(createId()); }
  static from(value: string): BgtSnapshotId { return new BgtSnapshotId(value); }
  equals(other: BgtSnapshotId): boolean { return this.value === other.value; }
}

export class BgtSnapshotDetailId {
  constructor(public readonly value: string) {}
  static generate(): BgtSnapshotDetailId { return new BgtSnapshotDetailId(createId()); }
  static from(value: string): BgtSnapshotDetailId { return new BgtSnapshotDetailId(value); }
  equals(other: BgtSnapshotDetailId): boolean { return this.value === other.value; }
}

export class BgtDimensionId {
  constructor(public readonly value: string) {}
  static generate(): BgtDimensionId { return new BgtDimensionId(createId()); }
  static from(value: string): BgtDimensionId { return new BgtDimensionId(value); }
  equals(other: BgtDimensionId): boolean { return this.value === other.value; }
}

export class BgtDimensionValueId {
  constructor(public readonly value: string) {}
  static generate(): BgtDimensionValueId { return new BgtDimensionValueId(createId()); }
  static from(value: string): BgtDimensionValueId { return new BgtDimensionValueId(value); }
  equals(other: BgtDimensionValueId): boolean { return this.value === other.value; }
}

export class BgtPeriodCloseId {
  constructor(public readonly value: string) {}
  static generate(): BgtPeriodCloseId { return new BgtPeriodCloseId(createId()); }
  static from(value: string): BgtPeriodCloseId { return new BgtPeriodCloseId(value); }
  equals(other: BgtPeriodCloseId): boolean { return this.value === other.value; }
}

export class BgtJournalId {
  constructor(public readonly value: string) {}
  static generate(): BgtJournalId { return new BgtJournalId(createId()); }
  static from(value: string): BgtJournalId { return new BgtJournalId(value); }
  equals(other: BgtJournalId): boolean { return this.value === other.value; }
}

export class BgtJournalLineId {
  constructor(public readonly value: string) {}
  static generate(): BgtJournalLineId { return new BgtJournalLineId(createId()); }
  static from(value: string): BgtJournalLineId { return new BgtJournalLineId(value); }
  equals(other: BgtJournalLineId): boolean { return this.value === other.value; }
}

export class BgtAuditLogId {
  constructor(public readonly value: string) {}
  static generate(): BgtAuditLogId { return new BgtAuditLogId(createId()); }
  static from(value: string): BgtAuditLogId { return new BgtAuditLogId(value); }
  equals(other: BgtAuditLogId): boolean { return this.value === other.value; }
}
