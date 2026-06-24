import type { DomainEvent } from "../../shared/domain-event.js";

function event(eventName: string, aggregateId: string, payload: Record<string, unknown>): DomainEvent {
  return { eventName, aggregateId, occurredAt: new Date(), payload };
}

export class FaAssetCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.created", aggregateId, payload);
  }
  static eventName = "fa.asset.created";
}

export class FaAssetAcquired {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.acquired", aggregateId, payload);
  }
  static eventName = "fa.asset.acquired";
}

export class FaAssetCapitalized {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.capitalized", aggregateId, payload);
  }
  static eventName = "fa.asset.capitalized";
}

export class FaAssetDepreciated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.depreciated", aggregateId, payload);
  }
  static eventName = "fa.asset.depreciated";
}

export class FaAssetRevalued {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.revalued", aggregateId, payload);
  }
  static eventName = "fa.asset.revalued";
}

export class FaAssetImpaired {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.impaired", aggregateId, payload);
  }
  static eventName = "fa.asset.impaired";
}

export class FaAssetDisposed {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.disposed", aggregateId, payload);
  }
  static eventName = "fa.asset.disposed";
}

export class FaAssetTransferred {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.transferred", aggregateId, payload);
  }
  static eventName = "fa.asset.transferred";
}

export class FaAssetSplit {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.split", aggregateId, payload);
  }
  static eventName = "fa.asset.split";
}

export class FaAssetMerged {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.merged", aggregateId, payload);
  }
  static eventName = "fa.asset.merged";
}

export class FaAssetWrittenOff {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.written_off", aggregateId, payload);
  }
  static eventName = "fa.asset.written_off";
}

export class FaAssetDonated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.donated", aggregateId, payload);
  }
  static eventName = "fa.asset.donated";
}

export class FaCipProjectCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.cip.created", aggregateId, payload);
  }
  static eventName = "fa.cip.created";
}

export class FaCipCapitalized {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.cip.capitalized", aggregateId, payload);
  }
  static eventName = "fa.cip.capitalized";
}

export class FaLeaseCreated {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.lease.created", aggregateId, payload);
  }
  static eventName = "fa.lease.created";
}

export class FaLeasePaymentMade {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.lease.payment_made", aggregateId, payload);
  }
  static eventName = "fa.lease.payment_made";
}

export class FaMaintenanceCompleted {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.maintenance.completed", aggregateId, payload);
  }
  static eventName = "fa.maintenance.completed";
}

export class FaPhysicalVerificationCompleted {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.verification.completed", aggregateId, payload);
  }
  static eventName = "fa.verification.completed";
}

export class FaAssetReopened {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.asset.reopened", aggregateId, payload);
  }
  static eventName = "fa.asset.reopened";
}

export class FaDepreciationRunCompleted {
  static create(aggregateId: string, payload: Record<string, unknown>): DomainEvent {
    return event("fa.depreciation_run.completed", aggregateId, payload);
  }
  static eventName = "fa.depreciation_run.completed";
}
