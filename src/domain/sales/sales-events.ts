import { DomainEvent } from "../../shared/domain-event.js";

export class CustomerCreated implements DomainEvent {
  readonly eventName = "CustomerCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CustomerUpdated implements DomainEvent {
  readonly eventName = "CustomerUpdated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CustomerBlocked implements DomainEvent {
  readonly eventName = "CustomerBlocked";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CustomerCreditLimitChanged implements DomainEvent {
  readonly eventName = "CustomerCreditLimitChanged";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CustomerBlacklisted implements DomainEvent {
  readonly eventName = "CustomerBlacklisted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class QuotationCreated implements DomainEvent {
  readonly eventName = "QuotationCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class QuotationSent implements DomainEvent {
  readonly eventName = "QuotationSent";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class QuotationAccepted implements DomainEvent {
  readonly eventName = "QuotationAccepted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class QuotationRejected implements DomainEvent {
  readonly eventName = "QuotationRejected";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class QuotationConverted implements DomainEvent {
  readonly eventName = "QuotationConverted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class QuotationExpired implements DomainEvent {
  readonly eventName = "QuotationExpired";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesOrderCreated implements DomainEvent {
  readonly eventName = "SalesOrderCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesOrderApproved implements DomainEvent {
  readonly eventName = "SalesOrderApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesOrderConfirmed implements DomainEvent {
  readonly eventName = "SalesOrderConfirmed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesOrderCancelled implements DomainEvent {
  readonly eventName = "SalesOrderCancelled";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesOrderOnHold implements DomainEvent {
  readonly eventName = "SalesOrderOnHold";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesOrderCompleted implements DomainEvent {
  readonly eventName = "SalesOrderCompleted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class DeliveryOrderCreated implements DomainEvent {
  readonly eventName = "DeliveryOrderCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class DeliveryOrderShipped implements DomainEvent {
  readonly eventName = "DeliveryOrderShipped";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class DeliveryOrderDelivered implements DomainEvent {
  readonly eventName = "DeliveryOrderDelivered";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class DeliveryConfirmed implements DomainEvent {
  readonly eventName = "DeliveryConfirmed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesInvoiceCreated implements DomainEvent {
  readonly eventName = "SalesInvoiceCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesInvoiceApproved implements DomainEvent {
  readonly eventName = "SalesInvoiceApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesInvoicePosted implements DomainEvent {
  readonly eventName = "SalesInvoicePosted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesInvoiceCancelled implements DomainEvent {
  readonly eventName = "SalesInvoiceCancelled";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CreditNoteCreated implements DomainEvent {
  readonly eventName = "CreditNoteCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class DebitNoteCreated implements DomainEvent {
  readonly eventName = "DebitNoteCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesReturnCreated implements DomainEvent {
  readonly eventName = "SalesReturnCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesReturnApproved implements DomainEvent {
  readonly eventName = "SalesReturnApproved";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class SalesReturnCompleted implements DomainEvent {
  readonly eventName = "SalesReturnCompleted";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CustomerReceiptCreated implements DomainEvent {
  readonly eventName = "CustomerReceiptCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CustomerReceiptAllocated implements DomainEvent {
  readonly eventName = "CustomerReceiptAllocated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReceivableCreated implements DomainEvent {
  readonly eventName = "ReceivableCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReceivablePaid implements DomainEvent {
  readonly eventName = "ReceivablePaid";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReceivableWrittenOff implements DomainEvent {
  readonly eventName = "ReceivableWrittenOff";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReservationCreated implements DomainEvent {
  readonly eventName = "ReservationCreated";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReservationFulfilled implements DomainEvent {
  readonly eventName = "ReservationFulfilled";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class ReservationCancelled implements DomainEvent {
  readonly eventName = "ReservationCancelled";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class GiftCardIssued implements DomainEvent {
  readonly eventName = "GiftCardIssued";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class GiftCardRedeemed implements DomainEvent {
  readonly eventName = "GiftCardRedeemed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class LoyaltyPointsEarned implements DomainEvent {
  readonly eventName = "LoyaltyPointsEarned";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class LoyaltyPointsRedeemed implements DomainEvent {
  readonly eventName = "LoyaltyPointsRedeemed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class LoyaltyTierChanged implements DomainEvent {
  readonly eventName = "LoyaltyTierChanged";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class PromotionApplied implements DomainEvent {
  readonly eventName = "PromotionApplied";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
export class CouponRedeemed implements DomainEvent {
  readonly eventName = "CouponRedeemed";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}
