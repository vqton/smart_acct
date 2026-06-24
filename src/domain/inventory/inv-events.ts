import { DomainEvent } from "../../shared/domain-event.js";

function event(eventName: string, aggregateId: string, payload: Record<string, unknown>): DomainEvent {
  return { eventName, aggregateId, occurredAt: new Date(), payload };
}

// Item events
export class ItemCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.item.created", aggregateId, payload);
  }
  static eventName = "inventory.item.created";
}

export class ItemUpdated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.item.updated", aggregateId, payload);
  }
  static eventName = "inventory.item.updated";
}

export class ItemStatusChanged {
  static create(aggregateId: string, status: string): DomainEvent {
    return event("inventory.item.status_changed", aggregateId, { status });
  }
  static eventName = "inventory.item.status_changed";
}

// Warehouse events
export class WarehouseCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.warehouse.created", aggregateId, payload);
  }
  static eventName = "inventory.warehouse.created";
}

export class LocationCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.location.created", aggregateId, payload);
  }
  static eventName = "inventory.location.created";
}

// Stock balance events
export class StockReceived {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.stock.received", aggregateId, payload);
  }
  static eventName = "inventory.stock.received";
}

export class StockIssued {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.stock.issued", aggregateId, payload);
  }
  static eventName = "inventory.stock.issued";
}

export class StockTransferred {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.stock.transferred", aggregateId, payload);
  }
  static eventName = "inventory.stock.transferred";
}

export class StockAdjusted {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.stock.adjusted", aggregateId, payload);
  }
  static eventName = "inventory.stock.adjusted";
}

// Transaction events
export class InventoryTransactionCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.transaction.created", aggregateId, payload);
  }
  static eventName = "inventory.transaction.created";
}

export class InventoryTransactionPosted {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.transaction.posted", aggregateId, payload);
  }
  static eventName = "inventory.transaction.posted";
}

export class InventoryTransactionReversed {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.transaction.reversed", aggregateId, payload);
  }
  static eventName = "inventory.transaction.reversed";
}

// Cost events
export class CostLayerCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.cost_layer.created", aggregateId, payload);
  }
  static eventName = "inventory.cost_layer.created";
}

export class CostLayerConsumed {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.cost_layer.consumed", aggregateId, payload);
  }
  static eventName = "inventory.cost_layer.consumed";
}

// Count events
export class StockCountCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.stock_count.created", aggregateId, payload);
  }
  static eventName = "inventory.stock_count.created";
}

export class StockCountCompleted {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.stock_count.completed", aggregateId, payload);
  }
  static eventName = "inventory.stock_count.completed";
}

export class CountVarianceResolved {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.count_variance.resolved", aggregateId, payload);
  }
  static eventName = "inventory.count_variance.resolved";
}

// Reservation events
export class InventoryReserved {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.reserved", aggregateId, payload);
  }
  static eventName = "inventory.reserved";
}

export class ReservationReleased {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("inventory.reservation.released", aggregateId, payload);
  }
  static eventName = "inventory.reservation.released";
}
