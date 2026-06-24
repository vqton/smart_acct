import { DomainEvent } from "../../shared/domain-event.js";

function event(name: string, aggregateId: string, payload: Record<string, unknown>): DomainEvent {
  return { eventName: name, aggregateId, occurredAt: new Date(), payload };
}

export const CostingEvents = {
  // Cost Version
  CostVersionCreated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.cost_version.created", id, p),
  CostVersionLocked: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.cost_version.locked", id, p),

  // BOM
  BomCreated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.bom.created", id, p),
  BomRevised: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.bom.revised", id, p),

  // Work Center
  WorkCenterCreated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.work_center.created", id, p),
  WorkCenterRateUpdated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.work_center.rate_updated", id, p),

  // Production Order
  ProductionOrderCreated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.created", id, p),
  ProductionOrderReleased: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.released", id, p),
  ProductionOrderCompleted: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.completed", id, p),
  ProductionOrderClosed: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.closed", id, p),
  ProductionOrderCancelled: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.cancelled", id, p),
  ProductionOrderVarianceCalculated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.variance_calculated", id, p),

  // Component
  ComponentIssued: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.component_issued", id, p),
  ComponentReturned: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.component_returned", id, p),

  // Operation
  OperationCompleted: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.production_order.operation_completed", id, p),

  // Cost Pool
  CostPoolCreated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.cost_pool.created", id, p),
  CostPoolAllocated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.cost_pool.allocated", id, p),

  // Allocation
  AllocationRuleCreated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.allocation_rule.created", id, p),
  AllocationExecuted: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.allocation.executed", id, p),

  // Overhead Rate
  OverheadRateCreated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.overhead_rate.created", id, p),

  // Snapshot
  CostSnapshotCreated: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.snapshot.created", id, p),
  CostSnapshotFrozen: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.snapshot.frozen", id, p),

  // Variance
  VarianceRecorded: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.variance.recorded", id, p),

  // Period Close
  PeriodCloseStarted: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.period_close.started", id, p),
  PeriodCloseCompleted: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.period_close.completed", id, p),

  // Rollup
  CostRollupCompleted: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.rollup.completed", id, p),

  // GL
  CostPostedToGL: (id: string, p: Record<string, unknown>): DomainEvent =>
    event("costing.gl.posted", id, p),
};
