import { DomainEvent } from "../../shared/domain-event.js";

// ─── Invoice Lifecycle Events ─────────────────────────────────────────────────

export class EinvInvoiceCreated implements DomainEvent {
  readonly eventName = "EinvInvoiceCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceSubmitted implements DomainEvent {
  readonly eventName = "EinvInvoiceSubmitted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceApproved implements DomainEvent {
  readonly eventName = "EinvInvoiceApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceSigned implements DomainEvent {
  readonly eventName = "EinvInvoiceSigned";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceIssued implements DomainEvent {
  readonly eventName = "EinvInvoiceIssued";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceSubmittedToTaxAuthority implements DomainEvent {
  readonly eventName = "EinvInvoiceSubmittedToTaxAuthority";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceAccepted implements DomainEvent {
  readonly eventName = "EinvInvoiceAccepted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceRejected implements DomainEvent {
  readonly eventName = "EinvInvoiceRejected";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceReplaced implements DomainEvent {
  readonly eventName = "EinvInvoiceReplaced";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceAdjusted implements DomainEvent {
  readonly eventName = "EinvInvoiceAdjusted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceCancelled implements DomainEvent {
  readonly eventName = "EinvInvoiceCancelled";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceArchived implements DomainEvent {
  readonly eventName = "EinvInvoiceArchived";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceRestored implements DomainEvent {
  readonly eventName = "EinvInvoiceRestored";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvInvoiceExpired implements DomainEvent {
  readonly eventName = "EinvInvoiceExpired";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

// ─── Transmission Events ──────────────────────────────────────────────────────

export class EinvTransmissionSent implements DomainEvent {
  readonly eventName = "EinvTransmissionSent";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvTransmissionAcknowledged implements DomainEvent {
  readonly eventName = "EinvTransmissionAcknowledged";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvTransmissionFailed implements DomainEvent {
  readonly eventName = "EinvTransmissionFailed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

// ─── Master Data Events ───────────────────────────────────────────────────────

export class EinvTemplateCreated implements DomainEvent {
  readonly eventName = "EinvTemplateCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvSeriesCreated implements DomainEvent {
  readonly eventName = "EinvSeriesCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvCertificateRegistered implements DomainEvent {
  readonly eventName = "EinvCertificateRegistered";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvCertificateExpired implements DomainEvent {
  readonly eventName = "EinvCertificateExpired";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export class EinvCertificateRevoked implements DomainEvent {
  readonly eventName = "EinvCertificateRevoked";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
